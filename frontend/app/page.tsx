/** Main page component */
'use client';

import { useState, useCallback } from 'react';
import { Loader2, Sparkles, Zap, Shield, Layers, Globe, CheckCircle2, AlertCircle } from 'lucide-react';
import { clsx } from 'clsx';
import { AnimatedBackground } from '@/components/animated-background';
import { InputMethod } from '@/components/input-method';
import { DockerfilePreview } from '@/components/dockerfile-preview';
import { ProjectInfoCard } from '@/components/project-info-card';
import { useDockerfileGenerator } from '@/hooks/use-generator';
import { useHealthCheck } from '@/hooks/use-health';
import type { DockerfileResult, GitHubInput, ZipInput } from '@/types/api';

export default function HomePage() {
  const [result, setResult] = useState<DockerfileResult | null>(null);
  const [showResult, setShowResult] = useState(false);
  const { health } = useHealthCheck(60000);

  const {
    result: hookResult,
    loading,
    error,
    progress,
    stage,
    generateFromGitHub,
    generateFromZipInput,
    clearResult,
    clearError,
  } = useDockerfileGenerator();

  const handleGitHubSubmit = useCallback(async (input: GitHubInput) => {
    try {
      await generateFromGitHub(input);
      setShowResult(true);
      // Scroll to result
      setTimeout(() => {
        document.getElementById('result-section')?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } catch (err) {
      // Error handled by hook
    }
  }, [generateFromGitHub]);

  const handleZipSubmit = useCallback(async (input: ZipInput) => {
    try {
      await generateFromZipInput(input);
      setShowResult(true);
      setTimeout(() => {
        document.getElementById('result-section')?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } catch (err) {
      // Error handled by hook
    }
  }, [generateFromZipInput]);

  const handleNewGeneration = useCallback(() => {
    setResult(null);
    setShowResult(false);
    clearResult();
    clearError();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [clearResult, clearError]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 relative overflow-x-hidden">
      <AnimatedBackground />
      
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-docker-500 flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20 6L12 1L4 6V12L12 17L20 12V6Z" stroke="currentColor" strokeWidth="2" fill="none"/>
                  <path d="M12 1V17" stroke="currentColor" strokeWidth="2"/>
                  <path d="M4 6L12 12" stroke="currentColor" strokeWidth="2"/>
                  <path d="M20 6L12 12" stroke="currentColor" strokeWidth="2"/>
                </svg>
              </div>
              <span className="font-bold text-xl text-slate-100">Dockerfile Gen</span>
            </div>
            <div className="flex items-center gap-4">
              {health && (
                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <span className="w-2 h-2 rounded-full bg-docker-500 animate-pulse" />
                  API Connected
                </div>
              )}
            </div>
          </div>
        </div>
      </nav>

      <main className="pt-16 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          {/* Hero Section */}
          <section className="mb-12 animate-fade-in">
            <div className="text-center max-w-3xl mx-auto">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-500/10 border border-primary-500/20 text-primary-400 text-sm font-medium mb-6">
                <Sparkles className="w-4 h-4" />
                AI-Enhanced Dockerfile Generation
              </div>
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight mb-6">
                Generate Optimized
                <br />
                <span className="bg-gradient-to-r from-primary-400 via-docker-400 to-purple-400 bg-clip-text text-transparent">
                  Dockerfiles in Seconds
                </span>
              </h1>
              <p className="text-lg sm:text-xl text-slate-400 mb-8 max-w-2xl mx-auto">
                Drop a GitHub repo or zip file — get a production-ready Dockerfile with multi-stage builds, 
                security hardening, and AI-powered optimizations.
              </p>
              
              {/* Feature badges */}
              <div className="flex flex-wrap items-center justify-center gap-3">
                <span className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800/50 border border-slate-700/50 rounded-full text-sm text-slate-300">
                  <Layers className="w-4 h-4 text-primary-400" />
                  Multi-stage
                </span>
                <span className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800/50 border border-slate-700/50 rounded-full text-sm text-slate-300">
                  <Shield className="w-4 h-4 text-docker-400" />
                  Security hardened
                </span>
                <span className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800/50 border border-slate-700/50 rounded-full text-sm text-slate-300">
                  <Zap className="w-4 h-4 text-amber-400" />
                  AI optimized
                </span>
                <span className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800/50 border border-slate-700/50 rounded-full text-sm text-slate-300">
                  <Globe className="w-4 h-4 text-cyan-400" />
                  15+ languages
                </span>
              </div>
            </div>
          </section>

          {/* Error Toast */}
          {error && (
            <div className="mb-8 animate-slide-down" role="alert">
              <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="font-medium text-red-300">Generation Failed</p>
                  <p className="text-sm text-slate-400 mt-1">{error}</p>
                </div>
                <button
                  onClick={clearError}
                  className="text-slate-500 hover:text-slate-300 p-1"
                  aria-label="Dismiss error"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          )}

          {/* Loading Progress */}
          {loading && (
            <div className="mb-8 animate-slide-down" id="progress-section">
              <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-primary-500/20 flex items-center justify-center">
                      <Loader2 className="w-5 h-5 text-primary-400 animate-spin" />
                    </div>
                    <div>
                      <p className="font-medium text-slate-100">Generating Dockerfile</p>
                      <p className="text-sm text-slate-400">{stage}</p>
                    </div>
                  </div>
                  <span className="text-lg font-mono text-primary-400">{progress}%</span>
                </div>
                <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-primary-500 to-docker-500 rounded-full transition-all duration-300 ease-out"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Input Section */}
          {!showResult && (
            <section className="mb-12 animate-slide-up">
              <div className="bg-slate-900/30 border border-slate-800/50 rounded-3xl p-6 sm:p-8 xl:p-10">
                <InputMethod
                  onGitHubSubmit={handleGitHubSubmit}
                  onZipSubmit={handleZipSubmit}
                  loading={loading}
                />
              </div>
            </section>
          )}

          {/* Result Section */}
          {showResult && hookResult && (
            <section id="result-section" className="animate-slide-up">
              {/* Project Info */}
              <ProjectInfoCard projectInfo={hookResult.project_info} />
              
              {/* Dockerfile Preview */}
              <div className="mt-8">
                <DockerfilePreview result={hookResult} className="h-[600px]" />
              </div>

              {/* Actions */}
              <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
                <button
                  onClick={handleNewGeneration}
                  className={clsx(
                    'px-6 py-3 rounded-xl font-medium text-sm',
                    'flex items-center gap-2',
                    'transition-all duration-200',
                    'focus:outline-none focus:ring-2 focus:ring-slate-500/50 focus:ring-offset-2 focus:ring-offset-slate-900',
                    'bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700'
                  )}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Generate Another
                </button>
                
                <div className="flex items-center gap-4 text-sm text-slate-500">
                  <span className="flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 text-docker-400" />
                    Ready to use
                  </span>
                  {hookResult.estimated_image_size_mb && (
                    <span className="flex items-center gap-1.5">
                      <Globe className="w-4 h-4 text-cyan-400" />
                      ~{hookResult.estimated_image_size_mb} MB
                    </span>
                  )}
                </div>
              </div>
            </section>
          )}

          {/* Footer */}
          <footer className="mt-20 text-center">
            <p className="text-slate-500 text-sm">
              Built with Next.js, FastAPI, and ❤️ for developers
            </p>
          </footer>
        </div>
      </main>
    </div>
  );
}