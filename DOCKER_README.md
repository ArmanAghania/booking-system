# 🐳 Booking System - Docker Setup

This document explains how to run the Booking System using Docker.

## 🚀 Quick Start

### Prerequisites
- Docker
- Docker Compose

### Development Setup

1. **Clone and navigate to the project:**
   ```bash
   cd booking-system
   ```

2. **Start the application:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Main application: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

### Production Setup

1. **Update environment file for production:**
   ```bash
   # Edit docker.env with production values:
   # - Set DEBUG=False
   # - Change SECRET_KEY to a secure value
   # - Set WEB_COMMAND=gunicorn booking_system.wsgi:application --bind 0.0.0.0:8000 --workers 3
   ```

2. **Start production services:**
   ```bash
   docker-compose up -d
   ```

## 📋 Available Services

### Services
- **web**: Django application (port 8000)
- **db**: PostgreSQL database (port 5432)

## 🔧 Configuration

### Environment Variables

The application uses the following environment variables (defined in `docker.env`):

```bash
# Database
POSTGRES_DB=booking_system
POSTGRES_USER=booking_user
POSTGRES_PASSWORD=booking_password_2024

# Django
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,web

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@bookingsystem.com
SITE_URL=http://localhost:8000
```

## 🎯 Demo Accounts

After running the setup, you can use these demo accounts:

### Admin Users
- **admin/admin123** - Super Admin
- **admin2/admin123** - Regular Admin

### Doctor Users
- **dr_smith/doctor123** - Dr. John Smith (Cardiology)
- **dr_johnson/doctor123** - Dr. Sarah Johnson (Dermatology)
- **dr_williams/doctor123** - Dr. Michael Williams (Neurology)
- **dr_brown/doctor123** - Dr. Emily Brown (Pediatrics)
- **dr_davis/doctor123** - Dr. Robert Davis (Orthopedics)
- **dr_wilson/doctor123** - Dr. Lisa Wilson (General Medicine)
- **dr_martinez/doctor123** - Dr. Maria Martinez (Psychiatry)
- **dr_taylor/doctor123** - Dr. Jennifer Taylor (Gynecology)

### Patient Users
- **patient1/patient123** - John Doe
- **patient2/patient123** - Jane Smith
- **patient3/patient123** - Mike Wilson
- **patient4/patient123** - Sarah Johnson
- **patient5/patient123** - David Brown
- **patient6/patient123** - Lisa Garcia
- **patient7/patient123** - Robert Miller
- **patient8/patient123** - Emily Davis

## 🛠️ Development Commands

### View logs
```bash
docker-compose logs -f web
```

### Access Django shell
```bash
docker-compose exec web python manage.py shell
```

### Run Django commands
```bash
docker-compose exec web python manage.py <command>
```

### Create new sample data
```bash
docker-compose exec web python manage.py create_sample_data
```

### Access database
```bash
docker-compose exec db psql -U booking_user -d booking_system
```

## 🔄 Switching Between Development and Production

### Development Mode (Default)
```bash
# Uses Django development server
docker-compose up --build
```

### Production Mode
```bash
# Update docker.env:
# - Set DEBUG=False
# - Set WEB_COMMAND=gunicorn booking_system.wsgi:application --bind 0.0.0.0:8000 --workers 3

# Then start services
docker-compose up --build
```

## 🔄 Database Management

### Reset database
```bash
docker-compose down -v
docker-compose up --build
```

### Backup database
```bash
docker-compose exec db pg_dump -U booking_user booking_system > backup.sql
```

### Restore database
```bash
docker-compose exec -T db psql -U booking_user booking_system < backup.sql
```

## 📧 Email Notifications

In development, emails are printed to the terminal. Check the web service logs to see email notifications:

```bash
docker-compose logs -f web
```

## 🐛 Troubleshooting

### Port conflicts
If ports 8000 or 5432 are already in use, modify the ports in `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### Database connection issues
Ensure the database is healthy before the web service starts:

```bash
docker-compose exec db pg_isready -U booking_user -d booking_system
```

### Permission issues
If you encounter permission issues, ensure the entrypoint script is executable:

```bash
chmod +x docker-entrypoint.sh
```

## 🚀 Production Deployment

### Using Docker Swarm
```bash
docker stack deploy -c docker-compose.prod.yml booking-system
```

### Using Kubernetes
Convert the docker-compose files to Kubernetes manifests:

```bash
kompose convert -f docker-compose.prod.yml
```

## 📊 Monitoring

### Health checks
- Database: `docker-compose exec db pg_isready -U booking_user -d booking_system`
- Web: `curl http://localhost:8000/`

### Resource usage
```bash
docker stats
```

## 🔒 Security Notes

- Change default passwords in production
- Use strong SECRET_KEY
- Enable SSL in production
- Configure proper ALLOWED_HOSTS
- Use environment-specific settings

## 📝 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Deployment Guide](https://docs.djangoproject.com/en/stable/howto/deployment/)
