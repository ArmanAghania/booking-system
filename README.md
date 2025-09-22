# 🏥 Booking System - Complete Medical Appointment Platform

A comprehensive Django-based medical appointment booking system with advanced features including user authentication, appointment management, payment processing, and email notifications.

## 📋 Table of Contents

- [Features Overview](#-features-overview)
- [Quick Start](#-quick-start)
- [Docker Setup](#-docker-setup)
- [User Types & Authentication](#-user-types--authentication)
- [Core Features](#-core-features)
- [API Documentation](#-api-documentation)
- [Development Guide](#-development-guide)
- [Deployment](#-deployment)
- [Documentation](#-documentation)
- [Contributing](#-contributing)

## 🚀 Features Overview

### 🔐 **Authentication & User Management**
- **Multi-role authentication** (Admin, Doctor, Patient)
- **Email verification** with OTP system
- **Password reset** functionality
- **Google OAuth integration** (optional)
- **Social login** support
- **Session management** with remember me

### 👨‍⚕️ **Doctor Management**
- **Doctor profiles** with specialties
- **Time slot management** (availability, scheduling)
- **Consultation fee** configuration
- **Doctor search** and filtering
- **Specialty-based** categorization

### 📅 **Appointment System**
- **Calendar-based booking** interface
- **Real-time availability** checking
- **Appointment status** management (Pending, Confirmed, Cancelled, Completed)
- **Email notifications** for all appointment events
- **Conflict prevention** and validation
- **Admin oversight** of all appointments

### 💳 **Payment Processing**
- **Wallet system** for patients
- **Multiple payment methods** (Wallet, Card simulation)
- **Transaction history** tracking
- **Payment confirmation** emails
- **Refund handling**

### ⭐ **Review System**
- **Patient reviews** for completed appointments
- **Rating system** (1-5 stars)
- **Review moderation** capabilities

### 📧 **Email Notifications**
- **Appointment confirmations**
- **Payment confirmations**
- **Cancellation notifications**
- **OTP verification** emails
- **Password reset** emails

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 15+
- Docker & Docker Compose (optional)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd booking-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your database and email settings
   ```

5. **Database setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py create_sample_data
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main app: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## 🐳 Docker Setup

### Quick Docker Start
```bash
# Start with sample data
docker compose --env-file docker.env up --build

# Access the application
# Main app: http://localhost:8000
# Admin: admin/admin123
```

### Docker Commands
```bash
# Development mode
docker compose --env-file docker.env up

# Production mode (update docker.env first)
WEB_COMMAND=gunicorn booking_system.wsgi:application --bind 0.0.0.0:8000 --workers 3
docker compose --env-file docker.env up

# Stop containers
docker compose down

# View logs
docker compose logs -f
```

For detailed Docker setup, see [DOCKER_README.md](DOCKER_README.md)

## 👥 User Types & Authentication

### 🔑 **User Roles**

#### **Admin Users**
- **Full system access** and management
- **View all appointments** across the system
- **User management** capabilities
- **System configuration** access
- **Django admin** panel access

#### **Doctor Users**
- **Profile management** and time slot creation
- **Appointment management** for their patients
- **Patient interaction** and consultation notes
- **Schedule optimization** tools

#### **Patient Users**
- **Appointment booking** and management
- **Payment processing** and wallet management
- **Review submission** for completed appointments
- **Profile management** and preferences

### 🔐 **Authentication Features**

#### **Login System**
- **Username/Email** login support
- **Remember me** functionality
- **Session management** with configurable expiry
- **Redirect handling** based on user type

#### **Registration Process**
- **Email verification** required
- **OTP-based** verification system
- **Profile completion** workflow
- **User type** selection during registration

#### **Password Management**
- **Secure password** requirements
- **Password reset** via OTP
- **Password change** functionality
- **Account security** features

#### **Social Authentication**
- **Google OAuth** integration
- **Social account** linking
- **Mock Google login** for development
- **Account merging** capabilities

## 🎯 Core Features

### 📅 **Appointment Booking System**

#### **Calendar Interface**
- **Interactive calendar** for date selection
- **Time slot visualization** with availability
- **Real-time updates** and conflict prevention
- **Mobile-responsive** design

#### **Booking Process**
1. **Doctor selection** from specialty or search
2. **Date and time** selection from available slots
3. **Appointment details** and notes
4. **Payment processing** (wallet or card)
5. **Confirmation** and email notification

#### **Appointment Management**
- **Status tracking** (Pending → Confirmed → Completed)
- **Cancellation** with email notifications
- **Rescheduling** capabilities
- **Admin oversight** and management

### 💰 **Payment System**

#### **Wallet Functionality**
- **Balance management** and transactions
- **Deposit/Withdrawal** capabilities
- **Transaction history** and reporting
- **Payment method** preferences

#### **Payment Processing**
- **Multiple payment** methods support
- **Secure transaction** handling
- **Payment confirmation** emails
- **Refund processing** capabilities

#### **Financial Features**
- **Consultation fee** management
- **Payment tracking** and reporting
- **Revenue analytics** for doctors
- **Transaction auditing**

### ⭐ **Review & Rating System**

#### **Patient Reviews**
- **Star rating** system (1-5 stars)
- **Written feedback** and comments
- **Review moderation** and approval
- **Doctor response** capabilities

#### **Review Management**
- **Review aggregation** and statistics
- **Quality control** and moderation
- **Review analytics** and insights
- **Patient satisfaction** tracking

### 📧 **Email Notification System**

#### **Automated Notifications**
- **Appointment confirmations** with details
- **Payment confirmations** and receipts
- **Cancellation notifications** with reasons
- **Reminder emails** for upcoming appointments

#### **Email Features**
- **HTML email** templates
- **Email logging** and tracking
- **Delivery confirmation** system
- **Email preferences** management

## 🔧 API Documentation

### **Authentication Endpoints**
- `POST /accounts/login/` - User login
- `POST /accounts/logout/` - User logout
- `POST /accounts/register/` - User registration
- `GET /accounts/profile/` - User profile

### **Appointment Endpoints**
- `GET /appointments/` - List appointments
- `POST /appointments/reserve/<slot_id>/` - Book appointment
- `GET /appointments/book/<doctor_id>/` - Booking interface
- `GET /appointments/calendar/<doctor_id>/` - Calendar view

### **Payment Endpoints**
- `GET /payments/wallet/` - Wallet details
- `POST /payments/deposit/` - Add funds
- `POST /payments/process/<appointment_id>/` - Process payment

### **Doctor Endpoints**
- `GET /doctors/` - List doctors
- `GET /doctors/<id>/` - Doctor details
- `GET /doctors/specialties/` - List specialties

## 🛠️ Development Guide

### **Project Structure**
```
booking-system/
├── accounts/           # User authentication & management
├── appointments/       # Appointment booking system
├── doctors/           # Doctor profiles & management
├── payments/          # Payment processing
├── reviews/           # Review & rating system
├── notifications/     # Email notification system
├── core/             # Core functionality & commands
├── templates/        # HTML templates
├── static/           # Static files (CSS, JS, images)
└── documents/        # Project documentation
```

### **Database Models**

#### **User Management**
- `User` - Extended user model with roles
- `UserProfile` - Additional user information
- `OTPVerification` - Email verification system

#### **Appointment System**
- `TimeSlot` - Doctor availability slots
- `Appointment` - Patient appointments
- `Specialty` - Medical specialties

#### **Payment System**
- `Wallet` - User wallet balances
- `Payment` - Payment transactions
- `WalletTransaction` - Wallet activity

#### **Review System**
- `Review` - Patient reviews and ratings

### **Key Services**

#### **Authentication Services**
- `OTPService` - Email verification handling
- `CustomAccountAdapter` - Social authentication
- `EmailVerificationMixin` - Email verification

#### **Appointment Services**
- `AppointmentEmailService` - Email notifications
- `TimeSlotValidation` - Conflict prevention
- `AppointmentManagement` - Status tracking

#### **Payment Services**
- `PaymentProcessor` - Transaction handling
- `WalletManager` - Balance management
- `TransactionLogger` - Audit trail

### **Development Commands**
```bash
# Create sample data
python manage.py create_sample_data

# Run tests
python manage.py test

# Collect static files
python manage.py collectstatic

# Database migrations
python manage.py makemigrations
python manage.py migrate
```

## 🚀 Deployment

### **Production Setup**

#### **Environment Configuration**
```bash
# Production environment variables
DEBUG=False
SECRET_KEY=your-secure-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@host:port/database
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

#### **Web Server Configuration**
- **Gunicorn** for WSGI serving
- **Nginx** for reverse proxy (optional)
- **PostgreSQL** for database
- **Redis** for caching (optional)

#### **Docker Production**
```bash
# Update docker.env for production
DEBUG=False
WEB_COMMAND=gunicorn booking_system.wsgi:application --bind 0.0.0.0:8000 --workers 3

# Deploy with Docker
docker compose --env-file docker.env up -d
```

### **Security Considerations**
- **HTTPS** enforcement
- **CSRF protection** enabled
- **XSS protection** implemented
- **SQL injection** prevention
- **Secure headers** configuration
- **Rate limiting** for API endpoints

## 📚 Documentation

### **Core Documentation**
- [API Documentation](documents/API_DOCUMENTATION.md) - Complete API reference with endpoints
- [Database Schema](documents/DATABASE_SCHEMA.md) - Database models and relationships
- [Deployment Guide](documents/DEPLOYMENT_GUIDE.md) - Production deployment instructions
- [Development Setup](documents/DEVELOPMENT_SETUP.md) - Local development environment
- [User Guide](documents/USER_GUIDE.md) - Step-by-step user instructions
- [Troubleshooting Guide](documents/TROUBLESHOOTING_GUIDE.md) - Common issues and solutions
- [Security Guide](documents/SECURITY_GUIDE.md) - Security best practices and implementation

### **Project Documentation**
- [Docker Setup Guide](DOCKER_README.md) - Complete Docker configuration
- [Project Specifications](documents/Project%20Specifications.pdf) - Detailed requirements
- [Project Backlog](documents/project_backlog.md) - Feature tracking
- [Git Flow Guide](documents/git_flow_guide.md) - Development workflow

### **Technical Documentation**
- [Google OAuth Setup](documents/GOOGLE_OAUTH_SETUP.md) - OAuth configuration
- [OAuth Implementation](documents/oauth_implementation_guide.md) - Social auth details
- [Email Configuration](documents/email_config_example.txt) - Email setup
- [Database ERD](documents/erd_diagram.mermaid) - Database schema

### **Quick Reference**
- **API Endpoints** - [API Documentation](documents/API_DOCUMENTATION.md)
- **Database Models** - [Database Schema](documents/DATABASE_SCHEMA.md)
- **Deployment** - [Deployment Guide](documents/DEPLOYMENT_GUIDE.md)
- **Development** - [Development Setup](documents/DEVELOPMENT_SETUP.md)
- **User Help** - [User Guide](documents/USER_GUIDE.md)
- **Issues** - [Troubleshooting Guide](documents/TROUBLESHOOTING_GUIDE.md)
- **Security** - [Security Guide](documents/SECURITY_GUIDE.md)

## 🎯 Demo Scenarios

### **For Patients**
1. **Browse doctors** by specialty
2. **Book appointments** using calendar interface
3. **Process payments** via wallet or card
4. **Leave reviews** for completed appointments
5. **Manage profile** and preferences

### **For Doctors**
1. **Set up profile** and specialties
2. **Manage time slots** and availability
3. **View appointments** and patient details
4. **Update consultation** fees
5. **Respond to reviews** and feedback

### **For Admins**
1. **Oversee all appointments** system-wide
2. **Manage users** and permissions
3. **Monitor payments** and transactions
4. **Moderate reviews** and content
5. **System configuration** and settings

## 🔧 Configuration

### **Email Configuration**
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

### **Database Configuration**
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'booking_system',
        'USER': 'booking_user',
        'PASSWORD': 'your-password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### **OAuth Configuration**
```python
# settings.py
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
    }
}
```

## 🧪 Testing

### **Test Coverage**
- **Unit tests** for models and services
- **Integration tests** for API endpoints
- **Authentication tests** for user flows
- **Payment tests** for transaction handling
- **Email tests** for notification system

### **Running Tests**
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test appointments

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 🤝 Contributing

### **Development Workflow**
1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Add** tests for new features
5. **Submit** a pull request

### **Code Standards**
- **PEP 8** compliance
- **Type hints** for functions
- **Docstrings** for classes and methods
- **Error handling** for edge cases
- **Security** best practices

### **Pull Request Process**
1. **Update** documentation
2. **Add** tests for new features
3. **Ensure** all tests pass
4. **Update** version numbers
5. **Submit** for review

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### **Getting Help**
- **Documentation** - Check this README and docs folder
- **Issues** - Create GitHub issues for bugs
- **Discussions** - Use GitHub discussions for questions
- **Email** - Contact the development team

### **Common Issues**
- **Database connection** - Check PostgreSQL service
- **Email sending** - Verify SMTP configuration
- **OAuth setup** - Check Google OAuth credentials
- **Docker issues** - Check container logs

## 🎉 Acknowledgments

- **Django** framework for the robust foundation
- **PostgreSQL** for reliable database management
- **Docker** for containerization
- **Tailwind CSS** for modern UI components
- **Font Awesome** for icons
- **Contributors** who helped build this system

---

**Built with ❤️ for better healthcare management**