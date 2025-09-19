import pytesseract
from pdf2image import convert_from_path
import os
import sys
import re

def extract_text_and_chapters(pdf_path):
    """
    Extracts text from a scanned PDF and splits it into chapters.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        list: A list of tuples, where each tuple contains the chapter title and the chapter text.
              Returns an empty list if an error occurs.
    """
    try:
        images = convert_from_path(pdf_path)
        chapters = []
        current_chapter_title = "Introduction"
        current_chapter_text = ""
        chapter_pattern = re.compile(r"^\s*chapter\s+\d+\s*\n", re.IGNORECASE | re.MULTILINE)

        for i, image in enumerate(images):
            print(f"Processing page {i+1}/{len(images)}...")
            page_text = pytesseract.image_to_string(image)
            match = chapter_pattern.search(page_text)

            if match:
                if current_chapter_text.strip(): # Save previous chapter
                    chapters.append((current_chapter_title, current_chapter_text))
                current_chapter_title = match.group(0).strip()
                current_chapter_text = page_text[match.end():] # Text after the chapter title
            else:
                current_chapter_text += page_text

        if current_chapter_text.strip(): # Add the last chapter
            chapters.append((current_chapter_title, current_chapter_text))

        return chapters

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_text.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        sys.exit(1)

    print(f"Extracting text and chapters from {pdf_path}...")
    chapters = extract_text_and_chapters(pdf_path)

    if not chapters:
        print("No chapters found, or an error occurred. No files were written.")
        sys.exit(1)

    output_dir = os.path.splitext(pdf_path)[0] + "_chapters"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i, (title, text) in enumerate(chapters):
        # Sanitize the title to create a valid filename
        safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
        if not safe_title:
            safe_title = f"chapter_{i+1}"
        output_filename = os.path.join(output_dir, f"{safe_title}.txt")
        with open(output_filename, "w") as f:
            f.write(text)
        print(f"Chapter saved to {output_filename}")

    print(f"\nAll chapters have been extracted and saved in the '{output_dir}' directory.")