# Student CSV Upload API Documentation

## Overview

The Student CSV Upload API allows administrators to bulk upload student data through CSV files. This feature includes validation, error reporting, and template generation to ensure data integrity and ease of use.

## Base URL
```
/api/students/students/
```

## Authentication
All endpoints require JWT authentication with administrator privileges.

**Headers Required:**
```
Authorization: Bearer <your_jwt_token>
Content-Type: multipart/form-data (for file upload)
```

---

## Endpoints

### 1. Upload CSV File

**Endpoint:** `POST /api/students/students/upload-csv/`

**Description:** Upload a CSV file containing student data for bulk creation.

**Content-Type:** `multipart/form-data`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| csv_file  | File | Yes      | CSV file containing student data |

**CSV File Requirements:**
- Format: CSV (.csv extension)
- Encoding: UTF-8
- Maximum size: 5MB
- Headers must match expected column names

**Required CSV Columns:**
- `surname` - Student's last name
- `first_name` - Student's first name  
- `registration_number` - Unique student registration number
- `department` - Academic department
- `program` - Academic program/course

**Optional CSV Columns:**
- `middle_name` - Student's middle name
- `email` - Student's email address
- `soma_class_code` - Class code
- `academic_year_status` - Academic status (see choices below)
- `student_status` - Enrollment status (see choices below)

**Academic Year Status Choices:**
- `Continuing`
- `Retake`
- `Deferred`
- `Probation`
- `Completed`

**Student Status Choices:**
- `Enrolled`
- `Withdrawn`
- `Suspended`

**Request Example:**
```javascript
const formData = new FormData();
formData.append('csv_file', fileInput.files[0]);

fetch('/api/students/students/upload-csv/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your_jwt_token_here'
  },
  body: formData
})
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Successfully created 25 students",
  "data": {
    "total_created": 25,
    "students": [
      {
        "student_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "surname": "Doe",
        "first_name": "John",
        "middle_name": "Michael",
        "email": "john.doe@example.com",
        "registration_number": "REG2024001",
        "department": "Computer Science",
        "program": "Bachelor of Computer Science",
        "soma_class_code": "CS2024A",
        "academic_year_status": "Continuing",
        "student_status": "Enrolled",
        "is_active": true,
        "created_at": "2025-09-12T10:30:00Z",
        "updated_at": "2025-09-12T10:30:00Z"
      }
      // ... more students
    ]
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
      "Row 3: Registration number 'REG2024001' already exists in database",
      "Row 5: Invalid email format: 'invalid-email'",
      "Row 7: Invalid academic_year_status: 'InvalidStatus'. Valid choices: ['Continuing', 'Retake', 'Deferred', 'Probation', 'Completed']"
    ],
    "total_rows": 10,
    "valid_rows": 6,
    "error_rows": 4
  }
}
```

---

### 2. Download CSV Template

**Endpoint:** `GET /api/students/students/csv-template/`

**Description:** Download a CSV template file with proper headers and an example row.

**Parameters:** None

**Request Example:**
```javascript
fetch('/api/students/students/csv-template/', {
  headers: {
    'Authorization': 'Bearer your_jwt_token_here'
  }
})
.then(response => response.blob())
.then(blob => {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'student_upload_template.csv';
  a.click();
});
```

**Response:**
- Content-Type: `text/csv`
- Content-Disposition: `attachment; filename="student_upload_template.csv"`
- File contains headers and one example row

**Template Content:**
```csv
surname,first_name,middle_name,email,registration_number,department,program,soma_class_code,academic_year_status,student_status
Doe,John,Michael,john.doe@example.com,REG2024001,Computer Science,Bachelor of Computer Science,CS2024A,Continuing,Enrolled
```

---

### 3. Get Validation Information

**Endpoint:** `GET /api/students/students/validation-info/`

**Description:** Get detailed information about CSV upload validation rules and acceptable values.

**Parameters:** None

**Request Example:**
```javascript
fetch('/api/students/students/validation-info/', {
  headers: {
    'Authorization': 'Bearer your_jwt_token_here'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

**Success Response (200 OK):**
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
  }
}
```

---

## CSV Upload Process Flow

1. **Preparation**
   - Download template using `/csv-template/` endpoint
   - Fill in student data following the template format
   - Ensure all required fields are populated

2. **Validation**
   - File format and size validation
   - CSV structure validation (required columns)
   - Data validation (email format, choice fields, uniqueness)
   - Row-by-row error reporting

3. **Upload**
   - If validation passes, students are created in bulk
   - Transaction ensures all-or-nothing creation
   - Success response includes created student details

---

## Error Handling

