# API Documentation

## Overview

This document provides comprehensive API documentation for the Booking System. The API follows RESTful principles and uses JSON for data exchange.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://yourdomain.com`

## Authentication

### Authentication Methods

1. **Session Authentication** (Default)
   - Uses Django's built-in session framework
   - Login via `/accounts/login/`
   - Logout via `/accounts/logout/`

2. **OAuth2 Authentication** (Optional)
   - Google OAuth2 integration
   - Login via `/accounts/google/login/`

### Authentication Headers

For API requests, include session cookie or OAuth token in headers.

## User Management API

### User Registration

**Endpoint**: `POST /accounts/register/`

**Request Body**:
```json
{
    "email": "user@example.com",
    "password1": "securepassword123",
    "password2": "securepassword123",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890"
}
```

**Response**:
```json
{
    "success": true,
    "message": "Registration successful. Please check your email for verification.",
    "user_id": 123
}
```

### User Login

**Endpoint**: `POST /accounts/login/`

**Request Body**:
```json
{
    "login": "user@example.com",
    "password": "securepassword123",
    "remember": true
}
```

**Response**:
```json
{
    "success": true,
    "message": "Login successful",
    "user": {
        "id": 123,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "user_type": "patient"
    }
}
```

### User Profile

**Endpoint**: `GET /accounts/profile/`

**Response**:
```json
{
    "user": {
        "id": 123,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+1234567890",
        "user_type": "patient",
        "wallet_balance": 100.00,
        "date_joined": "2024-01-15T10:30:00Z"
    }
}
```

### Update Profile

**Endpoint**: `POST /accounts/profile/`

**Request Body**:
```json
{
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890"
}
```

### Password Reset

**Endpoint**: `POST /accounts/password/reset/`

**Request Body**:
```json
{
    "email": "user@example.com"
}
```

**Response**:
```json
{
    "success": true,
    "message": "Password reset email sent"
}
```

## Doctor Management API

### List Doctors

**Endpoint**: `GET /doctors/`

**Query Parameters**:
- `specialty` (optional): Filter by specialty ID
- `search` (optional): Search by doctor name
- `page` (optional): Page number for pagination
- `limit` (optional): Number of results per page

**Response**:
```json
{
    "doctors": [
        {
            "id": 1,
            "name": "Dr. Jane Smith",
            "specialty": "Cardiology",
            "experience_years": 10,
            "consultation_fee": 150.00,
            "average_rating": 4.8,
            "total_reviews": 45,
            "bio": "Experienced cardiologist with 10 years of practice..."
        }
    ],
    "pagination": {
        "page": 1,
        "total_pages": 5,
        "total_count": 25,
        "has_next": true,
        "has_previous": false
    }
}
```

### Doctor Details

**Endpoint**: `GET /doctors/{doctor_id}/`

**Response**:
```json
{
    "id": 1,
    "name": "Dr. Jane Smith",
    "specialty": {
        "id": 1,
        "name": "Cardiology",
        "description": "Heart and cardiovascular system specialist"
    },
    "experience_years": 10,
    "consultation_fee": 150.00,
    "average_rating": 4.8,
    "total_reviews": 45,
    "bio": "Experienced cardiologist with 10 years of practice...",
    "license_number": "MD123456",
    "is_active": true,
    "reviews": [
        {
            "id": 1,
            "rating": 5,
            "comment": "Excellent doctor, very professional",
            "patient_name": "John D.",
            "created_at": "2024-01-10T14:30:00Z"
        }
    ]
}
```

### List Specialties

**Endpoint**: `GET /doctors/specialties/`

**Response**:
```json
{
    "specialties": [
        {
            "id": 1,
            "name": "Cardiology",
            "description": "Heart and cardiovascular system specialist"
        },
        {
            "id": 2,
            "name": "Dermatology",
            "description": "Skin, hair, and nail specialist"
        }
    ]
}
```

## Appointment Booking API

### Available Time Slots

**Endpoint**: `GET /appointments/calendar/{doctor_id}/`

**Query Parameters**:
- `date` (optional): Specific date (YYYY-MM-DD format)
- `month` (optional): Month and year (YYYY-MM format)

