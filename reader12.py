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
            # Scan blocks below header to find end of table
            table_blocks = []
            for block in blocks:
                x0, y0, x1, y1, text, *_ = block
                if y0 <= header_bottom:
                    continue  # Skip header and above
                clean_text = text.strip()
                if clean_text == "":
                    continue
                # Stop if we hit metadata or schema notes
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

            # Define crop region from first to last table block
            table_top = table_blocks[0][1] - 5  # Small buffer above
            table_bottom = table_blocks[-1][3] + 5  # Small buffer below
            table_rect = fitz.Rect(0, table_top, page.rect.width, table_bottom)

            # Render cropped region
            pix = page.get_pixmap(clip=table_rect, dpi=300)

            # Output page layout
            page_width = page.rect.width
            image_height = table_rect.height
            padding_top = 30
            new_page_height = image_height + padding_top + 30

            # Create new page and insert image
            new_page = output_doc.new_page(width=page_width, height=new_page_height)
            new_page.insert_text((50, 20), f"Page {page_num + 1} - TRANSACTIONS Table", fontsize=12)
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
