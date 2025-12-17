# Unscribe - AI-Powered Subscription Management Platform

**Unscribe** is an intelligent subscription management platform that automatically analyzes your Gmail inbox to discover, track, and cancel unwanted subscriptions. Our AI agents scan your emails, extract subscription details (cost, renewal dates, cancellation links), and present everything in a clean dashboard with real-time spending insights.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend)
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (recommended)

### Environment Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd CMPE-Fall25-Kanakasarat-Siripurapu-subscription-cancelling-agentic-app-main
```

2. **Create `.env` file** in project root (copy from `.env.example`):
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. **Start services with Docker Compose**:
```bash
docker-compose up -d
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Backend API (port 8000)
- Celery Worker
- Celery Beat

4. **Access the application**:
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Setup (Without Docker)

#### Backend Setup:
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations (if using Alembic)
# alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

#### Worker Setup (separate terminal):
```bash
cd backend
source venv/bin/activate
celery -A worker.tasks.celery_app worker --loglevel=info --concurrency=4
```

## 🏗️ Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application
│   │   ├── config.py               # Configuration
│   │   ├── database.py             # Database connection
│   │   ├── models/                 # SQLAlchemy models
│   │   ├── schemas/                # Pydantic schemas
│   │   ├── api/                    # API endpoints
│   │   │   ├── auth.py            # Authentication
│   │   │   ├── scan.py            # Email scanning
│   │   │   ├── subscriptions.py   # Subscription management
│   │   │   ├── dashboard.py       # Dashboard stats
│   │   │   └── activity.py        # Activity logs
│   │   ├── services/               # Business logic
│   │   │   ├── gmail_service.py    # Gmail OAuth + API
│   │   │   ├── detection_service.py # Subscription detection
│   │   │   └── unsubscribe_service.py
│   │   └── utils/                  # Helper functions
│   │       ├── patterns.py         # Regex patterns
│   │       ├── encryption.py       # Token encryption
│   │       └── llm_prompt.py       # LLM prompts
│   ├── worker/
│   │   └── tasks.py                # Celery tasks
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                        # (To be implemented)
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔑 Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:3000/auth/callback` (dev), `https://yourapp.com/auth/callback` (prod)
5. Copy Client ID and Client Secret to `.env`

## 📊 Database Schema

The database includes tables for:
- `users` - User accounts with encrypted Gmail credentials
- `subscriptions` - Detected subscriptions with metadata
- `email_import_sessions` - Tracks scanning progress
- `unsubscribe_actions` - Tracks cancellation attempts
- `subscription_events` - Audit trail of subscription events
- `activity_log` - Unified activity log

See `CI/postgre sql database schema.py` for the complete schema definition.

## 🔒 Security

- All data encrypted at rest (AES-256)
- Gmail refresh tokens encrypted with user-specific keys
- HTTPS/TLS for all communications
- Rate limiting (100 req/min per user)

## 📄 License

MIT License

## 🆘 Support

For issues or questions, please open an issue in the repository.

---

**Made with ❤️ by the Unscribe team**
