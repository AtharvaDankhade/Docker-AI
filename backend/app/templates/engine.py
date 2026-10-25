"""Dockerfile templates for each language/framework"""
from typing import Dict, Optional
from jinja2 import Environment, BaseLoader, Template
from ..models.schemas import Language, Framework


class TemplateEngine:
    """Jinja2-based template engine for Dockerfile generation"""
    
    def __init__(self):
        self.env = Environment(loader=BaseLoader(), trim_blocks=True, lstrip_blocks=True)
        self._templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Template]:
        """Load all Dockerfile templates"""
        templates = {}
        
        # Multi-stage templates
        templates["nodejs_multi"] = self.env.from_string(NODEJS_MULTI_TEMPLATE)
        templates["nodejs_single"] = self.env.from_string(NODEJS_SINGLE_TEMPLATE)
        templates["nextjs_multi"] = self.env.from_string(NEXTJS_MULTI_TEMPLATE)
        templates["nestjs_multi"] = self.env.from_string(NESTJS_MULTI_TEMPLATE)
        
        templates["python_multi"] = self.env.from_string(PYTHON_MULTI_TEMPLATE)
        templates["python_single"] = self.env.from_string(PYTHON_SINGLE_TEMPLATE)
        templates["fastapi_multi"] = self.env.from_string(FASTAPI_MULTI_TEMPLATE)
        templates["django_multi"] = self.env.from_string(DJANGO_MULTI_TEMPLATE)
        templates["flask_multi"] = self.env.from_string(FLASK_MULTI_TEMPLATE)
        
        templates["go_multi"] = self.env.from_string(GO_MULTI_TEMPLATE)
        templates["go_single"] = self.env.from_string(GO_SINGLE_TEMPLATE)
        
        templates["java_multi"] = self.env.from_string(JAVA_MULTI_TEMPLATE)
        templates["java_gradle_multi"] = self.env.from_string(JAVA_GRADLE_MULTI_TEMPLATE)
        
        templates["rust_multi"] = self.env.from_string(RUST_MULTI_TEMPLATE)
        templates["rust_single"] = self.env.from_string(RUST_SINGLE_TEMPLATE)
        
        templates["dotnet_multi"] = self.env.from_string(DOTNET_MULTI_TEMPLATE)
        
        templates["php_multi"] = self.env.from_string(PHP_MULTI_TEMPLATE)
        templates["laravel_multi"] = self.env.from_string(LARAVEL_MULTI_TEMPLATE)
        
        templates["ruby_multi"] = self.env.from_string(RUBY_MULTI_TEMPLATE)
        templates["rails_multi"] = self.env.from_string(RAILS_MULTI_TEMPLATE)
        
        templates["dart_multi"] = self.env.from_string(DART_MULTI_TEMPLATE)
        templates["elixir_multi"] = self.env.from_string(ELIXIR_MULTI_TEMPLATE)
        templates["haskell_multi"] = self.env.from_string(HASKELL_MULTI_TEMPLATE)
        templates["scala_multi"] = self.env.from_string(SCALA_MULTI_TEMPLATE)
        templates["kotlin_multi"] = self.env.from_string(KOTLIN_MULTI_TEMPLATE)
        templates["swift_multi"] = self.env.from_string(SWIFT_MULTI_TEMPLATE)
        templates["bun_multi"] = self.env.from_string(BUN_MULTI_TEMPLATE)
        templates["deno_multi"] = self.env.from_string(DENO_MULTI_TEMPLATE)
        
        # Generic/static
        templates["static_multi"] = self.env.from_string(STATIC_MULTI_TEMPLATE)
        
        return templates
    
    def get_template(self, language: Language, framework: Framework, multi_stage: bool = True) -> Template:
        """Get the appropriate template for language/framework"""
        key = self._get_template_key(language, framework, multi_stage)
        return self._templates.get(key, self._templates.get(f"{language.value}_multi" if multi_stage else f"{language.value}_single"))
    
    def _get_template_key(self, language: Language, framework: Framework, multi_stage: bool) -> str:
        """Generate template key"""
        suffix = "_multi" if multi_stage else "_single"
        
        # Framework-specific templates
        framework_keys = {
            Framework.NEXTJS: f"nextjs{suffix}",
            Framework.NESTJS: f"nestjs{suffix}",
            Framework.FASTAPI: f"fastapi{suffix}",
            Framework.DJANGO: f"django{suffix}",
            Framework.FLASK: f"flask{suffix}",
            Framework.LARAVEL: f"laravel{suffix}",
            Framework.RAILS: f"rails{suffix}",
        }
        
        if framework in framework_keys:
            return framework_keys[framework]
        
        # Language fallback
        return f"{language.value}{suffix}"
    
    def render(self, language: Language, framework: Framework, context: Dict, multi_stage: bool = True) -> str:
        """Render Dockerfile from template"""
        template = self.get_template(language, framework, multi_stage)
        return template.render(**context)


