import asyncio
import httpx
from bs4 import BeautifulSoup

URL = "https://www.amazon.in/Samsung-Galaxy-S24-Ultra-5G-Smartphone/dp/B0CS5XW6TN"

async def main():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as c:
        html = (await c.get(URL, headers=headers)).text
    soup = BeautifulSoup(html, "html.parser")

    for sel in ["#productOverview_feature_div tr", "#poExpander tr", "table.a-normal tr", ".a-expander-content tr"]:
        rows = soup.select(sel)
        if rows:
            print("SEL", sel, len(rows))
            for r in rows[:5]:
                print(" ", r.get_text(" ", strip=True)[:100])

asyncio.run(main())
