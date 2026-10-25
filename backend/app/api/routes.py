"""API routes for Dockerfile generation"""
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import HttpUrl

from ..models.schemas import (
    GenerateRequest, GenerationOptions, DockerfileResult,
    GitHubInput, ZipInput, InputType, HealthResponse,
)
from ..github import analyze_github_repo, validate_github_repo
from ..zip import analyze_zip_file, validate_zip_file
from ..generator import generate_dockerfile
from ..detection import detect_project
from ..core.config import get_settings


router = APIRouter(prefix="/api/v1", tags=["dockerfile"])
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    ollama_available = False
    try:
        from ..ai import get_ai_optimizer
        optimizer = get_ai_optimizer()
        if optimizer and settings.ollama_enabled:
            ollama_available = await optimizer.check_availability()
    except Exception:
        pass
    
    return HealthResponse(
        status="healthy",
        version=settings.version,
        ollama_available=ollama_available,
    )


@router.post("/validate/github")
async def validate_github(github_input: GitHubInput):
    """Validate GitHub repository accessibility"""
    result = await validate_github_repo(github_input)
    if not result.get("valid"):
        raise HTTPException(status_code=400, detail=result)
    return result


@router.post("/validate/zip")
async def validate_zip(zip_input: ZipInput):
    """Validate zip file"""
    result = validate_zip_file(zip_input, settings.max_zip_size_mb)
    if not result.get("valid"):
        raise HTTPException(status_code=400, detail=result)
    return result


@router.post("/analyze/github", response_model=DockerfileResult)
async def analyze_github(github_input: GitHubInput, options: Optional[GenerationOptions] = None):
    """Analyze GitHub repo and generate Dockerfile"""
    if options is None:
        options = GenerationOptions()
    
    project_info = await analyze_github_repo(github_input)
    result = generate_dockerfile(project_info, options)
    return result


@router.post("/analyze/zip", response_model=DockerfileResult)
async def analyze_zip(zip_input: ZipInput, options: Optional[GenerationOptions] = None):
    """Analyze zip file and generate Dockerfile"""
    if options is None:
        options = GenerationOptions()
    
    project_info = analyze_zip_file(zip_input, settings.max_zip_size_mb)
    result = generate_dockerfile(project_info, options)
    return result


@router.post("/generate", response_model=DockerfileResult)
async def generate_dockerfile_endpoint(request: GenerateRequest):
    """Generate Dockerfile from GitHub URL or zip file"""
    options = request.options or GenerationOptions()
    
    if request.input_type == InputType.GITHUB_URL:
        if not request.github:
            raise HTTPException(status_code=400, detail="GitHub input required")
        project_info = await analyze_github_repo(request.github)
    elif request.input_type == InputType.ZIP_FILE:
        if not request.zip:
            raise HTTPException(status_code=400, detail="Zip input required")
        project_info = analyze_zip_file(request.zip, settings.max_zip_size_mb)
    else:
        raise HTTPException(status_code=400, detail="Invalid input type")
    
    result = generate_dockerfile(project_info, options)
    return result


@router.post("/generate/file", response_class=PlainTextResponse)
async def generate_dockerfile_file(
    github_url: Optional[str] = Form(None),
    github_branch: str = Form("main"),
    github_token: Optional[str] = Form(None),
    zip_file: Optional[UploadFile] = File(None),
    multi_stage: bool = Form(True),
    optimize_layers: bool = Form(True),
    security_hardening: bool = Form(True),
    base_image: Optional[str] = Form(None),
    expose_port: Optional[int] = Form(None),
    ai_optimization: bool = Form(True),
):
    """Generate Dockerfile and return as plain text file"""
    options = GenerationOptions(
        multi_stage=multi_stage,
        optimize_layers=optimize_layers,
        security_hardening=security_hardening,
        base_image=base_image,
        expose_port=expose_port,
        ai_optimization=ai_optimization,
    )
    
    if github_url:
        github_input = GitHubInput(
            url=HttpUrl(github_url),
            branch=github_branch,
            access_token=github_token,
        )
        project_info = await analyze_github_repo(github_input)
    elif zip_file:
        content = await zip_file.read()
        import base64
        zip_input = ZipInput(
            filename=zip_file.filename or "upload.zip",
            content_base64=base64.b64encode(content).decode(),
        )
        project_info = analyze_zip_file(zip_input, settings.max_zip_size_mb)
    else:
        raise HTTPException(status_code=400, detail="Either github_url or zip_file required")
    
    result = generate_dockerfile(project_info, options)
    return result.dockerfile


@router.post("/analyze/local")
async def analyze_local_project(path: str = Form(...)):
    """Analyze local project directory (for development/testing)"""
    from pathlib import Path
    project_path = Path(path)
    if not project_path.exists() or not project_path.is_dir():
        raise HTTPException(status_code=400, detail="Invalid path")
    
    project_info = detect_project(project_path)
    return {
        "language": project_info.language.value,
        "framework": project_info.framework.value,
        "package_manager": project_info.package_manager,
        "entry_point": project_info.entry_point,
        "build_command": project_info.build_command,
        "start_command": project_info.start_command,
        "port": project_info.port,
        "dependencies_count": len(project_info.dependencies),
        "config_files": project_info.config_files,
    }


@router.get("/languages")
async def list_supported_languages():
    """List supported languages and frameworks"""
    from ..models.schemas import Language, Framework
    return {
        "languages": [{"value": l.value, "name": l.name} for l in Language],
        "frameworks": [{"value": f.value, "name": f.name} for f in Framework],
    }


@router.get("/templates/{language}")
async def get_template_preview(language: str, framework: Optional[str] = None):
    """Preview Dockerfile template for a language/framework"""
    from ..models.schemas import Language, Framework
    from ..templates import TemplateEngine
    from ..models.schemas import ProjectInfo, GenerationOptions
    
    try:
        lang = Language(language)
        fw = Framework(framework) if framework else Framework.UNKNOWN
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid language or framework")
    
    # Create minimal project info for preview
    project_info = ProjectInfo(language=lang, framework=fw)
    options = GenerationOptions(multi_stage=True)
    
    engine = TemplateEngine()
    context = {
        "language": lang.value,
        "framework": fw.value,
        "base_image": "node:20-alpine",
        "runtime_image": "node:20-alpine",
        "port": 3000,
        "lock_file": None,
        "build_deps": "python3 make g++",
        "install_cmd": "npm ci",
        "build_cmd": "npm run build",
        "start_cmd": "node index.js",
        "entry_point": "index.js",
        "binary_name": "main",
        "jar_name": "app.jar",
        "assembly_name": "App",
        "health_check": None,
        "output_dir": "dist",
        "static_dir": None,
        "main_package": ".",
        "arch": "amd64",
        "req_file": "requirements.txt",
        "pyproject": False,
        "poetry_lock": False,
        "pipfile": False,
        "csproj": None,
        "app_name": "app",
        "nginx_config": None,
    }
    
    dockerfile = engine.render(lang, fw, context, multi_stage=True)
    return {"dockerfile": dockerfile}