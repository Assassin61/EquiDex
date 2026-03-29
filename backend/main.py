from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import load_config
from backend.adapters.sqlite import SQLiteAdapter
from backend.routers.audit import router as audit_router  # ADD THIS

app = FastAPI(
    title="FairProbe",
    description="AI Bias Auditing Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(audit_router)  # ADD THIS

@app.on_event("startup")
async def startup():
    app.state.config = load_config()
    app.state.db = SQLiteAdapter(app.state.config)
    print("FairProbe started successfully")

@app.get("/")
async def root():
    return {
        "status": "running",
        "product": "FairProbe",
        "version": "1.0.0"
    }