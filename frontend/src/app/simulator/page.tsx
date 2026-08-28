'use client';

import React, { useState, useEffect } from 'react';
import {
  Sliders,
  Sparkles,
  TrendingUp,
  ArrowRight,
  ShieldCheck,
  Zap,
  Target,
  PiggyBank,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  RefreshCw,
  Award,
  ChevronRight,
  Flame
} from 'lucide-react';
import { api, SimulationResult } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';

export default function WhatIfSimulatorPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SimulationResult | null>(null);

  // Scenario Levers State
  const [incomePct, setIncomePct] = useState<number>(0);
  const [incomeAbs, setIncomeAbs] = useState<number>(0);
  const [foodReduction, setFoodReduction] = useState<number>(0);
  const [shoppingReduction, setShoppingReduction] = useState<number>(0);
  const [discretionaryReduction, setDiscretionaryReduction] = useState<number>(0);
  const [subReduction, setSubReduction] = useState<number>(0);
  const [extraGoalContribution, setExtraGoalContribution] = useState<number>(0);
  const [budgetChange, setBudgetChange] = useState<number>(0);
  const [investmentRoi, setInvestmentRoi] = useState<number>(12);
  const [inflationRate, setInflationRate] = useState<number>(6);

  useEffect(() => {
    runSim();
  }, [
    incomePct,
    incomeAbs,
    foodReduction,
    shoppingReduction,
    discretionaryReduction,
    subReduction,
    extraGoalContribution,
    budgetChange,
    investmentRoi,
    inflationRate
  ]);

  async function runSim() {
    setLoading(true);
    try {
      const res = await api.runSimulation({
        income_change_pct: incomePct,
        monthly_income_change: incomeAbs,
        food_spend_reduction: foodReduction,
        shopping_spend_reduction: shoppingReduction,
        discretionary_spend_reduction: discretionaryReduction,
        removed_subscriptions_amount: subReduction,
        extra_goal_contribution: extraGoalContribution,
        budget_limit_change: budgetChange,
        investment_roi: investmentRoi,
        inflation_rate: inflationRate,
        timeline_months: 24
      });
      setResult(res);
    } catch (err) {
      console.error('Simulation error:', err);
    } finally {
      setLoading(false);
    }
  }

  // Quick Preset Handlers
  function applyPreset(preset: string) {
    if (preset === 'food_2000') {
      setFoodReduction(2000);
      setShoppingReduction(0);
      setSubReduction(0);
      setIncomePct(0);
      setExtraGoalContribution(0);
    } else if (preset === 'income_10pct') {
      setIncomePct(10);
      setFoodReduction(0);
      setShoppingReduction(0);
      setSubReduction(0);
      setExtraGoalContribution(0);
    } else if (preset === 'cancel_subs') {
      setSubReduction(1500);
      setFoodReduction(0);
      setShoppingReduction(0);
      setIncomePct(0);
    } else if (preset === 'turbo_savings') {
      setIncomePct(10);
      setFoodReduction(2000);
      setShoppingReduction(3000);
      setSubReduction(1500);
      setExtraGoalContribution(10000);
    } else if (preset === 'reset') {
      setIncomePct(0);
      setIncomeAbs(0);
      setFoodReduction(0);
      setShoppingReduction(0);
      setDiscretionaryReduction(0);
      setSubReduction(0);
      setExtraGoalContribution(0);
      setBudgetChange(0);
      setInvestmentRoi(12);
      setInflationRate(6);
    }
  }

  const curr = result?.current_scenario;
  const sim = result?.simulated_scenario;
  const netDelta = result?.net_monthly_delta ?? 0;
  const annualDelta = result?.annual_savings_delta ?? 0;
  const healthDelta = result?.health_score_delta ?? 0;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2.5">
            <h1 className="text-2xl font-bold text-white tracking-tight">Deterministic What-If Financial Simulator</h1>
            <span className="px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 font-semibold text-xs border border-blue-500/20">
              Decimal-Safe Model
            </span>
          </div>
          <p className="text-slate-400 text-sm mt-0.5">
            Simulate income hikes, expense cutbacks, subscription pruning, and goal accelerations with mathematical precision
          </p>
        </div>

        <button
          onClick={() => applyPreset('reset')}
          className="flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-[#11192C] hover:bg-[#1E293B] border border-[#1E293B] text-slate-300 hover:text-white text-xs font-semibold transition-all self-start sm:self-auto"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Reset to Baseline</span>
        </button>
      </div>

      {/* Quick Scenario Preset Chips */}
      <div className="p-4 rounded-2xl bg-[#0D1322] border border-[#1E293B] space-y-2">
        <div className="flex items-center space-x-2 text-xs font-semibold text-slate-400">
          <Zap className="w-3.5 h-3.5 text-amber-400" />
          <span>Quick Scenario Experiments:</span>
        </div>
        <div className="flex flex-wrap gap-2 text-xs">
          <button
            onClick={() => applyPreset('food_2000')}
            className={`px-3 py-1.5 rounded-xl border transition-all ${
              foodReduction === 2000 && incomePct === 0 && subReduction === 0
                ? 'bg-blue-600 border-blue-500 text-white shadow-md'
                : 'bg-[#11192C] border-[#1E293B] text-slate-300 hover:text-white'
            }`}
          >
            🍔 Reduce Food Spend by ₹2,000/mo
          </button>

          <button
            onClick={() => applyPreset('income_10pct')}
            className={`px-3 py-1.5 rounded-xl border transition-all ${
              incomePct === 10 && foodReduction === 0
                ? 'bg-blue-600 border-blue-500 text-white shadow-md'
                : 'bg-[#11192C] border-[#1E293B] text-slate-300 hover:text-white'
            }`}
          >
            💼 Increase Income by +10%
          </button>

          <button
            onClick={() => applyPreset('cancel_subs')}
            className={`px-3 py-1.5 rounded-xl border transition-all ${
              subReduction === 1500 && foodReduction === 0
                ? 'bg-blue-600 border-blue-500 text-white shadow-md'
                : 'bg-[#11192C] border-[#1E293B] text-slate-300 hover:text-white'
            }`}
          >
            ✂️ Cancel OTT / Gym (-₹1,500/mo)
          </button>

          <button
            onClick={() => applyPreset('turbo_savings')}
            className={`px-3 py-1.5 rounded-xl border transition-all ${
              incomePct === 10 && foodReduction === 2000 && extraGoalContribution === 10000
                ? 'bg-emerald-600 border-emerald-500 text-white shadow-md'
                : 'bg-[#11192C] border-[#1E293B] text-slate-300 hover:text-white'
            }`}
          >
            🚀 Full Turbo Acceleration (+10% Inc, -₹6.5k Exp, +₹10k Goal)
          </button>
        </div>
      </div>

      {/* Main Grid: Levers on Left, Comparison on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Interactive Levers Control Panel (5 Cols) */}
        <div className="lg:col-span-5 p-6 rounded-2xl bg-[#0D1322] border border-[#1E293B] space-y-6">
          <div className="flex items-center space-x-3 border-b border-[#1E293B] pb-3">
            <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400">
              <Sliders className="w-5 h-5" />
            </div>
            <div>
              <h2 className="font-bold text-white text-sm">Simulation Levers</h2>
              <p className="text-[11px] text-slate-400">Tweak income, expenses, and investment parameters</p>
            </div>
          </div>

          {/* Income Levers */}
          <div className="space-y-4">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Income Levers</h3>
            <div>
              <div className="flex justify-between text-xs text-slate-300 font-semibold mb-1.5">
                <span>Income Growth:</span>
                <span className="text-emerald-400 font-bold">{incomePct >= 0 ? `+${incomePct}%` : `${incomePct}%`}</span>
              </div>
              <input
                type="range"
                min={-20}
                max={50}
                step={5}
                value={incomePct}
                onChange={(e) => setIncomePct(Number(e.target.value))}
                className="w-full h-2 bg-[#1A2338] rounded-lg appearance-none cursor-pointer accent-emerald-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs text-slate-300 font-semibold mb-1.5">
                <span>Additional Monthly Income (₹):</span>
                <span className="text-emerald-400 font-bold">+{formatCurrency(incomeAbs)}/mo</span>
              </div>
              <input
                type="range"
                min={0}
                max={50000}
                step={2500}
                value={incomeAbs}
                onChange={(e) => setIncomeAbs(Number(e.target.value))}
                className="w-full h-2 bg-[#1A2338] rounded-lg appearance-none cursor-pointer accent-emerald-500"
              />
            </div>
          </div>

          {/* Expense Cutback Levers */}
          <div className="space-y-4 pt-4 border-t border-[#1E293B]">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Expense Cutbacks</h3>
            <div>
              <div className="flex justify-between text-xs text-slate-300 font-semibold mb-1.5">
                <span>Reduce Food & Dining Spend:</span>
                <span className="text-blue-400 font-bold">-{formatCurrency(foodReduction)}/mo</span>
              </div>
              <input
                type="range"
                min={0}
                max={8000}
                step={500}
                value={foodReduction}
                onChange={(e) => setFoodReduction(Number(e.target.value))}
                className="w-full h-2 bg-[#1A2338] rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs text-slate-300 font-semibold mb-1.5">
                <span>Reduce Shopping & Wants:</span>
                <span className="text-purple-400 font-bold">-{formatCurrency(shoppingReduction)}/mo</span>
              </div>
              <input
                type="range"
                min={0}
                max={10000}
                step={500}
                value={shoppingReduction}
                onChange={(e) => setShoppingReduction(Number(e.target.value))}
                className="w-full h-2 bg-[#1A2338] rounded-lg appearance-none cursor-pointer accent-purple-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs text-slate-300 font-semibold mb-1.5">
                <span>Cancel Unused Subscriptions:</span>
                <span className="text-rose-400 font-bold">-{formatCurrency(subReduction)}/mo</span>
              </div>
              <input
                type="range"
                min={0}
                max={5000}
                step={250}
                value={subReduction}
                onChange={(e) => setSubReduction(Number(e.target.value))}
                className="w-full h-2 bg-[#1A2338] rounded-lg appearance-none cursor-pointer accent-rose-500"
              />
            </div>
          </div>

          {/* Goal & Compounding Levers */}
          <div className="space-y-4 pt-4 border-t border-[#1E293B]">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Goal & Compounding Levers</h3>
            <div>
              <div className="flex justify-between text-xs text-slate-300 font-semibold mb-1.5">
                <span>Extra Goal Monthly Contribution:</span>
                <span className="text-indigo-400 font-bold">+{formatCurrency(extraGoalContribution)}/mo</span>
              </div>
              <input
                type="range"
                min={0}
                max={30000}
                step={1000}
                value={extraGoalContribution}
                onChange={(e) => setExtraGoalContribution(Number(e.target.value))}
                className="w-full h-2 bg-[#1A2338] rounded-lg appearance-none cursor-pointer accent-indigo-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs text-slate-300 font-semibold mb-1.5">
                <span>Annual Investment ROI:</span>
                <span className="text-amber-400 font-bold">{investmentRoi}% CAGR</span>
              </div>
              <input
                type="range"
                min={6}
                max={18}
                step={0.5}
                value={investmentRoi}
                onChange={(e) => setInvestmentRoi(Number(e.target.value))}
                className="w-full h-2 bg-[#1A2338] rounded-lg appearance-none cursor-pointer accent-amber-500"
              />
            </div>
          </div>
        </div>

        {/* Current Scenario vs Simulated Scenario Side-by-Side (7 Cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Side-by-Side Comparison Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Current Scenario Box */}
            <div className="p-5 rounded-2xl bg-[#0D1322] border border-[#1E293B] space-y-4">
              <div className="flex items-center justify-between border-b border-[#1E293B] pb-3">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Current Baseline</span>
                <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-800 text-slate-300">
                  Actual Ledger
                </span>
              </div>

              <div className="space-y-3 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-400">Monthly Income:</span>
                  <span className="font-bold text-white">{formatCurrency(curr?.monthly_income || 75000)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Monthly Expenses:</span>
                  <span className="font-bold text-white">{formatCurrency(curr?.monthly_expenses || 35000)}</span>
                </div>
                <div className="flex justify-between pt-2 border-t border-[#1E293B]">
                  <span className="text-slate-300 font-semibold">Net Cash Flow Surplus:</span>
                  <span className="font-bold text-blue-400">{formatCurrency(curr?.monthly_net_cash_flow || 40000)}/mo</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Savings Rate:</span>
                  <span className="font-bold text-white">{curr?.savings_rate_pct?.toFixed(1) || 53.3}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">12-Month Annual Savings:</span>
                  <span className="font-bold text-slate-200">{formatCurrency(curr?.annual_savings || 480000)}</span>
                </div>
                <div className="flex justify-between pt-2 border-t border-[#1E293B]">
                  <span className="text-slate-400">Health Score:</span>
                  <span className="font-bold text-emerald-400">{curr?.health_score || 78}/100 ({curr?.health_rating || 'Good'})</span>
                </div>
              </div>
            </div>

            {/* Simulated Scenario Box */}
            <div className="p-5 rounded-2xl bg-[#0D1322] border-2 border-blue-500/50 space-y-4 shadow-xl shadow-blue-500/10">
              <div className="flex items-center justify-between border-b border-blue-500/30 pb-3">
                <span className="text-xs font-bold text-blue-400 uppercase tracking-wider">Simulated Scenario</span>
                <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30">
                  What-If Model
                </span>
              </div>

              <div className="space-y-3 text-xs">
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Monthly Income:</span>
                  <div className="flex items-center space-x-1.5 font-bold text-white">
                    <span>{formatCurrency(sim?.monthly_income || 75000)}</span>
                    {(sim?.monthly_income || 0) > (curr?.monthly_income || 0) && (
                      <span className="text-[10px] text-emerald-400">
                        (+{formatCurrency((sim?.monthly_income || 0) - (curr?.monthly_income || 0))})
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Monthly Expenses:</span>
                  <div className="flex items-center space-x-1.5 font-bold text-white">
                    <span>{formatCurrency(sim?.monthly_expenses || 35000)}</span>
                    {(sim?.monthly_expenses || 0) < (curr?.monthly_expenses || 0) && (
                      <span className="text-[10px] text-blue-400">
                        (-{formatCurrency((curr?.monthly_expenses || 0) - (sim?.monthly_expenses || 0))})
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex justify-between pt-2 border-t border-[#1E293B]">
                  <span className="text-slate-300 font-semibold">Net Cash Flow Surplus:</span>
                  <div className="flex items-center space-x-1.5 font-bold text-emerald-400">
                    <span>{formatCurrency(sim?.monthly_net_cash_flow || 40000)}/mo</span>
                    {netDelta !== 0 && (
                      <span className={`text-[10px] px-1.5 py-0.2 rounded font-extrabold ${netDelta > 0 ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'}`}>
                        {netDelta > 0 ? `+${formatCurrency(netDelta)}` : formatCurrency(netDelta)}
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Savings Rate:</span>
                  <div className="flex items-center space-x-1.5 font-bold text-white">
                    <span>{sim?.savings_rate_pct?.toFixed(1) || 53.3}%</span>
                    {(sim?.savings_rate_pct || 0) > (curr?.savings_rate_pct || 0) && (
                      <span className="text-[10px] text-emerald-400">
                        (+{((sim?.savings_rate_pct || 0) - (curr?.savings_rate_pct || 0)).toFixed(1)}%)
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">12-Month Annual Savings:</span>
                  <div className="flex items-center space-x-1.5 font-bold text-emerald-300">
                    <span>{formatCurrency(sim?.annual_savings || 480000)}</span>
                    {annualDelta > 0 && (
                      <span className="text-[10px] text-emerald-400 font-extrabold">
                        (+{formatCurrency(annualDelta)})
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex justify-between pt-2 border-t border-[#1E293B]">
                  <span className="text-slate-400">Health Score:</span>
                  <div className="flex items-center space-x-1.5 font-bold text-emerald-400">
                    <span>{sim?.health_score || 78}/100 ({sim?.health_rating || 'Good'})</span>
                    {healthDelta > 0 && (
                      <span className="text-[10px] px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300 font-bold">
                        +{healthDelta} pts
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* AI Explanation of Deterministic Output */}
          {result?.ai_explanation && (
            <div className="p-4 rounded-2xl bg-blue-500/10 border border-blue-500/20 space-y-1.5 text-xs text-blue-200">
              <div className="flex items-center space-x-2 font-bold text-blue-400">
                <Sparkles className="w-4 h-4" />
                <span>AI Simulation Synthesis (Deterministic Breakdown)</span>
              </div>
              <p className="leading-relaxed">{result.ai_explanation}</p>
            </div>
          )}

          {/* Goal Completion Acceleration Impact */}
          <div className="p-5 rounded-2xl bg-[#0D1322] border border-[#1E293B] space-y-3.5">
            <div className="flex items-center space-x-2.5 text-xs font-bold text-white">
              <Target className="w-4 h-4 text-indigo-400" />
              <span>Goal Completion Timeline Acceleration Impact</span>
            </div>

            <div className="space-y-2.5">
              {result?.goal_impacts?.map((g, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-[#11192C] border border-[#1E293B] flex items-center justify-between text-xs">
                  <div>
                    <h4 className="font-bold text-white">{g.goal_title}</h4>
                    <span className="text-slate-400 text-[11px]">
                      Target: {formatCurrency(g.target_amount)} • Remaining: {formatCurrency(g.remaining_amount)}
                    </span>
                  </div>

                  <div className="text-right">
                    <div className="flex items-center space-x-1.5 justify-end">
                      <span className="text-slate-400 line-through">{g.baseline_months_to_complete} mo</span>
                      <ArrowRight className="w-3 h-3 text-slate-500" />
                      <span className="font-bold text-white">{g.simulated_months_to_complete} mo</span>
                      {g.months_saved > 0 && (
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400">
                          {g.months_saved} mo faster!
                        </span>
                      )}
                    </div>
                    <span className="text-[10px] text-slate-400">Target Date: {g.accelerated_completion_date}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Guru Critiques on Simulation */}
          <div className="p-5 rounded-2xl bg-[#0D1322] border border-[#1E293B] space-y-3">
            <div className="flex items-center space-x-2 text-xs font-bold text-slate-300">
              <Award className="w-4 h-4 text-amber-400" />
              <span>Philosophy Critiques on This Simulated Scenario</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5 text-xs">
              <div className="p-3 rounded-xl bg-[#11192C] border border-[#1E293B] space-y-1">
                <span className="font-bold text-amber-400 text-[11px]">Warren Buffett</span>
                <p className="text-slate-300 text-[11px] leading-relaxed">{result?.guru_critique?.buffett}</p>
              </div>

              <div className="p-3 rounded-xl bg-[#11192C] border border-[#1E293B] space-y-1">
                <span className="font-bold text-purple-400 text-[11px]">Robert Kiyosaki</span>
                <p className="text-slate-300 text-[11px] leading-relaxed">{result?.guru_critique?.kiyosaki}</p>
              </div>

              <div className="p-3 rounded-xl bg-[#11192C] border border-[#1E293B] space-y-1">
                <span className="font-bold text-blue-400 text-[11px]">Ramit Sethi</span>
                <p className="text-slate-300 text-[11px] leading-relaxed">{result?.guru_critique?.sethi}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
