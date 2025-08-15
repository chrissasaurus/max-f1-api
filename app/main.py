from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import f1

app = FastAPI(title="F1 API Backend", version="1.0.0")

# CORS settings for Next.js & Discord bot
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in dev, allow all; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(f1.router, prefix="/api/f1", tags=["F1 Data"])

@app.get("/")
def root():
    return {"status": "Backend running"}
