import pytesseract
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import docx
import cv2
import numpy as np
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = (
    r"C:/Program Files/Tesseract-OCR/tesseract.exe"
)
POPPLER_PATH = r"C:/poppler-23.10.0/Library/bin"

def preprocess_image(pil_image):
    img = np.array(pil_image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return thresh

def read_pdf(file_path):
    text = ""

    # Try text-based extraction
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted
    except Exception:
        pass

    # OCR fallback
    if text.strip() == "":
        images = convert_from_path(
            file_path,
            dpi=300,
            poppler_path=POPPLER_PATH
        )

        for img in images:
            processed = preprocess_image(img)
            text += pytesseract.image_to_string(
                processed,
                config="--oem 3 --psm 6"
            )

    return text

def read_docx(path):
    document = docx.Document(path)
    return "\n".join(p.text for p in document.paragraphs)
