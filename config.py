"""Configuration settings for HK Travel Planner."""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class LLMConfig:
    """Configuration for LLM integration."""
    api_key: str
    base_url: str
    model: str
    max_tokens: int = 2000
    temperature: float = 0.7
    timeout: int = 30

@dataclass
class AppConfig:
    """Main application configuration."""
    llm: LLMConfig
    debug: bool = False
    cache_enabled: bool = True

def get_config() -> AppConfig:
    """Get application configuration."""
    
    # LLM Configuration - using provided Akash Network settings
    llm_config = LLMConfig(
        api_key="sk-UVKYLhiNf0MKXRqbnDiehA",
        base_url="https://chatapi.akash.network/api/v1",
        model="DeepSeek-R1-Distill-Llama-70B",
        max_tokens=2000,
        temperature=0.7,
        timeout=30
    )
    
    return AppConfig(
        llm=llm_config,
        debug=os.getenv("DEBUG", "false").lower() == "true",
        cache_enabled=os.getenv("CACHE_ENABLED", "true").lower() == "true"
    )