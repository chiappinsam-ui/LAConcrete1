import os, time, re
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Header, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# --- static folders (mount only if they exist) ---
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

# --- CORS (so your frontend domain can call the backend) ---
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

# --- uploads ---
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "devtoken")
SAFE_SLOT_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")  # allows img_<hash> slots too

def require_admin(x_admin_token: str | None):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

def validate_slot(slot: str):
    if not SAFE_SLOT_PATTERN.fullmatch(slot):
        raise HTTPException(status_code=400, detail="Invalid slot id")

def cache_busted(url: str) -> str:
    return f"{url}?v={int(time.time())}"

# --- pages ---
def serve_html(*candidates: str):
    for name in candidates:
        if os.path.exists(name):
            return FileResponse(name)
    raise HTTPException(404, detail=f"Missing file. Tried: {', '.join(candidates)}")

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

# --- API the editor uses ---
@app.get("/manifest.json")
def manifest(request: Request):
    base = str(request.base_url).rstrip("/")  # works on Render + local
    out = {}
    for p in UPLOAD_DIR.glob("*.jpg"):
        slot = p.stem
        out[slot] = cache_busted(f"{base}/uploads/{slot}.jpg")
    return JSONResponse(out)

@app.post("/admin/upload/{slot}")
async def upload(
    slot: str,
    file: UploadFile = File(...),
    x_admin_token: str | None = Header(default=None),
    request: Request = None,
):
    require_admin(x_admin_token)
    validate_slot(slot)

    data = await file.read()
    if not data:
        raise HTTPException(400, "Empty file")

    (UPLOAD_DIR / f"{slot}.jpg").write_bytes(data)

    base = str(request.base_url).rstrip("/") if request else ""
    url = cache_busted(f"{base}/uploads/{slot}.jpg") if base else cache_busted(f"/uploads/{slot}.jpg")
    return {"ok": True, "slot": slot, "url": url}
