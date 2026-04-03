#!/bin/bash

# Exit on any error
set -e

echo "--- BUILDING PROJECT ---"

# 1. Create a virtual environment for the build process
# This avoids the "externally-managed-environment" error on Vercel
echo "Setting up virtual environment..."
python3 -m venv venv_build
source venv_build/bin/activate

# 2. Upgrade pip and install dependencies 
echo "Installing pip dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 3. Run Django Management Commands
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear

echo "Running migrations..."
python3 manage.py migrate --noinput

echo "--- BUILD COMPLETE ---"
