# Card Management System API Documentation

## Overview

The Card Management System provides comprehensive API endpoints for managing ID cards for students, staff, and security personnel at Dar es Salaam Institute of Technology. The system supports card creation, printing, verification, and management with role-based access control.

## Base URL
```
/api/cards/
```

## Authentication
All endpoints require authentication except for verification endpoints. Two user roles are supported:
- **Administrator**: Full access to all operations including card deletion
- **Registration Officer**: Can create, view, and manage cards but cannot delete them

## Card Types
The system supports three types of cards:
- `student` - For student ID cards
- `staff` - For staff member ID cards  
- `security` - For security personnel ID cards

---

## Core Card Management Endpoints

### 1. List All Cards
**GET** `/api/cards/`

Lists all cards with pagination, filtering, and search capabilities.

**Query Parameters:**
- `page` (int): Page number for pagination
- `page_size` (int): Number of items per page
- `search` (string): Search across RFID numbers, names, and identification numbers
- `is_active` (boolean): Filter by card activation status
- `card_type` (string): Filter by card type (student/staff/security)
- `student__department` (string): Filter by student department
- `staff__department` (string): Filter by staff department
- `ordering` (string): Sort field (-created_at, issued_date, etc.)

**Response:**
```json
{
  "count": 150,
  "next": "/api/cards/?page=2",
  "previous": null,
  "results": [
    {
      "card_uuid": "123e4567-e89b-12d3-a456-426614174000",
      "rfid_number": "RF123456789",
      "card_type": "student",
      "is_active": true,
      "issued_date": "2025-10-10T10:30:00Z",
      "student": {
        "student_uuid": "uuid-here",
        "registration_number": "DIT/2024/01234",
        "full_name": "John Doe Smith",
        "department": "Computer Science"
      },
      "created_at": "2025-10-10T10:30:00Z"
    }
  ],
  "summary": {
    "total_cards": 150,
    "active_cards": 145,
    "inactive_cards": 5
  }
}
```

### 2. Create Single Card
**POST** `/api/cards/`

Creates a new card for a student, staff member, or security personnel.

**Request Body:**
```json
{
  "card_type": "student",
  "student_uuid": "123e4567-e89b-12d3-a456-426614174000",
  "generate_rfid": true
}
```

**Response:**
```json
{
  "card_uuid": "new-card-uuid",
  "rfid_number": "RF987654321",
  "card_type": "student",
  "is_active": true,
  "student": {
    "registration_number": "DIT/2024/01234",
    "full_name": "John Doe Smith"
  },
  "created_by": {
    "username": "admin_user",
    "user_type": "administrator"
  }
}
```

### 3. Get Card Details
**GET** `/api/cards/{card_uuid}/`

Retrieves detailed information about a specific card.

### 4. Update Card
**PUT/PATCH** `/api/cards/{card_uuid}/`

Updates card information (RFID number, activation status, etc.).

### 5. Delete Card (Administrators Only)
**DELETE** `/api/cards/{card_uuid}/`

Permanently deletes a card record.

---

## Card Statistics

### Get Card Statistics
**GET** `/api/cards/statistics/`

Returns comprehensive statistics about the card management system.

**Response:**
```json
{
  "summary": {
    "total_personnel": 5250,
    "total_students": 5000,
    "total_staff": 200,
    "total_security": 50,
    "total_cards": 4800,
    "active_cards": 4750,
    "inactive_cards": 50,
    "student_cards": 4600,
    "staff_cards": 180,
    "security_cards": 20,
    "students_without_cards": 400,
    "staff_without_cards": 20,
    "security_without_cards": 30,
    "coverage_percentage": 91.43,
    "recent_cards_30_days": 150
  },
  "cards_by_type": {
    "student": 4600,
    "staff": 180,
    "security": 20
  }
}
```

---

## Student Card Management

### 1. List Students Without Cards
**GET** `/api/cards/students-without-cards/`

Returns active students who don't have cards yet.

**Query Parameters:**
- `search` (string): Search by name, registration number, or department
- `department` (string): Filter by department

**Response:**
```json
{
  "count": 400,
  "students": [
    {
      "student_uuid": "uuid-here",
      "registration_number": "DIT/2024/01234",
      "full_name": "John Doe Smith",
      "department": "Computer Science",
      "student_status": "Active"
    }
  ],
  "message": "Found 400 students without cards."
}
```

### 2. Bulk Create Student Cards
**POST** `/api/cards/bulk-create-student-cards/`

Creates cards for multiple students in a single operation.

