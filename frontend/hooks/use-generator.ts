/** Custom hook for Dockerfile generation */
import { useState, useCallback, useRef } from 'react';
import { api, createDefaultOptions, fileToBase64, createZipInput, createGitHubInput } from '@/services/api';
import type { DockerfileResult, GenerationOptions, GitHubInput, ZipInput, ValidationResult } from '@/types/api';

interface UseDockerfileGeneratorReturn {
  // State
  result: DockerfileResult | null;
  loading: boolean;
  error: string | null;
  progress: number;
  stage: string;
  
  // Actions
  generateFromGitHub: (input: GitHubInput, options?: GenerationOptions) => Promise<void>;
  generateFromZip: (file: File, options?: GenerationOptions) => Promise<void>;
  generateFromZipInput: (input: ZipInput, options?: GenerationOptions) => Promise<void>;
  validateGitHub: (input: GitHubInput) => Promise<ValidationResult>;
  validateZip: (file: File) => Promise<ValidationResult>;
  clearResult: () => void;
  clearError: () => void;
}

export function useDockerfileGenerator(): UseDockerfileGeneratorReturn {
  const [result, setResult] = useState<DockerfileResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState('');
  const abortControllerRef = useRef<AbortController | null>(null);

  const clearResult = useCallback(() => {
    setResult(null);
    setError(null);
    setProgress(0);
    setStage('');
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const updateProgress = useCallback((p: number, s: string) => {
    setProgress(p);
    setStage(s);
  }, []);

  const generateFromGitHub = useCallback(async (
    input: GitHubInput,
    options?: GenerationOptions
  ) => {
    setLoading(true);
    setError(null);
    setProgress(0);
    setStage('Validating repository...');
    
    abortControllerRef.current = new AbortController();

    try {
      // Validate first
      updateProgress(10, 'Validating repository...');
      const validation = await api.validateGitHub(input);
      if (!validation.valid) {
        throw new Error(validation.error || 'Invalid repository');
      }

      updateProgress(30, 'Analyzing repository structure...');
      
      // Generate Dockerfile
      updateProgress(50, 'Generating Dockerfile...');
      const dockerfileResult = await api.analyzeGitHub(input, options || createDefaultOptions());
      
      updateProgress(90, 'Finalizing...');
      setResult(dockerfileResult);
      updateProgress(100, 'Complete!');
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        return;
      }
      const message = err instanceof Error ? err.message : 'Failed to generate Dockerfile';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
      setTimeout(() => setProgress(0), 1000);
    }
  }, [updateProgress]);

  const generateFromZip = useCallback(async (
    file: File,
    options?: GenerationOptions
  ) => {
    setLoading(true);
    setError(null);
    setProgress(0);
    setStage('Reading file...');
    
    abortControllerRef.current = new AbortController();

    try {
      // Convert to base64
      updateProgress(20, 'Reading file...');
      const base64 = await fileToBase64(file);
      const zipInput = createZipInput(file, base64);

      // Validate
      updateProgress(40, 'Validating archive...');
      const validation = await api.validateZip(zipInput);
      if (!validation.valid) {
        throw new Error(validation.error || 'Invalid archive');
      }

      // Generate
      updateProgress(60, 'Analyzing project...');
      const dockerfileResult = await api.analyzeZip(zipInput, options || createDefaultOptions());
      
      updateProgress(90, 'Finalizing...');
      setResult(dockerfileResult);
      updateProgress(100, 'Complete!');
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        return;
      }
      const message = err instanceof Error ? err.message : 'Failed to generate Dockerfile';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
      setTimeout(() => setProgress(0), 1000);
    }
  }, [updateProgress]);

  const generateFromZipInput = useCallback(async (
    input: ZipInput,
    options?: GenerationOptions
  ) => {
    setLoading(true);
    setError(null);
    setProgress(0);
    setStage('Validating archive...');
    
    abortControllerRef.current = new AbortController();

    try {
      // Validate
      updateProgress(30, 'Validating archive...');
      const validation = await api.validateZip(input);
      if (!validation.valid) {
        throw new Error(validation.error || 'Invalid archive');
      }

      // Generate
      updateProgress(50, 'Analyzing project...');
      const dockerfileResult = await api.analyzeZip(input, options || createDefaultOptions());
      
      updateProgress(90, 'Finalizing...');
      setResult(dockerfileResult);
      updateProgress(100, 'Complete!');
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        return;
      }
      const message = err instanceof Error ? err.message : 'Failed to generate Dockerfile';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
      setTimeout(() => setProgress(0), 1000);
    }
  }, [updateProgress]);

  const validateGitHub = useCallback(async (input: GitHubInput) => {
    return api.validateGitHub(input);
  }, []);

  const validateZip = useCallback(async (file: File) => {
    const base64 = await fileToBase64(file);
    const zipInput = createZipInput(file, base64);
    return api.validateZip(zipInput);
  }, []);

  return {
    result,
    loading,
    error,
    progress,
    stage,
    generateFromGitHub,
    generateFromZip,
    generateFromZipInput,
    validateGitHub,
    validateZip,
    clearResult,
    clearError,
  };
}