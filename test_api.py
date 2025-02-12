from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display

def generate_rtl_pdf(text, font_path, output_filename="rtl_text.pdf", font_size=12, margin=50):
    """Generates a PDF with right-to-left (RTL) text, handling reshaping, 
       proper display, text wrapping, and page breaks, drawing from top to bottom.

    Args:
        text (str): The RTL text.
        font_path (str): Path to the TTF font file.
        output_filename (str, optional): Output PDF filename. Defaults to "rtl_text.pdf".
        font_size (int, optional): Font size. Defaults to 12.
        margin (int, optional): Margin size in points. Defaults to 50.
    """

    reshaped_text = arabic_reshaper.reshape(text)
    final_text = get_display(reshaped_text)

    c = canvas.Canvas(output_filename, pagesize=letter)
    pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
    c.setFont("ArabicFont", font_size)

    page_width, page_height = letter
    available_width = page_width - 2 * margin

    lines = []
    current_line = ""

    words = final_text.split()

    for word in words:
        test_line = current_line + " " + word if current_line else word
        text_width = c.stringWidth(test_line, "ArabicFont", font_size)

        if text_width <= available_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word

    lines.append(current_line.strip())

    lines.reverse()  # <--- KEY CHANGE: Reverse the order of the lines

    y_position = page_height - margin
    line_height = font_size * 1.2

    for line in lines:
        c.drawString(margin, y_position, line)
        y_position -= line_height

        if y_position < margin:
            c.showPage()
            y_position = page_height - margin
            c.setFont("ArabicFont", font_size)

    c.save()
    print(f"PDF saved as {output_filename}")


# Example usage:
text = "شهرستان بروجرد یکی از شهرستان‌های استان لرستان است. مردم بروجرد مردم لر هستند. این شهرستان در منطقه کوهستانی زاگرس قرار گرفته و مرکز آن شهر بروجرد است. شهرستان بروجرد از شمال با شهرستان‌های ملایر و نهاوند در استان همدان، از شرق با شهرستان شازند در استان مرکزی، از جنوب با شهرستان دورود و از غرب با شهرستان‌های سلسله و دلفان و از جنوب غربی با خرم‌آباد دارای مرز است."
font_path = "./static/fonts/NotoSansArabic-Regular.ttf"  # Replace with your font path
generate_rtl_pdf(text, font_path)