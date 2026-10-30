"""Minimal Gemini REST client. The key is read in-process from a file and never printed or logged."""
import json, time, urllib.request, urllib.error


def call(key_path, model, system, user, temperature=0.0, retries=6, timeout=120):
    key = open(key_path).read().strip()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = json.dumps({
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {"temperature": temperature},
    }).encode()
    err = ""
    for a in range(retries):
        try:
            req = urllib.request.Request(url, body, {"Content-Type": "application/json", "x-goog-api-key": key})
            d = json.load(urllib.request.urlopen(req, timeout=timeout))
            parts = d["candidates"][0]["content"].get("parts", [])
            text = "".join(p.get("text", "") for p in parts)
            return text, d.get("usageMetadata", {}), ""
        except urllib.error.HTTPError as e:
            err = f"HTTP {e.code}: {e.read()[:200].decode('utf8','replace')}"
            if e.code in (429, 500, 503):
                time.sleep(min(60, 5 * 2 ** a))
                continue
            break
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
            time.sleep(5)
    return "", {}, err
