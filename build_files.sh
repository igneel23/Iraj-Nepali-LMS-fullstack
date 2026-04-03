#!/bin/bash

# Exit on any error
set -e

echo "--- BUILDING PROJECT ---"

# Install dependencies
echo "Installing pip dependencies..."
python3 -m pip install -r requirements.txt

# Run Management Commands
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear

echo "Running migrations..."
python3 manage.py migrate --noinput

echo "--- BUILD COMPLETE ---"

