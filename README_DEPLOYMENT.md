# Render Deployment Guide

## Prerequisites
Your system is now configured for Render deployment.

## Important Notes

### Media Files Warning
⚠️ **Render uses ephemeral storage** - uploaded media files (candidate photos, voter profiles) will be deleted on each deployment or restart.

**Solutions:**
1. **AWS S3** (Recommended)
   - Add to requirements.txt: `django-storages boto3`
   - Configure in settings.py
   
2. **Cloudinary** (Easier setup)
   - Add to requirements.txt: `django-cloudinary-storage`
   - Sign up at cloudinary.com
   - Add credentials to Render environment variables

## Deployment Steps

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Create Render Account**
   - Go to render.com and sign up

3. **Deploy from Dashboard**
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will auto-detect render.yaml

4. **Set Environment Variables** (in Render Dashboard)
   - `ALLOWED_HOSTS`: Add your Render URL (e.g., `voting-system.onrender.com`)
   - Other variables are auto-configured from render.yaml

5. **Create Superuser** (after first deployment)
   - Go to Render Dashboard → Shell
   - Run: `python manage.py createsuperuser`

## Post-Deployment
- Access admin: `https://your-app.onrender.com/admin/`
- Test the voting system
- Upload candidate photos (note: will be lost on restart without cloud storage)

## Next Steps
Configure cloud storage for persistent media files before production use.
