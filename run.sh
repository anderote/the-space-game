#!/bin/bash
# Space Game Clone - Panda3D Edition Runner Script

echo "🚀 Starting Space Game Clone - Panda3D Edition"
echo "=============================================="

# Check if virtual environment exists
if [ ! -d "panda3d_env" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   python3 -m venv panda3d_env"
    echo "   panda3d_env/bin/pip install -r panda3d_requirements.txt"
    exit 1
fi

# Run the game using the virtual environment
echo "🎮 Launching game..."
panda3d_env/bin/python main.py 