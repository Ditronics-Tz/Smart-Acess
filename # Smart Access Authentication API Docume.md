# Smart Access Authentication API Documentation

## Base URL
```
http://localhost:8000/auth/
```

## Authentication Endpoints

### 1. Login
**Endpoint:** `POST /login`

**Description:** Authenticates user and sends OTP to email

**Request Body:**
```json
{
    "username": "admin123",
    "password": "securepassword123",
    "user_type": "administrator"
}
```

**Field Validation:**
- `username`: 3-50 characters, required
- `password`: minimum 8 characters, required
- `user_type`: "administrator" or "registration_officer"

**Success Response (200):**
```json
{
    "session_id": "123e4567-e89b-12d3-a456-426614174000",
    "message": "Login successful. OTP sent to your email."
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

// Too many attempts (429)
{
    "detail": "Too many login attempts for this username. Try again in 10 minutes."
}
```

---

### 2. Verify OTP
**Endpoint:** `POST /verify-otp`

**Description:** Verifies OTP and returns JWT tokens

**Request Body:**
```json
{
    "session_id": "123e4567-e89b-12d3-a456-426614174000",
    "otp_code": "123456",
    "user_type": "administrator"
}
```

**Field Validation:**
- `session_id`: Valid UUID from login response
- `otp_code`: 6-digit numeric code
- `user_type`: "administrator" or "registration_officer"

**Success Response (200):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user_type": "administrator",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "admin123"
}
```

**Error Responses:**
```json
// Invalid OTP (400)
{
    "detail": "Invalid or expired OTP."
}

// OTP already used (400)
{
    "detail": "OTP already used."
}

// OTP expired (400)
{
    "detail": "OTP expired."
}
```

---

### 3. Resend OTP
**Endpoint:** `POST /resend-otp`

**Description:** Resends OTP for existing session

**Request Body:**
```json
{
    "session_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_type": "administrator"
}
```

**Success Response (200):**
```json
{
    "message": "New OTP sent to your email.",
    "session_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Error Responses:**
```json
// OTP still valid (400)
{
    "detail": "Current OTP is still valid for 3 minutes."
}

// Invalid session (400)
{
    "detail": "Invalid session or OTP already verified."
}
```

---

### 4. Create Registration Officer
**Endpoint:** `POST /create-registration-officer`

**Description:** Administrators can create registration officers

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "username": "officer123",
    "full_name": "John Doe",
    "email": "officer@example.com",
    "phone_number": "+1234567890",
    "password": "securepassword123",
    "confirm_password": "securepassword123"
}
```

**Field Validation:**
- `username`: 3-50 characters, unique, required
- `full_name`: 255 characters max, required
- `email`: Valid email format, unique, required
- `phone_number`: Optional, 20 characters max
- `password`: minimum 8 characters, required
- `confirm_password`: Must match password, required

**Success Response (201):**
```json
{
    "message": "Registration officer created successfully.",
    "officer_id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "officer123",
    "email": "officer@example.com"
}
```

**Error Responses:**
```json
// Not administrator (403)
{
    "detail": "Only administrators can create registration officers."
}

// Username exists (400)
{
    "username": ["Username already exists"]
}

// Email exists (400)
{
    "email": ["Email already exists"]
}

// Password mismatch (400)
{
    "non_field_errors": ["Passwords do not match"]
}
```

---

### 5. Refresh Token
**Endpoint:** `POST /refresh`

**Description:** Refreshes access token using refresh token

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

**Error Response (401):**
```json
{
    "detail": "Invalid refresh token."
}
```

---

### 6. Logout
**Endpoint:** `POST /logout`

**Description:** Logs out user and blacklists refresh token

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

**Error Response (400):**
```json
{
    "detail": "Invalid refresh token."
}
```

---

## Rate Limiting

### Login Endpoint
- **IP-based**: 5 attempts per 15 minutes
- **Username-based**: 3 attempts per 10 minutes
- **OTP Generation**: 3 requests per email per 5 minutes

### OTP Verification
- **IP-based**: 10 attempts per 10 minutes
- **Session-based**: 5 attempts per session

### Resend OTP
- **IP-based**: 3 attempts per 5 minutes

**Rate Limit Response (429):**
```json
{
    "detail": "Too many attempts. Try again in 15 minutes."
}
```

---

## User Types

### Administrator
- Can create registration officers
- Has account locking mechanism
- Tracks failed login attempts

### Registration Officer
- Can only login and access assigned features
- Uses active/inactive status instead of account locking

---

## Authentication Flow

1. **Login** → Get `session_id`
2. **Check Email** → Receive 6-digit OTP (expires in 5 minutes)
3. **Verify OTP** → Get JWT tokens
4. **Use Access Token** → For authenticated requests
5. **Refresh Token** → When access token expires
6. **Logout** → Blacklist refresh token

---

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Too Many Requests

---

## Notes for Frontend Team

1. **Store tokens securely** (localStorage/sessionStorage)
2. **Handle token expiration** gracefully
3. **Implement rate limiting feedback** to users
4. **Show OTP countdown timer** (5 minutes)
5. **Validate form inputs** before sending requests
6. **Handle network errors** appropriately
7. **Clear tokens on logout**

## Environment
- **Development**: `http://localhost:8000`
- **Production**: TBD