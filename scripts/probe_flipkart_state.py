import asyncio
import json
import re
import httpx

URL = "https://www.flipkart.com/apple-iphone-17-black-256-gb/p/itm6eb39da622cdd?pid=MOBHFN6YN2HXB5HE"

async def main():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as c:
        html = (await c.get(URL, headers=headers)).text

    m = re.search(r"window\.__INITIAL_STATE__\s*=\s*(\{.+?\})\s*;\s*</script>", html, re.DOTALL)
    if not m:
        m = re.search(r"__INITIAL_STATE__\s*=\s*(\{.+?\})\s*;", html, re.DOTALL)
    if not m:
        print("no state found")
        return

    raw = m.group(1)
    # Truncate safely - find balanced brace is hard; try json.loads on substring
    try:
        state = json.loads(raw)
    except json.JSONDecodeError:
        # try smaller chunk from start
        for end in range(len(raw), 1000, -1000):
            try:
                state = json.loads(raw[:end])
                break
            except json.JSONDecodeError:
                continue
        else:
            print("json parse failed")
            return

    print("top keys:", list(state.keys())[:20])

    def find_product(obj, depth=0):
        if depth > 12:
            return None
        if isinstance(obj, dict):
            if obj.get("titles") or obj.get("pricing") or obj.get("productDescription"):
                return obj
            for v in obj.values():
                r = find_product(v, depth + 1)
                if r:
                    return r
        elif isinstance(obj, list):
            for item in obj[:30]:
                r = find_product(item, depth + 1)
                if r:
                    return r
        return None

    prod = find_product(state)
    if prod:
        print("found product keys:", list(prod.keys())[:30])
        titles = prod.get("titles") or {}
        print("title:", titles.get("title") or titles.get("subtitle"))
        print("pricing:", prod.get("pricing"))
        desc = prod.get("productDescription")
        if desc:
            print("desc type", type(desc), str(desc)[:200])
        highlights = prod.get("highlights") or prod.get("productHighlights")
        print("highlights:", highlights)
    else:
        # search for iphone in json string
        s = json.dumps(state)[:5000]
        print("sample:", s[:500])

asyncio.run(main())
