"""
Configuration Management for DataWise AI
Loads environment variables and provides configuration settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application Settings"""
    
    # API Keys
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    
    # Database Configuration
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "datawise_ai")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "postgres123")
    
    # Application Settings
    app_port: int = int(os.getenv("APP_PORT", "8501"))
    debug_mode: bool = os.getenv("DEBUG_MODE", "True").lower() == "true"
    
    # ChromaDB Configuration
    chroma_host: str = os.getenv("CHROMA_HOST", "localhost")
    chroma_port: int = int(os.getenv("CHROMA_PORT", "8000"))
    chroma_persist_dir: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")
    
    # File Upload Settings
    max_upload_size_mb: int = 200
    allowed_extensions: list = [".csv", ".xlsx", ".xls", ".json"]
    
    # Paths
    base_dir: Path = Path(__file__).parent
    upload_dir: Path = base_dir / "uploads"
    data_dir: Path = base_dir / "data"
    reports_dir: Path = base_dir / "reports"
    logs_dir: Path = base_dir / "logs"
    
    # Gemini Model Configuration
    # Try different models in order: gemini-2.0-flash-exp, gemini-1.5-flash, gemini-pro
    gemini_model: str = "gemini-2.0-flash-exp"
    gemini_temperature: float = 0.7
    gemini_max_tokens: int = 2048
    
    # ChromaDB Settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create necessary directories
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.upload_dir,
            self.data_dir,
            self.reports_dir,
            self.logs_dir,
            Path(self.chroma_persist_dir)
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @property
    def database_url(self) -> str:
        """Get PostgreSQL connection URL"""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL"""
        return self.database_url
    
    def validate_gemini_key(self) -> bool:
        """Validate if Gemini API key is present"""
        return bool(self.gemini_api_key and len(self.gemini_api_key) > 0)


# Global settings instance
settings = Settings()


# Validation on import
def safe_print(text):
    """Print with encoding fallback for Windows console"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback to ASCII-safe version
        print(text.encode('ascii', 'ignore').decode('ascii'))

if not settings.validate_gemini_key():
    safe_print("⚠️  WARNING: GEMINI_API_KEY not found in .env file!")
    safe_print("Please add your API key to the .env file")
else:
    safe_print("✅ Configuration loaded successfully!")
    safe_print(f"📁 Upload directory: {settings.upload_dir}")
    safe_print(f"🗄️  Database: {settings.db_name}")
    safe_print(f"🤖 AI Model: {settings.gemini_model}")

