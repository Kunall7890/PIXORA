import asyncio
import re
import httpx
from bs4 import BeautifulSoup

URL = "https://www.amazon.in/Samsung-Galaxy-S24-Ultra-5G-Smartphone/dp/B0CS5XW6TN"

async def main():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0", "Accept-Language": "en-IN,en;q=0.9"}
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as c:
        html = (await c.get(URL, headers=headers)).text
    soup = BeautifulSoup(html, "html.parser")

    title = soup.select_one("#productTitle")
    print("title:", title.get_text(strip=True)[:80] if title else None)

    bullets = soup.select("#feature-bullets li span.a-list-item")
    print("bullets:", len(bullets))
    for b in bullets[:8]:
        print(" -", b.get_text(strip=True)[:100])

    desc = soup.select_one("#productDescription")
    print("desc len:", len(desc.get_text()) if desc else 0)

    # JSON in script tags
    for script in soup.find_all("script"):
        t = script.string or ""
        if "title" in t and "feature" in t.lower() and len(t) < 50000:
            if "productTitle" in t or "featureBullets" in t:
                print("script hint:", t[:200])

    # meta
    og = soup.find("meta", property="og:title")
    print("og:", og.get("content")[:80] if og else None)

asyncio.run(main())
