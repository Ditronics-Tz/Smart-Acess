# Administrator Module - Security Personnel Management API

## Overview

The Administrator module provides a comprehensive REST API for managing security personnel in the Smart Access system. This module handles CRUD operations for security personnel records with JWT-based authentication and role-based permissions.

## Features

- ✅ Complete CRUD operations (Create, Read, Update, Delete)
- ✅ Soft delete with restore functionality
- ✅ JWT-based authentication
- ✅ Role-based permissions (Administrator only)
- ✅ UUID-based primary keys
- ✅ Data validation and constraints
- ✅ Filtering and pagination support
- ✅ Database indexing for performance

## Model Structure

### SecurityPersonnel

The main model for storing security personnel information:

```python
class SecurityPersonnel(models.Model):
    security_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.CharField(max_length=50, unique=True)
    badge_number = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    hire_date = models.DateField(null=True, blank=True)
    termination_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
```

#### Fields Description

- **security_id**: UUID primary key, auto-generated
- **employee_id**: Unique employee identifier (string)
- **badge_number**: Unique badge number (string)
- **full_name**: Full name of the security personnel
- **phone_number**: Optional contact phone number
- **hire_date**: Date when the personnel was hired
- **termination_date**: Date when the personnel was terminated (if applicable)
- **is_active**: Boolean flag for active status
- **created_at**: Timestamp of record creation
- **updated_at**: Timestamp of last update
- **deleted_at**: Timestamp of soft deletion (null if not deleted)

#### Constraints

- Termination date must be after or equal to hire date
- Employee ID and badge number must be unique

## API Endpoints

### Base URL
```
/api/administrator/security-personnel/
```

### Authentication
All endpoints require JWT authentication with Administrator role.

#### Headers Required:
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

### Endpoints Overview

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/` | List all security personnel | Administrator |
| POST | `/create/` | Create new security personnel | Administrator |
| GET | `/{uuid}/` | Get specific security personnel | Administrator |
| PUT/PATCH | `/{uuid}/update/` | Update security personnel | Administrator |
| DELETE | `/{uuid}/delete/` | Soft delete security personnel | Administrator |
| POST | `/{uuid}/restore/` | Restore deleted security personnel | Administrator |

### 1. List Security Personnel
```http
GET /api/administrator/security-personnel/
```

**Query Parameters:**
- `employee_id`: Filter by employee ID
- `badge_number`: Filter by badge number
- `full_name`: Filter by full name (case-insensitive partial match)
- `is_active`: Filter by active status (true/false)
- `page`: Page number for pagination
- `page_size`: Number of records per page

**Example Response:**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/administrator/security-personnel/?page=2",
  "previous": null,
  "results": [
    {
      "security_id": "b462e657-4d37-49c5-878d-02c0070f9fd5",
      "employee_id": "EMP001",
      "badge_number": "BADGE001",
      "full_name": "Jane Doe",
      "phone_number": "+1234567890",
      "hire_date": "2024-01-15",
      "termination_date": null,
      "is_active": true,
      "created_at": "2025-08-25T19:14:30.123456Z",
      "updated_at": "2025-08-25T19:14:30.123456Z",
      "deleted_at": null
    }
  ]
}
```

### 2. Create Security Personnel
```http
POST /api/administrator/security-personnel/create/
```

**Request Body:**
```json
{
  "employee_id": "EMP002",
  "badge_number": "BADGE002",
  "full_name": "John Smith",
  "phone_number": "+1234567891",
  "hire_date": "2024-02-01"
}
```

**Response:**
```json
{
  "security_id": "c573f768-5e48-5a06-989e-13d1080g0ae6",
  "employee_id": "EMP002",
  "badge_number": "BADGE002",
  "full_name": "John Smith",
  "phone_number": "+1234567891",
  "hire_date": "2024-02-01",
  "termination_date": null,
  "is_active": true,
  "created_at": "2025-08-25T19:30:00.123456Z",
  "updated_at": "2025-08-25T19:30:00.123456Z",
  "deleted_at": null
}
```

### 3. Get Security Personnel Details
```http
GET /api/administrator/security-personnel/{security_id}/
```

**Response:**
```json
{
  "security_id": "b462e657-4d37-49c5-878d-02c0070f9fd5",
  "employee_id": "EMP001",
  "badge_number": "BADGE001",
  "full_name": "Jane Doe",
  "phone_number": "+1234567890",
  "hire_date": "2024-01-15",
  "termination_date": null,
  "is_active": true,
  "created_at": "2025-08-25T19:14:30.123456Z",
  "updated_at": "2025-08-25T19:14:30.123456Z",
  "deleted_at": null
}
```

### 4. Update Security Personnel
```http
PUT /api/administrator/security-personnel/{security_id}/update/
PATCH /api/administrator/security-personnel/{security_id}/update/
```

