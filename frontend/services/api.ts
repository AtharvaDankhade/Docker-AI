/** API Service for Dockerfile Generator */
import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  GenerateRequest,
  GenerationOptions,
  DockerfileResult,
  GitHubInput,
  ZipInput,
  HealthResponse,
  ValidationResult,
  SupportedLanguagesResponse,
  TemplatePreviewResponse,
  InputType,
} from '@/types/api';

// Use relative path - Next.js rewrites will proxy to backend
const API_BASE_URL = '/api/backend';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 120000, // 2 minutes for large repos
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        const message = error.response?.data as { detail?: string } | undefined;
        console.error('[API Error]', error.response?.status, message?.detail || error.message);
        return Promise.reject(error);
      }
    );
  }

  /** Health check */
  async healthCheck(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>('/health');
    return response.data;
  }

  /** Validate GitHub repository */
  async validateGitHub(input: GitHubInput): Promise<ValidationResult> {
    const response = await this.client.post<ValidationResult>('/validate/github', input);
    return response.data;
  }

  /** Validate zip file */
  async validateZip(input: ZipInput): Promise<ValidationResult> {
    const response = await this.client.post<ValidationResult>('/validate/zip', input);
    return response.data;
  }

  /** Analyze GitHub repo and generate Dockerfile */
  async analyzeGitHub(input: GitHubInput, options?: GenerationOptions): Promise<DockerfileResult> {
    const response = await this.client.post<DockerfileResult>('/analyze/github', input, {
      params: { options },
    });
    return response.data;
  }

  /** Analyze zip file and generate Dockerfile */
  async analyzeZip(input: ZipInput, options?: GenerationOptions): Promise<DockerfileResult> {
    const response = await this.client.post<DockerfileResult>('/analyze/zip', input, {
      params: { options },
    });
    return response.data;
  }

  /** Generate Dockerfile from request */
  async generate(request: GenerateRequest): Promise<DockerfileResult> {
    const response = await this.client.post<DockerfileResult>('/generate', request);
    return response.data;
  }

  /** Generate Dockerfile and return as file */
  async generateFile(
    githubUrl?: string,
    githubBranch?: string,
    githubToken?: string,
    zipFile?: File,
    options?: GenerationOptions
  ): Promise<Blob> {
    const formData = new FormData();
    
    if (githubUrl) {
      formData.append('github_url', githubUrl);
      if (githubBranch) formData.append('github_branch', githubBranch);
      if (githubToken) formData.append('github_token', githubToken);
    }
    
    if (zipFile) {
      formData.append('zip_file', zipFile);
    }
    
    if (options) {
      formData.append('multi_stage', String(options.multi_stage));
      formData.append('optimize_layers', String(options.optimize_layers));
      formData.append('security_hardening', String(options.security_hardening));
      if (options.base_image) formData.append('base_image', options.base_image);
      if (options.expose_port) formData.append('expose_port', String(options.expose_port));
      formData.append('ai_optimization', String(options.ai_optimization));
    }

    const response = await this.client.post('/generate/file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      responseType: 'blob',
    });
    
    return response.data;
  }

  /** Get supported languages and frameworks */
  async getSupportedLanguages(): Promise<SupportedLanguagesResponse> {
    const response = await this.client.get<SupportedLanguagesResponse>('/languages');
    return response.data;
  }

  /** Preview template for language/framework */
  async previewTemplate(language: string, framework?: string): Promise<TemplatePreviewResponse> {
    const response = await this.client.get<TemplatePreviewResponse>(`/templates/${language}`, {
      params: { framework },
    });
    return response.data;
  }

  /** Analyze local project (dev only) */
  async analyzeLocal(path: string): Promise<any> {
    const formData = new FormData();
    formData.append('path', path);
    const response = await this.client.post('/analyze/local', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }
}

// Export singleton instance
export const api = new ApiService();

// Helper functions
export async function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      // Remove data URL prefix
      const base64 = result.split(',')[1];
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

export function createZipInput(file: File, base64: string): ZipInput {
  return {
    filename: file.name,
    content_base64: base64,
  };
}

export function createGitHubInput(url: string, branch?: string, token?: string): GitHubInput {
  return {
    url,
    branch: branch || 'main',
    access_token: token,
  };
}

export function createDefaultOptions(): GenerationOptions {
  return {
    multi_stage: true,
    optimize_layers: true,
    security_hardening: true,
    target_platform: 'linux/amd64',
    env_vars: {},
    ai_optimization: true,
  };
}