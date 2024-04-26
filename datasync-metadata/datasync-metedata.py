import requests
import pandas as pd
import html
import re
import fitz
import os

def flatten_json(data, prefix=''):
    flat_data = {}
    for key, value in data.items():
        new_key = f"{prefix}.{key}" if prefix else key
        new_key = new_key.replace('.', '_')  # Replace dots with underscores
        if isinstance(value, dict):   
            flat_data.update(flatten_json(value, new_key))
        else:
            flat_data[new_key] = str(value)
    return flat_data
    
def clean_text(text):
    # Check if text is a string
    if isinstance(text, str):
        # HTML unescape (not necessary here)
        cleaned_text = html.unescape(text)
        # Remove newlines and leading/trailing whitespace
        cleaned_text = cleaned_text.replace('\n', ' ').strip()
        # Remove extra whitespace
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        return cleaned_text
    else:
        # If not a string, return the original value
        return text

def extract_page_numbers(doc_data):
    pdf_url = doc_data.get('pdfurl')
    print('pdf_url: ', pdf_url)
    if pdf_url:
        try:
            # Download PDF file locally
            pdf_filename = os.path.basename(pdf_url)
            pdf_path = os.path.join('meteorology_observation_pdf_files', pdf_filename)
            os.makedirs('meteorology_observation_pdf_files', exist_ok=True)
            with open(pdf_path, 'wb') as f:
                response = requests.get(pdf_url)
                response.raise_for_status()  # Raise an exception for HTTP errors
                f.write(response.content)
            
            # Extract page numbers from PDF
            with fitz.open(pdf_path) as pdf_document:
                last_page_number = len(pdf_document)
            
            return last_page_number
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return ''  # Return 'null' if unable to process the PDF
    else:
        return ''


try:
    url = "https://search.worldbank.org/api/v2/wds"
    params = {
        "qterm": "meteorology observation",
        "format": "json",
        "fl": "abstracts,authr,colti,count,display_title,docdt,docna,docty,geo_reg,guid,id,isbn,issn,keywd,lang,majdocty,majtheme,pdfurl,subsc,subtopic,theme,topic,url",
        "rows": "1",
        "lang_exact": "English"
    }

    # Fetch total number of rows
    response = requests.get(url, params=params)
    if response.status_code == 200:
        json_data = response.json()
        total_rows = json_data.get('total', 0)
        # total_rows = '10'
        
        # Make a single API call to fetch all rows
        params['rows'] = str(total_rows)
        response = requests.get(url, params=params)
        if response.status_code == 200:
            json_data = response.json()

            # Flatten JSON data and convert it to DataFrame
            flattened_data = []
            for doc_id, doc_data in json_data['documents'].items():
                print('doc_id: ', doc_id)
                if doc_id == "facets":
                    continue  # Skip processing this document
                
                flattened_doc_data = flatten_json(doc_data)
                flattened_doc_data['document_id'] = doc_id 
                flattened_doc_data['pdf_page_numbers'] = extract_page_numbers(doc_data)
                print('pdf_page_numbers: ', flattened_doc_data['pdf_page_numbers'])
                
                flattened_data.append(flattened_doc_data)
                
                # Delete the downloaded PDF file after processing
                # os.remove(pdf_path)
                
            df = pd.DataFrame(flattened_data)

            # Clean data for all columns
            df = df.applymap(clean_text)

            # Store cleaned data in a CSV file
            df.to_csv('meteorology-observation.csv', index=False)

            print("Data saved to meteorology-observation.csv")
        else:
            print("Error fetching all rows:", response.status_code)
    else:
        print("Error fetching total:", response.status_code)

except Exception as error:
    print('Exception occurred:', error)
