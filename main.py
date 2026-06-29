import webbrowser
import threading
import time
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from routes.export_routes import export_router
from routes.expense_routes import expense_router
from routes.report_routes import report_router
from routes.user_routes import user_router

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI()
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(expense_router)
app.include_router(report_router)
app.include_router(export_router)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.middleware("http")
async def disable_cache_for_frontend(request: Request, call_next):
    response = await call_next(request)
    if request.url.path == "/" or request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


def open_browser():
    """Open the application in Google Chrome after a short delay."""
    time.sleep(2)  # Wait for server to start
    try:
        # Try to open with Chrome/Google
        chrome_browser = webbrowser.get('chrome')
        chrome_browser.open("http://127.0.0.1:8000")
    except Exception:
        try:
            # Fallback: Try common Chrome paths on Windows
            import subprocess
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(
                    os.environ.get('USERNAME', 'User')
                )
            ]
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    subprocess.Popen([chrome_path, "http://127.0.0.1:8000"])
                    return
            # If Chrome not found, use default browser
            webbrowser.open("http://127.0.0.1:8000")
        except Exception:
            # Final fallback to default browser
            webbrowser.open("http://127.0.0.1:8000")


@app.on_event("startup")
def startup_event():
    """Start the browser opening in a separate thread."""
    thread = threading.Thread(target=open_browser, daemon=True)
    thread.start()


@app.get("/", response_class=HTMLResponse)
def home():
    return FRONTEND_DIR.joinpath("index.html").read_text(encoding="utf-8")
