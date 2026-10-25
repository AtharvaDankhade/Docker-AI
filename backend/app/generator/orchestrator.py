"""Dockerfile generation orchestration module"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ..models.schemas import (
    ProjectInfo, GenerationOptions, DockerfileResult,
    Language, Framework
)
from ..core.config import get_settings
from ..templates import TemplateEngine
from ..detection import LanguageDetector
from ..ai import get_ai_optimizer


@dataclass
class GenerationContext:
    """Context for Dockerfile generation"""
    project_info: ProjectInfo
    options: GenerationOptions
    settings: Any
    template_engine: TemplateEngine


class DockerfileGenerator:
    """Orchestrates Dockerfile generation"""
    
    def __init__(self):
        self.settings = get_settings()
        self.template_engine = TemplateEngine()
        self.detector = LanguageDetector()
    
    def generate(self, project_info: ProjectInfo, options: GenerationOptions) -> DockerfileResult:
        """Generate Dockerfile from project info"""
        context = GenerationContext(
            project_info=project_info,
            options=options,
            settings=self.settings,
            template_engine=self.template_engine,
        )
        
        # Build template context
        template_context = self._build_template_context(context)
        
        # Select template and render
        dockerfile = self.template_engine.render(
            language=project_info.language,
            framework=project_info.framework,
            context=template_context,
            multi_stage=options.multi_stage,
        )
        
        # Track applied optimizations
        optimizations = self._get_applied_optimizations(context)
        
        # Get AI suggestions if enabled
        ai_suggestions = None
        if options.ai_optimization:
            ai_suggestions = self._get_ai_suggestions(context, dockerfile)
        
        # Validate generated Dockerfile
        warnings = self._validate_dockerfile(dockerfile, context)
        
        # Estimate image size
        estimated_size = self._estimate_image_size(context)
        
        return DockerfileResult(
            dockerfile=dockerfile,
            project_info=project_info,
            optimizations_applied=optimizations,
            ai_suggestions=ai_suggestions,
            warnings=warnings,
            estimated_image_size_mb=estimated_size,
        )
    
    def _build_template_context(self, context: GenerationContext) -> Dict:
        """Build context dictionary for template rendering"""
        project = context.project_info
        options = context.options
        settings = context.settings
        
        # Determine base images
        lang_key = project.language.value
        base_image = options.base_image or settings.default_base_images.get(lang_key, "alpine:latest")
        runtime_image = settings.default_runtime_images.get(lang_key, "alpine:latest")
        
        # Determine port
        port = options.expose_port or project.port or self._get_default_port(project.framework)
        
        # Determine lock file
        lock_file = self._get_lock_file(project)
        
        # Determine build dependencies
        build_deps = self._get_build_deps(project.language)
        
        # Determine install command
        install_cmd = self._get_install_command(project)
        
        # Determine binary/jar names
        binary_name = self._get_binary_name(project)
        jar_name = self._get_jar_name(project)
        assembly_name = self._get_assembly_name(project)
        
        # Determine entry point and commands
        entry_point = project.entry_point or self._get_default_entry_point(project)
        build_cmd = project.build_command or self._get_default_build_command(project)
        start_cmd = project.start_command or self._get_default_start_command(project)
        
        # Health check
        health_check = self._get_health_check(project, port)
        
        # Output directory for static sites/Next.js
        output_dir = self._get_output_dir(project)
        
        return {
            "language": project.language.value,
            "framework": project.framework.value,
            "base_image": base_image,
            "runtime_image": runtime_image,
            "port": port,
            "lock_file": lock_file,
            "build_deps": build_deps,
            "install_cmd": install_cmd,
            "build_cmd": build_cmd,
            "start_cmd": start_cmd,
            "entry_point": entry_point,
            "binary_name": binary_name,
            "jar_name": jar_name,
            "assembly_name": assembly_name,
            "health_check": health_check,
            "output_dir": output_dir,
            "static_dir": self._get_static_dir(project),
            "main_package": self._get_main_package(project),
            "arch": "amd64",  # Could be made configurable
            "req_file": self._get_req_file(project),
            "pyproject": (project.config_files and "pyproject.toml" in project.config_files),
            "poetry_lock": (project.config_files and "poetry.lock" in project.config_files),
            "pipfile": (project.config_files and "Pipfile" in project.config_files),
            "csproj": self._get_csproj(project),
            "app_name": self._get_app_name(project),
            "nginx_config": self._get_nginx_config(project),
        }
    
    def _get_default_port(self, framework: Framework) -> int:
        """Get default port for framework"""
        defaults = {
            Framework.NEXTJS: 3000,
            Framework.NUXT: 3000,
            Framework.FASTAPI: 8000,
            Framework.DJANGO: 8000,
            Framework.FLASK: 5000,
            Framework.SPRING_BOOT: 8080,
            Framework.GIN: 8080,
            Framework.ECHO: 8080,
            Framework.FIBER: 3000,
            Framework.ACTIX: 8080,
            Framework.AXUM: 3000,
            Framework.ASPNET_CORE: 8080,
            Framework.LARAVEL: 8000,
            Framework.RAILS: 3000,
        }
        return defaults.get(framework, 8080)
    
    def _get_lock_file(self, project: ProjectInfo) -> Optional[str]:
        """Get lock file name"""
        lock_files = {
            "pnpm-lock.yaml": "pnpm-lock.yaml",
            "yarn.lock": "yarn.lock",
            "package-lock.json": "package-lock.json",
            "bun.lockb": "bun.lockb",
            "poetry.lock": "poetry.lock",
            "Pipfile.lock": "Pipfile.lock",
            "uv.lock": "uv.lock",
            "go.sum": "go.sum",
            "Cargo.lock": "Cargo.lock",
            "composer.lock": "composer.lock",
            "Gemfile.lock": "Gemfile.lock",
            "pubspec.lock": "pubspec.lock",
            "mix.lock": "mix.lock",
            "Package.resolved": "Package.resolved",
        }
        for f in project.config_files:
            if f in lock_files:
                return lock_files[f]
        return None
    
    def _get_build_deps(self, language: Language) -> str:
        """Get build dependencies for language"""
        deps = {
            Language.NODEJS: "python3 make g++",
            Language.PYTHON: "gcc musl-dev libffi-dev openssl-dev",
            Language.GO: "",
            Language.JAVA: "",
            Language.RUST: "musl-dev openssl-dev pkgconfig",
            Language.DOTNET: "",
            Language.PHP: "",
            Language.RUBY: "build-base",
            Language.DART: "",
            Language.ELIXIR: "",
            Language.HASKELL: "",
            Language.SCALA: "",
            Language.KOTLIN: "",
            Language.SWIFT: "",
            Language.BUN: "python3 make g++",
            Language.DENO: "",
        }
        return deps.get(language, "")
    
    def _get_install_command(self, project: ProjectInfo) -> str:
        """Get install command for language"""
        lang = project.language
        pm = project.package_manager
        
        if lang == Language.NODEJS:
            if pm == "pnpm":
                return "pnpm install --frozen-lockfile"
            elif pm == "yarn":
                return "yarn install --frozen-lockfile"
            elif pm == "bun":
                return "bun install --frozen-lockfile"
            return "npm ci"
        
        elif lang == Language.PYTHON:
            if pm == "poetry":
                return "poetry install --no-dev --no-interaction"
            elif pm == "pipenv":
                return "pipenv install --deploy --ignore-pipfile"
            elif pm == "uv":
                return "uv pip install --no-cache -r requirements.txt"
            return "pip install --no-cache-dir -r requirements.txt"
        
        elif lang == Language.GO:
            return "go mod download"
        
        elif lang == Language.RUST:
            return "cargo fetch"
        
        elif lang == Language.PHP:
            return "composer install --no-dev --optimize-autoloader --no-interaction"
        
        elif lang == Language.RUBY:
            return "bundle config set --local without 'development test' && bundle install --jobs 4 --retry 3"
        
        elif lang == Language.DART:
            return "dart pub get"
        
        elif lang == Language.ELIXIR:
            return "mix deps.get --only prod"
        
        elif lang == Language.BUN:
            return "bun install --frozen-lockfile"
        
        elif lang == Language.DENO:
            return "deno cache deno.json"
        
        return ""
    
    def _get_binary_name(self, project: ProjectInfo) -> str:
        """Get binary name for compiled languages"""
        if project.language == Language.GO:
            return "main"
        elif project.language == Language.RUST:
            return project.entry_point or "app"
        elif project.language == Language.DART:
            return "main"
        elif project.language == Language.ELIXIR:
            return "app"
        elif project.language == Language.HASKELL:
            return "main"
        elif project.language == Language.SWIFT:
            return "main"
        return "app"
    
    def _get_jar_name(self, project: ProjectInfo) -> str:
        """Get JAR name for Java"""
        return "app.jar"
    
    def _get_assembly_name(self, project: ProjectInfo) -> str:
        """Get assembly name for .NET"""
        return "App"
    
    def _get_default_entry_point(self, project: ProjectInfo) -> str:
        """Get default entry point"""
        if project.entry_point:
            return project.entry_point
        
        defaults = {
            Framework.NESTJS: "dist/main.js",
            Framework.FASTAPI: "main.py",
            Framework.DJANGO: "manage.py",
            Framework.FLASK: "app.py",
            Framework.EXPRESS: "index.js",
        }
        return defaults.get(project.framework, "index.js")
    
    def _get_default_build_command(self, project: ProjectInfo) -> Optional[str]:
        """Get default build command"""
        if project.build_command:
            return project.build_command
        
        if project.language == Language.NODEJS:
            if project.framework in [Framework.NEXTJS, Framework.NUXT]:
                return "npm run build"
            elif project.framework == Framework.NESTJS:
                return "npm run build"
        return None
    
    def _get_default_start_command(self, project: ProjectInfo) -> str:
        """Get default start command"""
        if project.start_command:
            return project.start_command
        
        lang = project.language
        fw = project.framework
        
        if lang == Language.NODEJS:
            if fw in [Framework.NEXTJS, Framework.NUXT]:
                return "node server.js"
            elif fw == Framework.NESTJS:
                return "node dist/main.js"
            return "node index.js"
        
        elif lang == Language.PYTHON:
            if fw == Framework.FASTAPI:
                module = (project.entry_point or "main.py").replace("/", ".").replace(".py", "")
                return f"uvicorn {module}:app --host 0.0.0.0 --port 8000"
            elif fw == Framework.DJANGO:
                return "python manage.py runserver 0.0.0.0:8000"
            elif fw == Framework.FLASK:
                return "gunicorn -b 0.0.0.0:5000 app:app"
            return "python app.py"
        
        elif lang == Language.GO:
            return "./main"
        
        elif lang == Language.JAVA:
            return "java -jar app.jar"
        
        elif lang == Language.RUST:
            return "./main"
        
        elif lang == Language.DOTNET:
            return "dotnet App.dll"
        
        elif lang == Language.PHP:
            if fw == Framework.LARAVEL:
                return "php artisan serve --host=0.0.0.0 --port=8000"
            return "php -S 0.0.0.0:8000"
        
        elif lang == Language.RUBY:
            if fw == Framework.RAILS:
                return "bundle exec rails server -b 0.0.0.0 -p 3000"
            return "ruby app.rb"
        
        return "echo 'No start command defined'"
    
    def _get_health_check(self, project: ProjectInfo, port: int) -> Optional[str]:
        """Get health check command"""
        health_checks = {
            Framework.NEXTJS: f"wget --no-verbose --tries=1 --spider http://localhost:{port}/api/health || exit 1",
            Framework.NUXT: f"wget --no-verbose --tries=1 --spider http://localhost:{port}/api/health || exit 1",
            Framework.FASTAPI: f"wget --no-verbose --tries=1 --spider http://localhost:{port}/health || exit 1",
            Framework.DJANGO: f"wget --no-verbose --tries=1 --spider http://localhost:{port}/health/ || exit 1",
            Framework.FLASK: f"wget --no-verbose --tries=1 --spider http://localhost:{port}/health || exit 1",
            Framework.SPRING_BOOT: f"wget --no-verbose --tries=1 --spider http://localhost:{port}/actuator/health || exit 1",
            Framework.GIN: f"wget --no-verbose --tries=1 --spider http://localhost:{port}/health || exit 1",
            Framework.ASPNET_CORE: f"wget --no-verbose --tries=1 --spider http://localhost:{port}/health || exit 1",
            Framework.LARAVEL: f"wget --no-verbose --tries=1 --spider http://localhost:{port}/health || exit 1",
            Framework.RAILS: f"wget --no-verbose --tries=1 --spider http://localhost:{port}/up || exit 1",
        }
        return health_checks.get(project.framework)
    
    def _get_output_dir(self, project: ProjectInfo) -> str:
        """Get output directory for static sites"""
        if project.framework == Framework.NEXTJS:
            return ".next/standalone"
        elif project.framework in [Framework.REACT, Framework.VUE, Framework.SVELTE, Framework.ASTRO]:
            return "dist"
        return "dist"
    
    def _get_static_dir(self, project: ProjectInfo) -> Optional[str]:
        """Get static directory for Go"""
        if project.language == Language.GO:
            return "static"
        return None
    
    def _get_main_package(self, project: ProjectInfo) -> str:
        """Get main package for Go"""
        if project.entry_point:
            return project.entry_point.replace(".go", "").replace("/", ".")
        return "."
    
    def _get_req_file(self, project: ProjectInfo) -> str:
        """Get requirements file for Python"""
        for f in project.config_files:
            if f in ["requirements.txt", "requirements.prod.txt"]:
                return f
        return "requirements.txt"
    
    def _get_csproj(self, project: ProjectInfo) -> Optional[str]:
        """Get csproj file for .NET"""
        for f in project.config_files:
            if f.endswith(".csproj"):
                return f
        return None
    
    def _get_app_name(self, project: ProjectInfo) -> str:
        """Get app name for Elixir"""
        return "app"
    
    def _get_nginx_config(self, project: ProjectInfo) -> Optional[str]:
        """Get custom nginx config if exists"""
        for f in project.config_files:
            if f in ["nginx.conf", "nginx.template.conf"]:
                return f
        return None
    
    def _get_applied_optimizations(self, context: GenerationContext) -> List[str]:
        """Get list of applied optimizations"""
        opts = []
        options = context.options
        project = context.project_info
        
        if options.multi_stage:
            opts.append("multi_stage_build")
        if options.optimize_layers:
            opts.append("layer_caching_optimized")
        if options.security_hardening:
            opts.append("non_root_user")
            opts.append("read_only_filesystem_ready")
            opts.append("minimal_base_image")
        
        # Language-specific optimizations
        if project.language in [Language.GO, Language.RUST]:
            opts.append("static_binary")
            opts.append("scratch_or_distroless_runtime")
        
        if project.language == Language.NODEJS:
            if project.framework in [Framework.NEXTJS, Framework.NUXT]:
                opts.append("nextjs_standalone_output")
            opts.append("npm_ci_for_reproducible_builds")
        
        if project.language == Language.PYTHON:
            opts.append("uv_for_fast_installs")
            opts.append("virtual_environment_isolation")
        
        if project.language == Language.JAVA:
            opts.append("jvm_container_awareness")
            opts.append("memory_percentage_limits")
        
        return opts
    
    def _get_ai_suggestions(self, context: GenerationContext, dockerfile: str) -> Optional[List[str]]:
        """Get AI-powered optimization suggestions"""
        try:
            optimizer = get_ai_optimizer()
            if optimizer and optimizer.is_available():
                return optimizer.get_suggestions(context.project_info, dockerfile)
        except Exception:
            pass
        return None
    
    def _validate_dockerfile(self, dockerfile: str, context: GenerationContext) -> List[str]:
        """Validate generated Dockerfile and return warnings"""
        warnings = []
        
        # Check for common issues
        if "latest" in dockerfile and ":latest" in dockerfile:
            warnings.append("Using 'latest' tag - consider pinning to specific version for reproducibility")
        
        if "USER root" in dockerfile and "USER " not in dockerfile.split("USER root")[-1]:
            warnings.append("Running as root - consider switching to non-root user")
        
        if "ADD http" in dockerfile:
            warnings.append("Using ADD with URL - prefer COPY with explicit download step")
        
        if context.project_info.language == Language.NODEJS and "npm install" in dockerfile and "npm ci" not in dockerfile:
            warnings.append("Using 'npm install' instead of 'npm ci' - ci provides reproducible builds")
        
        if "COPY . ." in dockerfile and ".dockerignore" not in context.project_info.config_files:
            warnings.append("No .dockerignore found - consider adding one to exclude unnecessary files")
        
        if context.options.multi_stage and "AS " not in dockerfile:
            warnings.append("Multi-stage requested but no stages detected in output")
        
        return warnings
    
    def _estimate_image_size(self, context: GenerationContext) -> Optional[float]:
        """Estimate final image size in MB"""
        project = context.project_info
        options = context.options
        
        # Base estimates per language (runtime image + app)
        base_estimates = {
            Language.NODEJS: 120 if options.multi_stage else 400,
            Language.PYTHON: 100 if options.multi_stage else 500,
            Language.GO: 15 if options.multi_stage else 300,
            Language.JAVA: 150 if options.multi_stage else 600,
            Language.RUST: 10 if options.multi_stage else 200,
            Language.DOTNET: 100 if options.multi_stage else 400,
            Language.PHP: 80 if options.multi_stage else 300,
            Language.RUBY: 120 if options.multi_stage else 400,
            Language.DART: 20 if options.multi_stage else 200,
            Language.ELIXIR: 50 if options.multi_stage else 300,
            Language.HASKELL: 100 if options.multi_stage else 500,
            Language.SCALA: 150 if options.multi_stage else 600,
            Language.KOTLIN: 150 if options.multi_stage else 600,
            Language.SWIFT: 50 if options.multi_stage else 400,
            Language.BUN: 100 if options.multi_stage else 300,
            Language.DENO: 50 if options.multi_stage else 200,
        }
        
        base = base_estimates.get(project.language, 100)
        
        # Adjust for framework
        if project.framework in [Framework.NEXTJS, Framework.NUXT]:
            base *= 1.2  # Standalone output is larger
        elif project.framework == Framework.SPRING_BOOT:
            base *= 1.3
        elif project.framework == Framework.RAILS:
            base *= 1.2
        
        return round(base, 1)


def generate_dockerfile(project_info: ProjectInfo, options: GenerationOptions) -> DockerfileResult:
    """Convenience function to generate Dockerfile"""
    generator = DockerfileGenerator()
    return generator.generate(project_info, options)