#!/bin/bash

# Clone the repository
git clone https://github.com/chiril-covali/gotomeeting-mp4-api.git temp_repo
cd temp_repo

# Remove all existing files except .git
rm -rf *

# Copy new files
cp ../app.py .
cp ../requirements.txt .
cp ../gunicorn_config.py .
cp ../Dockerfile .
cp ../README.md .
cp -r ../templates .

# Configure git
git config user.name "chiril-covali"
git config user.email "chiril.covali@gmail.com"

# Add all files
git add .

# Commit changes
git commit -m "Update application with new version"

# Push changes
git push origin main

# Clean up
cd ..
rm -rf temp_repo 