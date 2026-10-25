/** Dockerfile preview with Monaco editor */
'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import Editor from '@monaco-editor/react';
import { 
  Copy, 
  Download, 
  Check, 
  AlertTriangle, 
  Info,
  ChevronDown,
  ChevronUp,
  Zap,
  Shield,
  Layers,
  Clock,
  FileText
} from 'lucide-react';
import { clsx } from 'clsx';
import { useDockerfileActions } from '@/hooks';
import type { DockerfileResult } from '@/types/api';

interface DockerfilePreviewProps {
  result: DockerfileResult | null;
  className?: string;
}

export function DockerfilePreview({ result, className }: DockerfilePreviewProps) {
  const [copied, setCopied] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [showWarnings, setShowWarnings] = useState(false);
  const [showOptimizations, setShowOptimizations] = useState(true);
  const [showAISuggestions, setShowAISuggestions] = useState(true);
  // Editor ref not needed - Monaco Editor doesn't expose ref
  const editorRef = useRef(null);
  const { copyToClipboard, downloadDockerfile, validateDockerfile, getDockerfileStats } = useDockerfileActions();
  
  const validationWarnings = result ? validateDockerfile(result.dockerfile) : [];
  const stats = result ? getDockerfileStats(result.dockerfile) : null;

  const handleCopy = useCallback(async () => {
    if (!result) return;
    const success = await copyToClipboard(result.dockerfile);
    if (success) setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [result, copyToClipboard]);

  const handleDownload = useCallback(() => {
    if (!result) return;
    downloadDockerfile(result.dockerfile, 'Dockerfile');
  }, [result, downloadDockerfile]);

  if (!result) {
    return (
      <div className={clsx('h-96 bg-slate-800/30 border border-slate-700/50 rounded-2xl flex items-center justify-center', className)}>
        <div className="text-center p-8">
          <FileText className="w-16 h-16 text-slate-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-slate-400 mb-2">No Dockerfile Generated</h3>
          <p className="text-slate-500">Provide a GitHub repository or zip file to generate a Dockerfile</p>
        </div>
      </div>
    );
  }

  const language = result.project_info.language;
  const framework = result.project_info.framework;

  return (
    <div className={clsx('bg-slate-900/50 border border-slate-700/50 rounded-2xl overflow-hidden flex flex-col', className)}>
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 border-b border-slate-700/50 bg-slate-800/50">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary-500/20 flex items-center justify-center">
            <FileText className="w-5 h-5 text-primary-400" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-100">Generated Dockerfile</h3>
            <p className="text-sm text-slate-500">
              {language} {framework !== 'unknown' && `• ${framework}`}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {/* Stats */}
          {stats && (
            <div className="hidden sm:flex items-center gap-4 text-xs text-slate-400">
              <span className="flex items-center gap-1">
                <FileText className="w-3 h-3" /> {stats.totalLines} lines
              </span>
              <span className="flex items-center gap-1">
                <Layers className="w-3 h-3" /> {stats.stageCount} stage{stats.stageCount > 1 ? 's' : ''}
              </span>
              <span className="flex items-center gap-1">
                <Zap className="w-3 h-3" /> {stats.instructionCount} instructions
              </span>
              {stats.hasHealthCheck && (
                <span className="flex items-center gap-1 text-docker-400">
                  <Shield className="w-3 h-3" /> Health check
                </span>
              )}
              {stats.hasNonRootUser && (
                <span className="flex items-center gap-1 text-docker-400">
                  <Shield className="w-3 h-3" /> Non-root
                </span>
              )}
            </div>
          )}
          
          {/* Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              disabled={copied || downloading}
              className={clsx(
                'p-2 rounded-lg transition-colors',
                'bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-slate-100',
                'disabled:opacity-50'
              )}
              aria-label={copied ? 'Copied!' : 'Copy to clipboard'}
            >
              {copied ? (
                <Check className="w-5 h-5 text-docker-500" />
              ) : (
                <Copy className="w-5 h-5" />
              )}
            </button>
            
            <button
              onClick={handleDownload}
              disabled={downloading}
              className={clsx(
                'p-2 rounded-lg transition-colors',
                'bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-slate-100',
                'disabled:opacity-50'
              )}
              aria-label="Download Dockerfile"
            >
              <Download className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Editor */}
      <div className="flex-1 min-h-96 relative">
        <Editor
          height="100%"
          defaultLanguage="dockerfile"
          value={result.dockerfile}
          theme="vs-dark"
          options={{
            readOnly: true,
            minimap: { enabled: false },
            lineNumbers: 'on',
            fontSize: 13,
            fontFamily: '"JetBrains Mono", "Fira Code", monospace',
            tabSize: 2,
            wordWrap: 'on',
            scrollBeyondLastLine: false,
            automaticLayout: true,
            renderLineHighlight: 'line',
            overviewRulerLanes: 0,
            glyphMargin: false,
            folding: true,
            renderWhitespace: 'selection',
            cursorBlinking: 'smooth',
            smoothScrolling: true,
          }}
        />
      </div>

      {/* Info Panels */}
      <div className="border-t border-slate-700/50 bg-slate-800/30">
        {/* Optimizations Applied */}
        {result.optimizations_applied.length > 0 && (
          <details className="group" open={showOptimizations}>
            <summary 
              onClick={() => setShowOptimizations(!showOptimizations)}
              className={clsx(
                'flex items-center gap-3 p-4 cursor-pointer',
                'hover:bg-slate-800/50 transition-colors'
              )}
            >
              <Layers className={clsx('w-5 h-5 text-docker-400', showOptimizations && 'rotate-180')} />
              <span className="font-medium text-slate-100">Optimizations Applied</span>
              <span className="ml-auto px-2 py-0.5 bg-docker-500/20 text-docker-400 text-xs font-medium rounded">
                {result.optimizations_applied.length}
              </span>
            </summary>
            <div className="px-4 pb-4 animate-slide-down">
              <ul className="space-y-2">
                {result.optimizations_applied.map((opt, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm text-slate-300">
                    <span className="w-2 h-2 rounded-full bg-docker-500" />
                    <span className="font-mono text-xs text-slate-400">{opt}</span>
                    <span className="ml-auto text-xs text-slate-500">
                      {getOptimizationDescription(opt)}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </details>
        )}

        {/* AI Suggestions */}
        {result.ai_suggestions && result.ai_suggestions.length > 0 && (
          <details className="group" open={showAISuggestions}>
            <summary 
              onClick={() => setShowAISuggestions(!showAISuggestions)}
              className={clsx(
                'flex items-center gap-3 p-4 cursor-pointer',
                'hover:bg-slate-800/50 transition-colors'
              )}
            >
              <Zap className={clsx('w-5 h-5 text-purple-400', showAISuggestions && 'rotate-180')} />
              <span className="font-medium text-slate-100">AI Suggestions</span>
              <span className="ml-auto px-2 py-0.5 bg-purple-500/20 text-purple-400 text-xs font-medium rounded">
                {result.ai_suggestions.length}
              </span>
            </summary>
            <div className="px-4 pb-4 animate-slide-down">
              <ul className="space-y-2">
                {result.ai_suggestions.map((suggestion, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                    <span className="w-2 h-2 rounded-full bg-purple-500 mt-2 flex-shrink-0" />
                    <span>{suggestion}</span>
                  </li>
                ))}
              </ul>
            </div>
          </details>
        )}

        {/* Warnings */}
        {(validationWarnings.length > 0 || result.warnings.length > 0) && (
          <details className="group" open={showWarnings}>
            <summary 
              onClick={() => setShowWarnings(!showWarnings)}
              className={clsx(
                'flex items-center gap-3 p-4 cursor-pointer',
                'hover:bg-slate-800/50 transition-colors'
              )}
            >
              <AlertTriangle className={clsx('w-5 h-5 text-amber-400', showWarnings && 'rotate-180')} />
              <span className="font-medium text-slate-100">Warnings</span>
              <span className="ml-auto px-2 py-0.5 bg-amber-500/20 text-amber-400 text-xs font-medium rounded">
                {validationWarnings.length + result.warnings.length}
              </span>
            </summary>
            <div className="px-4 pb-4 animate-slide-down">
              <ul className="space-y-2">
                {[...validationWarnings, ...result.warnings].map((warning, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-amber-300">
                    <Info className="w-4 h-4 mt-0.5 flex-shrink-0 text-amber-400" />
                    <span>{warning}</span>
                  </li>
                ))}
              </ul>
            </div>
          </details>
        )}

        {/* Estimated Size */}
        {result.estimated_image_size_mb && (
          <div className="p-4 flex items-center gap-3 bg-slate-800/50">
            <Clock className="w-5 h-5 text-slate-500" />
            <span className="text-sm text-slate-300">
              Estimated image size: <strong className="text-slate-100">{result.estimated_image_size_mb} MB</strong>
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

function getOptimizationDescription(opt: string): string {
  const descriptions: Record<string, string> = {
    multi_stage_build: 'Separates build and runtime environments',
    layer_caching_optimized: 'Orders layers for maximum cache reuse',
    non_root_user: 'Runs container as non-root user',
    read_only_filesystem_ready: 'Compatible with read-only root filesystem',
    minimal_base_image: 'Uses minimal base image (Alpine/Distroless)',
    static_binary: 'Produces statically linked binary',
    scratch_or_distroless_runtime: 'Uses scratch or distroless runtime image',
    nextjs_standalone_output: 'Uses Next.js standalone output for minimal size',
    npm_ci_for_reproducible_builds: 'Uses npm ci for reproducible installs',
    uv_for_fast_installs: 'Uses uv for fast Python package installs',
    virtual_environment_isolation: 'Isolates dependencies in virtual environment',
    jvm_container_awareness: 'Configures JVM for container memory limits',
    memory_percentage_limits: 'Sets JVM heap as percentage of container memory',
  };
  return descriptions[opt] || '';
}