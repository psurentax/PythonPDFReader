import fitz  # PyMuPDF

def extract_transactions_table_preserved(input_pdf_path, output_pdf_path):
    doc = fitz.open(input_pdf_path)
    output_doc = fitz.open()

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("blocks")

        header_threshold = page.rect.height * 0.15
        found_header = False

        for block in blocks:
            x0, y0, x1, y1, text, *_ = block
            if text.strip() == "TRANSACTIONS" and y1 < header_threshold:
                found_header = True
                break

        if found_header:
            # Get full text with layout preserved
            full_text = page.get_text("text")

            # Optionally trim header if needed
            lines = full_text.splitlines()
            trimmed_lines = []
            skip_header = False
            for line in lines:
                if line.strip() == "TRANSACTIONS":
                    skip_header = True
                    continue
                if skip_header:
                    trimmed_lines.append(line)

            table_text = "\n".join(trimmed_lines)

            # Create new page and insert text with preserved layout
            new_page = output_doc.new_page(width=595, height=842)
            new_page.insert_text((50, 50), f"Page {page_num + 1} - TRANSACTIONS Table", fontsize=12)
            new_page.insert_textbox(fitz.Rect(50, 80, 545, 800), table_text, fontsize=9, fontname="courier")

    if output_doc.page_count > 0:
        output_doc.save(output_pdf_path)
        print(f"✅ Tables with preserved layout saved to: {output_pdf_path}")
    else:
        print("⚠️ No matching pages found.")

    doc.close()
    output_doc.close()

# 🔧 Replace with your actual paths
input_pdf = r"C:\Users\Suren\Downloads\input.pdf"
output_pdf = r"C:\Users\Suren\Downloads\transactions_output.pdf"

extract_transactions_table_preserved(input_pdf, output_pdf)
