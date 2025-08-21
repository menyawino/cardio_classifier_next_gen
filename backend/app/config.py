"""Configuration helpers for backend."""
from pydantic import BaseModel
import os

class Settings(BaseModel):
    environment: str = os.getenv("ENVIRONMENT", "dev")
    mcp_server_url: str = os.getenv("MCP_SERVER_URL", "http://mcp:8100")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./dev.db")
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret-change")

def get_settings() -> Settings:
    return Settings()
