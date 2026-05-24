"""Test multiple Flipkart/Amazon product URLs."""
import asyncio
import httpx

URLS = [
    ("flipkart_shoes", "https://www.flipkart.com/puma-men-sneakers/p/itm1234567890"),  # placeholder
    ("flipkart_laptop", "https://www.flipkart.com/hp-15s-intel-celeron-dual-core-8-gb-512-gb-ssd-windows-11-home/p/itmf3gfzzgzkfh4f"),
    ("flipkart_headphones", "https://www.flipkart.com/boat-airdopes-131-bluetooth-headset/p/itm6e6e6e6e6e6e6"),
    ("amazon_book", "https://www.amazon.in/dp/0143452137"),
    ("amazon_shoes", "https://www.amazon.in/dp/B0C1H26C46"),
]

# Real URLs - search common products
REAL = [
    "https://www.flipkart.com/boat-rockerz-450-bluetooth/p/itmfcg3fbp4z8yzf",
    "https://www.flipkart.com/samsung-galaxy-s25-5g-cobalt-violet-256-gb/p/itmcc838f4a3b7a9",
    "https://www.amazon.in/Samsung-Galaxy-S24-Ultra-Storage/dp/B0CS5XW6TN",
    "https://www.amazon.in/Apple-MacBook-Chip-10-core-Storage/dp/B0DZDC3WW5",
    "https://www.amazon.in/Nike-Revolution-Running-Shoes-Black/dp/B0B8XYZ",
]

async def probe(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
    try:
        async with httpx.AsyncClient(timeout=25, follow_redirects=True) as c:
            r = await c.get(url, headers=headers)
            print(url[:70], "->", r.status_code, len(r.text))
            h = r.text
            for m in ["__INITIAL_STATE__", "feature-bullets", "productDescription", "application/ld+json"]:
                print(" ", m, "yes" if m in h else "no")
    except Exception as e:
        print(url[:70], "ERR", e)

async def main():
    for u in REAL[:4]:
        await probe(u)
        print()

asyncio.run(main())
