import fitz
import json
import re
import requests

def extract_text_from_pdf(pdf_path):
    text_data = []
    with fitz.open(pdf_path) as pdf_document:
        for page_number in range(len(pdf_document)):
            page = pdf_document.load_page(page_number)
            # text = page.get_text().replace('\n', ' ').replace("”", "").replace("“", "").replace("’", "").replace("—", "").replace('.', '.\n')
            text = page.get_text()
            format_text = re.sub(r'[^\x00-\x7F]', '', text).strip()
            # Extract page number from the text
            page_number_text = str(page_number + 1)
            # Check if the text starts with the page number followed by non-digit characters
            if format_text.startswith(page_number_text) and not format_text[len(page_number_text)].isdigit():
                # Skip copying the page number
                format_text = format_text[len(page_number_text):].lstrip()
            # Normalize multiple spaces to a single space
            # format_text = re.sub(r'\s+', ' ', format_text)
            # Remove any remaining special characters or unwanted characters
            # format_text = re.sub(r'[^\w\s.,]', '', format_text)
            text_data.append({"page_number": page_number + 1, "text": format_text})
    return text_data


def save_text_to_file(text, save_path):
    with open(save_path, 'w', encoding='utf-8') as file:
        for page in text:
            file.write(f"Page {page['page_number']}:\n{page['text']}\n\n")

def convert_text_to_json(text):
    return json.dumps(text, indent=4)

# Example usage:
pdf_path = 'downloaded.pdf'
txt_save_path = './world-bank-okr/extracted_text.doc'

text_data = extract_text_from_pdf(pdf_path)
save_text_to_file(text_data, txt_save_path)

print("Text extracted from PDF and saved in", txt_save_path)




