import os

class Settings:
    """
    A class to hold all application settings.

    Using a class for settings provides a clear, organized, and centralized
    way to manage configuration variables. It makes it easy to import and
    use settings across different modules of the application.
    """
    # --- Project Information ---
    PROJECT_NAME: str = "Real-time AI Focus & Attention Tracker"
    PROJECT_VERSION: str = "1.0.0"

    # --- API Configuration ---
    # The prefix for all API routes. For example, endpoints will be at /api/v1/...
    API_V1_STR: str = "/api/v1"

    # --- WebSocket Configuration ---
    # The host for the WebSocket server. "0.0.0.0" makes it accessible from
    # other devices on the same network (including Docker containers).
    WEBSOCKET_HOST: str = "0.0.0.0"
    WEBSOCKET_PORT: int = 8000

    # --- Focus Analyzer Thresholds ---
    # These values define the sensitivity of the focus detection.
    # They can be tuned here without changing the core logic.
    
    # Yaw angle (left/right turn) threshold in degrees.
    # A value greater than this will be considered a distraction.
    YAW_THRESHOLD: int = 25

    # Positive pitch angle (looking up) threshold in degrees.
    PITCH_THRESHOLD_POS: int = 20
    
    # Negative pitch angle (looking down) threshold in degrees.
    PITCH_THRESHOLD_NEG: int = -20


# Create a single instance of the Settings class that can be imported
# and used throughout the application. This is a common pattern to ensure
# that settings are loaded only once.
settings = Settings()

# Example of how you might use an environment variable (optional)
# This allows you to override a setting without changing the code,
# which is useful for production deployments.
# For example, you could set an environment variable `WEBSOCKET_PORT=8080`
# settings.WEBSOCKET_PORT = int(os.getenv("WEBSOCKET_PORT", settings.WEBSOCKET_PORT))