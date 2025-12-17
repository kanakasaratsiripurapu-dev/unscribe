# Deployment Guide

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Install Docker Desktop** from https://www.docker.com/products/docker-desktop

2. **Create `.env` file** (copy from `.env.example`):
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Start all services**:
```bash
docker-compose up -d
```

4. **Check status**:
```bash
docker-compose ps
docker-compose logs -f backend
```

5. **Access the API**:
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health

### Option 2: Manual Setup (Without Docker)

#### Prerequisites
- Python 3.10+ (3.9 may work but some dependencies require 3.10+)
- PostgreSQL 15+
- Redis 7+

#### Step 1: Set up PostgreSQL
```bash
# macOS (using Homebrew)
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb subscout_db
psql subscout_db -c "CREATE USER subscout WITH PASSWORD 'password';"
psql subscout_db -c "GRANT ALL PRIVILEGES ON DATABASE subscout_db TO subscout;"
```

#### Step 2: Set up Redis
```bash
# macOS (using Homebrew)
brew install redis
brew services start redis

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

#### Step 3: Set up Python Environment
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers (for unsubscribe service)
playwright install chromium
```

#### Step 4: Configure Environment
```bash
# Copy example env file
cp ../.env.example ../.env

# Edit .env file with your credentials:
# - GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET (from Google Cloud Console)
# - OPENAI_API_KEY or ANTHROPIC_API_KEY (at least one required)
# - Generate ENCRYPTION_KEY: python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# - Generate JWT_SECRET_KEY: python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Step 5: Run Database Migrations
The application will automatically create tables on first startup, or you can run:
```bash
# If using Alembic (future)
# alembic upgrade head
```

#### Step 6: Start Backend Server
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Step 7: Start Celery Worker (in separate terminal)
```bash
cd backend
source venv/bin/activate
celery -A worker.tasks.celery_app worker --loglevel=info --concurrency=4
```

#### Step 8: Start Celery Beat (optional, for scheduled tasks)
```bash
cd backend
source venv/bin/activate
celery -A worker.tasks.celery_app beat --loglevel=info
```

## Configuration

### Required Environment Variables

1. **Google OAuth** (for Gmail access):
   - Go to https://console.cloud.google.com
   - Create a project and enable Gmail API
   - Create OAuth 2.0 credentials
   - Set redirect URI: `http://localhost:3000/auth/callback`

2. **LLM Provider** (at least one):
   - **OpenAI**: Get API key from https://platform.openai.com/api-keys
   - **Anthropic**: Get API key from https://console.anthropic.com/

3. **Security Keys**:
   ```bash
   # Generate encryption key
   python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   
   # Generate JWT secret
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

## Testing the Deployment

1. **Health Check**:
```bash
curl http://localhost:8000/health
```

2. **API Documentation**:
   - Open http://localhost:8000/docs in your browser
   - Interactive API documentation (Swagger UI)

3. **Test Authentication**:
```bash
curl http://localhost:8000/auth/login
```

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running: `pg_isready` or `brew services list`
- Check connection string in `.env`: `DATABASE_URL`
- Verify database exists: `psql -l | grep subscout`

### Redis Connection Issues
- Ensure Redis is running: `redis-cli ping`
- Check Redis URL in `.env`: `REDIS_URL`

### Port Already in Use
- Change port in `docker-compose.yml` or use: `uvicorn app.main:app --port 8001`

### Import Errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

## Production Deployment

For production deployment:

1. Set `ENVIRONMENT=production` in `.env`
2. Use strong, randomly generated keys
3. Set up proper SSL/TLS certificates
4. Configure reverse proxy (nginx, traefik)
5. Set up monitoring and logging
6. Use managed database (AWS RDS, Google Cloud SQL)
7. Use managed Redis (AWS ElastiCache, Redis Cloud)
8. Set up CI/CD pipeline
9. Configure backup strategy

## Next Steps

- Frontend implementation
- Add authentication middleware
- Set up monitoring and alerts
- Configure rate limiting
- Add comprehensive tests

