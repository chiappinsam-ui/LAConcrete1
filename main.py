import os, time, re, json
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Header, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# -------------------------
# Static folders (only mount if they exist)
# -------------------------
for folder in [
    "assets",
    "index1_files",
    "menu2_files",
    "gallery5_files",
    "contact6_files",
    "catering3_files",
    "bookins4html_files",
]:
    if os.path.isdir(folder):
        app.mount(f"/{folder}", StaticFiles(directory=folder), name=folder)

# -------------------------
# CORS
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://duplicate.mobilewoodfirepizza.com.au",
        "https://mobilewoodfirepizza.com.au",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Storage (disk)
# -------------------------
DATA_DIR = Path("data")
UPLOADS_DIR = DATA_DIR / "uploads"
DATA_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "devtoken")

SLOTS = ["home_hero", "gallery_01", "gallery_02", "about_banner"]
SAFE_SLOT_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")

def require_admin(x_admin_token: str | None):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

def validate_slot(slot: str):
    if not SAFE_SLOT_PATTERN.fullmatch(slot):
        raise HTTPException(status_code=400, detail="Invalid slot id")

def file_path(slot: str) -> Path:
    return UPLOADS_DIR / f"{slot}.jpg"

def absolute_url(base: str, slot: str):
    return f"{base}/uploads/{slot}.jpg?v={int(time.time())}"

def serve_html(*candidates: str):
    for name in candidates:
        if os.path.exists(name):
            return FileResponse(name)
    raise HTTPException(404, detail=f"Missing file. Tried: {', '.join(candidates)}")

# -------------------------
# Site pages
# -------------------------
@app.get("/")
def home():
    return serve_html("index1.html", "index.html")

@app.get("/menu")
def menu():
    return serve_html("menu2.html", "menu.html")

@app.get("/gallery")
def gallery():
    return serve_html("gallery5.html", "gallery.html")

@app.get("/contact")
def contact():
    return serve_html("contact6.html", "contact.html")

@app.get("/catering")
def catering():
    return serve_html("catering3.html", "catering.html")

@app.get("/bookings")
def bookings():
    # you had "bookins4.html" - keep both options just in case
    return serve_html("bookins4.html", "bookings.html")

# -------------------------
# Admin API
# -------------------------
@app.get("/manifest.json")
def manifest(host: str | None = Header(default=None)):
    base = ""
    if host:
        base = f"http://{host}" if "localhost" in host or "127.0.0.1" in host else f"https://{host}"

    out = {}
    for slot in SLOTS:
        out[slot] = absolute_url(base, slot) if base else f"/uploads/{slot}.jpg?v={int(time.time())}"
    return JSONResponse(out)

@app.post("/admin/upload/{slot}")
async def upload(
    slot: str,
    file: UploadFile = File(...),
    x_admin_token: str | None = Header(default=None),
    host: str | None = Header(default=None),
):
    require_admin(x_admin_token)
    validate_slot(slot)

    data = await file.read()
    if not data:
        raise HTTPException(400, "Empty file")

    file_path(slot).write_bytes(data)

    base = ""
    if host:
        base = f"http://{host}" if "localhost" in host or "127.0.0.1" in host else f"https://{host}"
    return {"ok": True, "slot": slot, "url": absolute_url(base, slot) if base else f"/uploads/{slot}.jpg?v={int(time.time())}"}

@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    slots_js = json.dumps(SLOTS)
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
    if (!res.ok) {{
      alert("manifest.json failed: " + await res.text());
      return;
    }}
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
