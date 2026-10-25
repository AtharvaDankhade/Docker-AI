"""GitHub repository analysis module"""
import os
import shutil
import tempfile
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse

import httpx
from githubkit import GitHub
from githubkit.exception import GitHubException

from ..core.config import get_settings
from ..models.schemas import GitHubInput, ProjectInfo
from ..detection import detect_project


class GitHubAnalyzer:
    """Analyzes GitHub repositories for Dockerfile generation"""
    
    def __init__(self):
        self.settings = get_settings()
        self._github_client: Optional[GitHub] = None
    
    @property
    def github_client(self) -> GitHub:
        """Lazy initialization of GitHub client"""
        if self._github_client is None:
            token = self.settings.github_token
            self._github_client = GitHub(token) if token else GitHub()
        return self._github_client
    
    def parse_github_url(self, url: str) -> Dict[str, str]:
        """Parse GitHub URL to extract owner, repo, and branch"""
        parsed = urlparse(url)
        
        # Handle different URL formats
        # https://github.com/owner/repo
        # https://github.com/owner/repo/tree/branch
        # https://github.com/owner/repo.git
        # git@github.com:owner/repo.git
        
        path = parsed.path.strip("/")
        if path.endswith(".git"):
            path = path[:-4]
        
        parts = path.split("/")
        if len(parts) < 2:
            raise ValueError(f"Invalid GitHub URL: {url}")
        
        owner = parts[0]
        repo = parts[1]
        branch = "main"
        
        # Check for branch in path
        if len(parts) >= 4 and parts[2] == "tree":
            branch = parts[3]
        
        return {
            "owner": owner,
            "repo": repo,
            "branch": branch,
            "full_name": f"{owner}/{repo}",
        }
    
    async def analyze(self, github_input: GitHubInput) -> ProjectInfo:
        """Analyze GitHub repository and return project info"""
        parsed = self.parse_github_url(str(github_input.url))
        
        # Override branch if provided
        if github_input.branch:
            parsed["branch"] = github_input.branch
        
        # Use access token if provided
        if github_input.access_token:
            self._github_client = GitHub(github_input.access_token)
        
        # Try GitHub API first (faster, no clone needed)
        try:
            return await self._analyze_via_api(parsed)
        except Exception as e:
            # Fallback to cloning
            print(f"API analysis failed, falling back to clone: {e}")
            return await self._analyze_via_clone(parsed)
    
    async def _analyze_via_api(self, parsed: Dict[str, str]) -> ProjectInfo:
        """Analyze repository using GitHub API (no clone)"""
        owner = parsed["owner"]
        repo = parsed["repo"]
        branch = parsed["branch"]
        
        # Get repository tree
        tree = await self.github_client.rest.repos.get_tree(
            owner=owner,
            repo=repo,
            tree_sha=branch,
            recursive="1",
        )
        
        # Filter relevant files
        files = [item.path for item in tree.parsed_data.tree if item.type == "blob"]
        
        # Create temporary directory with file structure
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create directory structure
            for file_path in files:
                full_path = tmp_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Try to get file content for key files
                if self._is_key_file(file_path):
                    try:
                        content = await self._get_file_content(owner, repo, file_path, branch)
                        full_path.write_text(content)
                    except Exception:
                        pass  # Skip files we can't read
            
            return detect_project(tmp_path)
    
    async def _analyze_via_clone(self, parsed: Dict[str, str]) -> ProjectInfo:
        """Analyze repository by shallow cloning"""
        owner = parsed["owner"]
        repo = parsed["repo"]
        branch = parsed["branch"]
        
        clone_url = f"https://github.com/{owner}/{repo}.git"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / repo
            
            # Shallow clone
            proc = await asyncio.create_subprocess_exec(
                "git", "clone", "--depth", str(self.settings.github_clone_depth),
                "--branch", branch, "--single-branch",
                clone_url, str(repo_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=self.settings.github_clone_timeout
                )
            except asyncio.TimeoutError:
                proc.kill()
                raise TimeoutError(f"Git clone timed out after {self.settings.github_clone_timeout}s")
            
            if proc.returncode != 0:
                error = stderr.decode() if stderr else "Unknown error"
                raise RuntimeError(f"Git clone failed: {error}")
            
            return detect_project(repo_path)
    
    def _is_key_file(self, file_path: str) -> bool:
        """Check if file is important for detection"""
        key_files = {
            "package.json", "pnpm-lock.yaml", "yarn.lock", "package-lock.json", "bun.lockb",
            "requirements.txt", "pyproject.toml", "setup.py", "setup.cfg", "Pipfile", "poetry.lock", "uv.lock",
            "go.mod", "go.sum", "go.work",
            "pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts",
            "Cargo.toml", "Cargo.lock",
            "*.csproj", "*.fsproj", "*.vbproj", "*.sln",
            "composer.json", "composer.lock",
            "Gemfile", "Gemfile.lock", "*.gemspec",
            "pubspec.yaml", "pubspec.lock",
            "mix.exs", "mix.lock",
            "*.cabal", "stack.yaml",
            "build.sbt", "build.scala",
            "Package.swift", "Package.resolved",
            "deno.json", "deno.jsonc",
            "Dockerfile", "dockerfile", ".dockerignore",
            "docker-compose.yml", "docker-compose.yaml",
        }
        
        name = Path(file_path).name
        return name in key_files or any(name.endswith(ext) for ext in [".csproj", ".fsproj", ".vbproj", ".gemspec", ".cabal"])
    
    async def _get_file_content(self, owner: str, repo: str, path: str, branch: str) -> str:
        """Get file content from GitHub API"""
        try:
            response = await self.github_client.rest.repos.get_content(
                owner=owner,
                repo=repo,
                path=path,
                ref=branch,
            )
            content = response.parsed_data.content
            if content:
                import base64
                return base64.b64decode(content).decode("utf-8", errors="ignore")
        except Exception:
            pass
        return ""


class GitHubValidator:
    """Validates GitHub repository accessibility"""
    
    def __init__(self):
        self.settings = get_settings()
    
    async def validate(self, github_input: GitHubInput) -> Dict[str, Any]:
        """Validate repository exists and is accessible"""
        analyzer = GitHubAnalyzer()
        parsed = analyzer.parse_github_url(str(github_input.url))
        
        if github_input.access_token:
            analyzer._github_client = GitHub(github_input.access_token)
        
        try:
            repo = await analyzer.github_client.rest.repos.get(
                owner=parsed["owner"],
                repo=parsed["repo"],
            )
            
            return {
                "valid": True,
                "name": repo.parsed_data.full_name,
                "description": repo.parsed_data.description,
                "private": repo.parsed_data.private,
                "size_kb": repo.parsed_data.size,
                "default_branch": repo.parsed_data.default_branch,
                "languages_url": repo.parsed_data.languages_url,
            }
        except GitHubException as e:
            return {
                "valid": False,
                "error": str(e),
                "status_code": e.response.status_code if e.response else None,
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
            }


async def analyze_github_repo(github_input: GitHubInput) -> ProjectInfo:
    """Convenience function to analyze a GitHub repository"""
    analyzer = GitHubAnalyzer()
    return await analyzer.analyze(github_input)


async def validate_github_repo(github_input: GitHubInput) -> Dict[str, Any]:
    """Convenience function to validate a GitHub repository"""
    validator = GitHubValidator()
    return await validator.validate(github_input)