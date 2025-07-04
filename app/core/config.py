from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application-wide settings.
    """
    PROJECT_NAME: str = "AI Focus & Attention Tracker"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Head pose analysis thresholds
    YAW_THRESHOLD: int = 20
    PITCH_THRESHOLD_POS: int = 20
    PITCH_THRESHOLD_NEG: int = -15

    class Config:
        case_sensitive = True

settings = Settings()
