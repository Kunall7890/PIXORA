"""
Product Research Agent
Extracts and understands product information from URLs
"""
import asyncio
import logging
from typing import Dict, List, Optional
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)


class ProductResearchAgent:
    """Scrapes and extracts product data from e-commerce URLs"""
    
    def __init__(self):
        self.timeout = 30
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    async def extract_product_info(self, url: str) -> Dict:
        """
        Extract product information from URL
        
        Returns:
            Dict with title, description, price, features, specs, reviews, images
        """
        try:
            logger.info(f"Researching product: {url}")
            
            # Fetch page content
            html_content = await self._fetch_page(url)
            if not html_content:
                logger.error(f"Failed to fetch URL: {url}")
                return self._default_product_data(url)
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract data
            product_data = {
                "url": url,
                "title": self._extract_title(soup),
                "description": self._extract_description(soup),
                "price": self._extract_price(soup),
                "currency": self._extract_currency(soup),
                "features": self._extract_features(soup),
                "specs": self._extract_specs(soup),
                "reviews_summary": self._extract_reviews(soup),
                "rating": self._extract_rating(soup),
                "image_urls": self._extract_images(soup),
                "brand": self._extract_brand(soup),
            }
            
            logger.info(f"✓ Successfully extracted product: {product_data['title']}")
            return product_data
            
        except Exception as e:
            logger.error(f"Error extracting product info: {str(e)}")
            return self._default_product_data(url)
    
    async def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch page content using Playwright for dynamic content"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url, wait_until="networkidle", timeout=self.timeout * 1000)
                content = await page.content()
                await browser.close()
                return content
        except Exception as e:
            logger.warning(f"Playwright failed, trying httpx: {str(e)}")
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url, headers={"User-Agent": self.user_agent})
                    return response.text if response.status_code == 200 else None
            except Exception as e:
                logger.error(f"Both methods failed: {str(e)}")
                return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract product title"""
        title = soup.find("h1")
        if title:
            return title.get_text(strip=True)
        
        title = soup.find("meta", property="og:title")
        if title:
            return title.get("content", "Unknown Product")
        
        return "Unknown Product"
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract product description"""
        desc = soup.find("meta", property="og:description")
        if desc:
            return desc.get("content", "")
        
        desc_tag = soup.find("meta", attrs={"name": "description"})
        if desc_tag:
            return desc_tag.get("content", "")
        
        # Try finding main description paragraph
        p_tags = soup.find_all("p")
        if p_tags:
            return " ".join([p.get_text(strip=True) for p in p_tags[:3]])
        
        return "No description available"
    
    def _extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract product price"""
        price_patterns = [
            soup.find("span", class_=lambda x: x and "price" in x.lower()),
            soup.find("div", class_=lambda x: x and "price" in x.lower()),
            soup.find("meta", property="product:price:amount"),
        ]
        
        for pattern in price_patterns:
            if pattern:
                text = pattern.get_text() if hasattr(pattern, 'get_text') else pattern.get("content", "")
                try:
                    # Extract numbers
                    import re
                    match = re.search(r'\d+\.?\d*', text.replace(',', ''))
                    if match:
                        return float(match.group())
                except:
                    pass
        
        return None
    
    def _extract_currency(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract currency"""
        currency_tag = soup.find("meta", property="product:price:currency")
        if currency_tag:
            return currency_tag.get("content")
        
        # Default based on common patterns
        html_str = str(soup)
        if "$" in html_str:
            return "USD"
        elif "€" in html_str:
            return "EUR"
        elif "£" in html_str:
            return "GBP"
        elif "₹" in html_str:
            return "INR"
        
        return "USD"
    
    def _extract_features(self, soup: BeautifulSoup) -> List[str]:
        """Extract product features"""
        features = []
        
        # Look for ul/li tags
        ul_tags = soup.find_all("ul")
        for ul in ul_tags[:3]:  # Get first 3 feature lists
            li_tags = ul.find_all("li")
            features.extend([li.get_text(strip=True) for li in li_tags[:8]])
        
        return features[:10]  # Return top 10
    
    def _extract_specs(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract technical specifications"""
        specs = {}
        
        # Look for tables or spec sections
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows[:10]:
                cols = row.find_all(["td", "th"])
                if len(cols) >= 2:
                    key = cols[0].get_text(strip=True)
                    value = cols[1].get_text(strip=True)
                    specs[key] = value
        
        return specs
    
    def _extract_reviews(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract review summary"""
        review_tags = soup.find_all(class_=lambda x: x and "review" in x.lower())
        if review_tags:
            reviews = [tag.get_text(strip=True) for tag in review_tags[:3]]
            return " ".join(reviews)
        
        return "No reviews found"
    
    def _extract_rating(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract product rating"""
        rating_meta = soup.find("meta", property="product:rating:value")
        if rating_meta:
            try:
                return float(rating_meta.get("content", 0))
            except:
                pass
        
        rating_tags = soup.find_all(class_=lambda x: x and "rating" in x.lower())
        for tag in rating_tags:
            text = tag.get_text(strip=True)
            try:
                import re
                match = re.search(r'(\d+\.?\d*)\s*(?:\/|out)', text)
                if match:
                    return float(match.group(1))
            except:
                pass
        
        return None
    
    def _extract_images(self, soup: BeautifulSoup) -> List[str]:
        """Extract product images"""
        images = []
        
        # Meta tags
        og_image = soup.find("meta", property="og:image")
        if og_image:
            images.append(og_image.get("content"))
        
        # Product images
        img_tags = soup.find_all("img", class_=lambda x: x and "product" in x.lower() if x else False)
        images.extend([img.get("src") or img.get("data-src") for img in img_tags if img.get("src") or img.get("data-src")])
        
        # All images as fallback
        if not images:
            all_imgs = soup.find_all("img")
            images = [img.get("src") or img.get("data-src") for img in all_imgs[:10] if img.get("src") or img.get("data-src")]
        
        # Filter valid URLs
        images = [img for img in images if img and ("http" in img or img.startswith("/"))]
        return list(set(images))[:10]  # Dedupe and limit to 10
    
    def _extract_brand(self, soup: BeautifulSoup) -> str:
        """Extract brand name"""
        brand_tag = soup.find("meta", property="product:brand")
        if brand_tag:
            return brand_tag.get("content", "Unknown")
        
        # Try to extract from URL
        from urllib.parse import urlparse
        domain = urlparse(str(soup)).netloc
        if domain:
            return domain.split('.')[-2].capitalize()
        
        return "Unknown Brand"
    
    def _default_product_data(self, url: str) -> Dict:
        """Return default product data when extraction fails"""
        return {
            "url": url,
            "title": "Product Unavailable",
            "description": "Unable to extract product information",
            "price": None,
            "currency": "USD",
            "features": [],
            "specs": {},
            "reviews_summary": "No reviews found",
            "rating": None,
            "image_urls": [],
            "brand": "Unknown",
        }


# Instantiate agent
product_researcher = ProductResearchAgent()
