# LegalAI Deployment Guide

## My Deployment URLs (fill in after deploying)
- Frontend (Vercel):  https://_____________________.vercel.app
- Backend (Render):   https://_____________________.onrender.com
- MongoDB Atlas:      cluster0._____________________.mongodb.net

---

## Tools to Install First
1. Git:    https://git-scm.com/download/win
2. Node:   https://nodejs.org  (LTS version)
3. Python: https://www.python.org/downloads/  ← CHECK "Add to PATH"

---

## Services to Sign Up For (all free)
1. GitHub:  https://github.com
2. MongoDB: https://www.mongodb.com/atlas
3. Render:  https://render.com
4. Vercel:  https://vercel.com

---

## Deployment Order
1. Install Git, Node, Python on your PC
2. Create GitHub account + new repo named "legalai"
3. Run push_to_github.bat to upload your code
4. Create MongoDB Atlas free cluster → copy connection string
5. Deploy backend on Render (root dir: backend)
6. Deploy frontend on Vercel (root dir: frontend)
7. Update ALLOWED_ORIGINS on Render with your Vercel URL
8. Test the live app!

---

## Backend Environment Variables (Render)
MONGODB_URL          = mongodb+srv://user:pass@cluster.mongodb.net/legal_assistant
DATABASE_NAME        = legal_assistant
SECRET_KEY           = (any long random string)
ALGORITHM            = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 60
OPENAI_API_KEY       = sk-your-key-here
MAX_FILE_SIZE_MB     = 10
ALLOWED_ORIGINS      = https://your-app.vercel.app

## Frontend Environment Variables (Vercel)
VITE_API_URL         = https://your-backend.onrender.com/api

---

## Render Build Settings
Root Directory:  backend
Build Command:   apt-get install -y tesseract-ocr && pip install -r requirements.txt
Start Command:   uvicorn main:app --host 0.0.0.0 --port $PORT
Runtime:         Python 3

## Vercel Build Settings
Root Directory:  frontend
Framework:       Vite
Build Command:   npm run build
Output Dir:      dist

---

## Troubleshooting
- CORS error?       → Check ALLOWED_ORIGINS matches Vercel URL exactly (no trailing slash)
- 401 errors?       → Check SECRET_KEY is set on Render
- DB connection?    → Check Atlas Network Access allows 0.0.0.0/0
- Render sleeping?  → Free tier sleeps after 15min. First request takes ~30s to wake up
- 404 on refresh?   → vercel.json handles this (already configured)
- Tesseract error?  → Build command must include apt-get install -y tesseract-ocr

## Keep Render Awake (Optional)
Sign up at https://uptimerobot.com (free)
Add HTTP monitor → URL: https://your-backend.onrender.com/health
Interval: every 14 minutes
This prevents the free tier from sleeping.
