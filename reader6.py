import fitz  # PyMuPDF

def copy_transaction_pages_exactly(input_pdf_path, output_pdf_path):
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
            # ✅ Copy the entire page exactly as-is
            output_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

    if output_doc.page_count > 0:
        output_doc.save(output_pdf_path)
        print(f"✅ Pages with 'TRANSACTIONS' copied exactly to: {output_pdf_path}")
    else:
        print("⚠️ No matching pages found.")

    doc.close()
    output_doc.close()

# 🔧 Replace with your actual paths
input_pdf = r"C:\Users\Suren\Downloads\input.pdf"
output_pdf = r"C:\Users\Suren\Downloads\transactions_output.pdf"

copy_transaction_pages_exactly(input_pdf, output_pdf)
