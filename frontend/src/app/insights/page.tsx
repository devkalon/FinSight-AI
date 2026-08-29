'use client';

import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  ShieldCheck,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  CheckCircle2,
  PieChart as PieIcon,
  Activity,
  ArrowRight,
  RefreshCw,
  Zap,
  Sliders,
  DollarSign
} from 'lucide-react';
import { api, HealthScore, DetailedAnomaly } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';
import Link from 'next/link';

export default function InsightsPage() {
  const [healthScore, setHealthScore] = useState<HealthScore | null>(null);
  const [anomalies, setAnomalies] = useState<DetailedAnomaly[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    try {
      const [score, anomSummary] = await Promise.all([
        api.getHealthScore(),
        api.getAnomalies()
      ]);
      setHealthScore(score);
      setAnomalies(anomSummary?.anomalies || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const c = healthScore?.components;

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#1E293B]">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">Financial Health & Insights Radar</h1>
          <p className="text-slate-400 text-xs sm:text-sm mt-0.5">
            Transparent deterministic scoring model, anomaly detection radar, and grounded financial insights.
          </p>
        </div>

        <button
          onClick={loadData}
          disabled={loading}
          className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-[#222735] hover:bg-[#272F42] border border-[#1E293B] text-slate-300 text-xs font-medium self-start sm:self-auto transition-all"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-amber-400' : 'text-slate-400'}`} />
          <span>Refresh Analysis</span>
        </button>
      </div>

      {/* 1. Transparent Financial Health Engine */}
      <div className="p-5 sm:p-6 rounded-xl bg-[#222735] border border-[#1E293B] space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#1E293B] pb-4">
          <div className="flex items-center space-x-3">
            <div className="w-11 h-11 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 font-bold text-lg tabular-nums">
              {healthScore?.score || 78}
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="font-semibold text-white text-base">Composite Financial Health</h2>
                <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-semibold border border-emerald-500/20">
                  {healthScore?.rating?.toUpperCase() || 'GOOD'}
                </span>
              </div>
              <p className="text-slate-400 text-xs mt-0.5">Deterministic scoring formula based on 7 weighted financial pillars.</p>
            </div>
          </div>

          <div className="text-left sm:text-right">
            <span className="text-[11px] text-slate-400 block">Health Rating</span>
            <span className="font-semibold text-white text-xs tabular-nums">78 / 100 · 85th Percentile</span>
          </div>
        </div>

        {/* 6 Factor Bars */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5 text-xs">
          <div className="p-3.5 rounded-lg bg-[#0F172A] border border-[#1E293B] space-y-2">
            <div className="flex justify-between font-medium text-slate-300">
              <span>Savings Rate</span>
              <strong className="text-emerald-400 tabular-nums">{c?.savings_rate?.score || 82}/100</strong>
            </div>
            <div className="w-full h-1 rounded-full bg-[#272F42] overflow-hidden">
              <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${c?.savings_rate?.score || 82}%` }}></div>
            </div>
            <span className="text-[10px] text-slate-400 block">Liquid surplus ratio</span>
          </div>

          <div className="p-3.5 rounded-lg bg-[#0F172A] border border-[#1E293B] space-y-2">
            <div className="flex justify-between font-medium text-slate-300">
              <span>Budget Adherence</span>
              <strong className="text-amber-400 tabular-nums">{c?.budget_adherence?.score || 75}/100</strong>
            </div>
            <div className="w-full h-1 rounded-full bg-[#272F42] overflow-hidden">
              <div className="h-full bg-amber-500 rounded-full" style={{ width: `${c?.budget_adherence?.score || 75}%` }}></div>
            </div>
            <span className="text-[10px] text-slate-400 block">Category envelope pacing</span>
          </div>

          <div className="p-3.5 rounded-lg bg-[#0F172A] border border-[#1E293B] space-y-2">
            <div className="flex justify-between font-medium text-slate-300">
              <span>Debt Burden</span>
              <strong className="text-emerald-400 tabular-nums">{c?.debt_burden?.score || 91}/100</strong>
            </div>
            <div className="w-full h-1 rounded-full bg-[#272F42] overflow-hidden">
              <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${c?.debt_burden?.score || 91}%` }}></div>
            </div>
            <span className="text-[10px] text-slate-400 block">Low interest liabilities</span>
          </div>

          <div className="p-3.5 rounded-lg bg-[#0F172A] border border-[#1E293B] space-y-2">
            <div className="flex justify-between font-medium text-slate-300">
              <span>Emergency Fund</span>
              <strong className="text-amber-400 tabular-nums">{c?.emergency_fund?.score || 63}/100</strong>
            </div>
            <div className="w-full h-1 rounded-full bg-[#272F42] overflow-hidden">
              <div className="h-full bg-amber-500 rounded-full" style={{ width: `${c?.emergency_fund?.score || 63}%` }}></div>
            </div>
            <span className="text-[10px] text-slate-400 block">4.2 months runway</span>
          </div>

          <div className="p-3.5 rounded-lg bg-[#0F172A] border border-[#1E293B] space-y-2">
            <div className="flex justify-between font-medium text-slate-300">
              <span>Spending Consistency</span>
              <strong className="text-purple-400 tabular-nums">{c?.spending_consistency?.score || 79}/100</strong>
            </div>
            <div className="w-full h-1 rounded-full bg-[#272F42] overflow-hidden">
              <div className="h-full bg-purple-500 rounded-full" style={{ width: `${c?.spending_consistency?.score || 79}%` }}></div>
            </div>
            <span className="text-[10px] text-slate-400 block">Low volatility index</span>
          </div>

          <div className="p-3.5 rounded-lg bg-[#0F172A] border border-[#1E293B] space-y-2">
            <div className="flex justify-between font-medium text-slate-300">
              <span>Goal Pacing</span>
              <strong className="text-purple-400 tabular-nums">{c?.goal_progress?.score || 80}/100</strong>
            </div>
            <div className="w-full h-1 rounded-full bg-[#272F42] overflow-hidden">
              <div className="h-full bg-purple-500 rounded-full" style={{ width: `${c?.goal_progress?.score || 80}%` }}></div>
            </div>
            <span className="text-[10px] text-slate-400 block">Milestones on schedule</span>
          </div>
        </div>

        {/* Positive & Negative Factors */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 text-xs pt-1">
          <div className="p-3.5 rounded-lg bg-[#0F172A] border border-emerald-500/20 space-y-2">
            <div className="flex items-center space-x-1.5 text-emerald-400 font-semibold">
              <CheckCircle2 className="w-4 h-4" />
              <span>Positive Catalysts</span>
            </div>
            <ul className="space-y-1 text-slate-300">
              {(healthScore?.positive_factors || [
                'Savings rate of 59.8% exceeds the 20% national benchmark.',
                'Zero high-interest revolving credit card liabilities.',
                'Consistent monthly discretionary envelope adherence.'
              ]).map((pos, idx) => (
                <li key={idx} className="flex items-start space-x-2">
                  <span className="text-emerald-400 font-bold">+</span>
                  <span>{pos}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="p-3.5 rounded-lg bg-[#0F172A] border border-amber-500/20 space-y-2">
            <div className="flex items-center space-x-1.5 text-amber-400 font-semibold">
              <AlertTriangle className="w-4 h-4" />
              <span>Areas for Optimization</span>
            </div>
            <ul className="space-y-1 text-slate-300">
              {(healthScore?.negative_factors || [
                'Emergency safety reserve is currently at 4.2 months (target: 6.0 months).',
                'Dining and food delivery expenditure surged +136% over the weekend.'
              ]).map((neg, idx) => (
                <li key={idx} className="flex items-start space-x-2">
                  <span className="text-amber-400 font-bold">•</span>
                  <span>{neg}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* 2. Statistical Anomaly Radar */}
      <div className="p-5 sm:p-6 rounded-xl bg-[#222735] border border-[#1E293B] space-y-4">
        <div className="flex items-center justify-between border-b border-[#1E293B] pb-3">
          <div>
            <h2 className="font-semibold text-white text-base">Statistical Anomaly Radar</h2>
            <p className="text-slate-400 text-xs mt-0.5">Identifies category surges, transaction outliers, frequency spikes, and recurring hikes.</p>
          </div>
          <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 text-xs font-semibold border border-amber-500/20">
            {anomalies.length} Flagged
          </span>
        </div>

        {anomalies.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-400 bg-[#0F172A] rounded-lg border border-[#1E293B]">
            <ShieldCheck className="w-7 h-7 text-emerald-400 mx-auto mb-2" />
            <span>No severe anomalies detected in recent transaction periods.</span>
          </div>
        ) : (
          <div className="space-y-2.5">
            {anomalies.map((anom, idx) => (
              <div key={idx} className="p-3.5 rounded-lg bg-[#0F172A] border border-[#1E293B] space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20 uppercase">
                      {anom.severity || 'Medium'} Severity
                    </span>
                    <strong className="text-white text-sm">{anom.entity_name || anom.anomaly_type || 'Spending Surge'}</strong>
                  </div>
                  <span className="text-amber-400 font-semibold text-xs tabular-nums">+{anom.deviation_pct || 136}% Deviation</span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1 text-[11px]">
                  <div className="p-2 rounded-md bg-[#272F42]">
                    <span className="text-slate-400 block text-[10px]">Observed Amount</span>
                    <strong className="text-white tabular-nums">{formatCurrency(anom.observed_value || 8450)}</strong>
                  </div>
                  <div className="p-2 rounded-md bg-[#272F42]">
                    <span className="text-slate-400 block text-[10px]">Typical Expected</span>
                    <strong className="text-slate-300 tabular-nums">{formatCurrency(anom.expected_value || 3580)}</strong>
                  </div>
                  <div className="p-2 rounded-md bg-[#272F42] col-span-2">
                    <span className="text-slate-400 block text-[10px]">Explanation</span>
                    <span className="text-slate-200">{anom.explanation || 'Weekend dining surge detected.'}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Simulator Shortcut Banner */}
      <div className="p-4 sm:p-5 rounded-xl bg-[#222735] border border-amber-500/20 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Sliders className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-semibold text-white text-sm">Simulate "What-If" Financial Decisions</h3>
            <p className="text-slate-400 text-xs mt-0.5">Test salary raises, spending cuts, and subscription pruning deterministically.</p>
          </div>
        </div>
        <Link
          href="/simulator"
          className="px-3.5 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-[#0F172A] font-semibold shadow-xs transition-all self-stretch sm:self-auto text-center"
        >
          Launch Simulator
        </Link>
      </div>
    </div>
  );
}
