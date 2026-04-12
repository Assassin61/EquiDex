from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import load_config
from backend.adapters.sqlite import SQLiteAdapter
from backend.routers.audit import router as audit_router
from backend.routers.actions import router as actions_router
from backend.routers.stats import router as stats_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle for FairProbe."""
    config = load_config()
    app.state.config = config

    # Config-driven database adapter selection
    db_type = config["database"]["type"]
    if db_type == "firebase":
        from backend.adapters.firebase import FirebaseAdapter
        app.state.db = FirebaseAdapter(config)
    else:
        app.state.db = SQLiteAdapter(config)

    print(f"FairProbe started successfully (db={db_type})")
    yield


app = FastAPI(
    title="FairProbe",
    description="AI Bias Auditing Platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(audit_router)
app.include_router(actions_router)
app.include_router(stats_router)


@app.get("/")
async def root():
    return {
        "status": "running",
        "product": "FairProbe",
        "version": "1.0.0"
    }