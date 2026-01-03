import os, time, re
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, Header, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ----------------------------
# Static folders (mount only if they exist)
# ----------------------------
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

# ----------------------------
# CORS (harmless even if same-origin)
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mobilewoodfirepizza.com.au",
        "https://duplicate.mobilewoodfirepizza.com.au",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Storage
# ----------------------------
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# If you keep originals in a folder called "media" in the repo, we will serve them as fallback
DEFAULT_MEDIA_DIRS = [Path("media"), Path("assets/media"), Path("static/media")]

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "devtoken")

SAFE_SLOT_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")

IMG_EXTS = [".jpg", ".jpeg", ".png", ".webp", ".gif"]

def require_admin(x_admin_token: Optional[str]):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

def validate_slot(slot: str):
    if not SAFE_SLOT_PATTERN.fullmatch(slot):
        raise HTTPException(status_code=400, detail="Invalid slot id")

def serve_html(*candidates: str):
    for name in candidates:
        if os.path.exists(name):
            return FileResponse(name)
    raise HTTPException(404, detail=f"Missing file. Tried: {', '.join(candidates)}")

def find_existing_file(base: Path, stem: str) -> Optional[Path]:
    for ext in IMG_EXTS:
        p = base / f"{stem}{ext}"
        if p.exists():
            return p
    return None

def cache_busted(url: str) -> str:
    return f"{url}?v={int(time.time())}"

# ----------------------------
# Pages
# ----------------------------
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
    return serve_html("bookins4.html", "bookings.html")

# ----------------------------
# IMPORTANT: /media/{slot}
# Your HTML uses src="/media/<slot>" (no extension).
# We serve (1) uploaded replacement if present, else (2) a default from repo.
# ----------------------------
@app.get("/media/{slot}")
def media(slot: str):
    validate_slot(slot)

    # 1) admin replacement
    uploaded = find_existing_file(UPLOAD_DIR, slot)
    if uploaded:
        return FileResponse(uploaded)

    # 2) default/originals folder(s)
    for d in DEFAULT_MEDIA_DIRS:
        if d.exists() and d.is_dir():
            original = find_existing_file(d, slot)
            if original:
                return FileResponse(original)

    raise HTTPException(status_code=404, detail=f"Media not found for slot: {slot}")

# ----------------------------
# API for editor
# ----------------------------
@app.get("/manifest.json")
def manifest(request: Request):
    base = str(request.base_url).rstrip("/")
    out = {}

    # expose only uploaded replacements
    for ext in IMG_EXTS:
        for p in UPLOAD_DIR.glob(f"*{ext}"):
            out[p.stem] = cache_busted(f"{base}/media/{p.stem}")

    return JSONResponse(out)

@app.post("/admin/upload/{slot}")
async def upload(
    slot: str,
    file: UploadFile = File(...),
    x_admin_token: Optional[str] = Header(default=None),
    request: Request = None,
):
    require_admin(x_admin_token)
    validate_slot(slot)

    data = await file.read()
    if not data:
        raise HTTPException(400, "Empty file")

    # Store as .jpg for simplicity
    (UPLOAD_DIR / f"{slot}.jpg").write_bytes(data)

    base = str(request.base_url).rstrip("/") if request else ""
    url = cache_busted(f"{base}/media/{slot}") if base else cache_busted(f"/media/{slot}")
    return {"ok": True, "slot": slot, "url": url}

@app.delete("/admin/delete/{slot}")
def delete(
    slot: str,
    x_admin_token: Optional[str] = Header(default=None),
):
    require_admin(x_admin_token)
    validate_slot(slot)

    deleted = False
    for ext in IMG_EXTS:
        p = UPLOAD_DIR / f"{slot}{ext}"
        if p.exists():
            p.unlink()
            deleted = True

    return {"ok": True, "slot": slot, "deleted": deleted}
