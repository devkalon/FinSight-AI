'use client';

/*
 * Entry experience — applies the FinSight AI design system (UI/UX Pro Max:
 * "Trust & Authority" pattern + "Minimalism & Swiss" style).
 * -------------------------------------------------------------------
 * Palette:   navy #0F172A · card #222735 · field #272F42 · line #334155
 *            trust gold (primary) #F59E0B · tech purple (accent, solid only) #8B5CF6
 *            text #F8FAFC · muted #94A3B8
 * Type:      IBM Plex Sans ("Financial Trust" pairing) — banking-grade, data-friendly.
 * Signature: a self-drawing "compounding curve" — one precise, meaningful graphic,
 *            in keeping with Swiss restraint (the only bold moment on the page).
 * Rule:      accent reserved for CTAs; no purple/pink gradients; 4.5:1 contrast; focus rings.
 */

import React, { useState } from 'react';
import Image from 'next/image';
import { ShieldCheck, Lock, ArrowRight, TrendingUp } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { API_BASE } from '@/lib/api';

export function AuthScreen() {
  const { login, loginWithGoogle, register } = useAuth();
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [monthlyIncome, setMonthlyIncome] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [loading, setLoading] = useState(false);

  // Google Prompt Modal for customizable Google user identity
  const [showGooglePromptModal, setShowGooglePromptModal] = useState(false);
  const [customGoogleEmail, setCustomGoogleEmail] = useState('');
  const [customGoogleName, setCustomGoogleName] = useState('');

  const handleGoogleClick = async () => {
    setErrorMsg('');
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/auth/google/url`).catch(() => null);
      if (res && res.ok) {
        const data = await res.json();
        if (data.client_id_configured && data.url) {
          window.location.href = data.url;
          return;
        }
      }
      setShowGooglePromptModal(true);
    } catch (err: any) {
      setErrorMsg(err.message || 'Google sign-in failed');
    } finally {
      setLoading(false);
    }
  };

  const handleCustomGoogleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customGoogleEmail) return;
    setLoading(true);
    try {
      await loginWithGoogle({
        email: customGoogleEmail,
        full_name: customGoogleName || customGoogleEmail.split('@')[0],
      });
      setShowGooglePromptModal(false);
    } catch (err: any) {
      setErrorMsg(err.message || 'Google sign-in failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    setLoading(true);
    try {
      if (isRegister) {
        await register({
          email,
          password,
          full_name: fullName,
          monthly_income: parseFloat(monthlyIncome) || 0,
        });
      } else {
        await login(email, password);
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0F172A] text-[#F8FAFC] font-[family-name:var(--font-body)] flex flex-col lg:flex-row">
      {/* Signature panel: a compounding curve that draws itself on load. */}
      <SignaturePanel isRegister={isRegister} />

      {/* Sign-in panel */}
      <div className="flex-1 flex flex-col items-center justify-center px-5 py-10 sm:px-8">
        <div className="w-full max-w-sm">
          {/* Wordmark — the serif carries the personality */}
          <div className="mb-8 lg:hidden">
            <Wordmark />
          </div>

          {/* Intro */}
          <div className="mb-6">
            <h2 className="font-[family-name:var(--font-display)] text-2xl sm:text-[28px] leading-tight text-white">
              {isRegister ? 'Start your ledger' : 'Welcome back'}
            </h2>
            <p className="mt-1.5 text-sm text-[#94A3B8]">
              {isRegister
                ? 'A clean slate — no sample data, no assumptions. Just your money, once you add it.'
                : 'Pick up where your money left off.'}
            </p>
          </div>

          {/* Google */}
          <button
            type="button"
            onClick={handleGoogleClick}
            disabled={loading}
            className="w-full py-2.5 px-4 rounded-lg bg-white hover:bg-[#F2F4F3] text-slate-900 font-medium text-sm transition-colors flex items-center justify-center gap-2.5 disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#F59E0B] focus-visible:ring-offset-2 focus-visible:ring-offset-[#0F172A]"
          >
            <GoogleGlyph />
            <span>Continue with Google</span>
          </button>

          <div className="relative flex py-4 items-center">
            <div className="flex-grow border-t border-[#334155]" />
            <span className="flex-shrink mx-3 text-[#64748B] text-[11px] uppercase tracking-wider">or with email</span>
            <div className="flex-grow border-t border-[#334155]" />
          </div>

          {/* Tabs */}
          <div className="flex gap-1 p-1 rounded-lg bg-[#222735] border border-[#334155] mb-5">
            <button
              type="button"
              onClick={() => { setIsRegister(false); setErrorMsg(''); }}
              className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[#F59E0B] ${
                !isRegister ? 'bg-[#F59E0B] text-[#0F172A]' : 'text-[#94A3B8] hover:text-white'
              }`}
            >
              Sign in
            </button>
            <button
              type="button"
              onClick={() => { setIsRegister(true); setErrorMsg(''); }}
              className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[#F59E0B] ${
                isRegister ? 'bg-[#F59E0B] text-[#0F172A]' : 'text-[#94A3B8] hover:text-white'
              }`}
            >
              Create account
            </button>
          </div>

          {errorMsg && (
            <div className="mb-4 p-3 rounded-lg bg-[#3F1D1D] border border-[#7F1D1D] text-[#FCA5A5] text-xs leading-relaxed">
              {errorMsg}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-3.5">
            {isRegister && (
              <Field
                label="Your name"
                type="text"
                required
                value={fullName}
                onChange={setFullName}
                placeholder="What should we call you?"
              />
            )}

            <Field
              label="Email"
              type="email"
              required
              value={email}
              onChange={setEmail}
              placeholder="you@example.com"
            />

            <Field
              label="Password"
              type="password"
              required
              minLength={8}
              value={password}
              onChange={setPassword}
              placeholder={isRegister ? 'At least 8 characters' : 'Your password'}
            />

            {isRegister && (
              <Field
                label="Monthly income (₹) — optional"
                type="number"
                value={monthlyIncome}
                onChange={setMonthlyIncome}
                placeholder="Add it now, or later in Settings"
              />
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-1 py-2.5 rounded-lg bg-[#F59E0B] hover:bg-[#FBBF24] text-[#0F172A] font-semibold text-sm transition-colors disabled:opacity-50 flex items-center justify-center gap-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#FBBF24] focus-visible:ring-offset-2 focus-visible:ring-offset-[#0F172A]"
            >
              <span>{loading ? 'One moment…' : isRegister ? 'Create my account' : 'Sign in'}</span>
              {!loading && <ArrowRight className="w-4 h-4" />}
            </button>
          </form>

          {/* Trust line — honest, not decorative */}
          <div className="mt-6 flex items-center justify-center gap-4 text-[11px] text-[#64748B]">
            <span className="flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-[#F59E0B]" />
              Encrypted at rest
            </span>
            <span className="text-[#334155]">•</span>
            <span className="flex items-center gap-1.5">
              <Lock className="w-3.5 h-3.5 text-[#8B5CF6]" />
              Your data stays yours
            </span>
          </div>
        </div>
      </div>

      {/* Google account modal (fallback when OAuth client isn't configured) */}
      {showGooglePromptModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-[#222735] border border-[#334155] rounded-2xl max-w-md w-full p-6 shadow-2xl">
            <div className="flex items-center gap-2.5 mb-2">
              <GoogleGlyph />
              <h2 className="font-[family-name:var(--font-display)] text-xl text-white">Continue with Google</h2>
            </div>
            <p className="text-xs text-[#94A3B8] mb-5">
              Tell us the Google account to sign in with.
            </p>

            <form onSubmit={handleCustomGoogleSubmit} className="space-y-4">
              <Field
                label="Name"
                type="text"
                value={customGoogleName}
                onChange={setCustomGoogleName}
                placeholder="Your name"
              />
              <Field
                label="Google email"
                type="email"
                required
                value={customGoogleEmail}
                onChange={setCustomGoogleEmail}
                placeholder="you@gmail.com"
              />

              <div className="flex gap-2 pt-1">
                <button
                  type="button"
                  onClick={() => setShowGooglePromptModal(false)}
                  className="flex-1 py-2.5 rounded-lg bg-[#272F42] hover:bg-[#2E3852] text-[#CBD5E1] text-xs font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#F59E0B]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading || !customGoogleEmail}
                  className="flex-1 py-2.5 rounded-lg bg-[#F59E0B] hover:bg-[#FBBF24] text-[#0F172A] text-xs font-semibold disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#FBBF24]"
                >
                  {loading ? 'One moment…' : 'Continue'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

/* ---- Wordmark: Uses the FinSight AI logo ---- */
function Wordmark() {
  return (
    <div className="flex flex-col items-start">
      <Image
        src="/logo.png"
        alt="FinSight AI — Insights Today. Wealth Tomorrow."
        width={220}
        height={60}
        className="object-contain"
        priority
      />
    </div>
  );
}

/* ---- Labeled, controlled input ---- */
function Field({
  label, type, value, onChange, placeholder, required, minLength,
}: {
  label: string;
  type: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  required?: boolean;
  minLength?: number;
}) {
  return (
    <label className="block">
      <span className="block text-[11px] font-medium text-[#94A3B8] mb-1.5">{label}</span>
      <input
        type={type}
        required={required}
        minLength={minLength}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full px-3.5 py-2.5 rounded-lg bg-[#272F42] border border-[#334155] text-[#F8FAFC] text-sm placeholder:text-[#64748B] transition-colors focus:outline-none focus:border-[#F59E0B] focus:ring-1 focus:ring-[#F59E0B]/40"
      />
    </label>
  );
}

/* ---- Google multicolor glyph ---- */
function GoogleGlyph() {
  return (
    <svg className="w-4 h-4" viewBox="0 0 24 24" aria-hidden="true">
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
    </svg>
  );
}

/* ---- Signature: a compounding curve that draws itself on load ---- */
function SignaturePanel({ isRegister }: { isRegister: boolean }) {
  return (
    <div className="relative hidden lg:flex lg:w-[46%] flex-col justify-between overflow-hidden border-r border-[#1E293B] bg-[#0B1120] p-10">
      {/* ambient wash */}
      <div className="pointer-events-none absolute -top-24 -left-24 h-96 w-96 rounded-full bg-[#F59E0B]/10 blur-[110px]" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-72 w-72 rounded-full bg-[#8B5CF6]/[0.06] blur-[90px]" />

      <div className="relative z-10">
        <Wordmark />
      </div>

      {/* the curve */}
      <div className="relative z-10 my-8 flex-1 flex items-center">
        <svg viewBox="0 0 400 220" className="w-full" role="img" aria-label="An upward compounding curve">
          {[0, 55, 110, 165].map((y) => (
            <line key={y} x1="0" y1={40 + y} x2="400" y2={40 + y} stroke="#1E293B" strokeWidth="1" />
          ))}
          <path
            className="fs-curve"
            d="M8 200 C 90 196, 150 170, 210 130 S 320 40, 392 18"
            fill="none"
            stroke="#F59E0B"
            strokeWidth="2.5"
            strokeLinecap="round"
          />
          <circle className="fs-dot" cx="392" cy="18" r="4.5" fill="#8B5CF6" />
        </svg>
      </div>

      <div className="relative z-10 max-w-xs">
        <p className="font-[family-name:var(--font-display)] text-xl leading-snug text-white">
          {isRegister ? 'Every fortune starts at zero.' : 'Small, steady, compounding.'}
        </p>
        <p className="mt-2 text-sm text-[#94A3B8]">
          Import your statements, let the AI make sense of them, and watch the line bend upward — with numbers that are actually yours.
        </p>
      </div>

      <style>{`
        .fs-curve { stroke-dasharray: 620; stroke-dashoffset: 0; }
        .fs-dot { opacity: 1; }
        @media (prefers-reduced-motion: no-preference) {
          .fs-curve { animation: fs-draw 1.9s cubic-bezier(.4,0,.2,1) forwards; }
          .fs-dot { opacity: 0; animation: fs-fade .5s ease 1.7s forwards; }
        }
        @keyframes fs-draw { from { stroke-dashoffset: 620; } to { stroke-dashoffset: 0; } }
        @keyframes fs-fade { to { opacity: 1; } }
      `}</style>
    </div>
  );
}