**Response**:
```json
{
    "doctor": {
        "id": 1,
        "name": "Dr. Jane Smith",
        "consultation_fee": 150.00
    },
    "available_slots": [
        {
            "id": 1,
            "date": "2024-01-15",
            "start_time": "09:00:00",
            "end_time": "09:30:00",
            "is_available": true
        },
        {
            "id": 2,
            "date": "2024-01-15",
            "start_time": "09:30:00",
            "end_time": "10:00:00",
            "is_available": true
        }
    ]
}
```

### Book Appointment

**Endpoint**: `POST /appointments/reserve/{slot_id}/`

**Request Body**:
```json
{
    "notes": "Regular checkup appointment",
    "payment_method": "wallet"
}
```

**Response**:
```json
{
    "success": true,
    "appointment": {
        "id": 123,
        "doctor": "Dr. Jane Smith",
        "date": "2024-01-15",
        "time": "09:00:00",
        "status": "pending",
        "consultation_fee": 150.00,
        "notes": "Regular checkup appointment"
    },
    "payment_required": true
}
```

### List Appointments

**Endpoint**: `GET /appointments/`

**Query Parameters**:
- `status` (optional): Filter by status (pending, confirmed, completed, cancelled)
- `doctor_id` (optional): Filter by doctor
- `date_from` (optional): Start date filter
- `date_to` (optional): End date filter

**Response**:
```json
{
    "appointments": [
        {
            "id": 123,
            "doctor": {
                "id": 1,
                "name": "Dr. Jane Smith",
                "specialty": "Cardiology"
            },
            "date": "2024-01-15",
            "time": "09:00:00",
            "status": "confirmed",
            "consultation_fee": 150.00,
            "notes": "Regular checkup appointment"
        }
    ],
    "pagination": {
        "page": 1,
        "total_pages": 3,
        "total_count": 15,
        "has_next": true,
        "has_previous": false
    }
}
```

### Appointment Details

**Endpoint**: `GET /appointments/{appointment_id}/`

**Response**:
```json
{
    "id": 123,
    "doctor": {
        "id": 1,
        "name": "Dr. Jane Smith",
        "specialty": "Cardiology",
        "phone": "+1234567890"
    },
    "patient": {
        "id": 456,
        "name": "John Doe",
        "phone": "+1234567890"
    },
    "date": "2024-01-15",
    "time": "09:00:00",
    "status": "confirmed",
    "consultation_fee": 150.00,
    "notes": "Regular checkup appointment",
    "created_at": "2024-01-10T14:30:00Z",
    "updated_at": "2024-01-10T14:30:00Z"
}
```

### Cancel Appointment

**Endpoint**: `POST /appointments/{appointment_id}/cancel/`

**Request Body**:
```json
{
    "reason": "Schedule conflict"
}
```

**Response**:
```json
{
    "success": true,
    "message": "Appointment cancelled successfully",
    "refund_amount": 150.00
}
```

## Payment API

### Wallet Details

**Endpoint**: `GET /payments/wallet/`

**Response**:
```json
{
    "balance": 250.00,
    "transactions": [
        {
            "id": 1,
            "type": "deposit",
            "amount": 100.00,
            "description": "Wallet top-up",
            "balance_after": 250.00,
            "created_at": "2024-01-10T14:30:00Z"
        }
    ]
}
```

### Add Money to Wallet

**Endpoint**: `POST /payments/deposit/`

**Request Body**:
```json
{
    "amount": 100.00,
    "payment_method": "card"
}
```

**Response**:
```json
{
    "success": true,
    "transaction_id": "txn_123456789",
    "new_balance": 350.00
}
```

### Process Payment

**Endpoint**: `POST /payments/process/{appointment_id}/`

**Request Body**:
```json
{
    "payment_method": "wallet"
}
```

**Response**:
```json
{
    "success": true,
    "payment": {
        "id": 789,
        "amount": 150.00,
        "status": "completed",
        "transaction_id": "txn_123456789",
        "paid_at": "2024-01-10T14:30:00Z"
    }
}
```

### Payment History

**Endpoint**: `GET /payments/history/`

**Query Parameters**:
- `page` (optional): Page number
- `limit` (optional): Results per page
- `type` (optional): Transaction type (deposit, withdrawal, payment)

