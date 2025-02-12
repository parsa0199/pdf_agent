import os
import fitz
import requests
import json
from typing import Optional
from dotenv import load_dotenv
from arabic_reshaper import reshape
from bidi.algorithm import get_display
import logging
from io import BytesIO
from reportlab.pdfbase import pdfmetrics  # Import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

load_dotenv()

# Configuration (from .env file)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = os.getenv("API_URL") or "https://openrouter.ai/api/v1/chat/completions"
MODEL = os.getenv("MODEL") or "deepseek/deepseek-r1"
TEMPERATURE = float(os.getenv("TEMPERATURE") or 0.7)
MAX_TOKENS = int(os.getenv("MAX_TOKENS") or 2000)
TIMEOUT = int(os.getenv("TIMEOUT") or 60) # Increased timeout
FONT_SIZE = int(os.getenv("FONT_SIZE") or 12)
FONT_COLOR = (0, 0, 0)  # Black color (fixed)

CONTEXT = '''
Translate the above text to Persian. Respond with only the translation, nothing else. 

'''

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
}

if not OPENROUTER_API_KEY:
    raise ValueError("[ERROR] OpenRouter API key not found. Please set OPENROUTER_API_KEY in .env file.")

# Set up logging
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")


def get_deepseek_translation(text: str) -> Optional[str]:
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": f"{text}\n {CONTEXT}"}],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "stream": True,
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=data, stream=True, timeout=TIMEOUT)
        response.raise_for_status()

        translation = ""
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8")
                if decoded_line.startswith("data: "):
                    try:
                        json_str = decoded_line[6:]
                        if json_str.strip() == "[DONE]":
                            break

                        json_obj = json.loads(json_str)
                        delta_content = json_obj.get("choices", [{}])[0].get("delta", {}).get("content")
                        if delta_content:
                            translation += delta_content
                            print(delta_content, end="", flush=True)

                    except json.JSONDecodeError:
                        logging.error(f"Invalid JSON: {decoded_line[:50]}...")
                        continue

        print()
        return translation

    except requests.exceptions.RequestException as e:
        logging.error(f"OpenRouter API request failed: {e}")
        if response:
            logging.error(f"Response status code: {response.status_code}")
            try:
                logging.error(f"Response content: {response.text}")
            except:
                logging.error("Could not get the response content")
        return None




def generate_rtl_pdf(text, font_path, output_filename="rtl_text.pdf", font_size=12, margin=50):
    """Generates a PDF with right-to-left (RTL) JUSTIFIED text, top-to-bottom, correct order, mixed content support."""

    reshaped_text = reshape(text)
    final_text = get_display(reshaped_text)

    c = canvas.Canvas(output_filename, pagesize=letter)
    pdfmetrics.registerFont(TTFont('ArabicFont', font_path))

    page_width, page_height = letter
    available_width = page_width - 2 * margin

    c.setFont("ArabicFont", font_size)

    y = page_height - margin

    lines = []
    current_line = ""
    words = final_text.split()

    for word in words:
        test_line = (current_line + " " + word).strip() if current_line else word
        text_width = c.stringWidth(test_line, "ArabicFont", font_size)

        if text_width <= available_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    lines.append(current_line)

    lines.reverse()  # Reverse for RTL line order

    for line in lines:
        text_width = c.stringWidth(line, "ArabicFont", font_size)
        x = page_width - margin - text_width  # Calculate RTL starting position

        c.drawString(x, y, line)  # Draw at the calculated position
        y -= font_size * 1.2

        if y < margin:
            c.showPage()
            y = page_height - margin
            c.setFont("ArabicFont", font_size)

    c.save()
    print(f"PDF saved as {output_filename}")



def translate_pdf(file_path: str) -> None:
    if not os.path.exists(file_path):
        print(f"❌ [ERROR] File '{file_path}' not found.")
        return

    try:
        doc = fitz.open(file_path)
    except (fitz.fitz.FileNotFoundError, RuntimeError) as e:
        print(f"❌ [ERROR] Could not open PDF: {e}")
        return

    print(f"[LOG] PDF opened. Total pages: {doc.page_count}")

    translations = []
    for page_num in range(doc.page_count):
        print(f"[LOG] Translating page {page_num + 1}...")
        page = doc.load_page(page_num)
        text = page.get_text("text")

        if text.strip():
            translation = get_deepseek_translation(text)
            if translation:
                translations.append(translation)
                print(f"[LOG] Page {page_num + 1} translation complete.")
            else:
                translations.append("")
                print(f"[ERROR] Translation failed for page {page_num + 1}.")
        else:
            translations.append("")
            print(f"[LOG] Page {page_num + 1} is empty, skipping.")

    base_name, _ = os.path.splitext(os.path.basename(file_path))
    output_pdf_path = f"{base_name}_translation.pdf"
    font_path = './static/fonts/NotoSansArabic-Regular.ttf'  # Path to your font

    all_text = ""
    for translation in translations:
        all_text += translation + "\n"

    generate_rtl_pdf(all_text, font_path, output_filename=output_pdf_path)

    doc.close()


if __name__ == "__main__":
    pdf_path = input("Enter the PDF file path: ")
    print("[LOG] Starting PDF translation...")
    translate_pdf(pdf_path)
    print("[LOG] PDF translation completed.")