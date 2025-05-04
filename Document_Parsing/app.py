import chainlit as cl
import os
import re
import mysql.connector
import google.generativeai as genai
from PIL import Image
from docx import Document
import easyocr
from pdf2image import convert_from_path
from dateutil import parser as date_parser

# Configure Gemini API
genai.configure(api_key="AIzaSyAbK2MMbNzD0OlRMnI95SFcjUrxKZ8wFg0") 

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'], gpu=True)

# MySQL Connection
def save_to_database(invoice_number, invoice_date, vendor_name, total_amount):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="invoices_db"
        )
        cursor = conn.cursor()
        sql = "INSERT INTO invoices (invoice_number, invoice_date, vendor_name, total_amount) VALUES (%s, %s, %s, %s)"
        values = (invoice_number, invoice_date, vendor_name, total_amount)
        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")

# Function to extract text based on file type
def extract_text(file_path):
    extracted_text = ""
    if file_path.endswith((".png", ".jpg", ".jpeg")):
        extracted_text = extract_text_easyocr(file_path)
    elif file_path.endswith(".pdf"):
        extracted_text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        for para in doc.paragraphs:
            extracted_text += para.text + "\n"
    else:
        extracted_text = "Unsupported file type!"
    return extracted_text.strip()

# EasyOCR for images
def extract_text_easyocr(file_path):
    result = reader.readtext(file_path, detail=0)
    return "\n".join(result).strip()

# PDF extraction
def extract_text_from_pdf(file_path):
    full_text = ""
    pages = convert_from_path(file_path, 300)
    for page_num, page in enumerate(pages, start=1):
        temp_image_path = f"page_{page_num}.jpg"
        page.save(temp_image_path, "JPEG")
        full_text += extract_text_easyocr(temp_image_path) + "\n"
        os.remove(temp_image_path)
    return full_text.strip()

# Normalize date to YYYY-MM-DD
def normalize_date(date_string):
    try:
        date_obj = date_parser.parse(date_string, dayfirst=True, fuzzy=True)
        return date_obj.strftime("%Y-%m-%d")
    except Exception:
        return None

# Chainlit handler
@cl.on_message
async def main(message: cl.Message):
    if not message.elements:
        await cl.Message(content="Please upload an invoice file (Image, PDF, or DOCX)!").send()
        return

    file = message.elements[0]
    file_path = file.path
    text = extract_text(file_path)

    if text == "Unsupported file type!" or len(text) == 0:
        await cl.Message(content="Could not extract text from this file!").send()
        return

    await cl.Message(content="Extracted text:\n\n" + text[:500] + ("..." if len(text) > 500 else "")).send()

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"""
You are an AI assistant specialized in extracting structured data from both printed and handwritten invoices. Invoices may contain spelling errors, inconsistent formatting, unclear handwriting, or overlapping stamps/signatures.

Please analyze the provided invoice text and return the following fields in JSON format:

1. **Invoice Number**: Unique identifier for the invoice. Look for patterns like:
   "Invoice No", "Invoice #", "Invoice Number", "Bill Number", "Inv #", "INV-". Handle handwriting variations too.

2. **Invoice Date**: The issue date. Look for:
   "Invoice Date", "Date of Issue", "Date", "Billing Date", "Dated". Normalize to `YYYY-MM-DD` if possible.

3. **Vendor Name**: Company or person issuing the invoice.
   Look near "From", "Vendor", "Supplier", "Issued By", or header area.

4. **Total Amount**: The total due.
   Look for "Total", "Total Due", "Grand Total", "Amount Due", "Amount Payable". Include currency symbols if available.

If any field is unclear or missing, return an empty string.

Expected JSON:
{{
    "Invoice Number": "",
    "Invoice Date": "",
    "Vendor Name": "",
    "Total Amount": ""
}}

Now extract from the following invoice text : 
{text}
"""
        response = model.generate_content(prompt)
        cleaned_json = response.text.strip()

        await cl.Message(content=f"Gemini Schema Output:\n\n{cleaned_json}").send()

        match = re.findall(r'"(.*?)":\s*(?:"(.*?)"|null)', cleaned_json)
        data = {key: value for key, value in match}

        if any(value for value in data.values()):
            invoice_number = data.get("Invoice Number", "")
            invoice_date_raw = data.get("Invoice Date", "")
            vendor_name = data.get("Vendor Name", "")
            total_amount_raw = data.get("Total Amount", "")

            # Clean total amount
            total_amount = re.sub(r'[^\d\.]', '', total_amount_raw)
            total_amount = float(total_amount) if total_amount else 0.00

            # Normalize invoice date
            invoice_date = normalize_date(invoice_date_raw)

            save_to_database(invoice_number, invoice_date, vendor_name, total_amount)
            await cl.Message(content="Data saved to MySQL successfully!").send()
        else:
            await cl.Message(content="No valid data to save. All fields are empty!").send()

    except Exception as e:
        await cl.Message(content=f"Error using Gemini: {e}").send()
