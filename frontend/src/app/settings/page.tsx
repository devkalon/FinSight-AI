'use client';

import React, { useState } from 'react';
import {
  Settings as SettingsIcon,
  ShieldCheck,
  Check,
  User,
  DollarSign,
  Bot,
  Percent,
  Trash2,
  Lock,
  Zap,
  Globe,
  Sliders
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

export default function SettingsPage() {
  const { user, updatePreferences, deleteAccount } = useAuth();

  const [currency, setCurrency] = useState(user?.preferred_currency || 'INR');
  const [guru, setGuru] = useState(user?.preferred_guru || 'balanced');
  const [risk, setRisk] = useState(user?.risk_tolerance || 'moderate');
  const [tax, setTax] = useState(user?.tax_regime || 'new');
  const [monthlyIncome, setMonthlyIncome] = useState(String(user?.monthly_income || 85000));
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await updatePreferences({
        preferred_currency: currency,
        preferred_guru: guru,
        risk_tolerance: risk,
        tax_regime: tax,
      });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 2500);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="border-b border-[#1D263B] pb-6">
        <h1 className="text-2xl font-bold text-white tracking-tight">Platform Settings & Privacy</h1>
        <p className="text-slate-400 text-xs mt-0.5">
          Manage currency standards, default AI advisory personas, tax regimes, and GDPR data rights.
        </p>
      </div>

      {savedSuccess && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold flex items-center space-x-2">
          <Check className="w-4 h-4" />
          <span>Preferences updated and persisted across your workspace!</span>
        </div>
      )}

      {/* Profile & Account Details */}
      <form onSubmit={handleSave} className="space-y-6">
        <div className="p-6 rounded-2xl bg-[#0F1626] border border-[#1D263B] space-y-4">
          <div className="flex items-center space-x-2 text-white font-bold text-sm border-b border-[#1D263B] pb-3">
            <User className="w-4 h-4 text-blue-400" />
            <span>Profile & Account Info</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="text-slate-400 block mb-1">Full Name</label>
              <input
                type="text"
                disabled
                value={user?.full_name || 'Alex Mercer'}
                className="w-full p-2.5 bg-[#0A0E1A] border border-[#1D263B] rounded-xl text-slate-300 opacity-80 cursor-not-allowed"
              />
            </div>

            <div>
              <label className="text-slate-400 block mb-1">Email Address</label>
              <input
                type="email"
                disabled
                value={user?.email || 'alex.mercer@finsight.ai'}
                className="w-full p-2.5 bg-[#0A0E1A] border border-[#1D263B] rounded-xl text-slate-300 opacity-80 cursor-not-allowed"
              />
            </div>
          </div>
        </div>

        {/* Currency & Financial Standards */}
        <div className="p-6 rounded-2xl bg-[#0F1626] border border-[#1D263B] space-y-4">
          <div className="flex items-center space-x-2 text-white font-bold text-sm border-b border-[#1D263B] pb-3">
            <Globe className="w-4 h-4 text-emerald-400" />
            <span>Currency & Valuation Standard</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="text-slate-400 block mb-1">Base Currency</label>
              <select
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
                className="w-full p-2.5 bg-[#0A0E1A] border border-[#1D263B] rounded-xl text-slate-200"
              >
                <option value="INR">INR (₹) — Indian Rupee (Lakhs / Crores standard)</option>
                <option value="USD">USD ($) — United States Dollar</option>
                <option value="EUR">EUR (€) — Euro</option>
                <option value="GBP">GBP (£) — British Pound</option>
              </select>
            </div>

            <div>
              <label className="text-slate-400 block mb-1">Tax Regime (India)</label>
              <select
                value={tax}
                onChange={(e) => setTax(e.target.value)}
                className="w-full p-2.5 bg-[#0A0E1A] border border-[#1D263B] rounded-xl text-slate-200"
              >
                <option value="new">New Tax Regime (Lower slab rates, simplified)</option>
                <option value="old">Old Tax Regime (Section 80C, 80D, HRA deductions)</option>
              </select>
            </div>
          </div>
        </div>

        {/* AI Advisory & Risk Preferences */}
        <div className="p-6 rounded-2xl bg-[#0F1626] border border-[#1D263B] space-y-4">
          <div className="flex items-center space-x-2 text-white font-bold text-sm border-b border-[#1D263B] pb-3">
            <Bot className="w-4 h-4 text-purple-400" />
            <span>AI Wealth Advisor Preferences</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="text-slate-400 block mb-1">Default Advisory Persona</label>
              <select
                value={guru}
                onChange={(e) => setGuru(e.target.value)}
                className="w-full p-2.5 bg-[#0A0E1A] border border-[#1D263B] rounded-xl text-slate-200"
              >
                <option value="balanced">Balanced Consensus Advisor</option>
                <option value="buffett">Warren Buffett (Value & Indexing)</option>
                <option value="kiyosaki">Robert Kiyosaki (Cashflow & Real Assets)</option>
                <option value="sethi">Ramit Sethi (Conscious Spending)</option>
                <option value="indian_expert">Indian Wealth Specialist (SIP & Tax)</option>
              </select>
            </div>

            <div>
              <label className="text-slate-400 block mb-1">Investment Risk Tolerance</label>
              <select
                value={risk}
                onChange={(e) => setRisk(e.target.value)}
                className="w-full p-2.5 bg-[#0A0E1A] border border-[#1D263B] rounded-xl text-slate-200"
              >
                <option value="conservative">Conservative (Capital preservation, debt, gold)</option>
                <option value="moderate">Moderate (Balanced equity SIPs & index funds)</option>
                <option value="aggressive">Aggressive (High equity allocation, growth)</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold shadow-md shadow-blue-500/25 transition-all"
          >
            {loading ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </form>

      {/* GDPR Privacy & Right to be Forgotten */}
      <div className="p-6 rounded-2xl bg-[#0F1626] border border-rose-500/20 space-y-4">
        <div className="flex items-center space-x-2 text-rose-400 font-bold text-sm border-b border-[#1D263B] pb-3">
          <ShieldCheck className="w-4 h-4" />
          <span>Data Privacy & GDPR Right to be Forgotten</span>
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 text-xs">
          <div>
            <h4 className="font-bold text-white">Permanently Delete Account & Financial Records</h4>
            <p className="text-slate-400 text-[11px] mt-0.5">
              Purges all transactions, OCR documents, budgets, goals, and vector embeddings from the server.
            </p>
          </div>

          <button
            onClick={async () => {
              if (confirm('Are you sure you want to permanently delete your financial data? This action cannot be reversed.')) {
                await deleteAccount();
              }
            }}
            className="px-4 py-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 font-bold text-xs transition-all whitespace-nowrap"
          >
            Delete Account Data
          </button>
        </div>
      </div>
    </div>
  );
}
