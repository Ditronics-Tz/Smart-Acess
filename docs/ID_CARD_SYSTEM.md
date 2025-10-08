# ID Card System Documentation

## Overview
This system manages student ID card generation, printing, and verification through QR codes.

## New Models

### 1. IDCardPrintLog
Tracks all ID card printing activities for audit purposes.

**Fields:**
- `card`: Foreign key to Card
- `student`: Foreign key to Student  
- `printed_at`: Timestamp of print
- `printed_by`: Username who printed
- `user_type`: User type (administrator/registration_officer)
- `pdf_generated`: Boolean indicating successful PDF generation

### 2. IDCardVerificationLog
Tracks QR code scans and verification attempts.

**Fields:**
- `student`: Foreign key to Student
- `verified_at`: Timestamp of verification
- `ip_address`: IP address of verifier
- `user_agent`: Browser/device information
- `verification_source`: How verification was initiated (qr_scan, direct_link)

## API Endpoints

### 1. Print ID Card
**Endpoint:** `POST /api/cards/{card_uuid}/print-card/`

**Authentication:** Required (Administrators & Registration Officers)

**Description:** Generates a PDF of the student ID card with QR code for verification.

**Response:** PDF file download

**Example:**
```bash
curl -X POST \
  http://localhost:8000/api/cards/{card_uuid}/print-card/ \
  -H "Authorization: Bearer <token>" \
  --output id_card.pdf
```

### 2. Verify Student (Public)
**Endpoint:** `GET /api/cards/verify/{student_uuid}/`

**Authentication:** None (Public endpoint)

**Description:** Verifies student identity via QR code scan or direct link. Returns student information for verification.

**Response:**
```json
{
    "success": true,
    "verified": true,
    "student": {
        "registration_number": "240126455426",
        "full_name": "REHEMA ANDREA ABDI",
        "department": "CE",
        "program": "BACHELOR OF ENGINEERING",
        "class_code": "BENG24CE",
        "status": "Enrolled",
        "academic_status": "Continuing",
        "photo_url": "http://localhost:8000/media/student_photos/uuid.jpg",
        "has_card": true,
        "card_active": true
    },
    "verified_at": "2025-10-08T14:00:00Z",
    "institution": "DAR ES SALAAM INSTITUTE OF TECHNOLOGY"
}
```

**Error Response (404):**
```json
{
    "success": false,
    "verified": false,
    "message": "Student not found or inactive."
}
```

**Usage:**
- QR code on ID card links to: `{FRONTEND_URL}/verify/{student_uuid}`
- Frontend can call API: `/api/cards/verify/{student_uuid}/`
- Logs each verification attempt with IP and user agent

## ID Card Features

### Auto-Generated DOI Code
Each ID card now includes a unique DOI (Document of Identification) code:
- Format: `DGBC XXXX` (4 random alphanumeric characters)
- Auto-generated for each card
- Displayed on card front (bottom right, yellow text)

### Student Photo Integration
- PDF service now correctly retrieves student photos from `StudentPhoto` model
- Falls back to placeholder if no photo exists
- Photos are circular on the card with yellow border

### QR Code
- Generated automatically for each card
- Links to verification URL: `{FRONTEND_URL}/verify/{student_uuid}`
- Located on back of card
- Scannable for instant verification

## Workflow

### Creating and Printing Cards

1. **Create Card**
   ```bash
   POST /api/cards/
   {
       "student_uuid": "uuid-here",
       "rfid_number": "1234567890",
       "generate_rfid": false
   }
   ```

2. **Print Card**
   ```bash
   POST /api/cards/{card_uuid}/print-card/
   ```
   - Generates PDF with front and back
   - Logs print action
   - Downloads PDF automatically

3. **Verification**
   - User scans QR code
   - Redirects to: `{FRONTEND_URL}/verify/{student_uuid}`
   - Frontend displays student info
   - Backend logs verification

## Security & Privacy

### What's Exposed in Verification:
✅ Registration number  
✅ Full name  
✅ Department  
✅ Program  
✅ Class code  
✅ Status  
✅ Photo  
✅ Card status  

### What's NOT Exposed:
❌ Student UUID (only in URL)  
❌ Mobile phone  
❌ Email  
❌ Other sensitive data  

## Database Migrations

After adding the new models, run:
```bash
python manage.py makemigrations cardmanage
python manage.py migrate
```

## Configuration

Add to `.env` file:
```
FRONTEND_URL=http://localhost:3000
```

Or set in settings.py:
```python
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
```

## Logging

All card operations are logged:
- Card creation
- Card printing (with user info)
- Verification attempts (with IP and user agent)
- PDF generation success/failure

## Future Enhancements

- [ ] Add expiry date validation on verification
- [ ] Add bulk print functionality
- [ ] Add reprint tracking
- [ ] Add verification statistics dashboard
- [ ] Add geo-location for verification logs
- [ ] Add notification on suspicious verification patterns
