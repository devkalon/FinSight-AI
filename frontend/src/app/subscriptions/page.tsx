'use client';

import React, { useState, useEffect } from 'react';
import {
  RefreshCcw,
  Plus,
  CheckCircle2,
  XCircle,
  Calendar,
  AlertTriangle,
  CreditCard,
  Tv,
  Zap,
  Dumbbell,
  FileText,
  Trash2,
  Edit2,
  Sparkles,
  ShieldCheck,
  X
} from 'lucide-react';
import { api, SubscriptionItem, SubscriptionDashboardData } from '@/lib/api';
import { formatCurrency, formatDate } from '@/lib/utils';

export default function SubscriptionsPage() {
  const [data, setData] = useState<SubscriptionDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [filterType, setFilterType] = useState<string>('all');

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingSub, setEditingSub] = useState<SubscriptionItem | null>(null);
  const [form, setForm] = useState({
    service_name: '',
    amount: '',
    billing_cycle: 'monthly',
    recurring_type: 'monthly_subscription',
    next_billing_date: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    try {
      const res = await api.getSubscriptionsDashboard();
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function handleScan() {
    setScanning(true);
    try {
      const res = await api.scanSubscriptions();
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setScanning(false);
    }
  }

  async function handleConfirm(id: string) {
    try {
      const updated = await api.confirmSubscription(id);
      setData((prev) => {
        if (!prev) return prev;
        const newSubs = prev.subscriptions.map((s) => (s.id === id ? updated : s));
        const active = newSubs.filter((s) => s.is_active && s.status !== 'dismissed');
        const pending = newSubs.filter((s) => s.status === 'detected');
        const totalMon = active.reduce((acc, s) => acc + (s.annualized_cost || s.amount * 12) / 12, 0);
        return {
          ...prev,
          active_subscriptions_count: active.length,
          pending_detection_count: pending.length,
          total_monthly_recurring: Math.round(totalMon),
          total_annual_recurring: Math.round(totalMon * 12),
          subscriptions: newSubs
        };
      });
    } catch (err) {
      console.error(err);
    }
  }

  async function handleDismiss(id: string) {
    try {
      const updated = await api.dismissSubscription(id);
      setData((prev) => {
        if (!prev) return prev;
        const newSubs = prev.subscriptions.map((s) => (s.id === id ? updated : s));
        const active = newSubs.filter((s) => s.is_active && s.status !== 'dismissed');
        const pending = newSubs.filter((s) => s.status === 'detected');
        const totalMon = active.reduce((acc, s) => acc + (s.annualized_cost || s.amount * 12) / 12, 0);
        return {
          ...prev,
          active_subscriptions_count: active.length,
          pending_detection_count: pending.length,
          total_monthly_recurring: Math.round(totalMon),
          total_annual_recurring: Math.round(totalMon * 12),
          subscriptions: newSubs
        };
      });
    } catch (err) {
      console.error(err);
    }
  }

  async function handleDelete(id: string) {
    try {
      await api.deleteSubscription(id);
      setData((prev) => {
        if (!prev) return prev;
        const newSubs = prev.subscriptions.filter((s) => s.id !== id);
        const active = newSubs.filter((s) => s.is_active && s.status !== 'dismissed');
        const pending = newSubs.filter((s) => s.status === 'detected');
        const totalMon = active.reduce((acc, s) => acc + (s.annualized_cost || s.amount * 12) / 12, 0);
        return {
          ...prev,
          active_subscriptions_count: active.length,
          pending_detection_count: pending.length,
          total_monthly_recurring: Math.round(totalMon),
          total_annual_recurring: Math.round(totalMon * 12),
          subscriptions: newSubs
        };
      });
    } catch (err) {
      console.error(err);
    }
  }

  function openCreateModal() {
    setEditingSub(null);
    setForm({
      service_name: '',
      amount: '',
      billing_cycle: 'monthly',
      recurring_type: 'monthly_subscription',
      next_billing_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    });
    setIsModalOpen(true);
  }

  function openEditModal(sub: SubscriptionItem) {
    setEditingSub(sub);
    setForm({
      service_name: sub.service_name,
      amount: String(sub.amount),
      billing_cycle: sub.billing_cycle,
      recurring_type: sub.recurring_type || 'monthly_subscription',
      next_billing_date: sub.next_billing_date ? sub.next_billing_date.split('T')[0] : ''
    });
    setIsModalOpen(true);
  }

  async function handleFormSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      if (editingSub && editingSub.id) {
        const updated = await api.updateSubscription(editingSub.id, {
          service_name: form.service_name,
          amount: parseFloat(form.amount) || editingSub.amount,
          billing_cycle: form.billing_cycle,
          recurring_type: form.recurring_type,
          next_billing_date: form.next_billing_date
        });
        setData((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            subscriptions: prev.subscriptions.map((s) => (s.id === updated.id ? updated : s))
          };
        });
      } else {
        const created = await api.createSubscription({
          service_name: form.service_name,
          amount: parseFloat(form.amount) || 499,
          billing_cycle: form.billing_cycle,
          recurring_type: form.recurring_type,
          next_billing_date: form.next_billing_date
        });
        setData((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            active_subscriptions_count: prev.active_subscriptions_count + 1,
            subscriptions: [...prev.subscriptions, created]
          };
        });
      }
      setIsModalOpen(false);
    } catch (err) {
      console.error(err);
    }
  }

  // Filter subscriptions
  const allSubs = data?.subscriptions || [];
  const pendingSubs = allSubs.filter((s) => s.status === 'detected');
  const filteredSubs = allSubs.filter((s) => {
    if (filterType === 'all') return true;
    if (filterType === 'pending') return s.status === 'detected';
    if (filterType === 'monthly') return s.recurring_type === 'monthly_subscription';
    if (filterType === 'annual') return s.recurring_type === 'annual_subscription';
    if (filterType === 'bills') return s.recurring_type === 'recurring_bill';
    if (filterType === 'memberships') return s.recurring_type === 'recurring_membership';
    return true;
  });

  const getTypeIcon = (type?: string) => {
    if (type === 'monthly_subscription') return <Tv className="w-4 h-4 text-amber-400" />;
    if (type === 'annual_subscription') return <Sparkles className="w-4 h-4 text-purple-400" />;
    if (type === 'recurring_bill') return <Zap className="w-4 h-4 text-amber-400" />;
    if (type === 'recurring_membership') return <Dumbbell className="w-4 h-4 text-emerald-400" />;
    return <CreditCard className="w-4 h-4 text-slate-400" />;
  };

  const getTypeName = (type?: string) => {
    if (type === 'monthly_subscription') return 'Monthly Sub';
    if (type === 'annual_subscription') return 'Annual Sub';
    if (type === 'recurring_bill') return 'Utility Bill';
    if (type === 'recurring_membership') return 'Membership';
    return 'Recurring Payment';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#1E293B]">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">Subscriptions & Recurring Payments</h1>
            <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 font-medium text-[11px] border border-amber-500/20">
              Auto-Detection Engine
            </span>
          </div>
          <p className="text-slate-400 text-xs sm:text-sm mt-0.5">
            Identify recurring monthly & annual subscriptions, utility bills, and memberships with annualized burn calculation
          </p>
        </div>

        <div className="flex items-center space-x-2.5 self-start sm:self-auto">
          <button
            onClick={handleScan}
            disabled={scanning}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-[#222735] hover:bg-[#272F42] border border-[#1E293B] text-slate-200 text-xs font-medium transition-all"
          >
            <RefreshCcw className={`w-3.5 h-3.5 ${scanning ? 'animate-spin text-amber-400' : 'text-slate-400'}`} />
            <span>{scanning ? 'Scanning...' : 'Scan Ledger'}</span>
          </button>

          <button
            onClick={openCreateModal}
            className="flex items-center space-x-2 px-3.5 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-[#0F172A] text-xs font-semibold shadow-xs transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Add Subscription</span>
          </button>
        </div>
      </div>

      {/* KPI Banners (4 Grid) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        <div className="p-4 sm:p-5 rounded-xl bg-[#222735] border border-[#1E293B] space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Monthly Outflow</span>
            <div className="p-1 rounded-md bg-rose-500/10 text-rose-400">
              <CreditCard className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="text-xl font-bold text-white tabular-nums">
            {formatCurrency(data?.total_monthly_recurring || 3478)} <span className="text-xs text-slate-500 font-normal">/mo</span>
          </div>
          <span className="text-[11px] text-slate-400 block">Fixed recurring commitment</span>
        </div>

        <div className="p-4 sm:p-5 rounded-xl bg-[#222735] border border-[#1E293B] space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Annualized Burn</span>
            <div className="p-1 rounded-md bg-purple-500/10 text-purple-400">
              <Sparkles className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="text-xl font-bold text-slate-100 tabular-nums">
            {formatCurrency(data?.total_annual_recurring || 41736)} <span className="text-xs text-slate-500 font-normal">/yr</span>
          </div>
          <span className="text-[11px] text-slate-400 block">Projected 12-month cumulative</span>
        </div>

        <div className="p-4 sm:p-5 rounded-xl bg-[#222735] border border-[#1E293B] space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Active Services</span>
            <div className="p-1 rounded-md bg-amber-500/10 text-amber-400">
              <ShieldCheck className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="text-xl font-bold text-white tabular-nums">
            {data?.active_subscriptions_count || 5} Services
          </div>
          <span className="text-[11px] text-slate-400 block">Recurring payments confirmed</span>
        </div>

        <div className="p-4 sm:p-5 rounded-xl bg-[#222735] border border-[#1E293B] space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Pending Review</span>
            <div className="p-1 rounded-md bg-amber-500/10 text-amber-400">
              <AlertTriangle className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="text-xl font-bold text-amber-400 tabular-nums">
            {pendingSubs.length} Detected
          </div>
          <span className="text-[11px] text-slate-400 block">Pattern matches to verify</span>
        </div>
      </div>

      {/* Pending Detection Review Banner if any */}
      {pendingSubs.length > 0 && (
        <div className="p-5 rounded-2xl bg-amber-500/10 border border-amber-500/20 space-y-3">
          <div className="flex items-center space-x-2.5 text-amber-400 font-bold text-xs">
            <AlertTriangle className="w-4 h-4" />
            <span>Action Required: Newly Detected Recurring Payments ({pendingSubs.length})</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            {pendingSubs.map((ps) => (
              <div key={ps.id} className="p-3.5 rounded-xl bg-[#0F172A] border border-[#1E293B] flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-white text-sm">{ps.service_name}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                      {getTypeName(ps.recurring_type)}
                    </span>
                  </div>
                  <div className="text-slate-400 text-xs mt-1">
                    Detected: <strong className="text-slate-200">{formatCurrency(ps.amount)}</strong> ({ps.billing_cycle}) • Confidence: <strong className="text-emerald-400">{Math.round((ps.confidence || 0.9) * 100)}%</strong>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => ps.id && handleConfirm(ps.id)}
                    className="flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold transition-all"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Confirm</span>
                  </button>
                  <button
                    onClick={() => ps.id && handleDismiss(ps.id)}
                    className="flex items-center space-x-1 px-2.5 py-1.5 rounded-lg bg-[#222735] hover:bg-[#1E293B] text-slate-400 hover:text-rose-400 transition-all border border-[#1E293B]"
                  >
                    <XCircle className="w-3.5 h-3.5" />
                    <span>Dismiss</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filter Tabs */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-1 text-xs">
        {[
          { id: 'all', label: 'All Recurring' },
          { id: 'monthly', label: 'Monthly Subscriptions' },
          { id: 'annual', label: 'Annual Subscriptions' },
          { id: 'bills', label: 'Utility Bills' },
          { id: 'memberships', label: 'Memberships' },
          { id: 'pending', label: `Pending Review (${pendingSubs.length})` }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setFilterType(tab.id)}
            className={`px-3.5 py-2 rounded-xl font-semibold transition-all whitespace-nowrap ${
              filterType === tab.id
                ? 'bg-amber-500 text-[#0F172A] shadow-md shadow-amber-500/20'
                : 'bg-[#0F172A] border border-[#1E293B] text-slate-400 hover:text-white'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Subscriptions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredSubs.map((sub) => {
          const isPending = sub.status === 'detected';
          const isDismissed = sub.status === 'dismissed';
          const nextDateStr = sub.next_billing_date ? formatDate(sub.next_billing_date) : 'Upcoming';

          return (
            <div
              key={sub.id}
              className={`p-5 rounded-2xl bg-[#0F172A] border flex flex-col justify-between space-y-4 transition-all hover:border-slate-700 ${
                isPending ? 'border-amber-500/40' : isDismissed ? 'opacity-50 border-[#1E293B]' : 'border-[#1E293B]'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <div className="p-2 rounded-xl bg-[#222735] border border-[#1E293B]">
                      {getTypeIcon(sub.recurring_type)}
                    </div>
                    <span className="text-[11px] font-semibold text-slate-400">
                      {getTypeName(sub.recurring_type)}
                    </span>
                  </div>

                  <div className="flex items-center space-x-1">
                    {isPending ? (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                        Needs Confirmation
                      </span>
                    ) : isDismissed ? (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-400">
                        Dismissed
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        Active
                      </span>
                    )}

                    <button
                      onClick={() => openEditModal(sub)}
                      className="p-1 rounded-lg text-slate-500 hover:text-white hover:bg-[#222735] transition-colors"
                    >
                      <Edit2 className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => sub.id && handleDelete(sub.id)}
                      className="p-1 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-[#222735] transition-colors"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                <div>
                  <h3 className="font-bold text-white text-base mb-1">{sub.service_name}</h3>
                  <div className="text-2xl font-extrabold text-slate-100">
                    {formatCurrency(sub.amount)}{' '}
                    <span className="text-slate-500 text-xs font-normal">/ {sub.billing_cycle}</span>
                  </div>
                </div>
              </div>

              {/* Card Meta Box */}
              <div className="space-y-3 pt-3 border-t border-[#1E293B] text-xs">
                <div className="flex justify-between text-slate-400">
                  <span>Annualized Cost:</span>
                  <strong className="text-slate-200">{formatCurrency(sub.annualized_cost || sub.amount * 12)}/yr</strong>
                </div>

                <div className="flex justify-between text-slate-400">
                  <span>Next Renewal:</span>
                  <div className="flex items-center space-x-1.5 text-white font-medium">
                    <Calendar className="w-3.5 h-3.5 text-slate-400" />
                    <span>{nextDateStr}</span>
                  </div>
                </div>

                {isPending && (
                  <div className="flex items-center space-x-2 pt-2 border-t border-[#1E293B]">
                    <button
                      onClick={() => sub.id && handleConfirm(sub.id)}
                      className="flex-1 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-center transition-all"
                    >
                      Confirm
                    </button>
                    <button
                      onClick={() => sub.id && handleDismiss(sub.id)}
                      className="flex-1 py-1.5 rounded-lg bg-[#222735] hover:bg-[#1E293B] border border-[#1E293B] text-slate-400 hover:text-rose-400 text-center transition-all"
                    >
                      Dismiss
                    </button>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0F172A] border border-[#1E293B] rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-white text-base">
                {editingSub ? 'Edit Recurring Payment' : 'Add Recurring Payment'}
              </h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleFormSubmit} className="space-y-4 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">Service / Merchant Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Netflix Premium"
                  value={form.service_name}
                  onChange={(e) => setForm({ ...form, service_name: e.target.value })}
                  className="w-full p-2.5 bg-[#222735] border border-[#1E293B] rounded-xl text-slate-200"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1">Amount (₹)</label>
                  <input
                    type="number"
                    required
                    placeholder="649"
                    value={form.amount}
                    onChange={(e) => setForm({ ...form, amount: e.target.value })}
                    className="w-full p-2.5 bg-[#222735] border border-[#1E293B] rounded-xl text-slate-200"
                  />
                </div>

                <div>
                  <label className="text-slate-400 block mb-1">Billing Cycle</label>
                  <select
                    value={form.billing_cycle}
                    onChange={(e) => setForm({ ...form, billing_cycle: e.target.value })}
                    className="w-full p-2.5 bg-[#222735] border border-[#1E293B] rounded-xl text-slate-200"
                  >
                    <option value="monthly">Monthly</option>
                    <option value="yearly">Yearly (Annual)</option>
                    <option value="quarterly">Quarterly</option>
                    <option value="weekly">Weekly</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Recurring Category Type</label>
                <select
                  value={form.recurring_type}
                  onChange={(e) => setForm({ ...form, recurring_type: e.target.value })}
                  className="w-full p-2.5 bg-[#222735] border border-[#1E293B] rounded-xl text-slate-200"
                >
                  <option value="monthly_subscription">Monthly Subscription (OTT, Cloud, Apps)</option>
                  <option value="annual_subscription">Annual Subscription (Prime, Licences)</option>
                  <option value="recurring_bill">Utility Bill (Broadband, Mobile, Electricity)</option>
                  <option value="recurring_membership">Membership (Gym, Clubhouse, Co-working)</option>
                </select>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Next Expected Billing Date</label>
                <input
                  type="date"
                  value={form.next_billing_date}
                  onChange={(e) => setForm({ ...form, next_billing_date: e.target.value })}
                  className="w-full p-2.5 bg-[#222735] border border-[#1E293B] rounded-xl text-slate-200"
                />
              </div>

              <button
                type="submit"
                className="w-full py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-[#0F172A] font-semibold shadow-lg shadow-amber-500/25 transition-all"
              >
                {editingSub ? 'Update Subscription' : 'Save Recurring Payment'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
