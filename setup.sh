#!/bin/bash

# Flask Cache Server Setup Script

echo "🚀 Setting up Flask Cache Server for NetworkMonitorLLM"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python3 is installed"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✅ pip3 is installed"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Make test script executable
chmod +x test_server.py

echo "✅ Test script is now executable"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file with default configuration..."
    cat > .env << EOF
# Flask Cache Server Configuration
FLASK_ENV=development
FLASK_DEBUG=True
API_KEY=your-secure-api-key-here
CACHE_DIR=./cache_files
MAX_FILE_SIZE=524288000
LOG_LEVEL=INFO
CORS_ORIGINS=*
EOF
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

# Create cache directory if it doesn't exist
if [ ! -d "cache_files" ]; then
    mkdir cache_files
    echo "✅ Created cache_files directory"
else
    echo "✅ cache_files directory already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file to set your API key and other configuration"
echo "2. Start the server: python3 app.py"
echo "3. Test the server: python3 test_server.py"
echo "4. Or use Docker: docker-compose up -d"
echo ""
echo "🌐 Server will be available at: http://localhost:5000"
echo "🏥 Health check: http://localhost:5000/health"
echo ""
echo "🔗 For NetworkMonitorLLM integration, update appsettings.json:"
echo '   "RemoteCache": {'
echo '     "Enabled": true,'
echo '     "Type": "Http",'
echo '     "BaseUrl": "http://localhost:5000",'
echo '     "ApiKey": "your-secure-api-key-here"'
echo '   }'
