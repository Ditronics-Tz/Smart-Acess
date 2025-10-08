# services/id_card_pdf_service.py
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import qrcode
from io import BytesIO
from PIL import Image
import os
from datetime import datetime, timedelta
from django.conf import settings


class IDCardPDFGenerator:
    """Generate ID Card PDF with front and back sides"""
    
    # CR80 Card Size (Credit Card Standard)
    CARD_WIDTH = 65 * mm
    CARD_HEIGHT = 100.00 * mm
    
    # Colors matching your design
    BG_DARK = HexColor('#1a1a1a')
    BG_ACCENT = HexColor('#2d2d2d')
    YELLOW = HexColor('#ffd700')
    BLUE = HexColor('#2196f3')
    LIGHT_BLUE = HexColor('#64b5f6')
    
    def __init__(self, student, card=None):
        self.student = student
        self.card = card
        self.buffer = BytesIO()
    
    def generate_doi_code(self):
        """Generate DOI code for the card"""
        import random
        import string
        prefix = "DGBC"
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"{prefix} {code}"
        
    def generate_qr_code(self):
        """Generate QR code for student verification"""
        verification_url = f"{settings.FRONTEND_URL}/verify/{self.student.student_uuid}"
        
        qr_data = {
            'uuid': str(self.student.student_uuid),
            'reg': self.student.registration_number,
            'verify_url': verification_url
        }
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=1,
        )
        qr.add_data(verification_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to BytesIO
        qr_buffer = BytesIO()
        img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        return qr_buffer
    
    def get_student_photo(self):
        """Get student photo or create placeholder"""
        try:
            # Check if student has photo relation
            if hasattr(self.student, 'photo') and self.student.photo and self.student.photo.photo:
                photo_path = self.student.photo.photo.path

                if os.path.exists(photo_path):
                    try:
                        # Load image with PIL and convert to RGB
                        with Image.open(photo_path) as img:
                            img.verify()  # Verify the image is valid

                        # Re-open the image (verify closes it)
                        with Image.open(photo_path) as img:
                            # Convert to RGB if necessary
                            if img.mode != 'RGB':
                                img = img.convert('RGB')

                            # Create a BytesIO buffer for the image
                            img_buffer = BytesIO()
                            img.save(img_buffer, format='JPEG')
                            img_buffer.seek(0)

                            return ImageReader(img_buffer)
                    except Exception as img_error:
                        pass
        except Exception as e:
            pass

        # Create placeholder with initials if no photo
        img = Image.new('RGB', (300, 300), color=(73, 109, 137))
        return ImageReader(img)
    
    def draw_front_side(self, c, x_offset, y_offset):
        """Draw the front side of ID card"""
        
        # Background
        c.setFillColor(self.BG_DARK)
        c.rect(x_offset, y_offset, self.CARD_WIDTH, self.CARD_HEIGHT, fill=1)
        
        # Decorative patterns (simplified)
        c.setFillColor(self.BG_ACCENT)
        c.setStrokeColor(self.BG_ACCENT)
        
        # Yellow arc (simplified as partial circle)
        c.setStrokeColor(self.YELLOW)
        c.setLineWidth(3 * mm)
        c.arc(
            x_offset + self.CARD_WIDTH/2 - 20*mm,
            y_offset + self.CARD_HEIGHT/2 - 20*mm,
            x_offset + self.CARD_WIDTH/2 + 20*mm,
            y_offset + self.CARD_HEIGHT/2 + 20*mm,
            45, 180
        )
        
        # Blue vertical bar
        c.setFillColor(self.BLUE)
        c.rect(
            x_offset + self.CARD_WIDTH - 2*mm,
            y_offset,
            2*mm,
            self.CARD_HEIGHT,
            fill=1,
            stroke=0
        )
        
        # Header
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 7)
        header_text = "DAR ES SALAAM INSTITUTE OF TECHNOLOGY"
        c.drawCentredString(
            x_offset + self.CARD_WIDTH/2,
            y_offset + self.CARD_HEIGHT - 6*mm,
            header_text
        )
        
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(
            x_offset + self.CARD_WIDTH/2,
            y_offset + self.CARD_HEIGHT - 11*mm,
            "STUDENT ID CARD"
        )
        
        # Photo circle
        photo_x = x_offset + self.CARD_WIDTH/2
        photo_y = y_offset + self.CARD_HEIGHT - 30*mm
        photo_radius = 15*mm
        
        # Yellow border circle
        c.setStrokeColor(self.YELLOW)
        c.setLineWidth(2*mm)
        c.circle(photo_x, photo_y, photo_radius, stroke=1, fill=0)
        
        # Photo - draw with circular clipping
        try:
            photo = self.get_student_photo()
            # Save graphics state
            c.saveState()
            
            # Create circular clipping path
            p = c.beginPath()
            p.circle(photo_x, photo_y, photo_radius - 1*mm)
            c.clipPath(p, stroke=0, fill=0)
            
            # Draw the photo
            photo_size = (photo_radius - 1*mm) * 2
            c.drawImage(
                photo,
                photo_x - (photo_radius - 1*mm),
                photo_y - (photo_radius - 1*mm),
                width=photo_size,
                height=photo_size,
                preserveAspectRatio=True
            )
            
            # Restore graphics state
            c.restoreState()
        except Exception as e:
            # Draw placeholder if photo fails
            c.setFillColor(HexColor('#496d89'))
            c.circle(photo_x, photo_y, photo_radius - 1*mm, stroke=0, fill=1)
        
        # Student Name
        c.setFont("Helvetica-Bold", 8)
        # Build full name with proper handling of middle name
        middle_name = f" {self.student.middle_name}" if self.student.middle_name else ""
        full_name = f"{self.student.surname} {self.student.first_name}{middle_name}"
        
        # Handle long names
        if len(full_name) > 25:
            c.setFont("Helvetica-Bold", 7)
        
        c.drawCentredString(
            x_offset + self.CARD_WIDTH/2,
            y_offset + self.CARD_HEIGHT - 53*mm,
            full_name.upper()
        )
        
        # Student Details
        details_x = x_offset + 5*mm
        details_y = y_offset + self.CARD_HEIGHT - 60*mm
        line_height = 4*mm
        
        # Use card dates if available, otherwise use student creation date
        issued_date = self.card.issued_date if self.card else self.student.created_at
        expiry_date = self.card.expiry_date if (self.card and self.card.expiry_date) else (issued_date + timedelta(days=1460))
        
        details = [
            ("REG NO:", self.student.registration_number or "N/A"),
            ("DEPT:", self.student.department or "N/A"),
            ("CLASS:", self.student.soma_class_code or "N/A"),
            ("STATUS:", self.student.academic_year_status or "N/A"),
            ("ISSUED:", issued_date.strftime("%d-%m-%Y")),
            ("EXPIRE:", expiry_date.strftime("%d-%m-%Y")),
        ]
        
        c.setFont("Helvetica-Bold", 7)
        c.setFillColor(self.LIGHT_BLUE)
        
        current_y = details_y
        for label, value in details:
            c.setFillColor(self.LIGHT_BLUE)
            c.drawString(details_x, current_y, label)
            
            c.setFillColor(white)
            c.setFont("Helvetica", 7)
            
            # Ensure value is a string
            value_str = str(value) if value else "N/A"
            
            if '\n' in value_str:  # Multi-line text
                lines = value_str.split('\n')
                for line in lines:
                    c.drawString(details_x + 15*mm, current_y, line)
                    current_y -= 3*mm
            else:
                c.drawString(details_x + 15*mm, current_y, value_str)
            
            current_y -= line_height
            c.setFont("Helvetica-Bold", 7)
        
        # DOI Code (bottom right) - Auto-generated
        doi_code = self.generate_doi_code()
        c.setFont("Helvetica-Bold", 5)
        c.setFillColor(self.YELLOW)
        c.drawRightString(
            x_offset + self.CARD_WIDTH - 3*mm,
            y_offset + 2*mm,
            f"DOI : {doi_code}"
        )
    
    def draw_back_side(self, c, x_offset, y_offset):
        """Draw the back side of ID card"""
        
        # Background
        c.setFillColor(white)
        c.rect(x_offset, y_offset, self.CARD_WIDTH, self.CARD_HEIGHT, fill=1)
        
        # Blue vertical bar
        c.setFillColor(self.BLUE)
        c.rect(
            x_offset + self.CARD_WIDTH - 2*mm,
            y_offset,
            2*mm,
            self.CARD_HEIGHT,
            fill=1,
            stroke=0
        )
        
        # Header
        c.setFillColor(self.BLUE)
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(
            x_offset + self.CARD_WIDTH/2,
            y_offset + self.CARD_HEIGHT - 8*mm,
            "DAR ES SALAAM INSTITUTE OF TECHNOLOGY"
        )
        
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 6)
        c.drawCentredString(
            x_offset + self.CARD_WIDTH/2,
            y_offset + self.CARD_HEIGHT - 12*mm,
            "Student Identity Card"
        )
        
        # Instructions
        c.setFont("Helvetica", 5)
        instructions = [
            "1. This ID card is the property of the Dar es Salaam Institute of Technology",
            "    and is non-transferable",
            "",
            "2. In case of any loss. Please report it immediately. If found, please return",
            "    it to the DASS office."
        ]
        
        inst_y = y_offset + self.CARD_HEIGHT - 17*mm
        for line in instructions:
            c.drawString(x_offset + 5*mm, inst_y, line)
            inst_y -= 2.5*mm
        
        # QR Code
        qr_image = self.generate_qr_code()
        qr_x = x_offset + self.CARD_WIDTH/2 - 10*mm
        qr_y = y_offset + 15*mm
        
        c.drawImage(
            ImageReader(qr_image),
            qr_x,
            qr_y,
            width=20*mm,
            height=20*mm
        )
        
        c.setFont("Helvetica-Bold", 5)
        c.drawCentredString(
            x_offset + self.CARD_WIDTH/2,
            y_offset + 13*mm,
            "SCAN TO VERIFY"
        )
        
        # Footer
        c.setFont("Helvetica", 5)
        c.setFillColor(self.BLUE)
        c.drawString(x_offset + 5*mm, y_offset + 6*mm, "DIT Website:")
        c.setFillColor(black)
        c.drawString(x_offset + 20*mm, y_offset + 6*mm, "http://www.ac.tz")
        
        c.setFillColor(self.BLUE)
        c.drawString(x_offset + 5*mm, y_offset + 3*mm, "ISSUED BY:")
        c.setFillColor(black)
        c.drawString(x_offset + 20*mm, y_offset + 3*mm, "DASS'S OFFICE")
    
    def generate(self):
        """Generate complete PDF with front and back"""
        
        # Create canvas with landscape A4 to fit both sides
        c = canvas.Canvas(self.buffer, pagesize=landscape((210*mm, 297*mm)))
        
        # Calculate positions to center both cards
        page_width, page_height = landscape((210*mm, 297*mm))
        
        # Front side (left)
        front_x = (page_width/2 - self.CARD_WIDTH - 5*mm) / 2
        front_y = (page_height - self.CARD_HEIGHT) / 2
        
        # Back side (right)
        back_x = page_width/2 + (page_width/2 - self.CARD_WIDTH - 5*mm) / 2
        back_y = (page_height - self.CARD_HEIGHT) / 2
        
        # Draw cards
        self.draw_front_side(c, front_x, front_y)
        self.draw_back_side(c, back_x, back_y)
        
        # Add labels
        c.setFont("Helvetica", 8)
        c.setFillColor(black)
        c.drawCentredString(front_x + self.CARD_WIDTH/2, front_y - 5*mm, "FRONT")
        c.drawCentredString(back_x + self.CARD_WIDTH/2, back_y - 5*mm, "BACK")
        
        # Add cutting guides
        c.setStrokeColor(HexColor('#cccccc'))
        c.setLineWidth(0.5)
        c.setDash(3, 3)
        
        # Front card guides
        c.rect(front_x, front_y, self.CARD_WIDTH, self.CARD_HEIGHT, fill=0)
        # Back card guides
        c.rect(back_x, back_y, self.CARD_WIDTH, self.CARD_HEIGHT, fill=0)
        
        c.showPage()
        c.save()
        
        self.buffer.seek(0)
        return self.buffer