import fitz  # PyMuPDF

def is_table_row(text):
    return (
        any(dtype in text.lower() for dtype in ["number", "varchar", "date"]) and
        len(text.strip().split()) >= 3
    )

def extract_table_if_header_present(input_pdf_path, output_pdf_path, header_keywords):
    doc = fitz.open(input_pdf_path)
    output_doc = fitz.open()

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = sorted(page.get_text("blocks"), key=lambda b: b[1])  # sort by y0

        # Step 1: Check for header in top 20% of page
        header_zone = page.rect.height * 0.2
        header_found = False
        header_bottom = None

        for block in blocks:
            x0, y0, x1, y1, text, *_ = block
            if y1 <= header_zone:
                if any(header in text.upper() for header in header_keywords):
                    header_found = True
                    header_bottom = y1
                    break

        if not header_found:
            continue  # Skip page

        # Step 2: Collect table rows below header
        table_blocks = []
        collecting = False

        for block in blocks:
            x0, y0, x1, y1, text, *_ = block
            if y0 <= header_bottom:
                continue  # Skip blocks above header

            clean_text = text.strip()
            if not collecting:
                if is_table_row(clean_text):
                    collecting = True
                    table_blocks.append(block)
            else:
                if is_table_row(clean_text):
                    table_blocks.append(block)
                else:
                    break  # Stop when pattern breaks

        if not table_blocks:
            continue

        # Step 3: Crop and render table region
        table_top = table_blocks[0][1] - 5
        table_bottom = table_blocks[-1][3] + 5
        table_rect = fitz.Rect(0, table_top, page.rect.width, table_bottom)

        pix = page.get_pixmap(clip=table_rect, dpi=300)

        new_page = output_doc.new_page(width=page.rect.width, height=table_rect.height + 30)
        new_page.insert_image(
            fitz.Rect(0, 30, page.rect.width, 30 + table_rect.height),
            pixmap=pix
        )

    if output_doc.page_count > 0:
        output_doc.save(output_pdf_path)
        print(f"✅ Table-only pages saved to: {output_pdf_path}")
    else:
        print("⚠️ No matching headers found.")

    doc.close()
    output_doc.close()

# 🔧 Replace with your actual paths and header keywords
input_pdf = r"C:\Users\Suren\Downloads\input.pdf"
output_pdf = r"C:\Users\Suren\Downloads\transaction_tables_only.pdf"
header_keywords = ["TRANSACTION", "TRAN_SUMS"]

extract_table_if_header_present(input_pdf, output_pdf, header_keywords)
