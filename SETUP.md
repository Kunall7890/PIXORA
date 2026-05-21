# 🚀 Getting Started with Pixora

This guide will get you up and running in **5 minutes**.

## ✅ Requirements

- Python 3.8+ ([Download](https://python.org))
- Groq API key - **FREE** ([Get one here](https://console.groq.com))
- 5-10 GB disk space for models
- 4GB+ RAM (8GB+ recommended)

## 📋 Step-by-Step Setup

### Step 1: Get Groq API Key (2 minutes)

1. Go to https://console.groq.com
2. Click "Sign up" (free)
3. Create account and verify email
4. Go to API Keys section
5. Copy your API key (looks like: `gsk_xxxxxx...`)
6. Keep it safe - you'll need it next

### Step 2: Clone Repository (1 minute)

```bash
# Clone the project
git clone https://github.com/yourusername/pixora.git
cd pixora

# On Windows, use Git Bash or WSL2
```

### Step 3: Create Virtual Environment (1 minute)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Dependencies (2 minutes)

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# This may take 2-3 minutes on first install
```

### Step 5: Configure Environment (30 seconds)

```bash
# Copy template
cp .env.example .env

# Edit .env and add your Groq API key
# Windows: notepad .env
# macOS/Linux: nano .env
```

**Edit `.env`:**
```bash
GROQ_API_KEY=gsk_xxxxxx...    # Paste your key here
```

Save and close.

### Step 6: Verify Installation (1 minute)

```bash
# Run test script
python test_installation.py

# Should see all ✓ marks
```

## 🎯 Quick Start

### Option A: Using the Web UI (Easiest)

```bash
# Terminal 1 - Start Backend
python -m api.main

# Wait for: "Uvicorn running on http://0.0.0.0:8000"

# Terminal 2 - Start Frontend
streamlit run frontend/app.py

# Open browser: http://localhost:8501
# You're ready to go!
```

### Option B: Using the API (For Developers)

```bash
# Terminal 1 - Start Backend
python -m api.main

# Terminal 2 - Test the API
python -c "
import requests
response = requests.post(
    'http://localhost:8000/api/v1/generate',
    json={'url': 'https://amazon.com/dp/B08234XKMP'}
)
print(response.json())
"
```

### Option C: Using Docker

```bash
# Build and run
docker-compose up --build

# Access at:
# API: http://localhost:8000
# UI: http://localhost:8501
```

## 📝 First Test

1. **Open** http://localhost:8501 (UI) or use curl
2. **Enter** any e-commerce product URL (e.g., Amazon link)
3. **Click** "Generate"
4. **Wait** 2-5 minutes
5. **View** generated images and videos

### Example Product URLs to Try

- Amazon: https://amazon.com/dp/B08234XKMP
- Any e-commerce site with product pages

## 🎨 What Happens Next?

When you click Generate:

```
1. 🔍 Product Research Agent
   → Extracts product info from URL (5-10s)

2. 💡 Creative Strategy Agent  
   → Generates marketing hooks (3-5s)

3. ✍️ Prompt Generation Agent
   → Creates image/video prompts (2-3s)

4. 🖼️ Image Generator
   → Creates 5 product images (60-120s)

5. 🎬 Video Generator
   → Creates 2 short videos (30-60s)

6. ✅ Critic Agent
   → Quality checks (3-5s)

7. 📦 Output
   → Shows all generated assets
```

## 🐛 Troubleshooting

### "ImportError: No module named 'fastapi'"

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### "ConnectionError: http://localhost:8000"

```bash
# Make sure backend is running in another terminal
# Terminal 1:
python -m api.main

# Should show: "Uvicorn running on http://0.0.0.0:8000"
```

### "API key not found"

```bash
# Check .env file exists
cat .env  # or: type .env (Windows)

# Should show: GROQ_API_KEY=gsk_...
# If not, edit .env and add your key
```

### "Out of Memory" (GPU issues)

- Use Together AI for images (set `TOGETHER_AI_API_KEY`)
- Reduce batch size
- Use mock mode for testing

## 📚 Next Steps

1. **Read** [README.md](README.md) - Full documentation
2. **Read** [DOCUMENTATION.md](DOCUMENTATION.md) - Architecture details
3. **Explore** API at http://localhost:8000/docs
4. **Try** bulk processing with CSV files
5. **Deploy** to production

## 🎯 Pro Tips

### Tip 1: Keep Terminal Open

```bash
# Don't close the "python -m api.main" terminal
# It needs to keep running for the UI to work
```

### Tip 2: Test without API Keys

```bash
# Mock mode uses placeholder images/videos
# Great for testing UI and workflow before spending time on generation
# Just comment out API keys in .env
```

### Tip 3: Use Better Product URLs

- ✅ Amazon product pages work great
- ✅ E-commerce websites work well
- ✅ Product landing pages work
- ❌ Avoid homepage URLs
- ❌ Avoid redirect URLs

### Tip 4: Monitor Progress

```bash
# In another terminal, watch the backend logs
tail -f logs/pixora.log  # macOS/Linux
```

## 💪 Advanced Setup

### Use GPU Acceleration

If you have NVIDIA GPU:

```bash
# Install CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Set in .env
USE_LOCAL_GPU=true
```

### Use Faster Video Generation

```bash
# Get Replicate API token: https://replicate.com
# Set in .env
REPLICATE_API_TOKEN=your_token_here
```

### Use Together AI (Faster Images)

```bash
# Get Together AI API key: https://www.together.ai
# Set in .env
TOGETHER_AI_API_KEY=your_key_here
```

## 📞 Still Having Issues?

1. **Check logs**: `cat logs/pixora.log`
2. **Run test**: `python test_installation.py`
3. **Read docs**: See [DOCUMENTATION.md](DOCUMENTATION.md)
4. **Open issue**: GitHub Issues

## ✨ You're All Set!

Congratulations! Pixora is ready to generate amazing marketing creatives.

**Next**: Open http://localhost:8501 and generate your first creatives! 🚀

---

**Questions?** Check [README.md](README.md) or [DOCUMENTATION.md](DOCUMENTATION.md)

**Want to contribute?** See [CONTRIBUTING.md](CONTRIBUTING.md)

---

Happy creating! 🎨
