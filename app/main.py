from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

# Import the application settings and the API router
from app.core.config import settings
from app.api.endpoints import tracking

# --- FastAPI App Initialization ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)

# --- Setup Monitoring ---
# This is the correct way to instrument the app.
# It's done at startup to avoid the "middleware after application has started" error.
@app.on_event("startup")
async def startup():
    # The instrumentator will automatically discover and expose the custom metrics
    # defined in other modules (like tracking.py).
    Instrumentator().instrument(app).expose(app)


# --- CORS Middleware ---
# This must be added before including routers.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include API Routers ---
app.include_router(tracking.router, prefix=settings.API_V1_STR)

# --- Root Endpoint ---
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to the {settings.PROJECT_NAME}!"}