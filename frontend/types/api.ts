/** API Types for Dockerfile Generator Frontend */

export type InputType = 'github_url' | 'zip_file';

export type Language = 
  | 'nodejs' | 'python' | 'go' | 'java' | 'rust' | 'dotnet'
  | 'php' | 'ruby' | 'dart' | 'elixir' | 'haskell' | 'scala'
  | 'kotlin' | 'swift' | 'bun' | 'deno' | 'unknown';

export type Framework = 
  // Node.js
  | 'express' | 'nestjs' | 'nextjs' | 'nuxt' | 'react' | 'vue'
  | 'svelte' | 'astro' | 'remix' | 'fastify' | 'koa' | 'hono'
  // Python
  | 'fastapi' | 'django' | 'flask' | 'starlette' | 'tornado'
  | 'sanic' | 'quart' | 'litestar' | 'streamlit' | 'gradio'
  // Go
  | 'gin' | 'echo' | 'fiber' | 'chi' | 'go_std'
  // Java
  | 'spring_boot' | 'quarkus' | 'micronaut' | 'vertx' | 'helidon'
  | 'maven' | 'gradle'
  // Rust
  | 'actix' | 'axum' | 'rocket' | 'warp' | 'poem'
  // .NET
  | 'aspnet_core'
  // PHP
  | 'laravel' | 'symfony' | 'slim' | 'lumen'
  // Ruby
  | 'rails' | 'sinatra' | 'hanami'
  // Generic
  | 'static_site' | 'docker_compose' | 'unknown';

export interface ProjectInfo {
  language: Language;
  framework: Framework;
  package_manager: string | null;
  entry_point: string | null;
  build_command: string | null;
  start_command: string | null;
  port: number | null;
  dependencies: Record<string, string>;
  dev_dependencies: Record<string, string>;
  config_files: string[];
  dockerfile_exists: boolean;
  dockerignore_exists: boolean;
}

export interface GitHubInput {
  url: string;
  branch?: string;
  access_token?: string;
}

export interface ZipInput {
  filename: string;
  content_base64: string;
}

export interface GenerationOptions {
  multi_stage: boolean;
  optimize_layers: boolean;
  security_hardening: boolean;
  base_image?: string;
  target_platform: string;
  expose_port?: number;
  env_vars: Record<string, string>;
  ai_optimization: boolean;
}

export interface GenerateRequest {
  input_type: InputType;
  github?: GitHubInput;
  zip?: ZipInput;
  options?: GenerationOptions;
}

export interface DockerfileResult {
  dockerfile: string;
  project_info: ProjectInfo;
  optimizations_applied: string[];
  ai_suggestions: string[] | null;
  warnings: string[];
  estimated_image_size_mb: number | null;
}

export interface HealthResponse {
  status: string;
  version: string;
  ollama_available: boolean;
}

export interface ValidationResult {
  valid: boolean;
  error?: string;
  size_mb?: number;
  filename?: string;
  name?: string;
  description?: string;
  private?: boolean;
  default_branch?: string;
}

export interface LanguageOption {
  value: Language;
  name: string;
}

export interface FrameworkOption {
  value: Framework;
  name: string;
}

export interface SupportedLanguagesResponse {
  languages: LanguageOption[];
  frameworks: FrameworkOption[];
}

export interface TemplatePreviewResponse {
  dockerfile: string;
}