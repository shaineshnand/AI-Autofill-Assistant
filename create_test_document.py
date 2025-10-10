#!/usr/bin/env python
"""
Create a test document for testing the AI Autofill Assistant
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_test_form():
    """Create a simple test form with blank fields"""
    # Create a white background
    width, height = 800, 600
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a default font, fallback to basic if not available
    try:
        font = ImageFont.truetype("arial.ttf", 16)
        title_font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
    
    # Title
    draw.text((50, 30), "Application Form", fill='black', font=title_font)
    
    # Form fields
    y_pos = 100
    
    # Name field
    draw.text((50, y_pos), "Full Name:", fill='black', font=font)
    draw.rectangle([200, y_pos-5, 500, y_pos+25], outline='black', width=2)
    y_pos += 50
    
    # Email field
    draw.text((50, y_pos), "Email Address:", fill='black', font=font)
    draw.rectangle([200, y_pos-5, 500, y_pos+25], outline='black', width=2)
    y_pos += 50
    
    # Phone field
    draw.text((50, y_pos), "Phone Number:", fill='black', font=font)
    draw.rectangle([200, y_pos-5, 500, y_pos+25], outline='black', width=2)
    y_pos += 50
    
    # Address field
    draw.text((50, y_pos), "Address:", fill='black', font=font)
    draw.rectangle([200, y_pos-5, 500, y_pos+25], outline='black', width=2)
    y_pos += 50
    
    # Date field
    draw.text((50, y_pos), "Date of Birth:", fill='black', font=font)
    draw.rectangle([200, y_pos-5, 500, y_pos+25], outline='black', width=2)
    y_pos += 50
    
    # Signature field
    draw.text((50, y_pos), "Signature:", fill='black', font=font)
    draw.rectangle([200, y_pos-5, 500, y_pos+25], outline='black', width=2)
    
    # Save the image
    test_image_path = "test_form.png"
    image.save(test_image_path)
    print(f"Test form created: {test_image_path}")
    return test_image_path

if __name__ == "__main__":
    create_test_form()