# ============================================================================
# TEMPLATE DEFINITIONS
# ============================================================================

# ----- Node.js -----
NODEJS_MULTI_TEMPLATE = """# ============================================================================
# Generated Dockerfile for Node.js project
# Language: {{ language }}, Framework: {{ framework }}
# Multi-stage build for optimal size and security
# ============================================================================

# Build stage
FROM {{ base_image }} AS builder

# Install build dependencies
RUN apk add --no-cache {{ build_deps }}

WORKDIR /app

# Copy package files first for layer caching
COPY package*.json ./
{% if lock_file %}COPY {{ lock_file }} ./{% endif %}

# Install dependencies
RUN {{ install_cmd }}

# Copy source code
COPY . .

# Build application
{% if build_cmd %}RUN {{ build_cmd }}{% endif %}

# ============================================================================
# Runtime stage
# ============================================================================
FROM {{ runtime_image }} AS runner

# Security: Create non-root user
RUN addgroup -g 1001 -S nodejs && \\
    adduser -S nodejs -u 1001

WORKDIR /app

# Copy built application from builder
{% if output_dir %}
COPY --from=builder --chown=nodejs:nodejs /app/{{ output_dir }} ./{{ output_dir }}
{% else %}
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/package*.json ./
COPY --from=builder --chown=nodejs:nodejs /app ./
{% endif %}

# Security: Use non-root user
USER nodejs

# Expose port
EXPOSE {{ port }}

# Health check
{% if health_check %}HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD {{ health_check }}{% endif %}

# Start application
CMD {{ start_cmd }}
"""

NODEJS_SINGLE_TEMPLATE = """# ============================================================================
# Generated Dockerfile for Node.js project (Single Stage)
# ============================================================================

FROM {{ base_image }}

WORKDIR /app

# Install dependencies
COPY package*.json ./
{% if lock_file %}COPY {{ lock_file }} ./{% endif %}
RUN {{ install_cmd }}

# Copy source
COPY . .

{% if build_cmd %}RUN {{ build_cmd }}{% endif %}

# Security: Create non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
USER nodejs

EXPOSE {{ port }}

{% if health_check %}HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD {{ health_check }}{% endif %}

CMD {{ start_cmd }}
"""

NEXTJS_MULTI_TEMPLATE = """# ============================================================================
# Generated Dockerfile for Next.js project
# Optimized for Next.js with standalone output
# ============================================================================

# Build stage
FROM {{ base_image }} AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
{% if lock_file %}COPY {{ lock_file }} ./{% endif %}

# Install dependencies
RUN {{ install_cmd }}

# Copy source
COPY . .

# Build with standalone output
ENV NEXT_TELEMETRY_DISABLED=1
RUN {{ build_cmd }}

# ============================================================================
# Runtime stage - minimal image with only standalone files
# ============================================================================
FROM {{ runtime_image }} AS runner

RUN addgroup -g 1001 -S nodejs && \\
    adduser -S nodejs -u 1001

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Copy standalone build
COPY --from=builder --chown=nodejs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nodejs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nodejs:nodejs /app/public ./public

USER nodejs

EXPOSE {{ port }}

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD wget --no-verbose --tries=1 --spider http://localhost:{{ port }}/api/health || exit 1

CMD ["node", "server.js"]
"""

