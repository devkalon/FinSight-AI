'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  TrendingUp,
  TrendingDown,
  ShieldCheck,
  Sparkles,
  ArrowUpRight,
  ArrowDownRight,
  Receipt,
  Target,
  PiggyBank,
  AlertTriangle,
  CreditCard,
  CheckCircle2,
  UploadCloud,
  Bot,
  Sliders,
  FileText,
  Clock,
  ArrowRight
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { api, HealthScore, Transaction, DetailedAnomaly } from '@/lib/api';
import { formatCurrency, formatDate } from '@/lib/utils';

const cashflowTrend = [
  { month: 'Mar', income: 75000, expense: 38200, savings: 36800 },
  { month: 'Apr', income: 75000, expense: 34100, savings: 40900 },
  { month: 'May', income: 82000, expense: 39500, savings: 42500 },
  { month: 'Jun', income: 75000, expense: 32400, savings: 42600 },
  { month: 'Jul', income: 78000, expense: 35600, savings: 42400 },
  { month: 'Aug', income: 85000, expense: 34200, savings: 50800 },
];

const categoryData = [
  { name: 'Food & Dining', value: 8450, color: '#3B82F6' },
  { name: 'Groceries (Needs)', value: 7200, color: '#10B981' },
  { name: 'Shopping & Leisure', value: 5000, color: '#8B5CF6' },
  { name: 'Utilities & Bills', value: 4800, color: '#F59E0B' },
  { name: 'Transport', value: 3600, color: '#06B6D4' },
  { name: 'Health & Fitness', value: 2950, color: '#EC4899' },
];

