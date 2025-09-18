# Student CSV Upload API Documentation

## Overview

The Student CSV Upload API allows administrators and registration officers to bulk upload student data through CSV files. This feature includes validation, error reporting, and template generation to ensure data integrity and ease of use.

## User Types & Permissions

The system supports two user types with different permissions:

1. **Administrators**
   - Full CRUD access to student records
   - Can upload CSV files
   - Can modify and delete existing records

2. **Registration Officers**
   - Can view student records
   - Can create new students
   - Can upload CSV files
   - **Cannot** modify or delete existing records

## Base URL
```
/api/students/students/
```

## Authentication
All endpoints require JWT authentication with appropriate privileges.

**Required Headers:**
```
Authorization: Bearer <your_jwt_token>
```

For file upload endpoints, additional headers:
```
Content-Type: multipart/form-data
```

---

## Endpoints

### 1. Upload CSV File

**Endpoint:** `POST /api/students/students/upload-csv/`

**Description:** Upload a CSV file containing student data for bulk creation.

**Permissions:** Both Administrators and Registration Officers

**Headers:**
```
Authorization: Bearer <your_jwt_token>
Content-Type: multipart/form-data
Accept: application/json
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| csv_file  | File | Yes      | CSV file containing student data |

**CSV File Requirements:**
- Format: CSV (.csv extension)
- Encoding: UTF-8
- Maximum size: 5MB
- Headers must match expected column names exactly

**Required CSV Headers:**
```csv
surname,first_name,registration_number,department
```

**Optional CSV Headers:**
```csv
middle_name,mobile_phone,soma_class_code,academic_year_status,student_status
```

**Complete CSV Header Format:**
```csv
surname,first_name,middle_name,mobile_phone,registration_number,department,soma_class_code,academic_year_status,student_status
```

**Field Descriptions:**
| Header | Type | Required | Max Length | Description | Validation Rules |
|--------|------|----------|------------|-------------|------------------|
| surname | String | Yes | 100 chars | Student's last name | Cannot be empty |
| first_name | String | Yes | 100 chars | Student's first name | Cannot be empty |
| middle_name | String | No | 100 chars | Student's middle name | Can be empty |
| mobile_phone | String | No | 15 chars | Student's mobile phone number | Optional but must be valid format if provided |
| registration_number | String | Yes | 20 chars | Unique student ID | Must be unique across all students |
| department | String | Yes | 255 chars | Academic department | Cannot be empty |
| soma_class_code | String | No | 20 chars | Class code | Can be empty |
| academic_year_status | Choice | No | - | Academic status | Must be valid choice if provided |
| student_status | Choice | No | - | Enrollment status | Must be valid choice if provided |

**Academic Year Status Choices:**
- `Continuing` (default)
- `Retake`
- `Deferred`
- `Probation`
- `Completed`

**Student Status Choices:**
- `Enrolled` (default)
- `Withdrawn`
- `Suspended`

**Example CSV Content:**
```csv
surname,first_name,middle_name,mobile_phone,registration_number,department,soma_class_code,academic_year_status,student_status
Doe,John,Michael,+255712345678,REG2024001,Computer Science,CS2024A,Continuing,Enrolled
Smith,Jane,,+255723456789,REG2024002,Engineering,ENG2024B,Continuing,Enrolled
Johnson,Mike,David,+255734567890,REG2024003,Mathematics,,Retake,Enrolled
```

**Request Example (JavaScript):**
```javascript
const formData = new FormData();
formData.append('csv_file', fileInput.files[0]);

