import fitz  # PyMuPDF

def extract_transaction_table_region(input_pdf_path, output_pdf_path):
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
            # ✅ Start crop just below the TRANSACTIONS block
            table_top = y1 + 5  # Start right after the header block
            table_bottom = page.rect.height - 30  # Use full bottom space
            table_rect = fitz.Rect(0, table_top, page.rect.width, table_bottom)

            # Render cropped region
            pix = page.get_pixmap(clip=table_rect, dpi=300)

            # Output page layout
            page_width = page.rect.width
            image_height = table_rect.height
            new_page_height = image_height + 30  # Bottom margin only

            # Create new page and insert image at top
            new_page = output_doc.new_page(width=page_width, height=new_page_height)
            new_page.insert_text((50, 20), f"Page {page_num + 1} - TRANSACTIONS Table", fontsize=12)
            new_page.insert_image(
                fitz.Rect(0, 30, page_width, 30 + image_height),
                pixmap=pix
            )

    if output_doc.page_count > 0:
        output_doc.save(output_pdf_path)
        print(f"✅ Cropped table regions saved to: {output_pdf_path}")
    else:
        print("⚠️ No matching pages found.")

    doc.close()
    output_doc.close()

# 🔧 Replace with your actual paths
input_pdf = r"C:\Users\Suren\Downloads\input.pdf"
output_pdf = r"C:\Users\Suren\Downloads\transactions_table_only.pdf"

extract_transaction_table_region(input_pdf, output_pdf)
