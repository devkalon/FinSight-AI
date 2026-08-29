'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { API_BASE } from '@/lib/api';

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  preferred_currency: string;
  preferred_guru: string;
  monthly_income: number;
  risk_tolerance?: string;
  country_code?: string;
  tax_regime?: string;
  is_active: boolean;
}

export interface UserPreferences {
  preferred_currency?: string;
  preferred_guru?: string;
  risk_tolerance?: string;
  tax_regime?: string;
}

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  loginWithGoogle: (googleData?: { email?: string; full_name?: string; id_token?: string }) => Promise<void>;
  applyToken: (accessToken: string) => Promise<void>;
  register: (data: { email: string; password: string; full_name: string; monthly_income?: number }) => Promise<void>;
  logout: () => Promise<void>;
  updatePreferences: (prefs: UserPreferences) => Promise<void>;
  deleteAccount: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Initialize and check persisted token on mount
  useEffect(() => {
    async function initAuth() {
      const savedToken = typeof window !== 'undefined' ? localStorage.getItem('finsight_token') : null;
      if (savedToken) {
        setToken(savedToken);
        await fetchUserProfile(savedToken);
      } else {
        setToken(null);
        setUser(null);
        setIsLoading(false);
      }
    }
    initAuth();
  }, []);

  const fetchUserProfile = async (authToken: string) => {
    try {
      const res = await fetch(`${API_BASE}/auth/me`, {
        headers: { Authorization: `Bearer ${authToken}` },
      });
      if (res.ok) {
        const data = await res.json();
        setUser(data);
      } else {
        localStorage.removeItem('finsight_token');
        setToken(null);
        setUser(null);
      }
    } catch {
      localStorage.removeItem('finsight_token');
      setToken(null);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  // Persist a token obtained out-of-band (e.g. the Google OAuth redirect flow)
  // and immediately hydrate context state + profile, so gated UI (AppShell)
  // reflects the authenticated session without needing a full page reload.
  const applyToken = async (accessToken: string) => {
    setIsLoading(true);
    try {
      setToken(accessToken);
      if (typeof window !== 'undefined') {
        localStorage.setItem('finsight_token', accessToken);
      }
      await fetchUserProfile(accessToken);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Login failed');
      }
      const data = await res.json();
      setToken(data.access_token);
      localStorage.setItem('finsight_token', data.access_token);
      await fetchUserProfile(data.access_token);
    } finally {
      setIsLoading(false);
    }
  };

  const loginWithGoogle = async (googleData?: { email?: string; full_name?: string; id_token?: string }) => {
    setIsLoading(true);
    try {
      const payload = {
        email: googleData?.email || 'google.user@finsight.ai',
        full_name: googleData?.full_name || 'Google Workspace User',
        id_token: googleData?.id_token || 'google-mock-jwt-token-oauth2',
        google_id: 'google-oauth2-verified'
      };

      const res = await fetch(`${API_BASE}/auth/google`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        setToken(data.access_token);
        localStorage.setItem('finsight_token', data.access_token);
        await fetchUserProfile(data.access_token);
      } else {
        const err = await res.json();
        throw new Error(err.detail || 'Google sign-in failed');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (payload: { email: string; password: string; full_name: string; monthly_income?: number }) => {
    setIsLoading(true);
    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Registration failed');
      }
      const data = await res.json();
      setToken(data.access_token);
      localStorage.setItem('finsight_token', data.access_token);
      await fetchUserProfile(data.access_token);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    if (token) {
      try {
        await fetch(`${API_BASE}/auth/logout`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        });
      } catch {
        // Continue local clearing
      }
    }
    localStorage.removeItem('finsight_token');
    setToken(null);
    setUser(null);
  };

  const updatePreferences = async (prefs: UserPreferences) => {
    if (!token) return;
    const res = await fetch(`${API_BASE}/auth/me/preferences`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(prefs),
    });
    if (res.ok) {
      const updated = await res.json();
      setUser(updated);
    }
  };

  const deleteAccount = async () => {
    if (!token) return;
    await fetch(`${API_BASE}/auth/me`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    });
    localStorage.removeItem('finsight_token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token,
        isLoading,
        login,
        loginWithGoogle,
        applyToken,
        register,
        logout,
        updatePreferences,
        deleteAccount,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