**Response**:
```json
{
    "transactions": [
        {
            "id": 1,
            "type": "payment",
            "amount": -150.00,
            "description": "Appointment payment - Dr. Jane Smith",
            "balance_after": 100.00,
            "appointment_id": 123,
            "created_at": "2024-01-10T14:30:00Z"
        }
    ],
    "pagination": {
        "page": 1,
        "total_pages": 5,
        "total_count": 25,
        "has_next": true,
        "has_previous": false
    }
}
```

## Review API

### Submit Review

**Endpoint**: `POST /reviews/submit/`

**Request Body**:
```json
{
    "appointment_id": 123,
    "rating": 5,
    "comment": "Excellent service, very professional",
    "is_anonymous": false
}
```

**Response**:
```json
{
    "success": true,
    "review": {
        "id": 456,
        "rating": 5,
        "comment": "Excellent service, very professional",
        "is_anonymous": false,
        "created_at": "2024-01-15T10:30:00Z"
    }
}
```

### Get Doctor Reviews

**Endpoint**: `GET /reviews/doctor/{doctor_id}/`

**Query Parameters**:
- `page` (optional): Page number
- `limit` (optional): Results per page
- `rating` (optional): Filter by rating (1-5)

**Response**:
```json
{
    "doctor": {
        "id": 1,
        "name": "Dr. Jane Smith",
        "average_rating": 4.8,
        "total_reviews": 45
    },
    "reviews": [
        {
            "id": 456,
            "rating": 5,
            "comment": "Excellent service, very professional",
            "patient_name": "John D.",
            "created_at": "2024-01-15T10:30:00Z"
        }
    ],
    "pagination": {
        "page": 1,
        "total_pages": 3,
        "total_count": 45,
        "has_next": true,
        "has_previous": false
    }
}
```

## Error Responses

### Standard Error Format

```json
{
    "error": true,
    "message": "Error description",
    "code": "ERROR_CODE",
    "details": {
        "field": "Specific field error if applicable"
    }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `AUTHENTICATION_REQUIRED` | 401 | User not authenticated |
| `PERMISSION_DENIED` | 403 | User lacks required permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `INSUFFICIENT_FUNDS` | 400 | Wallet balance insufficient |
| `APPOINTMENT_CONFLICT` | 400 | Time slot already booked |
| `INVALID_TIME_SLOT` | 400 | Time slot not available |
| `PAYMENT_FAILED` | 400 | Payment processing failed |

### Example Error Response

```json
{
    "error": true,
    "message": "Validation failed",
    "code": "VALIDATION_ERROR",
    "details": {
        "email": ["Enter a valid email address."],
        "password": ["Password must be at least 8 characters long."]
    }
}
```

## Rate Limiting

- **General API**: 1000 requests per hour per user
- **Authentication**: 10 login attempts per minute per IP
- **Payment**: 5 payment attempts per minute per user

## Pagination

All list endpoints support pagination with these parameters:

- `page`: Page number (default: 1)
- `limit`: Results per page (default: 20, max: 100)

Response includes pagination metadata:

```json
{
    "pagination": {
        "page": 1,
        "total_pages": 5,
        "total_count": 100,
        "has_next": true,
        "has_previous": false
    }
}
```

## Webhooks (Future Feature)

Webhooks will be available for:
- Appointment status changes
- Payment confirmations
- New review submissions

## SDKs and Libraries

### Python
```python
import requests

# Example API call
response = requests.get('http://localhost:8000/api/doctors/')
doctors = response.json()
```

### JavaScript
```javascript
// Example API call
fetch('/api/doctors/')
    .then(response => response.json())
    .then(data => console.log(data));
```

## Testing

### Test Environment
- **Base URL**: `http://localhost:8000`
- **Test User**: `test@example.com` / `testpassword123`
- **Test Doctor**: Dr. Test User (ID: 1)

### Postman Collection
A Postman collection is available in `/documents/postman_collection.json` for testing all endpoints.

## Support

For API support and questions:
- **Documentation**: Check this guide and inline code comments
- **Issues**: Create GitHub issues for bugs
- **Email**: Contact the development team
