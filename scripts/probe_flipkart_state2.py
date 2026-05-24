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
    if idx < 0:
        print("not found")
        return
    start = html.find("{", idx)
    # bracket matching
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
    raw = html[start:end]
    state = json.loads(raw)

    hits = []

    def walk(obj, path=""):
        if len(hits) > 30:
            return
        if isinstance(obj, dict):
            keys = set(obj.keys())
            interesting = keys & {
                "title", "titles", "pricing", "productDescription", "highlights",
                "productHighlights", "summary", "brand", "value", "description",
                "rating", "reviewCount", "prices", "finalPrice", "media",
            }
            if interesting:
                hits.append((path, {k: obj[k] for k in interesting if k in obj}))
            for k, v in list(obj.items())[:50]:
                walk(v, f"{path}.{k}" if path else k)
        elif isinstance(obj, list):
            for i, item in enumerate(obj[:5]):
                walk(item, f"{path}[{i}]")

    walk(state)
    for path, data in hits[:25]:
        print("---", path)
        s = json.dumps(data, ensure_ascii=False)[:300]
        print(s)

asyncio.run(main())
