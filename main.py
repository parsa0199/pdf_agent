import os
import fitz
import requests
import json
import logging
from typing import Optional, List
from dotenv import load_dotenv
from arabic_reshaper import reshape
from bidi.algorithm import get_display
from io import BytesIO
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

# Load environment variables
load_dotenv()

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = os.getenv("API_URL", "https://openrouter.ai/api/v1/chat/completions")
MODEL = os.getenv("MODEL", "google/gemini-2.0-flash-thinking-exp:free")
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 2000))
TIMEOUT = int(os.getenv("TIMEOUT", 60))
FONT_SIZE = int(os.getenv("FONT_SIZE", 14))
FONT_COLOR = (0, 0, 0)  # Black color
FONT_PATH = './static/fonts/NotoSansArabic-Regular.ttf'

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
}

CONTEXT = '''
Translate the above text to Persian. Respond with only the translation, nothing else.
'''

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def validate_api_key():
    """Ensure the API key is set."""
    if not OPENROUTER_API_KEY:
        raise ValueError("OpenRouter API key not found. Set OPENROUTER_API_KEY in the .env file.")


def call_translation_api(text: str) -> Optional[str]:
    """Calls OpenRouter API to translate text."""
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": f"{text}\n {CONTEXT}"}],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "stream": False,  # Removed streaming for simpler handling
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    except requests.exceptions.RequestException as e:
        logging.error(f"Translation API request failed: {e}")
        return None


def extract_text_from_pdf(pdf_path: str) -> List[str]:
    """Extracts text from each page of a PDF."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File '{pdf_path}' not found.")

    try:
        with fitz.open(pdf_path) as doc:
            return [page.get_text("text").strip() for page in doc]
    except Exception as e:
        logging.error(f"Failed to open PDF: {e}")
        return []


def translate_pdf_texts(texts: List[str]) -> List[str]:
    """Translates extracted PDF text."""
    translations = []
    for idx, text in enumerate(texts):
        if text:
            logging.info(f"Translating page {idx + 1}...")
            translation = call_translation_api(text)
            translations.append(translation or "")
        else:
            translations.append("")
            logging.info(f"Skipping empty page {idx + 1}.")
    return translations


def process_rtl_text(text: str) -> str:
    """Reverses and reshapes Arabic text for RTL rendering."""
    return get_display(reshape(text))


def generate_rtl_pdf(text: str, output_filename="translated.pdf", font_path=FONT_PATH, font_size=12, margin=50):
    """Generates a right-to-left formatted PDF with page numbers."""
    text = process_rtl_text(text)

    pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
    c = canvas.Canvas(output_filename, pagesize=letter)
    c.setFont("ArabicFont", font_size)

    page_width, page_height = letter
    available_width = page_width - 2 * margin

    lines, current_line = [], ""
    for word in text.split():
        test_line = (current_line + " " + word).strip() if current_line else word
        if c.stringWidth(test_line, "ArabicFont", font_size) <= available_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)

    lines.reverse()  # RTL order

    page_num, y = 1, page_height - margin
    for line in lines:
        x = page_width - margin - c.stringWidth(line, "ArabicFont", font_size)
        c.drawString(x, y, line)
        y -= font_size * 1.2

        if y < margin:
            draw_page_number(c, page_num, page_width, page_height)
            c.showPage()
            c.setFont("ArabicFont", font_size)
            y = page_height - margin
            page_num += 1

    draw_page_number(c, page_num, page_width, page_height)
    c.save()
    logging.info(f"PDF saved as {output_filename}")


def draw_page_number(c, page_num, page_width, page_height):
    """Adds a page number badge."""
    c.setFont("Helvetica", 10)
    num_text = str(page_num)
    x = page_width - inch - c.stringWidth(num_text, "Helvetica", 10) - 10
    y = inch - 60
    c.drawString(x, y, num_text)


def translate_pdf(pdf_path: str):
    """Main function to extract, translate, and generate a translated PDF."""
    logging.info("Starting PDF translation process...")
    validate_api_key()

    texts = extract_text_from_pdf(pdf_path)
    if not texts:
        logging.error("No text found in the PDF.")
        return

    translations = translate_pdf_texts(texts)
    translated_text = "\n".join(translations)

    output_pdf_path = f"{os.path.splitext(pdf_path)[0]}_translated.pdf"
    generate_rtl_pdf(translated_text, output_filename=output_pdf_path)

    logging.info("PDF translation completed successfully.")


if __name__ == "__main__":
    pdf_path = input("Enter the PDF file path: ").strip()
    translate_pdf(pdf_path)
