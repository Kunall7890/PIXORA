"""
FastAPI Backend
Main API application with endpoints for single and bulk processing
"""
import logging
import asyncio
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import List, Dict
import csv
import io
from pathlib import Path
from datetime import datetime
import uuid

# Import configuration and models
import config
from api.models import (
    ProductURLRequest, BulkProcessingRequest, WorkflowOutput,
    JobStatus, JobStatusResponse
)

# Import agents and generators
from agents.research_agent import product_researcher
from agents.product_enrichment import ProductEnrichmentAgent
from agents.strategy_agent import CreativeStrategyAgent
from agents.prompt_generation_agent import PromptGenerationAgent
from agents.critic_agent import CriticAgent
from generation.image_generator import ImageGenerator
from generation.video_generator import VideoGenerator
from orchestration.workflow import WorkflowOrchestrator

# Setup logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Pixora - AI Creative Generation",
    description="AI Product Creative Generation Workflow for E-commerce Brands",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount outputs directory for serving generated assets
app.mount("/outputs", StaticFiles(directory=str(config.OUTPUTS_DIR)), name="outputs")

# Initialize generators with config paths
image_generator = ImageGenerator(output_dir=str(config.OUTPUTS_DIR / "images"))
video_generator = VideoGenerator(
    output_dir=str(config.OUTPUTS_DIR / "videos"),
    replicate_token=config.REPLICATE_API_TOKEN or None,
)

# Initialize agents with Groq API key
strategy_agent = CreativeStrategyAgent(config.GROQ_API_KEY)
enrichment_agent = ProductEnrichmentAgent(config.GROQ_API_KEY)
prompt_agent = PromptGenerationAgent(config.GROQ_API_KEY)
critic_agent = CriticAgent(config.GROQ_API_KEY)

# Initialize orchestrator
orchestrator = WorkflowOrchestrator(
    research_agent=product_researcher,
    enrichment_agent=enrichment_agent,
    strategy_agent=strategy_agent,
    prompt_agent=prompt_agent,
    critic_agent=critic_agent,
    image_generator=image_generator,
    video_generator=video_generator
)

# Job tracking (in production, use Redis or database)
jobs = {}


# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Pixora Creative Engine",
        "engine_version": "2.2.0",
        "groq_configured": bool(config.GROQ_API_KEY),
        "groq_model": config.GROQ_MODEL,
        "timestamp": datetime.now().isoformat(),
    }


# ==================== Single Product Processing ====================

@app.post("/api/v1/generate")
async def generate_creatives(request: ProductURLRequest):
    """
    Generate marketing creatives for a single product URL
    
    Request:
        - url: Product page URL
        - brand_override: Optional brand name override
        - target_audience: Optional target audience
        - custom_themes: Optional custom visual themes
    
    Returns:
        WorkflowOutput with generated images, videos, and metadata
    """
    try:
        logger.info(f"Processing single URL: {request.url}")
        
        # Execute workflow
        result = await orchestrator.execute_workflow(
            url=str(request.url),
            brand_override=request.brand_override,
            target_audience=request.target_audience,
            custom_themes=request.custom_themes,
        )
        
        if result.get("status") == "failed":
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return result
    
    except Exception as e:
        logger.error(f"Error processing URL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/generate-async")
