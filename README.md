<div align="center">

# 🎨 Pixora

### AI-Powered Creative Generation Engine for E-Commerce Brands

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-FF6B35?style=flat-square)](https://langchain-ai.github.io/langgraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-F7DC6F?style=flat-square)](LICENSE)

**Pixora** turns any e-commerce product URL into a full creative package — images, videos, strategy, and quality reviews — in under 5 minutes.

[Quick Start](#-quick-start) · [Architecture](#-architecture) · [API Docs](#-api-reference) · [Deployment](#-deployment) · [Contributing](#-contributing)

</div>

---

## ✨ What Pixora Does

Given a product URL, Pixora's 7-agent pipeline automatically produces:

| Output | Details |
|--------|---------|
| 🖼️ **5 Marketing Images** | AI-generated via Stable Diffusion XL |
| 🎬 **2 Short Videos** | 8–15 second clips via CogVideoX |
| 💡 **Creative Strategy** | Hooks, audience targeting, visual themes |
| ✅ **Quality Review** | Hallucination detection + brand alignment scores |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     Frontend Layer                        │
│              Streamlit UI  ·  React SPA                  │
└──────────────────────────┬───────────────────────────────┘
                           │ HTTP / REST
┌──────────────────────────▼───────────────────────────────┐
│                    FastAPI Backend                         │
│        /generate  ·  /bulk-generate  ·  /job/{id}        │
└────────────┬─────────────┬───────────────┬───────────────┘
             │             │               │
      ┌──────▼───┐   ┌─────▼────┐   ┌─────▼────┐
      │  Celery  │   │  Redis   │   │  Storage │
      │  Queue   │   │  Store   │   │ S3/Local │
      └──────┬───┘   └──────────┘   └──────────┘
             │
┌────────────▼─────────────────────────────────────────────┐
│                 LangGraph Orchestration                    │
└──────┬──────────┬──────────┬──────────┬──────────┬───────┘
       │          │          │          │          │
  ┌────▼───┐ ┌───▼────┐ ┌───▼────┐ ┌───▼────┐ ┌───▼────┐
  │  1     │ │  2     │ │  3     │ │  4     │ │  5     │
  │Product │ │Creative│ │Prompt  │ │ Image  │ │ Video  │
  │Research│ │Strategy│ │  Gen   │ │  Gen   │ │  Gen   │
  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘
                               │
                      ┌────────▼────────┐
                      │   6  Critic     │
                      │     Agent       │
                      └────────┬────────┘
                               │
                      ┌────────▼────────┐
                      │  7  Assemble    │
                      │    Output       │
                      └─────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Redis (for bulk processing)
- CUDA GPU (optional, for local image generation)

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/pixora.git
cd pixora

python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Open `.env` and fill in your keys:

```bash
# Required
GROQ_API_KEY=your_groq_key           # Free at console.groq.com

# Optional
REPLICATE_API_TOKEN=your_token       # For video generation
TOGETHER_AI_API_KEY=your_key         # For cloud image generation

# Infrastructure
REDIS_HOST=localhost
REDIS_PORT=6379
```

> **Getting API keys:**
> - **Groq** (free, required): [console.groq.com](https://console.groq.com) — includes Llama 3.3 70B
> - **Replicate** (optional, for video): [replicate.com](https://replicate.com)
> - **Together AI** (optional, for images without GPU): [together.ai](https://together.ai)

### 3. Start the Backend

```bash
python -m api.main
# → Uvicorn running on http://0.0.0.0:8000
# → ✓ Groq API: Configured
```

### 4. Start the Frontend (Optional)

```bash
streamlit run frontend/app.py
# → Open http://localhost:8501
```

### 5. Generate Your First Creative

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/product",
    "brand_override": "YourBrand"
  }'
```

---

## 🤖 The 7-Agent Pipeline

### 1️⃣ Product Research Agent

Scrapes and structures product data from any e-commerce URL.

- **Tech:** Playwright + BeautifulSoup4
- **Time:** 5–10 seconds

```python
{
    "title": "Premium Wireless Headphones",
    "price": 199.99,
    "features": ["Active Noise Cancellation", "40hr Battery"],
    "specs": {"Driver": "40mm", "Freq": "20Hz–20kHz"},
    "rating": 4.8
}
```

---

### 2️⃣ Creative Strategy Agent

Analyzes product data and generates a full creative brief using LLM reasoning.

- **Tech:** Groq API (Llama 3.3 70B)
- **Time:** 3–5 seconds

```python
{
    "hooks": ["Hear. Feel. Experience.", "Premium Audio Redefined"],
    "target_audience": "Tech-savvy professionals, 25–45",
    "visual_themes": ["Modern minimalist", "Lifestyle luxury"],
    "color_palette": ["#1a1a1a", "#00d4ff", "#ffffff"]
}
```

---

### 3️⃣ Prompt Generation Agent

Translates the creative brief into optimized prompts for image and video models.

- **Tech:** Groq API (prompt engineering)
- **Time:** 2–3 seconds
- **Output:** 5 image prompts + 2 video scripts

---

### 4️⃣ Image Generation

Generates five high-quality product images in parallel.

- **Tech:** Stable Diffusion XL (local) or Together AI (cloud)
- **Time:** 60–120 seconds

```python
{
    "id": "img_12ab",
    "url": "/outputs/images/product_12ab.png",
    "quality_score": 0.87
}
```

---

### 5️⃣ Video Generation

Produces two short product videos (8–15 seconds each).

- **Tech:** CogVideoX via Replicate or RunPod
- **Time:** 30–60 seconds

```python
{
    "id": "vid_abc1",
    "url": "/outputs/videos/product_abc1.mp4",
    "duration": 8.5,
    "quality_score": 0.82
}
```

---

### 6️⃣ Critic / Review Agent

Evaluates all generated content before delivery.

- **Tech:** Groq API
- **Time:** 3–5 seconds

Checks performed:

| Check | Description |
|-------|-------------|
| 🔍 Hallucination Detection | Are all claims factually grounded in product data? |
| 🎯 Strategy Consistency | Does the creative match the brief? |
| 🏷️ Brand Alignment | Does it reflect the correct brand voice? |
| ⭐ Overall Quality | Composite score across all dimensions |

```python
{
    "hallucination_score": 0.92,
    "consistency_score": 0.88,
    "branding_score": 0.91,
    "overall_quality": 0.90,
    "approved": true,
    "suggestions": ["Add more lifestyle context in image 3"]
}
```

---

### 7️⃣ Bulk Processing Layer

Handles CSV-based batch jobs with async tracking.

- **Tech:** Celery + Redis (or AsyncIO)
- **Input:** CSV with `url`, `brand_override`, `custom_themes` columns

```bash
# Example CSV
url,brand_override,custom_themes
https://product1.com,Brand1,modern;minimalist
https://product2.com,Brand2,luxury;elegant
```

```python
# Job status response
{
    "job_id": "batch_xyz123",
    "status": "processing",
    "total_urls": 50,
    "processed": 23,
    "progress": 46
}
```

---

## 📡 API Reference

### `POST /api/v1/generate` — Single Product

```json
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
    "product_data": { "..." },
    "creative_brief": { "..." },
    "images": [ { "id": "...", "url": "...", "quality_score": 0.87 } ],
    "videos": [ { "id": "...", "url": "...", "duration": 8.5 } ],
    "critic_review": { "overall_quality": 0.90, "approved": true },
    "total_processing_time": 145.2,
    "status": "success"
}
```

---

### `POST /api/v1/bulk-generate` — Batch Processing

```bash
curl -X POST http://localhost:8000/api/v1/bulk-generate \
  -F "file=@products.csv"
```

**Response:**

```json
{
    "job_id": "batch_abc123",
    "status": "queued",
    "total_urls": 50
}
```

---

### `GET /api/v1/bulk-job/{job_id}` — Job Status

```json
{
    "job_id": "batch_abc123",
    "status": "processing",
    "progress": 72,
    "processed_urls": 36,
    "total_urls": 50
}
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit + React |
| Backend API | FastAPI + Uvicorn |
| Agent Orchestration | LangGraph |
| LLM | Groq API — Llama 3.3 70B |
| Image Generation | Stable Diffusion XL / Together AI |
| Video Generation | CogVideoX via Replicate |
| Web Scraping | Playwright + BeautifulSoup4 |
| Task Queue | Celery + Redis |
| Storage | Local filesystem / AWS S3 |

---

## 📁 Project Structure

```
pixora/
├── agents/
│   ├── research_agent.py            # Web scraping & product data
│   ├── strategy_agent.py            # Creative brief generation
│   ├── prompt_generation_agent.py   # Prompt engineering
│   └── critic_agent.py              # Quality review & scoring
├── generation/
│   ├── image_generator.py           # SDXL image pipeline
│   └── video_generator.py           # CogVideoX video pipeline
├── orchestration/
│   └── workflow.py                  # LangGraph state machine
├── api/
│   ├── main.py                      # FastAPI app & routes
│   └── models.py                    # Pydantic request/response schemas
├── frontend/
│   └── app.py                       # Streamlit UI
├── outputs/
│   ├── images/                      # Generated image files
│   └── videos/                      # Generated video files
├── config.py                        # App configuration & thresholds
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Configuration

Quality thresholds can be tuned in `config.py`:

```python
HALLUCINATION_THRESHOLD = 0.70   # Minimum factual accuracy score
CONSISTENCY_THRESHOLD   = 0.75   # Minimum strategy alignment score
BRANDING_THRESHOLD      = 0.80   # Minimum brand voice score
```

Increasing these thresholds improves output quality but may require regeneration passes.

---

## ⏱️ Performance

| Stage | Typical Duration |
|-------|----------------|
| Product Research | 5–10s |
| Creative Strategy | 3–5s |
| Prompt Generation | 2–3s |
| Image Generation (×5) | 60–120s |
| Video Generation (×2) | 30–60s |
| Critic Review | 3–5s |
| **Total** | **~2–5 minutes** |

---

## 🚢 Deployment

### Docker

```bash
docker build -t pixora:latest .

docker run -p 8000:8000 \
  -e GROQ_API_KEY=your_key \
  -e REPLICATE_API_TOKEN=your_token \
  pixora:latest
```

### Railway / Vercel

Deploy the FastAPI backend to [Railway](https://railway.app) and the Streamlit frontend to [Streamlit Cloud](https://streamlit.io/cloud). Set environment variables in each platform's dashboard.

### AWS EC2 / Google Cloud

```bash
sudo apt update && sudo apt install python3-pip -y
pip install -r requirements.txt
python -m api.main
```

---

## 🔒 Security

- API keys are stored in environment variables, never logged
- Rate limiting applied to all public endpoints
- Input validation on URLs and uploaded CSV files
- File upload size limits enforced
- CORS configured for frontend origin only

---

## 🐛 Troubleshooting

**`Groq API key not configured`**
```bash
echo "GROQ_API_KEY=your_key" >> .env
```

**`Cannot connect to localhost:8000`**
```bash
# Backend isn't running — start it first
python -m api.main
```

**Images not generating**
```
SDXL requires a CUDA GPU for local generation.
Without a GPU, set TOGETHER_AI_API_KEY in your .env to use cloud inference.
```

**Slow performance**
- Use a GPU for image generation (60–120s → ~20s)
- Groq is already the fastest available LLM API; no changes needed there
- For bulk jobs, scale Celery workers: `celery -A tasks worker --concurrency=4`

---

## 🗺️ Roadmap

- [ ] Vector search for similar product lookups
- [ ] A/B testing framework for creative variants
- [ ] Advanced video editing (transitions, background music)
- [ ] Multi-language creative generation
- [ ] Direct publishing to Facebook / Instagram Ads
- [ ] Analytics dashboard with CTR tracking
- [ ] Custom model fine-tuning on brand assets

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push and open a Pull Request

Please open an issue first for major changes so we can discuss the approach.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

Made with ❤️ for e-commerce brands · **Pixora v1.0**

[📧 Email](mailto:support@pixora.dev) · [💬 Discord](https://discord.gg/pixora) · [🐛 Report a Bug](https://github.com/yourusername/pixora/issues)

<div align="center">
