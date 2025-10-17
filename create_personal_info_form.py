"""
Create a Personal Info Form PDF for testing
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def create_personal_info_form():
    """Create a Personal Info Form similar to the one in the image"""
    
    pdf_path = "personal_info_form.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    # Set font
    c.setFont("Helvetica-Bold", 16)
    
    # Title
    c.drawCentredString(width/2, height - 80, "Personal Info Form")
    
    # Reset font for fields
    c.setFont("Helvetica-Bold", 12)
    
    # Fields with colons (similar to the image)
    y_pos = height - 150
    
    # Full Name field
    c.drawString(100, y_pos, "Full Name:")
    y_pos -= 40
    
    # Date of Birth field  
    c.drawString(100, y_pos, "Date of Birth:")
    y_pos -= 40
    
    # Signature field
    c.drawString(100, y_pos, "Signature:")
    y_pos -= 40
    
    # Add some additional fields to test
    c.drawString(100, y_pos, "Address:")
    y_pos -= 40
    
    c.drawString(100, y_pos, "Phone Number:")
    y_pos -= 40
    
    c.drawString(100, y_pos, "Email:")
    y_pos -= 40
    
    c.drawString(100, y_pos, "Date:")
    y_pos -= 40
    
    # Save the PDF
    c.save()
    print(f"Created Personal Info Form: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    create_personal_info_form()