async def generate_creatives_async(
    request: ProductURLRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate marketing creatives asynchronously
    Returns job_id for polling status
    """
    job_id = str(uuid.uuid4())[:12]
    
    jobs[job_id] = {
        "status": "queued",
        "url": str(request.url),
        "created_at": datetime.now().isoformat(),
        "progress": 0
    }
    
    # Schedule workflow execution
    background_tasks.add_task(
        _execute_and_store,
        job_id,
        str(request.url),
        request.brand_override,
        request.target_audience,
        request.custom_themes,
    )
    
    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Processing started. Check status with job_id"
    }


@app.get("/api/v1/job/{job_id}")
async def get_job_status(job_id: str):
    """
    Get status and progress of a job
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    return JobStatusResponse(
        job_id=job_id,
        status=job.get("status", "unknown"),
        progress=job.get("progress", 0),
        processing_time=0,
        results_count=1 if job.get("status") == "completed" else 0
    )


# ==================== Bulk CSV Processing ====================

@app.post("/api/v1/bulk-generate")
async def bulk_generate(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Process multiple product URLs from CSV file
    
    CSV format:
        url,brand_override,custom_themes
        https://product1.com,Brand1,modern;minimalist
        https://product2.com,Brand2,luxury;elegant
    
    Returns:
        job_id for tracking bulk processing
    """
    try:
        # Read CSV
        content = await file.read()
        csv_file = io.StringIO(content.decode('utf-8'))
        reader = csv.DictReader(csv_file)
        
        items = []
        for row in reader:
            if row.get("url"):
                themes_raw = row.get("custom_themes", "")
                custom_themes = (
                    [t.strip() for t in themes_raw.split(";") if t.strip()]
                    if themes_raw
                    else None
                )
                items.append({
                    "url": row["url"],
                    "brand_override": row.get("brand_override") or None,
                    "target_audience": row.get("target_audience") or None,
                    "custom_themes": custom_themes,
                })

        if not items:
            raise HTTPException(status_code=400, detail="No URLs found in CSV")

        if len(items) > config.MAX_BATCH_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum batch size is {config.MAX_BATCH_SIZE}"
            )
        
        # Create job
        job_id = str(uuid.uuid4())[:12]
        
        jobs[job_id] = {
            "status": "queued",
            "total_urls": len(items),
            "processed_urls": 0,
            "failed_urls": 0,
            "results": [],
            "created_at": datetime.now().isoformat(),
            "progress": 0
        }

        # Schedule processing
        if background_tasks:
            background_tasks.add_task(
                _execute_batch_and_store,
                job_id,
                items
            )

        return {
            "job_id": job_id,
            "status": "queued",
            "total_urls": len(items),
            "message": f"Batch processing started for {len(items)} products"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing bulk upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/bulk-job/{job_id}")
async def get_bulk_job_status(job_id: str):
    """
    Get status of bulk processing job
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    return {
        "job_id": job_id,
        "status": job.get("status", "unknown"),
        "total_urls": job.get("total_urls", 0),
        "processed_urls": job.get("processed_urls", 0),
        "failed_urls": job.get("failed_urls", 0),
        "progress": job.get("progress", 0),
        "results_available": len(job.get("results", [])) > 0
    }


@app.get("/api/v1/bulk-job/{job_id}/results")
async def get_bulk_job_results(job_id: str, limit: int = 10):
    """
    Get results of bulk processing job
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    results = job.get("results", [])
    
    return {
        "job_id": job_id,
        "status": job.get("status"),
        "total_results": len(results),
        "results": results[:limit]
    }


# ==================== Download Assets ====================

@app.get("/api/v1/download/image/{image_id}")
async def download_image(image_id: str):
    """Download generated image"""
    image_path = config.OUTPUTS_DIR / "images" / f"product_{image_id}.png"
    
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(image_path, media_type="image/png")


@app.get("/api/v1/download/video/{video_id}")
async def download_video(video_id: str):
    """Download generated video"""
    video_path = config.OUTPUTS_DIR / "videos" / f"product_{video_id}.mp4"
    
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(video_path, media_type="video/mp4")


# ==================== Helper Functions ====================

async def _execute_and_store(
    job_id: str,
    url: str,
    brand_override: str = None,
    target_audience: str = None,
    custom_themes: List[str] = None,
):
    """Execute workflow and store result"""
    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 20

        result = await orchestrator.execute_workflow(
            url,
            brand_override=brand_override,
            target_audience=target_audience,
            custom_themes=custom_themes,
        )
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["result"] = result
        jobs[job_id]["completed_at"] = datetime.now().isoformat()
        
        logger.info(f"✓ Job {job_id} completed")
    
    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


async def _execute_batch_and_store(job_id: str, items: List[Dict]):
    """Execute batch workflow and store results"""
    try:
        jobs[job_id]["status"] = "processing"

        result = await orchestrator.execute_batch_workflow(items)
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["results"] = result.get("results", [])
        jobs[job_id]["processed_urls"] = result.get("processed", 0)
        jobs[job_id]["failed_urls"] = result.get("failed", 0)
        jobs[job_id]["completed_at"] = datetime.now().isoformat()
        
        logger.info(f"✓ Batch job {job_id} completed")
    
    except Exception as e:
        logger.error(f"Batch job {job_id} failed: {str(e)}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


# ==================== Startup/Shutdown ====================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("🚀 Pixora Creative Engine starting...")
    logger.info(f"Groq API: {'✓ Configured' if config.GROQ_API_KEY else '❌ Missing'}")
    logger.info(f"Output directory: {config.OUTPUTS_DIR}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Pixora Creative Engine shutting down...")


# ==================== Root Endpoint ====================

@app.get("/")
async def root():
    """Browser UI for the deployed API."""
    return HTMLResponse(
        """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Pixora Creative Engine</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #101114;
      --panel: #181a20;
      --panel-2: #20232b;
      --text: #f5f7fb;
      --muted: #9aa3b2;
      --line: #303541;
      --accent: #35d399;
      --accent-2: #4da3ff;
      --danger: #ff6b6b;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    main {
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
      padding: 32px 0;
    }
    header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 24px;
      margin-bottom: 28px;
    }
    h1 {
      margin: 0 0 8px;
      font-size: clamp(2rem, 4vw, 4rem);
      line-height: 1;
      letter-spacing: 0;
    }
    p { color: var(--muted); line-height: 1.6; }
    a { color: var(--accent-2); text-decoration: none; }
    .status {
      min-width: 180px;
      padding: 12px 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      color: var(--muted);
      font-size: 0.95rem;
    }
    .dot {
      display: inline-block;
      width: 9px;
      height: 9px;
      margin-right: 8px;
      border-radius: 50%;
      background: var(--accent);
    }
    .layout {
      display: grid;
      grid-template-columns: minmax(0, 420px) minmax(0, 1fr);
      gap: 18px;
    }
    section {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
    }
    .panel { padding: 18px; }
    label {
      display: block;
      margin: 14px 0 7px;
      color: var(--muted);
      font-size: 0.9rem;
    }
    input {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: var(--panel-2);
      color: var(--text);
      padding: 12px;
      font: inherit;
      outline: none;
    }
    input:focus { border-color: var(--accent-2); }
    button {
      width: 100%;
      margin-top: 16px;
      border: 0;
      border-radius: 7px;
      background: var(--accent);
      color: #07110d;
      padding: 12px 14px;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
    }
    button:disabled {
      opacity: 0.65;
      cursor: wait;
    }
    .links {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 16px;
    }
    .links a {
      border: 1px solid var(--line);
      border-radius: 7px;
      padding: 8px 10px;
      background: var(--panel-2);
      color: var(--text);
      font-size: 0.9rem;
    }
    .result {
      min-height: 420px;
      padding: 18px;
      overflow: auto;
    }
    .empty {
      height: 100%;
      display: grid;
      place-items: center;
      color: var(--muted);
      text-align: center;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }
    .item {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: var(--panel-2);
    }
    .item h3 { margin: 0 0 8px; font-size: 1rem; }
    ul { margin: 8px 0 0; padding-left: 20px; color: var(--muted); }
    pre {
      white-space: pre-wrap;
      word-break: break-word;
      color: var(--muted);
      margin: 0;
    }
    .error { color: var(--danger); }
    @media (max-width: 820px) {
      header, .layout { display: block; }
      .status { margin-top: 18px; }
      .result { margin-top: 18px; }
      .grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>Pixora</h1>
        <p>Generate product creative strategy, prompts, mock images, and video scripts from an ecommerce product URL.</p>
      </div>
      <div class="status"><span class="dot"></span><span id="health">Checking API...</span></div>
    </header>

    <div class="layout">
      <section class="panel">
        <form id="generate-form">
          <label for="url">Product URL</label>
          <input id="url" name="url" type="url" placeholder="https://example.com/product" required />

          <label for="brand">Brand override</label>
          <input id="brand" name="brand" type="text" placeholder="Optional" />

          <label for="audience">Target audience</label>
          <input id="audience" name="audience" type="text" placeholder="Optional" />

          <button id="submit" type="submit">Generate Creatives</button>
        </form>
        <div class="links">
          <a href="/health">Health</a>
          <a href="/docs">API Docs</a>
          <a href="/openapi.json">OpenAPI</a>
        </div>
      </section>

      <section class="result" id="result">
        <div class="empty">
          <div>
            <strong>Ready when you are.</strong>
            <p>Enter a product URL to run the Pixora pipeline.</p>
          </div>
        </div>
      </section>
    </div>
  </main>

  <script>
    const health = document.getElementById("health");
    fetch("/health")
      .then((response) => response.ok ? response.json() : Promise.reject())
      .then((data) => { health.textContent = data.status === "healthy" ? "API healthy" : "API online"; })
      .catch(() => { health.textContent = "API status unavailable"; });

    const form = document.getElementById("generate-form");
    const urlInput = document.getElementById("url");
    const brandInput = document.getElementById("brand");
    const audienceInput = document.getElementById("audience");
    const result = document.getElementById("result");
    const submit = document.getElementById("submit");

    function escapeHtml(value) {
      return String(value || "").replace(/[<>&]/g, c => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;" }[c]));
    }

    function listItems(items) {
      if (!items || !items.length) return "<p>No items returned.</p>";
      return "<ul>" + items.map((item) => `<li>${escapeHtml(item)}</li>`).join("") + "</ul>";
    }

    function render(data) {
      if (data.status === "failed") {
        result.innerHTML = `<p class="error">${data.error || "Generation failed."}</p><pre>${JSON.stringify(data, null, 2)}</pre>`;
        return;
      }
      const product = data.product_data || {};
      const brief = data.creative_brief || {};
      const prompts = data.prompts || {};
      const review = data.critic_review || {};

      result.innerHTML = `
        <div class="grid">
          <div class="item">
            <h3>Product</h3>
            <p><strong>${escapeHtml(product.title || "Untitled product")}</strong></p>
            <p>${escapeHtml(product.description || "No description returned.")}</p>
            ${listItems(product.features || [])}
          </div>
          <div class="item">
            <h3>Strategy</h3>
            <p><strong>Audience:</strong> ${escapeHtml(brief.target_audience || "N/A")}</p>
            ${listItems(brief.hooks || [])}
          </div>
          <div class="item">
            <h3>Image Prompts</h3>
            ${listItems(prompts.image_prompts || [])}
          </div>
          <div class="item">
            <h3>Quality Review</h3>
            <p><strong>Overall:</strong> ${Math.round((review.overall_quality || 0) * 100)}%</p>
            ${listItems(review.suggestions || [])}
          </div>
        </div>
      `;
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      submit.disabled = true;
      submit.textContent = "Generating...";
      result.innerHTML = `<div class="empty"><div><strong>Running pipeline...</strong><p>This can take a little while on serverless.</p></div></div>`;

      const body = {
        url: urlInput.value,
        brand_override: brandInput.value || null,
        target_audience: audienceInput.value || null
      };

      try {
        const response = await fetch("/api/v1/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body)
        });
        const data = await response.json();
        render(data);
      } catch (error) {
        result.innerHTML = `<p class="error">Request failed: ${error.message}</p>`;
      } finally {
        submit.disabled = false;
        submit.textContent = "Generate Creatives";
      }
    });
  </script>
</body>
</html>
        """
    )


@app.get("/favicon.ico", include_in_schema=False)
async def favicon_ico():
    return Response(status_code=204)


@app.get("/favicon.png", include_in_schema=False)
async def favicon_png():
    return Response(status_code=204)


# ==================== Main ====================

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        log_level=config.LOG_LEVEL.lower()
    )
