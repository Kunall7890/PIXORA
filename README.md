# 🎨 Pixora - AI Product Creative Generation Engine

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Pixora is an **AI-powered creative generation workflow** for e-commerce brands. It automatically generates:
- 🖼️ **5 Product Marketing Images** (AI-generated with Stable Diffusion)
- 🎬 **2 Short Product Videos** (AI-generated with CogVideoX)
- 💡 **Creative Strategy** (AI-analyzed market positioning)
- ✅ **Quality Reviews** (AI-powered hallucination & brand checks)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                            │
│                  (Streamlit UI + React SPA)                     │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/REST
┌────────────────────────┴────────────────────────────────────────┐
│                      FastAPI Backend                             │
│         /generate  /bulk-generate  /job/{id}                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼────────┐  ┌───▼────────┐  ┌──▼──────────┐
│  Task Queue    │  │ Job Store  │  │ File Store  │
│  (Celery/      │  │ (Redis)    │  │ (S3/Local)  │
│   AsyncIO)     │  │            │  │             │
└────────────────┘  └────────────┘  └─────────────┘
        │
┌───────▼────────────────────────────────────────────────────────┐
│                    Agent Orchestration                           │
│                     (LangGraph State)                            │
└───────┬────────────────────────────────────────────────────────┘
        │
   ┌────┴─────────┬─────────────┬──────────────┬─────────┐
   │              │             │              │         │
┌──▼──┐    ┌──────▼──┐   ┌─────▼─────┐  ┌──────▼──┐  ┌─▼────┐
│ 1️⃣  │    │   2️⃣    │   │    3️⃣     │  │   4️⃣   │  │  5️⃣  │
│Prod │    │Creative │   │  Prompt   │  │ Image  │  │Video │
│Rsch │    │Strategy │   │   Gen     │  │ Gen    │  │ Gen  │
└──┬──┘    └──┬──────┘   └──┬────────┘  └──┬─────┘  └──┬───┘
   │          │            │              │          │
   └──────────┴────────────┴──────────────┴──────────┘
              │
        ┌─────▼──────────┐
        │    6️⃣ Critic   │
        │    Agent       │
        └─────┬──────────┘
              │
        ┌─────▼──────────────────┐
        │   7️⃣ Output Assembly   │
        │   (Images+Videos+Meta) │
        └────────────────────────┘
```

---

## 🚀 Quick Start

### Step 1: Clone & Setup

```bash
# Clone repository
git clone https://github.com/yourusername/pixora.git
cd pixora

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure API Keys

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your editor
```

**Required API Keys:**
- **Groq API** (Free): https://console.groq.com
  - Get free API key (Llama 3.3 70B included)
  - Paste in `GROQ_API_KEY`

- **Replicate** (Optional for video): https://replicate.com
  - Sign up free, paste token in `REPLICATE_API_TOKEN`

### Step 3: Run Backend

```bash
# Terminal 1: Start FastAPI backend
python -m api.main

# Output should show:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# ✓ Groq API: Configured
```

### Step 4: Run Frontend (Optional)

```bash
# Terminal 2: Start Streamlit UI
streamlit run frontend/app.py

# Open browser: http://localhost:8501
```

### Step 5: Test the System

```bash
# Terminal 3: Test API
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/product",
    "brand_override": "YourBrand"
  }'
