"""Pydantic models for the Dockerfile Generator API"""
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


class InputType(str, Enum):
    """Type of input provided by user"""
    GITHUB_URL = "github_url"
    ZIP_FILE = "zip_file"


class Language(str, Enum):
    """Supported programming languages/frameworks"""
    NODEJS = "nodejs"
    PYTHON = "python"
    GO = "go"
    JAVA = "java"
    RUST = "rust"
    DOTNET = "dotnet"
    PHP = "php"
    RUBY = "ruby"
    DART = "dart"
    ELIXIR = "elixir"
    HASKELL = "haskell"
    SCALA = "scala"
    KOTLIN = "kotlin"
    SWIFT = "swift"
    BUN = "bun"
    DENO = "deno"
    UNKNOWN = "unknown"


class Framework(str, Enum):
    """Detected frameworks per language"""
    # Node.js
    EXPRESS = "express"
    NESTJS = "nestjs"
    NEXTJS = "nextjs"
    NUXT = "nuxt"
    REACT = "react"
    VUE = "vue"
    SVELTE = "svelte"
    ASTRO = "astro"
    REMI = "remix"
    FASTIFY = "fastify"
    KOA = "koa"
    HONO = "hono"
    
    # Python
    FASTAPI = "fastapi"
    DJANGO = "django"
    FLASK = "flask"
    STARLETTE = "starlette"
    TORNADO = "tornado"
    SANIC = "sanic"
    QUART = "quart"
    LITESTAR = "litestar"
    STREAMLIT = "streamlit"
    GRADIO = "gradio"
    
    # Go
    GIN = "gin"
    ECHO = "echo"
    FIBER = "fiber"
    CHI = "chi"
    GO_STD = "go_std"
    
    # Java
    SPRING_BOOT = "spring_boot"
    QUARKUS = "quarkus"
    MICRONAUT = "micronaut"
    VERTX = "vertx"
    HELIDON = "helidon"
    MAVEN = "maven"
    GRADLE = "gradle"
    
    # Rust
    ACTIX = "actix"
    AXUM = "axum"
    ROCKET = "rocket"
    WARP = "warp"
    POEM = "poem"
    
    # .NET
    ASPNET_CORE = "aspnet_core"
    
    # PHP
    LARAVEL = "laravel"
    SYMFONY = "symfony"
    SLIM = "slim"
    LUMEN = "lumen"
    
    # Ruby
    RAILS = "rails"
    SINATRA = "sinatra"
    HANNAMI = "hanami"
    
    # Generic
    STATIC_SITE = "static_site"
    DOCKER_COMPOSE = "docker_compose"
    UNKNOWN = "unknown"


class ProjectInfo(BaseModel):
    """Information detected from the project"""
    language: Language = Language.UNKNOWN
    framework: Framework = Framework.UNKNOWN
    package_manager: Optional[str] = None
    entry_point: Optional[str] = None
    build_command: Optional[str] = None
    start_command: Optional[str] = None
    port: Optional[int] = None
    dependencies: Dict[str, str] = Field(default_factory=dict)
    dev_dependencies: Dict[str, str] = Field(default_factory=dict)
    config_files: List[str] = Field(default_factory=list)
    dockerfile_exists: bool = False
    dockerignore_exists: bool = False


class GitHubInput(BaseModel):
    """GitHub repository input"""
    url: HttpUrl
    branch: Optional[str] = "main"
    access_token: Optional[str] = None  # For private repos


class ZipInput(BaseModel):
    """Zip file input (base64 encoded)"""
    filename: str
    content_base64: str


class GenerateRequest(BaseModel):
    """Request to generate a Dockerfile"""
    input_type: InputType
    github: Optional[GitHubInput] = None
    zip: Optional[ZipInput] = None
    options: Optional["GenerationOptions"] = None


class GenerationOptions(BaseModel):
    """Options for Dockerfile generation"""
    multi_stage: bool = True
    optimize_layers: bool = True
    security_hardening: bool = True
    base_image: Optional[str] = None  # Override default base image
    target_platform: str = "linux/amd64"
    expose_port: Optional[int] = None
    env_vars: Dict[str, str] = Field(default_factory=dict)
    ai_optimization: bool = True  # Enable AI optimization tips


class DockerfileResult(BaseModel):
    """Generated Dockerfile result"""
    dockerfile: str
    project_info: ProjectInfo
    optimizations_applied: List[str] = Field(default_factory=list)
    ai_suggestions: Optional[List[str]] = None
    warnings: List[str] = Field(default_factory=list)
    estimated_image_size_mb: Optional[float] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str = "0.1.0"
    ollama_available: bool = False


# Update forward references
GenerateRequest.model_rebuild()