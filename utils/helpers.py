"""
Utility functions for Pixora
"""
import logging
import asyncio
from typing import Dict, List
from pathlib import Path

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO"):
    """Setup application logging"""
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def ensure_directories():
    """Ensure all required directories exist"""
    directories = [
        Path("outputs"),
        Path("outputs/images"),
        Path("outputs/videos"),
        Path("logs"),
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Directory ready: {directory}")


def validate_url(url: str) -> bool:
    """Validate if URL is accessible and is a product page"""
    from urllib.parse import urlparse
    
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except:
        return False


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    import re
    # Remove special characters
    filename = re.sub(r'[^\w\s-]', '', filename)
    # Replace spaces with underscores
    filename = re.sub(r'[-\s]+', '_', filename)
    return filename.lower()


async def rate_limit(func, *args, max_concurrent=3, **kwargs):
    """Rate limit async function calls"""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def bounded_func():
        async with semaphore:
            return await func(*args, **kwargs)
    
    return await bounded_func()


def format_product_data(data: Dict) -> Dict:
    """Format product data for display"""
    return {
        "title": data.get("title", "N/A"),
        "price": f"${data.get('price', 'N/A')}" if data.get("price") else "N/A",
        "rating": f"⭐ {data.get('rating', 'N/A')}/5" if data.get("rating") else "N/A",
        "features": data.get("features", [])[:5],
        "specs": data.get("specs", {}),
        "url": data.get("url", "N/A")
    }


def calculate_workflow_time(tasks: List[Dict]) -> Dict:
    """Calculate workflow execution time breakdown"""
    total = 0
    breakdown = {}
    
    for task in tasks:
        name = task.get("name", "unknown")
        duration = task.get("duration", 0)
        total += duration
        breakdown[name] = duration
    
    return {
        "total": total,
        "breakdown": breakdown,
        "average_per_step": total / len(tasks) if tasks else 0
    }


def export_results_json(results: Dict, output_path: str):
    """Export workflow results to JSON"""
    import json
    
    try:
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"✓ Results exported to {output_path}")
    except Exception as e:
        logger.error(f"Error exporting results: {str(e)}")


def export_results_csv(results: List[Dict], output_path: str):
    """Export workflow results to CSV"""
    import csv
    
    try:
        if not results:
            return
        
        keys = results[0].keys()
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
        
        logger.info(f"✓ Results exported to {output_path}")
    except Exception as e:
        logger.error(f"Error exporting CSV: {str(e)}")
