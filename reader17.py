import fitz  # PyMuPDF
from PyPDF2 import PdfWriter, PdfReader

def extract_table_regions(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    writer = PdfWriter()

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        page_height = float(page.mediabox.height)

        # Sort blocks top to bottom
        sorted_blocks = sorted(
            [b for b in blocks if "lines" in b],
            key=lambda b: b["bbox"][1]
        )

        table_started = False
        table_blocks = []
        footer_threshold = page_height * 0.90  # bottom 10%

        for block in sorted_blocks:
            y0, y1 = block["bbox"][1], block["bbox"][3]
            text = " ".join([span["text"] for line in block["lines"] for span in line["spans"]]).strip()
            lower_text = text.lower()

            # Skip footer blocks
            if y1 > footer_threshold:
                continue

            # Skip metadata blocks on last page
            if any(kw in lower_text for kw in [
                "primary key", "foreign key", "references", "constraint",
                "currencies", "data_sources", "job_id"
            ]):
                break

            # Start collecting only after table header
            if not table_started:
                if "column name" in lower_text and "data type" in lower_text:
                    table_started = True
                else:
                    continue

            if table_started:
                table_blocks.append(block)

        # Determine crop box from table blocks
        if table_blocks:
            x0 = min(b["bbox"][0] for b in table_blocks)
            y0 = min(b["bbox"][1] for b in table_blocks)
            x1 = max(b["bbox"][2] for b in table_blocks)
            y1 = min(max(b["bbox"][3] for b in table_blocks), footer_threshold - 10)

            # Crop and add to output
            page.set_cropbox(fitz.Rect(x0, y0, x1, y1))
            writer.add_page(PdfReader(input_pdf).pages[page_num])

    # Save output
    with open(output_pdf, "wb") as f:
        writer.write(f)

# Example usage
extract_table_regions("input.pdf", "output_cleaned.pdf")
