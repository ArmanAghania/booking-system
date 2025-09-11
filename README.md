# Booking System

A Django-based medical appointment booking system with support for doctors, patients, appointments, payments, reviews, and notifications.

## Prerequisites

Before setting up the project, ensure you have the following installed on your system:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **PostgreSQL 12+** - [Download PostgreSQL](https://www.postgresql.org/download/)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **pip** (Python package installer)

## Project Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd booking-system
```

### 2. Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS (using Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
Download and install from [PostgreSQL official website](https://www.postgresql.org/download/windows/)

#### Create Database and User

1. **Access PostgreSQL:**
```bash
sudo -u postgres psql
```

2. **Create database and user:**
```sql
-- Create a new user (replace 'your_username' and 'your_password' with your preferred credentials)
CREATE USER your_username WITH PASSWORD 'your_password';

-- Create the database
CREATE DATABASE booking_system_db;

-- Grant privileges to the user
GRANT ALL PRIVILEGES ON DATABASE booking_system_db TO your_username;

-- Exit PostgreSQL
\q
```

### 5. Environment Configuration

Create a `.env` file in the project root directory:

```bash
touch .env
```

Add the following environment variables to the `.env` file:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=booking_system_db
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

**Important:** Replace the placeholder values with your actual database credentials and generate a secure secret key.

### 6. Run Database Migrations

```bash
# Create migration files
python manage.py makemigrations

# Apply migrations to create database tables
python manage.py migrate
```

### 7. Create Superuser (Optional)

Create an admin user to access the Django admin interface:

```bash
python manage.py createsuperuser
```

Follow the prompts to set up your admin credentials.

### 8. Run the Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Project Structure

```
booking-system/
├── accounts/           # User authentication and profiles
├── appointments/       # Appointment booking and management
├── booking_system/     # Main Django project settings
├── core/              # Core functionality and utilities
├── doctors/           # Doctor profiles and management
├── documents/         # Project documentation
├── notifications/     # Notification system
├── payments/          # Payment processing
├── reviews/           # Review and rating system
├── manage.py          # Django management script
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Available Apps

- **Accounts**: User registration, authentication, and profile management
- **Doctors**: Doctor profiles, specialties, and availability
- **Appointments**: Booking system, scheduling, and appointment management
- **Payments**: Payment processing and transaction handling
- **Reviews**: Patient reviews and ratings for doctors
- **Notifications**: Email and system notifications
- **Core**: Shared utilities and common functionality

## Development Commands

### Database Operations
```bash
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset migrations (use with caution)
python manage.py migrate --fake-initial
```

### Django Admin
```bash
# Access admin interface
# Navigate to: http://127.0.0.1:8000/admin/
```

### Testing
```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test accounts
```

### Static Files
```bash
# Collect static files (for production)
python manage.py collectstatic
```

## Troubleshooting

### Common Issues

1. **Database Connection Error:**
   - Verify PostgreSQL is running
   - Check database credentials in `.env` file
   - Ensure database exists and user has proper permissions

2. **Migration Errors:**
   - Delete migration files in `*/migrations/` (except `__init__.py`)
   - Run `python manage.py makemigrations` again
   - Apply migrations with `python manage.py migrate`

3. **Import Errors:**
   - Ensure virtual environment is activated
   - Verify all dependencies are installed: `pip install -r requirements.txt`

4. **Port Already in Use:**
   - Use a different port: `python manage.py runserver 8001`
   - Or kill the process using port 8000

### Environment Variables

Make sure all required environment variables are set in your `.env` file:

- `SECRET_KEY`: Django secret key (generate a new one for production)
- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: Add your domain in production
- `DB_NAME`: PostgreSQL database name
- `DB_USER`: PostgreSQL username
- `DB_PASSWORD`: PostgreSQL password
- `DB_HOST`: Database host (usually `localhost`)
- `DB_PORT`: Database port (usually `5432`)

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `python manage.py test`
5. Commit your changes: `git commit -m "Add feature"`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please contact the development team or create an issue in the repository.
