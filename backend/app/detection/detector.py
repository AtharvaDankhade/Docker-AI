"""Language and framework detection engine"""
import os
import re
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field

from ..models.schemas import Language, Framework, ProjectInfo


@dataclass
class DetectionSignal:
    """A signal that contributes to language/framework detection"""
    language: Language
    framework: Optional[Framework] = None
    confidence: float = 0.0
    evidence: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class LanguageDetector:
    """Detects programming language and framework from project files"""
    
    # Manifest files per language
    MANIFEST_FILES = {
        Language.NODEJS: ["package.json", "pnpm-lock.yaml", "yarn.lock", "package-lock.json", "bun.lockb"],
        Language.PYTHON: ["requirements.txt", "pyproject.toml", "setup.py", "setup.cfg", "Pipfile", "poetry.lock", "uv.lock"],
        Language.GO: ["go.mod", "go.sum", "go.work"],
        Language.JAVA: ["pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts", "gradle.properties"],
        Language.RUST: ["Cargo.toml", "Cargo.lock"],
        Language.DOTNET: ["*.csproj", "*.fsproj", "*.vbproj", "*.sln", "global.json", "NuGet.Config"],
        Language.PHP: ["composer.json", "composer.lock"],
        Language.RUBY: ["Gemfile", "Gemfile.lock", "*.gemspec"],
        Language.DART: ["pubspec.yaml", "pubspec.lock"],
        Language.ELIXIR: ["mix.exs", "mix.lock"],
        Language.HASKELL: ["*.cabal", "stack.yaml", "hie.yaml"],
        Language.SCALA: ["build.sbt", "project/build.properties"],
        Language.KOTLIN: ["build.gradle.kts", "settings.gradle.kts"],
        Language.SWIFT: ["Package.swift", "*.xcodeproj", "*.xcworkspace"],
        Language.BUN: ["bun.lockb", "bunfig.toml"],
        Language.DENO: ["deno.json", "deno.jsonc", "import_map.json"],
    }
    
    # Framework detection patterns in manifest files
    FRAMEWORK_PATTERNS = {
        Language.NODEJS: {
            Framework.EXPRESS: [r'"express"\s*:', r"express"],
            Framework.NESTJS: [r'"@nestjs/core"\s*:', r"@nestjs"],
            Framework.NEXTJS: [r'"next"\s*:', r'"next"', r"next"],
            Framework.NUXT: [r'"nuxt"\s*:', r"nuxt"],
            Framework.REACT: [r'"react"\s*:', r'"react-dom"'],
            Framework.VUE: [r'"vue"\s*:', r'"@vue/'],
            Framework.SVELTE: [r'"svelte"\s*:', r'"@sveltejs/'],
            Framework.ASTRO: [r'"astro"\s*:', r"astro"],
            Framework.REMIX: [r'"@remix-run/', r"remix"],
            Framework.FASTIFY: [r'"fastify"\s*:', r"fastify"],
            Framework.KOA: [r'"koa"\s*:', r"koa"],
            Framework.HONO: [r'"hono"\s*:', r"hono"],
        },
        Language.PYTHON: {
            Framework.FASTAPI: [r'"fastapi"\s*[=<>]', r"fastapi", r"fastapi\s*[=<>]"],
            Framework.DJANGO: [r'"django"\s*[=<>]', r"django", r"django\s*[=<>]"],
            Framework.FLASK: [r'"flask"\s*[=<>]', r"flask", r"flask\s*[=<>]"],
            Framework.STARLETTE: [r'"starlette"\s*[=<>]', r"starlette"],
            Framework.TORNADO: [r'"tornado"\s*[=<>]', r"tornado"],
            Framework.SANIC: [r'"sanic"\s*[=<>]', r"sanic"],
            Framework.QUART: [r'"quart"\s*[=<>]', r"quart"],
            Framework.LITESTAR: [r'"litestar"\s*[=<>]', r"litestar"],
            Framework.STREAMLIT: [r'"streamlit"\s*[=<>]', r"streamlit"],
            Framework.GRADIO: [r'"gradio"\s*[=<>]', r"gradio"],
        },
        Language.GO: {
            Framework.GIN: [r"github\.com/gin-gonic/gin"],
            Framework.ECHO: [r"github\.com/labstack/echo"],
            Framework.FIBER: [r"github\.com/gofiber/fiber"],
            Framework.CHI: [r"github\.com/go-chi/chi"],
            Framework.GO_STD: [r"net/http"],
        },
        Language.JAVA: {
            Framework.SPRING_BOOT: [r"spring-boot-starter", r"org\.springframework\.boot"],
            Framework.QUARKUS: [r"io\.quarkus", r"quarkus"],
            Framework.MICRONAUT: [r"io\.micronaut", r"micronaut"],
            Framework.VERTX: [r"io\.vertx", r"vertx"],
            Framework.HELIDON: [r"io\.helidon", r"helidon"],
        },
        Language.RUST: {
            Framework.ACTIX: [r'actix-web\s*=', r"actix_web"],
            Framework.AXUM: [r"axum\s*="],
            Framework.ROCKET: [r"rocket\s*="],
            Framework.WARP: [r"warp\s*="],
            Framework.POEM: [r"poem\s*="],
        },
        Language.DOTNET: {
            Framework.ASPNET_CORE: [r"Microsoft\.AspNetCore", r"AspNetCore"],
        },
        Language.PHP: {
            Framework.LARAVEL: [r"laravel/framework", r"laravel"],
            Framework.SYMFONY: [r"symfony/", r"symfony"],
            Framework.SLIM: [r"slim/slim", r"slim"],
            Framework.LUMEN: [r"laravel/lumen", r"lumen"],
        },
        Language.RUBY: {
            Framework.RAILS: [r'"rails"\s*[=<>]', r"rails"],
            Framework.SINATRA: [r'"sinatra"\s*[=<>]', r"sinatra"],
            Framework.HANNAMI: [r'"hanami"\s*[=<>]', r"hanami"],
        },
    }
    
    # Entry point patterns per framework
    ENTRY_POINTS = {
        Framework.EXPRESS: ["index.js", "app.js", "server.js", "main.js", "src/index.js", "src/app.js"],
        Framework.NESTJS: ["main.ts", "src/main.ts"],
        Framework.NEXTJS: ["next.config.js", "next.config.ts"],
        Framework.NUXT: ["nuxt.config.js", "nuxt.config.ts"],
        Framework.FASTAPI: ["main.py", "app/main.py", "src/main.py", "app.py"],
        Framework.DJANGO: ["manage.py"],
        Framework.FLASK: ["app.py", "main.py", "wsgi.py"],
        Framework.STARLETTE: ["app.py", "main.py"],
        Framework.SPRING_BOOT: ["src/main/java/*/Application.java", "Application.java"],
        Framework.GIN: ["main.go", "cmd/main.go", "cmd/server/main.go"],
        Framework.ECHO: ["main.go", "server.go"],
        Framework.FIBER: ["main.go"],
        Framework.CHI: ["main.go"],
        Framework.ACTIX: ["src/main.rs"],
        Framework.AXUM: ["src/main.rs"],
        Framework.ROCKET: ["src/main.rs"],
        Framework.ASPNET_CORE: ["Program.cs", "Startup.cs"],
        Framework.LARAVEL: ["artisan", "public/index.php"],
        Framework.RAILS: ["config.ru", "bin/rails"],
    }
    
    # Port detection patterns
    PORT_PATTERNS = [
        (r'PORT\s*[=:]\s*(\d+)', 1),
        (r'port\s*[=:]\s*(\d+)', 1),
        (r'EXPOSE\s+(\d+)', 1),
        (r'listen\s*\(\s*(\d+)\s*\)', 1),
        (r'\.listen\s*\(\s*(\d+)\s*\)', 1),
        (r'--port\s+(\d+)', 1),
    ]
    
    def __init__(self):
        self.signals: List[DetectionSignal] = []
    
    def detect(self, project_path: Path) -> ProjectInfo:
        """Main detection entry point"""
        self.signals = []
        
        # 1. Detect language from manifest files
        language = self._detect_language(project_path)
        
        # 2. Detect framework from dependencies
        framework = self._detect_framework(project_path, language)
        
        # 3. Extract project metadata
        package_manager = self._detect_package_manager(project_path, language)
        entry_point = self._detect_entry_point(project_path, framework)
        build_command = self._detect_build_command(project_path, language, framework)
        start_command = self._detect_start_command(project_path, language, framework)
        port = self._detect_port(project_path)
        dependencies, dev_dependencies = self._extract_dependencies(project_path, language)
        config_files = self._find_config_files(project_path)
        dockerfile_exists = (project_path / "Dockerfile").exists() or (project_path / "dockerfile").exists()
        dockerignore_exists = (project_path / ".dockerignore").exists()
        
        return ProjectInfo(
            language=language,
            framework=framework,
            package_manager=package_manager,
            entry_point=entry_point,
            build_command=build_command,
            start_command=start_command,
            port=port,
            dependencies=dependencies,
            dev_dependencies=dev_dependencies,
            config_files=config_files,
            dockerfile_exists=dockerfile_exists,
            dockerignore_exists=dockerignore_exists,
        )
    
    def _detect_language(self, project_path: Path) -> Language:
        """Detect primary language from manifest files"""
        scores: Dict[Language, float] = {lang: 0.0 for lang in Language}
        
        for lang, manifests in self.MANIFEST_FILES.items():
            for manifest in manifests:
                if list(project_path.glob(manifest)):
                    scores[lang] += 1.0
                    self.signals.append(DetectionSignal(
                        language=lang,
                        confidence=1.0,
                        evidence=[f"Found {manifest}"]
                    ))
        
        # Check for specific files that strongly indicate language
        if any(project_path.glob("*.go")):
            scores[Language.GO] += 0.5
        if any(project_path.glob("*.py")):
            scores[Language.PYTHON] += 0.5
        if any(project_path.glob("*.rs")):
            scores[Language.RUST] += 0.5
        if any(project_path.glob("*.java")):
            scores[Language.JAVA] += 0.5
        if any(project_path.glob("*.cs")):
            scores[Language.DOTNET] += 0.5
        if any(project_path.glob("*.php")):
            scores[Language.PHP] += 0.5
        if any(project_path.glob("*.rb")):
            scores[Language.RUBY] += 0.5
        if any(project_path.glob("*.dart")):
            scores[Language.DART] += 0.5
        if any(project_path.glob("*.ex")) or any(project_path.glob("*.exs")):
            scores[Language.ELIXIR] += 0.5
        if any(project_path.glob("*.hs")):
            scores[Language.HASKELL] += 0.5
        if any(project_path.glob("*.scala")) or any(project_path.glob("*.sc")):
            scores[Language.SCALA] += 0.5
        if any(project_path.glob("*.kt")) or any(project_path.glob("*.kts")):
            scores[Language.KOTLIN] += 0.5
        if any(project_path.glob("*.swift")):
            scores[Language.SWIFT] += 0.5
        if any(project_path.glob("*.ts")) or any(project_path.glob("*.js")) or any(project_path.glob("*.tsx")) or any(project_path.glob("*.jsx")):
            scores[Language.NODEJS] += 0.3
        
        # Return language with highest score
        best_lang = max(scores, key=scores.get)
        return best_lang if scores[best_lang] > 0 else Language.UNKNOWN
    
    def _detect_framework(self, project_path: Path, language: Language) -> Framework:
        """Detect framework from dependencies in manifest files"""
        if language == Language.UNKNOWN:
            return Framework.UNKNOWN
        
        patterns = self.FRAMEWORK_PATTERNS.get(language, {})
        if not patterns:
            return Framework.UNKNOWN
        
        # Read relevant manifest files
        content = self._read_manifest_content(project_path, language)
        if not content:
            return Framework.UNKNOWN
        
        scores: Dict[Framework, float] = {fw: 0.0 for fw in patterns}
        
        for framework, regex_patterns in patterns.items():
            for pattern in regex_patterns:
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                if matches > 0:
                    scores[framework] += matches * 0.5
                    self.signals.append(DetectionSignal(
                        language=language,
                        framework=framework,
                        confidence=min(matches * 0.5, 1.0),
                        evidence=[f"Found {framework.value} in dependencies"]
                    ))
        
        best_framework = max(scores, key=scores.get)
        return best_framework if scores[best_framework] > 0 else Framework.UNKNOWN
    
    def _read_manifest_content(self, project_path: Path, language: Language) -> str:
        """Read content of all relevant manifest files"""
        manifests = self.MANIFEST_FILES.get(language, [])
        content_parts = []
        
        for manifest in manifests:
            for file_path in project_path.glob(manifest):
                try:
                    content_parts.append(file_path.read_text(encoding="utf-8", errors="ignore"))
                except Exception:
                    pass
        
        return "\n".join(content_parts)
    
    def _detect_package_manager(self, project_path: Path, language: Language) -> Optional[str]:
        """Detect package manager from lock files"""
        lock_files = {
            "pnpm": ["pnpm-lock.yaml"],
            "yarn": ["yarn.lock"],
            "npm": ["package-lock.json"],
            "bun": ["bun.lockb"],
            "poetry": ["poetry.lock"],
            "pipenv": ["Pipfile.lock"],
            "uv": ["uv.lock"],
            "go": ["go.sum"],
            "cargo": ["Cargo.lock"],
            "maven": ["pom.xml"],
            "gradle": ["build.gradle", "build.gradle.kts"],
            "composer": ["composer.lock"],
            "bundler": ["Gemfile.lock"],
            "pub": ["pubspec.lock"],
            "mix": ["mix.lock"],
            "stack": ["stack.yaml"],
            "sbt": ["build.sbt"],
            "swiftpm": ["Package.resolved"],
        }
        
        for manager, files in lock_files.items():
            for f in files:
                if list(project_path.glob(f)):
                    return manager
        
        # Default per language
        defaults = {
            Language.NODEJS: "npm",
            Language.PYTHON: "pip",
            Language.GO: "go mod",
            Language.JAVA: "maven",
            Language.RUST: "cargo",
            Language.DOTNET: "dotnet",
            Language.PHP: "composer",
            Language.RUBY: "bundler",
            Language.DART: "pub",
            Language.ELIXIR: "mix",
            Language.HASKELL: "stack",
            Language.SCALA: "sbt",
            Language.KOTLIN: "gradle",
            Language.SWIFT: "swiftpm",
            Language.BUN: "bun",
            Language.DENO: "deno",
        }
        return defaults.get(language)
    
    def _detect_entry_point(self, project_path: Path, framework: Framework) -> Optional[str]:
        """Detect entry point file"""
        patterns = self.ENTRY_POINTS.get(framework, [])
        
        for pattern in patterns:
            matches = list(project_path.glob(pattern))
            if matches:
                return str(matches[0].relative_to(project_path))
        
        # Fallback: common entry points
        common = ["index.js", "main.py", "main.go", "main.rs", "Program.cs", "app.py", "server.js", "index.ts"]
        for f in common:
            if (project_path / f).exists():
                return f
        
        return None
    
    def _detect_build_command(self, project_path: Path, language: Language, framework: Framework) -> Optional[str]:
        """Detect build command from package.json or other config"""
        if language == Language.NODEJS:
            pkg_path = project_path / "package.json"
            if pkg_path.exists():
                try:
                    pkg = json.loads(pkg_path.read_text())
                    scripts = pkg.get("scripts", {})
                    if "build" in scripts:
                        return "npm run build"
                    if "compile" in scripts:
                        return "npm run compile"
                except Exception:
                    pass
            return None
        
        build_commands = {
            Language.GO: "go build",
            Language.JAVA: "mvn package" if (project_path / "pom.xml").exists() else "gradle build",
            Language.RUST: "cargo build --release",
            Language.DOTNET: "dotnet publish -c Release",
            Language.PHP: None,  # Typically no build step
            Language.RUBY: None,
            Language.DART: "dart compile exe",
            Language.ELIXIR: "mix release",
            Language.HASKELL: "stack build",
            Language.SCALA: "sbt assembly",
            Language.KOTLIN: "gradle build",
            Language.SWIFT: "swift build -c release",
        }
        
        return build_commands.get(language)
    
    def _detect_start_command(self, project_path: Path, language: Language, framework: Framework) -> Optional[str]:
        """Detect start command"""
        if language == Language.NODEJS:
            pkg_path = project_path / "package.json"
            if pkg_path.exists():
                try:
                    pkg = json.loads(pkg_path.read_text())
                    scripts = pkg.get("scripts", {})
                    if "start" in scripts:
                        return "npm start"
                    if "dev" in scripts and framework in [Framework.NEXTJS, Framework.NUXT]:
                        return "npm run dev"
                except Exception:
                    pass
            return "node index.js"
        
        if language == Language.PYTHON:
            if framework == Framework.DJANGO:
                return "python manage.py runserver 0.0.0.0:8000"
            if framework == Framework.FASTAPI:
                entry = self._detect_entry_point(project_path, framework)
                if entry:
                    module = entry.replace("/", ".").replace(".py", "")
                    return f"uvicorn {module}:app --host 0.0.0.0 --port 8000"
            return "python app.py"
        
        start_commands = {
            Language.GO: "./main",
            Language.JAVA: "java -jar app.jar",
            Language.RUST: "./main",
            Language.DOTNET: "dotnet app.dll",
            Language.PHP: "php artisan serve --host=0.0.0.0 --port=8000" if framework == Framework.LARAVEL else "php -S 0.0.0.0:8000",
            Language.RUBY: "rails server -b 0.0.0.0 -p 3000" if framework == Framework.RAILS else "ruby app.rb",
            Language.DART: "./main",
            Language.ELIXIR: "mix phx.server",
            Language.HASKELL: "./main",
            Language.SCALA: "java -jar app.jar",
            Language.KOTLIN: "java -jar app.jar",
            Language.SWIFT: ".build/release/main",
            Language.BUN: "bun run index.js",
            Language.DENO: "deno run --allow-net main.ts",
        }
        
        return start_commands.get(language)
    
    def _detect_port(self, project_path: Path) -> Optional[int]:
        """Detect exposed port from config files"""
        # Check common config files
        config_files = [
            "package.json", ".env", ".env.example", ".env.local",
            "docker-compose.yml", "docker-compose.yaml",
            "Dockerfile", "dockerfile",
            "nginx.conf", "Caddyfile",
            "application.yml", "application.yaml", "application.properties",
            "config.yaml", "config.yml", "config.json",
        ]
        
        for config in config_files:
            for file_path in project_path.glob(config):
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    for pattern, group in self.PORT_PATTERNS:
                        match = re.search(pattern, content, re.IGNORECASE)
                        if match:
                            port = int(match.group(group))
                            if 1 <= port <= 65535:
                                return port
                except Exception:
                    pass
        
        # Framework defaults
        framework_defaults = {
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
        
        return None  # Will be set by ProjectInfo based on framework
    
    def _extract_dependencies(self, project_path: Path, language: Language) -> Tuple[Dict[str, str], Dict[str, str]]:
        """Extract dependencies from manifest files"""
        deps = {}
        dev_deps = {}
        
        if language == Language.NODEJS:
            pkg_path = project_path / "package.json"
            if pkg_path.exists():
                try:
                    pkg = json.loads(pkg_path.read_text())
                    deps = pkg.get("dependencies", {})
                    dev_deps = pkg.get("devDependencies", {})
                except Exception:
                    pass
        
        elif language == Language.PYTHON:
            # requirements.txt
            req_path = project_path / "requirements.txt"
            if req_path.exists():
                for line in req_path.read_text().splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        parts = re.split(r'[=<>!~]', line)
                        if parts:
                            deps[parts[0].strip()] = line
            
            # pyproject.toml
            pyproject = project_path / "pyproject.toml"
            if pyproject.exists():
                try:
                    import tomli
                    data = tomli.loads(pyproject.read_text())
                    project = data.get("project", {})
                    for dep in project.get("dependencies", []):
                        parts = re.split(r'[=<>!~]', dep)
                        if parts:
                            deps[parts[0].strip()] = dep
                    for dep in project.get("optional-dependencies", {}).get("dev", []):
                        parts = re.split(r'[=<>!~]', dep)
                        if parts:
                            dev_deps[parts[0].strip()] = dep
                except Exception:
                    pass
        
        return deps, dev_deps
    
    def _find_config_files(self, project_path: Path) -> List[str]:
        """Find common configuration files"""
        configs = [
            "Dockerfile", "dockerfile", ".dockerignore",
            "docker-compose.yml", "docker-compose.yaml",
            ".env", ".env.example", ".env.local", ".env.production",
            "nginx.conf", "Caddyfile",
            ".github/workflows", ".gitlab-ci.yml",
            "README.md", "README.rst", "CHANGELOG.md",
            "LICENSE", "LICENSE.txt",
            ".gitignore", ".prettierrc", ".eslintrc",
        ]
        
        found = []
        for config in configs:
            matches = list(project_path.glob(config))
            if matches:
                found.append(config)
        
        return found


# Convenience function
def detect_project(project_path: Path) -> ProjectInfo:
    """Detect project info from a directory"""
    detector = LanguageDetector()
    return detector.detect(project_path)