fetch('/api/students/students/upload-csv/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your_jwt_token_here',
    'Accept': 'application/json'
    // Note: Don't set Content-Type for FormData, browser will set it automatically
  },
  body: formData
})
```

**Request Example (cURL):**
```bash
curl -X POST \
  /api/students/students/upload-csv/ \
  -H 'Authorization: Bearer your_jwt_token_here' \
  -H 'Accept: application/json' \
  -F 'csv_file=@/path/to/students.csv'
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Successfully created 2 students",
  "data": {
    "total_created": 2,
    "students": [
      {
        "student_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "surname": "Doe",
        "first_name": "John",
        "middle_name": "Michael",
        "mobile_phone": "+255712345678",
        "registration_number": "REG2024001",
        "department": "Computer Science",
        "soma_class_code": "CS2024A",
        "academic_year_status": "Continuing",
        "student_status": "Enrolled",
        "is_active": true,
        "created_at": "2025-09-18T10:30:00Z",
        "updated_at": "2025-09-18T10:30:00Z"
      },
      {
        "student_uuid": "223e4567-e89b-12d3-a456-426614174001",
        "surname": "Smith",
        "first_name": "Jane",
        "middle_name": null,
        "mobile_phone": "+255723456789",
        "registration_number": "REG2024002",
        "department": "Engineering",
        "soma_class_code": "ENG2024B",
        "academic_year_status": "Continuing",
        "student_status": "Enrolled",
        "is_active": true,
        "created_at": "2025-09-18T10:30:00Z",
        "updated_at": "2025-09-18T10:30:00Z"
      }
    ],
    "uploaded_by": {
      "username": "user123",
      "user_type": "registration_officer",
      "full_name": "John Smith",
      "upload_timestamp": "2025-09-18T10:30:00Z"
    }
  }
}
```

**Error Response (400 Bad Request) - File Validation:**
```json
{
  "success": false,
  "message": "Invalid file upload",
  "errors": {
    "csv_file": ["File must be a CSV file."]
  }
}
```

**Error Response (400 Bad Request) - CSV Validation:**
```json
{
  "success": false,
  "message": "CSV validation failed",
  "errors": {
    "csv_errors": [
      "Row 2: Column 'surname' is required",
      "Row 3: Registration number 'REG2024001' already exists in database"
    ],
    "total_rows": 3,
    "valid_rows": 1,
    "error_rows": 2
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Error Response (403 Forbidden):**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

### 2. Download CSV Template

**Endpoint:** `GET /api/students/students/csv-template/`

**Description:** Download a CSV template file with headers and an example row.

**Permissions:** Both Administrators and Registration Officers

**Headers:**
```
Authorization: Bearer <your_jwt_token>
Accept: text/csv, application/octet-stream
```

**Parameters:** None

**Request Example (JavaScript):**
```javascript
fetch('/api/students/students/csv-template/', {
  headers: {
    'Authorization': 'Bearer your_jwt_token_here',
    'Accept': 'text/csv'
  }
})
.then(response => {
  if (response.ok) {
    return response.blob();
  }
  throw new Error('Failed to download template');
})
.then(blob => {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'student_upload_template.csv';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
});
```

**Request Example (cURL):**
```bash
curl -X GET \
  /api/students/students/csv-template/ \
  -H 'Authorization: Bearer your_jwt_token_here' \
  -H 'Accept: text/csv' \
  -o student_upload_template.csv
```

**Response Headers:**
```
Content-Type: text/csv
Content-Disposition: attachment; filename="student_upload_template.csv"
```

**Template Content (matching your actual model fields):**
```csv
surname,first_name,middle_name,email,registration_number,department,program,soma_class_code,academic_year_status,student_status
Doe,John,Michael,john.doe@example.com,REG2024001,Computer Science,Bachelor of Computer Science,CS2024A,Continuing,Enrolled
```

---

### 3. Get Validation Information

**Endpoint:** `GET /api/students/students/validation-info/`

**Description:** Get detailed information about CSV upload validation rules and acceptable values.

**Permissions:** Both Administrators and Registration Officers

**Headers:**
```
Authorization: Bearer <your_jwt_token>
Accept: application/json
```

**Parameters:** None

**Request Example (JavaScript):**
```javascript
fetch('/api/students/students/validation-info/', {
  headers: {
    'Authorization': 'Bearer your_jwt_token_here',
    'Accept': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

**Request Example (cURL):**
```bash
curl -X GET \
  /api/students/students/validation-info/ \
  -H 'Authorization: Bearer your_jwt_token_here' \
  -H 'Accept: application/json'
```

**Success Response (200 OK) - Based on your actual model:**
```json
{
  "required_fields": [
    "surname",
    "first_name", 
    "registration_number",
    "department",
    "program"
  ],
  "optional_fields": [
    "middle_name",
    "email",
    "soma_class_code",
    "academic_year_status",
    "student_status"
  ],
  "academic_year_status_choices": [
    "Continuing",
    "Retake", 
    "Deferred",
    "Probation",
    "Completed"
  ],
  "student_status_choices": [
    "Enrolled",
    "Withdrawn",
    "Suspended"
  ],
  "file_requirements": {
    "format": "CSV",
    "max_size": "5MB",
    "encoding": "UTF-8"
  },
  "validation_rules": {
    "registration_number": "Must be unique across all students",
    "email": "Must be valid email format if provided",
    "academic_year_status": "Must be one of the valid choices if provided",
    "student_status": "Must be one of the valid choices if provided"
  },
  "user_permissions": {
    "current_user": "user123",
    "user_type": "registration_officer",
    "full_name": "John Smith",
    "can_upload": true,
    "can_download_template": true,
    "can_create_students": true,
    "can_view_students": true,
    "can_modify_students": false,
    "can_delete_students": false
  }
}
```

---

### 4. Standard Student Management Endpoints

The following standard endpoints are available with different permissions:

| Endpoint | Method | Description | Administrator | Registration Officer |
|----------|--------|-------------|---------------|----------------------|
| `/api/students/students/` | GET | List all students | ✅ | ✅ |
| `/api/students/students/` | POST | Create a new student | ✅ | ✅ |
| `/api/students/students/{student_uuid}/` | GET | Retrieve a specific student | ✅ | ✅ |
| `/api/students/students/{student_uuid}/` | PUT | Update a student | ✅ | ❌ |
| `/api/students/students/{student_uuid}/` | PATCH | Partially update a student | ✅ | ❌ |
| `/api/students/students/{student_uuid}/` | DELETE | Delete a student | ✅ | ❌ |

---

## CSV Validation Rules

The system performs the following validation on CSV files based on the Student model:

1. **Required fields must be present:**
   - `surname` - Student's last name (max 100 characters)
   - `first_name` - Student's first name (max 100 characters)  
   - `registration_number` - Unique student ID (max 20 characters)
   - `department` - Academic department (max 255 characters)

2. **Optional fields:**
   - `middle_name` - Student's middle name (max 100 characters)
   - `mobile_phone` - Mobile phone number (max 15 characters)
   - `soma_class_code` - Class code (max 20 characters)
   - `academic_year_status` - Must be one of: `Continuing`, `Retake`, `Deferred`, `Probation`, `Completed`
   - `student_status` - Must be one of: `Enrolled`, `Withdrawn`, `Suspended`

3. **Validation rules:**
   - Registration numbers must be unique across all existing students
   - Registration numbers must be unique within the CSV file
   - Email addresses must be in valid email format if provided
   - Choice fields must match the predefined options
   - File must be CSV format with UTF-8 encoding
   - Maximum file size: 5MB

4. **Auto-generated fields:**
   - `student_uuid` - Automatically generated UUID
   - `is_active` - Defaults to `true`
   - `created_at` - Timestamp when record is created
   - `updated_at` - Timestamp when record is last modified

---

## Technical Implementation Notes

- The CSV upload is implemented in the `upload_csv` method of `StudentViewSet`
- Permissions are controlled by the `CanManageStudents` permission class
- Administrators have full access, Registration Officers have limited access  
- All operations are logged for auditing purposes
- Database transactions ensure data consistency during bulk operations
- Uses Django's `bulk_create()` for efficient database insertion

---

## CSV Upload Process Flow

1. **Preparation**
   - Get validation info: `GET /validation-info/`
   - Download template: `GET /csv-template/`
   - Fill in student data following the template format
   - Ensure all required fields are populated

2. **Validation**
   - File format and size validation
   - CSV structure validation (required columns)
   - Data validation (email format, choice fields, uniqueness)
   - Row-by-row error reporting

3. **Upload**
   - Upload CSV: `POST /upload-csv/`
   - If validation passes, students are created in bulk
   - Transaction ensures all-or-nothing creation
   - Success response includes created student details

---

## Error Handling

### HTTP Status Codes
- **200 OK** - Successful GET requests
- **201 Created** - Successful CSV upload
- **400 Bad Request** - Validation errors, malformed requests
- **401 Unauthorized** - Missing or invalid authentication
- **403 Forbidden** - Insufficient permissions
- **413 Payload Too Large** - File size exceeds limit
- **415 Unsupported Media Type** - Invalid file format
- **500 Internal Server Error** - Server-side errors

### Common Error Scenarios

**Authentication Errors:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Permission Errors:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**File Upload Errors:**
```json
{
  "success": false,
  "message": "Invalid file upload",
  "errors": {
    "csv_file": ["File must be a CSV file."]
  }
}
```

**CSV Structure Errors:**
```json
{
  "success": false,
  "message": "CSV validation failed",
  "errors": "Missing required columns: surname, first_name"
}
```

**Data Validation Errors:**
```json
{
  "success": false,
  "message": "CSV validation failed",
  "errors": {
    "csv_errors": [
      "Row 2: Column 'surname' is required",
      "Row 3: Registration number 'REG2024001' already exists in database",
      "Row 5: Invalid email format: 'invalid-email'"
    ],
    "total_rows": 10,
    "valid_rows": 7,
    "error_rows": 3
  }
}
```

---

## Integration Examples

### Complete React Component

```jsx
import React, { useState, useEffect } from 'react';

const StudentCSVUpload = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [validationInfo, setValidationInfo] = useState(null);

  const token = localStorage.getItem('token'); // Your JWT token

  // Get validation information on component mount
  useEffect(() => {
    fetchValidationInfo();
  }, []);

  const fetchValidationInfo = async () => {
    try {
      const response = await fetch('/api/students/students/validation-info/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setValidationInfo(data);
      }
    } catch (error) {
      console.error('Failed to fetch validation info:', error);
    }
  };

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setFile(selectedFile);
    setResult(null); // Clear previous results
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setResult(null);

    const formData = new FormData();
    formData.append('csv_file', file);

    try {
      const response = await fetch('/api/students/students/upload-csv/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
          // Don't set Content-Type for FormData
        },
        body: formData
      });

      const result = await response.json();
      setResult(result);
      
      if (result.success) {
        setFile(null); // Clear file input on success
        // Reset file input
        document.getElementById('csv-file-input').value = '';
      }
    } catch (error) {
      console.error('Upload error:', error);
      setResult({
        success: false,
        message: 'Network error occurred',
        error: error.message
      });
    } finally {
      setUploading(false);
    }
  };

  const downloadTemplate = async () => {
    try {
      const response = await fetch('/api/students/students/csv-template/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'text/csv'
        }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'student_upload_template.csv';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      } else {
        console.error('Failed to download template');
      }
    } catch (error) {
      console.error('Template download error:', error);
    }
  };

  return (
    <div className="csv-upload-container">
      <h2>Student CSV Upload</h2>
      
      {/* Validation Info Display */}
      {validationInfo && (
        <div className="validation-info">
          <h3>Upload Requirements:</h3>
          <p><strong>Required fields:</strong> {validationInfo.required_fields.join(', ')}</p>
          <p><strong>File format:</strong> {validationInfo.file_requirements.format}</p>
          <p><strong>Max size:</strong> {validationInfo.file_requirements.max_size}</p>
          <p><strong>Encoding:</strong> {validationInfo.file_requirements.encoding}</p>
        </div>
      )}
      
      {/* Template Download */}
      <div className="template-section">
        <button onClick={downloadTemplate} className="download-btn">
          📥 Download CSV Template
        </button>
        <p>Download the template to see the required format and headers.</p>
      </div>
      
      {/* File Upload */}
      <div className="upload-section">
        <input 
          id="csv-file-input"
          type="file" 
          accept=".csv" 
          onChange={handleFileChange}
          disabled={uploading}
        />
        
        <button 
          onClick={handleUpload} 
          disabled={!file || uploading}
          className="upload-btn"
        >
          {uploading ? '⏳ Uploading...' : '📤 Upload CSV'}
        </button>
      </div>

      {/* Upload Results */}
      {result && (
        <div className={`result ${result.success ? 'success' : 'error'}`}>
          {result.success ? (
            <div>
              <h3 style={{color: 'green'}}>✅ Upload Successful!</h3>
              <p>Created {result.data.total_created} students</p>
            </div>
          ) : (
            <div>
              <h3 style={{color: 'red'}}>❌ Upload Failed</h3>
              <p>{result.message}</p>
              
              {/* Display CSV validation errors */}
              {result.errors && result.errors.csv_errors && (
                <div>
                  <h4>Validation Errors:</h4>
                  <ul style={{textAlign: 'left'}}>
                    {result.errors.csv_errors.map((error, index) => (
                      <li key={index}>{error}</li>
                    ))}
                  </ul>
                  <p>
                    <strong>Summary:</strong> {result.errors.error_rows} errors 
                    out of {result.errors.total_rows} rows
                  </p>
                </div>
              )}
              
              {/* Display other errors */}
              {result.errors && !result.errors.csv_errors && (
                <pre>{JSON.stringify(result.errors, null, 2)}</pre>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default StudentCSVUpload;
```