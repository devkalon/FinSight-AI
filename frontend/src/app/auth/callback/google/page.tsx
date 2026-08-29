'use client';

import React, { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Image from 'next/image';
import { CheckCircle2, AlertCircle } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { API_BASE } from '@/lib/api';

function GoogleCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { applyToken } = useAuth();
  const [statusText, setStatusText] = useState('Exchanging Google OAuth 2.0 Token...');
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    async function exchangeToken() {
      const code = searchParams.get('code');
      const error = searchParams.get('error');

      if (error) {
        setErrorMsg(`Google OAuth error: ${error}`);
        return;
      }

      if (!code) {
        setErrorMsg('No authorization code returned from Google.');
        return;
      }

      try {
        setStatusText('Verifying Google Identity and Provisioning Profile...');
        const res = await fetch(`${API_BASE}/auth/google/callback`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code }),
        });

        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: 'Failed to verify Google token' }));
          throw new Error(err.detail || 'Google authentication failed');
        }

        const data = await res.json();
        if (data.access_token) {
          // Update AuthContext state (token + profile) BEFORE navigating, so the
          // gated AppShell sees an authenticated session and doesn't bounce the
          // user back to the sign-in screen.
          await applyToken(data.access_token);
          setStatusText('Authentication Successful! Redirecting to Dashboard...');
          setTimeout(() => {
            router.push('/dashboard');
          }, 800);
        } else {
          throw new Error('No access token returned from server.');
        }
      } catch (err: any) {
        setErrorMsg(err.message || 'Failed to complete Google OAuth2 flow');
      }
    }

    exchangeToken();
  }, [searchParams, router, applyToken]);

  return (
    <div className="min-h-screen bg-[#0F172A] flex flex-col items-center justify-center p-4 text-slate-100">
      <div className="bg-[#222735] border border-[#1E293B] rounded-2xl p-8 max-w-md w-full text-center space-y-5 shadow-2xl">
        <div className="w-12 h-12 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center mx-auto">
          {errorMsg ? (
            <AlertCircle className="w-6 h-6 text-rose-400" />
          ) : (
            <Image src="/logo.png" alt="FinSight AI" width={36} height={36} className="object-contain animate-pulse" />
          )}
        </div>

        <div>
          <h1 className="text-xl font-bold text-white mb-1">
            {errorMsg ? 'Google Sign-In Failed' : 'Authenticating with Google'}
          </h1>
          <p className="text-xs text-slate-400">
            {errorMsg || statusText}
          </p>
        </div>

        {errorMsg ? (
          <button
            onClick={() => (window.location.href = '/')}
            className="w-full py-2.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-[#0F172A] text-xs font-semibold"
          >
            Back to Sign In
          </button>
        ) : (
          <div className="w-8 h-8 border-2 border-amber-500/20 border-t-amber-500 rounded-full animate-spin mx-auto" />
        )}
      </div>
    </div>
  );
}

export default function GoogleCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-[#0F172A] flex flex-col items-center justify-center p-4 text-slate-100">
          <div className="w-8 h-8 border-2 border-amber-500/20 border-t-amber-500 rounded-full animate-spin mx-auto" />
        </div>
      }
    >
      <GoogleCallbackContent />
    </Suspense>
  );
}
