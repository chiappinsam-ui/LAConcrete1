import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).parent

UPLOADS_DIR = BASE_DIR / "data" / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
MANIFEST_PATH = UPLOADS_DIR / "manifest.json"

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "changeme")
SAFE_SLOT_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")

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

# Serve static folders used by the exported HTML
STATIC_FOLDERS = [
    ("assets", BASE_DIR / "assets"),
    ("index1_files", BASE_DIR / "index1_files"),
    ("menu2_files", BASE_DIR / "menu2_files"),
    ("gallery5_files", BASE_DIR / "gallery5_files"),
    ("contact6_files", BASE_DIR / "contact6_files"),
    ("catering3_files", BASE_DIR / "catering3_files"),
    ("bookins4html_files", BASE_DIR / "bookins4html_files"),
]

for mount, path in STATIC_FOLDERS:
    if path.exists():
        app.mount(f"/{mount}", StaticFiles(directory=path), name=mount)

# Optional: direct access to stored uploads (primary access is via /media/{slot})
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


def load_manifest() -> Dict[str, Any]:
    if MANIFEST_PATH.exists():
        try:
            return json.loads(MANIFEST_PATH.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_manifest(data: Dict[str, Any]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(data, indent=2))


manifest: Dict[str, Any] = load_manifest()


def require_admin(x_admin_token: Optional[str]) -> None:
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")


def validate_slot(slot: str) -> None:
    if not SAFE_SLOT_PATTERN.fullmatch(slot):
        raise HTTPException(status_code=400, detail="Invalid slot id")


def cache_busted_media_url(slot: str) -> str:
    return f"/media/{slot}?v={int(time.time())}"


@app.get("/manifest.json")
def get_manifest():
    return {slot: cache_busted_media_url(slot) for slot in manifest}


@app.get("/media/{slot}")
def get_media(slot: str):
    info = manifest.get(slot)
    if not info:
        return JSONResponse({"detail": "No image for this slot"}, status_code=404)

    path = UPLOADS_DIR / info["stored_name"]
    if not path.exists():
        return JSONResponse({"detail": "File missing"}, status_code=404)

    return FileResponse(path)


@app.post("/admin/upload/{slot}")
async def upload(slot: str, file: UploadFile = File(...), x_admin_token: Optional[str] = Header(default=None)):
    require_admin(x_admin_token)
    validate_slot(slot)

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")

    suffix = Path(file.filename or "").suffix
    stored_name = f"{slot}{suffix}" if suffix else slot

    # replace previous file if it existed
    old = manifest.get(slot)
    if old:
        old_path = UPLOADS_DIR / old.get("stored_name", "")
        if old_path.exists() and old_path.name != stored_name:
            old_path.unlink()

    target_path = UPLOADS_DIR / stored_name
    target_path.write_bytes(data)

    manifest[slot] = {
        "stored_name": stored_name,
        "original_name": file.filename or stored_name,
        "uploaded_at": int(time.time()),
    }
    save_manifest(manifest)

    return {"ok": True, "slot": slot, "url": cache_busted_media_url(slot)}


@app.delete("/admin/delete/{slot}")
def delete(slot: str, x_admin_token: Optional[str] = Header(default=None)):
    require_admin(x_admin_token)

    info = manifest.pop(slot, None)
    if info:
        path = UPLOADS_DIR / info["stored_name"]
        if path.exists():
            path.unlink()
        save_manifest(manifest)
    return {"ok": True, "slot": slot}


@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    # Lightweight helper page; main editing happens via assets/admin.js overlay
    return """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Image Admin</title>
  <style>
    body { font-family: Arial, sans-serif; background:#0f0f0f; color:#fff; padding:20px; }
    .row { display:flex; gap:12px; margin-bottom:14px; align-items:center; }
    input, button { padding:10px 12px; border-radius:10px; border:1px solid #2a2a2a; background:#151515; color:#fff; }
    .grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:14px; margin-top:12px; }
    .card { background:#171717; border:1px solid #2a2a2a; border-radius:12px; padding:12px; }
    img { width:100%; height:160px; object-fit:cover; border-radius:10px; border:1px solid #2a2a2a; }
    .label { font-size:12px; opacity:.75; margin-bottom:6px; }
  </style>
</head>
<body>
  <div class="row">
    <h2 style="margin:0;">Image Admin</h2>
    <input id="token" type="password" placeholder="Admin token" />
    <input id="slot" type="text" placeholder="slot name" />
    <input id="file" type="file" accept="image/*" />
    <button onclick="doUpload()">Upload</button>
    <button onclick="load()">Refresh</button>
  </div>
  <div id="grid" class="grid"></div>
<script>
async function load() {
  const grid = document.getElementById("grid");
  grid.innerHTML = "";
  const res = await fetch("/manifest.json", { cache: "no-store" });
  const data = await res.json();
  Object.entries(data).forEach(([slot, url]) => {
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `<div class="label">${slot}</div><img src="${url}" alt="${slot}" />`;
    grid.appendChild(card);
  });
}

async function doUpload() {
  const token = document.getElementById("token").value;
  const slot = document.getElementById("slot").value.trim();
  const file = document.getElementById("file").files[0];
  if (!slot || !file) { alert("slot + file required"); return; }
  const fd = new FormData();
  fd.append("file", file);
  const res = await fetch(`/admin/upload/${encodeURIComponent(slot)}`, {
    method: "POST",
    headers: { "X-Admin-Token": token },
    body: fd,
  });
  if (!res.ok) { alert(await res.text()); return; }
  await load();
}
load();
</script>
</body>
</html>
"""


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index1.html")


@app.get("/menu")
def menu():
    return FileResponse(BASE_DIR / "menu2.html")


@app.get("/gallery")
def gallery():
    return FileResponse(BASE_DIR / "gallery5.html")


@app.get("/contact")
def contact():
    return FileResponse(BASE_DIR / "contact6.html")


@app.get("/catering")
def catering():
    return FileResponse(BASE_DIR / "catering3.html")


@app.get("/bookings")
def bookings():
    return FileResponse(BASE_DIR / "bookins4.html")
