import requests
import os

try:
    url = "https://search.worldbank.org/api/v2/wds"
    params = {
        "qterm": "hepatitis",
        "format": "json",
        "fl": "issn,txturl,abstracts,guid,docna,count,authr,colti,display_title,docdt,docty,geo_reg,id,isbn,keywd,lang,majtheme,pdfurl,subsc,subtopic,theme,topic,url",
        "rows": "1"
    }

    # Fetch total number of rows
    response = requests.get(url, params=params)
    if response.status_code == 200:
        json_data = response.json()
        # total_rows = json_data.get('total', 0)
        total_rows = '10'
        print("Total Rows:", total_rows)
        
        # Make a single API call to fetch all rows
        params['rows'] = str(total_rows)
        print("Params: ", params)
        response = requests.get(url, params=params)
        if response.status_code == 200:
            json_data = response.json()
            documents = json_data.get('documents', {})
            # print('data: ', json_data)
            
            # Process documents as needed
            for document_id, document_info in documents.items():
                if document_id == "facets":
                    continue  # Skip processing this document
                
                # Create a folder for the current document ID
                folder_path = os.path.join(os.getcwd(), document_id)
                os.makedirs(folder_path, exist_ok=True)

                # Download PDF file
                pdf_url = document_info.get('pdfurl')
                if pdf_url:
                    pdf_response = requests.get(pdf_url)
                    if pdf_response.status_code == 200:
                        with open(os.path.join(folder_path, f"{document_id}.pdf"), 'wb') as f:
                            f.write(pdf_response.content)
                        print("PDF file downloaded successfully")
                    else:
                        print("Error downloading PDF file:", pdf_response.status_code)
                
                # Download TXT file
                txt_url = document_info.get('txturl')
                if txt_url:
                    txt_response = requests.get(txt_url)
                    if txt_response.status_code == 200:
                        with open(os.path.join(folder_path, f"{document_id}.txt"), 'w', encoding='utf-8') as f:
                            f.write(txt_response.text)
                        print("TXT file downloaded successfully")
                    else:
                        print("Error downloading TXT file:", txt_response.status_code)
                
        else:
            print("Error fetching all rows:", response.status_code)
    else:
        print("Error fetching total:", response.status_code)
                
except Exception as error:
    print('Exception occurred: ', error)
