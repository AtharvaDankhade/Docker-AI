/** Custom hook for health check */
import { useState, useEffect, useCallback } from 'react';
import { api } from '@/services/api';
import type { HealthResponse } from '@/types/api';

export function useHealthCheck(interval: number = 30000) {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const checkHealth = useCallback(async () => {
    try {
      const response = await api.healthCheck();
      setHealth(response);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Health check failed');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkHealth();
    
    const timer = setInterval(checkHealth, interval);
    return () => clearInterval(timer);
  }, [checkHealth, interval]);

  return { health, loading, error, refetch: checkHealth };
}