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

# --- Setup Monitoring ---
# THIS IS THE CORRECT ORDER: This must be the LAST thing you do to the app object.
# It instruments the app and exposes the /metrics endpoint.
Instrumentator().instrument(app).expose(app)


# --- Root Endpoint ---
@app.get("/", tags=["Root"])
async def read_root():
    """
    A simple root endpoint to confirm the API is running.
    """
    return {"message": f"Welcome to the {settings.PROJECT_NAME}!"}