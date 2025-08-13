import fitz  # PyMuPDF

def extract_transactions_above_line(input_pdf_path, output_pdf_path, keyword="TRANSACTIONS"):
    doc = fitz.open(input_pdf_path)
    output_doc = fitz.open()

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("blocks")  # Get text blocks with positions

        # Define top region threshold (e.g., top 100 points of page)
        header_threshold = page.rect.height * 0.15
        found_header = False

        for block in blocks:
            x0, y0, x1, y1, text, *_ = block
            if keyword in text.strip() and y1 < header_threshold:
                found_header = True
                break

        if found_header:
            # Extract full text from page (excluding header if needed)
            lines = page.get_text().splitlines()
            table_lines = []

            for line in lines:
                line = line.strip()
                if line == "":
                    continue
                # Skip header line
                if keyword in line:
                    continue
                # Stop at next section header
                if line.isupper() and not line.startswith("TRN_"):
                    break
                table_lines.append(line)

            if table_lines:
                table_text = "\n".join(table_lines)
                new_page = output_doc.new_page(width=595, height=842)  # A4
                new_page.insert_text((50, 50), f"Page {page_num + 1} - {keyword} Table", fontsize=12)
                new_page.insert_textbox(fitz.Rect(50, 80, 545, 800), table_text, fontsize=10, fontname="courier")

    if output_doc.page_count > 0:
        output_doc.save(output_pdf_path)
        print(f"✅ Extracted tables saved to: {output_pdf_path}")
    else:
        print("⚠️ No pages with '{keyword}' in header region were found.")

    doc.close()
    output_doc.close()

# 🔧 Replace with your actual paths
input_pdf = r"C:\Users\Suren\Downloads\input.pdf"
output_pdf = r"C:\Users\Suren\Downloads\transactions_output.pdf"

extract_transactions_above_line(input_pdf, output_pdf)
