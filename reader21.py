import pdfplumber
import json
import re
from typing import List, Dict, Any

def extract_transaction_table_with_plumber(input_pdf_path: str, output_json_path: str):
    """
    Extracts a table from a PDF based on a 'TRANSACTIONS' header using pdfplumber
    and saves the data to a JSON file.

    This function leverages pdfplumber's built-in table extraction capabilities,
    which are more robust than manual text block parsing.

    Args:
        input_pdf_path (str): The path to the input PDF file.
        output_json_path (str): The path to the output JSON file.
    """
    all_table_data = []
    
    # Use a flexible regex to find the header, ignoring case and whitespace
    header_pattern = re.compile(r"transactions", re.IGNORECASE)

    try:
        with pdfplumber.open(input_pdf_path) as pdf:
            # Iterate through each page of the document
            for page_num, page in enumerate(pdf.pages):
                print(f"🔎 Analyzing page {page_num + 1}...")
                
                # Check for the presence of the header on the page
                raw_text = page.extract_text()
                if not raw_text:
                    continue

                if header_pattern.search(raw_text):
                    print(f"✅ Found header 'TRANSACTIONS' on page {page_num + 1}.")
                    
                    # Find the bounding box of the header to define the crop area
                    header_bbox = None
                    for block in page.extract_text(x_tolerance=1, y_tolerance=1, layout=True).split("\n\n"):
                        # Extract the block text and its bbox. We use this method
                        # to get more accurate block coordinates.
                        lines = block.split('\n')
                        for line in lines:
                            if header_pattern.search(line):
                                header_bbox = page.crop(page.find_tables()[0].bbox).bbox
                                break
                        if header_bbox:
                            break
                    
                    # Use a heuristic to define the table region. pdfplumber is good at
                    # finding tables, so we can just look for the first one.
                    # This assumes the 'TRANSACTIONS' header is directly above the table.
                    tables = page.find_tables()

                    if tables:
                        for table in tables:
                            # Extract the raw table data as a list of lists
                            extracted_data = table.extract()
                            
                            if extracted_data and len(extracted_data) > 1:
                                # The first row is the header
                                headers = [h.strip() if h else '' for h in extracted_data[0]]
                                # The rest are the data rows
                                data_rows = extracted_data[1:]

                                # Sanity check: Ensure we have headers and at least one data row
                                if any(headers) and data_rows:
                                    current_table_data = {header: [] for header in headers}
                                    
                                    for row in data_rows:
                                        if len(row) == len(headers):
                                            for i, value in enumerate(row):
                                                # Append value, stripping whitespace
                                                current_table_data[headers[i]].append(value.strip() if value else '')
                                    
                                    all_table_data.append(current_table_data)

    except FileNotFoundError:
        print(f"❌ Error: The file at '{input_pdf_path}' was not found.")
        return
    except Exception as e:
        print(f"❌ An error occurred during PDF processing: {e}")
        return

    # Save the extracted data to a JSON file
    if all_table_data:
        # If only one table was found, save it directly
        if len(all_table_data) == 1:
            final_data = all_table_data[0]
        # If multiple tables were found (e.g., on different pages), save them in an array
        else:
            final_data = all_table_data
        
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
        print(f"✅ Table data successfully saved to: {output_json_path}")
    else:
        print("⚠️ No matching tables found in the PDF.")


# 🔧 Replace with your actual paths
input_pdf = r"C:\Users\Suren\Downloads\input.pdf"
output_json = r"C:\Users\Suren\Downloads\transactions_table_data.json"

# Execute the function
extract_transaction_table_with_plumber(input_pdf, output_json)
