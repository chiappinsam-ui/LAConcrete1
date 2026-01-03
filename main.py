import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Mount static folders if they exist (CRITICAL for *_files assets)
for folder in [
    "assets",
    "index1_files",
    "menu2_files",
    "gallery5_files",
    "contact6_files",
    "catering3_files",
    "bookins4html_files",
    "uploads",  # only if you actually have this folder
]:
    if os.path.isdir(folder):
        app.mount(f"/{folder}", StaticFiles(directory=folder), name=folder)


def serve(name: str):
    if not os.path.exists(name):
        raise HTTPException(404, f"Missing file: {name}")
    return FileResponse(name)


@app.get("/health")
def health():
    return JSONResponse({"ok": True})


# Pages
@app.get("/")
def home():
    return serve("index1.html")  # or index.html if that's the real one


@app.get("/menu")
def menu():
    return serve("menu2.html")


@app.get("/gallery")
def gallery():
    return serve("gallery5.html")


@app.get("/contact")
def contact():
    return serve("contact6.html")


@app.get("/catering")
def catering():
    return serve("catering3.html")


@app.get("/bookings")
def bookings():
    return serve("bookins4.html")  # double-check spelling


@app.get("/supabase-config.js")
def supabase_config():
    return serve("supabase-config.js")


@app.get("/supabase-init.js")
def supabase_init():
    return serve("supabase-init.js")


@app.get("/inline-edit.js")
def inline_edit():
    return serve("inline-edit.js")
