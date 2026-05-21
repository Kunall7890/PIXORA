from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime

# ==================== Request Models ====================

class ProductURLRequest(BaseModel):
    """Single product URL request"""
    url: HttpUrl
    brand_override: Optional[str] = None
    target_audience: Optional[str] = None
    custom_themes: Optional[List[str]] = None


class BulkProcessingRequest(BaseModel):
    """Bulk CSV processing request"""
    urls: List[str]
    priority: str = "normal"  # low, normal, high


# ==================== Response Models ====================

class ProductData(BaseModel):
    """Extracted product information"""
    url: str
    title: str
    description: str
    price: Optional[float]
    currency: Optional[str]
    features: List[str]
    specs: Dict[str, str]
    reviews_summary: Optional[str]
    rating: Optional[float]
    image_urls: List[str]
    brand: str


class CreativeBrief(BaseModel):
    """Generated creative strategy"""
    hooks: List[str]
    target_audience: str
    visual_themes: List[str]
    color_palette: List[str]
    marketing_angles: List[str]
    ad_captions: List[str]
    tone_of_voice: str


class GeneratedPrompts(BaseModel):
    """Optimized prompts for generation models"""
    image_prompts: List[str]
    video_scripts: List[str]
    visual_style_guide: str


class ImageAsset(BaseModel):
    """Generated image metadata"""
    id: str
    prompt: str
    url: str
    local_path: str
    created_at: datetime
    quality_score: Optional[float] = None


class VideoAsset(BaseModel):
    """Generated video metadata"""
    id: str
    script: str
    url: str
    local_path: str
    duration: float
    created_at: datetime
    quality_score: Optional[float] = None


class CriticReview(BaseModel):
    """Quality review from critic agent"""
    hallucination_score: float  # 0-1
    consistency_score: float
    branding_score: float
    overall_quality: float
    issues: List[str]
    suggestions: List[str]
    approved: bool


class WorkflowOutput(BaseModel):
    """Final workflow output"""
    product_data: ProductData
    creative_brief: CreativeBrief
    prompts: GeneratedPrompts
    images: List[ImageAsset]
    videos: List[VideoAsset]
    critic_review: CriticReview
    total_processing_time: float
    status: str  # success, partial, failed


class JobStatus(BaseModel):
    """Bulk job tracking"""
    job_id: str
    status: str  # queued, processing, completed, failed
    progress: int  # 0-100
    total_urls: int
    processed_urls: int
    failed_urls: int
    created_at: datetime
    updated_at: datetime
    results: Optional[List[WorkflowOutput]] = None
    error_message: Optional[str] = None


class JobStatusResponse(BaseModel):
    """Response for job status query"""
    job_id: str
    status: str
    progress: int
    processing_time: float
    results_count: int
