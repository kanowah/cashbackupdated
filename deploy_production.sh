#!/bin/bash

echo "🚀 Starting Production Deployment..."

# Navigate to app directory
cd /var/www/cashback

# Pull latest code
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# Clear all caches
echo "🧹 Clearing Python and Streamlit caches..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
rm -rf ~/.streamlit/ 2>/dev/null || true

# Clear temp files
echo "🗑️ Clearing temporary files..."
rm -f temp/temp_uploaded_* 2>/dev/null || true

# Stop and restart PM2 process
echo "🔄 Restarting PM2 process..."
pm2 stop streamlit-cashback
pm2 delete streamlit-cashback

# Start fresh PM2 process
pm2 start "streamlit run pdf_processor_final_working.py --server.port 8502 --server.address 0.0.0.0" --name streamlit-cashback --cwd /var/www/cashback

# Save PM2 configuration
pm2 save

# Check status
echo "✅ Deployment Status:"
pm2 status streamlit-cashback

# Test if app is responding
sleep 5
echo "🌐 Testing application response..."
curl -I http://localhost:8502 || echo "⚠️ App may still be starting..."

echo "🎉 Deployment completed!"
echo "📊 Access your app at: http://your-vps-ip:8502"