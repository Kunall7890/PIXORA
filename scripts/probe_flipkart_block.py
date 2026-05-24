import asyncio
import httpx

URLS = [
    "https://www.flipkart.com/apple-iphone-17-black-256-gb/p/itm6eb39da622cdd?pid=MOBHFN6YN2HXB5HE",
    "https://www.flipkart.com/boat-rockerz-450-bluetooth-wireless-on-ear-headphones/p/itmfcg3fbp4z8yzf",
    "https://www.amazon.in/Samsung-Galaxy-S24-Ultra-5G-Smartphone/dp/B0CS5XW6TN",
]

async def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-IN,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Upgrade-Insecure-Requests": "1",
    }
    for url in URLS:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as c:
            r = await c.get(url, headers=headers)
            t = r.text
            print("URL:", url[:65])
            print(" status", r.status_code, "len", len(t))
            print(" INITIAL_STATE", "__INITIAL_STATE__" in t)
            print(" title snippet", t[t.find("<title"):t.find("<title")+80] if "<title" in t else "no title")
            print()

asyncio.run(main())
