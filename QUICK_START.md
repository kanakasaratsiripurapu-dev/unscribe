# Quick Start Guide

## Step 1: Install Homebrew (if not installed)

Homebrew is a package manager for macOS. Install it with:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the on-screen instructions. After installation, you may need to add Homebrew to your PATH.

## Step 2: Install and Start PostgreSQL and Redis

Run the setup script:

```bash
./setup_services.sh
```

This will:
- Install PostgreSQL 15
- Install Redis
- Start both services
- Create the database and user

**OR** install manually:

```bash
# Install PostgreSQL
brew install postgresql@15
brew services start postgresql@15

# Install Redis  
brew install redis
brew services start redis

# Create database
createdb subscout_db
psql subscout_db -c "CREATE USER subscout WITH PASSWORD 'password';"
psql subscout_db -c "GRANT ALL PRIVILEGES ON DATABASE subscout_db TO subscout;"
```

## Step 3: Configure API Keys

Edit the `.env` file and add your API keys:

```bash
nano .env
```

**Required:**
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` - Get from [Google Cloud Console](https://console.cloud.google.com)
- At least one LLM API key:
  - `OPENAI_API_KEY` - Get from [OpenAI Platform](https://platform.openai.com/api-keys)
  - OR `ANTHROPIC_API_KEY` - Get from [Anthropic Console](https://console.anthropic.com/)

**Note:** The `.env` file already has generated `JWT_SECRET_KEY` and `ENCRYPTION_KEY` - you don't need to change these.

## Step 4: Start the Application

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Step 5: Verify It's Running

Open your browser to:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Alternative: Use Docker (If Available)

If you have Docker Desktop installed:

```bash
docker-compose up -d
```

This will start all services (PostgreSQL, Redis, Backend) automatically.

## Troubleshooting

### PostgreSQL connection error
```bash
# Check if PostgreSQL is running
brew services list | grep postgresql

# Start if not running
brew services start postgresql@15

# Test connection
psql postgres -c "SELECT version();"
```

### Redis connection error
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# Start if not running
brew services start redis
```

### Port already in use
```bash
# Change port in the uvicorn command
uvicorn app.main:app --port 8001
```

## Next Steps

1. Get Google OAuth credentials from Google Cloud Console
2. Get an LLM API key (OpenAI or Anthropic)
3. Update `.env` file with your credentials
4. Start the backend server
5. Access the API documentation at http://localhost:8000/docs

