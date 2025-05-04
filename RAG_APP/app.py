import chainlit as cl
from PIL import Image
import pytesseract
import os
import shutil
import logging
import fitz  # PyMuPDF
import base64
from io import BytesIO
import re

from transformers import pipeline
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_community.embeddings import SentenceTransformerEmbeddings

# Basic setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
qa_pipeline = pipeline("text2text-generation", model="google/flan-t5-large", max_length=512, device="cpu")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)

# Global variables
retriever = None
db = None
pdf_document = None
current_filename = None

# Directories
temp_dir = os.path.join(os.getcwd(), "temp_files")
pdf_storage_dir = os.path.join(os.getcwd(), "pdf_storage")
os.makedirs(temp_dir, exist_ok=True)
os.makedirs(pdf_storage_dir, exist_ok=True)

# Set Tesseract path 
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def process_pdf(file_path, filename):
    """Process PDF and create vector index"""
    global retriever, db, pdf_document, current_filename
    
    try:
        # Save PDF for viewing and create document object
        pdf_storage_path = os.path.join(pdf_storage_dir, filename)
        shutil.copy(file_path, pdf_storage_path)
        pdf_document = fitz.open(pdf_storage_path)
        current_filename = filename
        
        # Load and process document
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        if not docs:
            return "❌ No content found in the PDF."
            
        # Add metadata to documents
        for i, doc in enumerate(docs):
            doc.metadata["page"] = i + 1
            doc.metadata["source"] = filename
        
        # Create vector store
        chunks = text_splitter.split_documents(docs)
        db = FAISS.from_documents(chunks, embedding_model)
        retriever = db.as_retriever(search_kwargs={"k": 10})
        
        return "✅ PDF processed. Ask questions or request a summary!"
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        return f"❌ Error: {str(e)}"

def process_image(file_path, filename):
    """Process image with OCR"""
    global retriever, db, current_filename
    
    try:
        image = Image.open(file_path)
        extracted_text = pytesseract.image_to_string(image)
        
        if not extracted_text.strip():
            return "❌ No text extracted from image."
        
        current_filename = filename
        doc = Document(page_content=extracted_text, metadata={"source": filename})
        chunks = text_splitter.split_documents([doc])
        
        db = FAISS.from_documents(chunks, embedding_model)
        retriever = db.as_retriever(search_kwargs={"k": 5})
        
        return "✅ Image processed. Ask your questions!"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def render_pdf_page(page_number):
    """Render PDF page as base64 image"""
    if not pdf_document:
        return None
    
    try:
        page_idx = page_number - 1
        if page_idx < 0 or page_idx >= len(pdf_document):
            return None
        
        page = pdf_document[page_idx]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        
        img_data = BytesIO()
        pix.save(img_data, "png")
        img_data.seek(0)
        
        return f"data:image/png;base64,{base64.b64encode(img_data.read()).decode()}"
    except Exception as e:
        logger.error(f"Error rendering PDF page: {str(e)}")
        return None

def ask_question(question):
    """Answer questions based on document content"""
    if not retriever:
        return "Please upload a document first.", []
    
    try:
        # Get relevant documents
        docs = retriever.invoke(question)
        if not docs:
            return "I couldn't find relevant information.", []
        
        # Create context from documents
        context = "\n".join([doc.page_content for doc in docs])
        
        # Generate answer
        prompt = f"Based on this content, answer: {context}\n\nQuestion: {question}\n\nAnswer:"
        result = qa_pipeline(prompt)[0]['generated_text']
        
        # Format sources with page links
        sources = []
        seen = set()
        for doc in docs[:5]:  # Limit to 5 sources
            if "page" in doc.metadata:
                page = doc.metadata["page"]
                source = doc.metadata.get('source', '')
                key = f"{source}:page{page}"
                if key not in seen:
                    # Use simple numeric values for the action
                    sources.append(f"📄 [{source} page {page}](view_page:{page})")
                    seen.add(key)
            
        return result.strip(), sources
    except Exception as e:
        return f"Error: {str(e)}", []

