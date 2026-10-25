/** Custom hook for Dockerfile actions (copy, download, validate) */
import { useState, useCallback } from 'react';
import type { DockerfileResult } from '@/types/api';

export function useDockerfileActions() {
  const [copied, setCopied] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const copyToClipboard = useCallback(async (dockerfile: string) => {
    try {
      await navigator.clipboard.writeText(dockerfile);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      return true;
    } catch {
      return false;
    }
  }, []);

  const downloadDockerfile = useCallback((
    dockerfile: string,
    filename: string = 'Dockerfile'
  ) => {
    setDownloading(true);
    try {
      const blob = new Blob([dockerfile], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } finally {
      setDownloading(false);
    }
  }, []);

  const validateDockerfile = useCallback((dockerfile: string): string[] => {
    const warnings: string[] = [];
    
    // Check for common issues
    if (/:latest\b/.test(dockerfile)) {
      warnings.push('Using "latest" tag - consider pinning to specific version');
    }
    
    if (/USER root/.test(dockerfile) && !/USER \w+/.test(dockerfile.split('USER root')[1] || '')) {
      warnings.push('Running as root - consider switching to non-root user');
    }
    
    if (/ADD https?:\/\//.test(dockerfile)) {
      warnings.push('Using ADD with URL - prefer COPY with explicit download');
    }
    
    if (/npm install/.test(dockerfile) && !/npm ci/.test(dockerfile)) {
      warnings.push('Using "npm install" instead of "npm ci" for reproducible builds');
    }
    
    if (/COPY \. \./.test(dockerfile) && !/\.dockerignore/.test(dockerfile)) {
      warnings.push('No .dockerignore referenced - consider adding one');
    }
    
    if (!/^FROM /.test(dockerfile.trim())) {
      warnings.push('No FROM instruction found');
    }
    
    return warnings;
  }, []);

  const getDockerfileStats = useCallback((dockerfile: string) => {
    const lines = dockerfile.split('\n');
    const instructions = lines.filter(l => /^(FROM|RUN|COPY|ADD|CMD|ENTRYPOINT|WORKDIR|EXPOSE|ENV|USER|HEALTHCHECK|ARG|VOLUME|LABEL|ONBUILD|STOPSIGNAL|SHELL)\b/i.test(l.trim()));
    const stages = lines.filter(l => /^FROM /i.test(l.trim())).length;
    
    return {
      totalLines: lines.length,
      instructionCount: instructions.length,
      stageCount: stages,
      hasMultiStage: stages > 1,
      hasHealthCheck: /HEALTHCHECK/i.test(dockerfile),
      hasNonRootUser: /USER \w+/i.test(dockerfile) && !/USER root/i.test(dockerfile),
    };
  }, []);

  return {
    copied,
    downloading,
    copyToClipboard,
    downloadDockerfile,
    validateDockerfile,
    getDockerfileStats,
  };
}