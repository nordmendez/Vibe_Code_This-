#!/usr/bin/env bash

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Checking and installing requirements..."
pip install --upgrade pip
pip install PyQt6

# Run the application
echo "Starting Vibe_Code-This..."
python Python/Files/main.py
