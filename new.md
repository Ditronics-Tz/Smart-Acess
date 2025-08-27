# Smart Access User Management API Documentation

## Overview
This document covers the complete authentication and user management endpoints for the Smart Access system. These endpoints provide administrators with full control over registration officers and authentication flow.

## Base URL
```
http://localhost:8000/auth/
```

---

## Authentication Endpoints

### 1. Login
**Endpoint:** `POST /login`

**Description:** Authenticate users (administrators and registration officers)

**Request Body:**
```json
{
    "username": "admin_username",
    "password": "admin_password",
    "user_type": "administrator"
}
```

**Field Validation:**
- `username`: Required string
- `password`: Required string
- `user_type`: Required, choices: "administrator" or "registration_officer"

**Success Response (200):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user_type": "administrator",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "admin_username",
    "message": "Login successful."
}
```

**Error Responses:**
```json
// Invalid credentials (401)
{
    "detail": "Invalid credentials."
}

// Account locked (403)
{
    "detail": "Account is locked."
}

// Rate limited (429)
{
    "detail": "Too many attempts. Try again in 15 minutes."
}
```

---

### 2. Refresh Token
**Endpoint:** `POST /refresh`

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Success Response (200):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

### 3. Logout
**Endpoint:** `POST /logout`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Success Response (200):**
```json
{
    "message": "Successfully logged out."
}
```

---

## User Management Endpoints (Admin Only)

### 1. Create Registration Officer
**Endpoint:** `POST /create-user`

**Description:** Administrators can create new registration officers

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "username": "officer001",
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "phone_number": "+1234567890",
    "password": "securePassword123",
    "user_type": "registration_officer"
}
```

**Success Response (201):**
```json
{
    "message": "User created successfully.",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "officer001",
    "email": "john.doe@example.com"
}
```

---

### 2. List All Registration Officers
**Endpoint:** `GET /registration-officers`

**Description:** Get paginated list of all registration officers with filtering

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 10, max: 100)
- `search`: Search in username, full_name, email
- `is_active`: Filter by active status (true/false)

**Example URLs:**
```
GET /registration-officers
GET /registration-officers?page=2&page_size=20
GET /registration-officers?search=john&is_active=true
```

**Success Response (200):**
```json
{
    "registration_officers": [
        {
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "username": "officer001",
            "full_name": "John Doe",
            "email": "john.doe@example.com",
            "phone_number": "+1234567890",
            "is_active": true,
            "created_at": "2024-01-15T10:30:00.000000Z",
            "last_login": "2024-01-20T09:15:00.000000Z",
            "failed_login_attempts": 0,
            "account_locked": false
        }
    ],
    "pagination": {
        "current_page": 1,
        "total_pages": 3,
        "total_count": 25,
        "has_next": true,
        "has_previous": false,
        "page_size": 10
    }
}
```

---

### 3. Get Single Registration Officer
**Endpoint:** `GET /users/<user_id>`

**Description:** Get detailed information about a specific registration officer

**Headers:**
```
Authorization: Bearer <access_token>
```

**URL Parameters:**
- `user_id`: UUID of the registration officer

**Success Response (200):**
```json
{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "officer001",
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "phone_number": "+1234567890",
    "user_type": "registration_officer",
    "is_active": true
}
```

---

### 4. Change Registration Officer Password
**Endpoint:** `PATCH /users/<user_id>/change-password`

**Description:** Administrator can reset password for any registration officer

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**URL Parameters:**
- `user_id`: UUID of the registration officer

**Request Body:**
```json
{
    "new_password": "newSecurePassword123",
    "confirm_password": "newSecurePassword123"
}
```

**Field Validation:**
- `new_password`: Minimum 8 characters, required
- `confirm_password`: Must match new_password, required

**Success Response (200):**
```json
{
    "message": "Password updated successfully for officer001."
}
```

**Error Responses:**
```json
// Password mismatch (400)
{
    "detail": "Passwords do not match."
}

// Password too short (400)
{
    "detail": "Password must be at least 8 characters long."
}

// Missing fields (400)
{
    "detail": "Both new_password and confirm_password are required."
}
```

---

### 5. Deactivate Registration Officer
**Endpoint:** `PATCH /users/<user_id>/deactivate`

**Description:** Administrator can deactivate registration officer accounts

**Headers:**
```
Authorization: Bearer <access_token>
```

**URL Parameters:**
- `user_id`: UUID of the registration officer

**Success Response (200):**
```json
{
    "message": "User officer001 deactivated successfully."
}
```

---

## Common Error Responses

### Authorization Errors
```json
// Not administrator (403)
{
    "detail": "Only administrators can [action description]."
}

// Invalid/expired token (401)
{
    "detail": "Given token not valid for any token type"
}

// Missing token (401)
{
    "detail": "Authentication credentials were not provided."
}
```

### Resource Errors
```json
// User not found (404)
{
    "detail": "User not found."
}

// Validation errors (400)
{
    "field_name": ["This field is required."]
}
```

---

## Frontend Implementation Notes

### Token Management
1. Store `access` token for API requests
2. Store `refresh` token for refreshing access tokens
3. Include `Authorization: Bearer <access_token>` header in all authenticated requests
4. Implement automatic token refresh when access token expires

### User Flow for Admin Dashboard
1. **Login** → Get tokens and user info
2. **List Registration Officers** → Display paginated table with search/filter
3. **View Officer Details** → Show detailed information
4. **Manage Officers** → Change passwords, deactivate accounts
5. **Create New Officers** → Add new registration officers

### Search & Filtering
- Implement debounced search for better UX
- Use query parameters for maintaining state
- Handle pagination with proper navigation

### Error Handling
- Display user-friendly error messages
- Handle 401 errors by redirecting to login
- Show loading states during API calls
- Implement proper form validation