# ⚖️ LegalAI — AI-Powered Legal Documentation Assistant

> Analyze legal documents instantly using AI. Get plain-English summaries, risk assessments, warnings, and recommendations before you sign.

---

## 🌐 Live Project Links

| Service | URL |
|---------|-----|
| 🌐 **Frontend (Live App)** | https://legalai-q2y8.vercel.app |
| ⚙️ **Backend API** | https://legalai-backend-qr2l.onrender.com |
| 📚 **API Documentation** | https://legalai-backend-qr2l.onrender.com/docs |
| ❤️ **Health Check** | https://legalai-backend-qr2l.onrender.com/health |
| 🐙 **GitHub Repository** | https://github.com/abishek-046/legalai |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18 + Vite, Tailwind CSS, React Router v6, Axios, React Dropzone |
| **Backend** | Python FastAPI, JWT Authentication, Slowapi (rate limiting) |
| **Database** | Supabase (PostgreSQL) |
| **AI** | OpenAI GPT-4o-mini |
| **OCR** | pdfplumber (PDF), python-docx (DOCX), pytesseract (Images) |
| **PDF Reports** | ReportLab |
| **Hosting** | Vercel (frontend) + Render (backend) |

---

## 📁 Project Structure

```
legalai/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Environment settings
│   ├── database.py              # Supabase client
│   ├── requirements.txt         # Python dependencies
│   ├── build.sh                 # Render build script
│   ├── render.yaml              # Render deployment config
│   ├── runtime.txt              # Python version (3.11.9)
│   ├── .env.example             # Environment variables template
│   ├── routes/
│   │   ├── auth.py              # POST /register, POST /login
│   │   ├── documents.py         # POST /analyze
│   │   ├── reports.py           # GET/DELETE /report(s), PDF download
│   │   └── dependencies.py      # JWT auth guard
│   ├── services/
│   │   ├── auth_service.py      # User auth logic
│   │   └── document_service.py  # Supabase CRUD
│   ├── ai/
│   │   └── analyzer.py          # OpenAI GPT-4o-mini integration
│   ├── models/
│   │   ├── user.py              # Pydantic user schemas
│   │   └── document.py          # Pydantic document schemas
│   └── utils/
│       ├── ocr.py               # PDF/DOCX/Image text extraction
│       └── pdf_report.py        # ReportLab PDF generation
│
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    ├── vercel.json              # Vercel SPA routing fix
    └── src/
        ├── App.jsx
        ├── main.jsx
        ├── index.css
        ├── context/
        │   └── AuthContext.jsx  # Global auth state
        ├── services/
        │   ├── api.js           # Axios instance
        │   ├── authService.js   # Login/register API calls
        │   └── documentService.js # Upload/analyze/reports API calls
        ├── hooks/
        │   └── useDocuments.js  # Custom hook for reports
        ├── components/
        │   ├── Navbar.jsx
        │   ├── Footer.jsx
        │   ├── ProtectedRoute.jsx
        │   ├── LoadingSpinner.jsx
        │   ├── RiskBadge.jsx
        │   ├── AlertBox.jsx
        │   └── ReportCard.jsx
        └── pages/
            ├── Home.jsx
            ├── Login.jsx
            ├── Register.jsx
            ├── Upload.jsx
            ├── Report.jsx
            ├── Dashboard.jsx
            └── About.jsx
```

---

## 🗄️ Database Schema (Supabase PostgreSQL)

```sql
-- Users table
create table users (
  id uuid default gen_random_uuid() primary key,
  name text not null,
  email text unique not null,
  hashed_password text not null,
  created_at timestamptz default now()
);

-- Documents table
create table documents (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references users(id) on delete cascade,
  filename text not null,
  document_type text,
  extracted_text text,
  summary text,
  risk_level text,
  warnings text[],
  suspicious_clauses text[],
  missing_clauses text[],
  financial_risks text[],
  expiry_risks text[],
  unfair_conditions text[],
  recommendations text[],
  safe_to_sign boolean default false,
  created_at timestamptz default now()
);
```

---

## 📡 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/register` | No | Register new user |
| POST | `/api/login` | No | Login, get JWT token |
| POST | `/api/analyze` | Yes | Upload + AI analyze document |
| GET | `/api/reports` | Yes | List user's reports |
| GET | `/api/report/{id}` | Yes | Get single report |
| DELETE | `/api/report/{id}` | Yes | Delete report |
| GET | `/api/report/{id}/download` | Yes | Download PDF report |
| GET | `/health` | No | Health check |
| GET | `/debug` | No | Debug env vars |

---

## ✨ Features

- **User Authentication** — Register, login, JWT-protected routes
- **Document Upload** — Drag & drop, PDF/DOCX support
- **AI Analysis** — GPT-4o-mini powered legal analysis
- **Risk Assessment** — Low/Medium/High with color coding
- **Detailed Reports** — Warnings, suspicious clauses, missing clauses, financial risks, recommendations
- **PDF Download** — Professional PDF reports via ReportLab
- **Dashboard** — Search, filter by date, delete reports
- **Responsive Design** — Mobile-friendly throughout

---

## 🔒 Security Features

- Bcrypt password hashing
- JWT authentication with expiry
- File type validation (whitelist)
- File size limits (10MB)
- Rate limiting on all endpoints
- CORS configuration
- API keys in environment variables

---

## ⚙️ Environment Variables

### Backend (Render)

| Key | Description |
|-----|-------------|
| `SUPABASE_URL` | `https://uvskqnxnywfewbnbhses.supabase.co` |
| `SUPABASE_KEY` | Supabase anon public key |
| `SUPABASE_SERVICE_KEY` | Supabase service_role key |
| `SECRET_KEY` | Random string for JWT signing |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` |
| `OPENAI_API_KEY` | OpenAI API key |
| `MAX_FILE_SIZE_MB` | `10` |
| `ALLOWED_ORIGINS` | `https://legalai-q2y8.vercel.app` |
| `PYTHON_VERSION` | `3.11.9` |

### Frontend (Vercel)

| Key | Description |
|-----|-------------|
| `VITE_API_URL` | `https://legalai-backend-qr2l.onrender.com/api` |

---

## 🚀 Local Development Setup

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
# Create .env file with your values
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 📝 Supported File Types

| Type | Support |
|------|---------|
| PDF (text-based) | ✅ Full support |
| DOCX | ✅ Full support |
| PNG/JPG | ⚠️ Requires Tesseract (local only) |
| Scanned PDF | ❌ Not supported |

---

## ⚠️ Important Notes

- **Render free tier** sleeps after 15 minutes of inactivity. First request takes ~30 seconds to wake up
- This app is for **informational purposes only** — not a substitute for professional legal advice
- OpenAI API key required for real AI analysis. Without it, demo analysis is returned
- Use **UptimeRobot** (free) to ping `/health` every 14 minutes to keep Render awake

---

## 👨‍💻 Developer

**Abishek** — abishek.rdn@gmail.com  
GitHub: https://github.com/abishek-046

---

*Built with ❤️ using FastAPI, React, Supabase, and OpenAI*
