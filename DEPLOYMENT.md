# Deployment Guide for CalmMateAI

## Quick Deploy to Render (Recommended for Beginners)

### Step 1: Sign Up for Render
1. Go to [render.com](https://render.com)
2. Sign up for a free account (you can use GitHub to sign up)
3. Verify your email

### Step 2: Create a New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `saberabanu0001/NewCalmateAI`
3. Render will auto-detect your Flask app

### Step 3: Configure the Build
- **Name**: calmateai (or your preferred name)
- **Environment**: Python 3
- **Region**: Choose closest to you
- **Branch**: main
- **Root Directory**: (leave empty)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app` (Render requires this field)

### Step 4: Set Environment Variables
In the **Environment** section, add these variables:

```
FLASK_ENV=production
FLASK_SECRET_KEY=your-super-secret-key-here-change-this
GROQ_API_KEY=your-groq-api-key-here
PORT=10000
```

**⚠️ Important:** Generate a new secret key for FLASK_SECRET_KEY:
```bash
python -c 'import secrets; print(secrets.token_urlsafe(32))'
```

### Step 5: Deploy!
1. Click **"Create Web Service"**
2. Wait 3-5 minutes for build and deployment
3. Your app will be live at: `https://calmateai.onrender.com` (or your chosen name)

### Step 6: Add Persistent Storage (Important!)
Since Render's filesystem is ephemeral, you need to add a disk for data persistence:

1. Go to your service → **"Disks"** tab
2. Click **"Add Disk"**
3. **Name**: `data`
4. **Size**: 1 GB
5. **Mount Path**: `/var/data`
6. Click **"Mount"**

### Step 7: Update Code for Persistent Storage
After adding the disk, update your code to use `/var/data` for file storage.

---

## Deploy to Railway (Alternative)

### Step 1: Sign Up
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub

### Step 2: Create Project
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository

### Step 3: Set Environment Variables
- Click on your service → **Variables**
- Add the same environment variables as above

### Step 4: Deploy
Railway will automatically detect your Procfile and deploy!

---

## Deploy to Fly.io (Advanced)

### Step 1: Install Fly CLI
```bash
brew install flyctl  # macOS
# or visit https://fly.io/docs/getting-started/installing-flyctl/
```

### Step 2: Login
```bash
fly auth login
```

### Step 3: Create App
```bash
fly launch
```

### Step 4: Deploy
```bash
fly deploy
```

---

## Environment Variables Needed

```bash
FLASK_ENV=production
FLASK_SECRET_KEY=<generate-a-secure-random-key>
GROQ_API_KEY=<your-groq-api-key>
PORT=8080
```

---

## Post-Deployment Checklist

- [ ] Test user registration/login
- [ ] Test AI chat functionality
- [ ] Test emergency contacts search
- [ ] Test university access
- [ ] Check that persistent data (users.json, uploads) is working
- [ ] Verify HTTPS is working
- [ ] Test on mobile devices

---

## Troubleshooting

### Build Fails
- Check that `requirements.txt` is up to date
- Verify Python version in `runtime.txt` matches your local version
- Check build logs in Render/Railway dashboard

### App Crashes on Startup
- Verify all environment variables are set
- Check that GROQ_API_KEY is valid
- Look at application logs in the dashboard

### Data Not Persisting
- Make sure you've added a persistent disk
- Check file paths are using `/var/data` for storage
- Restart the service after adding the disk

---

## Need Help?
- Render Docs: https://render.com/docs
- Railway Docs: https://docs.railway.app
- Fly.io Docs: https://fly.io/docs

