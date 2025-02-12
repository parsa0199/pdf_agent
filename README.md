# PDF Translator (any language to Persian)

## Overview
This Python script extracts text from a PDF file, translates it from English to Persian using the OpenRouter AI API, and generates a new right-to-left (RTL) formatted PDF with the translated text. The output PDF includes proper text formatting and page numbers.

## Features
- Extracts text from a PDF file.
- Uses OpenRouter AI to translate the text to Persian.
- Formats the translated text in RTL (Right-to-Left) direction.
- Generates a new PDF with properly formatted Persian text and page numbers.
- Handles multi-page PDFs efficiently.

## Requirements
- Python 3.7+
- A valid OpenRouter API key
- Required dependencies (see below)

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/parsa0199/pdf-translator.git
   cd pdf-translator
   ```

2. **Create a virtual environment (optional but recommended):**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the project root and add the following:
   ```ini
   OPENROUTER_API_KEY=your_api_key_here
   API_URL=https://openrouter.ai/api/v1/chat/completions
   MODEL=deepseek/deepseek-r1
   TEMPERATURE=0.7
   MAX_TOKENS=2000
   TIMEOUT=60
   FONT_SIZE=14
   ```

   Replace `your_api_key_here` with your actual OpenRouter API key.

## Usage

1. **Run the script:**
   ```sh
   python main.py
   ```

2. **Enter the PDF file path when prompted:**
   ```sh
   Enter the PDF file path: path/to/your/document.pdf
   ```

3. **Wait for the translation to complete.** The translated PDF will be saved in the same directory with `_translated.pdf` added to its name.

## File Structure
```
.
├── main.py                  # Main script to translate PDF
├── requirements.txt         # Required dependencies
├── .env                     # Environment variables (ignored in Git)
├── static/fonts/            # Font files for Persian text rendering
├── README.md                # Project documentation
```

## Troubleshooting
- **Issue: API request failure**  
  Solution: Ensure your `OPENROUTER_API_KEY` is valid and correctly set in `.env`.
  
- **Issue: Output PDF has incorrect text formatting**  
  Solution: Ensure the font file (`NotoSansArabic-Regular.ttf`) exists in the `static/fonts/` directory.
  
- **Issue: PDF text extraction is incomplete**  
  Solution: Some PDFs have embedded text as images. Try OCR tools like `pytesseract`.
  
## Future Improvements
- Add asynchronous processing for faster translations.
- Support additional languages.
- Implement a GUI for easier usage.

## License
This project is licensed under the MIT License.

---

*Made with ❤️ by [parsa0199 using gemini ](https://github.com/parsa0199)*