### File Upload Errors
- **Invalid file format**: File must have .csv extension
- **File too large**: Maximum 5MB file size
- **Encoding issues**: File must be UTF-8 encoded

### CSV Structure Errors  
- **Missing required columns**: All required headers must be present
- **Empty required fields**: Required fields cannot be empty

### Data Validation Errors
- **Duplicate registration numbers**: Within CSV or existing in database
- **Invalid email format**: Must be valid email if provided
- **Invalid choice values**: Must match predefined choices
- **General data format errors**: Type mismatches, etc.

---

## Integration Examples

### React Frontend Component

```jsx
import React, { useState } from 'react';

const StudentCSVUpload = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('csv_file', file);

    try {
      const response = await fetch('/api/students/students/upload-csv/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });

      const result = await response.json();
      setResult(result);
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setUploading(false);
    }
  };

  const downloadTemplate = async () => {
    try {
      const response = await fetch('/api/students/students/csv-template/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'student_upload_template.csv';
      a.click();
    } catch (error) {
      console.error('Template download error:', error);
    }
  };

  return (
    <div>
      <h2>Student CSV Upload</h2>
      
      <button onClick={downloadTemplate}>
        Download Template
      </button>
      
      <input 
        type="file" 
        accept=".csv" 
        onChange={handleFileChange} 
      />
      
      <button 
        onClick={handleUpload} 
        disabled={!file || uploading}
      >
        {uploading ? 'Uploading...' : 'Upload CSV'}
      </button>

      {result && (
        <div>
          {result.success ? (
            <div style={{color: 'green'}}>
              Success! Created {result.data.total_created} students
            </div>
          ) : (
            <div style={{color: 'red'}}>
              <h4>Upload Failed:</h4>
              {result.errors.csv_errors && (
                <ul>
                  {result.errors.csv_errors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
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

### Python Client Example

```python
import requests

# Upload CSV
def upload_students_csv(file_path, token):
    url = "http://your-api-domain.com/api/students/students/upload-csv/"
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    with open(file_path, 'rb') as file:
        files = {'csv_file': file}
        response = requests.post(url, headers=headers, files=files)
    
    return response.json()

# Download template
def download_template(token):
    url = "http://your-api-domain.com/api/students/students/csv-template/"
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    response = requests.get(url, headers=headers)
    
    with open('student_template.csv', 'wb') as file:
        file.write(response.content)
```

---

## Testing

### Test CSV Examples

**Valid CSV:**
```csv
surname,first_name,middle_name,email,registration_number,department,program,soma_class_code,academic_year_status,student_status
Smith,Jane,Marie,jane.smith@example.com,REG2024001,Computer Science,Bachelor of Computer Science,CS2024A,Continuing,Enrolled
Johnson,Mike,,mike.j@example.com,REG2024002,Engineering,Bachelor of Engineering,ENG2024B,Continuing,Enrolled
```

**Invalid CSV (for testing error handling):**
```csv
surname,first_name,middle_name,email,registration_number,department,program,soma_class_code,academic_year_status,student_status
,Jane,Marie,jane.smith@example.com,REG2024001,Computer Science,Bachelor of Computer Science,CS2024A,Continuing,Enrolled
Johnson,Mike,,invalid-email,REG2024002,Engineering,Bachelor of Engineering,ENG2024B,InvalidStatus,Enrolled
```

---

## Security Considerations

1. **Authentication Required**: All endpoints require valid JWT token
2. **File Size Limits**: 5MB maximum to prevent abuse
3. **File Type Validation**: Only CSV files accepted
4. **Data Validation**: Comprehensive validation prevents invalid data
5. **Transaction Safety**: Bulk operations use database transactions
6. **Error Logging**: All operations are logged for audit purposes

---

## Performance Notes

- **Bulk Operations**: Uses Django's `bulk_create()` for efficient database insertion
- **Memory Efficient**: Streams CSV data to avoid memory issues with large files
- **Transaction Atomic**: Ensures data consistency during bulk operations
- **Indexing**: Database indexes on key fields improve lookup performance

---

## Support

For issues or questions regarding the CSV upload feature:

1. Check the validation info endpoint for current requirements
2. Ensure CSV format matches the template exactly
3. Verify all required fields are populated
4. Check file encoding is UTF-8
5. Ensure registration numbers are unique

Common issues:
- **UTF-8 encoding**: Save CSV with UTF-8 encoding to avoid character issues
- **Excel compatibility**: When saving from Excel, choose "CSV UTF-8" format
- **Empty rows**: Remove any empty rows from the CSV file
- **Special characters**: Ensure proper encoding for names with special characters