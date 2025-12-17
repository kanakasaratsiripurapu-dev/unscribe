#!/bin/bash
# Script to set up PostgreSQL and Redis services

set -e

echo "=== SubScout Service Setup ==="
echo ""

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "⚠️  Homebrew is not installed."
    echo ""
    echo "To install Homebrew, run:"
    echo '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    echo ""
    echo "After installing Homebrew, run this script again."
    exit 1
fi

echo "✅ Homebrew found"
echo ""

# Install PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "📦 Installing PostgreSQL..."
    brew install postgresql@15
else
    echo "✅ PostgreSQL already installed"
fi

# Install Redis
if ! command -v redis-cli &> /dev/null; then
    echo "📦 Installing Redis..."
    brew install redis
else
    echo "✅ Redis already installed"
fi

echo ""

# Start PostgreSQL
echo "🚀 Starting PostgreSQL..."
brew services start postgresql@15
sleep 3

# Start Redis
echo "🚀 Starting Redis..."
brew services start redis
sleep 2

# Verify services are running
echo ""
echo "🔍 Verifying services..."

if psql -U postgres -c "SELECT 1;" &> /dev/null || psql postgres -c "SELECT 1;" &> /dev/null; then
    echo "✅ PostgreSQL is running"
else
    echo "⚠️  PostgreSQL may need manual setup"
fi

if redis-cli ping &> /dev/null; then
    echo "✅ Redis is running"
else
    echo "⚠️  Redis may need manual setup"
fi

# Set up database
echo ""
echo "📊 Setting up database..."
psql postgres << 'EOF' || echo "Note: You may need to run database setup manually"
-- Create database if it doesn't exist
SELECT 'CREATE DATABASE subscout_db' 
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'subscout_db')\gexec

-- Create user if it doesn't exist
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'subscout') THEN
      CREATE USER subscout WITH PASSWORD 'password';
   END IF;
END
$$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE subscout_db TO subscout;
EOF

echo ""
echo "✅ Setup complete!"
echo ""
echo "Services status:"
brew services list | grep -E "postgresql|redis" || echo "Run 'brew services list' to check status"

