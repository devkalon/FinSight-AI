'use client';

import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  ArrowDownRight,
  Calendar,
  Wallet,
  PiggyBank,
  PieChart as PieChartIcon,
  BarChart3,
  Sliders,
  ShieldAlert,
  RefreshCw,
  Layers,
  ShoppingBag,
  CheckCircle2,
  AlertTriangle,
  Zap,
  Filter
} from 'lucide-react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { api, ComprehensiveAnalyticsDashboard, ForecastData, AnomalySummary, DetailedAnomaly } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';

const DATE_PRESETS = [
  { label: 'This Month', value: 'this_month' },
  { label: 'Last Month', value: 'last_month' },
  { label: 'Last 3 Months', value: '3_months' },
  { label: 'Last 6 Months', value: '6_months' },
  { label: 'Year to Date', value: 'ytd' },
  { label: 'Custom', value: 'custom' },
];

export default function AnalyticsPage() {
  const [dashboard, setDashboard] = useState<ComprehensiveAnalyticsDashboard | null>(null);
  const [forecast, setForecast] = useState<ForecastData | null>(null);
  const [anomalyData, setAnomalyData] = useState<AnomalySummary | null>(null);
  const [isScanningAnomalies, setIsScanningAnomalies] = useState(false);
  const [anomalySeverityFilter, setAnomalySeverityFilter] = useState('all');
  const [anomalyTypeFilter, setAnomalyTypeFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [preset, setPreset] = useState('this_month');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  // What-If Simulation State
  const [incomeChange, setIncomeChange] = useState(15000);
  const [expenseCut, setExpenseCut] = useState(5000);
  const [oneTimeSpend, setOneTimeSpend] = useState(50000);
  const [inflation, setInflation] = useState(6);

  const calculateDatesForPreset = (presetKey: string) => {
    const today = new Date();
    const endStr = today.toISOString().split('T')[0];
    let startStr = '';

    if (presetKey === 'this_month') {
      const start = new Date(today.getFullYear(), today.getMonth(), 1);
      startStr = start.toISOString().split('T')[0];
    } else if (presetKey === 'last_month') {
      const start = new Date(today.getFullYear(), today.getMonth() - 1, 1);
      const end = new Date(today.getFullYear(), today.getMonth(), 0);
      return { startStr: start.toISOString().split('T')[0], endStr: end.toISOString().split('T')[0] };
    } else if (presetKey === '3_months') {
      const start = new Date(today.getFullYear(), today.getMonth() - 3, 1);
      startStr = start.toISOString().split('T')[0];
    } else if (presetKey === '6_months') {
      const start = new Date(today.getFullYear(), today.getMonth() - 6, 1);
      startStr = start.toISOString().split('T')[0];
    } else if (presetKey === 'ytd') {
      const start = new Date(today.getFullYear(), 0, 1);
      startStr = start.toISOString().split('T')[0];
    }
    return { startStr, endStr };
  };

  const fetchAnalytics = async (sDate?: string, eDate?: string) => {
    setLoading(true);
    try {
      const [dashData, forecastData, anomData] = await Promise.all([
        api.getAnalyticsDashboard(sDate, eDate),
        api.getForecast(),
        api.getAnomalies()
      ]);
      setDashboard(dashData);
      setForecast(forecastData);
      setAnomalyData(anomData);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleScanAnomalies = async () => {
    setIsScanningAnomalies(true);
    try {
      const freshAnom = await api.scanAnomalies();
      setAnomalyData(freshAnom);
    } catch (e) {
      console.error(e);
    } finally {
      setIsScanningAnomalies(false);
    }
  };

  useEffect(() => {
    const { startStr, endStr } = calculateDatesForPreset('this_month');
    setStartDate(startStr);
    setEndDate(endStr);
    fetchAnalytics(startStr, endStr);
  }, []);

  const handlePresetChange = (newPreset: string) => {
    setPreset(newPreset);
    if (newPreset !== 'custom') {
      const { startStr, endStr } = calculateDatesForPreset(newPreset);
      setStartDate(startStr);
      setEndDate(endStr);
      fetchAnalytics(startStr, endStr);
    }
  };

  const handleCustomApply = () => {
    fetchAnalytics(startDate, endDate);
  };

  // What-If Scenario Calculation
  const baseIncome = (dashboard?.summary.total_income || 85000) + incomeChange;
  const baseExpense = Math.max((dashboard?.summary.total_expenses || 35000) - expenseCut, 10000);
  const baseMonthlyNet = baseIncome - baseExpense;
  const projected2YearCorpus = (baseMonthlyNet * 24 * (1 + 0.12)) - oneTimeSpend;

  const summary = dashboard?.summary;
  const mom = dashboard?.month_over_month;
  const split = dashboard?.spending_split;

  return (
    <div className="space-y-8">
      {/* Header & Date-Range Controls */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Financial Analytics & Intelligence</h1>
          <p className="text-slate-400 text-sm mt-0.5">
            Deterministic decimal-safe ledger calculations, cash flow trends & scenario modeling
          </p>
        </div>

        {/* Date Range Selector Bar */}
        <div className="flex flex-wrap items-center gap-2 bg-[#0D1322] p-1.5 rounded-xl border border-[#1E293B]">
          {DATE_PRESETS.map((p) => (
            <button
              key={p.value}
              onClick={() => handlePresetChange(p.value)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                preset === p.value
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-[#1E293B]/50'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Custom Date Inputs if custom is selected */}
      {preset === 'custom' && (
        <div className="p-4 rounded-xl bg-[#0D1322] border border-[#1E293B] flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 font-medium">From:</span>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="bg-[#11192C] border border-[#1E293B] rounded-lg px-3 py-1.5 text-xs text-white"
            />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 font-medium">To:</span>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="bg-[#11192C] border border-[#1E293B] rounded-lg px-3 py-1.5 text-xs text-white"
            />
          </div>
          <button
            onClick={handleCustomApply}
            className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold transition-colors"
          >
            Apply Filter
          </button>
        </div>
      )}

      {/* 5 Deterministic KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Total Income */}
        <div className="p-5 rounded-2xl bg-[#0D1322] border border-[#1E293B] relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Total Income</span>
            <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-white mt-2">
            {formatCurrency(summary?.total_income || 0)}
          </div>
          {mom && (
            <div className="flex items-center gap-1 mt-2 text-xs">
              {mom.income_change_pct >= 0 ? (
                <span className="text-emerald-400 font-semibold flex items-center">
                  <ArrowUpRight className="w-3.5 h-3.5" /> +{mom.income_change_pct}%
                </span>
              ) : (
                <span className="text-rose-400 font-semibold flex items-center">
                  <ArrowDownRight className="w-3.5 h-3.5" /> {mom.income_change_pct}%
                </span>
              )}
              <span className="text-slate-500">vs prior period</span>
            </div>
          )}
        </div>

        {/* Total Expenses */}
        <div className="p-5 rounded-2xl bg-[#0D1322] border border-[#1E293B] relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Total Expenses</span>
            <div className="p-1.5 rounded-lg bg-rose-500/10 text-rose-400">
              <TrendingDown className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-white mt-2">
            {formatCurrency(summary?.total_expenses || 0)}
          </div>
          {mom && (
            <div className="flex items-center gap-1 mt-2 text-xs">
              {mom.expense_change_pct <= 0 ? (
                <span className="text-emerald-400 font-semibold flex items-center">
                  <ArrowDownRight className="w-3.5 h-3.5" /> {mom.expense_change_pct}%
                </span>
              ) : (
                <span className="text-rose-400 font-semibold flex items-center">
                  <ArrowUpRight className="w-3.5 h-3.5" /> +{mom.expense_change_pct}%
                </span>
              )}
              <span className="text-slate-500">vs prior period</span>
            </div>
          )}
        </div>

        {/* Net Savings */}
        <div className="p-5 rounded-2xl bg-[#0D1322] border border-[#1E293B] relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Net Savings</span>
            <div className="p-1.5 rounded-lg bg-blue-500/10 text-blue-400">
              <PiggyBank className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-emerald-400 mt-2">
            {formatCurrency(summary?.net_savings || 0)}
          </div>
          {mom && (
            <div className="flex items-center gap-1 mt-2 text-xs">
              <span className={`font-semibold ${mom.savings_change_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                {mom.savings_change_pct >= 0 ? `+${mom.savings_change_pct}%` : `${mom.savings_change_pct}%`}
              </span>
              <span className="text-slate-500">net shift</span>
            </div>
          )}
        </div>

        {/* Savings Rate */}
        <div className="p-5 rounded-2xl bg-[#0D1322] border border-[#1E293B] relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Savings Rate</span>
            <div className="p-1.5 rounded-lg bg-purple-500/10 text-purple-400">
              <Zap className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-purple-400 mt-2">
            {summary?.savings_rate_pct || 0}%
          </div>
          <div className="w-full bg-[#1A2338] h-1.5 rounded-full mt-3 overflow-hidden">
            <div
              className="bg-purple-500 h-full rounded-full transition-all duration-500"
              style={{ width: `${Math.min(summary?.savings_rate_pct || 0, 100)}%` }}
            />
          </div>
        </div>

        {/* Daily Average Burn */}
        <div className="p-5 rounded-2xl bg-[#0D1322] border border-[#1E293B] relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Daily Avg Spend</span>
            <div className="p-1.5 rounded-lg bg-amber-500/10 text-amber-400">
              <Wallet className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-white mt-2">
            {formatCurrency(summary?.average_daily_spending || 0)}
          </div>
          <p className="text-xs text-slate-500 mt-2">Over {summary?.days_in_period || 30} days window</p>
        </div>
      </div>

      {/* Income vs Expenses Cashflow Trends + Category Breakdown Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Income vs Expenses Bar Chart */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-[#0D1322] border border-[#1E293B] space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-bold text-white text-base">Cash Flow & Savings Trajectory</h2>
              <p className="text-xs text-slate-400">Monthly income vs expenses comparison</p>
            </div>
            <span className="text-xs px-2.5 py-1 rounded-md bg-blue-500/10 text-blue-400 font-semibold border border-blue-500/20">
              Deterministic Ledger
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={dashboard?.income_vs_expense_trends || []} barGap={4}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
                <XAxis dataKey="month" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={11} tickLine={false} tickFormatter={(v) => `₹${(v/1000)}k`} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0D1322', borderColor: '#1E293B', borderRadius: '12px' }}
                  formatter={(val: number) => [`₹${val.toLocaleString()}`, '']}
                />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                <Bar dataKey="income" name="Income" fill="#10B981" radius={[4, 4, 0, 0]} />
                <Bar dataKey="expense" name="Expenses" fill="#EF4444" radius={[4, 4, 0, 0]} />
                <Bar dataKey="savings" name="Net Savings" fill="#3B82F6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Breakdown Donut */}
        <div className="p-6 rounded-2xl bg-[#0D1322] border border-[#1E293B] space-y-4">
          <div>
            <h2 className="font-bold text-white text-base">Category Allocation</h2>
            <p className="text-xs text-slate-400">Share of total debit expenses</p>
          </div>

          <div className="h-52 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={dashboard?.category_breakdown || []}
                  dataKey="total_amount"
                  nameKey="category_name"
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={3}
                >
                  {(dashboard?.category_breakdown || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color || '#6366F1'} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0D1322', borderColor: '#1E293B', borderRadius: '12px' }}
                  formatter={(val: number) => [`₹${val.toLocaleString()}`, '']}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Category List */}
          <div className="space-y-2 max-h-40 overflow-y-auto pr-1">
            {(dashboard?.category_breakdown || []).slice(0, 5).map((cat, idx) => (
              <div key={idx} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: cat.color }} />
                  <span className="text-slate-300 font-medium">{cat.category_name}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-slate-400">{cat.percentage_of_total}%</span>
                  <span className="text-white font-semibold">{formatCurrency(cat.total_amount)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 50/30/20 Essential vs Discretionary Split & Budget Utilization */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Essential vs Discretionary Spending */}
        <div className="p-6 rounded-2xl bg-[#0D1322] border border-[#1E293B] space-y-5">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-bold text-white text-base">Essential vs Discretionary Allocation</h2>
              <p className="text-xs text-slate-400">50/30/20 Financial Framework Adherence</p>
            </div>
            <span className="text-xs px-2.5 py-1 rounded-md bg-purple-500/10 text-purple-400 font-semibold border border-purple-500/20">
              Needs vs Wants
            </span>
          </div>

          {/* Multi-segment Progress Bar */}
          <div className="w-full bg-[#1A2338] h-3.5 rounded-full flex overflow-hidden">
            <div
              className="bg-emerald-500 h-full transition-all"
              style={{ width: `${split?.essential_pct || 50}%` }}
              title={`Essential: ${split?.essential_pct}%`}
            />
            <div
              className="bg-purple-500 h-full transition-all"
              style={{ width: `${split?.discretionary_pct || 30}%` }}
              title={`Discretionary: ${split?.discretionary_pct}%`}
            />
            <div
              className="bg-blue-500 h-full transition-all"
              style={{ width: `${split?.savings_investment_pct || 20}%` }}
              title={`Savings & Investments: ${split?.savings_investment_pct}%`}
            />
          </div>

          {/* Breakdown Pills */}
          <div className="grid grid-cols-3 gap-3">
            <div className="p-3.5 rounded-xl bg-[#11192C] border border-[#1E293B]">
              <div className="flex items-center gap-1.5 text-xs text-emerald-400 font-semibold">
                <div className="w-2 h-2 rounded-full bg-emerald-500" />
                Needs (Essential)
              </div>
              <div className="text-base font-bold text-white mt-1">{formatCurrency(split?.essential_amount || 0)}</div>
              <span className="text-xs text-slate-400">{split?.essential_pct || 0}% of budget</span>
            </div>

            <div className="p-3.5 rounded-xl bg-[#11192C] border border-[#1E293B]">
              <div className="flex items-center gap-1.5 text-xs text-purple-400 font-semibold">
                <div className="w-2 h-2 rounded-full bg-purple-500" />
                Wants (Lifestyle)
              </div>
              <div className="text-base font-bold text-white mt-1">{formatCurrency(split?.discretionary_amount || 0)}</div>
              <span className="text-xs text-slate-400">{split?.discretionary_pct || 0}% of budget</span>
            </div>

            <div className="p-3.5 rounded-xl bg-[#11192C] border border-[#1E293B]">
              <div className="flex items-center gap-1.5 text-xs text-blue-400 font-semibold">
                <div className="w-2 h-2 rounded-full bg-blue-500" />
                Savings & SIPs
              </div>
              <div className="text-base font-bold text-white mt-1">{formatCurrency(split?.savings_investment_amount || 0)}</div>
              <span className="text-xs text-slate-400">{split?.savings_investment_pct || 0}% allocated</span>
            </div>
          </div>
        </div>

        {/* Budget Utilization Gauges */}
        <div className="p-6 rounded-2xl bg-[#0D1322] border border-[#1E293B] space-y-4">
          <div>
            <h2 className="font-bold text-white text-base">Category Budget Utilization</h2>
            <p className="text-xs text-slate-400">Actual period spending vs monthly limits</p>
          </div>

          <div className="space-y-3.5 max-h-56 overflow-y-auto pr-1">
            {(dashboard?.budget_utilization || []).map((b, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-[#11192C] border border-[#1E293B] space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-slate-200">{b.category_name}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-slate-400">{formatCurrency(b.spent_amount)} / {formatCurrency(b.budgeted_amount)}</span>
                    <span className={`font-bold ${b.is_over_budget ? 'text-rose-400' : 'text-emerald-400'}`}>
                      {b.utilization_pct}%
                    </span>
                  </div>
                </div>
                <div className="w-full bg-[#1A2338] h-2 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${
                      b.is_over_budget ? 'bg-rose-500' : b.utilization_pct > 80 ? 'bg-amber-500' : 'bg-emerald-500'
                    }`}
                    style={{ width: `${Math.min(b.utilization_pct, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Top Merchants Leaderboard & Recurring Commitments */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Merchants */}
        <div className="p-6 rounded-2xl bg-[#0D1322] border border-[#1E293B] space-y-4">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400">
              <ShoppingBag className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-white text-base">Top Spending Merchants</h3>
              <p className="text-xs text-slate-400">Largest vendors by volume in selected period</p>
            </div>
          </div>

          <div className="divide-y divide-[#1E293B]">
            {(dashboard?.largest_merchants || []).map((m, idx) => (
              <div key={idx} className="py-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-xs font-bold text-slate-500 w-4">#{idx + 1}</span>
                  <div>
                    <div className="text-sm font-semibold text-slate-200">{m.merchant_name}</div>
                    <div className="text-xs text-slate-400">{m.transaction_count} transactions • {m.percentage_of_expenses}% of expenses</div>
                  </div>
                </div>
                <div className="text-sm font-bold text-white">{formatCurrency(m.total_amount)}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Recurring Expenses Schedule */}
        <div className="p-6 rounded-2xl bg-[#0D1322] border border-[#1E293B] space-y-4">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400">
              <RefreshCw className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-white text-base">Active Recurring Commitments</h3>
              <p className="text-xs text-slate-400">Automated subscriptions & bills</p>
            </div>
          </div>

          <div className="divide-y divide-[#1E293B]">
            {(dashboard?.recurring_expenses || []).map((sub, idx) => (
              <div key={idx} className="py-3 flex items-center justify-between">
                <div>
                  <div className="text-sm font-semibold text-slate-200">{sub.service_name}</div>
                  <div className="text-xs text-slate-400 mt-0.5">{sub.category_name || 'Subscriptions'} • Next: {sub.next_billing_date}</div>
                </div>
                <div className="text-sm font-bold text-purple-400">{formatCurrency(sub.amount)}/mo</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Predictive Expense Forecasting Engine */}
      <div className="p-6 rounded-2xl bg-[#0D1322] border border-[#1E293B] space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#1E293B] pb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <TrendingUp className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="font-bold text-white text-base">Predictive Expense Forecasting Engine</h2>
                <span className="px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 text-[10px] font-bold">
                  {forecast?.confidence_score ? `${Math.round(forecast.confidence_score * 100)}% Confidence` : '85% CI'}
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Multi-horizon probabilistic projection across total, category, and recurring liabilities
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3 text-xs">
            <div className="px-3 py-1.5 rounded-xl bg-[#11192C] border border-[#1E293B] text-slate-300">
              Trend: <strong className="text-white capitalize">{forecast?.trend || 'Stable'}</strong>
            </div>
            <div className="px-3 py-1.5 rounded-xl bg-[#11192C] border border-[#1E293B] text-slate-300">
              Daily Burn: <strong className="text-white">{formatCurrency(forecast?.historical_average_daily || 0)}/day</strong>
            </div>
          </div>
        </div>

        {/* Statistical Non-Guaranteed Disclaimer Notice */}
        <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-start space-x-3">
          <AlertTriangle className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" />
          <p className="text-xs text-amber-300/90 leading-relaxed">
            {forecast?.disclaimer || "Statistical Projection Notice: Future expense forecasts are probabilistic mathematical estimates derived from historical spending patterns and recurring commitments. They do not constitute guaranteed outcomes."}
          </p>
        </div>

        {/* 3 Horizon KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-[#11192C] border border-[#1E293B]">
            <span className="text-[10px] text-slate-400 uppercase font-semibold">Next 30 Days Forecast</span>
            <div className="text-2xl font-extrabold text-white mt-1">
              {formatCurrency(forecast?.projected_next_30_days_total || 0)}
            </div>
            {forecast?.monthly_prediction_interval && (
              <div className="text-[11px] text-slate-400 mt-1">
                Range: <span className="text-slate-200">{formatCurrency(forecast.monthly_prediction_interval.lower_bound)}</span> – <span className="text-slate-200">{formatCurrency(forecast.monthly_prediction_interval.upper_bound)}</span>
              </div>
            )}
          </div>

          <div className="p-4 rounded-xl bg-[#11192C] border border-[#1E293B]">
            <span className="text-[10px] text-slate-400 uppercase font-semibold">Next 60 Days Cumulative</span>
            <div className="text-2xl font-extrabold text-white mt-1">
              {formatCurrency(forecast?.projected_next_60_days_total || 0)}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              Estimated 2-month burn baseline
            </div>
          </div>

          <div className="p-4 rounded-xl bg-[#11192C] border border-[#1E293B]">
            <span className="text-[10px] text-slate-400 uppercase font-semibold">Next 90 Days Cumulative</span>
            <div className="text-2xl font-extrabold text-white mt-1">
              {formatCurrency(forecast?.projected_next_90_days_total || 0)}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              Estimated Runway: <span className="text-emerald-400 font-bold">{forecast?.estimated_runway_months || 24} mos</span>
            </div>
          </div>
        </div>

        {/* Human Readable Explanation Box */}
        {forecast?.human_readable_explanation && (
          <div className="p-4 rounded-xl bg-[#11192C] border border-[#1E293B] space-y-2">
            <span className="text-[10px] text-blue-400 uppercase font-bold tracking-wider">AI Forecast Synthesis</span>
            <p className="text-xs text-slate-200 leading-relaxed">{forecast.human_readable_explanation}</p>
            {forecast.major_contributing_factors && forecast.major_contributing_factors.length > 0 && (
              <div className="pt-2 flex flex-wrap gap-1.5">
                {forecast.major_contributing_factors.map((factor, fIdx) => (
                  <span key={fIdx} className="px-2.5 py-1 rounded-md bg-[#0D1322] border border-[#1E293B] text-[11px] text-slate-300">
                    • {factor}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Time-Series 30-Day Forecast Chart */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-white">30-Day Daily Expense Confidence Band</span>
            <span className="text-[11px] text-slate-400">Upper 80% CI | Projected | Lower 80% CI</span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={forecast?.forecast_points || []}>
                <defs>
                  <linearGradient id="forecastGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
                <XAxis dataKey="date" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={11} tickLine={false} tickFormatter={(val) => `₹${val}`} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0D1322', borderColor: '#1E293B', borderRadius: '12px' }}
                  formatter={(val: number) => [`₹${val.toLocaleString()}`, '']}
                />
                <Area type="monotone" dataKey="upper_bound" stroke="#60A5FA" strokeDasharray="4 4" strokeWidth={1} fillOpacity={0} name="Upper Bound" />
                <Area type="monotone" dataKey="projected_expense" stroke="#3B82F6" strokeWidth={2.5} fillOpacity={1} fill="url(#forecastGrad)" name="Projected Expense" />
                <Area type="monotone" dataKey="lower_bound" stroke="#93C5FD" strokeDasharray="4 4" strokeWidth={1} fillOpacity={0} name="Lower Bound" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category-Level Future Expense Projections */}
        {forecast?.category_forecasts && forecast.category_forecasts.length > 0 && (
          <div className="space-y-3">
            <span className="text-xs font-bold text-white block">Category-Level Future Projections</span>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {forecast.category_forecasts.map((cat, idx) => (
                <div key={idx} className="p-3.5 rounded-xl bg-[#11192C] border border-[#1E293B] space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-xs text-white">{cat.category_name}</span>
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400">
                      {cat.percentage_of_total}% share
                    </span>
                  </div>
                  <div className="text-lg font-extrabold text-white">{formatCurrency(cat.predicted_amount)}</div>
                  <div className="text-[10px] text-slate-400">
                    Est. Range: {formatCurrency(cat.prediction_interval.lower_bound)} – {formatCurrency(cat.prediction_interval.upper_bound)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Holdout Model Evaluation vs Naive Baseline Benchmark Card */}
        {forecast?.evaluation && (
          <div className="p-4 rounded-xl bg-[#11192C] border border-[#1E293B] space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs font-bold text-white">Model Evaluation Benchmark (Historical Holdout)</span>
                <p className="text-[11px] text-slate-400">Advanced Seasonal Trend Model vs Simple Moving Average Baseline</p>
              </div>
              <span className="px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 text-xs font-bold border border-emerald-500/20">
                +{forecast.evaluation.accuracy_improvement_pct}% More Accurate
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-2.5 rounded-lg bg-[#0D1322] border border-[#1E293B]">
                <span className="text-[10px] text-slate-400 uppercase">MAPE (Advanced)</span>
                <div className="text-sm font-bold text-emerald-400 mt-0.5">{forecast.evaluation.mape}%</div>
                <span className="text-[10px] text-slate-500">Baseline: {forecast.evaluation.baseline_mape}%</span>
              </div>
              <div className="p-2.5 rounded-lg bg-[#0D1322] border border-[#1E293B]">
                <span className="text-[10px] text-slate-400 uppercase">RMSE (Advanced)</span>
                <div className="text-sm font-bold text-emerald-400 mt-0.5">₹{forecast.evaluation.rmse}</div>
                <span className="text-[10px] text-slate-500">Baseline: ₹{forecast.evaluation.baseline_rmse}</span>
              </div>
              <div className="p-2.5 rounded-lg bg-[#0D1322] border border-[#1E293B]">
                <span className="text-[10px] text-slate-400 uppercase">MAE (Advanced)</span>
                <div className="text-sm font-bold text-emerald-400 mt-0.5">₹{forecast.evaluation.mae}</div>
                <span className="text-[10px] text-slate-500">Baseline: ₹{forecast.evaluation.baseline_mae}</span>
              </div>
              <div className="p-2.5 rounded-lg bg-[#0D1322] border border-[#1E293B]">
                <span className="text-[10px] text-slate-400 uppercase">Holdout Sample</span>
                <div className="text-sm font-bold text-white mt-0.5">{forecast.evaluation.evaluation_holdout_days} Days</div>
                <span className="text-[10px] text-slate-500">Temporal Split</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Interactive What-If Scenario Simulator */}
      <div className="p-6 rounded-2xl bg-[#0D1322] border border-[#1E293B] space-y-6">
        <div className="flex items-center space-x-3 border-b border-[#1E293B] pb-4">
          <div className="p-2.5 rounded-xl bg-blue-500/10 text-blue-400">
            <Sliders className="w-5 h-5" />
          </div>
          <div>
            <h2 className="font-bold text-white text-base">What-If Financial Scenario Simulator</h2>
            <p className="text-xs text-slate-400">Model career promotions, inflation spikes, cost-cutting, and major purchases</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div>
            <label className="text-xs text-slate-300 font-semibold block mb-2">Monthly Income Increase (₹)</label>
            <input
              type="range"
              min={0}
              max={100000}
              step={5000}
              value={incomeChange}
              onChange={(e) => setIncomeChange(Number(e.target.value))}
              className="w-full h-2 bg-[#1A2338] rounded-lg accent-blue-500"
            />
            <span className="text-xs text-blue-400 font-bold mt-1 block">+{formatCurrency(incomeChange)}/mo</span>
          </div>

          <div>
            <label className="text-xs text-slate-300 font-semibold block mb-2">Monthly Expense Reduction (₹)</label>
            <input
              type="range"
              min={0}
              max={25000}
              step={1000}
              value={expenseCut}
              onChange={(e) => setExpenseCut(Number(e.target.value))}
              className="w-full h-2 bg-[#1A2338] rounded-lg accent-emerald-500"
            />
            <span className="text-xs text-emerald-400 font-bold mt-1 block">-{formatCurrency(expenseCut)}/mo burn</span>
          </div>

          <div>
            <label className="text-xs text-slate-300 font-semibold block mb-2">One-Time Asset Purchase (₹)</label>
            <input
              type="range"
              min={0}
              max={500000}
              step={10000}
              value={oneTimeSpend}
              onChange={(e) => setOneTimeSpend(Number(e.target.value))}
              className="w-full h-2 bg-[#1A2338] rounded-lg accent-rose-500"
            />
            <span className="text-xs text-rose-400 font-bold mt-1 block">{formatCurrency(oneTimeSpend)}</span>
          </div>

          <div>
            <label className="text-xs text-slate-300 font-semibold block mb-2">Inflation Rate (%)</label>
            <input
              type="range"
              min={3}
              max={12}
              step={0.5}
              value={inflation}
              onChange={(e) => setInflation(Number(e.target.value))}
              className="w-full h-2 bg-[#1A2338] rounded-lg accent-amber-500"
            />
            <span className="text-xs text-amber-400 font-bold mt-1 block">{inflation}% Annual</span>
          </div>
        </div>

        {/* Simulation Output Box */}
        <div className="p-5 rounded-xl bg-[#11192C] border border-[#1E293B] flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400">Projected 24-Month Portfolio with Simulation:</span>
            <div className="text-2xl font-extrabold text-white mt-0.5">{formatCurrency(projected2YearCorpus)}</div>
          </div>
          <div className="right text-right">
            <span className="text-xs text-slate-400">Monthly Net Surplus:</span>
            <div className="text-lg font-bold text-emerald-400 mt-0.5">{formatCurrency(baseMonthlyNet)}/mo</div>
          </div>
        </div>
      </div>

      {/* Statistical Anomaly & Outlier Detection Dashboard */}
      <div className="p-6 rounded-2xl bg-[#0D1322] border border-[#1E293B] space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#1E293B] pb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="font-bold text-white text-base">Statistical Anomaly & Spending Outlier Radar</h2>
                {anomalyData && anomalyData.total_anomalies > 0 && (
                  <span className="px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-400 text-[10px] font-bold">
                    {anomalyData.total_anomalies} flagged
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400">
                Multi-dimensional detection across category surges, single-transaction outliers, frequency bursts & price hikes
              </p>
            </div>
          </div>

          <button
            onClick={handleScanAnomalies}
            disabled={isScanningAnomalies}
            className="flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-[#11192C] hover:bg-[#1E293B] border border-[#1E293B] text-xs font-semibold text-slate-200 transition-all shadow-sm"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-blue-400 ${isScanningAnomalies ? 'animate-spin' : ''}`} />
            <span>{isScanningAnomalies ? 'Scanning Ledger...' : 'Run Anomaly Scan'}</span>
          </button>
        </div>

        {/* Anomaly KPI Summary Bar */}
        {anomalyData && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3.5 rounded-xl bg-[#11192C] border border-[#1E293B]">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Total Anomalies</span>
              <div className="text-xl font-bold text-white mt-0.5">{anomalyData.total_anomalies}</div>
            </div>
            <div className="p-3.5 rounded-xl bg-[#11192C] border border-[#1E293B]">
              <span className="text-[10px] text-rose-400 uppercase font-semibold">Critical / High Severity</span>
              <div className="text-xl font-bold text-rose-400 mt-0.5">
                {(anomalyData.critical_count || 0) + (anomalyData.high_count || 0)}
              </div>
            </div>
            <div className="p-3.5 rounded-xl bg-[#11192C] border border-[#1E293B]">
              <span className="text-[10px] text-amber-400 uppercase font-semibold">Medium Severity</span>
              <div className="text-xl font-bold text-amber-400 mt-0.5">{anomalyData.medium_count || 0}</div>
            </div>
            <div className="p-3.5 rounded-xl bg-[#11192C] border border-[#1E293B]">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Net Excess Deviation</span>
              <div className="text-xl font-bold text-emerald-400 mt-0.5">
                +{formatCurrency(anomalyData.total_excess_deviation || 0)}
              </div>
            </div>
          </div>
        )}

        {/* Severity Filter Controls */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="text-slate-400 text-[11px] mr-1">Severity:</span>
          {['all', 'critical', 'high', 'medium'].map((sev) => (
            <button
              key={sev}
              onClick={() => setAnomalySeverityFilter(sev)}
              className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition-all ${
                anomalySeverityFilter === sev
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'bg-[#11192C] text-slate-400 hover:text-white border border-[#1E293B]'
              }`}
            >
              {sev.toUpperCase()}
            </button>
          ))}
        </div>

        {/* Anomaly Cards List */}
        {anomalyData && anomalyData.anomalies && anomalyData.anomalies.length > 0 ? (
          <div className="space-y-3">
            {anomalyData.anomalies
              .filter((a) => anomalySeverityFilter === 'all' || a.severity === anomalySeverityFilter)
              .map((anom) => {
                const isCritical = anom.severity === 'critical';
                const isHigh = anom.severity === 'high';
                const badgeColor = isCritical
                  ? 'bg-rose-500/20 text-rose-400 border-rose-500/30'
                  : isHigh
                  ? 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                  : 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';

                return (
                  <div
                    key={anom.id}
                    className="p-4 rounded-xl bg-[#11192C] border border-[#1E293B] space-y-3 hover:border-slate-700 transition-all"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <div className="flex items-center space-x-2.5">
                        <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold uppercase border ${badgeColor}`}>
                          {anom.severity}
                        </span>
                        <span className="font-bold text-sm text-white">{anom.entity_name}</span>
                        <span className="text-[10px] text-slate-400 font-mono">
                          ({anom.anomaly_type.replace('_', ' ')})
                        </span>
                      </div>

                      {/* Deviation Badge */}
                      <div className="flex items-center space-x-3 text-xs">
                        <span className="text-slate-400">
                          Observed: <strong className="text-white">{formatCurrency(anom.observed_value)}</strong>
                        </span>
                        <span className="text-slate-500">|</span>
                        <span className="text-slate-400">
                          Typical: <strong className="text-slate-300">{formatCurrency(anom.expected_value)}</strong>
                        </span>
                        <span className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 font-mono font-bold text-[11px]">
                          {anom.deviation}
                        </span>
                      </div>
                    </div>

                    <p className="text-xs text-slate-300 leading-relaxed bg-[#0D1322] p-2.5 rounded-lg border border-[#1E293B]/60">
                      {anom.explanation}
                    </p>

                    {/* Affected Transactions List */}
                    {anom.affected_transactions && anom.affected_transactions.length > 0 && (
                      <div className="pt-1 space-y-1.5">
                        <span className="text-[10px] text-slate-400 uppercase font-semibold">Affected Transactions:</span>
                        <div className="flex flex-wrap gap-2">
                          {anom.affected_transactions.map((tx, idx) => (
                            <div
                              key={idx}
                              className="px-2.5 py-1 rounded-lg bg-[#0D1322] border border-[#1E293B] text-[11px] text-slate-300 flex items-center space-x-2"
                            >
                              <span className="text-slate-400">{tx.transaction_date}</span>
                              <span className="font-medium text-white">{tx.merchant || tx.description}</span>
                              <span className="font-bold text-rose-400">{formatCurrency(tx.amount)}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
          </div>
        ) : (
          <div className="p-6 rounded-xl bg-[#11192C] border border-[#1E293B] text-center space-y-2">
            <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto" />
            <div className="font-bold text-white text-sm">All Spending Patterns Healthy</div>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              No statistical anomalies, category spikes, or duplicate charges detected. All expenditures are within normal baseline ranges.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
