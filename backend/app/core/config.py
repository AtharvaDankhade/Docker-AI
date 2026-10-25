"""Configuration management"""
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    app_name: str = "Dockerfile Generator"
    version: str = "0.1.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # GitHub
    github_token: Optional[str] = None
    github_api_url: str = "https://api.github.com"
    github_clone_depth: int = 1
    github_clone_timeout: int = 120
    
    # File processing
    max_zip_size_mb: int = 100
    max_github_repo_size_mb: int = 500
    temp_dir: str = "/tmp/dockerfile-gen"
    
    # Ollama (AI optimization)
    ollama_enabled: bool = False
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "codellama:7b"
    ollama_timeout: int = 60
    
    # Dockerfile generation defaults
    default_base_images: dict = Field(default_factory=lambda: {
        "nodejs": "node:20-alpine",
        "python": "python:3.12-alpine",
        "go": "golang:1.22-alpine",
        "java": "eclipse-temurin:21-jdk-alpine",
        "rust": "rust:1.79-alpine",
        "dotnet": "mcr.microsoft.com/dotnet/sdk:8.0-alpine",
        "php": "php:8.3-alpine",
        "ruby": "ruby:3.3-alpine",
        "dart": "dart:3.4-alpine",
        "elixir": "elixir:1.15-alpine",
        "haskell": "haskell:9.8-alpine",
        "scala": "eclipse-temurin:21-jdk-alpine",
        "kotlin": "eclipse-temurin:21-jdk-alpine",
        "swift": "swift:5.10-alpine",
        "bun": "oven/bun:1.1-alpine",
        "deno": "denoland/deno:alpine",
    })
    
    # Runtime base images (for multi-stage)
    default_runtime_images: dict = Field(default_factory=lambda: {
        "nodejs": "node:20-alpine",
        "python": "python:3.12-alpine",
        "go": "alpine:3.20",
        "java": "eclipse-temurin:21-jre-alpine",
        "rust": "alpine:3.20",
        "dotnet": "mcr.microsoft.com/dotnet/aspnet:8.0-alpine",
        "php": "php:8.3-fpm-alpine",
        "ruby": "ruby:3.3-alpine",
        "dart": "dart:3.4-runtime-alpine",
        "elixir": "elixir:1.15-alpine",
        "haskell": "debian:bookworm-slim",
        "scala": "eclipse-temurin:21-jre-alpine",
        "kotlin": "eclipse-temurin:21-jre-alpine",
        "swift": "swift:5.10-slim",
        "bun": "oven/bun:1.1-alpine",
        "deno": "denoland/deno:alpine",
    })
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()