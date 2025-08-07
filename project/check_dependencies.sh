#!/bin/bash
# check_dependencies.sh
# Script to validate Python package dependencies in requirements.txt

echo "Checking Python package dependencies..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed. Please install Python first."
    exit 1
fi

# Create a temporary virtual environment
echo "Creating temporary virtual environment..."
python3 -m venv .venv_check
source .venv_check/bin/activate

# Upgrade pip
pip install --upgrade pip

# Check dependencies without installing
echo "Checking dependencies for compatibility..."
pip install --dry-run -r requirements.txt

# Save the result
RESULT=$?

# Clean up
echo "Cleaning up..."
deactivate
rm -rf .venv_check

# Report results
if [ $RESULT -eq 0 ]; then
    echo "✅ All dependencies are compatible!"
    echo "You can now build the Docker image with: docker-compose build"
    exit 0
else
    echo "❌ Dependency conflicts detected. Please fix requirements.txt and try again."
    exit 1
fi
