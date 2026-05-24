import asyncio
import re
import httpx

URL = "https://www.flipkart.com/apple-iphone-17-black-256-gb/p/itm6eb39da622cdd?pid=MOBHFN6YN2HXB5HE"

async def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "en-IN,en;q=0.9",
    }
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as c:
        r = await c.get(URL, headers=headers)
        print("status", r.status_code, "len", len(r.text))
        html = r.text
        for pat in ["__INITIAL_STATE__", "__PRELOADED_STATE__", "iPhone 17", "Flipkart Internet", "My Profile"]:
            print(pat, "yes" if pat in html else "no")

asyncio.run(main())
