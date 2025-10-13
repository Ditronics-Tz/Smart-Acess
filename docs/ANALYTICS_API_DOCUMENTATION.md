# Analytics API Documentation

## Overview

The Analytics API provides comprehensive reporting and monitoring capabilities for the Smart Access Control System. It offers detailed insights into user demographics, card usage patterns, system health, and real-time alerts.

## Base URL
```
/api/stats/
```

## Authentication
All endpoints require administrator-level authentication using JWT tokens.

## API Endpoints

### 1. Dashboard Overview
**GET** `/dashboard/`

Returns key system metrics and overview data for the main dashboard.

**Response Example:**
```json
{
  "success": true,
  "data": {
    "overview": {
      "total_users": 1250,
      "total_students": 1000,
      "total_staff": 200,
      "total_security": 50,
      "total_cards": 1200,
      "active_cards": 1180
    },
    "recent_activity": {
      "today_verifications": 450,
      "today_print_jobs": 15,
      "this_week_new_cards": 25
    },
    "photo_completion": {
      "students": {
        "with_photos": 950,
        "total": 1000,
        "completion_rate": 95.0
      },
      "staff": {
        "with_photos": 195,
        "total": 200,
        "completion_rate": 97.5
      }
    }
  },
  "generated_at": "2024-01-15T10:30:00Z"
}
```

### 2. Card Analytics
**GET** `/analytics/cards/`

Provides detailed analytics on card issuance and distribution patterns.

**Response Example:**
```json
{
  "success": true,
  "data": {
    "issuance_trends": [
      {
        "date": "2024-01-01",
        "student_cards": 15,
        "staff_cards": 3,
        "security_cards": 1
      }
    ],
    "distribution": {
      "by_type": [
        {"card_type": "student", "count": 1000},
        {"card_type": "staff", "count": 200}
      ],
      "by_status": [
        {"is_active": true, "count": 1180},
        {"is_active": false, "count": 20}
      ]
    },
    "print_statistics": {
      "total_print_jobs": 1250,
      "successful_prints": 1200,
      "failed_prints": 50,
      "success_rate": 96.0
    }
  },
  "generated_at": "2024-01-15T10:30:00Z"
}
```

### 3. Verification Analytics
**GET** `/analytics/verifications/`

Shows card usage and verification patterns across the system.

**Query Parameters:**
- `days`: Number of days to analyze (default: 30)
- `location`: Filter by specific location

