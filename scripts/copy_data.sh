#!/bin/bash
# Copy generated retrograde data to public folder

# Check if the JSON file exists
if [ -f "data/retrograde_periods.json" ]; then
    echo "Copying retrograde_periods.json to public folder..."
    cp data/retrograde_periods.json public/
    echo "Data copied successfully!"
elif [ -f "data/retrograde_periods.json.gz" ]; then
    echo "Found compressed data. Decompressing and copying..."
    gunzip -c data/retrograde_periods.json.gz > public/retrograde_periods.json
    echo "Data decompressed and copied successfully!"
else
    echo "Error: No retrograde data file found in data/"
    echo "Please run the retrograde calculator first."
    exit 1
fi

# Check file size
if [ -f "public/retrograde_periods.json" ]; then
    SIZE=$(ls -lh public/retrograde_periods.json | awk '{print $5}')
    echo "File size: $SIZE"
fi