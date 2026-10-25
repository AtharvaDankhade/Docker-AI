/** Input method selector and forms */
'use client';

import { useState, useCallback, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  Github, 
  FileCode, 
  Loader2, 
  CheckCircle2, 
  AlertCircle,
  ChevronDown,
  ExternalLink,
  Eye,
  Code2
} from 'lucide-react';
import { clsx } from 'clsx';
import type { GitHubInput, ZipInput, ValidationResult } from '@/types/api';
import { api, createGitHubInput, fileToBase64, createZipInput } from '@/services/api';

interface InputMethodProps {
  onGitHubSubmit: (input: GitHubInput) => void;
  onZipSubmit: (input: ZipInput) => void;
  loading: boolean;
  disabled?: boolean;
}

export function InputMethod({ onGitHubSubmit, onZipSubmit, loading, disabled }: InputMethodProps) {
  const [activeTab, setActiveTab] = useState<'github' | 'zip'>('github');
  const [githubUrl, setGithubUrl] = useState('');
  const [githubBranch, setGithubBranch] = useState('main');
  const [githubToken, setGithubToken] = useState('');
  const [showToken, setShowToken] = useState(false);
  const [githubValidating, setGithubValidating] = useState(false);
  const [githubValidation, setGithubValidation] = useState<ValidationResult | null>(null);
  const [zipFile, setZipFile] = useState<File | null>(null);
  const [zipValidating, setZipValidating] = useState(false);
  const [zipValidation, setZipValidation] = useState<ValidationResult | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // GitHub dropzone (for URL paste detection)
  const onGitHubDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      if (file.name.endsWith('.zip')) {
        setActiveTab('zip');
        handleZipFile(file);
      }
    }
  }, []);

  const { getRootProps: getGitHubRootProps, getInputProps: getGitHubInputProps } = useDropzone({
    onDrop: onGitHubDrop,
    accept: { '.zip': [] },
    disabled: activeTab !== 'github' || loading,
  });

  // Zip dropzone
  const onZipDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      handleZipFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps: getZipRootProps, getInputProps: getZipInputProps, isDragActive } = useDropzone({
    onDrop: onZipDrop,
    accept: { '.zip': ['.zip'] },
    disabled: loading,
  });

  const handleZipFile = async (file: File) => {
    if (file.size > 100 * 1024 * 1024) {
      alert('File too large. Maximum size is 100MB.');
      return;
    }
    
    setZipFile(file);
    setZipValidation(null);
    setZipValidating(true);
    
    try {
      const base64 = await fileToBase64(file);
      const zipInput = createZipInput(file, base64);
      const validation = await api.validateZip(zipInput);
      setZipValidation(validation);
    } catch (err) {
      setZipValidation({ valid: false, error: 'Failed to validate file' });
    } finally {
      setZipValidating(false);
    }
  };

  const handleGitHubValidate = async () => {
    if (!githubUrl.trim()) return;
    
    setGithubValidating(true);
    setGithubValidation(null);
    
    try {
      const input = createGitHubInput(githubUrl, githubBranch, githubToken || undefined);
      const validation = await api.validateGitHub(input);
      setGithubValidation(validation);
    } catch (err) {
      setGithubValidation({ valid: false, error: 'Failed to validate repository' });
    } finally {
      setGithubValidating(false);
    }
  };

  const handleGitHubSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!githubUrl.trim()) return;
    
    const input = createGitHubInput(githubUrl, githubBranch, githubToken || undefined);
    onGitHubSubmit(input);
  };

  const handleZipSubmit = async () => {
    if (!zipFile) return;
    
    setZipValidating(true);
    try {
      const base64 = await fileToBase64(zipFile);
      const zipInput = createZipInput(zipFile, base64);
      onZipSubmit(zipInput);
    } catch (err) {
      alert('Failed to process file');
    } finally {
      setZipValidating(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div {...getGitHubRootProps()} className="w-full">
      {/* Tab Navigation */}
      <div className="relative mb-6">
        <div className="flex gap-1 bg-slate-800/50 rounded-xl p-1 border border-slate-700/50">
          <button
            type="button"
            onClick={() => { setActiveTab('github'); setGithubValidation(null); }}
            className={clsx(
              'flex-1 py-3 px-6 rounded-lg text-sm font-medium transition-all duration-200',
              'flex items-center justify-center gap-2',
              activeTab === 'github'
                ? 'bg-primary-500/20 text-primary-400 shadow-lg shadow-primary-500/10'
                : 'text-slate-400 hover:text-slate-200'
            )}
            disabled={loading}
          >
            <Github className="w-5 h-5" />
            GitHub Repository
          </button>
          <button
            type="button"
            onClick={() => { setActiveTab('zip'); setZipValidation(null); }}
            className={clsx(
              'flex-1 py-3 px-6 rounded-lg text-sm font-medium transition-all duration-200',
              'flex items-center justify-center gap-2',
              activeTab === 'zip'
                ? 'bg-docker-500/20 text-docker-400 shadow-lg shadow-docker-500/10'
                : 'text-slate-400 hover:text-slate-200'
            )}
            disabled={loading}
          >
            <FileCode className="w-5 h-5" />
            Zip File
          </button>
        </div>
      </div>

      {/* GitHub Tab */}
      {activeTab === 'github' && (
        <form onSubmit={handleGitHubSubmit} className="space-y-4 animate-slide-down">
          <div className="relative">
            <label htmlFor="github-url" className="block text-sm font-medium text-slate-300 mb-2">
              Repository URL
            </label>
            <div className="relative">
              <Github className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
              <input
                id="github-url"
                type="url"
                value={githubUrl}
                onChange={(e) => { setGithubUrl(e.target.value); setGithubValidation(null); }}
                placeholder="https://github.com/owner/repo"
                className={clsx(
                  'w-full pl-12 pr-4 py-3.5 bg-slate-800/50 border rounded-xl',
                  'text-slate-100 placeholder-slate-500',
                  'focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500',
                  'transition-all duration-200',
                  githubValidation?.valid === true && 'border-docker-500 bg-docker-500/5',
                  githubValidation?.valid === false && 'border-red-500 bg-red-500/5',
                  disabled && 'opacity-50 cursor-not-allowed'
                )}
                disabled={loading || disabled}
                aria-describedby="github-url-hint"
              />
              {githubValidating && (
                <Loader2 className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-primary-400 animate-spin" />
              )}
              {githubValidation?.valid === true && (
                <CheckCircle2 className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-docker-500" />
              )}
              {githubValidation?.valid === false && (
                <AlertCircle className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-red-500" />
              )}
            </div>
            <p id="github-url-hint" className="mt-1.5 text-xs text-slate-500">
              Supports: github.com/owner/repo, github.com/owner/repo/tree/branch, or git@github.com:owner/repo.git
            </p>
            {githubValidation && (
              <p className={clsx('mt-2 text-sm flex items-center gap-1.5', githubValidation.valid ? 'text-docker-400' : 'text-red-400')}>
                {githubValidation.valid ? (
                  <>
                    <CheckCircle2 className="w-4 h-4" />
                    Repository found: <strong>{githubValidation.name}</strong>
                    {githubValidation.private && <span className="px-2 py-0.5 bg-slate-700 rounded text-xs">Private</span>}
                    {githubValidation.description && <span className="text-slate-500 ml-2">— {githubValidation.description}</span>}
                  </>
                ) : (
                  <>
                    <AlertCircle className="w-4 h-4" />
                    {githubValidation.error}
                  </>
                )}
              </p>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="github-branch" className="block text-sm font-medium text-slate-300 mb-2">
                Branch / Tag
              </label>
              <input
                id="github-branch"
                type="text"
                value={githubBranch}
                onChange={(e) => { setGithubBranch(e.target.value); setGithubValidation(null); }}
                placeholder="main"
                className={clsx(
                  'w-full px-4 py-3.5 bg-slate-800/50 border rounded-xl',
                  'text-slate-100 placeholder-slate-500',
                  'focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500',
                  disabled && 'opacity-50 cursor-not-allowed'
                )}
                disabled={loading || disabled}
              />
            </div>
            <div>
              <label htmlFor="github-token" className="block text-sm font-medium text-slate-300 mb-2 flex items-center gap-2">
                Access Token (Optional)
                <a href="https://github.com/settings/tokens" target="_blank" rel="noopener noreferrer" className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1">
                  <ExternalLink className="w-3 h-3" />
                  Create token
                </a>
              </label>
              <div className="relative">
                <input
                  id="github-token"
                  type={showToken ? 'text' : 'password'}
                  value={githubToken}
                  onChange={(e) => { setGithubToken(e.target.value); setGithubValidation(null); }}
                  placeholder="ghp_..."
                  className={clsx(
                    'w-full px-4 py-3.5 bg-slate-800/50 border rounded-xl pr-12',
                    'text-slate-100 placeholder-slate-500',
                    'focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500',
                    disabled && 'opacity-50 cursor-not-allowed'
                  )}
                  disabled={loading || disabled}
                />
                <button
                  type="button"
                  onClick={() => setShowToken(!showToken)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                  aria-label={showToken ? 'Hide token' : 'Show token'}
                >
                  <Eye className={clsx('w-5 h-5', !showToken && 'opacity-50')} />
                </button>
              </div>
            </div>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={loading || disabled || !githubUrl.trim() || githubValidating}
              className={clsx(
                'w-full py-3.5 px-6 rounded-xl font-medium text-sm',
                'flex items-center justify-center gap-2',
                'transition-all duration-200',
                'focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:ring-offset-2 focus:ring-offset-slate-900',
                loading || githubValidating
                  ? 'bg-primary-500/50 text-slate-300 cursor-not-allowed'
                  : 'bg-primary-600 hover:bg-primary-500 text-white shadow-lg shadow-primary-500/25 hover:shadow-primary-500/40'
              )}
            >
              {loading || githubValidating ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Code2 className="w-5 h-5" />
                  Generate Dockerfile
                </>
              )}
            </button>
          </div>
        </form>
      )}

      {/* Zip Tab */}
      {activeTab === 'zip' && (
        <div className="space-y-4 animate-slide-down">
          <div
            {...getZipRootProps()}
            className={clsx(
              'relative border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-200',
              'bg-slate-800/30',
              isDragActive && 'border-primary-500 bg-primary-500/10 scale-[1.01]',
              dragActive && 'border-docker-500 bg-docker-500/10',
              disabled && 'opacity-50 cursor-not-allowed'
            )}
            onDragEnter={() => setDragActive(true)}
            onDragLeave={() => setDragActive(false)}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => { e.preventDefault(); setDragActive(false); }}
          >
            <input {...getZipInputProps()} />
            <FileCode className={clsx(
              'mx-auto mb-4 w-12 h-12 transition-transform duration-200',
              isDragActive && 'scale-110 text-primary-400',
              'text-slate-500'
            )} />
            <p className="text-lg font-medium text-slate-200 mb-1">
              {isDragActive ? 'Drop your zip file here' : 'Drag & drop a zip file'}
            </p>
            <p className="text-slate-500 text-sm mb-4">
              or click to browse (max 100MB)
            </p>
            {zipFile && (
              <div className="mx-auto max-w-md">
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4 flex items-center gap-4">
                  <FileCode className="w-8 h-8 text-docker-400 flex-shrink-0" />
                  <div className="flex-1 min-w-0 text-left">
                    <p className="font-medium text-slate-100 truncate">{zipFile.name}</p>
                    <p className="text-sm text-slate-500">{formatFileSize(zipFile.size)}</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => { setZipFile(null); setZipValidation(null); fileInputRef.current?.value = ''; }}
                    className="text-slate-500 hover:text-red-400 p-1"
                    aria-label="Remove file"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                {zipValidation && (
                  <p className={clsx('mt-3 text-sm flex items-center justify-center gap-1.5', zipValidation.valid ? 'text-docker-400' : 'text-red-400')}>
                    {zipValidation.valid ? (
                      <>
                        <CheckCircle2 className="w-4 h-4" />
                        Archive valid — {zipValidation.size_mb?.toFixed(1)} MB
                      </>
                    ) : (
                      <>
                        <AlertCircle className="w-4 h-4" />
                        {zipValidation.error}
                      </>
                    )}
                  </p>
                )}
                {zipValidating && (
                  <div className="mt-3 flex items-center justify-center gap-2 text-sm text-primary-400">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Validating...
                  </div>
                )}
              </div>
            )}
          </div>

          {zipFile && (
            <div className="pt-2">
              <button
                onClick={handleZipSubmit}
                disabled={loading || disabled || zipValidating || !zipValidation?.valid}
                className={clsx(
                  'w-full py-3.5 px-6 rounded-xl font-medium text-sm',
                  'flex items-center justify-center gap-2',
                  'transition-all duration-200',
                  'focus:outline-none focus:ring-2 focus:ring-docker-500/50 focus:ring-offset-2 focus:ring-offset-slate-900',
                  loading || zipValidating
                    ? 'bg-docker-500/50 text-slate-300 cursor-not-allowed'
                    : zipValidation?.valid
                      ? 'bg-docker-600 hover:bg-docker-500 text-white shadow-lg shadow-docker-500/25 hover:shadow-docker-500/40'
                      : 'bg-slate-700 text-slate-500 cursor-not-allowed'
                )}
              >
                {loading || zipValidating ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Code2 className="w-5 h-5" />
                    Generate Dockerfile
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}