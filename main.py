from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field
import re
import time, json
from fastapi.staticfiles import StaticFiles

app = FastAPI()
templates = Jinja2Templates(directory=".")

app.mount("/static", StaticFiles(directory="."), name="static")

# INDEX PAGE
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# User Model
class User(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    phone: str = Field(min_length=10, max_length=10)

@app.get("/login-page", response_class=HTMLResponse)
def get_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
# API
@app.post("/login-page")
def register(user: User):

    # Phone validation
    if not re.fullmatch(r"\d{10}", user.phone):
        return {
            "status": "error",
            "message": "Invalid phone number (10 digits required)"
        }

    # Indian number check
    if not user.phone.startswith(("6","7","8","9")):
        return {
            "status": "error",
            "message": "Invalid Indian phone number"
        }

    # Name validation
    if any(char.isdigit() for char in user.name):
        return {
            "status": "error",
            "message": "Name should not contain numbers"
        }

    return {
        "status": "success",
        "message": "User data received successfully",
        "data": user.dict()
    }

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# ---------------- MESSAGE SCAM DETECTION ----------------
@app.post("/check-message")
def check_message(data: dict):
    text = data.get("text", "").lower()

    scam_keywords = [
        "win", "lottery", "urgent", "otp", "bank",
        "free money", "click here", "limited offer"
    ]

    score = 0

    for word in scam_keywords:
        if word in text:
            score += 15

    # Cap score at 100
    score = min(score, 100)

    return {
        "message": text,
        "scam_score": score,
        "result": "SCAM" if score > 40 else "SAFE"
    }
@app.get("/message", response_class=HTMLResponse)
def message_page(request: Request):
    return templates.TemplateResponse("message.html", {"request": request})

# ---------------- WEBSITE CHECK ----------------
@app.post("/check-website")
def check_website(data: dict):
    url = data.get("url", "").lower()

    score = 0

    # 1. HTTPS check
    if not url.startswith("https"):
        score += 30

    # 2. Suspicious keywords
    keywords = ["login", "verify", "bank", "secure", "account", "update"]
    for word in keywords:
        if word in url:
            score += 10

    # 3. Too long URL
    if len(url) > 50:
        score += 10

    # 4. Too many dots (fake domains)
    if url.count('.') > 3:
        score += 20

    score = min(score, 100)

    return {
        "url": url,
        "risk_score": score,
        "result": "SCAM" if score > 40 else "SAFE"
    }
@app.get("/check-website", response_class=HTMLResponse)
def website_page(request: Request):
    return templates.TemplateResponse("website.html", {"request": request})

@app.get("/call-scan", response_class=HTMLResponse)
def voice_page(request: Request):
    return templates.TemplateResponse("voice.html", {"request": request})

import os

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
