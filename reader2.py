import fitz  # PyMuPDF

def extract_transaction_tables_to_pdf(input_pdf_path, output_pdf_path, keyword="TRANSACTIONS"):
    doc = fitz.open(input_pdf_path)
    output_doc = fitz.open()

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text_blocks = page.get_text("blocks")  # Get text with position info

        # Check top-right corner for keyword
        found_macro = False
        for block in text_blocks:
            x0, y0, x1, y1, text, *_ = block
            if keyword in text.strip() and x1 > page.rect.width * 0.6 and y1 < page.rect.height * 0.3:
                found_macro = True
                break

        if found_macro:
            # Extract table-like text from the page
            table_text = ""
            lines = page.get_text().splitlines()
            for line in lines:
                if line.strip() == "":
                    continue
                if line.strip().isupper() and line.strip() != keyword:
                    break  # Stop at next section header
                table_text += line + "\n"

            # Create a new page and write the table
            new_page = output_doc.new_page(width=595, height=842)  # A4 size
            new_page.insert_text((50, 50), f"Page {page_num + 1} - {keyword} Table", fontsize=12, fontname="helv", fill=(0, 0, 0))
            new_page.insert_textbox(fitz.Rect(50, 80, 545, 800), table_text, fontsize=10, fontname="courier", fill=(0, 0, 0))

    if output_doc.page_count > 0:
        output_doc.save(output_pdf_path)
        print(f"✅ Extracted tables saved to: {output_pdf_path}")
    else:
        print("⚠️ No pages with the specified macro were found.")

    doc.close()
    output_doc.close()

# 🔧 Replace with your actual paths
input_pdf = r"C:\Users\Suren\Downloads\input.pdf"
output_pdf = r"C:\Users\Suren\Downloads\transactions_output.pdf"

extract_transaction_tables_to_pdf(input_pdf, output_pdf)
