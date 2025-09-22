# Troubleshooting Guide

## Overview

This comprehensive troubleshooting guide helps resolve common issues encountered when using the Booking System. The guide is organized by issue type and provides step-by-step solutions.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Database Issues](#database-issues)
3. [Authentication Issues](#authentication-issues)
4. [Appointment Issues](#appointment-issues)
5. [Payment Issues](#payment-issues)
6. [Email Issues](#email-issues)
7. [Performance Issues](#performance-issues)
8. [Docker Issues](#docker-issues)
9. [Development Issues](#development-issues)
10. [Production Issues](#production-issues)
11. [User Issues](#user-issues)
12. [Emergency Procedures](#emergency-procedures)

## Installation Issues

### Python Environment Issues

#### Issue: Python Version Not Supported

**Symptoms:**
- `Python 3.10+ is required` error
- Import errors for Python modules
- Syntax errors in Python 3.10+ features

**Solutions:**

1. **Check Python Version:**
```bash
python --version
python3 --version
```

2. **Install Python 3.10+:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev

# macOS (using Homebrew)
brew install python@3.10

# Windows
# Download from https://www.python.org/downloads/
```

3. **Create Virtual Environment:**
```bash
python3.10 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

#### Issue: Virtual Environment Not Working

**Symptoms:**
- `command not found` errors
- Packages installed globally instead of in venv
- Import errors for installed packages

**Solutions:**

1. **Verify Virtual Environment:**
```bash
which python
which pip
# Should point to venv/bin/python and venv/bin/pip
```

2. **Recreate Virtual Environment:**
```bash
rm -rf venv
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

3. **Check Activation:**
```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Dependency Installation Issues

#### Issue: Package Installation Fails

**Symptoms:**
- `pip install` fails with errors
- Package conflicts
- Build errors for native packages

**Solutions:**

1. **Update pip and setuptools:**
```bash
pip install --upgrade pip setuptools wheel
```

2. **Install system dependencies:**
```bash
# Ubuntu/Debian
sudo apt install build-essential libpq-dev python3-dev

# macOS
xcode-select --install
brew install postgresql

# Windows
# Install Visual Studio Build Tools
```

3. **Install packages individually:**
```bash
pip install django
pip install psycopg2-binary
pip install -r requirements.txt
```

#### Issue: psycopg2 Installation Fails

**Symptoms:**
- `error: Microsoft Visual C++ 14.0 is required`
- `fatal error: Python.h: No such file or directory`
- PostgreSQL development headers not found

**Solutions:**

1. **Install PostgreSQL development headers:**
```bash
# Ubuntu/Debian
sudo apt install libpq-dev python3-dev

# macOS
brew install postgresql

# Windows
# Install PostgreSQL from https://www.postgresql.org/download/windows/
```

2. **Use binary package:**
```bash
pip install psycopg2-binary
```

3. **Alternative installation:**
```bash
pip install psycopg2-binary --no-cache-dir
```

## Database Issues

### PostgreSQL Connection Issues

#### Issue: Database Connection Refused

**Symptoms:**
- `django.db.utils.OperationalError: could not connect to server`
- `FATAL: password authentication failed`
- `FATAL: database "booking_system" does not exist`

**Solutions:**

1. **Check PostgreSQL Status:**
```bash
# Ubuntu/Debian
sudo systemctl status postgresql

# macOS
brew services list | grep postgresql

# Windows
# Check Services in Control Panel
```

2. **Start PostgreSQL:**
```bash
# Ubuntu/Debian
sudo systemctl start postgresql
sudo systemctl enable postgresql

# macOS
brew services start postgresql

# Windows
# Start PostgreSQL service in Services
```

3. **Check Database and User:**
```bash
sudo -u postgres psql
\l  # List databases
\du  # List users
```

4. **Create Database and User:**
```bash
sudo -u postgres psql
CREATE DATABASE booking_system;
CREATE USER booking_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE booking_system TO booking_user;
\q
```

#### Issue: Migration Errors

**Symptoms:**
- `django.db.utils.ProgrammingError: relation does not exist`
- `django.db.utils.IntegrityError: duplicate key value`
- Migration conflicts

**Solutions:**

1. **Reset Migrations:**
```bash
# Backup database first
pg_dump booking_system > backup.sql

# Reset migrations
python manage.py migrate --fake-initial
```

2. **Handle Migration Conflicts:**
```bash
# Show migration status
python manage.py showmigrations

# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

3. **Reset Database (Development Only):**
```bash
# Drop and recreate database
sudo -u postgres psql
DROP DATABASE booking_system;
CREATE DATABASE booking_system;
GRANT ALL PRIVILEGES ON DATABASE booking_system TO booking_user;
\q

# Run migrations
python manage.py migrate
```

### Database Performance Issues

#### Issue: Slow Database Queries

**Symptoms:**
- Slow page load times
- Database timeout errors
- High CPU usage

**Solutions:**

1. **Add Database Indexes:**
```python
# In models.py
class Meta:
    indexes = [
        models.Index(fields=['user_type']),
        models.Index(fields=['created_at']),
        models.Index(fields=['status']),
    ]
```

2. **Optimize Queries:**
```python
# Use select_related for foreign keys
doctors = Doctor.objects.select_related('user', 'specialty').all()

# Use prefetch_related for reverse relationships
appointments = Appointment.objects.prefetch_related('patient', 'doctor').all()
```

3. **Database Configuration:**
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'booking_system',
        'USER': 'booking_user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'MAX_CONNS': 20,
        }
    }
}
```

## Authentication Issues

### Login Problems

#### Issue: User Cannot Log In

**Symptoms:**
- "Invalid credentials" error
- User account not found
- Account locked

**Solutions:**

1. **Check User Account:**
```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(email='user@example.com')
>>> user.is_active
>>> user.check_password('password')
```

2. **Reset User Password:**
```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(email='user@example.com')
>>> user.set_password('newpassword')
>>> user.save()
```

3. **Activate User Account:**
```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(email='user@example.com')
>>> user.is_active = True
>>> user.save()
```

#### Issue: OAuth Login Fails

**Symptoms:**
- Google OAuth redirect errors
- "Invalid client" error
- OAuth callback not working

**Solutions:**

1. **Check OAuth Configuration:**
```bash
# Check environment variables
echo $GOOGLE_OAUTH2_CLIENT_ID
echo $GOOGLE_OAUTH2_CLIENT_SECRET
```

2. **Verify Google Console Settings:**
- Check authorized redirect URIs
- Verify client ID and secret
- Check OAuth consent screen

3. **Test OAuth Flow:**
```bash
# Check Django settings
python manage.py shell
>>> from django.conf import settings
>>> print(settings.SOCIALACCOUNT_PROVIDERS)
```

### Session Issues

#### Issue: Session Expires Too Quickly

**Symptoms:**
- Users logged out frequently
- Session data lost
- "Session expired" errors

**Solutions:**

1. **Configure Session Settings:**
```python
# settings.py
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True
```

2. **Check Session Backend:**
```python
# settings.py
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
```

3. **Clear Sessions:**
```bash
python manage.py clearsessions
```

## Appointment Issues

### Booking Problems

#### Issue: Cannot Book Appointment

**Symptoms:**
- Time slot not available
- Booking form errors
- Payment processing fails

**Solutions:**

1. **Check Time Slot Availability:**
```bash
python manage.py shell
>>> from appointments.models import TimeSlot
>>> TimeSlot.objects.filter(doctor_id=1, is_available=True)
```

2. **Verify Payment Method:**
```bash
python manage.py shell
>>> from accounts.models import User
>>> user = User.objects.get(id=1)
>>> print(user.wallet_balance)
```

3. **Check Appointment Conflicts:**
```bash
python manage.py shell
>>> from appointments.models import Appointment
>>> Appointment.objects.filter(time_slot_id=1)
```

#### Issue: Appointment Not Showing

**Symptoms:**
- Appointment not in dashboard
- Email confirmation not sent
- Appointment status incorrect

**Solutions:**

1. **Check Appointment Status:**
```bash
python manage.py shell
>>> from appointments.models import Appointment
>>> appointment = Appointment.objects.get(id=1)
>>> print(appointment.status)
```

2. **Resend Email Confirmation:**
```bash
python manage.py shell
>>> from appointments.services import AppointmentEmailService
>>> service = AppointmentEmailService()
>>> service.send_confirmation(appointment)
```

3. **Update Appointment Status:**
```bash
python manage.py shell
>>> from appointments.models import Appointment
>>> appointment = Appointment.objects.get(id=1)
>>> appointment.status = 'confirmed'
>>> appointment.save()
```

### Time Slot Issues

#### Issue: Time Slots Not Available

**Symptoms:**
- No available time slots
- Time slots not showing
- Incorrect time slot display

**Solutions:**

1. **Check Time Slot Creation:**
```bash
python manage.py shell
>>> from appointments.models import TimeSlot
>>> TimeSlot.objects.filter(doctor_id=1, is_available=True)
```

2. **Create Time Slots:**
```bash
python manage.py shell
>>> from appointments.models import TimeSlot, Doctor
>>> doctor = Doctor.objects.get(id=1)
>>> TimeSlot.objects.create(
...     doctor=doctor,
...     date='2024-01-15',
...     start_time='09:00:00',
...     end_time='09:30:00',
...     is_available=True
... )
```

3. **Bulk Create Time Slots:**
```bash
python manage.py create_sample_data
```

## Payment Issues

### Payment Processing Failures

#### Issue: Payment Not Processing

**Symptoms:**
- Payment form errors
- Transaction failed
- Payment not recorded

**Solutions:**

1. **Check Payment Configuration:**
```bash
# Check environment variables
echo $STRIPE_PUBLISHABLE_KEY
echo $STRIPE_SECRET_KEY
```

2. **Test Payment Processing:**
```bash
python manage.py shell
>>> from payments.services import PaymentProcessor
>>> processor = PaymentProcessor()
>>> result = processor.process_payment(amount=100, method='card')
```

3. **Check Payment Status:**
```bash
python manage.py shell
>>> from payments.models import Payment
>>> Payment.objects.filter(status='pending')
```

#### Issue: Wallet Balance Issues

**Symptoms:**
- Incorrect wallet balance
- Transaction not recorded
- Balance not updating

**Solutions:**

1. **Check Wallet Balance:**
```bash
python manage.py shell
>>> from accounts.models import User
>>> user = User.objects.get(id=1)
>>> print(user.wallet_balance)
```

2. **Update Wallet Balance:**
```bash
python manage.py shell
>>> from accounts.models import User
>>> user = User.objects.get(id=1)
>>> user.wallet_balance = 100.00
>>> user.save()
```

3. **Check Transaction History:**
```bash
python manage.py shell
>>> from payments.models import WalletTransaction
>>> WalletTransaction.objects.filter(user_id=1)
```

### Refund Issues

#### Issue: Refund Not Processed

**Symptoms:**
- Refund not showing in wallet
- Refund status pending
- Refund amount incorrect

**Solutions:**

1. **Check Refund Status:**
```bash
python manage.py shell
>>> from payments.models import Payment
>>> payment = Payment.objects.get(id=1)
>>> print(payment.status)
```

2. **Process Refund:**
```bash
python manage.py shell
>>> from payments.services import PaymentProcessor
>>> processor = PaymentProcessor()
>>> processor.process_refund(payment_id=1)
```

3. **Update Refund Status:**
```bash
python manage.py shell
>>> from payments.models import Payment
>>> payment = Payment.objects.get(id=1)
>>> payment.status = 'refunded'
>>> payment.save()
```

## Email Issues

### Email Not Sending

#### Issue: Emails Not Delivered

**Symptoms:**
- No email confirmations
- Email errors in logs
- SMTP connection failed

**Solutions:**

1. **Check Email Configuration:**
```bash
# Check environment variables
echo $EMAIL_HOST
echo $EMAIL_PORT
echo $EMAIL_HOST_USER
```

2. **Test Email Sending:**
```bash
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

3. **Check Email Backend:**
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Development
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Production
```

#### Issue: SMTP Authentication Failed

**Symptoms:**
- "Authentication failed" error
- SMTP connection refused
- Gmail app password required

**Solutions:**

1. **Check SMTP Settings:**
```python
# settings.py
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Not your regular password
```

2. **Generate App Password (Gmail):**
- Go to Google Account settings
- Enable 2-factor authentication
- Generate app password
- Use app password in EMAIL_HOST_PASSWORD

3. **Test SMTP Connection:**
```bash
python manage.py shell
>>> from django.core.mail import get_connection
>>> connection = get_connection()
>>> connection.open()
>>> connection.close()
```

### Email Template Issues

#### Issue: Email Templates Not Loading

**Symptoms:**
- Template not found errors
- Email formatting issues
- Missing email content

**Solutions:**

1. **Check Template Paths:**
```bash
# Check if templates exist
ls -la templates/accounts/emails/
ls -la templates/appointments/emails/
```

2. **Test Email Templates:**
```bash
python manage.py shell
>>> from django.template.loader import render_to_string
>>> html = render_to_string('accounts/emails/verification_email.html', {'user': user})
```

3. **Update Template Settings:**
```python
# settings.py
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

## Performance Issues

### Slow Page Load Times

#### Issue: Application Running Slow

**Symptoms:**
- Slow page responses
- High server load
- Database timeout errors

**Solutions:**

1. **Check Database Queries:**
```bash
# Enable query logging
python manage.py shell
>>> from django.db import connection
>>> from django.conf import settings
>>> settings.DEBUG = True
>>> print(connection.queries)
```

2. **Optimize Database Queries:**
```python
# Use select_related and prefetch_related
doctors = Doctor.objects.select_related('user', 'specialty').all()
appointments = Appointment.objects.prefetch_related('patient', 'doctor').all()
```

3. **Add Database Indexes:**
```python
# In models.py
class Meta:
    indexes = [
        models.Index(fields=['user_type']),
        models.Index(fields=['created_at']),
        models.Index(fields=['status']),
    ]
```

#### Issue: Memory Usage High

**Symptoms:**
- Out of memory errors
- Slow server response
- High CPU usage

**Solutions:**

1. **Check Memory Usage:**
```bash
# Check system memory
free -h
htop
```

2. **Optimize Gunicorn Workers:**
```bash
# Reduce workers
gunicorn booking_system.wsgi:application --bind 0.0.0.0:8000 --workers 2
```

3. **Enable Caching:**
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### Static Files Issues

#### Issue: Static Files Not Loading

**Symptoms:**
- CSS/JS files return 404
- Broken page styling
- Static files not found

**Solutions:**

1. **Collect Static Files:**
```bash
python manage.py collectstatic --noinput
```

2. **Check Static Files Configuration:**
```python
# settings.py
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
```

3. **Check File Permissions:**
```bash
# Check static files directory
ls -la static/
chmod -R 755 static/
```

## Docker Issues

### Container Issues

#### Issue: Docker Container Not Starting

**Symptoms:**
- Container exits immediately
- Port binding errors
- Volume mount issues

**Solutions:**

1. **Check Container Logs:**
```bash
docker-compose logs web
docker-compose logs db
```

2. **Check Docker Configuration:**
```bash
# Check docker-compose.yml
docker-compose config

# Check Dockerfile
docker build -t booking-system .
```

3. **Rebuild Containers:**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### Issue: Database Connection in Docker

**Symptoms:**
- Database connection refused
- Container networking issues
- Environment variable problems

**Solutions:**

1. **Check Container Networking:**
```bash
docker network ls
docker network inspect booking-system_default
```

2. **Check Environment Variables:**
```bash
docker-compose exec web env | grep DATABASE
```

3. **Test Database Connection:**
```bash
docker-compose exec web python manage.py dbshell
```

### Volume Issues

#### Issue: Volume Mount Not Working

**Symptoms:**
- Files not persisting
- Permission denied errors
- Volume not mounting

**Solutions:**

1. **Check Volume Mounts:**
```bash
docker-compose exec web ls -la /var/www/booking-system/
```

2. **Fix Volume Permissions:**
```bash
# Check volume permissions
docker-compose exec web ls -la /var/www/booking-system/static/
```

3. **Recreate Volumes:**
```bash
docker-compose down -v
docker-compose up -d
```

## Development Issues

### Code Quality Issues

#### Issue: Linting Errors

**Symptoms:**
- Flake8 errors
- Black formatting issues
- Import sorting problems

**Solutions:**

1. **Fix Flake8 Errors:**
```bash
flake8 .
# Fix the errors shown
```

2. **Format Code with Black:**
```bash
black .
```

3. **Sort Imports:**
```bash
isort .
```

#### Issue: Test Failures

**Symptoms:**
- Tests failing
- Test database issues
- Test data problems

**Solutions:**

1. **Run Tests:**
```bash
pytest
pytest -v
pytest --cov=booking_system
```

2. **Check Test Database:**
```bash
python manage.py test --settings=booking_system.settings.test
```

3. **Fix Test Issues:**
```bash
# Check test database
python manage.py shell --settings=booking_system.settings.test
```

### Development Environment Issues

#### Issue: Debug Toolbar Not Showing

**Symptoms:**
- Debug toolbar not visible
- Internal IPs not configured
- Middleware not working

**Solutions:**

1. **Check Debug Toolbar Configuration:**
```python
# settings/development.py
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1', 'localhost']
```

2. **Check Internal IPs:**
```bash
python manage.py shell
>>> from django.conf import settings
>>> print(settings.INTERNAL_IPS)
```

3. **Enable Debug Mode:**
```python
# settings/development.py
DEBUG = True
```

#### Issue: Static Files in Development

**Symptoms:**
- Static files not loading
- CSS/JS not working
- Static files 404 errors

**Solutions:**

1. **Check Static Files Configuration:**
```python
# settings/development.py
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
```

2. **Serve Static Files:**
```bash
python manage.py runserver
# Static files should be served automatically in development
```

3. **Check Static Files Directory:**
```bash
ls -la static/
ls -la static/css/
ls -la static/js/
```

## Production Issues

### Server Issues

#### Issue: Application Not Responding

**Symptoms:**
- 502 Bad Gateway errors
- Application timeout
- Server not responding

**Solutions:**

1. **Check Application Status:**
```bash
# Check if application is running
ps aux | grep gunicorn
systemctl status booking-system
```

2. **Restart Application:**
```bash
systemctl restart booking-system
systemctl restart nginx
```

3. **Check Application Logs:**
```bash
journalctl -u booking-system -f
tail -f /var/log/booking-system/django.log
```

#### Issue: Database Connection Issues

**Symptoms:**
- Database connection errors
- Connection pool exhausted
- Database timeout

**Solutions:**

1. **Check Database Status:**
```bash
systemctl status postgresql
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

2. **Check Connection Limits:**
```bash
sudo -u postgres psql -c "SHOW max_connections;"
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"
```

3. **Restart Database:**
```bash
systemctl restart postgresql
```

### SSL/HTTPS Issues

#### Issue: SSL Certificate Problems

**Symptoms:**
- SSL certificate errors
- Mixed content warnings
- HTTPS not working

**Solutions:**

1. **Check SSL Certificate:**
```bash
openssl x509 -in /etc/letsencrypt/live/yourdomain.com/cert.pem -text -noout
```

2. **Renew SSL Certificate:**
```bash
certbot renew
systemctl reload nginx
```

3. **Check Nginx Configuration:**
```bash
nginx -t
systemctl reload nginx
```

## User Issues

### User Account Issues

#### Issue: User Cannot Access Account

**Symptoms:**
- Login not working
- Account locked
- Password reset not working

**Solutions:**

1. **Check User Account Status:**
```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(email='user@example.com')
>>> print(user.is_active)
>>> print(user.is_locked)
```

2. **Unlock User Account:**
```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(email='user@example.com')
>>> user.is_active = True
>>> user.save()
```

3. **Reset User Password:**
```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(email='user@example.com')
>>> user.set_password('newpassword')
>>> user.save()
```

### User Data Issues

#### Issue: User Data Not Saving

**Symptoms:**
- Profile updates not saving
- Data not persisting
- Form validation errors

**Solutions:**

1. **Check Form Validation:**
```bash
python manage.py shell
>>> from accounts.forms import UserProfileForm
>>> form = UserProfileForm(data={'first_name': 'John'})
>>> print(form.is_valid())
>>> print(form.errors)
```

2. **Check Database Permissions:**
```bash
python manage.py shell
>>> from accounts.models import User
>>> user = User.objects.get(id=1)
>>> user.first_name = 'John'
>>> user.save()
```

3. **Check Model Validation:**
```bash
python manage.py shell
>>> from accounts.models import User
>>> user = User.objects.get(id=1)
>>> user.full_clean()
```

## Emergency Procedures

### System Down

#### Issue: Complete System Failure

**Symptoms:**
- Website not accessible
- Database not responding
- All services down

**Solutions:**

1. **Check System Status:**
```bash
# Check system resources
htop
df -h
free -h

# Check services
systemctl status postgresql
systemctl status nginx
systemctl status booking-system
```

2. **Restart All Services:**
```bash
systemctl restart postgresql
systemctl restart nginx
systemctl restart booking-system
```

3. **Check Application Logs:**
```bash
journalctl -u booking-system -f
tail -f /var/log/booking-system/django.log
tail -f /var/log/nginx/error.log
```

### Data Recovery

#### Issue: Data Loss or Corruption

**Symptoms:**
- Data missing from database
- Database corruption
- Backup not available

**Solutions:**

1. **Check Database Integrity:**
```bash
sudo -u postgres psql -c "VACUUM ANALYZE;"
sudo -u postgres psql -c "REINDEX DATABASE booking_system;"
```

2. **Restore from Backup:**
```bash
# Stop application
systemctl stop booking-system

# Restore database
gunzip -c backup.sql.gz | psql -h localhost -U booking_user booking_system

# Start application
systemctl start booking-system
```

3. **Check Data Consistency:**
```bash
python manage.py shell
>>> from accounts.models import User
>>> print(User.objects.count())
>>> from appointments.models import Appointment
>>> print(Appointment.objects.count())
```

### Security Incidents

#### Issue: Security Breach

**Symptoms:**
- Unauthorized access
- Data breach
- Security alerts

**Solutions:**

1. **Immediate Response:**
```bash
# Change all passwords
# Disable compromised accounts
# Check access logs
tail -f /var/log/nginx/access.log
```

2. **Security Audit:**
```bash
# Check user accounts
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.filter(is_active=True)
```

3. **Implement Security Measures:**
```bash
# Update security settings
# Enable additional logging
# Review access controls
```

## Getting Help

### Support Channels

1. **Documentation:**
   - Check this troubleshooting guide
   - Review API documentation
   - Check user guide

2. **Community Support:**
   - GitHub issues
   - Community forum
   - Stack Overflow

3. **Professional Support:**
   - Contact development team
   - Hire system administrator
   - Use managed hosting services

### Reporting Issues

1. **Bug Reports:**
   - Describe the issue clearly
   - Include steps to reproduce
   - Provide error messages
   - Include system information

2. **Feature Requests:**
   - Describe the desired feature
   - Explain the use case
   - Provide examples
   - Consider implementation complexity

3. **Security Issues:**
   - Report privately
   - Include detailed information
   - Follow responsible disclosure
   - Wait for response before public disclosure

This troubleshooting guide provides comprehensive solutions for common issues encountered with the Booking System. For additional help or specific issues not covered here, please contact the development team or refer to the official documentation.