NESTJS_MULTI_TEMPLATE = """# ============================================================================
# Generated Dockerfile for NestJS project
# ============================================================================

# Build stage
FROM {{ base_image }} AS builder

WORKDIR /app

COPY package*.json ./
{% if lock_file %}COPY {{ lock_file }} ./{% endif %}

RUN {{ install_cmd }}

COPY . .

RUN {{ build_cmd }}

# ============================================================================
# Runtime stage
# ============================================================================
FROM {{ runtime_image }} AS runner

RUN addgroup -g 1001 -S nodejs && \\
    adduser -S nodejs -u 1001

WORKDIR /app

COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/package*.json ./

USER nodejs

EXPOSE {{ port }}

{% if health_check %}HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD {{ health_check }}{% endif %}

CMD {{ start_cmd }}
"""

# ----- Python -----
PYTHON_MULTI_TEMPLATE = """# ============================================================================
# Generated Dockerfile for Python project
# ============================================================================

# Build stage
FROM {{ base_image }} AS builder

# Install build dependencies
RUN apk add --no-cache {{ build_deps }}

WORKDIR /app

# Install uv for fast dependency resolution
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY {% if req_file %}{{ req_file }}{% else %}requirements.txt{% endif %} ./
{% if pyproject %}COPY pyproject.toml ./{% endif %}
{% if poetry_lock %}COPY poetry.lock ./{% endif %}
{% if pipfile %}COPY Pipfile Pipfile.lock ./{% endif %}

# Install dependencies to virtual environment
RUN uv venv /opt/venv && \\
    /opt/venv/bin/pip install --no-cache-dir -r {% if req_file %}{{ req_file }}{% else %}requirements.txt{% endif %}

# Copy source
COPY . .

{% if build_cmd %}RUN {{ build_cmd }}{% endif %}

# ============================================================================
# Runtime stage
# ============================================================================
FROM {{ runtime_image }} AS runner

# Security: Create non-root user
RUN addgroup -g 1001 -S appgroup && \\
    adduser -S appuser -u 1001 -G appgroup

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application
COPY --from=builder --chown=appuser:appgroup /app ./

# Security: Use non-root user
USER appuser

# Add venv to PATH
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE {{ port }}

{% if health_check %}HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD {{ health_check }}{% endif %}

CMD {{ start_cmd }}
"""

PYTHON_SINGLE_TEMPLATE = """# ============================================================================
# Generated Dockerfile for Python project (Single Stage)
# ============================================================================

FROM {{ base_image }}

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY {% if req_file %}{{ req_file }}{% else %}requirements.txt{% endif %} ./
{% if pyproject %}COPY pyproject.toml ./{% endif %}

RUN uv venv /opt/venv && \\
    /opt/venv/bin/pip install --no-cache-dir -r {% if req_file %}{{ req_file }}{% else %}requirements.txt{% endif %}

COPY . .

{% if build_cmd %}RUN {{ build_cmd }}{% endif %}

RUN addgroup -g 1001 -S appgroup && adduser -S appuser -u 1001 -G appgroup
USER appuser

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE {{ port }}

{% if health_check %}HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD {{ health_check }}{% endif %}

CMD {{ start_cmd }}
"""

FASTAPI_MULTI_TEMPLATE = """# ============================================================================
# Generated Dockerfile for FastAPI project
# Optimized with uv for fast installs
# ============================================================================

# Build stage
FROM {{ base_image }} AS builder

RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY {% if req_file %}{{ req_file }}{% else %}requirements.txt{% endif %} ./
{% if pyproject %}COPY pyproject.toml ./{% endif %}

RUN uv venv /opt/venv && \\
    /opt/venv/bin/pip install --no-cache-dir -r {% if req_file %}{{ req_file }}{% else %}requirements.txt{% endif %}

COPY . .

# ============================================================================
# Runtime stage
# ============================================================================
FROM {{ runtime_image }} AS runner

RUN addgroup -g 1001 -S appgroup && \\
    adduser -S appuser -u 1001 -G appgroup

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder --chown=appuser:appgroup /app ./

USER appuser

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE {{ port }}

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD wget --no-verbose --tries=1 --spider http://localhost:{{ port }}/health || exit 1

CMD {{ start_cmd }}
"""

