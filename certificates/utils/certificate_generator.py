import os
import uuid
from io import BytesIO
from django.conf import settings
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color

def generate_certificate_pdf(student_name, registration_number, output_filename, template_path):
    """
    Generate a personalized PDF certificate by overlaying:
    - Student Name (gold color)
    - Registration Number (solid black)
    - Auto-adjust name coordinates depending on word count
    """

    # Load the template PDF
    template_pdf = PdfReader(template_path)
    writer = PdfWriter()
    page = template_pdf.pages[0]

    # Create a BytesIO buffer for the overlay
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=(page.mediabox.width, page.mediabox.height))

    # Load custom font if available, fallback to Helvetica-Bold
    font_path = os.path.join(settings.BASE_DIR, "static", "fonts", "PinyonScript-Regular.ttf")
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont("PinyonScript-Regular", font_path))
        font_name = "PinyonScript-Regular"
    else:
        font_name = "Helvetica-Bold"

    # Set gold-like color for name (you can adjust for your design)
    gold_color = Color(0.85, 0.65, 0.13)  # soft gold tone

    # Determine how many words are in the student's name
    word_count = len(student_name.split())

    # Adjust coordinates dynamically
    if word_count == 2:
        name_x, name_y = 380, 390  # for normal 2-word names
    elif word_count == 3:
        name_x, name_y = 320, 390  # shift slightly left for longer names
    else:
        name_x, name_y = 250, 390  # fallback for 4+ words

    # --- Draw Student Name ---
    c.setFont(font_name, 68)
    c.setFillColor(gold_color)
    c.drawString(name_x, name_y, student_name)

    # --- Draw Registration Number ---
    c.setFont("Helvetica", 18)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(150, 700, f"{registration_number}")

    # Finalize overlay
    c.save()
    packet.seek(0)

    # Merge overlay with the template
    overlay_pdf = PdfReader(packet)
    overlay_page = overlay_pdf.pages[0]
    page.merge_page(overlay_page)
    writer.add_page(page)

    # Add remaining pages if any
    for extra_page in template_pdf.pages[1:]:
        writer.add_page(extra_page)

    # Save output
    cert_dir = os.path.join(settings.MEDIA_ROOT, "certificates")
    os.makedirs(cert_dir, exist_ok=True)

    output_path = os.path.join(cert_dir, output_filename)
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path
