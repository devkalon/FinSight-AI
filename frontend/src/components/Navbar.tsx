'use client';

import React, { useState } from 'react';
import { Sparkles, Download, User as UserIcon, LogIn, LogOut, Settings, Shield, X, Check, Menu } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { api, API_BASE } from '@/lib/api';

export function Navbar({ onToggleSidebar }: { onToggleSidebar?: () => void }) {
  const { user, isAuthenticated, login, loginWithGoogle, register, logout, updatePreferences, deleteAccount } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState<boolean>(false);
  const [isRegisterMode, setIsRegisterMode] = useState<boolean>(false);
  const [showPreferencesModal, setShowPreferencesModal] = useState<boolean>(false);
  const [isExporting, setIsExporting] = useState<boolean>(false);

  // Form states
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [monthlyIncome, setMonthlyIncome] = useState('85000');
  const [errorMsg, setErrorMsg] = useState('');
  const [loading, setLoading] = useState(false);

  // Preferences form
  const [currency, setCurrency] = useState(user?.preferred_currency || 'INR');
  const [guru, setGuru] = useState(user?.preferred_guru || 'balanced');
  const [risk, setRisk] = useState(user?.risk_tolerance || 'moderate');
  const [tax, setTax] = useState(user?.tax_regime || 'new');
  const [prefSuccess, setPrefSuccess] = useState(false);

  const handleExportPdf = async () => {
    setIsExporting(true);
    try {
      await api.downloadStatementPdf();
    } catch {
      // Fallback direct url
      const token = typeof window !== 'undefined' ? localStorage.getItem('finsight_token') : '';
      window.open(`${API_BASE}/reports/export/pdf?token=${token || ''}`, '_blank');
    } finally {
      setIsExporting(false);
    }
  };

  const handleGoogleAuth = async () => {
    setErrorMsg('');
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/auth/google/url`);
      if (!res.ok) {
        throw new Error('Failed to initiate Google OAuth');
      }
      const data = await res.json();
      if (data.client_id_configured && data.url) {
        window.location.href = data.url;
        return;
      } else {
        setErrorMsg('Google OAuth is not configured on this server. Please set GOOGLE_CLIENT_ID in your backend environment variables.');
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Google sign-in failed');
    } finally {
      setLoading(false);
    }
  };

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    setLoading(true);
    try {
      if (isRegisterMode) {
        await register({
          email,
          password,
          full_name: fullName,
          monthly_income: parseFloat(monthlyIncome) || 0,
        });
      } else {
        await login(email, password);
      }
      setShowAuthModal(false);
      setEmail('');
      setPassword('');
    } catch (err: any) {
      setErrorMsg(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handlePreferencesSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await updatePreferences({
      preferred_currency: currency,
      preferred_guru: guru,
      risk_tolerance: risk,
      tax_regime: tax,
    });
    setPrefSuccess(true);
    setTimeout(() => {
      setPrefSuccess(false);
      setShowPreferencesModal(false);
    }, 1200);
  };

  return (
    <>
      <header className="h-16 bg-[#0F172A]/90 backdrop-blur-md border-b border-[#1E293B] fixed top-0 right-0 left-0 lg:left-64 z-30 px-4 sm:px-6 lg:px-8 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <button
            onClick={onToggleSidebar}
            className="lg:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-[#1E293B] transition-colors"
            aria-label="Toggle navigation menu"
          >
            <Menu className="w-5 h-5" />
          </button>

          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-semibold border border-emerald-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            FinSight Math Shield Active
          </span>
        </div>

        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* Quick Report Download */}
          <button
            onClick={handleExportPdf}
            disabled={isExporting}
            className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-[#222735] hover:bg-[#272F42] text-slate-300 text-xs font-medium border border-[#1E293B] transition-colors disabled:opacity-50"
          >
            <Download className="w-3.5 h-3.5 text-slate-400" />
            <span>{isExporting ? 'Generating...' : 'Export PDF'}</span>
          </button>

          {/* Advisor Quick Access */}
          <a
            href="/advisor"
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-[#0F172A] text-xs font-semibold shadow-xs transition-all"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Ask Advisor</span>
          </a>

          {/* User Auth Widget */}
          {user ? (
            <div className="flex items-center space-x-2 pl-2 sm:pl-3 border-l border-[#1E293B]">
              <button
                onClick={() => setShowPreferencesModal(true)}
                className="flex items-center space-x-2 hover:bg-[#222735] p-1.5 rounded-lg transition-colors text-left"
                title="Account Preferences"
              >
                <div className="w-7 h-7 rounded-full bg-amber-500 flex items-center justify-center text-xs font-bold text-[#0F172A] shadow-xs">
                  {user.full_name?.charAt(0) || 'U'}
                </div>
                <div className="hidden md:block">
                  <div className="text-xs font-semibold text-white leading-tight">{user.full_name}</div>
                  <div className="text-[10px] text-slate-400">{user.preferred_currency} • {user.preferred_guru}</div>
                </div>
              </button>

              <button
                onClick={() => setShowPreferencesModal(true)}
                className="p-1.5 text-slate-400 hover:text-white transition-colors"
                title="Preferences"
              >
                <Settings className="w-4 h-4" />
              </button>

              <button
                onClick={() => logout()}
                className="p-1.5 text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 rounded-lg transition-colors"
                title="Log Out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={() => {
                setIsRegisterMode(false);
                setShowAuthModal(true);
              }}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-[#222735] hover:bg-[#272F42] text-slate-200 text-xs font-medium border border-[#1E293B] transition-colors"
            >
              <LogIn className="w-3.5 h-3.5 text-amber-400" />
              <span>Sign In</span>
            </button>
          )}
        </div>
      </header>

      {/* Auth Modal */}
      {showAuthModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-[#0F172A] border border-[#1E293B] rounded-2xl max-w-md w-full p-6 shadow-2xl relative">
            <button
              onClick={() => setShowAuthModal(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center space-x-2 text-amber-400 mb-2">
              <Shield className="w-5 h-5" />
              <span className="text-xs font-bold tracking-wider uppercase">FinSight Security</span>
            </div>

            <h2 className="text-xl font-bold text-white mb-1">
              {isRegisterMode ? 'Create Your Account' : 'Welcome Back'}
            </h2>
            <p className="text-xs text-slate-400 mb-6">
              {isRegisterMode
                ? 'Join FinSight AI for intelligent wealth management and expense automation.'
                : 'Enter your credentials to access your financial dashboard.'}
            </p>

            {errorMsg && (
              <div className="mb-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-medium">
                {errorMsg}
              </div>
            )}

            {/* Continue with Google Button */}
            <button
              type="button"
              onClick={handleGoogleAuth}
              disabled={loading}
              className="w-full mb-4 py-2.5 px-4 rounded-lg bg-white hover:bg-slate-100 text-slate-900 font-semibold text-sm transition-colors flex items-center justify-center space-x-2.5 shadow-sm disabled:opacity-50"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                />
              </svg>
              <span>Continue with Google</span>
            </button>

            <div className="relative flex py-2 items-center mb-4">
              <div className="flex-grow border-t border-[#1E293B]"></div>
              <span className="flex-shrink mx-3 text-slate-500 text-xs uppercase font-medium">or continue with email</span>
              <div className="flex-grow border-t border-[#1E293B]"></div>
            </div>

            <form onSubmit={handleAuthSubmit} className="space-y-4">
              {isRegisterMode && (
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Full Name</label>
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Alex Mercer"
                    className="w-full px-3.5 py-2 rounded-lg bg-[#272F42] border border-[#1E293B] text-slate-100 text-sm focus:outline-none focus:border-amber-500"
                  />
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="alex.mercer@finsight.ai"
                  className="w-full px-3.5 py-2 rounded-lg bg-[#272F42] border border-[#1E293B] text-slate-100 text-sm focus:outline-none focus:border-amber-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Password</label>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full px-3.5 py-2 rounded-lg bg-[#272F42] border border-[#1E293B] text-slate-100 text-sm focus:outline-none focus:border-amber-500"
                />
                {isRegisterMode && (
                  <span className="text-[10px] text-slate-400 mt-1 block">Must be at least 8 characters.</span>
                )}
              </div>

              {isRegisterMode && (
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Estimated Monthly Income (₹)</label>
                  <input
                    type="number"
                    value={monthlyIncome}
                    onChange={(e) => setMonthlyIncome(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-lg bg-[#272F42] border border-[#1E293B] text-slate-100 text-sm focus:outline-none focus:border-amber-500"
                  />
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-[#0F172A] font-semibold text-sm transition-colors shadow-lg shadow-amber-500/20 disabled:opacity-50"
              >
                {loading ? 'Authenticating...' : isRegisterMode ? 'Register Account' : 'Sign In'}
              </button>
            </form>

            <div className="mt-4 text-center">
              <button
                type="button"
                onClick={() => {
                  setIsRegisterMode(!isRegisterMode);
                  setErrorMsg('');
                }}
                className="text-xs text-slate-400 hover:text-amber-400 transition-colors"
              >
                {isRegisterMode
                  ? 'Already have an account? Sign In'
                  : "Don't have an account yet? Create one"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Preferences & Privacy Modal */}
      {showPreferencesModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-[#0F172A] border border-[#1E293B] rounded-2xl max-w-md w-full p-6 shadow-2xl relative">
            <button
              onClick={() => setShowPreferencesModal(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>

            <h2 className="text-xl font-bold text-white mb-1">Profile & Advisory Preferences</h2>
            <p className="text-xs text-slate-400 mb-6">Customize currency, default financial advisor, and privacy settings.</p>

            {prefSuccess && (
              <div className="mb-4 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium flex items-center gap-2">
                <Check className="w-4 h-4" /> Preferences updated successfully!
              </div>
            )}

            <form onSubmit={handlePreferencesSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Preferred Currency</label>
                <select
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-lg bg-[#272F42] border border-[#1E293B] text-slate-100 text-sm focus:outline-none focus:border-amber-500"
                >
                  <option value="INR">INR (₹) — Indian Rupee</option>
                  <option value="USD">USD ($) — US Dollar</option>
                  <option value="EUR">EUR (€) — Euro</option>
                  <option value="GBP">GBP (£) — British Pound</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Default AI Advisory Persona</label>
                <select
                  value={guru}
                  onChange={(e) => setGuru(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-lg bg-[#272F42] border border-[#1E293B] text-slate-100 text-sm focus:outline-none focus:border-amber-500"
                >
                  <option value="balanced">Balanced Wealth Advisor (Consensus)</option>
                  <option value="buffett">Warren Buffett (Value & Indexing)</option>
                  <option value="kiyosaki">Robert Kiyosaki (Cashflow & Assets)</option>
                  <option value="sethi">Ramit Sethi (Conscious Spending)</option>
                  <option value="indian_expert">Indian Wealth Specialist (SIP & Tax)</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Risk Profile</label>
                  <select
                    value={risk}
                    onChange={(e) => setRisk(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-lg bg-[#272F42] border border-[#1E293B] text-slate-100 text-sm focus:outline-none focus:border-amber-500"
                  >
                    <option value="conservative">Conservative</option>
                    <option value="moderate">Moderate</option>
                    <option value="aggressive">Aggressive</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Tax Regime</label>
                  <select
                    value={tax}
                    onChange={(e) => setTax(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-lg bg-[#272F42] border border-[#1E293B] text-slate-100 text-sm focus:outline-none focus:border-amber-500"
                  >
                    <option value="new">New Tax Regime</option>
                    <option value="old">Old Tax Regime (80C/80D)</option>
                  </select>
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-2.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-[#0F172A] font-semibold text-sm transition-colors"
              >
                Save Preferences
              </button>
            </form>

            <div className="mt-6 pt-4 border-t border-[#1E293B] flex justify-between items-center">
              <div>
                <div className="text-xs font-semibold text-rose-400">Right to be Forgotten (GDPR)</div>
                <div className="text-[10px] text-slate-400">Permanently delete all stored financial data</div>
              </div>
              <button
                onClick={async () => {
                  if (confirm('Are you sure you want to permanently delete your account and all financial data? This cannot be undone.')) {
                    await deleteAccount();
                    setShowPreferencesModal(false);
                  }
                }}
                className="px-3 py-1 rounded bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 text-xs font-semibold border border-rose-500/20 transition-colors"
              >
                Delete Data
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
