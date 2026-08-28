'use client';

import React, { useState } from 'react';
import { Sparkles, Download, User as UserIcon, LogIn, LogOut, Settings, Shield, X, Check } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

export function Navbar() {
  const { user, isAuthenticated, login, register, logout, updatePreferences, deleteAccount } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState<boolean>(false);
  const [isRegisterMode, setIsRegisterMode] = useState<boolean>(false);
  const [showPreferencesModal, setShowPreferencesModal] = useState<boolean>(false);

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
      <header className="h-16 bg-[#0B101D]/80 backdrop-blur-md border-b border-[#1E293B] fixed top-0 right-0 left-64 z-30 px-8 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-semibold border border-emerald-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            FinSight Security Shield Active
          </span>
        </div>

        <div className="flex items-center space-x-4">
          {/* Quick Report Download */}
          <a
            href="http://127.0.0.1:8000/api/v1/reports/export/pdf"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-2 px-3.5 py-1.5 rounded-lg bg-[#151D30] hover:bg-[#1E293B] text-slate-300 text-xs font-medium border border-[#1E293B] transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-slate-400" />
            <span>Export PDF</span>
          </a>

          {/* Advisor Quick Access */}
          <a
            href="/advisor"
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-md shadow-blue-500/20 transition-all"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Ask Advisor</span>
          </a>

          {/* User Auth Widget */}
          {user ? (
            <div className="flex items-center space-x-3 pl-3 border-l border-[#1E293B]">
              <button
                onClick={() => setShowPreferencesModal(true)}
                className="flex items-center space-x-2 hover:bg-[#151D30] p-1.5 rounded-lg transition-colors text-left"
                title="Account Preferences"
              >
                <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-xs font-bold text-white shadow-sm">
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
                className="p-1.5 text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 rounded transition-colors"
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
              className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-[#151D30] hover:bg-[#1E293B] text-slate-200 text-xs font-medium border border-[#1E293B] transition-colors"
            >
              <LogIn className="w-3.5 h-3.5 text-blue-400" />
              <span>Sign In / Register</span>
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

            <div className="flex items-center space-x-2 text-blue-400 mb-2">
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
                    className="w-full px-3.5 py-2 rounded-lg bg-[#151D30] border border-[#1E293B] text-slate-100 text-sm focus:outline-none focus:border-blue-500"
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
                  className="w-full px-3.5 py-2 rounded-lg bg-[#151D30] border border-[#1E293B] text-slate-100 text-sm focus:outline-none focus:border-blue-500"
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
                  className="w-full px-3.5 py-2 rounded-lg bg-[#151D30] border border-[#1E293B] text-slate-100 text-sm focus:outline-none focus:border-blue-500"
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
                    className="w-full px-3.5 py-2 rounded-lg bg-[#151D30] border border-[#1E293B] text-slate-100 text-sm focus:outline-none focus:border-blue-500"
                  />
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm transition-colors shadow-lg shadow-blue-500/20 disabled:opacity-50"
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
                className="text-xs text-slate-400 hover:text-blue-400 transition-colors"
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
                  className="w-full px-3.5 py-2 rounded-lg bg-[#151D30] border border-[#1E293B] text-slate-100 text-sm focus:outline-none focus:border-blue-500"
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
                  className="w-full px-3.5 py-2 rounded-lg bg-[#151D30] border border-[#1E293B] text-slate-100 text-sm focus:outline-none focus:border-blue-500"
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
                    className="w-full px-3.5 py-2 rounded-lg bg-[#151D30] border border-[#1E293B] text-slate-100 text-sm focus:outline-none focus:border-blue-500"
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
                    className="w-full px-3.5 py-2 rounded-lg bg-[#151D30] border border-[#1E293B] text-slate-100 text-sm focus:outline-none focus:border-blue-500"
                  >
                    <option value="new">New Tax Regime</option>
                    <option value="old">Old Tax Regime (80C/80D)</option>
                  </select>
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm transition-colors"
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