DJANGO_MULTI_TEMPLATE = """# ============================================================================
# Generated Dockerfile for Django project
# ============================================================================

# Build stage
FROM {{ base_image }} AS builder

RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev postgresql-dev

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY {% if req_file %}{{ req_file }}{% else %}requirements.txt{% endif %} ./
{% if pyproject %}COPY pyproject.toml ./{% endif %}

RUN uv venv /opt/venv && \\
    /opt/venv/bin/pip install --no-cache-dir -r {% if req_file %}{{ req_file }}{% else %}requirements.txt{% endif %}

COPY . .

# Collect static files
RUN /opt/venv/bin/python manage.py collectstatic --noinput

# ============================================================================
# Runtime stage
# ============================================================================
FROM {{ runtime_image }} AS runner

RUN addgroup -g 1001 -S appgroup && \\
    adduser -S appuser -u 1001 -G appgroup

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder --chown=appuser:appgroup /app ./

USER appuser

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE {{ port }}

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \\
    CMD wget --no-verbose --tries=1 --spider http://localhost:{{ port }}/health/ || exit 1

CMD {{ start_cmd }}
"""

FLASK_MULTI_TEMPLATE = """# ============================================================================
# Generated Dockerfile for Flask project
# ============================================================================

# Build stage
FROM {{ base_image }} AS builder

RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY {% if req_file %}{{ req_file }}{% else %}requirements.txt{% endif %} ./
{% if pyproject %}COPY pyproject.toml ./{% endif %}

RUN uv venv /opt/venv && \\
    /opt/venv/bin/pip install --no-cache-dir -r {% if req_file %}{{ req_file }}{% else %}requirements.txt{% endif %}

COPY . .

# ============================================================================
# Runtime stage
# ============================================================================
FROM {{ runtime_image }} AS runner

RUN addgroup -g 1001 -S appgroup && \\
    adduser -S appuser -u 1001 -G appgroup

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder --chown=appuser:appgroup /app ./

USER appuser

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE {{ port }}

{% if health_check %}HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD {{ health_check }}{% endif %}

CMD {{ start_cmd }}
"""

# ----- Go -----
GO_MULTI_TEMPLATE = """# ============================================================================
# Generated Dockerfile for Go project
# Multi-stage build with minimal runtime image
# ============================================================================

# Build stage
FROM {{ base_image }} AS builder

WORKDIR /app

# Copy go mod files for layer caching
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy source
COPY . .

# Build with optimizations
RUN CGO_ENABLED=0 GOOS=linux GOARCH={{ arch }} go build \\
    -ldflags='-w -s -extldflags="-static"' \\
    -o {{ binary_name }} {{ main_package }}

# ============================================================================
# Runtime stage - scratch or distroless for minimal attack surface
# ============================================================================
FROM {{ runtime_image }} AS runner

# Security: Non-root user
RUN addgroup -g 1001 -S appgroup && \\
    adduser -S appuser -u 1001 -G appgroup

WORKDIR /app

# Copy binary
COPY --from=builder --chown=appuser:appgroup /app/{{ binary_name }} .

# Copy any static assets if needed
{% if static_dir %}COPY --from=builder --chown=appuser:appgroup /app/{{ static_dir }} ./{{ static_dir }}{% endif %}

USER appuser

EXPOSE {{ port }}

{% if health_check %}HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD {{ health_check }}{% endif %}

CMD ["./{{ binary_name }}"]
"""

GO_SINGLE_TEMPLATE = """# ============================================================================
# Generated Dockerfile for Go project (Single Stage)
# ============================================================================

FROM {{ base_image }}

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH={{ arch }} go build \\
    -ldflags='-w -s -extldflags="-static"' \\
    -o {{ binary_name }} {{ main_package }}

RUN addgroup -g 1001 -S appgroup && adduser -S appuser -u 1001 -G appgroup
USER appuser

EXPOSE {{ port }}

CMD ["./{{ binary_name }}"]
"""

