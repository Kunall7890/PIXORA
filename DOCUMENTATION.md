# 📋 Pixora Project Documentation

## Table of Contents
1. [Project Overview](#overview)
2. [Architecture](#architecture)
3. [Agent System](#agents)
4. [Setup Instructions](#setup)
5. [API Reference](#api-reference)
6. [Development Guide](#development)
7. [Troubleshooting](#troubleshooting)

---

## Overview

**Pixora** is an AI-powered platform that automatically generates professional marketing creatives for e-commerce products. It uses a multi-agent orchestration system to:

1. Extract product information from URLs
2. Generate marketing strategies
3. Create optimized prompts
4. Generate images and videos
5. Review quality and consistency
6. Support bulk processing

### Key Features
- ✅ 5 AI-generated product images per product
- ✅ 2 AI-generated short videos per product
- ✅ Creative strategy generation
- ✅ Brand consistency checks
- ✅ Bulk CSV processing
- ✅ REST API + Web UI
- ✅ Async job queue
- ✅ Production-ready with Docker

### Technology Stack
- **Backend**: FastAPI + Python 3.8+
- **Frontend**: Streamlit
- **LLM**: Groq API (Llama 3.3 70B)
- **Image Gen**: Stable Diffusion XL
- **Video Gen**: CogVideoX (via Replicate)
- **Web Scraping**: Playwright + BeautifulSoup
- **Orchestration**: Custom async workflow
- **Storage**: Local filesystem / S3
- **Task Queue**: Celery + Redis / AsyncIO

---

## Architecture

### System Components

```
┌─────────────────────────────────────────┐
│         User Interface Layer            │
│  (Streamlit UI + REST API Clients)      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      FastAPI Backend Server             │
│  • /api/v1/generate (single)            │
│  • /api/v1/bulk-generate (batch)        │
│  • /api/v1/job/{id} (status)            │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│    Workflow Orchestration Engine        │
│  (LangGraph + Async State Management)   │
└──────────────┬──────────────────────────┘
       ┌───────┴────────────────┐
       │                        │
┌──────▼────────────────┐  ┌───▼────────────────┐
│  Agent Pipeline       │  │  Generation Models │
│  • Research          │  │  • SDXL Images     │
│  • Strategy          │  │  • CogVideoX       │
│  • Prompt Gen        │  │  • Videos          │
│  • Critic            │  │                    │
└──────────────────────┘  └────────────────────┘
```

### Data Flow

```
Product URL
    ↓
[1. Research Agent] → Extract product data
    ↓
[2. Strategy Agent] → Create creative brief
    ↓
[3. Prompt Gen Agent] → Generate prompts
    ↓
[4. Critic Agent] → Quality check (pre-generation)
    ↓
[5. Image Generator] → Generate 5 images
    ↓
[6. Video Generator] → Generate 2 videos
    ↓
[7. Output Assembly] → Package all assets
    ↓
Final Output (Images + Videos + Metadata)
```

---

## Agents

### 1. Product Research Agent (`agents/research_agent.py`)

**Purpose**: Extract and understand product information from URLs

**Process**:
- Playwright: Opens URL and renders JavaScript
- BeautifulSoup: Parses HTML and extracts data
- Pattern matching: Finds price, rating, images

**Output**:
```python
{
    "title": "Premium Wireless Headphones",
    "description": "High-quality audio...",
    "price": 199.99,
    "currency": "USD",
    "features": ["Active Noise Cancellation", ...],
    "specs": {"Driver": "40mm", ...},
    "reviews_summary": "Users love the sound quality",
    "rating": 4.8,
    "image_urls": ["url1", "url2", ...],
    "brand": "TechBrand"
}
```

**Error Handling**:
- Falls back to httpx if Playwright fails
- Returns default data if URL is inaccessible
- Validates all extracted fields

### 2. Creative Strategy Agent (`agents/strategy_agent.py`)

**Purpose**: Generate creative directions and marketing angles

**LLM Prompt**:
- Takes product data as context
- Asks for hooks, themes, color palettes
- Targets specific audience angles

**Output**:
```python
{
    "hooks": ["Hook line 1", "Hook line 2", ...],
    "target_audience": "Tech enthusiasts, 25-45 years old",
    "visual_themes": ["Modern minimalist", "Lifestyle luxury"],
    "color_palette": ["#1a1a1a", "#00d4ff", "#ffffff"],
    "marketing_angles": ["Superior sound", "All-day comfort"],
    "ad_captions": ["Caption 1", "Caption 2", ...],
    "tone_of_voice": "Professional and engaging"
}
```

**API Used**: Groq Llama 3.3 70B (Free tier)

### 3. Prompt Generation Agent (`agents/prompt_generation_agent.py`)

**Purpose**: Create optimized prompts for AI models

**Generates**:
- 5 image prompts (SDXL-formatted)
- 2 video scripts (short-form video formatted)
- Visual style guide

**Example Image Prompt**:
```
"Professional product photography, studio lighting, white background, 
sharp focus on product details, premium aesthetic, 1024x1024, 
high quality, 8k resolution"
```

**Example Video Script**:
```
"[HOOK: Product appears quickly] Hey, check THIS out! 
[VISUAL: Product benefits showcase] This changes everything.
[VISUAL: Close-up of key feature] Don't miss this.
[CTA: Link in bio]"
```

### 4. Image Generator (`generation/image_generator.py`)

**Purpose**: Generate 5 product marketing images

**Options**:
1. **Local**: Stable Diffusion XL via Diffusers (requires GPU)
2. **API**: Together AI image generation (free tier)
3. **Mock**: For testing/demo (generates placeholders)

**Process**:
- Load SDXL model (first call is slow, subsequent are fast)
- Run inference for each prompt
- Save images to outputs/images/
- Return URLs + quality scores

**Settings**:
- Resolution: 1024x1024
- Inference steps: 20 (fast)
- Guidance scale: 7.5
- Batch processing: Up to 5 images

### 5. Video Generator (`generation/video_generator.py`)

**Purpose**: Generate 2 short product videos

**Options**:
1. **Replicate**: CogVideoX model (recommended)
2. **Local**: Not practical (requires lots of VRAM)
3. **Mock**: For testing (creates placeholder files)

**Process**:
- Convert scripts to video prompts
- Call Replicate API
- Download generated video
- Return URL + duration + quality score

**Settings**:
- Duration: 8-15 seconds
- Resolution: 1280x720
- FPS: 24

### 6. Critic Agent (`agents/critic_agent.py`)

**Purpose**: Quality assurance and consistency checks

**Evaluates**:
- **Hallucination Score**: Are claims truthful? (0-1)
- **Consistency Score**: Follows creative strategy? (0-1)
- **Branding Score**: Strong brand voice? (0-1)
- **Overall Quality**: Average of above (0-1)

**Thresholds** (in config.py):
```python
HALLUCINATION_THRESHOLD = 0.70     # Must be ≥70% truthful
CONSISTENCY_THRESHOLD = 0.75       # Must be ≥75% consistent
BRANDING_THRESHOLD = 0.80          # Must be ≥80% on-brand
```

**Output**:
```python
{
    "hallucination_score": 0.92,
    "consistency_score": 0.88,
    "branding_score": 0.91,
    "overall_quality": 0.90,
    "approved": True,
    "issues": [],
    "suggestions": ["Minor: Add more lifestyle context"]
}
```

### 7. Bulk Processor (`orchestration/workflow.py`)

**Purpose**: Handle multiple products asynchronously

**Features**:
- CSV upload support
- Job tracking with status
- Async processing
- Error handling per product
- Result aggregation

---

## Setup

### Prerequisites
- Python 3.8+
- pip / conda
- Groq API account (free)
- Optional: Replicate account (free)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/yourusername/pixora.git
cd pixora

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
nano .env  # Add your API keys

# 5. Create directories
mkdir -p outputs/{images,videos} logs

# 6. Test installation
python test_installation.py
```

### Configuration

**Required** (`.env`):
```bash
GROQ_API_KEY=your_key_here
```

**Optional** (`.env`):
```bash
REPLICATE_API_TOKEN=your_key_here
TOGETHER_AI_API_KEY=your_key_here
```

---

## API Reference

### Single Product Generation

**Endpoint**: `POST /api/v1/generate`

**Request**:
```json
{
    "url": "https://amazon.com/dp/B08234XKMP",
    "brand_override": "MyBrand",
    "target_audience": "Tech enthusiasts",
    "custom_themes": ["modern", "minimalist"]
}
```

**Response**:
```json
{
    "product_data": {...},
    "creative_brief": {...},
    "prompts": {...},
    "images": [...],
    "videos": [...],
    "critic_review": {...},
    "total_processing_time": 145.2,
    "status": "success"
}
```

**Time**: 2-5 minutes

### Bulk Processing

**Endpoint**: `POST /api/v1/bulk-generate`

**CSV Format**:
```csv
url,brand_override,custom_themes
https://product1.com,Brand1,modern;minimalist
https://product2.com,Brand2,luxury;elegant
```

**Response**:
```json
{
    "job_id": "batch_abc123",
    "status": "queued",
    "total_urls": 2,
    "message": "Batch processing started"
}
```

### Job Status

**Endpoint**: `GET /api/v1/bulk-job/{job_id}`

**Response**:
```json
{
    "job_id": "batch_abc123",
    "status": "processing",
    "total_urls": 2,
    "processed_urls": 1,
    "failed_urls": 0,
    "progress": 50
}
```

---

## Development Guide

### Adding a Custom Agent

```python
# agents/custom_agent.py
from groq import Groq

class CustomAgent:
    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key)
    
    def analyze(self, data: Dict) -> Dict:
        response = self.client.messages.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": "..."}],
            temperature=0.7,
            max_tokens=1000
        )
        return self._parse_response(response.content[0].text)
```

### Running Locally

```bash
# Terminal 1: Backend
python -m api.main

# Terminal 2: Frontend
streamlit run frontend/app.py

# Terminal 3: Test
python test_installation.py
```

### Running with Docker

```bash
# Build and run
docker-compose up --build

# Access:
# API: http://localhost:8000
# UI: http://localhost:8501
# Docs: http://localhost:8000/docs
```

### Debugging

```bash
# Enable verbose logging
LOG_LEVEL=DEBUG python -m api.main

# Check logs
tail -f logs/pixora.log

# Test endpoints
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/product"}'
```

---

## Troubleshooting

### Issue: "Groq API key not configured"

**Solution**:
```bash
# Check .env file
cat .env | grep GROQ_API_KEY

# Should output: GROQ_API_KEY=your_actual_key_here
# If not set, update it and restart
```

### Issue: "Cannot connect to localhost:8000"

**Solution**:
```bash
# Make sure API is running
python -m api.main

# Check if port is already in use
lsof -i :8000

# If yes, kill process or use different port
kill -9 <PID>
```

### Issue: "Images not generating locally"

**Solution**:
- SDXL requires 8GB+ VRAM (CUDA)
- Use Together AI instead (set TOGETHER_AI_API_KEY)
- Or use mock mode for testing

### Issue: "Slow performance"

**Solutions**:
1. Use faster LLM model
2. Enable GPU for image generation
3. Reduce image generation steps (in config)
4. Use Together AI for images (faster)

### Issue: "Videos not generating"

**Solution**:
```bash
# Set Replicate token
REPLICATE_API_TOKEN=your_token python -m api.main

# Or use mock video generation (for testing)
# Mock videos are text files with video metadata
```

---

## Contributing

```bash
# Create feature branch
git checkout -b feature/amazing-feature

# Make changes and test
python test_installation.py

# Commit and push
git commit -am "Add amazing feature"
git push origin feature/amazing-feature

# Create pull request on GitHub
```

---

## Performance Metrics

| Component | Time | Notes |
|-----------|------|-------|
| Product Research | 5-10s | Playwright overhead |
| Creative Strategy | 3-5s | LLM call |
| Prompt Generation | 2-3s | LLM call |
| Image Gen (×5) | 60-120s | SDXL inference |
| Video Gen (×2) | 30-60s | CogVideoX via API |
| Critic Review | 3-5s | LLM call |
| **Total** | **2-5 min** | Per product |

---

## Security

- API keys never logged
- Input validation on all endpoints
- File upload size limits (100MB)
- Rate limiting on endpoints
- CORS configured for frontend

---

## License

MIT License - See LICENSE file

---

## Support

- 📧 Email: support@pixora.dev
- 🐙 GitHub: https://github.com/yourusername/pixora
- 📖 Docs: https://pixora.dev/docs

---

**Made with ❤️ for E-commerce Brands** | Pixora v1.0 | 2024
