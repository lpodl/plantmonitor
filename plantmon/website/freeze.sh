#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate plantmon
python freeze.py

cd build
mv plantmonitor-dynamic index.html

# Delete everything except 'index.html' and 'styles.css'
find . -type f -not \( -name 'index.html' -or -name 'plantmon.css' \) -delete
find . -type d -empty -delete

# copy to local plantmonito-static directory and push
cp -r index.html static ~/plantmonitor-static/
cd ~/plantmonitor-static

git add .
git commit -m "Update $(date '+%Y-%m-%d %H:%M')"
git push origin main