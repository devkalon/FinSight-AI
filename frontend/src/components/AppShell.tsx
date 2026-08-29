'use client';

import React, { useState } from 'react';
import { usePathname } from 'next/navigation';
import Image from 'next/image';
import { Sidebar } from '@/components/Sidebar';
import { Navbar } from '@/components/Navbar';
import { AuthScreen } from '@/components/AuthScreen';
import { useAuth } from '@/context/AuthContext';

// Routes that must render WITHOUT the auth gate. The OAuth callback lands here
// before a token exists; if the gate intercepted it, the token-exchange effect
// would never run and the user would be bounced back to the login screen.
const PUBLIC_ROUTE_PREFIXES = ['/auth/'];

export function AppShell({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const isPublicRoute = PUBLIC_ROUTE_PREFIXES.some((prefix) => pathname?.startsWith(prefix));

  // Public routes (e.g. the Google OAuth callback) render standalone, bypassing
  // both the loading spinner and the auth gate.
  if (isPublicRoute) {
    return <>{children}</>;
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0F172A] flex flex-col items-center justify-center space-y-4">
        <Image
          src="/logo.png"
          alt="FinSight AI"
          width={160}
          height={44}
          className="object-contain animate-pulse"
          priority
        />
        <div className="w-8 h-8 border-2 border-amber-500/20 border-t-amber-500 rounded-full animate-spin" />
        <span className="text-xs font-semibold text-slate-400">Verifying Secure Session...</span>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AuthScreen />;
  }

  return (
    <div className="min-h-screen bg-[#0F172A] text-slate-100 flex">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="flex-1 lg:ml-64 flex flex-col min-h-screen">
        <Navbar onToggleSidebar={() => setSidebarOpen((prev) => !prev)} />
        <main className="flex-1 px-4 sm:px-6 lg:px-8 pt-20 pb-12 max-w-7xl w-full mx-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
