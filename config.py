import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
TOGETHER_AI_API_KEY = os.getenv("TOGETHER_AI_API_KEY", "")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")

# Models
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
IMAGE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
VIDEO_MODEL = "cogvideox"  # Via Replicate

# Generation settings
NUM_IMAGES = 5
NUM_VIDEOS = 2
IMAGE_SIZE = (1024, 1024)
VIDEO_DURATION = 8  # seconds
VIDEO_FPS = 24

# Batch processing
MAX_BATCH_SIZE = 50
JOB_TIMEOUT = 3600  # 1 hour per job

# Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_DB = os.getenv("REDIS_DB", 0)

# Web scraping
PLAYWRIGHT_HEADLESS = True
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# API Settings
API_HOST = "0.0.0.0"
API_PORT = 8000

# Quality thresholds for critic agent
HALLUCINATION_THRESHOLD = 0.7
CONSISTENCY_THRESHOLD = 0.75
BRANDING_THRESHOLD = 0.8