```

---

## 📋 7-Agent Workflow Explained

### 1️⃣ **Product Research Agent**
- **Input**: E-commerce product URL
- **Process**: Web scraping + HTML parsing (Playwright + BeautifulSoup)
- **Output**: Structured product data (title, features, specs, price, reviews)
- **Tech**: Playwright, BeautifulSoup4

```python
product_data = {
    "title": "Premium Wireless Headphones",
    "price": 199.99,
    "features": ["Active Noise Cancellation", "40hr Battery", "Premium Sound"],
    "specs": {"Driver": "40mm", "Freq": "20Hz-20kHz"},
    "rating": 4.8,
    "image_urls": [...]
}
```

### 2️⃣ **Creative Strategy Agent**
- **Input**: Product data
- **Process**: LLM analysis (Groq Llama 3.3 70B)
- **Output**: Creative brief with hooks, audience, themes, captions
- **Tech**: Groq API

```python
creative_brief = {
    "hooks": ["Hear. Feel. Experience.", "Premium Audio Redefined"],
    "target_audience": "Tech-savvy professionals, 25-45 years",
    "visual_themes": ["Modern minimalist", "Lifestyle luxury"],
    "color_palette": ["#1a1a1a", "#00d4ff", "#ffffff"],
    "marketing_angles": ["Superior sound quality", "All-day comfort"]
}
```

### 3️⃣ **Prompt Generation Agent**
- **Input**: Product data + creative brief
- **Process**: LLM creates optimized prompts for image/video models
- **Output**: 5 image prompts + 2 video scripts
- **Tech**: Groq API (prompt engineering)

```python
prompts = {
    "image_prompts": [
        "Premium headphones on black minimalist desk, professional photography, soft lighting",
        "Lifestyle shot: person wearing headphones, outdoor urban setting, golden hour"
        # ... 3 more
    ],
    "video_scripts": [
        "[Hook] Tired of average sound? [Product showcase] Meet true audio quality",
        # ... 1 more
    ]
}
```

### 4️⃣ **Image Generation Workflow**
- **Input**: 5 image prompts
- **Process**: Stable Diffusion XL (local or via API)
- **Output**: 5 high-quality product images
- **Tech**: HuggingFace Diffusers (SDXL-Turbo) or Together AI

```python
images = [
    {
        "id": "img_12ab",
        "prompt": "...",
        "url": "/outputs/images/product_12ab.png",
        "quality_score": 0.87
    },
    # ... 4 more
]
```

### 5️⃣ **Video Generation Workflow**
- **Input**: 2 video scripts
- **Process**: CogVideoX (via Replicate or local)
- **Output**: 2 short (8-15 sec) product videos
- **Tech**: CogVideoX via Replicate or RunPod

```python
videos = [
    {
        "id": "vid_abc1",
        "script": "...",
        "url": "/outputs/videos/product_abc1.mp4",
        "duration": 8.5,
        "quality_score": 0.82
    },
    # ... 1 more
]
```

### 6️⃣ **Critic/Review Agent**
- **Input**: Generated images, videos, prompts
- **Process**: LLM quality evaluation
- **Output**: Quality scores + improvement suggestions
- **Tech**: Groq API

Checks:
- ✓ Hallucination detection (false claims)
- ✓ Consistency with strategy
- ✓ Brand alignment
- ✓ Overall quality score

```python
critic_review = {
    "hallucination_score": 0.92,  # 0-1, how truthful
    "consistency_score": 0.88,    # 0-1, matches strategy
    "branding_score": 0.91,       # 0-1, brand voice
    "overall_quality": 0.90,
    "approved": true,
    "issues": [],
    "suggestions": ["Add more lifestyle context in image 3"]
}
```

### 7️⃣ **Bulk Processing Layer**
- **Input**: CSV file with multiple URLs
- **Process**: Async job queue + tracking
- **Output**: Job ID + progress tracking + batch results
- **Tech**: Celery + Redis (or AsyncIO)

```python
# CSV input
url,brand_override,custom_themes
https://product1.com,Brand1,modern;minimalist
https://product2.com,Brand2,luxury;elegant

# Response
{
    "job_id": "batch_xyz123",
    "status": "processing",
    "total_urls": 2,
    "processed_urls": 1,
    "progress": 50
}
```

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit + React | UI for testing & deployment |
| **Backend API** | FastAPI + Uvicorn | REST endpoints |
| **Orchestration** | LangGraph | Agent state management |
| **LLM Models** | Groq API (Llama 3.3 70B) | Text/strategy generation |
| **Image Generation** | Stable Diffusion XL | Product image creation |
| **Video Generation** | CogVideoX (Replicate) | Short video creation |
| **Web Scraping** | Playwright + BeautifulSoup | Product data extraction |
| **Task Queue** | Celery + Redis | Async bulk processing |
| **Storage** | Local filesystem / S3 | Image & video storage |

---

## 📊 API Endpoints

### Single Product Generation

```http
POST /api/v1/generate
Content-Type: application/json

{
    "url": "https://example.com/product",
    "brand_override": "Your Brand",
    "target_audience": "Tech enthusiasts",
    "custom_themes": ["modern", "minimalist"]
}
```

**Response:**
```json
{
    "product_data": {...},
    "creative_brief": {...},
    "prompts": {...},
    "images": [{...}, {...}, ...],
    "videos": [{...}, {...}],
    "critic_review": {...},
    "total_processing_time": 145.2,
    "status": "success"
}
```

### Bulk Processing

```http
POST /api/v1/bulk-generate
Content-Type: multipart/form-data

