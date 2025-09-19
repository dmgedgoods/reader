import os
import sys
import re
from pdf2image import convert_from_path
import pytesseract
from pytesseract import Output

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black
from reportlab.lib.units import inch


def ocr_pdf_with_layout(input_pdf_path, output_pdf_path):
    """
    args:   input_pdf_path (str): Path to the input non-OCR PDF.
            output_pdf_path (str): Path to save the output OCR PDF.
    """
    try:
        images = convert_from_path(input_pdf_path)
        c = canvas.Canvas(output_pdf_path, pagesize=letter)
        width, height = letter

        # chapter detection pattern
        chapter_pattern = re.compile(
            r"^(Chapter\s+[IVXLCDM]+\b|Chapter\s+\d+\b|\d+\.\s+.*?)$",
            re.MULTILINE | re.IGNORECASE,
        )

        for i, image in enumerate(images):
            print(f"Processing page {i+1}/{len(images)} for OCR and layout...")

            # OCR to get data including bounding boxes
            data = pytesseract.image_to_data(image, output_type=Output.DICT)

            # check for chapter title on this page
            page_text_full = pytesseract.image_to_string(image)
            chapter_match = chapter_pattern.search(page_text_full)

            if (
                chapter_match and i > 0
            ):  # Start new page for chapter, but not for the very first page
                c.showPage()

            # font for the page
            c.setFont("Helvetica", 12)

            # iterate through the OCR data to place text
            n_boxes = len(data["text"])
            for j in range(n_boxes):
                if (
                    int(data["conf"][j]) > 60
                ):  # only draw text with high confidence, adjust this
                    text = data["text"][j]
                    x = data["left"][j]
                    y = (
                        height - data["top"][j] - data["height"][j]
                    )  # Adjust y-coordinate
                    font_size = data["height"][j]  # use detected height as font size

                    # simple scaling for coordinates and font size
                    # per google: Tesseract coordinates are based on image pixels, ReportLab uses points
                    # adjust as needed
                    scale_factor_x = width / image.width
                    scale_factor_y = height / image.height

                    # adjust font size based on scaling
                    scaled_font_size = font_size * scale_factor_y
                    if scaled_font_size < 6:  # Minimum readable font size
                        scaled_font_size = 6

                    c.setFont("Helvetica", scaled_font_size)
                    c.drawString(x * scale_factor_x, y * scale_factor_y, text)

            c.showPage()  # end of current page

        c.save()
        print(f"Successfully created OCR PDF with layout: {output_pdf_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pdf_ocr_with_layout.py <path_to_input_pdf>")
        sys.exit(1)

    input_pdf_path = sys.argv[1]
    if not os.path.exists(input_pdf_path):
        print(f"Error: File not found at {input_pdf_path}")
        sys.exit(1)

    output_pdf_path = os.path.splitext(input_pdf_path)[0] + "_ocr_layout.pdf"
    ocr_pdf_with_layout(input_pdf_path, output_pdf_path)
