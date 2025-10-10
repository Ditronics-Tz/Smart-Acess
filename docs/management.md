# Smart Access Administrator API Documentation

## Overview
This document covers the complete API endpoints for administrators in the Smart Access system, including Security Personnel, Physical Locations, and Access Gates management. These endpoints allow administrators to perform complete CRUD operations with soft delete functionality.

## Authentication
All endpoints require JWT authentication with Administrator role.

**Required Headers:**
```
Authorization: Bearer <your_jwt_access_token>
Content-Type: application/json
```

---

# Security Personnel Management API Documentation

## Base URL
```
http://localhost:8000/api/administrator/security-personnel/
```

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

# Physical Locations Management API Documentation

## Base URL
```
http://localhost:8000/api/administrator/physical-locations/
```

## Endpoints

### 1. Create Physical Location
**Endpoint:** `POST /api/administrator/physical-locations/create/`

**Description:** Create a new physical location record

**Request Body:**
```json
{
    "location_name": "Main Campus",
    "location_type": "campus",
    "description": "Primary campus location",
    "is_restricted": false
}
```

**Field Validation:**
- `location_name`: Required string
- `location_type`: Required choice from ['campus', 'building', 'floor', 'room', 'gate', 'area']
- `description`: Optional text
- `is_restricted`: Optional boolean (default: false)

**Success Response (201):**
```json
{
    "location_id": "456e7890-e89b-12d3-a456-426614174001",
    "location_name": "Main Campus",
    "location_type": "campus",
    "description": "Primary campus location",
    "is_restricted": false,
    "created_at": "2024-01-15T10:30:00.000000Z",
    "updated_at": "2024-01-15T10:30:00.000000Z",
    "deleted_at": null
}
```

### 2. List All Physical Locations
**Endpoint:** `GET /api/administrator/physical-locations/`

**Description:** Get paginated list of all physical locations with filtering and search

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)
- `search`: Search in location_name
- `location_type`: Filter by location type
- `is_restricted`: Filter by restriction status (true/false)
- `ordering`: Sort by fields (location_name, location_type, created_at)

**Example URLs:**
```
GET /api/administrator/physical-locations/
GET /api/administrator/physical-locations/?location_type=building&is_restricted=true
GET /api/administrator/physical-locations/?search=main&ordering=-created_at
```

**Success Response (200):**
```json
{
    "count": 10,
    "next": null,
    "previous": null,
    "results": [
        {
            "location_id": "456e7890-e89b-12d3-a456-426614174001",
            "location_name": "Main Campus",
            "location_type": "campus",
            "description": "Primary campus location",
            "is_restricted": false,
            "created_at": "2024-01-15T10:30:00.000000Z",
            "updated_at": "2024-01-15T10:30:00.000000Z",
            "deleted_at": null
        }
    ]
}
```

### 3. Get Single Physical Location
**Endpoint:** `GET /api/administrator/physical-locations/<location_id>/`

**Description:** Get detailed information about a specific physical location

**URL Parameters:**
- `location_id`: UUID of the physical location

**Success Response (200):**
```json
{
    "location_id": "456e7890-e89b-12d3-a456-426614174001",
    "location_name": "Main Campus",
    "location_type": "campus",
    "description": "Primary campus location",
    "is_restricted": false,
    "created_at": "2024-01-15T10:30:00.000000Z",
    "updated_at": "2024-01-15T10:30:00.000000Z",
    "deleted_at": null
}
```

### 4. Update Physical Location
**Endpoint:** `PUT /api/administrator/physical-locations/<location_id>/update/`
**Endpoint:** `PATCH /api/administrator/physical-locations/<location_id>/update/`

**Description:** Update physical location information (PUT = full update, PATCH = partial update)

**URL Parameters:**
- `location_id`: UUID of the physical location

**Request Body (PATCH - partial update):**
```json
{
    "location_name": "Updated Campus Name",
    "is_restricted": true
}
```

**Success Response (200):**
```json
{
    "location_id": "456e7890-e89b-12d3-a456-426614174001",
    "location_name": "Updated Campus Name",
    "location_type": "campus",
    "description": "Primary campus location",
    "is_restricted": true,
    "created_at": "2024-01-15T10:30:00.000000Z",
    "updated_at": "2024-01-15T15:45:00.000000Z",
    "deleted_at": null
}
```

### 5. Delete Physical Location (Soft Delete)
**Endpoint:** `DELETE /api/administrator/physical-locations/<location_id>/delete/`

**Description:** Soft delete physical location (marks as deleted but keeps record)

**URL Parameters:**
- `location_id`: UUID of the physical location

**Success Response (200):**
```json
{
    "message": "Physical location soft deleted successfully",
    "deleted_at": "2024-01-15T16:00:00.000000Z"
}
```

