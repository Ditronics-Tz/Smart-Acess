# services/security_id_card_pdf_service.py
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


class SecurityIDCardPDFGenerator:
    """Generate Security Personnel ID Card PDF with white front and back sides"""
    
    # CR80 Card Size (Credit Card Standard)
    CARD_WIDTH = 65 * mm
    CARD_HEIGHT = 100.00 * mm
    
    # Colors for security card design
    BG_DARK = HexColor('#1a1a1a')
    BG_ACCENT = HexColor('#2d2d2d')
    YELLOW = HexColor('#ffd700')
    BLUE = HexColor('#2196f3')
    LIGHT_BLUE = HexColor('#64b5f6')
    RED = HexColor('#dc3545')  # For security identification
    
    def __init__(self, security_personnel, card=None):
        self.security_personnel = security_personnel
        self.card = card
        self.buffer = BytesIO()
    
    def generate_doi_code(self):
        """Generate DOI code for the security card"""
        import random
        import string
        prefix = "DITS"  # DIT Security
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"{prefix} {code}"
        
    def generate_qr_code(self):
        """Generate QR code for security personnel verification"""
        verification_url = f"{settings.FRONTEND_URL}/verify/security/{self.security_personnel.security_id}"
        
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
    
    def draw_front_side(self, c, x_offset, y_offset):
        """Draw the front side of Security ID card - WHITE BACKGROUND"""
        
        # White background
        c.setFillColor(white)
        c.rect(x_offset, y_offset, self.CARD_WIDTH, self.CARD_HEIGHT, fill=1)
        
        # Red vertical bar on the left for security identification
        c.setFillColor(self.RED)
        c.rect(
            x_offset,
            y_offset,
            2*mm,
            self.CARD_HEIGHT,
            fill=1,
            stroke=0
        )
        
        c.setFillColor(self.RED)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(
            x_offset + self.CARD_WIDTH/2,
            y_offset + self.CARD_HEIGHT - 11*mm,
            "SECURITY ID CARD"
        )
        
        # Security Details at bottom left
        details_x = x_offset + 5*mm
        line_height = 4*mm
        num_details = 3
        details_y = y_offset + 2*mm + (num_details - 1) * line_height
        
        # Use card dates if available, otherwise use security personnel creation date
        issued_date = self.card.issued_date if self.card else self.security_personnel.created_at
        expiry_date = self.card.expiry_date if (self.card and self.card.expiry_date) else (issued_date + timedelta(days=1095))  # 3 years for security
        
        badge_number = self.security_personnel.badge_number or "N/A"
        
        details = [
            ("BADGE:", badge_number),
            ("ISSUED:", issued_date.strftime("%d-%m-%Y")),
            ("EXPIRE:", expiry_date.strftime("%d-%m-%Y")),
        ]
        
        c.setFont("Helvetica-Bold", 7)
        c.setFillColor(self.RED)
        
        current_y = details_y
        for label, value in details:
            c.setFillColor(self.RED)
            c.drawString(details_x, current_y, label)
            
            c.setFillColor(black)
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
        c.setFillColor(self.RED)
        c.drawRightString(
            x_offset + self.CARD_WIDTH - 3*mm,
            y_offset + 2*mm,
            f"DOI : {doi_code}"
        )
    
    def draw_back_side(self, c, x_offset, y_offset):
        """Draw the back side of Security ID card - Same as student card back"""
        
        # White background
        c.setFillColor(white)
        c.rect(x_offset, y_offset, self.CARD_WIDTH, self.CARD_HEIGHT, fill=1)
        
        # Red vertical bar for security
        c.setFillColor(self.RED)
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
            "Security Personnel Identity Card"
        )
        
        # Instructions
        c.setFont("Helvetica", 5)
        instructions = [
            "1. This ID card is the property of the Dar es Salaam Institute of Technology",
            "    and is non-transferable",
            "",
            "2. In case of any loss. Please report it immediately. If found, please return",
            "    it to the Security Office.",
            "",
            "3. This card grants access to authorized areas only. Unauthorized use is",
            "    strictly prohibited."
        ]
        
        inst_y = y_offset + self.CARD_HEIGHT - 17*mm
        for line in instructions:
            c.drawString(x_offset + 5*mm, inst_y, line)
            inst_y -= 2.5*mm
        
        # QR Code
        qr_image = self.generate_qr_code()
        qr_x = x_offset + self.CARD_WIDTH/2 - 10*mm
        qr_y = y_offset + 18*mm
        
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
            y_offset + 16*mm,
            "SCAN TO VERIFY"
        )
        
        # Footer
        c.setFont("Helvetica", 5)
        c.setFillColor(self.BLUE)
        c.drawString(x_offset + 5*mm, y_offset + 8*mm, "DIT Website:")
        c.setFillColor(black)
        c.drawString(x_offset + 20*mm, y_offset + 8*mm, "http://www.ac.tz")
        
        c.setFillColor(self.BLUE)
        c.drawString(x_offset + 5*mm, y_offset + 5*mm, "ISSUED BY:")
        c.setFillColor(black)
        c.drawString(x_offset + 20*mm, y_offset + 5*mm, "SECURITY OFFICE")
    
    def generate(self):
        """Generate complete PDF with front on page 1 and back on page 2, using card size without extra white space"""
        
        # Create canvas with card size (portrait since height > width)
        c = canvas.Canvas(self.buffer, pagesize=(self.CARD_WIDTH, self.CARD_HEIGHT))
        
        # Draw front side on page 1
        self.draw_front_side(c, 0, 0)
        c.showPage()
        
        # Draw back side on page 2
        self.draw_back_side(c, 0, 0)
        c.showPage()
        c.save()
        
        self.buffer.seek(0)
        return self.buffer