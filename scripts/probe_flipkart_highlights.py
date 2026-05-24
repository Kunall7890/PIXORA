import asyncio
import json
import httpx

URL = "https://www.flipkart.com/apple-iphone-17-black-256-gb/p/itm6eb39da622cdd?pid=MOBHFN6YN2HXB5HE"

async def main():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as c:
        html = (await c.get(URL, headers=headers)).text

    start = html.find("{", html.find("window.__INITIAL_STATE__"))
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

    found = []

    def walk(obj, path=""):
        if isinstance(obj, dict):
            if "highlights" in str(obj.keys()).lower() or obj.get("type") == "Highlights":
                if "values" in obj or "list" in obj or isinstance(obj.get("highlights"), list):
                    found.append((path, obj))
            for k, v in obj.items():
                if "highlight" in k.lower() or k in ("values", "renderableComponents"):
                    walk(v, f"{path}.{k}")
                elif len(path) < 80:
                    walk(v, f"{path}.{k}" if path else k)
        elif isinstance(obj, list) and len(path) < 80:
            for i, item in enumerate(obj[:8]):
                walk(item, f"{path}[{i}]")

    walk(state["multiWidgetState"].get("widgetsData", {}))
    for path, obj in found[:8]:
        print("PATH", path[:100])
        print(json.dumps(obj, ensure_ascii=False)[:400])
        print()

asyncio.run(main())
