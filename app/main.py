from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import api

app = FastAPI(
    title="F1 API Backend",
    description="Backend API for live and historical Formula 1 data using FastF1",
    version="1.0.0",
    docs_url="/docs",         # Swagger UI (default: /docs)
    redoc_url="/redoc",       # ReDoc documentation (default: /redoc)
    openapi_url="/openapi.json"  # OpenAPI schema URL
)

# CORS settings for Next.js & Discord bot
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all in dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(api.router, prefix="/api/api", tags=["F1 Data"])

@app.get("/", summary="Health Check")
def root():
    return {"status": "Backend running"}
