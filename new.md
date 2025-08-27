# Smart Access User Management API Documentation

## Overview
This document covers the new user management endpoints added to the Smart Access authentication system. These endpoints provide administrators with complete control over user accounts.

## Base URL
```
http://localhost:8000/auth/
```

---

## New Endpoints

### 1. Retrieve User Details
**Endpoint:** `GET /users/<user_id>/`

**Description:** Administrators can retrieve detailed information about any user

**Headers:**
```
Authorization: Bearer <access_token>
```

**URL Parameters:**
- `user_id`: UUID of the user to retrieve

**Success Response (200):**
```json
{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "officer001",
    "full_name": "Jane Smith",
    "email": "jane.smith@example.com",
    "phone_number": "+1234567890",
    "user_type": "registration_officer",
    "is_active": true
}
```

**Error Responses:**
```json
// Not administrator (403)
{
    "detail": "Only administrators can retrieve users."
}

// User not found (404)
{
    "detail": "User not found."
}
```

---

### 2. Deactivate User
**Endpoint:** `PATCH /users/<user_id>/deactivate/`

**Description:** Administrators can deactivate user accounts (soft deactivation)

**Headers:**
```
Authorization: Bearer <access_token>
```

**URL Parameters:**
- `user_id`: UUID of the user to deactivate

**Success Response (200):**
```json
{
    "message": "User officer001 deactivated successfully."
}
```

**Error Responses:**
```json
// Not administrator (403)
{
    "detail": "Only administrators can deactivate users."
}

// User not found (404)
{
    "detail": "User not found."
}
```

---

### 3. Change User Password
**Endpoint:** `PATCH /users/<user_id>/change-password/`

**Description:** Administrators can reset/change passwords for any user

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**URL Parameters:**
- `user_id`: UUID of the user whose password to change

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
// Not administrator (403)
{
    "detail": "Only administrators can change passwords."
}

// User not found (404)
{
    "detail": "User not found."
}

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

