import pdfplumber
import json
import re
from typing import List, Dict, Any

def extract_transaction_table_with_plumber(input_pdf_path: str, output_json_path: str):
    """
    Extracts a table from a PDF based on a 'TRANSACTIONS' header.
    The header must be in the top-right corner, above a blue horizontal line.
    
    This function uses pdfplumber to identify specific text and line objects
    based on their position and color.

    Args:
        input_pdf_path (str): The path to the input PDF file.
        output_json_path (str): The path to the output JSON file.
    """
    all_table_data = []
    
    # Use a flexible regex to find the header, ignoring case and whitespace
    header_pattern = re.compile(r"transactions", re.IGNORECASE)

    try:
        with pdfplumber.open(input_pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                print(f"🔎 Analyzing page {page_num + 1}...")

                found_blue_line = False
                blue_line_y = None
                
                # Search for a blue horizontal line near the top of the page
                # The color is represented as a tuple of RGB values.
                # Common blue is [0, 0, 255]. We'll be a bit flexible.
                # A "blue" color check. Adjust the tolerance if needed.
                is_blue = lambda c: isinstance(c, list) and c[0] < 50 and c[1] < 50 and c[2] > 200

                # Look for a line that is horizontal and blue
                for line in page.lines:
                    # Check if the line is horizontal (start and end y are close)
                    if abs(line["x0"] - line["x1"]) > 100 and abs(line["y0"] - line["y1"]) < 2:
                        # Check if the color is blue
                        if is_blue(line.get("stroke")):
                            found_blue_line = True
                            blue_line_y = line["y1"]
                            print(f"✅ Found a blue line at y-coordinate: {blue_line_y}")
                            break
                
                if not found_blue_line:
                    continue

                found_header = False
                header_bbox = None
                # Search for the "TRANSACTIONS" text block in the top-right corner
                # `page.extract_text(layout=True)` provides block-level information including coordinates
                
                # Check blocks to find the header that meets the criteria
                for block in page.extract_text(layout=True).split('\n'):
                    # The block's layout info is lost, so we'll use a manual check against page text
                    text_content = block.strip()
                    if header_pattern.search(text_content):
                        # Now, find the actual text block with coordinates
                        words = page.extract_words()
                        for word in words:
                            if header_pattern.search(word['text']):
                                # Check if the header is above the blue line and on the right side
                                # Using a threshold of 70% of the page width
                                if word['top'] < blue_line_y and word['x1'] > page.width * 0.70:
                                    print(f"✅ Found 'TRANSACTIONS' header in the correct position.")
                                    # Create a bounding box for the header
                                    header_bbox = (word['x0'], word['top'], word['x1'], word['bottom'])
                                    found_header = True
                                    break
                        if found_header:
                            break
                
                if not found_header:
                    print(f"⚠️ No 'TRANSACTIONS' header found matching position criteria on page {page_num + 1}.")
                    continue

                # Find all tables on the page. We will assume the correct table is the first one found
                # that is below our identified header.
                tables = page.find_tables()
                
                # Find the first table below the header
                target_table = None
                for table in tables:
                    # A table is below the header if its top y-coordinate is greater than the header's bottom y-coordinate
                    # and the header bbox was found.
                    if header_bbox and table.bbox[1] > header_bbox[3]:
                        target_table = table
                        break
                
                if target_table:
                    # Extract the raw table data as a list of lists
                    extracted_data = target_table.extract()
                    
                    if extracted_data and len(extracted_data) > 1:
                        # The first row is the header
                        headers = [h.strip() if h else '' for h in extracted_data[0]]
                        # The rest are the data rows
                        data_rows = extracted_data[1:]

                        if any(headers) and data_rows:
                            current_table_data = {header: [] for header in headers}
                            
                            for row in data_rows:
                                if len(row) == len(headers):
                                    for i, value in enumerate(row):
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
        if len(all_table_data) == 1:
            final_data = all_table_data[0]
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