**Request Body:**
```json
{
  "student_uuids": [
    "uuid1",
    "uuid2",
    "uuid3"
  ],
  "generate_rfid": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Created 2 student cards, 1 errors.",
  "created_cards": [
    {
      "card_uuid": "new-uuid-1",
      "rfid_number": "RF123456789",
      "student": {
        "registration_number": "DIT/2024/01234"
      }
    }
  ],
  "errors": [
    {
      "student_uuid": "uuid3",
      "errors": {
        "non_field_errors": ["Student already has a card"]
      }
    }
  ],
  "summary": {
    "total_requested": 3,
    "successful": 2,
    "failed": 1
  }
}
```

### 3. Print Student Card
**GET/POST** `/api/cards/{card_uuid}/print-student-card/`

Generates and downloads a PDF of the student ID card.

**Response:** PDF file download with filename `Student_ID_Card_{registration_number}.pdf`

---

## Staff Card Management

### 1. List Staff Without Cards
**GET** `/api/cards/staff-without-cards/`

Returns active staff members who don't have cards yet.

**Query Parameters:**
- `search` (string): Search by name, staff number, or department
- `department` (string): Filter by department

**Response:**
```json
{
  "count": 20,
  "staff": [
    {
      "staff_uuid": "uuid-here",
      "staff_number": "STAFF/2024/001",
      "full_name": "Jane Smith Johnson",
      "department": "Human Resources",
      "position": "HR Manager",
      "employment_status": "Active"
    }
  ],
  "message": "Found 20 staff without cards."
}
```

### 2. Bulk Create Staff Cards
**POST** `/api/cards/bulk-create-staff-cards/`

Creates cards for multiple staff members in a single operation.

**Request Body:**
```json
{
  "staff_uuids": [
    "uuid1",
    "uuid2"
  ],
  "generate_rfid": true
}
```

### 3. Print Staff Card
**GET/POST** `/api/cards/{card_uuid}/print-staff-card/`

Generates and downloads a PDF of the staff ID card.

**Response:** PDF file download with filename `Staff_ID_Card_{staff_number}.pdf`

---

## Security Personnel Card Management

### 1. List Security Personnel Without Cards
**GET** `/api/cards/security-without-cards/`

Returns active security personnel who don't have cards yet.

**Query Parameters:**
- `search` (string): Search by name, employee ID, or badge number

**Response:**
```json
{
  "count": 30,
  "security": [
    {
      "security_id": "uuid-here",
      "employee_id": "SEC/2024/001",
      "badge_number": "BADGE001",
      "full_name": "Michael Security Officer",
      "phone_number": "+255123456789"
    }
  ],
  "message": "Found 30 security personnel without cards."
}
```

### 2. Bulk Create Security Cards
**POST** `/api/cards/bulk-create-security-cards/`

Creates cards for multiple security personnel in a single operation.

**Request Body:**
```json
{
  "security_uuids": [
    "uuid1",
    "uuid2"
  ],
  "generate_rfid": true
}
```

### 3. Print Security Card
**GET/POST** `/api/cards/{card_uuid}/print-security-card/`

Generates and downloads a PDF of the security personnel ID card.

**Response:** PDF file download with filename `Security_ID_Card_{employee_id}.pdf`

---

## Card Verification Endpoints

These endpoints are public (no authentication required) and are used for QR code verification.

### 1. Verify Student Card
**GET** `/api/cards/verify/student/{student_uuid}/`

Verifies a student's identity via QR code or direct link.

**Response:**
```json
{
  "success": true,
  "verified": true,
  "student": {
    "registration_number": "DIT/2024/01234",
    "full_name": "John Doe Smith",
    "department": "Computer Science",
    "program": "BACHELOR OF ENGINEERING",
    "class_code": "CS2024A",
    "status": "Active",
    "academic_status": "Current",
    "photo_url": "https://example.com/media/photos/student.jpg",
    "has_card": true,
    "card_active": true
  },
  "verified_at": "2025-10-10T15:30:00Z",
  "institution": "DAR ES SALAAM INSTITUTE OF TECHNOLOGY"
}
```

### 2. Verify Staff Card
**GET** `/api/cards/verify/staff/{staff_uuid}/`

Verifies a staff member's identity via QR code or direct link.

**Response:**
```json
{
  "success": true,
  "verified": true,
  "staff": {
    "staff_number": "STAFF/2024/001",
    "full_name": "Jane Smith Johnson",
    "department": "Human Resources",
    "position": "HR Manager",
    "employment_status": "Active",
    "photo_url": "https://example.com/media/photos/staff.jpg",
    "has_card": true,
    "card_active": true
  },
  "verified_at": "2025-10-10T15:30:00Z",
  "institution": "DAR ES SALAAM INSTITUTE OF TECHNOLOGY"
}
```

### 3. Verify Security Card
**GET** `/api/cards/verify/security/{security_uuid}/`

