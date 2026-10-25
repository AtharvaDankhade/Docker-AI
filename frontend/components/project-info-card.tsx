/** Project info card component */
'use client';

import { clsx } from 'clsx';
import { 
  Code2, 
  Box, 
  Package, 
  Play, 
  Hammer, 
  Terminal,
  Globe,
  FileJson,
  Lock,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import type { ProjectInfo } from '@/types/api';

interface ProjectInfoCardProps {
  projectInfo: ProjectInfo;
}

const LANGUAGE_ICONS: Record<string, React.ReactNode> = {
  nodejs: <Code2 className="w-5 h-5 text-green-400" />,
  python: <Code2 className="w-5 h-5 text-yellow-400" />,
  go: <Code2 className="w-5 h-5 text-cyan-400" />,
  java: <Code2 className="w-5 h-5 text-orange-400" />,
  rust: <Code2 className="w-5 h-5 text-red-400" />,
  dotnet: <Code2 className="w-5 h-5 text-purple-400" />,
  php: <Code2 className="w-5 h-5 text-violet-400" />,
  ruby: <Code2 className="w-5 h-5 text-red-500" />,
  dart: <Code2 className="w-5 h-5 text-blue-400" />,
  elixir: <Code2 className="w-5 h-5 text-purple-500" />,
  haskell: <Code2 className="w-5 h-5 text-amber-400" />,
  scala: <Code2 className="w-5 h-5 text-red-400" />,
  kotlin: <Code2 className="w-5 h-5 text-orange-400" />,
  swift: <Code2 className="w-5 h-5 text-orange-500" />,
  bun: <Code2 className="w-5 h-5 text-amber-400" />,
  deno: <Code2 className="w-5 h-5 text-green-400" />,
};

const LANGUAGE_COLORS: Record<string, string> = {
  nodejs: 'bg-green-500/20 text-green-400 border-green-500/30',
  python: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  go: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
  java: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  rust: 'bg-red-500/20 text-red-400 border-red-500/30',
  dotnet: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  php: 'bg-violet-500/20 text-violet-400 border-violet-500/30',
  ruby: 'bg-red-500/20 text-red-400 border-red-500/30',
  dart: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  elixir: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  haskell: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  scala: 'bg-red-500/20 text-red-400 border-red-500/30',
  kotlin: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  swift: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  bun: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  deno: 'bg-green-500/20 text-green-400 border-green-500/30',
};

export function ProjectInfoCard({ projectInfo }: ProjectInfoCardProps) {
  const language = projectInfo.language;
  const framework = projectInfo.framework;
  
  const formatFramework = (fw: string) => {
    return fw
      .split('_')
      .map(w => w.charAt(0).toUpperCase() + w.slice(1))
      .join(' ');
  };

  const formatLanguage = (lang: string) => {
    const names: Record<string, string> = {
      nodejs: 'Node.js',
      dotnet: '.NET',
    };
    return names[lang] || lang.charAt(0).toUpperCase() + lang.slice(1);
  };

  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-6">
      <div className="flex items-start justify-between gap-4 mb-6">
        <div className="flex items-center gap-4">
          <div className={clsx(
            'w-14 h-14 rounded-xl flex items-center justify-center',
            LANGUAGE_COLORS[language] || 'bg-slate-700 text-slate-400'
          )}>
            {LANGUAGE_ICONS[language] || <Code2 className="w-6 h-6" />}
          </div>
          <div>
            <h3 className="text-xl font-semibold text-slate-100">
              {formatLanguage(language)}
            </h3>
            <p className="text-slate-400">
              {framework !== 'unknown' ? formatFramework(framework) : 'No framework detected'}
            </p>
          </div>
        </div>
        {projectInfo.dockerfile_exists && (
          <span className="flex items-center gap-1.5 px-3 py-1.5 bg-docker-500/20 text-docker-400 text-sm font-medium rounded-lg">
            <CheckCircle2 className="w-4 h-4" />
            Existing Dockerfile
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Package Manager */}
        <div className="bg-slate-900/50 border border-slate-700/50 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-slate-700/50 flex items-center justify-center">
              <Package className="w-5 h-5 text-slate-400" />
            </div>
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider">Package Manager</p>
              <p className="font-medium text-slate-100">
                {projectInfo.package_manager || 'Not detected'}
              </p>
            </div>
          </div>
        </div>

        {/* Port */}
        <div className="bg-slate-900/50 border border-slate-700/50 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-slate-700/50 flex items-center justify-center">
              <Globe className="w-5 h-5 text-slate-400" />
            </div>
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider">Port</p>
              <p className="font-medium text-slate-100">
                {projectInfo.port ? `${projectInfo.port}` : 'Not detected'}
              </p>
            </div>
          </div>
        </div>

        {/* Entry Point */}
        <div className="bg-slate-900/50 border border-slate-700/50 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-slate-700/50 flex items-center justify-center">
              <Play className="w-5 h-5 text-slate-400" />
            </div>
            <div className="min-w-0">
              <p className="text-xs text-slate-500 uppercase tracking-wider">Entry Point</p>
              <p className="font-medium text-slate-100 truncate font-mono text-sm">
                {projectInfo.entry_point || 'Not detected'}
              </p>
            </div>
          </div>
        </div>

        {/* Build Command */}
        <div className="bg-slate-900/50 border border-slate-700/50 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-slate-700/50 flex items-center justify-center">
              <Hammer className="w-5 h-5 text-slate-400" />
            </div>
            <div className="min-w-0">
              <p className="text-xs text-slate-500 uppercase tracking-wider">Build Command</p>
              <p className="font-medium text-slate-100 truncate font-mono text-sm">
                {projectInfo.build_command || 'Auto-detected'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Additional Info */}
      {(projectInfo.dependencies && Object.keys(projectInfo.dependencies).length > 0) ||
       (projectInfo.config_files && projectInfo.config_files.length > 0) && (
        <div className="mt-6 pt-6 border-t border-slate-700/50">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {projectInfo.dependencies && Object.keys(projectInfo.dependencies).length > 0 && (
              <div>
                <p className="text-xs text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <Package className="w-3.5 h-3.5" />
                  Dependencies ({Object.keys(projectInfo.dependencies).length})
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {Object.entries(projectInfo.dependencies).slice(0, 8).map(([name, version]) => (
                    <span key={name} className="px-2 py-1 bg-slate-900/50 border border-slate-700/50 rounded text-xs font-mono text-slate-300">
                      {name}@{version}
                    </span>
                  ))}
                  {Object.keys(projectInfo.dependencies).length > 8 && (
                    <span className="px-2 py-1 bg-slate-900/50 border border-slate-700/50 rounded text-xs text-slate-500">
                      +{Object.keys(projectInfo.dependencies).length - 8} more
                    </span>
                  )}
                </div>
              </div>
            )}
            
            {projectInfo.config_files && projectInfo.config_files.length > 0 && (
              <div>
                <p className="text-xs text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <FileJson className="w-3.5 h-3.5" />
                  Config Files
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {projectInfo.config_files.slice(0, 10).map((file) => (
                    <span key={file} className="px-2 py-1 bg-slate-900/50 border border-slate-700/50 rounded text-xs font-mono text-slate-300">
                      {file}
                    </span>
                  ))}
                  {projectInfo.config_files.length > 10 && (
                    <span className="px-2 py-1 bg-slate-900/50 border border-slate-700/50 rounded text-xs text-slate-500">
                      +{projectInfo.config_files.length - 10} more
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {projectInfo.dockerignore_exists && (
        <div className="mt-4 p-3 bg-docker-500/10 border border-docker-500/20 rounded-xl flex items-center gap-2">
          <Lock className="w-5 h-5 text-docker-400" />
          <span className="text-sm text-docker-300">
            <strong>.dockerignore</strong> found — build context will be optimized
          </span>
        </div>
      )}
    </div>
  );
}