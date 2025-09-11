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
git clone https://github.com/ArmanAghania/booking-system.git
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

## Git Flow Workflow

This project uses Git Flow for branch management and release coordination. Git Flow provides a robust framework for managing features, releases, and hotfixes.

> 📖 **For a comprehensive Git Flow guide, see [Git Flow Documentation](documents/git_flow_guide.md)**

### Quick Reference

- **`main`**: Production-ready code
- **`develop`**: Integration branch for features
- **`feature/*`**: New features and enhancements
- **`bugfix/*`**: Bug fixes for the develop branch
- **`release/*`**: Release preparation branches
- **`hotfix/*`**: Critical fixes for production

### Git Flow Commands

#### Starting a New Feature
```bash
# Start a new feature
git flow feature start feature-name

# This creates and switches to feature/feature-name branch
# Make your changes, commit them
git add .
git commit -m "Add new feature"

# Finish the feature (merges to develop and deletes feature branch)
git flow feature finish feature-name
```

#### Starting a Bug Fix
```bash
# Start a bug fix
git flow bugfix start bugfix-name

# Make your changes, commit them
git add .
git commit -m "Fix bug description"

# Finish the bug fix
git flow bugfix finish bugfix-name
```

#### Creating a Release
```bash
# Start a new release
git flow release start 1.0.0

# Make any final adjustments, update version numbers
# Finish the release (creates tag and merges to main and develop)
git flow release finish 1.0.0
```

#### Creating a Hotfix
```bash
# Start a hotfix for production
git flow hotfix start 1.0.1

# Make critical fixes, commit them
git add .
git commit -m "Critical fix description"

# Finish the hotfix (merges to main and develop, creates tag)
git flow hotfix finish 1.0.1
```

### Workflow for Contributors

#### Option 1: Direct Repository Access (Recommended for team members)

If you have direct push access to the repository:

1. **Clone the repository** locally:
   ```bash
   git clone https://github.com/ArmanAghania/booking-system.git
   cd booking-system
   ```

2. **Create a feature branch** using Git Flow:
   ```bash
   git flow feature start your-feature-name
   ```

3. **Make your changes** and commit them:
   ```bash
   git add .
   git commit -m "Add your feature description"
   ```

4. **Run tests** to ensure everything works:
   ```bash
   python manage.py test
   ```

5. **Push your feature branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub:
   - Go to the repository on GitHub
   - Click "Compare & pull request"
   - **Important**: Set base branch to `develop` (not `main`)
   - Provide a clear description of your changes

7. **After PR approval and merge**:
   - The feature branch will be automatically merged into `develop`
   - Clean up your local branches:
   ```bash
   git checkout develop
   git pull origin develop
   git branch -d feature/your-feature-name
   ```

#### Option 2: Fork-based Contribution (For external contributors)

If you don't have direct access and need to fork:

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/booking-system.git
   cd booking-system
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/ArmanAghania/booking-system.git
   ```

4. **Create a feature branch** using Git Flow:
   ```bash
   git flow feature start your-feature-name
   ```

5. **Make your changes** and commit them:
   ```bash
   git add .
   git commit -m "Add your feature description"
   ```

6. **Run tests** to ensure everything works:
   ```bash
   python manage.py test
   ```

7. **Push your feature branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request** on GitHub:
   - Go to your fork on GitHub
   - Click "Compare & pull request"
   - **Important**: Set base branch to `develop` (not `main`)
   - Provide a clear description of your changes

9. **After PR approval and merge**:
   - Update your fork and clean up:
   ```bash
   git checkout develop
   git pull upstream develop
   git push origin develop
   git branch -d feature/your-feature-name
   ```

### Branch Protection Rules

- **`main` branch**: Protected, requires PR reviews
- **`develop` branch**: Protected, requires PR reviews
- **All features must be merged into `develop` first**
- **Only release branches can merge into `main`**

### ⚠️ Important: Pull Request Target

**Always create pull requests targeting the `develop` branch, NOT `main`!**

- ✅ **Correct**: `feature/your-feature` → `develop`
- ❌ **Wrong**: `feature/your-feature` → `main`

The `main` branch is only updated through release branches or hotfixes.

### Version Tagging

Releases are tagged with version numbers (e.g., `v1.0.0`). Tags are automatically created when using:
- `git flow release finish`
- `git flow hotfix finish`

### Best Practices

1. **Always start from `develop`** when creating new features
2. **Keep feature branches small** and focused on single features
3. **Write descriptive commit messages**
4. **Run tests before pushing**
5. **Update documentation** if needed
6. **Follow the existing code style**
7. **Create meaningful branch names** that describe the feature/fix

### Getting Help

If you're new to Git Flow, check out:
- 📖 **[Project Git Flow Guide](documents/git_flow_guide.md)** - Comprehensive guide for this project
- [Git Flow Documentation](https://github.com/nvie/gitflow)
- [Atlassian Git Flow Tutorial](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please contact the development team or create an issue in the repository.
