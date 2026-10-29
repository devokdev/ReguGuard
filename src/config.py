"""
ReguGuard Central Configuration Loader
======================================
Loads application configurations, model selections, pricing tables, and paths.

Single Source of Truth: PRD §12
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Dict, Any
import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


# CONCEPT: Configuration Management
class Settings(BaseSettings):
    """Application settings with environment variable overrides."""
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # API Keys
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # Models
    GENERATOR_MODEL: str = "qwen/qwen3.8-27b"
    JUDGE_MODEL: str = "qwen/qwen3.8-27b"
    EMBEDDING_MODEL: str = "text-embedding-004"

    # Network Hosts & Ports
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    STREAMLIT_PORT: int = 8501
    A2A_SERVER_PORT: int = 8001
    BLACKBOARD_SERVER_PORT: int = 8002

    # Directories
    DATA_DIR: Path = BASE_DIR / "data"
    CORPUS_DIR: Path = BASE_DIR / "data" / "corpus"
    SMES_FILE: Path = BASE_DIR / "data" / "smes" / "smes.json"
    CASES_FILE: Path = BASE_DIR / "data" / "cases" / "cases.jsonl"
    PERSONAS_DIR: Path = BASE_DIR / "data" / "personas"
    EVAL_DIR: Path = BASE_DIR / "data" / "eval"
    CHROMA_DIR: Path = BASE_DIR / "data" / "chroma"
    DB_PATH: Path = BASE_DIR / "data" / "reguguard.db"
    TRACE_DB_PATH: Path = BASE_DIR / "data" / "traces.db"

    # Execution limits & controls
    MAX_USD_BUDGET: float = 10.0
    SEED: int = 42


settings = Settings()


def load_yaml(filepath: Path | str) -> Dict[str, Any]:
    """Helper to load a YAML file safely."""
    path = Path(filepath)
    if not path.is_absolute():
        path = BASE_DIR / path
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_pricing_config() -> Dict[str, Any]:
    """Load pricing specifications for cost tracking."""
    return load_yaml("config/pricing.yaml")


def get_models_config() -> Dict[str, Any]:
    """Load models specification."""
    return load_yaml("config/models.yaml")