[CSV file upload]
```

**Response:**
```json
{
    "job_id": "batch_abc123",
    "status": "queued",
    "total_urls": 50,
    "message": "Batch processing started"
}
```

### Job Status

```http
GET /api/v1/bulk-job/{job_id}
```

---

## 📁 Project Structure

```
pixora/
├── agents/
│   ├── research_agent.py           # Product research (scraping)
│   ├── strategy_agent.py           # Creative strategy generation
│   ├── prompt_generation_agent.py  # Prompt engineering
│   └── critic_agent.py             # Quality review
├── generation/
│   ├── image_generator.py          # Image generation (SDXL)
│   └── video_generator.py          # Video generation (CogVideoX)
├── orchestration/
│   └── workflow.py                 # LangGraph orchestration
├── api/
│   ├── main.py                     # FastAPI app
│   └── models.py                   # Pydantic schemas
├── frontend/
│   └── app.py                      # Streamlit UI
├── outputs/
│   ├── images/                     # Generated images
│   └── videos/                     # Generated videos
├── config.py                       # Configuration
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
└── README.md                       # This file
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# API Keys
GROQ_API_KEY=xxx                    # Required
REPLICATE_API_TOKEN=xxx             # Optional (for video)
TOGETHER_AI_API_KEY=xxx             # Optional (for images)

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# App Settings
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
```

### Quality Thresholds

Edit in `config.py`:
```python
HALLUCINATION_THRESHOLD = 0.70      # Min truthfulness
CONSISTENCY_THRESHOLD = 0.75        # Min consistency
BRANDING_THRESHOLD = 0.80           # Min brand alignment
```

---

## 💡 Usage Examples

### Example 1: Generate Creatives for Single Product

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/generate",
    json={
        "url": "https://amazon.com/dp/B08234XKMP",
        "brand_override": "TechBrand"
    }
)

result = response.json()
print(f"Images generated: {len(result['images'])}")
print(f"Videos generated: {len(result['videos'])}")
print(f"Quality score: {result['critic_review']['overall_quality']:.0%}")
```

### Example 2: Bulk Processing

```python
# Create CSV file
csv_content = """url,brand_override
https://product1.com,Brand1
https://product2.com,Brand2
https://product3.com,Brand3"""

# Upload
files = {"file": ("products.csv", csv_content)}
response = requests.post(
    "http://localhost:8000/api/v1/bulk-generate",
    files=files
)

job_id = response.json()["job_id"]
print(f"Batch job started: {job_id}")

# Poll status
import time
while True:
    status = requests.get(
        f"http://localhost:8000/api/v1/bulk-job/{job_id}"
    ).json()
    
    print(f"Progress: {status['progress']}%")
    if status['status'] in ['completed', 'failed']:
        break
    time.sleep(5)
```

---

## 🧪 Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test single product
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/product"}'

# View API docs
# Open http://localhost:8000/docs in browser
```

---

## 🚢 Deployment Options

### Option 1: Docker (Production)

```bash
# Build image
docker build -t pixora:latest .

# Run container
docker run -p 8000:8000 \
  -e GROQ_API_KEY=xxx \
  -e REPLICATE_API_TOKEN=xxx \
  pixora:latest
```

### Option 2: Vercel / Railway (Serverless)

```bash
# Deploy Streamlit app to Streamlit Cloud
# Deploy FastAPI to Railway/Vercel

# In streamlit.toml:
[server]
headless = true
```

### Option 3: AWS EC2 / Google Cloud

```bash
# Install on Ubuntu
sudo apt update && apt install python3-pip
pip install -r requirements.txt
python -m api.main
```

---

## 📈 Performance Metrics

| Component | Time | Status |
|-----------|------|--------|
| Product Research | 5-10s | Fast (Playwright) |
| Creative Strategy | 3-5s | Fast (Groq) |
| Prompt Generation | 2-3s | Very Fast |
| Image Generation (×5) | 60-120s | Medium (SDXL) |
| Video Generation (×2) | 30-60s | Medium (CogVideoX) |
| Critic Review | 3-5s | Fast |
| **Total Workflow** | **2-5 min** | ✓ Acceptable |

---

## 🔒 Security Considerations

- ✓ API keys never logged
- ✓ Rate limiting on endpoints
- ✓ Input validation (URLs, CSV)
- ✓ File upload size limits
- ✓ CORS enabled for frontend
- ✓ Environment variables for secrets

---

## 🐛 Troubleshooting

### Error: "Groq API key not configured"
```bash
# Make sure .env has GROQ_API_KEY set
echo "GROQ_API_KEY=your_key" >> .env
```

### Error: "Cannot connect to localhost:8000"
```bash
# Backend not running. Start it:
python -m api.main
```

### Images not generating locally
```bash
# SDXL requires CUDA. Use Together AI instead:
# Set TOGETHER_AI_API_KEY in .env
```

### Slow performance
- Increase quality thresholds in config.py
- Use GPU for image generation
- Switch to faster LLM model (Groq already optimized)

---

## 📝 Future Roadmap

- [ ] Vector search for similar products
- [ ] A/B testing framework
- [ ] Advanced video editing (transitions, music)
- [ ] Multi-language support
- [ ] Facebook/Instagram direct integration
- [ ] Analytics dashboard
- [ ] Custom model fine-tuning

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -am 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

---

## 👋 Support

- 📧 Email: support@pixora.dev
- 💬 Discord: [Join Community](https://discord.gg/pixora)
- 🐙 GitHub Issues: [Report Bug](https://github.com/yourusername/pixora/issues)

---

**Made with ❤️ for E-commerce Brands** | Pixora v1.0 | 2024
#   P I X O R A  
 