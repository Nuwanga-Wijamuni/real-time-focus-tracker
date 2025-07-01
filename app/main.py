from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the application settings and the API router
from app.core.config import settings
from app.api.endpoints import tracking

# Create the main FastAPI application instance
# The title and version are pulled from your central settings file
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)

# --- CORS (Cross-Origin Resource Sharing) Middleware ---
# This is a crucial security feature that controls which domains are allowed
# to communicate with your API. For development, it's common to allow all
# origins, but for production, you should restrict this to your frontend's
# domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


# --- Include API Routers ---
# This line includes all the routes defined in the tracking.py file.
# The `prefix` ensures that all routes in that file will start with /api/v1.
# For example, the /ws WebSocket route will be available at /api/v1/ws.
app.include_router(tracking.router, prefix=settings.API_V1_STR)


# --- Root Endpoint ---
# This is a simple endpoint at the root of the API (e.g., http://localhost:8000/)
# It's useful for a quick "health check" to see if the server is running.
@app.get("/", tags=["Root"])
async def read_root():
    """
    A simple root endpoint to confirm the API is running.
    """
    return {"message": f"Welcome to the {settings.PROJECT_NAME}!"}