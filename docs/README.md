# Smart Access Card Management System Documentation

## Overview

The Smart Access Card Management System is a comprehensive multi-entity card management solution for Dar es Salaam Institute of Technology. It supports RFID access cards for **students**, **staff**, and **security personnel** with full CRUD operations, bulk management capabilities, and detailed tracking of card lifecycle.

## System Capabilities

### Multi-Entity Support
- **Student Cards**: Academic identification and access control
- **Staff Cards**: Employee identification and facility access  
- **Security Personnel Cards**: Security team identification and specialized access

### Core Features
- Individual and bulk card creation
- PDF card printing with entity-specific templates
- QR code verification for all card types
- Comprehensive audit logging and tracking
- Role-based access control (Administrator/Registration Officer)
- Real-time statistics and reporting

## Table of Contents

1. [Models](#models)
2. [API Endpoints](#api-endpoints)
3. [Permissions](#permissions)
4. [Usage Examples](#usage-examples)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Audit Logging](#audit-logging)

## Models

### Card Model

The `Card` model represents an RFID access card assigned to a student.

```python
class Card(models.Model):
    card_uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    rfid_number = models.CharField(max_length=50, unique=True)
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    issued_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Key Features:**
- **One-to-One Relationship**: Each student can have only one active card
- **UUID Primary Key**: Uses UUID for card identification instead of sequential IDs
- **RFID Number**: Unique identifier for the physical card
- **Status Tracking**: Track active/inactive status and expiry dates
- **Audit Trail**: Automatic timestamps for creation and updates

## API Endpoints

### Base URL: `/api/cards/`

### 1. List Cards
**GET** `/api/cards/`

Lists all cards with pagination, filtering, and search capabilities.

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)
- `search` - Search in RFID number, student names, registration number, department
- `is_active` - Filter by card status (true/false)
- `student__department` - Filter by student department
- `student__student_status` - Filter by student status
- `ordering` - Sort by fields (created_at, issued_date, student__surname, rfid_number)

**Response:**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/cards/?page=2",
  "previous": null,
  "results": [
    {
      "card_uuid": "123e4567-e89b-12d3-a456-426614174000",
      "rfid_number": "1234567890",
      "student_name": "John Doe",
      "registration_number": "REG001",
      "department": "Computer Science",
      "student_status": "Enrolled",
      "is_active": true,
      "issued_date": "2024-01-15T10:30:00Z",
      "expiry_date": null,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "summary": {
    "total_cards": 150,
    "active_cards": 145,
    "inactive_cards": 5
  }
}
```

### 2. Create Card
**POST** `/api/cards/`

Creates a new card for a student.

**Request Body:**
```json
{
  "student_uuid": "123e4567-e89b-12d3-a456-426614174000",
  "rfid_number": "1234567890",  // Optional if generate_rfid is true
  "generate_rfid": false,       // Set to true to auto-generate RFID
  "expiry_date": "2025-12-31T23:59:59Z"  // Optional
}
```

**Response:**
```json
{
  "card_uuid": "987fcdeb-51a2-43d1-9f4e-5678901234ab",
  "rfid_number": "1234567890",
  "student_info": {
    "student_uuid": "123e4567-e89b-12d3-a456-426614174000",
    "first_name": "John",
    "surname": "Doe",
    "registration_number": "REG001",
    "department": "Computer Science"
  },
  "is_active": true,
  "issued_date": "2024-01-15T10:30:00Z",
  "created_by": {
    "username": "admin",
    "user_type": "administrator",
    "full_name": "System Administrator"
  }
}
```

### 3. Get Card Details
**GET** `/api/cards/{card_uuid}/`

Retrieves detailed information about a specific card.

**Response:**
```json
{
  "card_uuid": "987fcdeb-51a2-43d1-9f4e-5678901234ab",
  "rfid_number": "1234567890",
  "student_info": {
    // Full student details
  },
  "is_active": true,
  "issued_date": "2024-01-15T10:30:00Z",
  "expiry_date": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "user_permissions": {
    "can_modify": true,
    "can_deactivate": true,
    "can_delete": false  // Only administrators
  }
}
```

### 4. Update Card
**PUT/PATCH** `/api/cards/{card_uuid}/`

Updates card information.

**Request Body:**
```json
{
  "rfid_number": "0987654321",
  "is_active": true,
  "expiry_date": "2025-12-31T23:59:59Z"
}
```

### 5. Delete Card
**DELETE** `/api/cards/{card_uuid}/`

Deletes a card. **Only available to administrators.**

### 6. Activate Card
**PATCH** `/api/cards/{card_uuid}/activate/`

Activates an inactive card.

**Response:**
```json
{
  "message": "Card activated successfully.",
  "data": {
    // Updated card details
  }
}
```

### 7. Deactivate Card
**PATCH** `/api/cards/{card_uuid}/deactivate/`

Deactivates an active card.

**Response:**
```json
{
  "message": "Card deactivated successfully.",
  "data": {
    // Updated card details
  }
}
```

### 8. Students Without Cards
**GET** `/api/cards/students-without-cards/`

Gets a list of students who don't have cards yet.

**Query Parameters:**
- `search` - Search in student names, registration number, department
- `department` - Filter by department

**Response:**
```json
{
  "count": 25,
  "students": [
    {
      "student_uuid": "123e4567-e89b-12d3-a456-426614174000",
      "registration_number": "REG002",
      "full_name": "Jane Smith",
      "department": "Electrical Engineering",
      "student_status": "Enrolled",
      "created_at": "2024-01-10T08:00:00Z"
    }
  ],
  "message": "Found 25 students without cards."
}
```

### 9. Card Statistics
**GET** `/api/cards/statistics/`

Provides comprehensive statistics about the card system.

**Response:**
```json
{
  "summary": {
    "total_students": 200,
    "total_cards": 175,
    "active_cards": 170,
    "inactive_cards": 5,
    "students_without_cards": 25,
    "coverage_percentage": 87.5,
    "recent_cards_30_days": 15
  },
  "cards_by_department": [
    {
      "student__department": "Computer Science",
      "count": 85
    },
    {
      "student__department": "Electrical Engineering",
      "count": 45
    }
  ],
  "user_info": {
    "current_user": "admin",
    "user_type": "administrator",
    "generated_at": "2024-01-15T10:30:00Z"
  }
}
```

### 10. Bulk Create Cards
**POST** `/api/cards/bulk-create/`

Creates cards for multiple students at once.

**Request Body:**
```json
{
  "student_uuids": [
    "123e4567-e89b-12d3-a456-426614174000",
    "456e7890-e89b-12d3-a456-426614174001"
  ],
  "generate_rfid": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Created 2 cards, 0 errors.",
  "created_cards": [
    // Array of created card objects
  ],
  "errors": [],
  "summary": {
    "total_requested": 2,
    "successful": 2,
    "failed": 0
  },
  "created_by": {
    "username": "admin",
    "user_type": "administrator",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## Permissions

### User Types and Access Levels

| Action | Administrator | Registration Officer |
|--------|---------------|---------------------|
| List Cards | ✅ | ✅ |
| Create Card | ✅ | ✅ |
| View Card Details | ✅ | ✅ |
| Update Card | ✅ | ✅ |
| Activate/Deactivate | ✅ | ✅ |
| Delete Card | ✅ | ❌ |
| Bulk Operations | ✅ | ✅ |
| Statistics | ✅ | ✅ |

### Permission Classes

- `IsAdministrator`: Only administrators
- `CanManageCards`: Both administrators and registration officers

## Usage Examples

### 1. Creating a Card with Auto-Generated RFID

```bash
curl -X POST http://localhost:8000/api/cards/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_uuid": "123e4567-e89b-12d3-a456-426614174000",
    "generate_rfid": true
  }'
```

### 2. Searching for Cards

```bash
# Search by student name
curl "http://localhost:8000/api/cards/?search=John%20Doe" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by department
curl "http://localhost:8000/api/cards/?student__department=Computer%20Science" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Get inactive cards
curl "http://localhost:8000/api/cards/?is_active=false" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Bulk Card Creation

```bash
curl -X POST http://localhost:8000/api/cards/bulk-create/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_uuids": [
      "123e4567-e89b-12d3-a456-426614174000",
      "456e7890-e89b-12d3-a456-426614174001"
    ],
    "generate_rfid": true
  }'
```

### 4. Deactivating a Card

```bash
curl -X PATCH http://localhost:8000/api/cards/987fcdeb-51a2-43d1-9f4e-5678901234ab/deactivate/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Error Handling

### Common Error Responses

**400 Bad Request - Student Already Has Card:**
```json
{
  "student": ["Student John Doe already has a card assigned."]
}
```

**400 Bad Request - Duplicate RFID:**
```json
{
  "rfid_number": ["This RFID number is already in use."]
}
```

**404 Not Found:**
```json
{
  "detail": "Card not found."
}
```

**403 Forbidden:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**429 Too Many Requests:**
```json
{
  "detail": "Request rate limit exceeded. Try again later."
}
```

### Validation Rules

1. **Student Validation:**
   - Student must exist and be active
   - Student cannot already have a card

2. **RFID Validation:**
   - Must be unique across all cards
   - Required unless auto-generation is enabled

3. **Permission Validation:**
   - User must be authenticated
   - User must have appropriate permissions

## Rate Limiting

Rate limits are applied to prevent abuse:

- **Card Creation**: 30 requests per minute per user
- **Bulk Operations**: 5 requests per minute per user
- **Search/List**: 60 requests per minute per user

## Audit Logging

All card operations are logged with the following information:

- **User Information**: Username, user type, timestamp
- **Action Performed**: Create, update, activate, deactivate, delete
- **Card Details**: Card UUID, affected student
- **IP Address**: For security tracking

### Log Examples

```
INFO: Card creation initiated by admin (administrator)
INFO: Card created successfully by admin (administrator): 987fcdeb-51a2-43d1-9f4e-5678901234ab for student REG001
WARNING: Card 987fcdeb-51a2-43d1-9f4e-5678901234ab deactivated by reg_officer (registration_officer)
```

## Database Indexes

For optimal performance, the following indexes are created:

- `rfid_number` - For fast RFID lookups
- `card_uuid` - For UUID-based queries
- `is_active` - For status filtering
- `student` - For student-based queries

## Security Considerations

1. **UUID Usage**: Cards use UUIDs instead of sequential IDs to prevent enumeration attacks
2. **RFID Uniqueness**: Enforced at database level to prevent conflicts
3. **Permission Checks**: All operations require appropriate user permissions
4. **Audit Logging**: All operations are logged for security monitoring
5. **Rate Limiting**: Prevents abuse and DoS attacks

## Integration with Access Control

The card management system integrates with the access control system by:

1. **RFID Lookups**: Access gates can query cards by RFID number
2. **Status Validation**: Only active cards grant access
3. **Student Information**: Access logs include student details via card relationship
4. **Real-time Updates**: Card status changes are immediately effective

## Troubleshooting

### Common Issues

1. **Card Creation Fails - Student Already Has Card**
   - Check if student already has an existing card
   - Use the students-without-cards endpoint to verify

2. **RFID Conflicts**
   - Ensure RFID numbers are unique
   - Use auto-generation to avoid conflicts

3. **Permission Denied**
   - Verify user has correct user_type
   - Check authentication token validity

4. **Performance Issues**
   - Use filtering and pagination for large datasets
   - Leverage database indexes for efficient queries

### Monitoring Endpoints

- `GET /api/cards/statistics/` - System health and usage metrics
- `GET /api/cards/students-without-cards/` - Coverage gaps
- Server logs for detailed operation tracking

---

## Quick Links

- **[Complete API Documentation](CARD_MANAGEMENT_API.md)** - Detailed endpoint documentation
- **[Multi-Card System Implementation](MULTI_CARD_SYSTEM_IMPLEMENTATION.md)** - Technical implementation details
- **[Staff Management API](STAFF_MANAGEMENT_API.md)** - Staff-specific endpoints
- **[Student Photo Upload API](STUDENT_PHOTO_UPLOAD_API.md)** - Photo management

## New Features (Multi-Card System)

### Entity-Specific Endpoints
Each entity type (student/staff/security) now has dedicated endpoints:

```
# Student Cards
GET    /api/cards/students-without-cards/
POST   /api/cards/bulk-create-student-cards/
GET    /api/cards/{card_uuid}/print-student-card/
GET    /api/cards/verify/student/{student_uuid}/

# Staff Cards  
GET    /api/cards/staff-without-cards/
POST   /api/cards/bulk-create-staff-cards/
GET    /api/cards/{card_uuid}/print-staff-card/
GET    /api/cards/verify/staff/{staff_uuid}/

# Security Cards
GET    /api/cards/security-without-cards/
POST   /api/cards/bulk-create-security-cards/
GET    /api/cards/{card_uuid}/print-security-card/
GET    /api/cards/verify/security/{security_uuid}/
```

### Enhanced Statistics
The statistics endpoint now provides comprehensive metrics across all entity types:
- Total personnel count by type
- Card coverage percentages
- Entity-specific without-card counts
- Recent activity tracking

---

**Last Updated**: October 10, 2025  
**Version**: 2.0 (Multi-Card System)  
**Maintainer**: Smart Access Development Team