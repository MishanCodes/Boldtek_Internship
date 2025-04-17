import chainlit as cl
import google.generativeai as genai
import json
import pytesseract
from PIL import Image
from docx import Document
import PyPDF2
import os

# Set up Gemini API Key
genai.configure(api_key="AIzaSyAbK2MMbNzD0OlRMnI95SFcjUrxKZ8wFg0")

# Set up Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@cl.on_message
async def main(message: cl.Message):
    if not message.elements:
        await cl.Message(content="Please upload a file (JSON, image, PDF, or DOCX)!").send()
        return

    file = message.elements[0]
    file_path = file.path
    extracted_text = ""

    # Check file type and extract text
    if file_path.endswith(".json"):
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                extracted_text = json.dumps(data, indent=2)
        except Exception as e:
            await cl.Message(content=f"Error reading JSON: {e}").send()
            return

    elif file_path.endswith(".png") or file_path.endswith(".jpg") or file_path.endswith(".jpeg"):
        try:
            image = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(image)
        except Exception as e:
            await cl.Message(content=f"Error processing image: {e}").send()
            return

    elif file_path.endswith(".pdf"):
        try:
            reader = PyPDF2.PdfReader(file_path)
            text_list = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_list.append(page_text)
            extracted_text = "\n".join(text_list)
        except Exception as e:
            await cl.Message(content=f"Error reading PDF: {e}").send()
            return

    elif file_path.endswith(".docx"):
        try:
            doc = Document(file_path)
            text_list = []
            for para in doc.paragraphs:
                text_list.append(para.text)
            extracted_text = "\n".join(text_list)
        except Exception as e:
            await cl.Message(content=f"Error processing DOCX: {e}").send()
            return

    else:
        await cl.Message(content="Unsupported file type! Please upload JSON, Image, PDF, or DOCX.").send()
        return

    # Show a short preview
    if len(extracted_text) > 500:
        preview_text = extracted_text[:500] + "..."
    else:
        preview_text = extracted_text

    await cl.Message(content="Extracted text:\n\n" + preview_text).send()

    # Send the text to Gemini for summary
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"""You are a helpful AI assistant.
Please summarize the following document content clearly and briefly in 2-3 sentences. 
Focus on the key information, purpose, or overall meaning — avoid technical or structural descriptions.

Document:
{extracted_text.strip()}
"""
        response = model.generate_content(prompt)

        await cl.Message(content=f"Gemini Output:\n\n{response.text.strip()}").send()
    except Exception as e:
        await cl.Message(content=f"Error with Gemini API: {e}").send()
