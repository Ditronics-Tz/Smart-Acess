# Security Personnel Management API Documentation

## Overview
This document covers the Security Personnel Management endpoints for administrators in the Smart Access system. These endpoints allow administrators to perform complete CRUD operations on security personnel records.

## Base URL
```
http://localhost:8000/api/administrator/security-personnel/
```

---

## Authentication
All endpoints require JWT authentication with Administrator role.

**Required Headers:**
```
Authorization: Bearer <your_jwt_access_token>
Content-Type: application/json
```

---

## Endpoints

### 1. Create Security Personnel
**Endpoint:** `POST /api/administrator/security-personnel/create/`

**Description:** Create a new security personnel record

**Request Body:**
```json
{
    "employee_id": "EMP001",
    "badge_number": "BADGE001",
    "full_name": "John Smith",
    "phone_number": "+1234567890",
    "hire_date": "2024-01-15"
}
```

**Field Validation:**
- `employee_id`: Required, must be unique
- `badge_number`: Required, must be unique
- `full_name`: Required string
- `phone_number`: Optional phone number
- `hire_date`: Optional date in YYYY-MM-DD format

**Success Response (201):**
```json
{
    "security_id": "123e4567-e89b-12d3-a456-426614174000",
    "employee_id": "EMP001",
    "badge_number": "BADGE001",
    "full_name": "John Smith",
    "phone_number": "+1234567890",
    "hire_date": "2024-01-15",
    "termination_date": null,
    "is_active": true,
    "created_at": "2024-01-15T10:30:00.000000Z",
    "updated_at": "2024-01-15T10:30:00.000000Z",
    "deleted_at": null
}
```

---

### 2. List All Security Personnel
**Endpoint:** `GET /api/administrator/security-personnel/`

**Description:** Get paginated list of all security personnel with filtering and search

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)
- `search`: Search in full_name, employee_id, badge_number
- `is_active`: Filter by active status (true/false)
- `ordering`: Sort by fields (full_name, employee_id, badge_number, hire_date, created_at)

**Example URLs:**
```
GET /api/administrator/security-personnel/
GET /api/administrator/security-personnel/?page=2&page_size=10
GET /api/administrator/security-personnel/?search=john&is_active=true
GET /api/administrator/security-personnel/?ordering=-created_at
```

**Success Response (200):**
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/administrator/security-personnel/?page=2",
    "previous": null,
    "results": [
        {
            "security_id": "123e4567-e89b-12d3-a456-426614174000",
            "employee_id": "EMP001",
            "badge_number": "BADGE001",
            "full_name": "John Smith",
            "phone_number": "+1234567890",
            "hire_date": "2024-01-15",
            "termination_date": null,
            "is_active": true,
            "created_at": "2024-01-15T10:30:00.000000Z",
            "updated_at": "2024-01-15T10:30:00.000000Z",
            "deleted_at": null
        }
    ]
}
```

---

### 3. Get Single Security Personnel
**Endpoint:** `GET /api/administrator/security-personnel/<security_id>/`

**Description:** Get detailed information about a specific security personnel

**URL Parameters:**
- `security_id`: UUID of the security personnel

**Success Response (200):**
```json
{
    "security_id": "123e4567-e89b-12d3-a456-426614174000",
    "employee_id": "EMP001",
    "badge_number": "BADGE001",
    "full_name": "John Smith",
    "phone_number": "+1234567890",
    "hire_date": "2024-01-15",
    "termination_date": null,
    "is_active": true,
    "created_at": "2024-01-15T10:30:00.000000Z",
    "updated_at": "2024-01-15T10:30:00.000000Z",
    "deleted_at": null
}
```

---

### 4. Update Security Personnel
**Endpoint:** `PUT /api/administrator/security-personnel/<security_id>/update/`
**Endpoint:** `PATCH /api/administrator/security-personnel/<security_id>/update/`

**Description:** Update security personnel information (PUT = full update, PATCH = partial update)

**URL Parameters:**
- `security_id`: UUID of the security personnel

**Request Body (PATCH - partial update):**
```json
{
    "full_name": "John Smith Jr.",
    "phone_number": "+1234567891",
    "termination_date": "2024-12-31",
    "is_active": false
}
```

**Request Body (PUT - full update):**
```json
{
    "employee_id": "EMP001",
    "badge_number": "BADGE001",
    "full_name": "John Smith Jr.",
    "phone_number": "+1234567891",
    "hire_date": "2024-01-15",
    "termination_date": "2024-12-31",
    "is_active": false
}
```

**Success Response (200):**
```json
{
    "security_id": "123e4567-e89b-12d3-a456-426614174000",
    "employee_id": "EMP001",
    "badge_number": "BADGE001",
    "full_name": "John Smith Jr.",
    "phone_number": "+1234567891",
    "hire_date": "2024-01-15",
    "termination_date": "2024-12-31",
    "is_active": false,
    "created_at": "2024-01-15T10:30:00.000000Z",
    "updated_at": "2024-01-15T15:45:00.000000Z",
    "deleted_at": null
}
```

---

### 5. Delete Security Personnel (Soft Delete)
**Endpoint:** `DELETE /api/administrator/security-personnel/<security_id>/delete/`

**Description:** Soft delete security personnel (marks as deleted but keeps record)

**URL Parameters:**
- `security_id`: UUID of the security personnel

**Success Response (200):**
```json
{
    "message": "Security personnel soft deleted successfully",
    "deleted_at": "2024-01-15T16:00:00.000000Z",
    "is_active": false
}
```

---

### 6. Restore Security Personnel
**Endpoint:** `POST /api/administrator/security-personnel/<security_id>/restore/`

**Description:** Restore a previously soft-deleted security personnel

**URL Parameters:**
- `security_id`: UUID of the security personnel

**Success Response (200):**
```json
{
    "message": "Security personnel restored successfully",
    "data": {
        "security_id": "123e4567-e89b-12d3-a456-426614174000",
        "employee_id": "EMP001",
        "badge_number": "BADGE001",
        "full_name": "John Smith",
        "phone_number": "+1234567890",
        "hire_date": "2024-01-15",
        "termination_date": null,
        "is_active": true,
        "created_at": "2024-01-15T10:30:00.000000Z",
        "updated_at": "2024-01-15T16:05:00.000000Z",
        "deleted_at": null
    }
}
```

---

## Common Error Responses

### Authentication Errors
```json
// Missing token (401)
{
    "detail": "Authentication credentials were not provided."
}