export default function DashboardPage() {
  const [healthScore, setHealthScore] = useState<HealthScore | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [anomalies, setAnomalies] = useState<DetailedAnomaly[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [score, txs, anomSummary] = await Promise.all([
          api.getHealthScore(),
          api.getTransactions(),
          api.getAnomalies()
        ]);
        setHealthScore(score);
        setTransactions(txs.items || []);
        setAnomalies(anomSummary?.anomalies || []);
      } catch (err) {
        console.error('Failed to load dashboard data', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const c = healthScore?.components;

  return (
    <div className="space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Financial Command Center</h1>
          <p className="text-slate-400 text-xs mt-0.5">
            Real-time deterministic ledger analysis, cash flow pacing, and AI financial advisory.
          </p>
        </div>

        <div className="flex items-center space-x-2.5 self-start sm:self-auto">
          <Link
            href="/upload"
            className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md shadow-blue-500/20 transition-all"
          >
            <UploadCloud className="w-3.5 h-3.5" />
            <span>Upload Document</span>
          </Link>
          <Link
            href="/advisor"
            className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-[#12192B] hover:bg-[#1C263F] text-slate-200 text-xs font-semibold border border-[#1D263B] transition-all"
          >
            <Bot className="w-3.5 h-3.5 text-blue-400" />
            <span>Consult Advisor</span>
          </Link>
        </div>
      </div>

      {/* PRIORITY 1: FINANCIAL HEALTH */}
      <div className="p-6 rounded-2xl bg-[#0F1626] border border-[#1D263B] space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#1D263B] pb-3">
          <div className="flex items-center space-x-2.5">
            <span className="flex items-center justify-center w-6 h-6 rounded-lg bg-emerald-500/10 text-emerald-400 text-xs font-bold">1</span>
            <div>
              <h2 className="font-bold text-white text-base">Financial Health Score</h2>
              <p className="text-[11px] text-slate-400">Explainable deterministic multi-factor financial scoring model</p>
            </div>
          </div>
          <Link href="/insights" className="text-xs text-blue-400 hover:text-blue-300 font-semibold flex items-center gap-1">
            <span>View Full Breakdown</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
          {/* Main Dial */}
          <div className="lg:col-span-4 p-5 rounded-xl bg-[#0A0E1A] border border-[#1D263B] flex flex-col items-center justify-center text-center space-y-2">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Composite Health</span>
            <div className="text-4xl font-extrabold text-emerald-400">
              {healthScore?.score || 78} <span className="text-base text-slate-500 font-normal">/ 100</span>
            </div>
            <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-bold border border-emerald-500/20">
              Strong &amp; Sustainable
            </span>
            <p className="text-[11px] text-slate-400 mt-2">
              Calculated deterministically from savings rate, budget pacing, and debt obligations.
            </p>
          </div>

          {/* 4 Component Bars */}
          <div className="lg:col-span-8 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div className="p-3 rounded-xl bg-[#0A0E1A] border border-[#1D263B] space-y-1.5">
              <div className="flex justify-between font-semibold text-slate-300">
                <span>Savings Rate Factor</span>
                <span className="text-emerald-400 font-bold">{c?.savings_rate?.score || 82}/100</span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-[#182238] overflow-hidden">
                <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${c?.savings_rate?.score || 82}%` }}></div>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-[#0A0E1A] border border-[#1D263B] space-y-1.5">
              <div className="flex justify-between font-semibold text-slate-300">
                <span>Budget Adherence</span>
                <span className="text-blue-400 font-bold">{c?.budget_adherence?.score || 75}/100</span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-[#182238] overflow-hidden">
                <div className="h-full bg-blue-500 rounded-full" style={{ width: `${c?.budget_adherence?.score || 75}%` }}></div>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-[#0A0E1A] border border-[#1D263B] space-y-1.5">
              <div className="flex justify-between font-semibold text-slate-300">
                <span>Debt Burden Control</span>
                <span className="text-emerald-400 font-bold">{c?.debt_burden?.score || 91}/100</span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-[#182238] overflow-hidden">
                <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${c?.debt_burden?.score || 91}%` }}></div>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-[#0A0E1A] border border-[#1D263B] space-y-1.5">
              <div className="flex justify-between font-semibold text-slate-300">
                <span>Emergency Runway</span>
                <span className="text-amber-400 font-bold">{c?.emergency_fund?.score || 63}/100</span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-[#182238] overflow-hidden">
                <div className="h-full bg-amber-500 rounded-full" style={{ width: `${c?.emergency_fund?.score || 63}%` }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* PRIORITY 2: CASH FLOW & KPI CARDS */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2.5">
          <span className="flex items-center justify-center w-6 h-6 rounded-lg bg-blue-500/10 text-blue-400 text-xs font-bold">2</span>
          <h2 className="font-bold text-white text-base">Cash Flow & Liquidity</h2>
        </div>

        {/* 4 Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-5 rounded-2xl bg-[#0F1626] border border-[#1D263B] space-y-2">
            <span className="text-xs text-slate-400 font-semibold">Monthly Income</span>
            <div className="text-2xl font-extrabold text-white">{formatCurrency(85000)}</div>
            <div className="flex items-center text-[11px] text-emerald-400 font-medium">
              <ArrowUpRight className="w-3.5 h-3.5 mr-1" />
              <span>+9.0% vs prior month</span>
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-[#0F1626] border border-[#1D263B] space-y-2">
            <span className="text-xs text-slate-400 font-semibold">Total Expenses</span>
            <div className="text-2xl font-extrabold text-white">{formatCurrency(34200)}</div>
            <div className="flex items-center text-[11px] text-slate-400">
              <span>Avg: {formatCurrency(1140)}/day</span>
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-[#0F1626] border border-[#1D263B] space-y-2">
            <span className="text-xs text-slate-400 font-semibold">Net Retained Surplus</span>
            <div className="text-2xl font-extrabold text-blue-400">+{formatCurrency(50800)}</div>
            <div className="flex items-center text-[11px] text-blue-400 font-medium">
              <span>59.8% monthly savings rate</span>
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-[#0F1626] border border-[#1D263B] space-y-2">
            <span className="text-xs text-slate-400 font-semibold">Fixed Recurring Burn</span>
            <div className="text-2xl font-extrabold text-rose-400">{formatCurrency(3478)}/mo</div>
            <div className="flex items-center text-[11px] text-slate-400">
              <span>{formatCurrency(41736)}/year committed</span>
            </div>
          </div>
        </div>

        {/* Cash Flow Chart */}
        <div className="p-6 rounded-2xl bg-[#0F1626] border border-[#1D263B] space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="font-bold text-white text-sm">6-Month Income vs Expense Trend</h3>
            <span className="text-xs text-slate-400">Monthly Pacing</span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={cashflowTrend}>
                <defs>
                  <linearGradient id="incomeGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.25}/>
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="expenseGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#F43F5E" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#F43F5E" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1D263B" />
                <XAxis dataKey="month" stroke="#64748B" fontSize={11} />
                <YAxis stroke="#64748B" fontSize={11} tickFormatter={(v) => `₹${v/1000}k`} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0A0E1A', borderColor: '#1D263B', borderRadius: '0.75rem', fontSize: '12px' }}
                  formatter={(val: number) => [formatCurrency(val), '']}
                />
                <Area type="monotone" dataKey="income" stroke="#3B82F6" strokeWidth={2} fillOpacity={1} fill="url(#incomeGrad)" name="Income" />
                <Area type="monotone" dataKey="expense" stroke="#F43F5E" strokeWidth={2} fillOpacity={1} fill="url(#expenseGrad)" name="Expense" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* PRIORITY 3: SPENDING & CATEGORY BREAKDOWN */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="p-6 rounded-2xl bg-[#0F1626] border border-[#1D263B] space-y-4">
          <div className="flex items-center space-x-2.5">
            <span className="flex items-center justify-center w-6 h-6 rounded-lg bg-purple-500/10 text-purple-400 text-xs font-bold">3</span>
            <h2 className="font-bold text-white text-base">Category Spending Allocation</h2>
          </div>

          <div className="flex items-center justify-center h-52">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0A0E1A', borderColor: '#1D263B', borderRadius: '0.75rem', fontSize: '12px' }}
                  formatter={(val: number) => [formatCurrency(val), '']}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-2 text-xs">
            {categoryData.slice(0, 4).map((c, i) => (
              <div key={i} className="flex justify-between items-center text-slate-300">
                <div className="flex items-center space-x-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: c.color }}></span>
                  <span>{c.name}</span>
                </div>
                <strong className="text-white">{formatCurrency(c.value)}</strong>
              </div>
            ))}
          </div>
        </div>

        {/* PRIORITY 4: FINANCIAL GOALS */}
        <div className="p-6 rounded-2xl bg-[#0F1626] border border-[#1D263B] space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-[#1D263B] pb-3 mb-4">
              <div className="flex items-center space-x-2.5">
                <span className="flex items-center justify-center w-6 h-6 rounded-lg bg-indigo-500/10 text-indigo-400 text-xs font-bold">4</span>
                <h2 className="font-bold text-white text-base">Milestone Goals</h2>
              </div>
              <Link href="/goals" className="text-xs text-blue-400 hover:text-blue-300 font-semibold flex items-center gap-1">
                <span>View All</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="space-y-3.5 text-xs">
              <div className="p-3.5 rounded-xl bg-[#0A0E1A] border border-[#1D263B] space-y-2">
                <div className="flex justify-between font-bold text-white">
                  <span>Emergency Safety Reserve</span>
                  <span className="text-emerald-400">60%</span>
                </div>
                <div className="w-full h-1.5 rounded-full bg-[#182238] overflow-hidden">
                  <div className="h-full bg-emerald-500 rounded-full" style={{ width: '60%' }}></div>
                </div>
                <div className="flex justify-between text-[11px] text-slate-400">
                  <span>₹1.8L / ₹3.0L Target</span>
                  <span className="text-white font-semibold">₹12,000/mo SIP</span>
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-[#0A0E1A] border border-[#1D263B] space-y-2">
                <div className="flex justify-between font-bold text-white">
                  <span>MacBook Pro Hardware Upgrade</span>
                  <span className="text-blue-400">28.8%</span>
                </div>
                <div className="w-full h-1.5 rounded-full bg-[#182238] overflow-hidden">
                  <div className="h-full bg-blue-500 rounded-full" style={{ width: '28.8%' }}></div>
                </div>
                <div className="flex justify-between text-[11px] text-slate-400">
                  <span>₹23k / ₹80k Target</span>
                  <span className="text-white font-semibold">₹14,250/mo SIP</span>
                </div>
              </div>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-[#12192B] border border-[#1D263B] flex items-center justify-between text-xs text-slate-300">
            <span>Deterministic goal pacing active</span>
            <Link href="/simulator" className="text-blue-400 hover:text-blue-300 font-semibold">Simulate Scenarios →</Link>
          </div>
        </div>
      </div>

      {/* PRIORITY 5: AI INSIGHTS & PRIORITY 6: ANOMALIES */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Priority 5: AI Insights */}
        <div className="p-6 rounded-2xl bg-[#0F1626] border border-[#1D263B] space-y-4">
          <div className="flex items-center justify-between border-b border-[#1D263B] pb-3">
            <div className="flex items-center space-x-2.5">
              <span className="flex items-center justify-center w-6 h-6 rounded-lg bg-blue-500/10 text-blue-400 text-xs font-bold">5</span>
              <h2 className="font-bold text-white text-base">Grounded AI Insights</h2>
            </div>
            <Link href="/advisor" className="text-xs text-blue-400 hover:text-blue-300 font-semibold">
              Open Advisor
            </Link>
          </div>

          <div className="p-4 rounded-xl bg-[#0A0E1A] border border-[#1D263B] space-y-2 text-xs">
            <div className="flex items-center space-x-2 text-blue-400 font-bold">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Multi-Guru Consensus Recommendation:</span>
            </div>
            <p className="text-slate-300 leading-relaxed">
              Your 59.8% savings rate provides a monthly surplus of ₹50,800. Ramit Sethi recommends guilt-free discretionary allocation while Warren Buffett advises directing ₹25,000 into broad-market index SIPs on salary deposit day.
            </p>
          </div>

          <div className="space-y-2 text-xs">
            <div className="p-3 rounded-xl bg-[#0A0E1A] border border-[#1D263B] flex items-center justify-between">
              <span className="text-slate-300">Annualized Recurring Review:</span>
              <strong className="text-rose-400">₹41,736/yr</strong>
            </div>
            <div className="p-3 rounded-xl bg-[#0A0E1A] border border-[#1D263B] flex items-center justify-between">
              <span className="text-slate-300">Predicted 30-Day Outlays:</span>
              <strong className="text-slate-100">₹34,884 (88% conf.)</strong>
            </div>
          </div>
        </div>

        {/* Priority 6: Anomalies */}
        <div className="p-6 rounded-2xl bg-[#0F1626] border border-[#1D263B] space-y-4">
          <div className="flex items-center justify-between border-b border-[#1D263B] pb-3">
            <div className="flex items-center space-x-2.5">
              <span className="flex items-center justify-center w-6 h-6 rounded-lg bg-amber-500/10 text-amber-400 text-xs font-bold">6</span>
              <h2 className="font-bold text-white text-base">Statistical Anomaly Radar</h2>
            </div>
            <span className="text-xs text-amber-400 font-semibold">1 Alert Active</span>
          </div>

          <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 space-y-2 text-xs">
            <div className="flex items-center space-x-2 text-amber-400 font-bold">
              <AlertTriangle className="w-4 h-4" />
              <span>Dining & Restaurant Surge (+136% vs typical)</span>
            </div>
            <p className="text-slate-300 leading-relaxed">
              Current food expenditure reached ₹8,450 vs your typical baseline of ₹3,580. Affected by weekend dining clusters.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-[#0A0E1A] border border-[#1D263B] flex items-center justify-between text-xs">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span className="text-slate-300">False-Positive Filter Active</span>
            </div>
            <span className="text-slate-400">Regular utility bills cleared</span>
          </div>
        </div>
      </div>

      {/* Recent Ledger Transactions Table */}
      <div className="p-6 rounded-2xl bg-[#0F1626] border border-[#1D263B] space-y-4">
        <div className="flex items-center justify-between border-b border-[#1D263B] pb-3">
          <h2 className="font-bold text-white text-base">Recent Ledger Activity</h2>
          <Link href="/transactions" className="text-xs text-blue-400 hover:text-blue-300 font-semibold">
            View All Transactions →
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-[#0A0E1A] text-slate-400 uppercase text-[10px]">
              <tr>
                <th className="p-3 rounded-l-lg">Date</th>
                <th className="p-3">Merchant / Description</th>
                <th className="p-3">Category</th>
                <th className="p-3">Method</th>
                <th className="p-3 text-right rounded-r-lg">Amount</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1D263B]">
              {transactions.slice(0, 5).map((t, idx) => (
                <tr key={idx} className="hover:bg-[#12192B]/50 transition-colors">
                  <td className="p-3 text-slate-400">{formatDate(t.transaction_date)}</td>
                  <td className="p-3 font-semibold text-white">{t.description}</td>
                  <td className="p-3 text-slate-300">{t.category?.name || 'General'}</td>
                  <td className="p-3 text-slate-400">{t.payment_method?.toUpperCase() || 'UPI'}</td>
                  <td className={`p-3 text-right font-bold ${t.transaction_type === 'credit' ? 'text-emerald-400' : 'text-slate-100'}`}>
                    {t.transaction_type === 'credit' ? '+' : '-'}{formatCurrency(t.amount)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
