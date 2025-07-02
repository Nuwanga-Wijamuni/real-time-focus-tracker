from prometheus_fastapi_instrumentator import Instrumentator

# Create a single instance of the Instrumentator to be shared across the application.
# This ensures all custom metrics are registered with the same instrumentator
# that is attached to the FastAPI app.
instrumentator = Instrumentator()