// Invalid token (401)
{
    "detail": "Given token not valid for any token type"
}

// Not administrator (403)
{
    "detail": "You do not have permission to perform this action."
}
```

### Resource Errors
```json
// Security personnel not found (404)
{
    "detail": "Not found."
}

// Validation errors (400)
{
    "employee_id": ["This field is required."],
    "badge_number": ["Security personnel with this badge number already exists."]
}

// Cannot restore active record (400)
{
    "error": "Security personnel is not deleted and cannot be restored"
}
```

---

## Frontend Implementation Guide

### Complete Workflow for Security Personnel Management

#### 1. Get Admin JWT Token
```javascript
// Login first to get admin token
const loginResponse = await fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        username: 'admin_username',
        password: 'admin_password',
        user_type: 'administrator'
    })
});
const { access } = await loginResponse.json();
```

#### 2. List Security Personnel with Search/Filter
```javascript
const listPersonnel = async (page = 1, search = '', isActive = null) => {
    let url = `http://localhost:8000/api/administrator/security-personnel/?page=${page}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    if (isActive !== null) url += `&is_active=${isActive}`;
    
    const response = await fetch(url, {
        headers: {
            'Authorization': `Bearer ${access}`,
            'Content-Type': 'application/json'
        }
    });
    return await response.json();
};
```

#### 3. Create New Security Personnel
```javascript
const createPersonnel = async (personnelData) => {
    const response = await fetch('http://localhost:8000/api/administrator/security-personnel/create/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${access}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(personnelData)
    });
    return await response.json();
};
```

#### 4. Update Security Personnel
```javascript
const updatePersonnel = async (securityId, updateData) => {
    const response = await fetch(`http://localhost:8000/api/administrator/security-personnel/${securityId}/update/`, {
        method: 'PATCH',
        headers: {
            'Authorization': `Bearer ${access}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(updateData)
    });
    return await response.json();
};
```

#### 5. Delete Security Personnel
```javascript
const deletePersonnel = async (securityId) => {
    const response = await fetch(`http://localhost:8000/api/administrator/security-personnel/${securityId}/delete/`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${access}`,
            'Content-Type': 'application/json'
        }
    });
    return await response.json();
};
```

#### 6. Restore Security Personnel
```javascript
const restorePersonnel = async (securityId) => {
    const response = await fetch(`http://localhost:8000/api/administrator/security-personnel/${securityId}/restore/`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${access}`,
            'Content-Type': 'application/json'
        }
    });
    return await response.json();
};
```

### Error Handling
```javascript
const handleApiResponse = async (response) => {
    if (!response.ok) {
        const error = await response.json();
        if (response.status === 401) {
            // Redirect to login
            window.location.href = '/login';
        } else if (response.status === 403) {
            alert('Access denied. Administrator privileges required.');
        } else {
            console.error('API Error:', error);
        }
        throw new Error(error.detail || 'API request failed');
    }
    return await response.json();
};
```

### Recommended UI Flow
1. **Dashboard** → Display security personnel table with search/filter
2. **Add New** → Form to create new personnel
3. **View Details** → Show detailed personnel information
4. **Edit** → Form to update personnel data
5. **Delete** → Confirmation dialog then soft delete
6. **Restore** → Option to restore deleted personnel

This API provides complete CRUD functionality for managing security personnel in your Smart Access system! 🚀