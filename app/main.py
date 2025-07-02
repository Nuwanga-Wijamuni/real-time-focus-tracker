from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the application settings, API router, and the new shared instrumentator
from app.core.config import settings
from app.api.endpoints import tracking
from app.core.instrumentation import instrumentator

# Create the main FastAPI application instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)

# --- Expose Prometheus Metrics ---
# This is the key change. We now explicitly instrument the app
# and expose the /metrics endpoint using our shared instrumentator.
instrumentator.instrument(app).expose(app)

# --- CORS (Cross-Origin Resource Sharing) Middleware ---
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
    """
    A simple root endpoint to confirm the API is running.
    """
    return {"message": f"Welcome to the {settings.PROJECT_NAME}!"}