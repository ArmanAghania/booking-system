# Google OAuth2 Setup for Development

## Quick Setup for Localhost Testing

### 1. Google Cloud Console Setup

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Create a new project or select existing one

2. **Enable Google+ API**
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API" and enable it

3. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Add authorized redirect URIs:
     - `http://localhost:8001/accounts/google/login/callback/`
     - `http://127.0.0.1:8001/accounts/google/login/callback/`

4. **Copy Credentials**
   - Copy the Client ID and Client Secret

### 2. Update Django Settings

Run this command with your actual credentials:

```bash
python manage.py setup_google_oauth --client-id "YOUR_ACTUAL_CLIENT_ID" --client-secret "YOUR_ACTUAL_CLIENT_SECRET"
```

### 3. Test the Integration

1. **Start the server:**
   ```bash
   python manage.py runserver 0.0.0.0:8001
   ```

2. **Visit the login page:**
   - Go to: http://localhost:8001/accounts/login/
   - You should see the "Continue with Google" button

3. **Test Google Login:**
   - Click "Continue with Google"
   - Complete the OAuth flow
   - You should be redirected back to your app

### 4. Development URLs

For development, use these URLs:
- **Main site**: http://localhost:8001/
- **Login page**: http://localhost:8001/accounts/login/
- **Google OAuth callback**: http://localhost:8001/accounts/google/login/callback/

### 5. Troubleshooting

**Common Issues:**

1. **"redirect_uri_mismatch" error:**
   - Make sure you added the exact callback URL in Google Console
   - Check that the URL matches exactly: `http://localhost:8001/accounts/google/login/callback/`

2. **"invalid_client" error:**
   - Verify your Client ID and Secret are correct
   - Make sure you're using the right project in Google Console

3. **"access_denied" error:**
   - Check that Google+ API is enabled
   - Verify OAuth consent screen is configured

**Debug Steps:**
1. Check Django logs for errors
2. Verify site domain in Django admin: `/admin/sites/site/`
3. Check social app configuration: `/admin/socialaccount/socialapp/`

### 6. Production Setup

When moving to production:
1. Update the site domain to your actual domain
2. Add production callback URLs to Google Console
3. Update the social app with production URLs

## Testing Without Google OAuth

If you want to test the UI without setting up Google OAuth:

1. The "Continue with Google" button will still be visible
2. Clicking it will show an error (which is expected)
3. You can still test regular email/password login
4. The OAuth integration is ready for when you set up the credentials

## Development Tips

- Use `http://localhost:8001` (not `127.0.0.1`) for consistency
- Test both login and registration flows
- Check that profile data is imported correctly
- Verify account linking works for existing users
