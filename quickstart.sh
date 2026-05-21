#!/bin/bash
# Pixora Quick Start Script

set -e

echo "🎨 Pixora Creative Engine - Quick Start"
echo "========================================"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✓ Virtual environment exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt

# Setup environment
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys:"
    echo "   - GROQ_API_KEY (required)"
    echo "   - REPLICATE_API_TOKEN (optional)"
else
    echo "✓ .env file exists"
fi

# Create required directories
echo "📁 Creating directories..."
mkdir -p outputs/images outputs/videos logs

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Next steps:"
echo ""
echo "1. Edit .env and add your Groq API key:"
echo "   nano .env"
echo ""
echo "2. Start the backend (Terminal 1):"
echo "   python -m api.main"
echo ""
echo "3. Start the frontend (Terminal 2):"
echo "   streamlit run frontend/app.py"
echo ""
echo "4. Open browser:"
echo "   http://localhost:8501"
echo ""
echo "📖 Documentation: README.md"
