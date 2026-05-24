"""Test extraction across Amazon and Flipkart product types."""
import asyncio
import config
from agents.research_agent import product_researcher

TESTS = [
    ("Amazon Phone", "https://www.amazon.in/Samsung-Galaxy-S24-Ultra-5G-Smartphone/dp/B0CS5XW6TN"),
    ("Amazon Laptop", "https://www.amazon.in/dp/B0CX23V2ZK"),
    ("Flipkart iPhone", "https://www.flipkart.com/apple-iphone-17-black-256-gb/p/itm6eb39da622cdd?pid=MOBHFN6YN2HXB5HE"),
    ("Flipkart Headphones", "https://www.flipkart.com/boat-rockerz-450-bluetooth-wireless-on-ear-headphones/p/itmfcg3fbp4z8yzf"),
]

async def main():
    for label, url in TESTS:
        print("=" * 60)
        print(label)
        d = await product_researcher.extract_product_info(url)
        print(" Title:", d.get("title", "")[:70])
        print(" Brand:", d.get("brand"))
        print(" Price:", d.get("currency"), d.get("price"))
        print(" Quality:", d.get("scrape_quality"))
        print(" Features:", len(d.get("features", [])))
        for f in d.get("features", [])[:5]:
            print("  -", f[:90])
        print()

asyncio.run(main())
