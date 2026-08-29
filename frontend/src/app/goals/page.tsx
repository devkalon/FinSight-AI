'use client';

import React, { useState, useEffect } from 'react';
import { Target, TrendingUp, Plus, Sparkles, CheckCircle2, Calculator, ArrowRight, X, Trash2, DollarSign, Calendar } from 'lucide-react';
import { api, Goal } from '@/lib/api';
import { formatCurrency, formatDate } from '@/lib/utils';

const PRESET_CATEGORIES = [
  { name: 'Emergency Fund', defaultTitle: 'Emergency Safety Reserve', defaultAmount: 300000 },
  { name: 'Laptop Purchase', defaultTitle: 'MacBook Pro M-Series', defaultAmount: 80000 },
  { name: 'Travel', defaultTitle: 'Global Vacation Fund', defaultAmount: 150000 },
  { name: 'Education', defaultTitle: 'Executive Leadership Certification', defaultAmount: 120000 },
  { name: 'Home Down Payment', defaultTitle: 'Apartment Down Payment', defaultAmount: 1000000 },
  { name: 'Custom Goal', defaultTitle: 'New Financial Milestone', defaultAmount: 50000 }
];

export default function GoalsPage() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);

  // SIP Calculator State
  const [sipMonthly, setSipMonthly] = useState(15000);
  const [sipRate, setSipRate] = useState(12);
  const [sipYears, setSipYears] = useState(10);

  // New Goal Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [goalForm, setGoalForm] = useState({
    title: 'MacBook Pro M-Series',
    category: 'Laptop Purchase',
    target_amount: '80000',
    current_amount: '23000',
    target_date: '2026-12-31',
    monthly_contribution: '14250'
  });

  // Contribute Modal State
  const [contributeModal, setContributeModal] = useState<{ isOpen: boolean; goalId: string; goalTitle: string; amount: string }>({
    isOpen: false,
    goalId: '',
    goalTitle: '',
    amount: '5000'
  });

  useEffect(() => {
    loadGoals();
  }, []);

  async function loadGoals() {
    try {
      const data = await api.getGoals();
      setGoals(data);
    } finally {
      setLoading(false);
    }
  }

  // Calculate live compound SIP metrics
  const i = (sipRate / 100) / 12;
  const n = sipYears * 12;
  const totalInvested = sipMonthly * n;
  const futureValue = sipMonthly * (((Math.pow(1 + i, n) - 1) / i)) * (1 + i);
  const wealthGain = futureValue - totalInvested;

  // Real-time preview calculations for the new goal modal
  const formTarget = parseFloat(goalForm.target_amount) || 0;
  const formCurrent = parseFloat(goalForm.current_amount) || 0;
  const formRemaining = Math.max(formTarget - formCurrent, 0);
  const formTargetDate = new Date(goalForm.target_date || '2026-12-31');
  const now = new Date();
  const formMonthsRemaining = Math.max(
    (formTargetDate.getFullYear() - now.getFullYear()) * 12 + (formTargetDate.getMonth() - now.getMonth()),
    1
  );
  const formRequiredMonthly = formRemaining > 0 ? Math.round(formRemaining / formMonthsRemaining) : 0;

  function handleSelectPreset(preset: typeof PRESET_CATEGORIES[0]) {
    setGoalForm((prev) => ({
      ...prev,
      category: preset.name,
      title: preset.defaultTitle,
      target_amount: String(preset.defaultAmount),
      monthly_contribution: String(Math.round(preset.defaultAmount / 6))
    }));
  }

  async function handleCreateGoal(e: React.FormEvent) {
    e.preventDefault();
    try {
      const created = await api.createGoal({
        title: goalForm.title,
        category: goalForm.category,
        target_amount: parseFloat(goalForm.target_amount) || 80000,
        current_amount: parseFloat(goalForm.current_amount) || 0,
        target_date: goalForm.target_date,
        monthly_contribution: parseFloat(goalForm.monthly_contribution) || formRequiredMonthly
      });
      setGoals((prev) => [...prev, created]);
      setIsModalOpen(false);
      setGoalForm({
        title: 'MacBook Pro M-Series',
        category: 'Laptop Purchase',
        target_amount: '80000',
        current_amount: '23000',
        target_date: '2026-12-31',
        monthly_contribution: '14250'
      });
    } catch (err) {
      console.error(err);
    }
  }

  async function handleContributeSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      const updated = await api.contributeGoal(contributeModal.goalId, parseFloat(contributeModal.amount) || 1000);
      setGoals((prev) => prev.map((g) => (g.id === updated.id ? updated : g)));
      setContributeModal({ isOpen: false, goalId: '', goalTitle: '', amount: '5000' });
    } catch (err) {
      console.error(err);
    }
  }

  async function handleDeleteGoal(id: string) {
    try {
      await api.deleteGoal(id);
      setGoals((prev) => prev.filter((g) => g.id !== id));
    } catch (err) {
      console.error(err);
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#1E293B]">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">Financial Goals & SIP Compounding</h1>
          <p className="text-slate-400 text-xs sm:text-sm mt-0.5">
            Deterministic milestone trackers, dynamic required monthly savings & wealth compounding simulator
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center space-x-2 px-3.5 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-[#0F172A] text-xs font-semibold shadow-xs transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>Create New Goal</span>
        </button>
      </div>

      {/* Goals Progress Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {goals.map((g) => {
          const reqMonthly = g.required_monthly_saving || g.required_monthly_sip || 0;
          const isCompleted = g.current_amount >= g.target_amount || g.status === 'achieved';

          return (
            <div key={g.id} className="p-4 sm:p-5 rounded-xl bg-[#222735] border border-[#1E293B] flex flex-col justify-between space-y-4 hover:border-[#334155] transition-all">
              <div>
                <div className="flex items-center justify-between mb-2.5">
                  <span className="text-[10px] px-2 py-0.5 rounded font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
                    {g.category}
                  </span>
                  <div className="flex items-center space-x-1 text-slate-400 text-[11px]">
                    <Calendar className="w-3 h-3" />
                    <span>{formatDate(g.target_date)}</span>
                  </div>
                </div>

                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-white text-sm mb-1">{g.title}</h3>
                    <div className="text-xl font-bold text-slate-100 tabular-nums">
                      {formatCurrency(g.current_amount)} <span className="text-slate-500 text-xs font-normal">/ {formatCurrency(g.target_amount)}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteGoal(g.id)}
                    className="p-1 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-[#272F42] transition-colors"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {/* Progress Bar & Dynamic Completion Metric */}
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-xs text-slate-400 mb-1.5">
                    <span>Progress</span>
                    <span className="text-slate-200 font-semibold tabular-nums">{g.progress_percentage.toFixed(1)}%</span>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-[#272F42] overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        isCompleted
                          ? 'bg-emerald-500'
                          : 'bg-amber-500'
                      }`}
                      style={{ width: `${Math.min(g.progress_percentage, 100)}%` }}
                    ></div>
                  </div>
                </div>

                {/* Deterministic Dynamic Metrics Grid */}
                <div className="grid grid-cols-2 gap-2 pt-2 border-t border-[#1E293B] text-xs">
                  <div className="p-2 rounded-lg bg-[#0F172A] border border-[#1E293B]">
                    <span className="text-[10px] text-slate-400 uppercase">Required Monthly</span>
                    <div className="font-semibold text-emerald-400 mt-0.5 tabular-nums">
                      {isCompleted ? 'Target Achieved' : `${formatCurrency(reqMonthly)}/mo`}
                    </div>
                  </div>
                  <div className="p-2 rounded-lg bg-[#0F172A] border border-[#1E293B]">
                    <span className="text-[10px] text-slate-400 uppercase">Projected Completion</span>
                    <div className="font-semibold text-white mt-0.5">
                      {g.projected_completion_date || formatDate(g.target_date)}
                    </div>
                  </div>
                </div>

                {/* AI Contextual Recommendation */}
                {g.ai_recommendation && (
                  <div className="p-2.5 rounded-lg bg-[#0F172A] border border-[#1E293B] flex items-start space-x-2 text-xs text-slate-300">
                    <Sparkles className="w-3 h-3 text-amber-400 mt-0.5 flex-shrink-0" />
                    <p className="leading-relaxed">{g.ai_recommendation}</p>
                  </div>
                )}

                {/* Deposit / Contribute Action Button */}
                {!isCompleted && (
                  <button
                    onClick={() => setContributeModal({ isOpen: true, goalId: g.id, goalTitle: g.title, amount: '5000' })}
                    className="w-full py-2 rounded-lg bg-[#0F172A] hover:bg-[#272F42] border border-[#1E293B] text-xs font-semibold text-slate-200 transition-colors flex items-center justify-center space-x-1.5"
                  >
                    <Plus className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Contribute Savings</span>
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Interactive SIP Compound Interest Calculator Card */}
      <div className="p-5 sm:p-6 rounded-xl bg-[#222735] border border-[#1E293B] space-y-5">
        <div className="flex items-center justify-between border-b border-[#1E293B] pb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Calculator className="w-4 h-4" />
            </div>
            <div>
              <h2 className="font-semibold text-white text-sm sm:text-base">Interactive SIP Wealth Compounding Simulator</h2>
              <p className="text-xs text-slate-400">Explore how systematic equity investing harnesses mathematical compound interest</p>
            </div>
          </div>
          <span className="text-[11px] text-emerald-400 font-medium px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
            12% CAGR Model
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-center">
          {/* Sliders */}
          <div className="lg:col-span-2 space-y-4">
            <div>
              <div className="flex justify-between text-xs text-slate-300 font-medium mb-1.5">
                <span>Monthly Investment:</span>
                <span className="text-amber-400 font-semibold tabular-nums">{formatCurrency(sipMonthly)}/mo</span>
              </div>
              <input
                type="range"
                min={1000}
                max={100000}
                step={1000}
                value={sipMonthly}
                onChange={(e) => setSipMonthly(Number(e.target.value))}
                className="w-full h-1.5 bg-[#272F42] rounded-lg appearance-none cursor-pointer accent-amber-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs text-slate-300 font-medium mb-1.5">
                <span>Expected Annual Return (ROI):</span>
                <span className="text-emerald-400 font-semibold tabular-nums">{sipRate}% CAGR</span>
              </div>
              <input
                type="range"
                min={6}
                max={18}
                step={0.5}
                value={sipRate}
                onChange={(e) => setSipRate(Number(e.target.value))}
                className="w-full h-1.5 bg-[#272F42] rounded-lg appearance-none cursor-pointer accent-emerald-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs text-slate-300 font-medium mb-1.5">
                <span>Investment Horizon:</span>
                <span className="text-purple-400 font-semibold tabular-nums">{sipYears} Years</span>
              </div>
              <input
                type="range"
                min={1}
                max={30}
                value={sipYears}
                onChange={(e) => setSipYears(Number(e.target.value))}
                className="w-full h-1.5 bg-[#272F42] rounded-lg appearance-none cursor-pointer accent-purple-500"
              />
            </div>
          </div>

          {/* Results Box */}
          <div className="p-4 rounded-xl bg-[#0F172A] border border-[#1E293B] space-y-3">
            <div>
              <span className="text-[11px] text-slate-400">Total Capital Invested</span>
              <div className="text-base font-bold text-slate-200 mt-0.5 tabular-nums">{formatCurrency(totalInvested)}</div>
            </div>

            <div>
              <span className="text-[11px] text-slate-400">Estimated Wealth Gain</span>
              <div className="text-base font-bold text-emerald-400 mt-0.5 tabular-nums">+{formatCurrency(wealthGain)}</div>
            </div>

            <div className="pt-2.5 border-t border-[#1E293B]">
              <span className="text-[11px] text-slate-400">Projected Maturity Corpus</span>
              <div className="text-xl font-bold text-white mt-0.5 tabular-nums">{formatCurrency(futureValue)}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Goal Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0F172A] border border-[#1E293B] rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-white text-base">Create Financial Goal</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Quick Preset Chips */}
            <div className="space-y-1.5">
              <span className="text-[11px] text-slate-400">Quick Presets:</span>
              <div className="flex flex-wrap gap-1.5">
                {PRESET_CATEGORIES.map((cat, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSelectPreset(cat)}
                    className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition-all ${
                      goalForm.category === cat.name
                        ? 'bg-amber-500 text-[#0F172A]'
                        : 'bg-[#222735] text-slate-300 hover:text-white border border-[#1E293B]'
                    }`}
                  >
                    {cat.name}
                  </button>
                ))}
              </div>
            </div>

            <form onSubmit={handleCreateGoal} className="space-y-3.5 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">Goal Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. MacBook Pro M-Series"
                  value={goalForm.title}
                  onChange={(e) => setGoalForm({ ...goalForm, title: e.target.value })}
                  className="w-full p-2.5 bg-[#222735] border border-[#1E293B] rounded-xl text-slate-200"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1">Target Amount (₹)</label>
                  <input
                    type="number"
                    required
                    placeholder="80000"
                    value={goalForm.target_amount}
                    onChange={(e) => setGoalForm({ ...goalForm, target_amount: e.target.value })}
                    className="w-full p-2.5 bg-[#222735] border border-[#1E293B] rounded-xl text-slate-200"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Current Savings (₹)</label>
                  <input
                    type="number"
                    placeholder="23000"
                    value={goalForm.current_amount}
                    onChange={(e) => setGoalForm({ ...goalForm, current_amount: e.target.value })}
                    className="w-full p-2.5 bg-[#222735] border border-[#1E293B] rounded-xl text-slate-200"
                  />
                </div>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Target Date</label>
                <input
                  type="date"
                  value={goalForm.target_date}
                  onChange={(e) => setGoalForm({ ...goalForm, target_date: e.target.value })}
                  className="w-full p-2.5 bg-[#222735] border border-[#1E293B] rounded-xl text-slate-200"
                />
              </div>

              {/* Dynamic Required Monthly Saving Preview Box */}
              <div className="p-3.5 rounded-xl bg-[#222735] border border-[#1E293B] space-y-1">
                <div className="flex justify-between text-slate-400 text-[11px]">
                  <span>Remaining Corpus:</span>
                  <strong className="text-white">{formatCurrency(formRemaining)}</strong>
                </div>
                <div className="flex justify-between text-slate-400 text-[11px]">
                  <span>Timeline:</span>
                  <strong className="text-white">{formMonthsRemaining} Months</strong>
                </div>
                <div className="flex justify-between text-emerald-400 font-bold pt-1 border-t border-[#1E293B] text-xs">
                  <span>Dynamically Calculated Monthly Saving:</span>
                  <span>{formatCurrency(formRequiredMonthly)}/mo</span>
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-[#0F172A] font-semibold shadow-lg shadow-amber-500/25 transition-all"
              >
                Start Tracking Goal
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Quick Contribute Modal */}
      {contributeModal.isOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0F172A] border border-[#1E293B] rounded-2xl max-w-sm w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-white text-base">Contribute to {contributeModal.goalTitle}</h3>
              <button onClick={() => setContributeModal({ isOpen: false, goalId: '', goalTitle: '', amount: '5000' })} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleContributeSubmit} className="space-y-4 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">Contribution Amount (₹)</label>
                <input
                  type="number"
                  required
                  value={contributeModal.amount}
                  onChange={(e) => setContributeModal({ ...contributeModal, amount: e.target.value })}
                  className="w-full p-2.5 bg-[#222735] border border-[#1E293B] rounded-xl text-slate-200"
                />
              </div>

              <button
                type="submit"
                className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold transition-all"
              >
                Deposit to Goal
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
