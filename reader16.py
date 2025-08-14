import fitz  # PyMuPDF

def extract_transaction_table_region(input_pdf_path, output_pdf_path):
    doc = fitz.open(input_pdf_path)
    output_doc = fitz.open()

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("blocks")

        header_threshold = page.rect.height * 0.15
        found_header = False
        header_bottom = None

        for block in blocks:
            x0, y0, x1, y1, text, *_ = block
            if text.strip() == "TRANSACTIONS" and y1 < header_threshold:
                found_header = True
                header_bottom = y1
                break

        if found_header:
            table_blocks = []
            for block in blocks:
                x0, y0, x1, y1, text, *_ = block
                if y0 <= header_bottom:
                    continue
                clean_text = text.strip()
                if clean_text == "":
                    continue
                if clean_text.isupper() and (
                    "PRIMARY KEY" in clean_text or
                    "FOREIGN KEY" in clean_text or
                    "REFERENCES" in clean_text or
                    "CONSTRAINT" in clean_text
                ):
                    break
                table_blocks.append(block)

            if not table_blocks:
                continue

            table_top = table_blocks[0][1] - 5
            table_bottom = table_blocks[-1][3] + 5
            table_rect = fitz.Rect(0, table_top, page.rect.width, table_bottom)

            pix = page.get_pixmap(clip=table_rect, dpi=300)

            # Create new page with exact height of table image
            new_page = output_doc.new_page(width=page.rect.width, height=table_rect.height)
            new_page.insert_image(
                fitz.Rect(0, 0, page.rect.width, table_rect.height),
                pixmap=pix
            )

    if output_doc.page_count > 0:
        output_doc.save(output_pdf_path)
        print(f"✅ Table-only pages saved to: {output_pdf_path}")
    else:
        print("⚠️ No matching pages found.")

    doc.close()
    output_doc.close()

# 🔧 Replace with your actual paths
input_pdf = r"C:\Users\Suren\Downloads\input.pdf"
output_pdf = r"C:\Users\Suren\Downloads\transactions_table_only_clean.pdf"

extract_transaction_table_region(input_pdf, output_pdf)
