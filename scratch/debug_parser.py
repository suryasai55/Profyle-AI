import os
import tempfile
from app import create_app
from app.resume.parser import parse_resume

def debug():
    app = create_app('testing')
    
    mock_pdf_text = (
        b"%PDF-1.4\n"
        b"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
        b"2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
        b"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources <</Font <</F1 5 0 R>>>>>> endobj\n"
        b"4 0 obj <</Length 70>> stream\n"
        b"BT /F1 12 Tf 70 700 Td (Python Docker Jenkins Git AWS C++) Tj ET\n"
        b"endstream\n"
        b"endobj\n"
        b"5 0 obj <</Type /Font /Subtype /Type1 /BaseFont /Helvetica>> endobj\n"
        b"xref\n"
        b"0 6\n"
        b"0000000000 65535 f\n"
        b"0000000009 00000 n\n"
        b"0000000056 00000 n\n"
        b"0000000111 00000 n\n"
        b"0000000224 00000 n\n"
        b"0000000344 00000 n\n"
        b"trailer <</Size 6 /Root 1 0 R>>\n"
        b"startxref\n"
        b"421\n"
        b"%%EOF\n"
    )
    
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
        temp_pdf.write(mock_pdf_text)
        temp_path = temp_pdf.name
        
    try:
        score, detected, missing = parse_resume(temp_path, app.config['NLTK_DATA_DIR'])
        print("Cleaned text extracted:")
        from app.resume.parser import extract_text_from_pdf
        raw_text = extract_text_from_pdf(temp_path)
        print(f"[{raw_text}]")
        print(f"Detected skills: {detected}")
        print(f"Missing skills: {missing}")
        print(f"Total Score: {score}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    debug()
