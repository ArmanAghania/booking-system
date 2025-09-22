# Database Schema Documentation

## Overview

This document provides a comprehensive overview of the database schema for the Booking System. The system uses PostgreSQL as the primary database with Django ORM for data modeling.

## Database Architecture

### Technology Stack
- **Database**: PostgreSQL 15+
- **ORM**: Django ORM
- **Migrations**: Django migrations
- **Connection Pooling**: django-db-connection-pool (optional)

### Database Design Principles
- **Normalization**: 3NF compliance for data integrity
- **Referential Integrity**: Foreign key constraints
- **Indexing**: Optimized for common queries
- **Audit Trail**: Created/updated timestamps on all models

## Core Models

### User Management

#### User Model
```python
class User(AbstractUser):
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=20, blank=True)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Fields**:
- `id`: Primary key (auto-increment)
- `username`: Unique username (inherited from AbstractUser)
- `email`: Email address (inherited from AbstractUser)
- `first_name`: User's first name
- `last_name`: User's last name
- `user_type`: Type of user (admin, patient, doctor)
- `phone_number`: Contact phone number
- `wallet_balance`: Available wallet balance
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp

**Indexes**:
- Primary key on `id`
- Unique index on `username`
- Unique index on `email`
- Index on `user_type` for filtering

#### OTPVerification Model
```python
class OTPVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
```

**Purpose**: Email verification system
**Relationships**: One-to-many with User

### Medical Specialties

#### Specialty Model
```python
class Specialty(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Fields**:
- `id`: Primary key
- `name`: Specialty name (e.g., "Cardiology")
- `description`: Detailed description
- `created_at`: Creation timestamp

**Indexes**:
- Primary key on `id`
- Unique index on `name`

### Doctor Management

#### Doctor Model
```python
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=50, unique=True)
    experience_years = models.PositiveIntegerField()
    bio = models.TextField()
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_doctors')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Fields**:
- `id`: Primary key
- `user`: One-to-one relationship with User
- `specialty`: Foreign key to Specialty
- `license_number`: Medical license number
- `experience_years`: Years of experience
- `bio`: Doctor's biography
- `consultation_fee`: Fee per consultation
- `is_active`: Whether doctor is accepting patients
- `average_rating`: Calculated average rating
- `total_reviews`: Total number of reviews
- `created_by`: Admin who created the doctor profile
- `created_at`: Profile creation timestamp
- `updated_at`: Last update timestamp

**Indexes**:
- Primary key on `id`
- Unique index on `license_number`
- Index on `specialty` for filtering
- Index on `is_active` for filtering
- Index on `average_rating` for sorting

### Time Management

#### TimeSlot Model
```python
class TimeSlot(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Fields**:
- `id`: Primary key
- `doctor`: Foreign key to Doctor
- `date`: Available date
- `start_time`: Slot start time
- `end_time`: Slot end time
- `is_available`: Whether slot is available for booking
- `created_by`: User who created the slot
- `created_at`: Creation timestamp

**Indexes**:
- Primary key on `id`
- Composite index on `(doctor, date, start_time)`
- Index on `is_available` for filtering
- Index on `date` for date-based queries

### Appointment System

#### Appointment Model
```python
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='doctor_appointments')
    time_slot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    confirmation_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Fields**:
- `id`: Primary key
- `patient`: Foreign key to User (patient)
- `doctor`: Foreign key to Doctor
- `time_slot`: One-to-one with TimeSlot
- `status`: Current appointment status
- `consultation_fee`: Fee for this appointment
- `notes`: Patient notes for the appointment
- `confirmation_sent`: Email confirmation status
- `created_at`: Booking timestamp
- `updated_at`: Last update timestamp

**Indexes**:
- Primary key on `id`
- Index on `patient` for patient queries
- Index on `doctor` for doctor queries
- Index on `status` for filtering
- Index on `created_at` for date-based queries
- Composite index on `(patient, status)`

### Payment System

#### Payment Model
```python
class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Fields**:
- `id`: Primary key
- `appointment`: One-to-one with Appointment
- `amount`: Payment amount
- `status`: Payment status
- `transaction_id`: External transaction ID
- `paid_at`: Payment completion timestamp
- `created_at`: Payment creation timestamp

**Indexes**:
- Primary key on `id`
- Unique index on `transaction_id`
- Index on `status` for filtering
- Index on `paid_at` for date-based queries

#### WalletTransaction Model
```python
class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('payment', 'Payment'),
        ('refund', 'Refund'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Fields**:
- `id`: Primary key
- `user`: Foreign key to User
- `transaction_type`: Type of transaction
- `amount`: Transaction amount (positive for deposits, negative for payments)
- `description`: Transaction description
- `balance_after`: Wallet balance after transaction
- `appointment`: Related appointment (if applicable)
- `created_at`: Transaction timestamp

**Indexes**:
- Primary key on `id`
- Index on `user` for user queries
- Index on `transaction_type` for filtering
- Index on `created_at` for date-based queries
- Composite index on `(user, created_at)`

### Review System

#### Review Model
```python
class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Fields**:
- `id`: Primary key
- `appointment`: One-to-one with Appointment
- `patient`: Foreign key to User (reviewer)
- `doctor`: Foreign key to Doctor (reviewed)
- `rating`: Star rating (1-5)
- `comment`: Written review
- `is_anonymous`: Whether review is anonymous
- `created_at`: Review submission timestamp
- `updated_at`: Last update timestamp

**Indexes**:
- Primary key on `id`
- Index on `doctor` for doctor queries
- Index on `rating` for filtering
- Index on `created_at` for date-based queries
- Composite index on `(doctor, rating)`

## Database Relationships

### Entity Relationship Diagram

```
User (1) ←→ (1) Doctor
User (1) ←→ (0..*) Appointment (as patient)
User (1) ←→ (0..*) WalletTransaction
User (1) ←→ (0..*) Review (as reviewer)

Specialty (1) ←→ (0..*) Doctor

Doctor (1) ←→ (0..*) TimeSlot
Doctor (1) ←→ (0..*) Appointment
Doctor (1) ←→ (0..*) Review (as reviewed)

TimeSlot (1) ←→ (0..1) Appointment

Appointment (1) ←→ (1) Payment
Appointment (1) ←→ (0..1) Review
Appointment (1) ←→ (0..*) WalletTransaction
```

### Key Relationships

1. **User → Doctor**: One-to-one (doctor profile)
2. **User → Appointments**: One-to-many (patient appointments)
3. **Doctor → TimeSlots**: One-to-many (availability)
4. **Doctor → Appointments**: One-to-many (doctor's appointments)
5. **TimeSlot → Appointment**: One-to-one (booking)
6. **Appointment → Payment**: One-to-one (payment record)
7. **Appointment → Review**: One-to-one (review after completion)

## Database Constraints

### Primary Keys
- All models have auto-incrementing integer primary keys
- Primary keys are named `id` for consistency

### Foreign Keys
- All foreign keys have `on_delete` constraints defined
- `CASCADE`: Delete related records when parent is deleted
- `SET_NULL`: Set to NULL when parent is deleted
- `PROTECT`: Prevent deletion if related records exist

### Unique Constraints
- `User.username`: Unique username
- `User.email`: Unique email address
- `Doctor.license_number`: Unique license number
- `Payment.transaction_id`: Unique transaction ID
- `Appointment.time_slot`: One appointment per time slot
- `Review.appointment`: One review per appointment

### Check Constraints
- `User.wallet_balance >= 0`: Non-negative wallet balance
- `Review.rating BETWEEN 1 AND 5`: Valid rating range
- `Doctor.experience_years >= 0`: Non-negative experience
- `TimeSlot.end_time > start_time`: Valid time range

## Indexing Strategy

### Primary Indexes
- All primary keys are automatically indexed
- Foreign keys are automatically indexed

### Performance Indexes
- **User queries**: `user_type`, `email`
- **Doctor queries**: `specialty`, `is_active`, `average_rating`
- **Appointment queries**: `patient`, `doctor`, `status`, `created_at`
- **TimeSlot queries**: `doctor`, `date`, `is_available`
- **Payment queries**: `status`, `paid_at`
- **Review queries**: `doctor`, `rating`, `created_at`

### Composite Indexes
- `(doctor, date, start_time)`: TimeSlot availability
- `(patient, status)`: Patient appointment filtering
- `(doctor, rating)`: Doctor review filtering
- `(user, created_at)`: User transaction history

## Data Validation

### Model-Level Validation
- **Email format**: Django's built-in email validation
- **Phone number**: Custom validation for international formats
- **Decimal precision**: Consistent decimal places for currency
- **Date/time**: Future date validation for appointments
- **Rating range**: 1-5 star validation

### Database-Level Validation
- **NOT NULL constraints**: Required fields
- **CHECK constraints**: Value range validation
- **UNIQUE constraints**: Data uniqueness
- **FOREIGN KEY constraints**: Referential integrity

## Migration Strategy

### Initial Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### Data Migration Examples
```python
# Example: Update doctor ratings
def update_doctor_ratings(apps, schema_editor):
    Doctor = apps.get_model('doctors', 'Doctor')
    Review = apps.get_model('reviews', 'Review')
    
    for doctor in Doctor.objects.all():
        reviews = Review.objects.filter(doctor=doctor)
        if reviews.exists():
            avg_rating = reviews.aggregate(avg=models.Avg('rating'))['avg']
            doctor.average_rating = round(avg_rating, 2)
            doctor.total_reviews = reviews.count()
            doctor.save()
```

## Performance Optimization

### Query Optimization
- **Select related**: Use `select_related()` for foreign keys
- **Prefetch related**: Use `prefetch_related()` for reverse relationships
- **Database views**: Create views for complex queries
- **Raw SQL**: Use for complex aggregations

### Caching Strategy
- **Model caching**: Cache frequently accessed models
- **Query caching**: Cache expensive queries
- **Session caching**: Cache user sessions
- **Redis**: Use Redis for session and cache storage

### Database Maintenance
- **Regular VACUUM**: Clean up deleted records
- **ANALYZE**: Update query statistics
- **Index maintenance**: Monitor index usage
- **Connection pooling**: Manage database connections

## Backup and Recovery

### Backup Strategy
- **Daily backups**: Full database backups
- **Incremental backups**: Transaction log backups
- **Point-in-time recovery**: Restore to specific timestamp
- **Cross-region replication**: Geographic redundancy

### Recovery Procedures
- **Full restore**: Complete database restoration
- **Partial restore**: Restore specific tables
- **Data migration**: Move data between environments
- **Rollback procedures**: Revert to previous state

## Security Considerations

### Data Protection
- **Encryption at rest**: Database-level encryption
- **Encryption in transit**: SSL/TLS connections
- **Access control**: Role-based permissions
- **Audit logging**: Track all database changes

### Compliance
- **GDPR compliance**: Data protection regulations
- **HIPAA compliance**: Healthcare data protection
- **Data retention**: Automated data cleanup
- **Privacy controls**: User data management

## Monitoring and Maintenance

### Performance Monitoring
- **Query performance**: Slow query identification
- **Index usage**: Index effectiveness monitoring
- **Connection monitoring**: Database connection health
- **Storage monitoring**: Disk space usage

### Maintenance Tasks
- **Regular updates**: Database software updates
- **Security patches**: Apply security fixes
- **Performance tuning**: Optimize based on usage
- **Capacity planning**: Plan for growth

## Development Guidelines

### Model Design
- **Single responsibility**: Each model has one purpose
- **Normalization**: Follow 3NF principles
- **Naming conventions**: Consistent naming
- **Documentation**: Comprehensive docstrings

### Migration Guidelines
- **Backward compatibility**: Maintain API compatibility
- **Data integrity**: Validate data during migrations
- **Rollback planning**: Plan for migration failures
- **Testing**: Test migrations in staging

### Code Standards
- **Django best practices**: Follow Django conventions
- **Type hints**: Use type annotations
- **Error handling**: Comprehensive error handling
- **Logging**: Detailed logging for debugging
