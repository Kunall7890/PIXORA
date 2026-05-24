import asyncio
import json
import re
import httpx

URL = "https://www.flipkart.com/apple-iphone-17-black-256-gb/p/itm6eb39da622cdd?pid=MOBHFN6YN2HXB5HE"

async def main():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as c:
        html = (await c.get(URL, headers=headers)).text

    idx = html.find("window.__INITIAL_STATE__")
    start = html.find("{", idx)
    depth = 0
    end = start
    for i, ch in enumerate(html[start:start + 3000000], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    state = json.loads(html[start:end])

    seo = state["multiWidgetState"]["pageDataResponse"]["seoData"]
    print("SEO title:", seo["seo"]["title"])
    print("SEO desc:", seo["seo"]["description"][:200])
    schema = seo["schema"][0]
    print("brand:", schema.get("brand"))
    print("rating:", schema.get("aggregateRating"))
    print("offers:", schema.get("offers", {}).get("price"))

    ctx = state["multiWidgetState"]["pageDataResponse"]["pageContext"]
    print("fdp ppd:", ctx.get("fdpEventTracking", {}).get("events", {}).get("psi", {}).get("ppd"))

    # search highlights in full json string
    blob = json.dumps(state)
    for kw in ["highlights", "Highlights", "256 GB", "48 MP", "A19", "Bionic"]:
        print(kw, blob.count(kw))

asyncio.run(main())
