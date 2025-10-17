"""
Create a Personal Info Form with blue input boxes like the original
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import black, lightblue, blue
from reportlab.lib.units import inch

def create_blue_personal_info_form():
    """Create a Personal Info Form with blue input boxes like the original image"""
    
    pdf_path = "blue_personal_info_form.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    # Set font
    c.setFont("Helvetica-Bold", 16)
    
    # Title
    c.drawCentredString(width/2, height - 80, "Personal Info Form")
    
    # Reset font for fields
    c.setFont("Helvetica-Bold", 12)
    
    # Define positions for fields
    label_x = 100
    field_x = 300
    field_width = 200
    field_height = 25
    
    # Starting Y position
    y_pos = height - 150
    
    # Full Name field
    c.drawString(label_x, y_pos, "Full Name:")
    c.setFillColor(lightblue)
    c.rect(field_x, y_pos - 5, field_width, field_height, fill=1, stroke=1)
    c.setFillColor(black)
    y_pos -= 50
    
    # Date of Birth field
    c.drawString(label_x, y_pos, "Date of Birth:")
    c.setFillColor(lightblue)
    c.rect(field_x, y_pos - 5, field_width, field_height, fill=1, stroke=1)
    c.setFillColor(black)
    y_pos -= 50
    
    # Signature field
    c.drawString(label_x, y_pos, "Signature:")
    c.setFillColor(lightblue)
    c.rect(field_x, y_pos - 5, field_width, field_height, fill=1, stroke=1)
    c.setFillColor(black)
    y_pos -= 50
    
    # Address field
    c.drawString(label_x, y_pos, "Address:")
    c.setFillColor(lightblue)
    c.rect(field_x, y_pos - 5, field_width, field_height, fill=1, stroke=1)
    c.setFillColor(black)
    y_pos -= 50
    
    # Phone Number field
    c.drawString(label_x, y_pos, "Phone Number:")
    c.setFillColor(lightblue)
    c.rect(field_x, y_pos - 5, field_width, field_height, fill=1, stroke=1)
    c.setFillColor(black)
    y_pos -= 50
    
    # Email field
    c.drawString(label_x, y_pos, "Email:")
    c.setFillColor(lightblue)
    c.rect(field_x, y_pos - 5, field_width, field_height, fill=1, stroke=1)
    c.setFillColor(black)
    
    # Save the PDF
    c.save()
    print(f"Created Blue Personal Info Form: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    create_blue_personal_info_form()
