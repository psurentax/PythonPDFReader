import fitz  # PyMuPDF

def extract_transactions_table(pdf_path, output_txt_path):
    doc = fitz.open(pdf_path)
    extracted_tables = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        lines = text.splitlines()

        # Look for exact match "TRANSACTIONS"
        for i, line in enumerate(lines):
            if line.strip() == "TRANSACTIONS":
                # Extract lines that follow the keyword
                table_lines = []
                for follow_line in lines[i+1:]:
                    if follow_line.strip() == "":
                        continue
                    # Stop if we hit another section or header
                    if follow_line.isupper() and not follow_line.startswith("TRN_"):
                        break
                    table_lines.append(follow_line)
                if table_lines:
                    extracted_tables.append(f"\nPage {page_num + 1}:\n" + "\n".join(table_lines))
                break  # Only one "TRANSACTIONS" section per page

    # Write to output file
    with open(output_txt_path, "w", encoding="utf-8") as f:
        for table in extracted_tables:
            f.write(table + "\n")

    print(f"✅ Extracted {len(extracted_tables)} table(s) to {output_txt_path}")

# 🔧 Replace with your actual file paths
pdf_path = "your_file.pdf"
output_txt_path = "transactions_table.txt"

extract_transactions_table(pdf_path, output_txt_path)