# ----- Java -----
JAVA_MULTI_TEMPLATE = """# ============================================================================
# Generated Dockerfile for Java (Maven) project
# ============================================================================

# Build stage
FROM {{ base_image }} AS builder

WORKDIR /app

# Copy Maven files for layer caching
COPY pom.xml .
COPY .mvn .mvn
COPY mvnw .

# Download dependencies
RUN ./mvnw dependency:go-offline -B

# Copy source
COPY src ./src

# Build
RUN ./mvnw package -DskipTests -B

# ============================================================================
# Runtime stage
# ============================================================================
FROM {{ runtime_image }} AS runner

RUN addgroup -g 1001 -S appgroup && \\
    adduser -S appuser -u 1001 -G appgroup

WORKDIR /app

# Copy built jar
COPY --from=builder --chown=appuser:appgroup /app/target/{{ jar_name }} ./app.jar

USER appuser

EXPOSE {{ port }}

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \\
    CMD wget --no-verbose --tries=1 --spider http://localhost:{{ port }}/actuator/health || exit 1

ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "-jar", "app.jar"]
"""

JAVA_GRADLE_MULTI_TEMPLATE = """# ============================================================================
# Generated Dockerfile for Java (Gradle) project
# ============================================================================

# Build stage
FROM {{ base_image }} AS builder

WORKDIR /app

# Copy Gradle files for layer caching
COPY build.gradle* settings.gradle* gradle.properties* ./
COPY gradle ./gradle
COPY gradlew .

# Download dependencies
RUN ./gradlew dependencies --no-daemon

# Copy source
COPY src ./src

# Build
RUN ./gradlew build -x test --no-daemon

# ============================================================================
# Runtime stage
# ============================================================================
FROM {{ runtime_image }} AS runner

RUN addgroup -g 1001 -S appgroup && \\
    adduser -S appuser -u 1001 -G appgroup

WORKDIR /app

COPY --from=builder --chown=appuser:appgroup /app/build/libs/{{ jar_name }} ./app.jar

USER appuser

EXPOSE {{ port }}

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \\
    CMD wget --no-verbose --tries=1 --spider http://localhost:{{ port }}/actuator/health || exit 1

ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "-jar", "app.jar"]
"""

# ----- Rust -----
RUST_MULTI_TEMPLATE = """# ============================================================================
# Generated Dockerfile for Rust project
# ============================================================================

# Build stage
FROM {{ base_image }} AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache musl-dev openssl-dev pkgconfig

# Copy Cargo files for layer caching
COPY Cargo.toml Cargo.lock ./

# Create dummy main to cache dependencies
RUN mkdir src && echo "fn main() {}" > src/main.rs
RUN cargo build --release
RUN rm -rf src

# Copy actual source
COPY src ./src

# Build application
RUN cargo build --release

# ============================================================================
# Runtime stage
# ============================================================================
FROM {{ runtime_image }} AS runner

RUN addgroup -g 1001 -S appgroup && \\
    adduser -S appuser -u 1001 -G appgroup

WORKDIR /app

COPY --from=builder --chown=appuser:appgroup /app/target/release/{{ binary_name }} .

USER appuser

EXPOSE {{ port }}

{% if health_check %}HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD {{ health_check }}{% endif %}

CMD ["./{{ binary_name }}"]
"""

RUST_SINGLE_TEMPLATE = """# ============================================================================
# Generated Dockerfile for Rust project (Single Stage)
# ============================================================================

FROM {{ base_image }}

WORKDIR /app

RUN apk add --no-cache musl-dev openssl-dev pkgconfig

COPY Cargo.toml Cargo.lock ./
RUN mkdir src && echo "fn main() {}" > src/main.rs
RUN cargo build --release
RUN rm -rf src

COPY src ./src
RUN cargo build --release

RUN addgroup -g 1001 -S appgroup && adduser -S appuser -u 1001 -G appgroup
USER appuser

EXPOSE {{ port }}

CMD ["./target/release/{{ binary_name }}"]
"""

# ----- .NET -----
DOTNET_MULTI_TEMPLATE = """# ============================================================================
# Generated Dockerfile for .NET project
# ============================================================================

# Build stage
FROM {{ base_image }} AS builder

WORKDIR /src

# Copy csproj files for layer caching
COPY {% if csproj %}{{ csproj }}{% else %}*.csproj{% endif %} ./
RUN dotnet restore

# Copy source
COPY . .

# Publish
RUN dotnet publish {% if csproj %}{{ csproj }}{% else %}*.csproj{% endif %} -c Release -o /app/publish /p:UseAppHost=false

# ============================================================================
# Runtime stage
# ============================================================================
FROM {{ runtime_image }} AS runner

RUN addgroup -g 1001 -S appgroup && \\
    adduser -S appuser -u 1001 -G appgroup

WORKDIR /app

COPY --from=builder --chown=appuser:appgroup /app/publish .

USER appuser

EXPOSE {{ port }}

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \\
    CMD wget --no-verbose --tries=1 --spider http://localhost:{{ port }}/health || exit 1

ENTRYPOINT ["dotnet", "{{ assembly_name }}.dll"]
"""

