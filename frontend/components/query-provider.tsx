/** Query Provider placeholder - React Query not needed for this app */
'use client';

import { ReactNode } from 'react';

export function QueryProvider({ children }: { children: ReactNode }) {
  return <>{children}</>;
}