### 6. Restore Physical Location
**Endpoint:** `POST /api/administrator/physical-locations/<location_id>/restore/`

**Description:** Restore a previously soft-deleted physical location

**URL Parameters:**
- `location_id`: UUID of the physical location

**Success Response (200):**
```json
{
    "message": "Physical location restored successfully",
    "data": {
        "location_id": "456e7890-e89b-12d3-a456-426614174001",
        "location_name": "Main Campus",
        "location_type": "campus",
        "description": "Primary campus location",
        "is_restricted": false,
        "created_at": "2024-01-15T10:30:00.000000Z",
        "updated_at": "2024-01-15T16:05:00.000000Z",
        "deleted_at": null
    }
}
```

---

# Access Gates Management API Documentation

## Base URL
```
http://localhost:8000/api/administrator/access-gates/
```

## Endpoints

### 1. Create Access Gate
**Endpoint:** `POST /api/administrator/access-gates/create/`

**Description:** Create a new access gate record

**Request Body:**
```json
{
    "gate_code": "GATE001",
    "gate_name": "Main Entrance Gate",
    "location": "456e7890-e89b-12d3-a456-426614174001",
    "gate_type": "bidirectional",
    "hardware_id": "HW001",
    "ip_address": "192.168.1.100",
    "mac_address": "00:11:22:33:44:55",
    "status": "active",
    "emergency_override_enabled": false,
    "backup_power_available": true
}
```

**Field Validation:**
- `gate_code`: Required, must be unique
- `gate_name`: Required string
- `location`: Required UUID of physical location
- `gate_type`: Required choice from ['entry', 'exit', 'bidirectional'] (default: 'bidirectional')
- `hardware_id`: Required, must be unique
- `ip_address`: Optional IPv4/IPv6 address
- `mac_address`: Optional MAC address
- `status`: Required choice from ['active', 'inactive', 'maintenance', 'error'] (default: 'active')
- `emergency_override_enabled`: Optional boolean (default: false)
- `backup_power_available`: Optional boolean (default: false)

**Success Response (201):**
```json
{
    "gate_id": "789e0123-e89b-12d3-a456-426614174002",
    "gate_code": "GATE001",
    "gate_name": "Main Entrance Gate",
    "location": "456e7890-e89b-12d3-a456-426614174001",
    "location_name": "Main Campus",
    "location_type": "campus",
    "gate_type": "bidirectional",
    "hardware_id": "HW001",
    "ip_address": "192.168.1.100",
    "mac_address": "00:11:22:33:44:55",
    "status": "active",
    "emergency_override_enabled": false,
    "backup_power_available": true,
    "created_at": "2024-01-15T10:30:00.000000Z",
    "updated_at": "2024-01-15T10:30:00.000000Z",
    "deleted_at": null
}
```

### 2. List All Access Gates
**Endpoint:** `GET /api/administrator/access-gates/`

**Description:** Get paginated list of all access gates with filtering and search

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)
- `search`: Search in gate_code, gate_name, hardware_id
- `gate_type`: Filter by gate type
- `status`: Filter by status
- `location`: Filter by location UUID
- `ordering`: Sort by fields (gate_name, gate_code, created_at)

**Example URLs:**
```
GET /api/administrator/access-gates/
GET /api/administrator/access-gates/?status=active&gate_type=entry
GET /api/administrator/access-gates/?search=main&ordering=-created_at
```

**Success Response (200):**
```json
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "gate_id": "789e0123-e89b-12d3-a456-426614174002",
            "gate_code": "GATE001",
            "gate_name": "Main Entrance Gate",
            "location": "456e7890-e89b-12d3-a456-426614174001",
            "location_name": "Main Campus",
            "location_type": "campus",
            "gate_type": "bidirectional",
            "hardware_id": "HW001",
            "ip_address": "192.168.1.100",
            "mac_address": "00:11:22:33:44:55",
            "status": "active",
            "emergency_override_enabled": false,
            "backup_power_available": true,
            "created_at": "2024-01-15T10:30:00.000000Z",
            "updated_at": "2024-01-15T10:30:00.000000Z",
            "deleted_at": null
        }
    ]
}
```

### 3. Get Single Access Gate
**Endpoint:** `GET /api/administrator/access-gates/<gate_id>/`

**Description:** Get detailed information about a specific access gate

**URL Parameters:**
- `gate_id`: UUID of the access gate

**Success Response (200):**
```json
{
    "gate_id": "789e0123-e89b-12d3-a456-426614174002",
    "gate_code": "GATE001",
    "gate_name": "Main Entrance Gate",
    "location": "456e7890-e89b-12d3-a456-426614174001",
    "location_name": "Main Campus",
    "location_type": "campus",
    "gate_type": "bidirectional",
    "hardware_id": "HW001",
    "ip_address": "192.168.1.100",
    "mac_address": "00:11:22:33:44:55",
    "status": "active",
    "emergency_override_enabled": false,
    "backup_power_available": true,
    "created_at": "2024-01-15T10:30:00.000000Z",
    "updated_at": "2024-01-15T10:30:00.000000Z",
    "deleted_at": null
}
```