Verifies a security personnel's identity via QR code or direct link.

**Response:**
```json
{
  "success": true,
  "verified": true,
  "security": {
    "employee_id": "SEC/2024/001",
    "badge_number": "BADGE001",
    "full_name": "Michael Security Officer",
    "phone_number": "+255123456789",
    "hire_date": "2024-01-15",
    "has_card": true,
    "card_active": true
  },
  "verified_at": "2025-10-10T15:30:00Z",
  "institution": "DAR ES SALAAM INSTITUTE OF TECHNOLOGY"
}
```

---

## Card Activation/Deactivation

### 1. Deactivate Card
**PATCH** `/api/cards/{card_uuid}/deactivate/`

Deactivates a card (sets is_active to False).

**Response:**
```json
{
  "message": "Card deactivated successfully.",
  "data": {
    "card_uuid": "uuid-here",
    "is_active": false,
    "updated_at": "2025-10-10T15:30:00Z"
  }
}
```

### 2. Activate Card
**PATCH** `/api/cards/{card_uuid}/activate/`

Activates a card (sets is_active to True).

**Response:**
```json
{
  "message": "Card activated successfully.",
  "data": {
    "card_uuid": "uuid-here",
    "is_active": true,
    "updated_at": "2025-10-10T15:30:00Z"
  }
}
```

---

## Error Handling

The API uses standard HTTP status codes and returns error information in JSON format:

### Common Error Responses

**400 Bad Request:**
```json
{
  "error": "student_uuids list is required."
}
```

**401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**404 Not Found:**
```json
{
  "success": false,
  "verified": false,
  "message": "Student not found or inactive."
}
```

**500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to generate ID card PDF: [error details]"
}
```

---

## Data Models

### Card Model Fields
- `card_uuid` (UUID): Unique identifier for the card
- `rfid_number` (string): RFID number of the physical card
- `card_type` (string): Type of card (student/staff/security)
- `student` (FK): Link to Student model (for student cards)
- `staff` (FK): Link to Staff model (for staff cards)
- `security_personnel` (FK): Link to SecurityPersonnel model (for security cards)
- `is_active` (boolean): Whether the card is currently active
- `issued_date` (datetime): Date when the card was issued
- `expiry_date` (datetime): Optional expiry date
- `created_at` (datetime): Record creation timestamp
- `updated_at` (datetime): Record last update timestamp

### Card Type Validation
- Each card can only be linked to one entity (student OR staff OR security)
- The `card_type` field must match the linked entity
- Validation ensures data consistency across the system

---

## Logging and Audit Trail

The system maintains comprehensive audit trails:

### Print Logs (IDCardPrintLog)
- Tracks who printed cards and when
- Records PDF generation success/failure
- Links to the appropriate entity type

### Verification Logs (IDCardVerificationLog)
- Tracks QR code scans and verifications
- Records IP addresses and user agents
- Monitors verification patterns for security

---

## Usage Examples

### Example 1: Create Student Cards in Bulk
```bash
curl -X POST /api/cards/bulk-create-student-cards/ \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "student_uuids": ["uuid1", "uuid2", "uuid3"],
    "generate_rfid": true
  }'
```

### Example 2: Search for Cards
```bash
curl -X GET "/api/cards/?search=john&card_type=student&is_active=true" \
  -H "Authorization: Bearer your-token"
```

### Example 3: Verify Student via QR Code
```bash
curl -X GET /api/cards/verify/student/123e4567-e89b-12d3-a456-426614174000/
```

---

## Security Considerations

1. **Authentication Required**: All management endpoints require valid authentication
2. **Role-Based Access**: Different permissions for Administrators vs Registration Officers
3. **Public Verification**: Verification endpoints are intentionally public for QR scanning
4. **Audit Logging**: All actions are logged with user information and timestamps
5. **Data Validation**: Strict validation prevents invalid card configurations
6. **RFID Security**: RFID numbers are unique and auto-generated to prevent conflicts

---

## Rate Limiting

Consider implementing rate limiting for:
- Bulk operations (card creation)
- Verification endpoints (to prevent abuse)
- Print operations (to manage server resources)

---

## Troubleshooting

### Common Issues

1. **"Student already has a card" error**
   - Check if the student already has an active card
   - Use the students-without-cards endpoint to get eligible students

2. **PDF generation fails**
   - Ensure the PDF service is properly configured
   - Check that student photos exist and are accessible
   - Verify server has sufficient memory for PDF generation

3. **Permission denied errors**
   - Verify user authentication and role
   - Check that the user type has appropriate permissions

4. **Card type validation errors**
   - Ensure the card_type matches the provided UUID type
   - Verify that only one entity UUID is provided per card