**Request Body (PUT - all fields required):**
```json
{
  "employee_id": "EMP001",
  "badge_number": "BADGE001",
  "full_name": "Jane Doe Smith",
  "phone_number": "+1234567890",
  "hire_date": "2024-01-15",
  "termination_date": "2024-12-31",
  "is_active": false
}
```

**Request Body (PATCH - partial update):**
```json
{
  "full_name": "Jane Doe Smith",
  "termination_date": "2024-12-31",
  "is_active": false
}
```

### 5. Delete Security Personnel (Soft Delete)
```http
DELETE /api/administrator/security-personnel/{security_id}/delete/
```

**Response:**
```json
{
  "message": "Security personnel deleted successfully"
}
```

### 6. Restore Security Personnel
```http
POST /api/administrator/security-personnel/{security_id}/restore/
```

**Response:**
```json
{
  "message": "Security personnel restored successfully"
}
```

## Error Responses

### Authentication Errors
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Permission Errors
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### Validation Errors
```json
{
  "employee_id": ["This field is required."],
  "badge_number": ["Security personnel with this badge number already exists."]
}
```

### Not Found Errors
```json
{
  "detail": "Not found."
}
```

## Database Indexes

The following indexes are created for optimal performance:

- `idx_security_employee_id` - Index on employee_id field
- `idx_security_badge` - Index on badge_number field
- `idx_security_active` - Index on is_active field
- `idx_security_deleted` - Index on deleted_at field

## Permissions

### IsAdministrator Permission

Custom permission class that ensures only users with administrator role can access the endpoints.

```python
class IsAdministrator(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'role') and 
            request.user.role == 'administrator'
        )
```

## Usage Examples

### Getting JWT Token

First, obtain a JWT token by authenticating:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "your_password"
  }'
```

### Creating Security Personnel

```bash
curl -X POST http://localhost:8000/api/administrator/security-personnel/create/ \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP003",
    "badge_number": "BADGE003",
    "full_name": "Alice Johnson",
    "phone_number": "+1234567892",
    "hire_date": "2024-03-01"
  }'
```

### Listing Security Personnel with Filters

```bash
curl -X GET "http://localhost:8000/api/administrator/security-personnel/?is_active=true&page=1&page_size=10" \
  -H "Authorization: Bearer your_jwt_token"
```

### Updating Security Personnel

```bash
curl -X PATCH http://localhost:8000/api/administrator/security-personnel/b462e657-4d37-49c5-878d-02c0070f9fd5/update/ \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567899"
  }'
```

### Soft Deleting Security Personnel

```bash
curl -X DELETE http://localhost:8000/api/administrator/security-personnel/b462e657-4d37-49c5-878d-02c0070f9fd5/delete/ \
  -H "Authorization: Bearer your_jwt_token"
```

### Restoring Security Personnel

```bash
curl -X POST http://localhost:8000/api/administrator/security-personnel/b462e657-4d37-49c5-878d-02c0070f9fd5/restore/ \
  -H "Authorization: Bearer your_jwt_token"
```

## File Structure

```
adminstrator/
├── __init__.py
├── admin.py              # Django admin configuration
├── apps.py               # App configuration
├── models.py             # SecurityPersonnel model
├── serializers.py        # DRF serializers
├── views.py              # API views
├── urls.py               # URL routing
├── permissions.py        # Custom permissions
├── tests.py              # Unit tests
├── README.md             # This documentation
└── migrations/
    ├── __init__.py
    └── 0001_initial.py   # Initial migration
```

## Testing

Run the tests for this module:

```bash
python manage.py test adminstrator
```

## Development Notes

1. **UUID Primary Keys**: This module uses UUID primary keys instead of integer IDs for better security and scalability.

2. **Soft Delete**: Records are not permanently deleted but marked with a `deleted_at` timestamp.

3. **Validation**: The model includes constraints to ensure data integrity (e.g., termination date >= hire date).

4. **Performance**: Database indexes are strategically placed on frequently queried fields.

5. **Security**: All endpoints require JWT authentication and administrator role permissions.

## Future Enhancements

- [ ] Add bulk operations (bulk create, update, delete)
- [ ] Implement audit logging for all operations
- [ ] Add export functionality (CSV, PDF)
- [ ] Implement advanced search with full-text search
- [ ] Add file upload for profile pictures
- [ ] Implement notification system for personnel changes

## Troubleshooting

### Common Issues

1. **404 Errors**: Ensure you're using the correct UUID format in URLs
2. **Permission Denied**: Verify JWT token is valid and user has administrator role
3. **Validation Errors**: Check required fields and unique constraints
4. **Database Errors**: Ensure migrations are applied and database is accessible

### Debug Mode

Set `DEBUG = True` in settings.py for detailed error messages during development.

---

For more information, refer to the main project documentation or contact the development team.
