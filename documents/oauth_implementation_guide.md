# OAuth2 Implementation Guide for Django

## 1. Choose OAuth Library

**Recommended Options:**
- `django-allauth` - Most popular, comprehensive
- `social-auth-app-django` - Lightweight, flexible
- `django-oauth-toolkit` - If you need to provide OAuth services too

**Best Choice:** `django-allauth` for your use case

## 2. Google Cloud Console Setup

### Steps:
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable Google+ API and/or Google Identity API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Configure OAuth consent screen:
   - Add your app name, logo, privacy policy
   - Add test users during development
6. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URIs: 
     - `http://localhost:8000/accounts/google/login/callback/` (development)
     - `https://yourdomain.com/accounts/google/login/callback/` (production)

### Save These Values:
- Client ID
- Client Secret

## 3. Django Project Configuration

### Install Package:
```bash
pip install django-allauth
```

### Settings.py Configuration:

#### Add to INSTALLED_APPS:
```python
INSTALLED_APPS = [
    # ... your apps
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]
```

#### Add Middleware (if needed):
```python
MIDDLEWARE = [
    # ... existing middleware
    'allauth.account.middleware.AccountMiddleware',
]
```

#### Site Framework:
```python
SITE_ID = 1
```

#### Authentication Backends:
```python
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
```

#### OAuth Settings:
```python
# Allauth settings
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  # or 'optional'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USERNAME_REQUIRED = False
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Social account settings
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'  # Google already verifies
SOCIALACCOUNT_QUERY_EMAIL = True

# Google-specific settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}
```

## 4. Environment Variables

### .env file:
```
GOOGLE_OAUTH2_CLIENT_ID=your_client_id_here
GOOGLE_OAUTH2_CLIENT_SECRET=your_client_secret_here
```

### Load in settings.py:
```python
import os
from decouple import config  # pip install python-decouple

# OAuth credentials
GOOGLE_OAUTH2_CLIENT_ID = config('GOOGLE_OAUTH2_CLIENT_ID')
GOOGLE_OAUTH2_CLIENT_SECRET = config('GOOGLE_OAUTH2_CLIENT_SECRET')
```

## 5. Database Setup

### Run Migrations:
```bash
python manage.py migrate
```

### Create Social Application:
**Option 1 - Admin Panel:**
1. Go to `/admin/`
2. Navigate to "Social Applications"
3. Add new application:
   - Provider: Google
   - Name: Google
   - Client ID: Your Google Client ID
   - Secret Key: Your Google Client Secret
   - Sites: Select your site

**Option 2 - Management Command:**
Create a custom management command to automate this

## 6. URL Configuration

### Project urls.py:
```python
urlpatterns = [
    # ... your URLs
    path('accounts/', include('allauth.urls')),
]
```

## 7. Templates Integration

### Login Template:
```html
<!-- In your login template -->
{% load socialaccount %}

<!-- Traditional login form -->
<form method="post">
    <!-- your login fields -->
</form>

<!-- OAuth login -->
<div class="social-login">
    <a href="{% provider_login_url 'google' %}">
        <button>Login with Google</button>
    </a>
</div>
```

## 8. Signal Handlers (Optional)

### Handle user creation/login:
```python
# signals.py
from allauth.socialaccount.signals import pre_social_login
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(pre_social_login)
def handle_social_login(sender, request, sociallogin, **kwargs):
    # Custom logic for handling social login
    # e.g., set user_type, create doctor profile, etc.
    pass
```

## 9. Custom User Integration

### Link with your User model:
Since you have a custom User model with `user_type`, you'll need to:

1. **Override allauth adapter:**
   - Create custom adapter to set `user_type = 'patient'` for OAuth users
   - Handle first-time login vs returning user

2. **Profile completion:**
   - Redirect new OAuth users to complete profile
   - Collect additional required information

## 10. Testing Strategy

### Development Testing:
1. Use `http://localhost:8000` in Google Console
2. Test OAuth flow end-to-end
3. Verify user creation and data population

### Production Considerations:
1. Update redirect URIs in Google Console
2. Use HTTPS for all OAuth redirects
3. Configure proper domain verification

## 11. Security Considerations

### Best Practices:
1. **Environment Variables**: Never commit OAuth secrets
2. **HTTPS**: Always use HTTPS in production
3. **CSRF Protection**: Ensure CSRF tokens are properly handled
4. **Scope Limitation**: Only request necessary permissions
5. **Token Management**: Implement proper token refresh if needed

## 12. Error Handling

### Common Issues:
1. **Redirect URI Mismatch**: Ensure URLs match exactly
2. **Email Conflicts**: Handle existing users with same email
3. **Incomplete Profiles**: Guide users to complete missing information
4. **Permission Errors**: Handle declined permissions gracefully

## 13. Integration with Your Models

### Consider These Integrations:
1. **User Type Setting**: Automatically set `user_type = 'patient'`
2. **Profile Completion**: Redirect to complete phone number, etc.
3. **Wallet Initialization**: Create wallet with 0 balance
4. **Welcome Flow**: Show app tutorial for new OAuth users

## 14. Additional OAuth Providers (Optional)

### To add more providers:
```python
INSTALLED_APPS += [
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.github',
    # etc.
]
```

## 15. Monitoring and Analytics

### Track OAuth Usage:
1. Monitor successful/failed OAuth attempts
2. Track user preferences (OAuth vs traditional login)
3. Analyze user conversion rates from OAuth signup