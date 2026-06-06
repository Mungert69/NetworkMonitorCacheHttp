#!/bin/bash

# Security Check Script for Flask Cache Server
# This script installs security tools and runs vulnerability scans

set -e  # Exit on any error

echo "🔒 Starting Security Check..."
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if Python and pip are available
if ! command -v python3 &> /dev/null; then
    print_error "Python3 is not installed"
    exit 1
fi

if ! command -v pip &> /dev/null; then
    print_error "pip is not installed"
    exit 1
fi

print_status "Python and pip are available"

# Install security tools
echo ""
echo "📦 Installing security tools..."
echo "=================================="

# Install development dependencies
print_status "Installing security scanning tools..."
pip install --upgrade pip
pip install -r requirements-dev.txt

print_status "Security tools installed successfully"

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found"
    exit 1
fi

# Install project dependencies if not already installed
print_status "Installing project dependencies..."
pip install -r requirements.txt

echo ""
echo "🔍 Running Security Scans..."
echo "=================================="

# Safety check - vulnerability scanning
print_status "Running safety vulnerability check..."
if safety check --json; then
    print_status "✅ No vulnerabilities found by safety"
else
    print_warning "⚠️  Safety scan found potential vulnerabilities"
fi

# Alternative safety output (non-JSON)
echo ""
print_status "Running detailed safety check..."
safety check

# pip-audit for comprehensive security check
echo ""
print_status "Running pip-audit comprehensive security check..."
if pip-audit; then
    print_status "✅ No vulnerabilities found by pip-audit"
else
    print_warning "⚠️  pip-audit found potential vulnerabilities"
fi

# Check for known vulnerable packages
echo ""
print_status "Checking for known vulnerable packages..."
echo "=================================="

# Check for specific vulnerable packages that might affect Flask
vulnerable_packages=(
    "flask"
    "werkzeug"
    "jinja2"
    "click"
    "itsdangerous"
    "flask-cors"
    "python-dotenv"
)

for package in "${vulnerable_packages[@]}"; do
    if pip list | grep -q "$package"; then
        version=$(pip list | grep "$package" | awk '{print $2}')
        print_status "$package: $version"
    else
        print_warning "$package: Not installed"
    fi
done

echo ""
echo "📋 Security Summary"
echo "=================================="

# Display project information
if [ -f "app.py" ]; then
    print_status "Flask Cache Server security check completed"
else
    print_warning "app.py not found - Flask application not detected"
fi

# Check if API key is secure (if config exists)
if [ -f "config.py" ]; then
    if grep -q "default-api-key-change-in-production" config.py; then
        print_error "⚠️  Using default API key - change this in production!"
    else
        print_status "API key appears to be custom (not default)"
    fi
fi

# Check file permissions
echo ""
print_status "Checking file permissions..."
if [ -f "requirements.txt" ]; then
    perms=$(stat -c "%a" requirements.txt)
    print_status "requirements.txt permissions: $perms"
fi

if [ -f "config.py" ]; then
    perms=$(stat -c "%a" config.py)
    print_status "config.py permissions: $perms"
fi

echo ""
echo "✅ Security check completed!"
echo "=================================="
echo "💡 Recommendations:"
echo "   - Review any warnings above"
echo "   - Keep dependencies updated regularly"
echo "   - Monitor for new security alerts"
echo "   - Run this script regularly (e.g., weekly)"