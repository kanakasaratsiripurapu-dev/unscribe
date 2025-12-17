#!/bin/bash

echo "🌐 Setting up public URL for your application..."
echo ""
echo "Starting localtunnel on port 3000..."
echo "This will create a public URL you can share."
echo ""
echo "Once you see a URL like 'https://xxx.loca.lt', copy it and:"
echo "1. Update Google Cloud Console redirect URI to: https://xxx.loca.lt/auth/callback"
echo "2. Update .env file: GOOGLE_REDIRECT_URI=https://xxx.loca.lt/auth/callback"
echo "3. Restart your backend"
echo ""
echo "Starting tunnel (keep this terminal open)..."
echo ""

npx --yes localtunnel --port 3000

