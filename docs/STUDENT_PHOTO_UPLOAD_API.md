# Student Photo Upload API

## Overview
This API endpoint allows uploading photos for existing students. Photos are stored separately from student records to maintain data integrity.

## Endpoint
```
POST /api/students/{student_uuid}/upload-photo/
```

## Permissions
- **Administrators**: Full access
- **Registration Officers**: Full access

## Request
- **Content-Type**: `multipart/form-data`
- **Body Parameters**:
  - `photo` (file): Image file (JPEG or PNG, max 5MB)

## Validation Rules
- **File Type**: Only JPEG and PNG images are allowed
- **File Size**: Maximum 5MB
- **Student**: Must exist and be active

## Success Response (201 Created)
```json
{
    "success": true,
    "message": "Photo uploaded successfully",
    "data": {
        "student_uuid": "uuid-string",
        "registration_number": "240126000000",
        "photo_url": "http://localhost:8000/media/student_photos/photo.jpg",
        "uploaded_at": "2025-10-08T12:00:00Z",
        "uploaded_by": {
            "username": "admin",
            "user_type": "administrator",
            "full_name": "Admin User"
        }
    }
}
```

## Error Responses

### 400 Bad Request - No Photo File
```json
{
    "success": false,
    "error": "No photo file provided"
}
```

### 400 Bad Request - Invalid File Type
```json
{
    "success": false,
    "error": "Invalid file type. Only JPEG and PNG images are allowed."
}
```

### 400 Bad Request - File Too Large
```json
{
    "success": false,
    "error": "File size too large. Maximum size is 5MB."
}
```

### 404 Not Found - Student Not Found
```json
{
    "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
    "success": false,
    "error": "An error occurred while uploading the photo"
}
```

## Usage Example
```bash
curl -X POST \
  http://localhost:8000/api/students/123e4567-e89b-12d3-a456-426614174000/upload-photo/ \
  -H "Authorization: Bearer <your-token>" \
  -F "photo=@student_photo.jpg"
```

## Notes
- If a photo already exists for the student, it will be replaced
- Old photos are automatically deleted when replaced
- Photos are stored in the `student_photos/` directory
- The photo URL is accessible via the media URL configured in Django settings