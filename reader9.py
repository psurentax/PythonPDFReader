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
            # Adjusted table region: start slightly lower to avoid overlap
            buffer_above_table = 20  # Extra space to avoid clipping
            table_top = header_threshold + buffer_above_table
            table_bottom = page.rect.height - 50
            table_rect = fitz.Rect(0, table_top, page.rect.width, table_bottom)

            # Render cropped region
            pix = page.get_pixmap(clip=table_rect, dpi=300)

            # Output page layout
            page_width = page.rect.width
            image_height = table_rect.height
            padding_top = 50  # Increased padding to prevent overlap
            padding_bottom = 30
            new_page_height = image_height + padding_top + padding_bottom

            # Create new page and insert image
            new_page = output_doc.new_page(width=page_width, height=new_page_height)
            new_page.insert_text((50, 30), f"Page {page_num + 1} - TRANSACTIONS Table", fontsize=12)
            new_page.insert_image(
                fitz.Rect(0, padding_top, page_width, padding_top + image_height),
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
