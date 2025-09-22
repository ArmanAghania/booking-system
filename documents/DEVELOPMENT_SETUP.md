# Development Setup Guide

## Overview

This guide provides comprehensive instructions for setting up the Booking System development environment. It covers local development, testing, debugging, and contribution workflows.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Development Environment Configuration](#development-environment-configuration)
4. [Database Setup](#database-setup)
5. [Testing Setup](#testing-setup)
6. [Development Tools](#development-tools)
7. [Code Quality Tools](#code-quality-tools)
8. [Debugging Setup](#debugging-setup)
9. [Git Workflow](#git-workflow)
10. [Contributing Guidelines](#contributing-guidelines)
11. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

**Minimum Requirements:**
- **OS**: Ubuntu 20.04+ / macOS 10.15+ / Windows 10+
- **Python**: 3.10+
- **Node.js**: 16+ (for frontend tools)
- **Git**: 2.30+
- **PostgreSQL**: 15+ (or Docker)

**Recommended Requirements:**
- **OS**: Ubuntu 22.04 LTS / macOS 12+ / Windows 11
- **Python**: 3.11+
- **RAM**: 8GB+
- **Storage**: 10GB+ free space

### Development Tools

**Essential Tools:**
- **IDE**: VS Code, PyCharm, or Vim/Emacs
- **Terminal**: iTerm2 (macOS), Windows Terminal, or default
- **Browser**: Chrome, Firefox, or Safari with dev tools
- **Database Client**: pgAdmin, DBeaver, or command line

**Optional Tools:**
- **Docker**: For containerized development
- **Redis**: For caching and sessions
- **Elasticsearch**: For advanced search (future)

## Local Development Setup

### 1. Clone Repository

```bash
# Clone the repository
git clone https://github.com/your-org/booking-system.git
cd booking-system

# Checkout development branch
git checkout develop
```

### 2. Python Environment Setup

**Using venv (Recommended):**
```bash
# Create virtual environment
python3.10 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

**Using conda (Alternative):**
```bash
# Create conda environment
conda create -n booking-system python=3.10
conda activate booking-system
```

### 3. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

**requirements-dev.txt:**
```txt
# Testing
pytest==7.4.0
pytest-django==4.5.2
pytest-cov==4.1.0
factory-boy==3.2.1

# Code Quality
black==23.7.0
flake8==6.0.0
isort==5.12.0
mypy==1.5.1

# Development Tools
django-debug-toolbar==4.2.0
django-extensions==3.2.3
ipython==8.14.0

# Documentation
sphinx==7.1.2
sphinx-rtd-theme==1.3.0
```

### 4. Environment Configuration

**Create .env file:**
```bash
# Copy environment template
cp .env.example .env
```

**.env file:**
```bash
# Django Settings
DEBUG=True
SECRET_KEY=your-development-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE_URL=postgresql://booking_user:password@localhost:5432/booking_system_dev

# Email Configuration (Development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=test@example.com

# OAuth Configuration (Optional)
GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=DEBUG
```

## Development Environment Configuration

### Django Settings

**settings/development.py:**
```python
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'booking_system_dev',
        'USER': 'booking_user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Debug toolbar
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1', 'localhost']

# Logging for development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'booking_system': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Environment Variables

**Load environment variables:**
```python
# settings/base.py
import os
from decouple import config

# Load environment variables
DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')
DATABASE_URL = config('DATABASE_URL')
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
```

## Database Setup

### PostgreSQL Installation

**Ubuntu/Debian:**
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS:**
```bash
# Using Homebrew
brew install postgresql
brew services start postgresql
```

**Windows:**
- Download and install from https://www.postgresql.org/download/windows/

### Database Configuration

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE booking_system_dev;
CREATE USER booking_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE booking_system_dev TO booking_user;
\q
```

### Database Migrations

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data
python manage.py create_sample_data
```

### Database Management

**Useful commands:**
```bash
# Reset database
python manage.py flush

# Show migrations
python manage.py showmigrations

# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check database connection
python manage.py dbshell
```

## Testing Setup

### Test Configuration

**pytest.ini:**
```ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = booking_system.settings.test
python_files = tests.py test_*.py *_tests.py
addopts = --tb=short --strict-markers --disable-warnings
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

**settings/test.py:**
```python
from .base import *

# Test database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'booking_system_test',
        'USER': 'booking_user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Test email backend
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable logging during tests
LOGGING_CONFIG = None
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific app tests
pytest accounts/
pytest appointments/

# Run with coverage
pytest --cov=booking_system --cov-report=html

# Run specific test
pytest tests/test_models.py::TestUserModel::test_user_creation

# Run tests in parallel
pytest -n auto
```

### Test Data Factories

**factories.py:**
```python
import factory
from django.contrib.auth import get_user_model
from accounts.models import User
from doctors.models import Doctor, Specialty
from appointments.models import Appointment, TimeSlot

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    user_type = 'patient'
    phone_number = factory.Faker('phone_number')

class SpecialtyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Specialty
    
    name = factory.Faker('job')
    description = factory.Faker('text', max_nb_chars=200)

class DoctorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Doctor
    
    user = factory.SubFactory(UserFactory, user_type='doctor')
    specialty = factory.SubFactory(SpecialtyFactory)
    license_number = factory.Faker('numerify', text='MD######')
    experience_years = factory.Faker('random_int', min=1, max=30)
    bio = factory.Faker('text', max_nb_chars=500)
    consultation_fee = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
```

## Development Tools

### Django Debug Toolbar

**Installation:**
```bash
pip install django-debug-toolbar
```

**Configuration:**
```python
# settings/development.py
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1', 'localhost']
    
    # Debug toolbar configuration
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TEMPLATE_CONTEXT': True,
        'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
    }
```

### Django Extensions

**Installation:**
```bash
pip install django-extensions
```

**Useful commands:**
```bash
# Show URL patterns
python manage.py show_urls

# Create a new app
python manage.py startapp myapp

# Run shell with IPython
python manage.py shell_plus

# Show model information
python manage.py graph_models -a -o models.png
```

### IPython and Jupyter

**Installation:**
```bash
pip install ipython jupyter
```

**Jupyter configuration:**
```python
# settings/development.py
INSTALLED_APPS += ['django_extensions']

# Jupyter notebook configuration
NOTEBOOK_ARGUMENTS = [
    '--ip=0.0.0.0',
    '--port=8888',
    '--no-browser',
    '--allow-root'
]
```

## Code Quality Tools

### Black (Code Formatter)

**Installation:**
```bash
pip install black
```

**Configuration (.black):**
```toml
[tool.black]
line-length = 88
target-version = ['py310']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''
```

**Usage:**
```bash
# Format all Python files
black .

# Check formatting
black --check .

# Format specific file
black myfile.py
```

### Flake8 (Linter)

**Installation:**
```bash
pip install flake8
```

**Configuration (.flake8):**
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    .venv,
    venv,
    migrations,
    settings
```

**Usage:**
```bash
# Lint all Python files
flake8 .

# Lint specific file
flake8 myfile.py
```

### isort (Import Sorter)

**Installation:**
```bash
pip install isort
```

**Configuration (.isort.cfg):**
```ini
[settings]
profile = black
multi_line_output = 3
line_length = 88
known_django = django
known_first_party = booking_system
sections = FUTURE,STDLIB,DJANGO,THIRDPARTY,FIRSTPARTY,LOCALFOLDER
```

**Usage:**
```bash
# Sort imports
isort .

# Check import sorting
isort --check-only .
```

### MyPy (Type Checker)

**Installation:**
```bash
pip install mypy django-stubs
```

**Configuration (mypy.ini):**
```ini
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_optional = True

[mypy-django.*]
ignore_missing_imports = True
```

**Usage:**
```bash
# Type check all files
mypy .

# Type check specific file
mypy myfile.py
```

### Pre-commit Hooks

**Installation:**
```bash
pip install pre-commit
```

**Configuration (.pre-commit-config.yaml):**
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [django-stubs]
```

**Setup:**
```bash
# Install pre-commit hooks
pre-commit install

# Run hooks on all files
pre-commit run --all-files
```

## Debugging Setup

### VS Code Configuration

**.vscode/settings.json:**
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/migrations": false
    },
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "."
    ],
    "python.testing.unittestEnabled": false
}
```

**.vscode/launch.json:**
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Django: Debug Server",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/manage.py",
            "args": ["runserver", "0.0.0.0:8000"],
            "django": true,
            "justMyCode": false,
            "env": {
                "DJANGO_SETTINGS_MODULE": "booking_system.settings.development"
            }
        },
        {
            "name": "Django: Debug Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["-v"],
            "django": true,
            "justMyCode": false
        }
    ]
}
```

### PyCharm Configuration

**Run Configuration:**
- **Script path**: `manage.py`
- **Parameters**: `runserver 0.0.0.0:8000`
- **Environment variables**: `DJANGO_SETTINGS_MODULE=booking_system.settings.development`

**Test Configuration:**
- **Test runner**: pytest
- **Working directory**: Project root
- **Environment variables**: `DJANGO_SETTINGS_MODULE=booking_system.settings.test`

### Debugging Tools

**Django Debug Toolbar:**
```python
# Add to templates for debugging
{% load debug_toolbar %}
{% debug_toolbar %}
```

**Logging configuration:**
```python
# settings/development.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'booking_system': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

## Git Workflow

### Branch Strategy

**Main branches:**
- `main`: Production-ready code
- `develop`: Integration branch for features

**Feature branches:**
- `feature/feature-name`: New features
- `bugfix/bug-name`: Bug fixes
- `hotfix/hotfix-name`: Critical fixes

### Git Hooks

**.git/hooks/pre-commit:**
```bash
#!/bin/sh
# Run code quality checks before commit

echo "Running code quality checks..."

# Run black
black --check .
if [ $? -ne 0 ]; then
    echo "Black formatting failed. Run 'black .' to fix."
    exit 1
fi

# Run flake8
flake8 .
if [ $? -ne 0 ]; then
    echo "Flake8 linting failed. Fix the issues above."
    exit 1
fi

# Run isort
isort --check-only .
if [ $? -ne 0 ]; then
    echo "Import sorting failed. Run 'isort .' to fix."
    exit 1
fi

echo "All checks passed!"
```

### Commit Message Convention

**Format:**
```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build process or auxiliary tool changes

**Examples:**
```
feat(auth): add OAuth2 login support
fix(payments): resolve currency conversion bug
docs(readme): update installation instructions
refactor(api): simplify appointment booking logic
```

## Contributing Guidelines

### Development Process

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Write tests**
5. **Run quality checks**
6. **Submit a pull request**

### Code Standards

**Python:**
- Follow PEP 8 style guide
- Use type hints for functions
- Write docstrings for classes and methods
- Keep functions small and focused
- Use meaningful variable names

**Django:**
- Follow Django best practices
- Use Django's built-in features
- Write model methods for business logic
- Use Django's ORM efficiently
- Follow Django's naming conventions

**Testing:**
- Write unit tests for models
- Write integration tests for views
- Test edge cases and error conditions
- Aim for high test coverage
- Use factories for test data

### Pull Request Process

**Before submitting:**
1. **Run tests**: `pytest`
2. **Check formatting**: `black .`
3. **Check linting**: `flake8 .`
4. **Check imports**: `isort .`
5. **Check types**: `mypy .`

**Pull request template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Manual testing completed
- [ ] New tests added for new functionality

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues

**Symptoms**: `django.db.utils.OperationalError: could not connect to server`
**Solutions**:
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Check database exists
psql -h localhost -U booking_user -l

# Create database if missing
createdb -h localhost -U booking_user booking_system_dev
```

#### 2. Virtual Environment Issues

**Symptoms**: `ModuleNotFoundError: No module named 'django'`
**Solutions**:
```bash
# Check virtual environment
which python
which pip

# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 3. Migration Issues

**Symptoms**: `django.db.utils.ProgrammingError: relation does not exist`
**Solutions**:
```bash
# Reset migrations
python manage.py migrate --fake-initial

# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

#### 4. Static Files Issues

**Symptoms**: CSS/JS files return 404
**Solutions**:
```bash
# Collect static files
python manage.py collectstatic

# Check static files directory
ls -la static/

# Check settings
python manage.py diffsettings | grep STATIC
```

#### 5. Email Issues

**Symptoms**: Emails not sending
**Solutions**:
```bash
# Check email backend
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])

# Check console output for emails
# Emails should appear in console with console backend
```

### Performance Issues

#### 1. Slow Database Queries

**Solutions**:
```python
# Use select_related for foreign keys
doctors = Doctor.objects.select_related('user', 'specialty').all()

# Use prefetch_related for reverse relationships
appointments = Appointment.objects.prefetch_related('patient', 'doctor').all()

# Use database indexes
# Add indexes in models.py
class Meta:
    indexes = [
        models.Index(fields=['user_type']),
        models.Index(fields=['created_at']),
    ]
```

#### 2. Memory Issues

**Solutions**:
```bash
# Check memory usage
htop
free -h

# Use database connection pooling
# Add to settings.py
DATABASES['default']['OPTIONS'] = {
    'MAX_CONNS': 20,
}
```

### Debugging Tips

#### 1. Django Debug Toolbar

```python
# Add to templates
{% load debug_toolbar %}
{% debug_toolbar %}
```

#### 2. Logging

```python
import logging
logger = logging.getLogger(__name__)

def my_view(request):
    logger.debug('Processing request')
    logger.info('User authenticated')
    logger.warning('Deprecated function used')
    logger.error('Database connection failed')
```

#### 3. Database Queries

```python
# Enable query logging
from django.db import connection
from django.conf import settings

if settings.DEBUG:
    print(connection.queries)
```

#### 4. Shell Debugging

```bash
# Django shell
python manage.py shell

# IPython shell
python manage.py shell_plus

# Debug specific model
python manage.py shell
>>> from accounts.models import User
>>> User.objects.all()
>>> User.objects.filter(user_type='patient')
```

### Development Tips

#### 1. Use Django Extensions

```bash
# Show URL patterns
python manage.py show_urls

# Show model information
python manage.py graph_models -a -o models.png

# Run shell with IPython
python manage.py shell_plus
```

#### 2. Use Factory Boy for Tests

```python
# Create test data
user = UserFactory()
doctor = DoctorFactory()
appointment = AppointmentFactory(patient=user, doctor=doctor)
```

#### 3. Use Django Debug Toolbar

```python
# Add to INSTALLED_APPS
INSTALLED_APPS += ['debug_toolbar']

# Add to MIDDLEWARE
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

#### 4. Use Environment Variables

```python
# Use python-decouple
from decouple import config

DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')
DATABASE_URL = config('DATABASE_URL')
```

This development setup guide provides comprehensive instructions for setting up and working with the Booking System development environment. Follow the appropriate sections based on your development needs and preferences.