**Response Example:**
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_verifications": 15000,
      "successful_verifications": 14500,
      "failed_verifications": 500,
      "success_rate": 96.67
    },
    "daily_trends": [
      {
        "date": "2024-01-01",
        "total_verifications": 450,
        "successful": 435,
        "failed": 15
      }
    ],
    "by_location": [
      {
        "location": "Main Building",
        "total_verifications": 8000,
        "success_rate": 97.2
      }
    ],
    "peak_hours": [
      {"hour": 8, "count": 200},
      {"hour": 12, "count": 180}
    ]
  },
  "generated_at": "2024-01-15T10:30:00Z"
}
```

### 4. User Demographics
**GET** `/analytics/demographics/`

Comprehensive user population analytics and demographic breakdowns.

**Response Example:**
```json
{
  "success": true,
  "data": {
    "students": {
      "total": 1000,
      "by_status": [
        {"academic_year_status": "undergraduate", "count": 750},
        {"academic_year_status": "graduate", "count": 250}
      ],
      "by_department": [
        {"department": "Computer Science", "count": 300},
        {"department": "Engineering", "count": 250}
      ],
      "registration_trends": [
        {"date": "2024-01-01", "count": 15}
      ],
      "phone_completion_rate": 95.5
    },
    "staff": {
      "total": 200,
      "by_status": [
        {"employment_status": "full_time", "count": 180},
        {"employment_status": "part_time", "count": 20}
      ],
      "by_department": [
        {"department": "Administration", "count": 50},
        {"department": "Academic", "count": 150}
      ],
      "phone_completion_rate": 98.0
    },
    "security_personnel": {
      "total": 50,
      "active": 48
    }
  },
  "generated_at": "2024-01-15T10:30:00Z"
}
```

### 5. System Health Report
**GET** `/system/health/`

Infrastructure status and data integrity checks.

**Response Example:**
```json
{
  "success": true,
  "data": {
    "infrastructure": {
      "gates": {
        "total": 25,
        "status_summary": [
          {"status": "active", "count": 22},
          {"status": "maintenance", "count": 3}
        ],
        "by_location": [
          {
            "location__location_name": "Main Building",
            "location__location_type": "academic",
            "gate_count": 8
          }
        ]
      },
      "locations": {
        "total": 15,
        "restricted": 8,
        "by_type": [
          {"location_type": "academic", "count": 10},
          {"location_type": "administrative", "count": 5}
        ]
      }
    },
    "data_integrity": {
      "students_without_cards": 20,
      "staff_without_cards": 5,
      "cards_without_photos": 15
    }
  },
  "generated_at": "2024-01-15T10:30:00Z"
}
```

### 6. Comprehensive Report
**GET** `/reports/comprehensive/`

Combined analytics report with all system insights and executive summary.

**Response Example:**
```json
{
  "success": true,
  "report_type": "comprehensive",
  "data": {
    "executive_summary": {
      "total_system_users": 1250,
      "total_active_cards": 1200,
      "card_utilization_rate": 12.5,
      "system_health_score": 25,
      "data_completeness_score": 96.25
    },
    "dashboard_overview": { /* Dashboard data */ },
    "card_analytics": { /* Card analytics data */ },
    "verification_analytics": { /* Verification data */ },
    "user_demographics": { /* Demographics data */ },
    "system_health": { /* Health data */ }
  },
  "generated_at": "2024-01-15T10:30:00Z",
  "report_version": "1.0"
}
```

### 7. System Alerts
**GET** `/alerts/`

Current system alerts and notifications.

**Response Example:**
```json
{
  "success": true,
  "data": {
    "active_alerts": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "type": "system_health",
        "severity": "warning",
        "title": "High Card Verification Failures",
        "description": "Card verification failure rate exceeded threshold",
        "metric_value": 15.5,
        "threshold_value": 10.0,
        "created_at": "2024-01-15T08:30:00Z",
        "acknowledged_at": null,
        "acknowledged_by": null
      }
    ],
    "resolved_alerts": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "type": "data_integrity",
        "severity": "info",
        "title": "Photo Upload Batch Complete",
        "resolved_at": "2024-01-14T16:45:00Z"
      }
    ],
    "summary": {
      "total_active": 1,
      "by_severity": [
        {"severity": "warning", "count": 1}
      ]
    }
  },
  "generated_at": "2024-01-15T10:30:00Z"
}
```

### 8. Acknowledge Alert
**POST** `/alerts/{alert_id}/acknowledge/`

Acknowledge a specific system alert.

**Response Example:**
```json
{
  "success": true,
  "message": "Alert acknowledged successfully",
  "alert_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 9. Resolve Alert
**POST** `/alerts/{alert_id}/resolve/`

Resolve a specific system alert.

**Response Example:**
```json
{
  "success": true,
  "message": "Alert resolved successfully",
  "alert_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 10. Historical Analytics
**GET** `/analytics/historical/`

Historical analytics snapshots with trend analysis.

**Query Parameters:**
- `type`: Snapshot type (daily, weekly, monthly) - default: daily
- `days`: Number of days to retrieve - default: 30

**Response Example:**
```json
{
  "success": true,
  "data": {
    "snapshots": [
      {
        "date": "2024-01-01",
        "total_users": 1200,
        "total_students": 950,
        "total_staff": 200,
        "total_cards": 1150,
        "daily_verifications": 420,
        "student_photo_completion": 94.5,
        "staff_photo_completion": 96.8
      }
    ],
    "trends": {
      "user_growth": 50,
      "card_growth": 50,
      "verification_change": 30
    },
    "parameters": {
      "report_type": "daily",
      "days": 30,
      "total_snapshots": 30
    }
  },
  "generated_at": "2024-01-15T10:30:00Z"
}
```

### 11. Generate Snapshot
**POST** `/snapshots/generate/`

Manually generate a new analytics snapshot.

**Request Body:**
```json
{
  "type": "manual"
}
```

**Response Example:**
```json
{
  "success": true,
  "message": "Analytics snapshot created successfully",
  "snapshot_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Error Responses

All endpoints return standardized error responses:

```json
{
  "success": false,
  "error": "Error description here"
}
```

Common HTTP status codes:
- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Performance Notes

1. **Caching**: Most analytics data is cached for 5-15 minutes to improve performance
2. **Pagination**: Large datasets are automatically paginated
3. **Rate Limiting**: API calls are rate-limited per user
4. **Background Processing**: Snapshots and alerts are processed asynchronously

## Usage Examples

### Python (requests)
```python
import requests

# Get dashboard data
response = requests.get(
    'http://your-domain/api/stats/dashboard/',
    headers={'Authorization': 'Bearer your-jwt-token'}
)
data = response.json()

# Acknowledge an alert
response = requests.post(
    f'http://your-domain/api/stats/alerts/{alert_id}/acknowledge/',
    headers={'Authorization': 'Bearer your-jwt-token'}
)
```

### JavaScript (fetch)
```javascript
// Get verification analytics
const response = await fetch('/api/stats/analytics/verifications/', {
  headers: {
    'Authorization': 'Bearer your-jwt-token',
    'Content-Type': 'application/json'
  }
});
const data = await response.json();

// Generate manual snapshot
const snapshot = await fetch('/api/stats/snapshots/generate/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your-jwt-token',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ type: 'manual' })
});
```

## Integration with Frontend

The analytics API is designed to support modern dashboard interfaces with:

1. **Real-time updates** through WebSocket connections (planned)
2. **Interactive charts** with drill-down capabilities
3. **Export functionality** for reports (PDF/CSV)
4. **Alert notifications** for system administrators
5. **Mobile-responsive** data formats

## Security Considerations

1. All endpoints require administrator-level authentication
2. Sensitive data is filtered based on user permissions
3. API rate limiting prevents abuse
4. Audit logging tracks all analytics access
5. Data anonymization for compliance requirements

## Monitoring and Maintenance

1. **Health Checks**: Built-in system health monitoring
2. **Performance Metrics**: Response time and query optimization
3. **Alert System**: Proactive issue detection and notification
4. **Backup Strategy**: Automated snapshot backups
5. **Scalability**: Designed for horizontal scaling

---

*For technical support or feature requests, please contact the development team.*