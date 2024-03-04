#!/usr/bin/env python3
import sys
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: extract.py file.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_text = extract_text_from_pdf(pdf_path)
    txt_file_path = pdf_path.rsplit('.', 1)[0] + '.txt'

    with open(txt_file_path, 'w') as txt_file:
        txt_file.write(output_text)

    print(output_text)  # Also print the extracted text to stdout
