"""
Paytm Campus OS — FastAPI Backend
==================================
AI-powered campus travel & payments platform for Indian college students.

Run: uvicorn main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from routers import dashboard, yatra, gharwaapsi, concession, campuspay, festpass, kharcha

# ── App Configuration ──────────────────────────────────────
app = FastAPI(
    title="Paytm Campus OS API",
    description="AI-powered campus travel & payments backend for Indian college students",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS Middleware ────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",       # Vite dev server
        "http://localhost:5173",       # Vite default
        "http://localhost:3000",       # Fallback
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ──────────────────────────────────────
app.include_router(dashboard.router)
app.include_router(yatra.router)
app.include_router(gharwaapsi.router)
app.include_router(concession.router)
app.include_router(campuspay.router)
app.include_router(festpass.router)
app.include_router(kharcha.router)


# ── Health Check ───────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "app": "Paytm Campus OS API",
        "version": "1.0.0",
        "status": "running ✅",
        "docs": "/docs",
        "endpoints": [
            "/api/dashboard",
            "/api/yatra/chat",
            "/api/yatra/plan",
            "/api/yatra/chips",
            "/api/gharwaapsi/route",
            "/api/gharwaapsi/hostelmates",
            "/api/gharwaapsi/tatkal",
            "/api/gharwaapsi/papa-pay",
            "/api/concession/stations",
            "/api/concession/calculate",
            "/api/concession/bonafide",
            "/api/campuspay/balance",
            "/api/campuspay/spending",
            "/api/campuspay/debts",
            "/api/campuspay/settle",
            "/api/campuspay/categories",
            "/api/festpass/featured",
            "/api/festpass/list",
            "/api/festpass/book",
            "/api/kharcha/report",
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
