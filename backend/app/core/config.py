"""
MindGuard AI - Backend Configuration
=======================================
All configuration comes from environment variables (loaded from a .env
file that is NEVER committed to version control - see .env.example for
the template). This follows the "never hardcode secrets" rule from the
project spec.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Database ---
    # Format: mysql+pymysql://<user>:<password>@<host>:<port>/<database>
    DATABASE_URL: str

    # --- JWT Auth ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- App ---
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = "http://localhost:5173"  # Vite's default dev port

    # --- ML ---
    ML_MODEL_PATH: str = "../ml/artifacts/risk_model.joblib"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Single shared settings instance, imported everywhere else in the app
settings = Settings()