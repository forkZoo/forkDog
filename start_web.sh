#!/bin/bash

# ForkDog Web Interface Launcher

echo "🐵 Starting ForkDog Web Interface..."
echo ""

# Check if dog exists
if [ ! -f "dog_data/dna.json" ]; then
    echo "⚠️  No dog found! Initializing..."
    python src/cli.py init
    echo ""
fi

# Start web server
echo "🚀 Starting web server..."
python web/serve.py
