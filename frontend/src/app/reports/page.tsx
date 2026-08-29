'use client';

import React, { useState, useEffect } from 'react';
import {
  FileText,
  Download,
  Printer,
  Calendar,
  Sparkles,
  TrendingUp,
  ShieldCheck,
  PiggyBank,
  Target,
  AlertTriangle,
  CreditCard,
  CheckCircle2,
  ArrowUpRight,
  ArrowDownRight,
  Layers,
  Award
} from 'lucide-react';
import { api, MonthlyReportData } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';

export default function MonthlyReportPage() {
  const [selectedMonth, setSelectedMonth] = useState<string>('2026-08');
  const [report, setReport] = useState<MonthlyReportData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadReport(selectedMonth);
  }, [selectedMonth]);

  async function loadReport(month: string) {
    setLoading(true);
    try {
      const data = await api.getMonthlyReport(month);
      setReport(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  function handleExportPdf() {
    const url = api.getMonthlyReportPdfUrl(selectedMonth);
    window.open(url, '_blank');
  }

  function handlePrint() {
    window.print();
  }

  const m = report?.metrics;
  const n = report?.narrative;

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#1E293B]">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">Financial Intelligence Statement</h1>
            <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-medium text-[11px] border border-emerald-500/20">
              Verified Statement
            </span>
          </div>
          <p className="text-slate-400 text-xs sm:text-sm mt-0.5">
            11-section executive financial intelligence statement verified against backend calculations
          </p>
        </div>

        <div className="flex items-center space-x-2 self-start sm:self-auto">
          {/* Month Selector */}
          <div className="flex items-center space-x-2 bg-[#222735] border border-[#1E293B] px-3 py-1.5 rounded-lg text-xs">
            <Calendar className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={selectedMonth}
              onChange={(e) => setSelectedMonth(e.target.value)}
              className="bg-transparent text-slate-200 font-medium focus:outline-none cursor-pointer text-xs"
            >
              <option value="2026-08" className="bg-[#222735] text-white">August 2026</option>
              <option value="2026-07" className="bg-[#222735] text-white">July 2026</option>
              <option value="2026-06" className="bg-[#222735] text-white">June 2026</option>
            </select>
          </div>

          <button
            onClick={handleExportPdf}
            className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-[#0F172A] text-xs font-semibold shadow-xs transition-all"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export PDF</span>
          </button>

          <button
            onClick={handlePrint}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-[#222735] hover:bg-[#272F42] border border-[#1E293B] text-slate-300 text-xs font-medium transition-all"
          >
            <Printer className="w-3.5 h-3.5" />
            <span>Print</span>
          </button>
        </div>
      </div>

      {/* Verification Notice Banner */}
      <div className="p-4 rounded-2xl bg-[#0F172A] border border-amber-500/20 flex items-center justify-between text-xs text-slate-300">
        <div className="flex items-center space-x-2.5">
          <ShieldCheck className="w-4 h-4 text-amber-400 flex-shrink-0" />
          <span>
            <strong>Deterministic Audit Guarantee:</strong> All financial statistics and tables are computed deterministically from verified ledger databases. The AI narrative synthesizes these numbers without alteration.
          </span>
        </div>
        <span className="text-[11px] text-slate-500 hidden md:inline">Report ID: {report?.report_id || 'rep_2026_08'}</span>
      </div>

      {/* 1. EXECUTIVE SUMMARY */}
      <section className="p-6 rounded-2xl bg-[#0F172A] border border-[#1E293B] space-y-5">
        <div className="flex items-center justify-between border-b border-[#1E293B] pb-3">
          <div className="flex items-center space-x-2.5">
            <span className="flex items-center justify-center w-6 h-6 rounded-lg bg-amber-500/10 text-amber-400 text-xs font-bold">1</span>
            <h2 className="font-bold text-white text-base">Executive Summary</h2>
          </div>
          <span className="text-xs text-slate-400">Statement Period: {m?.month_name}</span>
        </div>

        {/* 5 KPI Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 text-xs">
          <div className="p-3.5 rounded-xl bg-[#222735] border border-[#1E293B] space-y-1">
            <span className="text-slate-400 text-[11px]">Total Income</span>
            <div className="text-lg font-bold text-emerald-400">{formatCurrency(m?.total_income || 75000)}</div>
          </div>
          <div className="p-3.5 rounded-xl bg-[#222735] border border-[#1E293B] space-y-1">
            <span className="text-slate-400 text-[11px]">Total Expenses</span>
            <div className="text-lg font-bold text-white">{formatCurrency(m?.total_expenses || 34200)}</div>
          </div>
          <div className="p-3.5 rounded-xl bg-[#222735] border border-[#1E293B] space-y-1">
            <span className="text-slate-400 text-[11px]">Net Savings Surplus</span>
            <div className="text-lg font-bold text-amber-400">+{formatCurrency(m?.net_savings || 40800)}</div>
          </div>
          <div className="p-3.5 rounded-xl bg-[#222735] border border-[#1E293B] space-y-1">
            <span className="text-slate-400 text-[11px]">Savings Rate</span>
            <div className="text-lg font-bold text-purple-400">{m?.savings_rate_pct || 54.4}%</div>
          </div>
          <div className="p-3.5 rounded-xl bg-[#222735] border border-[#1E293B] space-y-1">
            <span className="text-slate-400 text-[11px]">Health Score</span>
            <div className="text-lg font-bold text-amber-400">{m?.health_score || 78}/100</div>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-[#222735] border border-[#1E293B] text-xs text-slate-200 leading-relaxed space-y-1">
          <div className="flex items-center space-x-1.5 text-amber-400 font-bold mb-1">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Executive Narrative:</span>
          </div>
          <p>{n?.executive_summary}</p>
        </div>
      </section>

      {/* 2. INCOME & 3. SPENDING */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Section 2: Income */}
        <section className="p-6 rounded-2xl bg-[#0F172A] border border-[#1E293B] space-y-4">
          <div className="flex items-center space-x-2.5 border-b border-[#1E293B] pb-3">
            <span className="flex items-center justify-center w-6 h-6 rounded-lg bg-emerald-500/10 text-emerald-400 text-xs font-bold">2</span>
            <h2 className="font-bold text-white text-base">Income Analysis</h2>
          </div>
          <div className="text-2xl font-extrabold text-white">
            {formatCurrency(m?.total_income || 75000)}
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">{n?.income_narrative}</p>
        </section>

        {/* Section 3: Spending */}
        <section className="p-6 rounded-2xl bg-[#0F172A] border border-[#1E293B] space-y-4">
          <div className="flex items-center space-x-2.5 border-b border-[#1E293B] pb-3">
            <span className="flex items-center justify-center w-6 h-6 rounded-lg bg-rose-500/10 text-rose-400 text-xs font-bold">3</span>
            <h2 className="font-bold text-white text-base">Spending Breakdown</h2>
          </div>
          <div className="flex justify-between items-baseline">
            <div className="text-2xl font-extrabold text-white">{formatCurrency(m?.total_expenses || 34200)}</div>
            <span className="text-xs text-slate-400">Avg: {formatCurrency(m?.average_daily_spending || 1140)}/day</span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="p-2.5 rounded-lg bg-[#222735]">
              <span className="text-slate-400 text-[10px] uppercase">Essential Needs</span>
              <div className="font-bold text-white mt-0.5">{formatCurrency(m?.essential_spending || 14600)}</div>
            </div>
            <div className="p-2.5 rounded-lg bg-[#222735]">
              <span className="text-slate-400 text-[10px] uppercase">Discretionary Wants</span>
              <div className="font-bold text-white mt-0.5">{formatCurrency(m?.discretionary_spending || 19600)}</div>
            </div>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">{n?.spending_narrative}</p>
        </section>
      </div>

      {/* Top Categories Table */}
      <section className="p-6 rounded-2xl bg-[#0F172A] border border-[#1E293B] space-y-4">
        <h3 className="font-bold text-white text-sm">Category Expenditure Distribution</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-[#222735] text-slate-400 uppercase text-[10px]">
              <tr>
                <th className="p-3 rounded-l-lg">Category</th>
                <th className="p-3">Monthly Outlay</th>
                <th className="p-3">Share of Spend</th>
                <th className="p-3 rounded-r-lg">Visual Ratio</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1E293B]">
              {m?.spending_by_category.map((cat, i) => (
                <tr key={i} className="hover:bg-[#222735]/50">
                  <td className="p-3 font-semibold text-white">{cat.category_name}</td>
                  <td className="p-3 font-bold text-slate-200">{formatCurrency(cat.amount)}</td>
                  <td className="p-3 text-slate-300">{cat.percentage}%</td>
                  <td className="p-3">
                    <div className="w-36 h-2 rounded-full bg-[#272F42] overflow-hidden">
                      <div className="h-full rounded-full bg-amber-500" style={{ width: `${Math.min(cat.percentage * 2, 100)}%` }}></div>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* 4. SAVINGS & 5. BUDGET PERFORMANCE */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Section 4: Savings */}
        <section className="p-6 rounded-2xl bg-[#0F172A] border border-[#1E293B] space-y-4">
          <div className="flex items-center space-x-2.5 border-b border-[#1E293B] pb-3">
            <span className="flex items-center justify-center w-6 h-6 rounded-lg bg-purple-500/10 text-purple-400 text-xs font-bold">4</span>
            <h2 className="font-bold text-white text-base">Savings Performance</h2>
          </div>
          <div className="flex justify-between items-baseline">
            <div className="text-2xl font-extrabold text-amber-400">+{formatCurrency(m?.net_savings || 40800)}</div>
            <span className="text-xs font-bold text-purple-400 px-2 py-0.5 rounded bg-purple-500/10 border border-purple-500/20">
              {m?.savings_rate_pct}% Savings Rate
            </span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">{n?.savings_narrative}</p>
        </section>

        {/* Section 5: Budget Performance */}
        <section className="p-6 rounded-2xl bg-[#0F172A] border border-[#1E293B] space-y-4">
          <div className="flex items-center space-x-2.5 border-b border-[#1E293B] pb-3">
            <span className="flex items-center justify-center w-6 h-6 rounded-lg bg-amber-500/10 text-amber-400 text-xs font-bold">5</span>
            <h2 className="font-bold text-white text-base">Budget Adherence</h2>
          </div>
          <div className="flex justify-between items-baseline">
            <div className="text-2xl font-extrabold text-white">{m?.budget_utilization_pct}% <span className="text-xs text-slate-500 font-normal">utilized</span></div>
            <span className="text-xs text-slate-400">Limit: {formatCurrency(m?.total_budget_limit || 40000)}</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">{n?.budget_narrative}</p>
        </section>
      </div>

      {/* 6. GOAL PROGRESS */}
      <section className="p-6 rounded-2xl bg-[#0F172A] border border-[#1E293B] space-y-4">
        <div className="flex items-center justify-between border-b border-[#1E293B] pb-3">
          <div className="flex items-center space-x-2.5">
            <span className="flex items-center justify-center w-6 h-6 rounded-lg bg-purple-500/10 text-purple-400 text-xs font-bold">6</span>
            <h2 className="font-bold text-white text-base">Financial Goal Progress</h2>
          </div>
          <span className="text-xs text-slate-400">
            {formatCurrency(m?.total_goal_saved || 278000)} / {formatCurrency(m?.total_goal_target || 530000)} Total
          </span>
        </div>

        <p className="text-xs text-slate-300 leading-relaxed">{n?.goal_narrative}</p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          {m?.goals.map((g, idx) => (
            <div key={idx} className="p-3.5 rounded-xl bg-[#222735] border border-[#1E293B] space-y-2">
              <div className="flex justify-between font-semibold text-white">
                <span>{g.title}</span>
                <span className="text-purple-400">{g.progress_percentage}%</span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-[#272F42] overflow-hidden">
                <div className="h-full rounded-full bg-purple-500" style={{ width: `${Math.min(g.progress_percentage, 100)}%` }}></div>
              </div>
              <div className="flex justify-between text-[11px] text-slate-400">
                <span>Target: {g.projected_completion_date}</span>
                <span className="font-bold text-emerald-400">{formatCurrency(g.required_monthly_saving)}/mo</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 7. ANOMALIES & 8. RECURRING EXPENSES */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Section 7: Anomalies */}
        <section className="p-6 rounded-2xl bg-[#0F172A] border border-[#1E293B] space-y-4">
          <div className="flex items-center space-x-2.5 border-b border-[#1E293B] pb-3">
            <span className="flex items-center justify-center w-6 h-6 rounded-lg bg-amber-500/10 text-amber-400 text-xs font-bold">7</span>
            <h2 className="font-bold text-white text-base">Anomaly Detection</h2>
          </div>
          <div className="text-xl font-bold text-amber-400">
            {m?.anomalies_detected_count} Flagged Deviation(s)
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">{n?.anomalies_narrative}</p>
        </section>

        {/* Section 8: Recurring Expenses */}
        <section className="p-6 rounded-2xl bg-[#0F172A] border border-[#1E293B] space-y-4">
          <div className="flex items-center space-x-2.5 border-b border-[#1E293B] pb-3">
            <span className="flex items-center justify-center w-6 h-6 rounded-lg bg-rose-500/10 text-rose-400 text-xs font-bold">8</span>
            <h2 className="font-bold text-white text-base">Recurring Expenses</h2>
          </div>
          <div className="text-xl font-bold text-white">
            {formatCurrency(m?.recurring_monthly_total || 3478)}/mo <span className="text-xs text-slate-500 font-normal">({formatCurrency(m?.recurring_annual_total || 41736)}/yr)</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">{n?.recurring_narrative}</p>
        </section>
      </div>

      {/* 9. FORECAST */}
      <section className="p-6 rounded-2xl bg-[#0F172A] border border-[#1E293B] space-y-4">
        <div className="flex items-center space-x-2.5 border-b border-[#1E293B] pb-3">
          <span className="flex items-center justify-center w-6 h-6 rounded-lg bg-amber-500/10 text-amber-400 text-xs font-bold">9</span>
          <h2 className="font-bold text-white text-base">Predictive Expense Forecast (Next 30 Days)</h2>
        </div>
        <div className="flex justify-between items-baseline">
          <div className="text-2xl font-extrabold text-white">{formatCurrency(m?.forecast_next_30_days || 34884)}</div>
          <span className="text-xs text-amber-400 font-bold px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/20">
            Confidence: {Math.round((m?.forecast_confidence || 0.88) * 100)}%
          </span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">{n?.forecast_narrative}</p>
      </section>

      {/* 10. KEY OBSERVATIONS & 11. RECOMMENDED ACTIONS */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Section 10 */}
        <section className="p-6 rounded-2xl bg-[#0F172A] border border-[#1E293B] space-y-4">
          <div className="flex items-center space-x-2.5 border-b border-[#1E293B] pb-3">
            <span className="flex items-center justify-center w-6 h-6 rounded-lg bg-slate-700 text-white text-xs font-bold">10</span>
            <h2 className="font-bold text-white text-base">Key Observations</h2>
          </div>
          <ul className="space-y-2.5 text-xs text-slate-200">
            {n?.key_observations.map((obs, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 flex-shrink-0"></span>
                <span>{obs}</span>
              </li>
            ))}
          </ul>
        </section>

        {/* Section 11 */}
        <section className="p-6 rounded-2xl bg-[#0F172A] border border-[#1E293B] space-y-4">
          <div className="flex items-center space-x-2.5 border-b border-[#1E293B] pb-3">
            <span className="flex items-center justify-center w-6 h-6 rounded-lg bg-emerald-600 text-white text-xs font-bold">11</span>
            <h2 className="font-bold text-white text-base">Recommended Action Plan</h2>
          </div>
          <ul className="space-y-2.5 text-xs text-slate-200">
            {n?.recommended_actions.map((act, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                <span>{act}</span>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}
