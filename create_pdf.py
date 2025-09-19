import os
import sys
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

def create_pdf_from_text(text_path, pdf_path):
    """
    Creates a PDF from a text file, preserving chapter breaks.

    Args:
        text_path (str): The path to the text file.
        pdf_path (str): The path to save the output PDF.
    """
    try:
        with open(text_path, 'r') as f:
            full_text = f.read()

        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        normal_style = styles["Normal"]
        heading1_style = styles["h1"]
        story = []

        # Regex to find chapter titles. Adjust as needed for your specific text.
        # This regex looks for lines starting with 'Chapter' followed by a number or Roman numeral,
        # or just a number followed by a period and a space.
        chapter_pattern = re.compile(r"^(Chapter\s+[IVXLCDM]+\b|Chapter\s+\d+\b|\d+\.\s+.*?)$", re.MULTILINE | re.IGNORECASE)

        # Split the text by potential chapter titles
        # The re.split function will include the delimiters (chapter titles) in the result
        parts = chapter_pattern.split(full_text)

        # The first part might be introductory text before the first chapter
        # or empty if the text starts directly with a chapter.
        current_chapter_content = []
        current_chapter_title = ""

        for i, part in enumerate(parts):
            if not part.strip():
                continue

            if chapter_pattern.match(part):
                # This part is a chapter title
                if current_chapter_content: # If there's content from the previous chapter
                    if story: # Add page break before new chapter, if not the very first one
                        story.append(PageBreak())
                    story.append(Paragraph(current_chapter_title, heading1_style))
                    story.append(Spacer(1, 0.2 * inch))
                    for para_text in "".join(current_chapter_content).split('\n\n'):
                        if para_text.strip():
                            story.append(Paragraph(para_text, normal_style))
                            story.append(Spacer(1, 0.1 * inch))
                    current_chapter_content = []

                current_chapter_title = part.strip()
            else:
                # This part is content for the current chapter
                current_chapter_content.append(part)

        # Add the last chapter's content
        if current_chapter_content:
            if story: # Add page break before new chapter, if not the very first one
                story.append(PageBreak())
            story.append(Paragraph(current_chapter_title, heading1_style))
            story.append(Spacer(1, 0.2 * inch))
            for para_text in "".join(current_chapter_content).split('\n\n'):
                if para_text.strip():
                    story.append(Paragraph(para_text, normal_style))
                    story.append(Spacer(1, 0.1 * inch))

        doc.build(story)
        print(f"Successfully created PDF: {pdf_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_pdf.py <path_to_text_file>")
        sys.exit(1)

    text_path = sys.argv[1]
    if not os.path.exists(text_path):
        print(f"Error: File not found at {text_path}")
        sys.exit(1)

    output_filename = os.path.splitext(text_path)[0] + "_formatted.pdf"
    create_pdf_from_text(text_path, output_filename)