# ----- PHP -----
PHP_MULTI_TEMPLATE = """# ============================================================================
# Generated Dockerfile for PHP project
# ============================================================================

# Build stage
FROM {{ base_image }} AS builder

WORKDIR /app

# Install composer
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

COPY composer.json composer.lock ./
RUN composer install --no-dev --optimize-autoloader --no-interaction

COPY . .

# ============================================================================
# Runtime stage
# ============================================================================
FROM {{ runtime_image }} AS runner

RUN addgroup -g 1001 -S appgroup && \\
    adduser -S appuser -u 1001 -G appgroup

WORKDIR /app

COPY --from=builder --chown=appuser:appgroup /app .

USER appuser

EXPOSE {{ port }}

{% if health_check %}HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD {{ health_check }}{% endif %}

CMD {{ start_cmd }}
"""

LARAVEL_MULTI_TEMPLATE = """# ============================================================================
# Generated Dockerfile for Laravel project
# ============================================================================

# Build stage
FROM {{ base_image }} AS builder

WORKDIR /app

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

COPY composer.json composer.lock ./
RUN composer install --no-dev --optimize-autoloader --no-interaction

COPY . .

# Generate key and cache config
RUN php artisan key:generate --force && \\
    php artisan config:cache && \\
    php artisan route:cache && \\
    php artisan view:cache

# ============================================================================
# Runtime stage
# ============================================================================
FROM {{ runtime_image }} AS runner

RUN addgroup -g 1001 -S appgroup && \\
    adduser -S appuser -u 1001 -G appgroup

WORKDIR /app

COPY --from=builder --chown=appuser:appgroup /app .

# Ensure storage and cache are writable
RUN chown -R appuser:appgroup storage bootstrap/cache

USER appuser

EXPOSE {{ port }}

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \\
    CMD wget --no-verbose --tries=1 --spider http://localhost:{{ port }}/health || exit 1

CMD ["php", "artisan", "serve", "--host=0.0.0.0", "--port=8000"]
"""

# ----- Ruby -----
RUBY_MULTI_TEMPLATE = """# ============================================================================
# Generated Dockerfile for Ruby project
# ============================================================================

# Build stage
FROM {{ base_image }} AS builder

WORKDIR /app

COPY Gemfile Gemfile.lock ./
RUN bundle config set --local without 'development test' && \\
    bundle install --jobs 4 --retry 3

COPY . .

# ============================================================================
# Runtime stage
# ============================================================================
FROM {{ runtime_image }} AS runner

RUN addgroup -g 1001 -S appgroup && \\
    adduser -S appuser -u 1001 -G appgroup

WORKDIR /app

COPY --from=builder --chown=appuser:appgroup /usr/local/bundle /usr/local/bundle
COPY --from=builder --chown=appuser:appgroup /app .

USER appuser

EXPOSE {{ port }}

{% if health_check %}HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD {{ health_check }}{% endif %}

CMD {{ start_cmd }}
"""

RAILS_MULTI_TEMPLATE = """# ============================================================================
# Generated Dockerfile for Rails project
# ============================================================================

# Build stage
FROM {{ base_image }} AS builder

WORKDIR /app

COPY Gemfile Gemfile.lock ./
RUN bundle config set --local without 'development test' && \\
    bundle install --jobs 4 --retry 3

COPY . .

# Precompile assets
RUN bundle exec rails assets:precompile

# ============================================================================
# Runtime stage
# ============================================================================
FROM {{ runtime_image }} AS runner

RUN addgroup -g 1001 -S appgroup && \\
    adduser -S appuser -u 1001 -G appgroup

WORKDIR /app

COPY --from=builder --chown=appuser:appgroup /usr/local/bundle /usr/local/bundle
COPY --from=builder --chown=appuser:appgroup /app .

USER appuser

EXPOSE {{ port }}

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \\
    CMD wget --no-verbose --tries=1 --spider http://localhost:{{ port }}/up || exit 1

CMD ["bundle", "exec", "rails", "server", "-b", "0.0.0.0", "-p", "3000"]
"""

