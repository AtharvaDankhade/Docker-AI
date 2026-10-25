# Dockerfile Generator

An AI-enhanced Dockerfile generator that creates optimized, production-ready Dockerfiles from GitHub repositories or zip files.

## Features

- **Multi-input support**: GitHub URL (public/private) or zip file upload
- **Auto-detection**: Identifies 15+ languages and 30+ frameworks automatically
- **Optimized templates**: Multi-stage builds, layer caching, security hardening
- **AI-powered suggestions**: Optional Ollama integration for optimization tips
- **Modern UI**: Beautiful Next.js frontend with drag-and-drop, live preview, syntax highlighting
- **Production-ready**: Non-root users, health checks, minimal base images

## Supported Languages & Frameworks

| Language | Frameworks |
|----------|------------|
| **Node.js** | Express, NestJS, Next.js, Nuxt, React, Vue, Svelte, Astro, Remix, Fastify, Koa, Hono |
| **Python** | FastAPI, Django, Flask, Starlette, Tornado, Sanic, Quart, Litestar, Streamlit, Gradio |
| **Go** | Gin, Echo, Fiber, Chi, Standard Library |
| **Java** | Spring Boot, Quarkus, Micronaut, Vert.x, Helidon (Maven/Gradle) |
| **Rust** | Actix, Axum, Rocket, Warp, Poem |
| **.NET** | ASP.NET Core |
| **PHP** | Laravel, Symfony, Slim, Lumen |
| **Ruby** | Rails, Sinatra, Hanami |
| **Dart** | Flutter, Server |
| **Elixir** | Phoenix |
| **Haskell** | Yesod, Servant |
| **Scala** | Akka, Play |
| **Kotlin** | Ktor, Spring |
| **Swift** | Vapor, Kitura |
| **Bun** | Native, Elysia |
| **Deno** | Oak, Fresh |

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# Start with AI optimization (requires GPU)
docker-compose --profile ai up -d

# View logs
docker-compose logs -f
```

Services:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Ollama (optional): http://localhost:11434

### Local Development

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

## Configuration

### Backend Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `true` | Enable debug mode |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `GITHUB_TOKEN` | - | GitHub API token for private repos |
| `MAX_ZIP_SIZE_MB` | `100` | Max zip upload size |
| `OLLAMA_ENABLED` | `false` | Enable AI optimization |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `codellama:7b` | Model to use |

### Frontend Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API URL |

## API Endpoints

### Health Check
```
GET /api/v1/health
```

### Generate from GitHub
```
POST /api/v1/analyze/github
{
  "url": "https://github.com/owner/repo",
  "branch": "main",
  "access_token": "ghp_...",
  "options": {
    "multi_stage": true,
    "optimize_layers": true,
    "security_hardening": true,
    "ai_optimization": true
  }
}
```

### Generate from Zip
```
POST /api/v1/analyze/zip
{
  "filename": "project.zip",
  "content_base64": "...",
  "options": { ... }
}
```

### Get Supported Languages
```
GET /api/v1/languages
```

### Preview Template
```
GET /api/v1/templates/{language}?framework={framework}
```

## Project Structure

```
Docker_AI/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI routes
│   │   ├── ai/            # Ollama integration
│   │   ├── detection/     # Language/framework detection
│   │   ├── generator/     # Dockerfile generation orchestration
│   │   ├── github/        # GitHub repository analysis
│   │   ├── templates/     # Jinja2 Dockerfile templates
│   │   ├── zip/           # Zip file analysis
│   │   ├── models/        # Pydantic schemas
│   │   ├── core/          # Configuration
│   │   └── main.py        # FastAPI entry point
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/               # Next.js App Router pages
│   ├── components/        # React components
│   ├── hooks/             # Custom React hooks
│   ├── services/          # API service layer
│   ├── types/             # TypeScript types
│   ├── public/            # Static assets
│   ├── Dockerfile
│   ├── package.json
│   └── .env.example
├── docker-compose.yml
└── README.md
```

## How It Works

1. **Input**: User provides GitHub URL or uploads zip file
2. **Analysis**: Backend detects language, framework, package manager, entry point, dependencies
3. **Template Selection**: Chooses appropriate Dockerfile template (framework-specific or language fallback)
4. **Generation**: Renders template with project-specific context (multi-stage, security, optimizations)
5. **AI Enhancement**: Optional Ollama analysis for additional optimization suggestions
6. **Output**: Returns complete Dockerfile with metadata, warnings, and size estimates

## Optimization Features

- **Multi-stage builds**: Separate build and runtime environments
- **Layer caching**: Orders COPY/RUN for optimal Docker layer reuse
- **Security hardening**: Non-root users, read-only filesystem ready, minimal attack surface
- **Language-specific**:
  - Node.js: npm ci, standalone output for Next.js/Nuxt
  - Python: uv for fast installs, virtual environments
  - Go/Rust: Static binaries, scratch/distroless runtime
  - Java: JVM container awareness, memory limits
  - .NET: Self-contained, trimmed builds

## License

MIT