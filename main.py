import os, time, re
from fastapi import FastAPI, File, UploadFile, Header, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://duplicate.mobilewoodfirepizza.com.au",
        "https://mobilewoodfirepizza.com.au",
        "http://127.0.0.1:8000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- settings ---
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# simple shared password token (set this in Render env later)
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "devtoken")

# the editable slots your admin page will show
SLOTS = ["home_hero", "gallery_01", "gallery_02", "about_banner"]
SAFE_SLOT_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")

def file_path(slot: str):
    return os.path.join(UPLOAD_DIR, f"{slot}.jpg")

def absolute_url(request_host: str, slot: str):
    # cache-bust with timestamp
    return f"{request_host}/uploads/{slot}.jpg?v={int(time.time())}"

def require_admin(x_admin_token: str | None):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

def validate_slot(slot: str):
    if not SAFE_SLOT_PATTERN.fullmatch(slot):
        raise HTTPException(status_code=400, detail="Invalid slot id")

@app.get("/manifest.json")
def manifest(host: str | None = Header(default=None)):
    # host header gives us current base URL (works local + Render)
    base = f"http://{host}" if host and "localhost" in host else (f"https://{host}" if host else "")
    out = {}
    for slot in SLOTS:
        out[slot] = absolute_url(base, slot) if base else f"/uploads/{slot}.jpg?v={int(time.time())}"
    return JSONResponse(out)

@app.post("/admin/upload/{slot}")
async def upload(slot: str, file: UploadFile = File(...), x_admin_token: str | None = Header(default=None), host: str | None = Header(default=None)):
    require_admin(x_admin_token)
    validate_slot(slot)

    data = await file.read()
    if not data:
        raise HTTPException(400, "Empty file")

    with open(file_path(slot), "wb") as f:
        f.write(data)

    base = f"http://{host}" if host and "localhost" in host else (f"https://{host}" if host else "")
    return {"ok": True, "slot": slot, "url": absolute_url(base, slot)}

@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    # minimal click-to-replace UI
    slots_js = str(SLOTS).replace("'", '"')
    return f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Image Changer</title>
  <style>
    body {{ font-family: Arial, sans-serif; background:#0f0f0f; color:#fff; padding:20px; }}
    .grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap:16px; }}
    .card {{ background:#171717; border:1px solid #2a2a2a; border-radius:14px; padding:12px; }}
    .label {{ font-size:12px; opacity:.75; margin-bottom:8px; }}
    img {{ width:100%; height:180px; object-fit:cover; border-radius:12px; border:1px solid #2a2a2a; cursor:pointer; }}
    .hint {{ font-size:12px; opacity:.65; margin-top:8px; }}
    .row {{ display:flex; gap:12px; align-items:center; margin-bottom:14px; }}
    input[type="password"] {{ padding:10px; border-radius:10px; border:1px solid #2a2a2a; background:#0b0b0b; color:#fff; }}
    button {{ padding:10px 12px; border-radius:10px; border:1px solid #2a2a2a; background:#151515; color:#fff; cursor:pointer; }}
  </style>
</head>
<body>
  <div class="row">
    <h2 style="margin:0;">Image Changer</h2>
    <input id="token" type="password" placeholder="Admin token" />
    <button onclick="load()">Refresh</button>
  </div>

  <div class="hint">Click an image to replace it.</div><br/>

  <input id="file" type="file" accept="image/*" style="display:none" />
  <div id="grid" class="grid"></div>

<script>
  const slots = {slots_js};
  const grid = document.getElementById("grid");
  const fileInput = document.getElementById("file");
  const tokenInput = document.getElementById("token");
  let currentSlot = null;

  async function load() {{
    const res = await fetch("/manifest.json", {{ cache: "no-store" }});
    const manifest = await res.json();

    grid.innerHTML = "";
    for (const slot of slots) {{
      const card = document.createElement("div");
      card.className = "card";

      const label = document.createElement("div");
      label.className = "label";
      label.textContent = slot;

      const img = document.createElement("img");
      img.alt = slot;
      img.src = manifest[slot] || ("/uploads/" + slot + ".jpg");

      img.onclick = () => {{
        currentSlot = slot;
        fileInput.value = "";
        fileInput.click();
      }};

      const hint = document.createElement("div");
      hint.className = "hint";
      hint.textContent = "Click to upload a new file";

      card.appendChild(label);
      card.appendChild(img);
      card.appendChild(hint);
      grid.appendChild(card);
    }}
  }}

  fileInput.addEventListener("change", async () => {{
    const file = fileInput.files[0];
    if (!file || !currentSlot) return;

    const form = new FormData();
    form.append("file", file);

    const res = await fetch("/admin/upload/" + encodeURIComponent(currentSlot), {{
      method: "POST",
      headers: {{ "X-Admin-Token": tokenInput.value }},
      body: form
    }});

    if (!res.ok) {{
      alert("Upload failed: " + await res.text());
      return;
    }}

    const out = await res.json();
    document.querySelectorAll("img").forEach(img => {{
      if (img.alt === currentSlot) img.src = out.url;
    }});
  }});

  load();
</script>
</body>
</html>
"""