# ----- Dart -----
DART_MULTI_TEMPLATE = """# ============================================================================
# Generated Dockerfile for Dart project
# ============================================================================

# Build stage
FROM {{ base_image }} AS builder

WORKDIR /app

COPY pubspec.yaml pubspec.lock ./
RUN dart pub get

COPY . .

RUN dart compile exe {{ entry_point }} -o {{ binary_name }}

# ============================================================================
# Runtime stage
# ============================================================================
FROM {{ runtime_image }} AS runner

RUN addgroup -g 1001 -S appgroup && \\
    adduser -S appuser -u 1001 -G appgroup

WORKDIR /app

COPY --from=builder --chown=appuser:appgroup /app/{{ binary_name }} .

USER appuser

EXPOSE {{ port }}

{% if health_check %}HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD {{ health_check }}{% endif %}

CMD ["./{{ binary_name }}"]
"""

# ----- Elixir -----
ELIXIR_MULTI_TEMPLATE = """# ============================================================================
# Generated Dockerfile for Elixir project
# ============================================================================

# Build stage
FROM {{ base_image }} AS builder

WORKDIR /app

COPY mix.exs mix.lock ./
RUN mix deps.get --only prod

COPY . .

RUN MIX_ENV=prod mix compile && \\
    MIX_ENV=prod mix release

# ============================================================================
# Runtime stage
# ============================================================================
FROM {{ runtime_image }} AS runner

RUN addgroup -g 1001 -S appgroup && \\
    adduser -S appuser -u 1001 -G appgroup

WORKDIR /app

COPY --from=builder --chown=appuser:appgroup /app/_build/prod/rel/{{ app_name }} .

USER appuser

EXPOSE {{ port }}

{% if health_check %}HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \\
    CMD {{ health_check }}{% endif %}

CMD ["bin/{{ app_name }}", "start"]
"""

# ----- Haskell -----
HASKELL_MULTI_TEMPLATE = """# ============================================================================
# Generated Dockerfile for Haskell project
# ============================================================================

# Build stage
FROM {{ base_image }} AS builder

WORKDIR /app

COPY *.cabal ./
COPY stack.yaml ./
RUN stack build --only-dependencies

COPY . .
RUN stack build --copy-bins

# ============================================================================
# Runtime stage
# ============================================================================
FROM {{ runtime_image }} AS runner

RUN addgroup -g 1001 -S appgroup && \\
    adduser -S appuser -u 1001 -G appgroup

WORKDIR /app

COPY --from=builder --chown=appuser:appgroup /root/.local/bin/{{ binary_name }} .

USER appuser

EXPOSE {{ port }}

{% if health_check %}HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD {{ health_check }}{% endif %}

CMD ["./{{ binary_name }}"]
"""

# ----- Scala -----
SCALA_MULTI_TEMPLATE = """# ============================================================================
# Generated Dockerfile for Scala project
# ============================================================================

# Build stage
FROM {{ base_image }} AS builder

WORKDIR /app

COPY build.sbt project/build.properties ./
COPY project ./project
RUN sbt update

COPY . .
RUN sbt assembly

# ============================================================================
# Runtime stage
# ============================================================================
FROM {{ runtime_image }} AS runner

RUN addgroup -g 1001 -S appgroup && \\
    adduser -S appuser -u 1001 -G appgroup

WORKDIR /app

COPY --from=builder --chown=appuser:appgroup /app/target/scala-*/{{ jar_name }} ./app.jar

USER appuser

EXPOSE {{ port }}

{% if health_check %}HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \\
    CMD {{ health_check }}{% endif %}

ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "-jar", "app.jar"]
"""

