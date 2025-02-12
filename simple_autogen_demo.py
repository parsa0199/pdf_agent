import os
import fitz  # PyMuPDF
import requests
import json
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("[ERROR] OpenRouter API key not found")

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "deepseek/deepseek-r1"  # Or another suitable model
TEMPERATURE = 0.7
MAX_TOKENS = 2000
TIMEOUT = 30

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
}

def get_deepseek_translation(text: str) -> Optional[str]:
    """
    Gets a streaming translation from the OpenRouter API, ensuring a Persian response.
    """

    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": f"{text}\nTranslate the above text to Persian. Respond with only the translation, nothing else."}],  # Improved prompt
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "stream": True,
    }

    try:
        response = requests.post(
            API_URL, headers=HEADERS, json=data, stream=True, timeout=TIMEOUT
        )
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

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
                            print(delta_content, end="", flush=True)  # Real-time output

                    except json.JSONDecodeError:
                        print("[ERROR] Invalid JSON received:", decoded_line[:50], "...")  # Log truncated invalid JSON
                        continue  # Skip to the next line

        print()  # Add newline after the complete translation
        return translation

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] OpenRouter API request failed: {e}")
        return None

def translate_pdf(file_path: str) -> None:
    """Translates a PDF document page by page."""

    if not os.path.exists(file_path):
        print(f"❌ [ERROR] File '{file_path}' not found.")
        return

    try:
        doc = fitz.open(file_path)
    except fitz.fitz.FileNotFoundError:
        print(f"❌ [ERROR] File '{file_path}' not found or corrupted.")
        return
    except Exception as e:
        print(f"❌ [ERROR] Error opening PDF: {e}")
        return

    print(f"[LOG] PDF opened. Total pages: {doc.page_count}")

    for page_num in range(doc.page_count):
        print(f"[LOG] Translating page {page_num + 1}...")
        page = doc.load_page(page_num)
        text = page.get_text("text")

        if text.strip():
            translation = get_deepseek_translation(text)
            if translation:
                print(f"[LOG] Page {page_num + 1} translation complete.")
            else:
                print(f"[ERROR] Translation failed for page {page_num + 1}.")
        else:
            print(f"[LOG] Page {page_num + 1} is empty, skipping.")


if __name__ == "__main__":
    pdf_path = input("Enter the PDF file path: ")
    print("[LOG] Starting PDF translation...")
    translate_pdf(pdf_path)
    print("[LOG] PDF translation completed.")