### 4. Update Access Gate
**Endpoint:** `PUT /api/administrator/access-gates/<gate_id>/update/`
**Endpoint:** `PATCH /api/administrator/access-gates/<gate_id>/update/`

**Description:** Update access gate information (PUT = full update, PATCH = partial update)

**URL Parameters:**
- `gate_id`: UUID of the access gate

**Request Body (PATCH - partial update):**
```json
{
    "status": "maintenance",
    "emergency_override_enabled": true
}
```

**Success Response (200):**
```json
{
    "gate_id": "789e0123-e89b-12d3-a456-426614174002",
    "gate_code": "GATE001",
    "gate_name": "Main Entrance Gate",
    "location": "456e7890-e89b-12d3-a456-426614174001",
    "location_name": "Main Campus",
    "location_type": "campus",
    "gate_type": "bidirectional",
    "hardware_id": "HW001",
    "ip_address": "192.168.1.100",
    "mac_address": "00:11:22:33:44:55",
    "status": "maintenance",
    "emergency_override_enabled": true,
    "backup_power_available": true,
    "created_at": "2024-01-15T10:30:00.000000Z",
    "updated_at": "2024-01-15T15:45:00.000000Z",
    "deleted_at": null
}
```

### 5. Delete Access Gate (Soft Delete)
**Endpoint:** `DELETE /api/administrator/access-gates/<gate_id>/delete/`

**Description:** Soft delete access gate (marks as deleted but keeps record)

**URL Parameters:**
- `gate_id`: UUID of the access gate

**Success Response (200):**
```json
{
    "message": "Access gate soft deleted successfully",
    "deleted_at": "2024-01-15T16:00:00.000000Z"
}
```

### 6. Restore Access Gate
**Endpoint:** `POST /api/administrator/access-gates/<gate_id>/restore/`

**Description:** Restore a previously soft-deleted access gate

**URL Parameters:**
- `gate_id`: UUID of the access gate

**Success Response (200):**
```json
{
    "message": "Access gate restored successfully",
    "data": {
        "gate_id": "789e0123-e89b-12d3-a456-426614174002",
        "gate_code": "GATE001",
        "gate_name": "Main Entrance Gate",
        "location": "456e7890-e89b-12d3-a456-426614174001",
        "location_name": "Main Campus",
        "location_type": "campus",
        "gate_type": "bidirectional",
        "hardware_id": "HW001",
        "ip_address": "192.168.1.100",
        "mac_address": "00:11:22:33:44:55",
        "status": "active",
        "emergency_override_enabled": false,
        "backup_power_available": true,
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
// Resource not found (404)
{
    "detail": "Not found."
}

// Validation errors (400)
{
    "gate_code": ["This field is required."],
    "hardware_id": ["Access gate with this hardware id already exists."]
}

// Cannot restore active record (400)
{
    "error": "Resource is not deleted and cannot be restored"
}
```

---

## Frontend Implementation Guide

### Complete Workflow for All Resources

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

#### 2. Physical Locations Management
```javascript
// List locations
const listLocations = async (page = 1, search = '', type = '') => {
    let url = `http://localhost:8000/api/administrator/physical-locations/?page=${page}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    if (type) url += `&location_type=${type}`;

    const response = await fetch(url, {
        headers: {
            'Authorization': `Bearer ${access}`,
            'Content-Type': 'application/json'
        }
    });
    return await response.json();
};

// Create location
const createLocation = async (locationData) => {
    const response = await fetch('http://localhost:8000/api/administrator/physical-locations/create/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${access}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(locationData)
    });
    return await response.json();
};
```

#### 3. Access Gates Management
```javascript
// List gates with location filter
const listGates = async (page = 1, locationId = '', status = '') => {
    let url = `http://localhost:8000/api/administrator/access-gates/?page=${page}`;
    if (locationId) url += `&location=${locationId}`;
    if (status) url += `&status=${status}`;

    const response = await fetch(url, {
        headers: {
            'Authorization': `Bearer ${access}`,
            'Content-Type': 'application/json'
        }
    });
    return await response.json();
};

// Create gate
const createGate = async (gateData) => {
    const response = await fetch('http://localhost:8000/api/administrator/access-gates/create/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${access}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(gateData)
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
1. **Locations Management** → Create and manage physical locations first
2. **Gates Management** → Create gates linked to locations
3. **Personnel Management** → Manage security personnel
4. **Dashboard** → Overview of all resources with filtering

This API provides complete CRUD functionality for managing physical locations, access gates, and security personnel in your Smart Access system! 🚀