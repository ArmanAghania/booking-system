# Security Guide

## Overview

This comprehensive security guide outlines best practices, security considerations, and implementation details for the Booking System. It covers authentication, data protection, network security, and compliance requirements.

## Table of Contents

1. [Security Architecture](#security-architecture)
2. [Authentication Security](#authentication-security)
3. [Data Protection](#data-protection)
4. [Network Security](#network-security)
5. [Application Security](#application-security)
6. [Database Security](#database-security)
7. [Email Security](#email-security)
8. [Payment Security](#payment-security)
9. [Infrastructure Security](#infrastructure-security)
10. [Compliance and Privacy](#compliance-and-privacy)
11. [Security Monitoring](#security-monitoring)
12. [Incident Response](#incident-response)
13. [Security Testing](#security-testing)
14. [Security Checklist](#security-checklist)

## Security Architecture

### Security Principles

**Defense in Depth:**
- Multiple layers of security controls
- Network, application, and data security
- Redundant security measures

**Least Privilege:**
- Users have minimum required permissions
- Principle of least access
- Regular permission reviews

**Zero Trust:**
- Never trust, always verify
- Continuous authentication
- Micro-segmentation

### Security Layers

```
┌─────────────────────────────────────┐
│           User Interface            │
├─────────────────────────────────────┤
│         Application Layer           │
├─────────────────────────────────────┤
│          Database Layer             │
├─────────────────────────────────────┤
│          Network Layer              │
├─────────────────────────────────────┤
│         Infrastructure Layer        │
└─────────────────────────────────────┘
```

## Authentication Security

### Password Security

#### Password Requirements

**Strong Password Policy:**
```python
# settings.py
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
```

**Password Complexity Requirements:**
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, symbols
- No common passwords
- No user information in password
- No sequential characters

#### Password Storage

**Secure Password Hashing:**
```python
# Django uses PBKDF2 by default
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]
```

**Password Reset Security:**
```python
# settings.py
PASSWORD_RESET_TIMEOUT = 3600  # 1 hour
PASSWORD_RESET_TOKEN_EXPIRY = 3600
```

### Multi-Factor Authentication (MFA)

#### TOTP Implementation

**Install Required Packages:**
```bash
pip install django-otp
pip install qrcode
```

**Configuration:**
```python
# settings.py
INSTALLED_APPS = [
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
]

MIDDLEWARE = [
    'django_otp.middleware.OTPMiddleware',
]
```

**MFA Views:**
```python
# views.py
from django_otp.decorators import otp_required
from django_otp.forms import OTPTokenForm

@otp_required
def secure_view(request):
    # This view requires MFA
    pass
```

#### SMS-Based MFA

**SMS OTP Implementation:**
```python
# services.py
import random
import string
from django.core.cache import cache
from django.core.mail import send_mail

class SMSOTPService:
    def generate_otp(self, phone_number):
        otp = ''.join(random.choices(string.digits, k=6))
        cache.set(f'otp_{phone_number}', otp, timeout=300)  # 5 minutes
        return otp
    
    def verify_otp(self, phone_number, otp):
        cached_otp = cache.get(f'otp_{phone_number}')
        return cached_otp == otp
```

### Session Security

#### Session Configuration

**Secure Session Settings:**
```python
# settings.py
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF protection
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600  # 1 hour
```

**Session Management:**
```python
# Custom session management
class SecureSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check for suspicious activity
        if self.is_suspicious(request):
            request.session.flush()
        
        response = self.get_response(request)
        return response
    
    def is_suspicious(self, request):
        # Implement suspicious activity detection
        pass
```

## Data Protection

### Data Encryption

#### Encryption at Rest

**Database Encryption:**
```python
# Use encrypted database fields
from django_cryptography.fields import encrypt

class User(models.Model):
    ssn = encrypt(models.CharField(max_length=11))
    credit_card = encrypt(models.CharField(max_length=19))
```

**File Encryption:**
```python
# Encrypt sensitive files
from cryptography.fernet import Fernet

class FileEncryption:
    def __init__(self, key):
        self.cipher = Fernet(key)
    
    def encrypt_file(self, file_path):
        with open(file_path, 'rb') as f:
            data = f.read()
        encrypted_data = self.cipher.encrypt(data)
        with open(file_path + '.enc', 'wb') as f:
            f.write(encrypted_data)
    
    def decrypt_file(self, encrypted_file_path):
        with open(encrypted_file_path, 'rb') as f:
            encrypted_data = f.read()
        decrypted_data = self.cipher.decrypt(encrypted_data)
        return decrypted_data
```

#### Encryption in Transit

**HTTPS Configuration:**
```python
# settings.py
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
```

**API Encryption:**
```python
# Use JWT for API authentication
import jwt
from datetime import datetime, timedelta

class JWTAuthentication:
    def generate_token(self, user):
        payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    
    def verify_token(self, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
```

### Data Anonymization

#### PII Protection

**Data Anonymization:**
```python
# Anonymize sensitive data
class DataAnonymizer:
    def anonymize_user_data(self, user):
        user.first_name = self.hash_data(user.first_name)
        user.last_name = self.hash_data(user.last_name)
        user.email = self.hash_email(user.email)
        user.phone_number = self.hash_phone(user.phone_number)
        return user
    
    def hash_data(self, data):
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()[:8]
    
    def hash_email(self, email):
        local, domain = email.split('@')
        return f"{local[:2]}***@{domain}"
    
    def hash_phone(self, phone):
        return f"{phone[:3]}***{phone[-4:]}"
```

#### Data Retention

**Data Retention Policy:**
```python
# Automatic data cleanup
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Delete old inactive users
        cutoff_date = timezone.now() - timedelta(days=365)
        User.objects.filter(
            last_login__lt=cutoff_date,
            is_active=False
        ).delete()
        
        # Delete old logs
        LogEntry.objects.filter(
            created_at__lt=cutoff_date
        ).delete()
```

## Network Security

### Firewall Configuration

#### UFW Firewall Rules

**Basic Firewall Setup:**
```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22

# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow PostgreSQL (if needed)
sudo ufw allow from 10.0.0.0/8 to any port 5432

# Deny all other traffic
sudo ufw default deny incoming
sudo ufw default allow outgoing
```

**Advanced Firewall Rules:**
```bash
# Rate limiting for SSH
sudo ufw limit ssh

# Allow specific IP ranges
sudo ufw allow from 192.168.1.0/24

# Block suspicious IPs
sudo ufw deny from 192.168.1.100
```

#### iptables Configuration

**Advanced iptables Rules:**
```bash
# Create iptables script
#!/bin/bash

# Clear existing rules
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X

# Set default policies
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow SSH
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow HTTP and HTTPS
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow PostgreSQL (if needed)
iptables -A INPUT -p tcp --dport 5432 -s 10.0.0.0/8 -j ACCEPT

# Rate limiting
iptables -A INPUT -p tcp --dport 22 -m limit --limit 3/min -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j DROP
```

### VPN and Remote Access

#### OpenVPN Configuration

**Server Configuration:**
```bash
# Install OpenVPN
sudo apt install openvpn easy-rsa

# Generate CA and certificates
make-ca
make-server-key
make-client-key client1

# Server configuration
port 1194
proto udp
dev tun
ca ca.crt
cert server.crt
key server.key
dh dh2048.pem
server 10.8.0.0 255.255.255.0
ifconfig-pool-persist ipp.txt
push "redirect-gateway def1 bypass-dhcp"
push "dhcp-option DNS 8.8.8.8"
push "dhcp-option DNS 8.8.4.4"
keepalive 10 120
cipher AES-256-CBC
user nobody
group nogroup
persist-key
persist-tun
status openvpn-status.log
verb 3
```

#### SSH Security

**SSH Hardening:**
```bash
# /etc/ssh/sshd_config
Port 2222
Protocol 2
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
PermitEmptyPasswords no
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
AllowUsers admin
DenyUsers root
```

## Application Security

### Input Validation

#### Form Validation

**Secure Form Handling:**
```python
# forms.py
from django import forms
from django.core.validators import RegexValidator

class UserRegistrationForm(forms.ModelForm):
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    phone_number = forms.CharField(validators=[phone_validator])
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 12:
            raise forms.ValidationError("Password must be at least 12 characters long")
        return password
```

#### API Input Validation

**API Security:**
```python
# views.py
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
import json

@method_decorator(csrf_exempt, name='dispatch')
@require_http_methods(["POST"])
def api_endpoint(request):
    try:
        data = json.loads(request.body)
        # Validate input data
        if not validate_input(data):
            return JsonResponse({'error': 'Invalid input'}, status=400)
        
        # Process data
        result = process_data(data)
        return JsonResponse(result)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Internal server error'}, status=500)
```

### SQL Injection Prevention

#### ORM Security

**Safe Database Queries:**
```python
# Safe ORM usage
def get_user_appointments(user_id):
    # Safe - uses parameterized queries
    return Appointment.objects.filter(patient_id=user_id)

def search_doctors(query):
    # Safe - uses parameterized queries
    return Doctor.objects.filter(
        Q(user__first_name__icontains=query) |
        Q(user__last_name__icontains=query)
    )

# Unsafe - don't do this
def unsafe_query(user_input):
    # This is vulnerable to SQL injection
    return Appointment.objects.raw(f"SELECT * FROM appointments WHERE notes = '{user_input}'")
```

#### Raw SQL Security

**Safe Raw SQL:**
```python
# Safe raw SQL with parameters
def get_appointments_by_date(date):
    return Appointment.objects.raw(
        "SELECT * FROM appointments WHERE date = %s",
        [date]
    )

# Unsafe raw SQL
def unsafe_raw_query(user_input):
    # This is vulnerable to SQL injection
    return Appointment.objects.raw(f"SELECT * FROM appointments WHERE notes = '{user_input}'")
```

### XSS Prevention

#### Template Security

**Safe Template Rendering:**
```html
<!-- Safe - Django auto-escapes -->
<p>{{ user.first_name }}</p>

<!-- Safe - explicit escaping -->
<p>{{ user.first_name|escape }}</p>

<!-- Unsafe - don't do this -->
<p>{{ user.first_name|safe }}</p>
```

**Content Security Policy:**
```python
# settings.py
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
CSP_OBJECT_SRC = ("'none'",)
CSP_MEDIA_SRC = ("'self'",)
CSP_FRAME_SRC = ("'none'",)
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)
```

### CSRF Protection

#### CSRF Configuration

**CSRF Settings:**
```python
# settings.py
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_TRUSTED_ORIGINS = ['https://yourdomain.com']
```

**CSRF in Templates:**
```html
<!-- Include CSRF token in forms -->
<form method="post">
    {% csrf_token %}
    <!-- form fields -->
</form>

<!-- AJAX CSRF token -->
<script>
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
</script>
```

## Database Security

### Database Access Control

#### User Permissions

**PostgreSQL User Setup:**
```sql
-- Create application user
CREATE USER booking_user WITH PASSWORD 'secure_password';

-- Grant minimal permissions
GRANT CONNECT ON DATABASE booking_system TO booking_user;
GRANT USAGE ON SCHEMA public TO booking_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO booking_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO booking_user;

-- Create read-only user for backups
CREATE USER backup_user WITH PASSWORD 'backup_password';
GRANT CONNECT ON DATABASE booking_system TO backup_user;
GRANT USAGE ON SCHEMA public TO backup_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup_user;
```

#### Row-Level Security

**PostgreSQL RLS:**
```sql
-- Enable row-level security
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;

-- Create policy for patients
CREATE POLICY patient_appointments ON appointments
    FOR ALL TO booking_user
    USING (patient_id = current_setting('app.current_user_id')::integer);

-- Create policy for doctors
CREATE POLICY doctor_appointments ON appointments
    FOR ALL TO booking_user
    USING (doctor_id = current_setting('app.current_doctor_id')::integer);
```

### Database Encryption

#### Transparent Data Encryption

**PostgreSQL TDE:**
```sql
-- Enable encryption
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/etc/ssl/certs/server.crt';
ALTER SYSTEM SET ssl_key_file = '/etc/ssl/private/server.key';

-- Restart PostgreSQL
SELECT pg_reload_conf();
```

#### Column-Level Encryption

**Encrypted Fields:**
```python
# models.py
from django_cryptography.fields import encrypt

class User(models.Model):
    ssn = encrypt(models.CharField(max_length=11, blank=True))
    credit_card = encrypt(models.CharField(max_length=19, blank=True))
    
    def get_ssn(self):
        return self.ssn  # Automatically decrypted
    
    def set_ssn(self, value):
        self.ssn = value  # Automatically encrypted
```

## Email Security

### SMTP Security

#### Secure Email Configuration

**SMTP Security Settings:**
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Use app password, not regular password
```

#### Email Authentication

**SPF, DKIM, DMARC:**
```dns
; SPF Record
yourdomain.com. IN TXT "v=spf1 include:_spf.google.com ~all"

; DKIM Record
default._domainkey.yourdomain.com. IN TXT "v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC..."

; DMARC Record
_dmarc.yourdomain.com. IN TXT "v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com"
```

### Email Content Security

#### Email Template Security

**Safe Email Templates:**
```html
<!-- Safe email template -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Appointment Confirmation</title>
</head>
<body>
    <h1>Appointment Confirmed</h1>
    <p>Dear {{ user.first_name|escape }},</p>
    <p>Your appointment with Dr. {{ doctor.name|escape }} is confirmed for {{ appointment.date|date:"F j, Y" }} at {{ appointment.time|time:"g:i A" }}.</p>
    <p>Thank you for using our booking system.</p>
</body>
</html>
```

#### Email Validation

**Email Security Validation:**
```python
# email_validation.py
import re
from django.core.validators import EmailValidator

class SecureEmailValidator:
    def __init__(self):
        self.validator = EmailValidator()
    
    def validate_email(self, email):
        # Basic email validation
        self.validator(email)
        
        # Check for suspicious patterns
        if self.is_suspicious_email(email):
            raise ValidationError("Suspicious email address")
        
        return email
    
    def is_suspicious_email(self, email):
        suspicious_patterns = [
            r'\.{2,}',  # Multiple consecutive dots
            r'@.*@',    # Multiple @ symbols
            r'\.@',     # Dot before @
            r'@\.',     # Dot after @
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, email):
                return True
        
        return False
```

## Payment Security

### PCI DSS Compliance

#### Payment Data Handling

**Secure Payment Processing:**
```python
# payment_security.py
import stripe
from django.conf import settings

class SecurePaymentProcessor:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
    
    def process_payment(self, amount, token):
        try:
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=amount * 100,  # Convert to cents
                currency='usd',
                payment_method=token,
                confirmation_method='manual',
                confirm=True
            )
            
            return intent
        except stripe.error.CardError as e:
            # Handle card errors
            raise PaymentError(f"Card error: {e.user_message}")
        except stripe.error.StripeError as e:
            # Handle other Stripe errors
            raise PaymentError(f"Stripe error: {str(e)}")
```

#### Tokenization

**Payment Tokenization:**
```python
# tokenization.py
class PaymentTokenization:
    def tokenize_card(self, card_data):
        # Never store card data directly
        # Use tokenization service
        token = self.create_token(card_data)
        return token
    
    def create_token(self, card_data):
        # Use secure tokenization
        # This is a simplified example
        import hashlib
        import time
        
        # Create secure token
        token_data = f"{card_data['number']}{card_data['expiry']}{time.time()}"
        token = hashlib.sha256(token_data.encode()).hexdigest()
        
        return token
```

### Fraud Detection

#### Fraud Prevention

**Fraud Detection System:**
```python
# fraud_detection.py
class FraudDetection:
    def __init__(self):
        self.suspicious_patterns = [
            'multiple_failed_attempts',
            'unusual_location',
            'high_value_transaction',
            'rapid_successive_transactions'
        ]
    
    def analyze_transaction(self, transaction):
        risk_score = 0
        
        # Check for suspicious patterns
        if self.multiple_failed_attempts(transaction):
            risk_score += 30
        
        if self.unusual_location(transaction):
            risk_score += 20
        
        if self.high_value_transaction(transaction):
            risk_score += 25
        
        if self.rapid_successive_transactions(transaction):
            risk_score += 35
        
        return risk_score
    
    def should_block_transaction(self, risk_score):
        return risk_score > 70
```

## Infrastructure Security

### Server Hardening

#### System Security

**Server Hardening Script:**
```bash
#!/bin/bash

# Update system
apt update && apt upgrade -y

# Install security tools
apt install -y fail2ban ufw unattended-upgrades

# Configure automatic updates
echo 'Unattended-Upgrade::Automatic-Reboot "true";' >> /etc/apt/apt.conf.d/50unattended-upgrades

# Configure fail2ban
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3
EOF

# Start fail2ban
systemctl enable fail2ban
systemctl start fail2ban

# Configure UFW
ufw enable
ufw allow ssh
ufw allow 80
ufw allow 443
```

#### File System Security

**File Permissions:**
```bash
# Set secure file permissions
chmod 600 /etc/ssh/sshd_config
chmod 600 /etc/postgresql/*/main/postgresql.conf
chmod 600 /etc/nginx/nginx.conf

# Set directory permissions
chmod 755 /var/www/booking-system
chmod 755 /var/www/booking-system/static
chmod 755 /var/www/booking-system/media

# Set ownership
chown -R www-data:www-data /var/www/booking-system
chown -R postgres:postgres /var/lib/postgresql
```

### Container Security

#### Docker Security

**Secure Dockerfile:**
```dockerfile
FROM python:3.10-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Run application
CMD ["gunicorn", "booking_system.wsgi:application", "--bind", "0.0.0.0:8000"]
```

**Docker Security Configuration:**
```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    user: "1000:1000"  # Non-root user
    read_only: true
    tmpfs:
      - /tmp
      - /var/run
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
    networks:
      - app-network
```

## Compliance and Privacy

### GDPR Compliance

#### Data Protection

**GDPR Implementation:**
```python
# gdpr_compliance.py
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()

class GDPRCompliance:
    def export_user_data(self, user):
        """Export all user data for GDPR compliance"""
        data = {
            'personal_info': {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number': user.phone_number,
            },
            'appointments': list(user.patient_appointments.values()),
            'reviews': list(user.reviews_given.values()),
            'transactions': list(user.wallettransaction_set.values()),
        }
        return data
    
    def delete_user_data(self, user):
        """Delete all user data for GDPR compliance"""
        # Anonymize instead of delete for legal requirements
        user.email = f"deleted_{user.id}@example.com"
        user.first_name = "Deleted"
        user.last_name = "User"
        user.phone_number = ""
        user.is_active = False
        user.save()
        
        # Delete related data
        user.patient_appointments.all().delete()
        user.reviews_given.all().delete()
        user.wallettransaction_set.all().delete()
    
    def send_data_export(self, user):
        """Send user data export via email"""
        data = self.export_user_data(user)
        
        # Create export file
        import json
        export_data = json.dumps(data, indent=2)
        
        # Send email with data
        send_mail(
            'Your Data Export',
            'Please find your data export attached.',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
            html_message=f'<pre>{export_data}</pre>'
        )
```

#### Privacy Controls

**Privacy Settings:**
```python
# privacy_controls.py
class PrivacyControls:
    def update_privacy_settings(self, user, settings):
        """Update user privacy settings"""
        user.privacy_settings = {
            'email_notifications': settings.get('email_notifications', True),
            'sms_notifications': settings.get('sms_notifications', False),
            'data_sharing': settings.get('data_sharing', False),
            'marketing_emails': settings.get('marketing_emails', False),
        }
        user.save()
    
    def check_data_sharing_consent(self, user):
        """Check if user has consented to data sharing"""
        return user.privacy_settings.get('data_sharing', False)
```

### HIPAA Compliance

#### Healthcare Data Protection

**HIPAA Implementation:**
```python
# hipaa_compliance.py
class HIPAACompliance:
    def __init__(self):
        self.phi_fields = ['ssn', 'medical_record_number', 'diagnosis']
    
    def protect_phi(self, data):
        """Protect Protected Health Information"""
        protected_data = data.copy()
        
        for field in self.phi_fields:
            if field in protected_data:
                protected_data[field] = self.encrypt_phi(protected_data[field])
        
        return protected_data
    
    def encrypt_phi(self, phi_value):
        """Encrypt PHI data"""
        from cryptography.fernet import Fernet
        key = Fernet.generate_key()
        cipher = Fernet(key)
        return cipher.encrypt(phi_value.encode())
    
    def audit_access(self, user, data_type, action):
        """Audit access to PHI data"""
        audit_log = {
            'user_id': user.id,
            'data_type': data_type,
            'action': action,
            'timestamp': timezone.now(),
            'ip_address': self.get_client_ip(),
        }
        
        # Store audit log
        AuditLog.objects.create(**audit_log)
```

## Security Monitoring

### Logging and Monitoring

#### Security Logging

**Security Event Logging:**
```python
# security_logging.py
import logging
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

logger = logging.getLogger('security')

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    logger.info(f"User {user.email} logged in from {request.META.get('REMOTE_ADDR')}")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    logger.info(f"User {user.email} logged out from {request.META.get('REMOTE_ADDR')}")

class SecurityLogger:
    def log_failed_login(self, email, ip_address):
        logger.warning(f"Failed login attempt for {email} from {ip_address}")
    
    def log_suspicious_activity(self, user, activity, ip_address):
        logger.error(f"Suspicious activity: {activity} by user {user.email} from {ip_address}")
    
    def log_data_access(self, user, data_type, action):
        logger.info(f"Data access: {action} on {data_type} by user {user.email}")
```

#### Intrusion Detection

**Intrusion Detection System:**
```python
# intrusion_detection.py
class IntrusionDetection:
    def __init__(self):
        self.suspicious_patterns = [
            'multiple_failed_logins',
            'unusual_access_patterns',
            'suspicious_file_access',
            'privilege_escalation_attempts'
        ]
    
    def detect_intrusion(self, request, user):
        """Detect potential intrusion attempts"""
        if self.multiple_failed_logins(user):
            self.alert_security_team(user, 'Multiple failed logins')
        
        if self.unusual_access_patterns(request, user):
            self.alert_security_team(user, 'Unusual access patterns')
        
        if self.suspicious_file_access(request):
            self.alert_security_team(user, 'Suspicious file access')
    
    def alert_security_team(self, user, reason):
        """Alert security team of potential intrusion"""
        # Send alert to security team
        send_mail(
            'Security Alert',
            f'Potential intrusion detected: {reason} for user {user.email}',
            'security@yourdomain.com',
            ['security@yourdomain.com'],
            fail_silently=False
        )
```

### Security Metrics

#### Security Dashboard

**Security Metrics:**
```python
# security_metrics.py
class SecurityMetrics:
    def get_security_metrics(self):
        """Get security metrics for dashboard"""
        return {
            'failed_logins_24h': self.get_failed_logins_24h(),
            'suspicious_activities_24h': self.get_suspicious_activities_24h(),
            'data_access_24h': self.get_data_access_24h(),
            'security_alerts_24h': self.get_security_alerts_24h(),
        }
    
    def get_failed_logins_24h(self):
        """Get failed login attempts in last 24 hours"""
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff = timezone.now() - timedelta(hours=24)
        return SecurityLog.objects.filter(
            event_type='failed_login',
            timestamp__gte=cutoff
        ).count()
```

## Incident Response

### Security Incident Response

#### Incident Response Plan

**Incident Response Procedure:**
```python
# incident_response.py
class IncidentResponse:
    def __init__(self):
        self.severity_levels = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
    
    def handle_security_incident(self, incident_type, severity, details):
        """Handle security incident"""
        if severity == 'critical':
            self.emergency_response(incident_type, details)
        elif severity == 'high':
            self.immediate_response(incident_type, details)
        else:
            self.standard_response(incident_type, details)
    
    def emergency_response(self, incident_type, details):
        """Emergency response for critical incidents"""
        # Immediate actions
        self.isolate_affected_systems()
        self.notify_security_team()
        self.activate_incident_response_team()
        
        # Document incident
        self.document_incident(incident_type, 'critical', details)
    
    def isolate_affected_systems(self):
        """Isolate affected systems"""
        # Implement system isolation
        pass
    
    def notify_security_team(self):
        """Notify security team"""
        # Send emergency notification
        pass
```

#### Incident Documentation

**Incident Documentation:**
```python
# incident_documentation.py
class IncidentDocumentation:
    def document_incident(self, incident_type, severity, details):
        """Document security incident"""
        incident = SecurityIncident.objects.create(
            incident_type=incident_type,
            severity=severity,
            details=details,
            timestamp=timezone.now(),
            status='open'
        )
        
        # Create incident log
        self.create_incident_log(incident)
        
        return incident
    
    def create_incident_log(self, incident):
        """Create incident log entry"""
        log_entry = IncidentLog.objects.create(
            incident=incident,
            action='incident_created',
            details=f'Incident {incident.id} created with severity {incident.severity}',
            timestamp=timezone.now()
        )
```

## Security Testing

### Vulnerability Assessment

#### Security Testing Tools

**Automated Security Testing:**
```bash
# Install security testing tools
pip install bandit safety django-security

# Run security tests
bandit -r . -f json -o security_report.json
safety check --json --output safety_report.json
python manage.py check --deploy
```

**Security Test Configuration:**
```python
# security_tests.py
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

class SecurityTestCase(TestCase):
    def test_sql_injection_protection(self):
        """Test SQL injection protection"""
        client = Client()
        
        # Attempt SQL injection
        response = client.get('/search/', {'q': "'; DROP TABLE users; --"})
        
        # Should not cause database error
        self.assertEqual(response.status_code, 200)
    
    def test_xss_protection(self):
        """Test XSS protection"""
        client = Client()
        
        # Attempt XSS
        response = client.get('/search/', {'q': '<script>alert("XSS")</script>'})
        
        # Should escape HTML
        self.assertNotIn('<script>', response.content.decode())
    
    def test_csrf_protection(self):
        """Test CSRF protection"""
        client = Client()
        
        # Attempt CSRF attack
        response = client.post('/appointments/book/', {
            'doctor_id': 1,
            'date': '2024-01-15',
            'time': '09:00:00'
        })
        
        # Should require CSRF token
        self.assertEqual(response.status_code, 403)
```

### Penetration Testing

#### Manual Security Testing

**Penetration Testing Checklist:**
```python
# penetration_testing.py
class PenetrationTesting:
    def __init__(self):
        self.test_cases = [
            'sql_injection',
            'xss_attacks',
            'csrf_attacks',
            'authentication_bypass',
            'privilege_escalation',
            'file_upload_vulnerabilities',
            'session_management',
            'input_validation'
        ]
    
    def run_security_tests(self):
        """Run comprehensive security tests"""
        results = {}
        
        for test_case in self.test_cases:
            results[test_case] = self.run_test(test_case)
        
        return results
    
    def run_test(self, test_case):
        """Run individual security test"""
        if test_case == 'sql_injection':
            return self.test_sql_injection()
        elif test_case == 'xss_attacks':
            return self.test_xss_attacks()
        # Add more test cases
```

## Security Checklist

### Pre-Deployment Security Checklist

**Security Checklist:**
```markdown
## Pre-Deployment Security Checklist

### Authentication & Authorization
- [ ] Strong password policy implemented
- [ ] Multi-factor authentication enabled
- [ ] Session security configured
- [ ] User permissions properly set
- [ ] OAuth security implemented

### Data Protection
- [ ] Data encryption at rest
- [ ] Data encryption in transit
- [ ] PII data protection
- [ ] Data retention policy
- [ ] Data anonymization

### Application Security
- [ ] Input validation implemented
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF protection
- [ ] Content Security Policy

### Network Security
- [ ] Firewall configured
- [ ] VPN access secured
- [ ] SSH hardening
- [ ] Network segmentation
- [ ] DDoS protection

### Infrastructure Security
- [ ] Server hardening
- [ ] Container security
- [ ] File system permissions
- [ ] Service isolation
- [ ] Backup security

### Monitoring & Logging
- [ ] Security logging enabled
- [ ] Intrusion detection
- [ ] Security monitoring
- [ ] Incident response plan
- [ ] Security metrics

### Compliance
- [ ] GDPR compliance
- [ ] HIPAA compliance (if applicable)
- [ ] Privacy controls
- [ ] Data subject rights
- [ ] Audit trails

### Testing
- [ ] Security testing completed
- [ ] Vulnerability assessment
- [ ] Penetration testing
- [ ] Code security review
- [ ] Security documentation
```

### Ongoing Security Maintenance

**Security Maintenance Checklist:**
```markdown
## Ongoing Security Maintenance

### Daily
- [ ] Review security logs
- [ ] Check for failed login attempts
- [ ] Monitor system performance
- [ ] Verify backup integrity

### Weekly
- [ ] Review user access
- [ ] Check for suspicious activity
- [ ] Update security patches
- [ ] Review firewall rules

### Monthly
- [ ] Security audit
- [ ] User permission review
- [ ] Vulnerability scan
- [ ] Security training

### Quarterly
- [ ] Penetration testing
- [ ] Security policy review
- [ ] Incident response drill
- [ ] Security documentation update
```

This security guide provides comprehensive security measures for the Booking System. Regular security reviews and updates are essential to maintain a secure system. Always consult with security professionals for specific security requirements and compliance needs.