@cl.on_chat_start
async def start():
    """Initialize chat session"""
    await cl.Message(content="📄 **PDF & Image Q&A**\n\nUpload a document using the 'attach files' button.").send()
    
    # Register a single view_page action handler
    @cl.action_callback("view_page")
    async def on_view_page(action):
        try:
            # Extract page number from the action value
            page = int(action.value)
            
            if not pdf_document:
                await cl.Message(content="No PDF document loaded.").send()
                return
                
            img_data = render_pdf_page(page)
            if not img_data:
                await cl.Message(content=f"Could not render page {page}.").send()
                return
                
            await cl.Message(
                content=f"**Page {page} of {current_filename}**",
                elements=[cl.Image(name=f"Page {page}", display="inline", data=img_data)]
            ).send()
        except Exception as e:
            logger.error(f"Error in view_page action: {e}")
            await cl.Message(content=f"Error showing page: {str(e)}").send()

@cl.on_message
async def on_message(message: cl.Message):
    """Handle user messages"""
    # Check for page view link clicks from text (format: view_page:X)
    if message.content and "view_page:" in message.content:
        match = re.search(r'view_page:(\d+)', message.content)
        if match:
            page_num = int(match.group(1))
            
            if not pdf_document:
                await cl.Message(content="No PDF document loaded.").send()
                return
                
            img_data = render_pdf_page(page_num)
            if not img_data:
                await cl.Message(content=f"Could not render page {page_num}.").send()
                return
                
            await cl.Message(
                content=f"**Page {page_num} of {current_filename}**",
                elements=[cl.Image(name=f"Page {page_num}", display="inline", data=img_data)]
            ).send()
            return
    
    # Handle file uploads
    files = getattr(message, 'files', []) or []
    if hasattr(message, 'elements') and message.elements:
        for elem in message.elements:
            if hasattr(elem, 'name') and hasattr(elem, 'type'):
                files.append(elem)
    
    if files:
        for file in files:
            file_path = os.path.join(temp_dir, file.name)
            
            # Save file
            try:
                if hasattr(file, 'path') and os.path.exists(file.path):
                    shutil.copy(file.path, file_path)
                else:
                    with open(file_path, "wb") as f:
                        f.write(file.content)
            except Exception as e:
                await cl.Message(content=f"Error saving file: {str(e)}").send()
                continue
                
            # Process file
            file_type = getattr(file, 'type', '')
            if file_type == "application/pdf" or file.name.lower().endswith('.pdf'):
                result = process_pdf(file_path, file.name)
            elif file_type.startswith("image/") or any(file.name.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                result = process_image(file_path, file.name)
            else:
                result = "Unsupported file type. Please upload a PDF or image."
                
            await cl.Message(content=result).send()
            
            # Process question if provided with upload
            if message.content and "processed" in result:
                thinking = cl.Message(content="Analyzing document...")
                await thinking.send()
                
                answer, sources = ask_question(message.content)
                response = answer
                if sources:
                    response += "\n\n**Sources:**\n" + "\n".join(sources)
                    
                await cl.Message(content=response).send()
                return
        return
            
    # Handle questions
    if message.content:
        if not retriever:
            await cl.Message(content="Please upload a document first.").send()
            return
            
        thinking = cl.Message(content="Analyzing document...")
        await thinking.send()
        
        answer, sources = ask_question(message.content)
        response = answer
        if sources:
            response += "\n\n**Sources:**\n" + "\n".join(sources)
            
        # Check for any page numbers mentioned and add clickable links
        page_numbers = re.findall(r'page (\d+)', response.lower())
        for page in page_numbers:
            page_num = int(page)
            response = response.replace(f"page {page}", f"[page {page}](view_page:{page_num})")
            response = response.replace(f"Page {page}", f"[Page {page}](view_page:{page_num})")
            
        await cl.Message(content=response).send()

@cl.on_stop
def on_stop():
    """Clean up on exit"""
    if pdf_document:
        try:
            pdf_document.close()
        except:
            pass
        
    for directory in [temp_dir, pdf_storage_dir]:
        try:
            shutil.rmtree(directory)
        except:
            pass