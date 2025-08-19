import fitz  # PyMuPDF
import json
import re

def extract_transaction_table_to_json(input_pdf_path, output_json_path):
    """
    Extracts a table from a PDF based on a 'TRANSACTIONS' header and
    saves the data to a JSON file.

    Args:
        input_pdf_path (str): The path to the input PDF file.
        output_json_path (str): The path to the output JSON file.
    """
    doc = fitz.open(input_pdf_path)
    all_table_data = []

    # Iterate through each page of the document
    for page_num, page in enumerate(doc):
        print(f"🔎 Analyzing page {page_num + 1}...")
        blocks = page.get_text("blocks")
        header_bottom = None

        # Use a more flexible regex search for the header, ignoring case
        header_pattern = re.compile(r"transactions", re.IGNORECASE)

        # Find the header to define the start of the table region
        for block in blocks:
            x0, y0, x1, y1, text, *_ = block
            if header_pattern.search(text.strip()):
                print(f"✅ Found header 'TRANSACTIONS' on page {page_num + 1}.")
                header_bottom = y1
                break

        if header_bottom is not None:
            table_blocks = []
            # Find the blocks that belong to the table
            for block in blocks:
                x0, y0, x1, y1, text, *_ = block
                clean_text = text.strip()

                # This is a heuristic to find the end of the table
                # Based on the assumption that the table ends before a section of all-caps text,
                # like a new header or a SQL-like constraint. You may need to adjust this.
                if y0 > header_bottom and clean_text.isupper() and (
                    "PRIMARY KEY" in clean_text or
                    "FOREIGN KEY" in clean_text or
                    "REFERENCES" in clean_text or
                    "CONSTRAINT" in clean_text
                ):
                    print(f"🛑 Found end of table marker: '{clean_text[:20]}...'")
                    break

                if y0 > header_bottom and clean_text:
                    table_blocks.append(block)

            # If a table region was found
            if table_blocks:
                # Get the bounding box for the entire table region
                table_top = table_blocks[0][1] - 5
                table_bottom = table_blocks[-1][3] + 5
                table_rect = fitz.Rect(0, table_top, page.rect.width, table_bottom)

                # Extract raw text from the defined table region
                raw_text = page.get_text("text", clip=table_rect)
                lines = raw_text.strip().split('\n')

                if not lines:
                    print(f"⚠️ No text found in the defined table region on page {page_num + 1}.")
                    continue

                # The first non-empty line is assumed to be the header row
                header_line = lines[0].strip()
                # Split headers by multiple spaces, which is common in tabular data
                headers = re.split(r'\s{2,}', header_line)

                # Check for a single header that is a full sentence and ignore it
                if len(headers) < 2:
                    print(f"⚠️ Could not parse headers on page {page_num + 1}. Header line was: '{header_line}'")
                    continue
                
                # The rest are data rows
                data_lines = lines[1:]
                
                # Initialize a dictionary for the current table's data
                current_table_data = {header: [] for header in headers}

                for line in data_lines:
                    # Clean up the line and split it based on header alignment
                    # This simple split will work if the data is well-aligned
                    values = re.split(r'\s{2,}', line.strip())

                    # Ensure the number of values matches the number of headers
                    if len(values) == len(headers):
                        for i, value in enumerate(values):
                            current_table_data[headers[i]].append(value)
                
                # Add the parsed table data to our list of all tables found
                all_table_data.append(current_table_data)

    doc.close()

    # Check if any data was extracted
    if all_table_data:
        # If only one table was found, save it directly
        if len(all_table_data) == 1:
            final_data = all_table_data[0]
        # If multiple tables were found (e.g., on different pages), save them in an array
        else:
            final_data = all_table_data
            
        with open(output_json_path, 'w', encoding='utf-8') as f:
            # Use json.dumps with indent for a readable output
            json.dump(final_data, f, ensure_ascii=False, indent=4)
        print(f"✅ Table data successfully saved to: {output_json_path}")
    else:
        print("⚠️ No matching tables found in the PDF.")

# 🔧 Replace with your actual paths
input_pdf = r"C:\Users\Suren\Downloads\input.pdf"
output_json = r"C:\Users\Suren\Downloads\transactions_table_data.json"

extract_transaction_table_to_json(input_pdf, output_json)