# ----- Kotlin -----
KOTLIN_MULTI_TEMPLATE = """# ============================================================================
# Generated Dockerfile for Kotlin project
# ============================================================================

# Build stage
FROM {{ base_image }} AS builder

WORKDIR /app

COPY build.gradle.kts settings.gradle.kts ./
COPY gradle ./gradle
COPY gradlew .
RUN ./gradlew dependencies --no-daemon

COPY src ./src
RUN ./gradlew build -x test --no-daemon

# ============================================================================
# Runtime stage
# ============================================================================
FROM {{ runtime_image }} AS runner

RUN addgroup -g 1001 -S appgroup && \\
    adduser -S appuser -u 1001 -G appgroup

WORKDIR /app

COPY --from=builder --chown=appuser:appgroup /app/build/libs/{{ jar_name }} ./app.jar

USER appuser

EXPOSE {{ port }}

{% if health_check %}HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \\
    CMD {{ health_check }}{% endif %}

ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "-jar", "app.jar"]
"""

# ----- Swift -----
SWIFT_MULTI_TEMPLATE = """# ============================================================================
# Generated Dockerfile for Swift project
# ============================================================================

# Build stage
FROM {{ base_image }} AS builder

WORKDIR /app

COPY Package.swift Package.resolved ./
RUN swift package resolve

COPY Sources ./Sources
RUN swift build -c release

# ============================================================================
# Runtime stage
# ============================================================================
FROM {{ runtime_image }} AS runner

RUN addgroup -g 1001 -S appgroup && \\
    adduser -S appuser -u 1001 -G appgroup

WORKDIR /app

COPY --from=builder --chown=appuser:appgroup /app/.build/release/{{ binary_name }} .

USER appuser

EXPOSE {{ port }}

{% if health_check %}HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD {{ health_check }}{% endif %}

CMD ["./{{ binary_name }}"]
"""

# ----- Bun -----
BUN_MULTI_TEMPLATE = """# ============================================================================
# Generated Dockerfile for Bun project
# ============================================================================

# Build stage
FROM {{ base_image }} AS builder

WORKDIR /app

COPY package.json bun.lockb ./
RUN bun install --frozen-lockfile

COPY . .

{% if build_cmd %}RUN {{ build_cmd }}{% endif %}

# ============================================================================
# Runtime stage
# ============================================================================
FROM {{ runtime_image }} AS runner

RUN addgroup -g 1001 -S appgroup && \\
    adduser -S appuser -u 1001 -G appgroup

WORKDIR /app

COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:appgroup /app/package.json ./
COPY --from=builder --chown=appuser:appgroup /app ./

USER appuser

EXPOSE {{ port }}

{% if health_check %}HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD {{ health_check }}{% endif %}

CMD {{ start_cmd }}
"""

# ----- Deno -----
DENO_MULTI_TEMPLATE = """# ============================================================================
# Generated Dockerfile for Deno project
# ============================================================================

# Build stage (cache dependencies)
FROM {{ base_image }} AS builder

WORKDIR /app

COPY deno.json* ./
RUN deno cache --reload deno.json

COPY . .

{% if build_cmd %}RUN {{ build_cmd }}{% endif %}

# ============================================================================
# Runtime stage
# ============================================================================
FROM {{ runtime_image }} AS runner

WORKDIR /app

COPY --from=builder /app ./

EXPOSE {{ port }}

{% if health_check %}HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD {{ health_check }}{% endif %}

CMD {{ start_cmd }}
"""

# ----- Static Site -----
STATIC_MULTI_TEMPLATE = """# ============================================================================
# Generated Dockerfile for Static Site
# Served with Nginx
# ============================================================================

# Build stage (if needed)
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
{% if lock_file %}COPY {{ lock_file }} ./{% endif %}
RUN npm ci

COPY . .
{% if build_cmd %}RUN {{ build_cmd }}{% endif %}

# ============================================================================
# Runtime stage - Nginx
# ============================================================================
FROM nginx:alpine AS runner

# Copy built files
COPY --from=builder /app/{{ output_dir }} /usr/share/nginx/html

# Copy nginx config
{% if nginx_config %}COPY {{ nginx_config }} /etc/nginx/conf.d/default.conf{% else %}
COPY <<EOF /etc/nginx/conf.d/default.conf
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;
    
    location / {
        try_files \\$uri \\$uri/ /index.html;
    }
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";
}
EOF
{% endif %}

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
"""