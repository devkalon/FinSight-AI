'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Receipt,
  Plus,
  Search,
  SlidersHorizontal,
  ChevronLeft,
  ChevronRight,
  Edit2,
  Trash2,
  Eye,
  X,
  ArrowUpDown,
  CreditCard,
  RefreshCw,
  Info
} from 'lucide-react';
import { api, Transaction, Category, PaginatedResponse, TransactionFilterParams } from '@/lib/api';
import { formatCurrency, formatDate } from '@/lib/utils';
import { useAuth } from '@/context/AuthContext';

export default function TransactionsPage() {
  const { user } = useAuth();

  const [paginatedData, setPaginatedData] = useState<PaginatedResponse<Transaction>>({
    items: [],
    total_count: 0,
    page: 1,
    page_size: 10,
    total_pages: 1,
  });
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);

  // Filter States
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [merchantFilter, setMerchantFilter] = useState('');
  const [paymentMethodFilter, setPaymentMethodFilter] = useState('all');
  const [sourceFilter, setSourceFilter] = useState('all');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [minAmount, setMinAmount] = useState('');
  const [maxAmount, setMaxAmount] = useState('');
  const [sortBy, setSortBy] = useState('transaction_date');
  const [sortOrder, setSortOrder] = useState('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);

  // Modal States
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
  const [selectedTx, setSelectedTx] = useState<Transaction | null>(null);

  // Form State
  const [formData, setFormData] = useState({
    description: '',
    merchant_name: '',
    amount: '',
    currency: 'INR',
    transaction_type: 'debit',
    category_id: '',
    subcategory: '',
    payment_method: 'UPI',
    source: 'manual',
    transaction_date: new Date().toISOString().split('T')[0],
    notes: '',
  });
  const [formError, setFormError] = useState('');
  const [formSubmitting, setFormSubmitting] = useState(false);

  useEffect(() => {
    async function loadCats() {
      const cats = await api.getCategories();
      setCategories(cats);
    }
    loadCats();
  }, []);

  const fetchTransactions = useCallback(async () => {
    setLoading(true);
    try {
      const params: TransactionFilterParams = {
        page: currentPage,
        page_size: pageSize,
        search: search.trim() || undefined,
        category_id: selectedCategory || undefined,
        merchant_name: merchantFilter.trim() || undefined,
        transaction_type: filterType !== 'all' ? filterType : undefined,
        payment_method: paymentMethodFilter !== 'all' ? paymentMethodFilter : undefined,
        source: sourceFilter !== 'all' ? sourceFilter : undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        min_amount: minAmount ? parseFloat(minAmount) : undefined,
        max_amount: maxAmount ? parseFloat(maxAmount) : undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
      };

      const data = await api.getTransactions(params);
      setPaginatedData(data);
    } finally {
      setLoading(false);
    }
  }, [
    currentPage,
    pageSize,
    search,
    selectedCategory,
    merchantFilter,
    filterType,
    paymentMethodFilter,
    sourceFilter,
    startDate,
    endDate,
    minAmount,
    maxAmount,
    sortBy,
    sortOrder,
  ]);

  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  const resetFilters = () => {
    setSearch('');
    setFilterType('all');
    setSelectedCategory('');
    setMerchantFilter('');
    setPaymentMethodFilter('all');
    setSourceFilter('all');
    setStartDate('');
    setEndDate('');
    setMinAmount('');
    setMaxAmount('');
    setSortBy('transaction_date');
    setSortOrder('desc');
    setCurrentPage(1);
  };

  const openCreateModal = () => {
    setFormData({
      description: '',
      merchant_name: '',
      amount: '',
      currency: user?.preferred_currency || 'INR',
      transaction_type: 'debit',
      category_id: categories[0]?.id || '',
      subcategory: '',
      payment_method: 'UPI',
      source: 'manual',
      transaction_date: new Date().toISOString().split('T')[0],
      notes: '',
    });
    setFormError('');
    setIsCreateModalOpen(true);
  };

  const openEditModal = (tx: Transaction) => {
    setSelectedTx(tx);
    setFormData({
      description: tx.description,
      merchant_name: tx.merchant_name || '',
      amount: String(tx.amount),
      currency: tx.currency || 'INR',
      transaction_type: tx.transaction_type,
      category_id: tx.category?.id || tx.category_id || '',
      subcategory: tx.subcategory || '',
      payment_method: tx.payment_method || 'UPI',
      source: tx.source || 'manual',
      transaction_date: tx.transaction_date,
      notes: tx.notes || '',
    });
    setFormError('');
    setIsEditModalOpen(true);
  };

  const openDetailsModal = (tx: Transaction) => {
    setSelectedTx(tx);
    setIsDetailsModalOpen(true);
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError('');
    const amt = parseFloat(formData.amount);
    if (isNaN(amt) || amt <= 0) {
      setFormError('Amount must be a valid positive number');
      return;
    }

    setFormSubmitting(true);
    try {
      if (isEditModalOpen && selectedTx) {
        await api.updateTransaction(selectedTx.id, {
          description: formData.description,
          merchant_name: formData.merchant_name || undefined,
          amount: amt,
          currency: formData.currency,
          transaction_type: formData.transaction_type,
          category_id: formData.category_id || undefined,
          subcategory: formData.subcategory || undefined,
          payment_method: formData.payment_method,
          source: formData.source,
          transaction_date: formData.transaction_date,
          notes: formData.notes || undefined,
        });
        setIsEditModalOpen(false);
      } else {
        await api.createTransaction({
          description: formData.description,
          merchant_name: formData.merchant_name || undefined,
          amount: amt,
          currency: formData.currency,
          transaction_type: formData.transaction_type,
          category_id: formData.category_id || undefined,
          subcategory: formData.subcategory || undefined,
          payment_method: formData.payment_method,
          source: formData.source,
          transaction_date: formData.transaction_date,
          notes: formData.notes || undefined,
        });
        setIsCreateModalOpen(false);
      }
      fetchTransactions();
    } catch (err: any) {
      setFormError(err.message || 'Operation failed');
    } finally {
      setFormSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this transaction?')) return;
    try {
      await api.deleteTransaction(id);
      fetchTransactions();
    } catch (err: any) {
      alert(err.message || 'Failed to delete transaction');
    }
  };

  return (
    <div className="space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#1E293B]">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">Transaction Ledger</h1>
          <p className="text-slate-400 text-xs sm:text-sm mt-0.5">
            Complete financial record with multi-source ingestion, intelligent categorization, and deterministic audit trail.
          </p>
        </div>
        <div className="flex items-center space-x-2.5">
          <button
            onClick={fetchTransactions}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-[#222735] hover:bg-[#272F42] text-slate-300 text-xs font-medium border border-[#1E293B] transition-all"
            title="Refresh transactions"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">Refresh</span>
          </button>
          <button
            onClick={openCreateModal}
            className="flex items-center space-x-2 px-3.5 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-[#0F172A] text-xs font-semibold shadow-xs transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Record Transaction</span>
          </button>
        </div>
      </div>

      <div className="p-4 rounded-xl bg-[#222735] border border-[#1E293B] space-y-3">
        <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-2.5" />
            <input
              type="text"
              placeholder="Search description, merchant or notes..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full pl-10 pr-4 py-2 bg-[#0F172A] border border-[#1E293B] rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500 transition-colors"
            />
          </div>

          <div className="flex items-center space-x-1 bg-[#0F172A] p-1 rounded-lg border border-[#1E293B]">
            {['all', 'debit', 'credit'].map((type) => (
              <button
                key={type}
                onClick={() => {
                  setFilterType(type);
                  setCurrentPage(1);
                }}
                className={`px-3 py-1.5 rounded-md text-xs font-medium capitalize transition-all ${
                  filterType === type
                    ? 'bg-amber-500 text-[#0F172A]'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {type === 'all' ? 'All' : type === 'debit' ? 'Outflow' : 'Inflow'}
              </button>
            ))}
          </div>

          <button
            onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
            className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-xs font-medium border transition-all ${
              showAdvancedFilters || selectedCategory || startDate || minAmount
                ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
                : 'bg-[#0F172A] border-[#1E293B] text-slate-400 hover:text-slate-200'
            }`}
          >
            <SlidersHorizontal className="w-3.5 h-3.5" />
            <span>Filters</span>
          </button>
        </div>

        {showAdvancedFilters && (
          <div className="pt-3 border-t border-[#1E293B] grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
            <div>
              <label className="block text-slate-400 mb-1">Category</label>
              <select
                value={selectedCategory}
                onChange={(e) => {
                  setSelectedCategory(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full p-2 bg-[#0F172A] border border-[#1E293B] rounded-lg text-slate-200 focus:outline-none focus:border-amber-500 transition-colors"
              >
                <option value="">All Categories</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-slate-400 mb-1">Payment Method</label>
              <select
                value={paymentMethodFilter}
                onChange={(e) => {
                  setPaymentMethodFilter(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full p-2 bg-[#222735] border border-[#1E293B] rounded-lg text-slate-200 focus:outline-none focus:border-amber-500"
              >
                <option value="all">All Methods</option>
                <option value="UPI">UPI</option>
                <option value="Credit Card">Credit Card</option>
                <option value="Debit Card">Debit Card</option>
                <option value="Net Banking">Net Banking</option>
                <option value="Cash">Cash</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-400 mb-1">Source</label>
              <select
                value={sourceFilter}
                onChange={(e) => {
                  setSourceFilter(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full p-2 bg-[#222735] border border-[#1E293B] rounded-lg text-slate-200 focus:outline-none focus:border-amber-500"
              >
                <option value="all">All Sources</option>
                <option value="manual">Manual Entry</option>
                <option value="ocr_receipt">OCR Receipt</option>
                <option value="bank_pdf">Bank PDF</option>
                <option value="csv">CSV Statement</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-400 mb-1">Sort By</label>
              <div className="flex space-x-1.5">
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="flex-1 p-2 bg-[#222735] border border-[#1E293B] rounded-lg text-slate-200 focus:outline-none focus:border-amber-500"
                >
                  <option value="transaction_date">Date</option>
                  <option value="amount">Amount</option>
                  <option value="merchant_name">Merchant</option>
                  <option value="created_at">Created Time</option>
                </select>
                <button
                  onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                  className="px-2.5 bg-[#222735] border border-[#1E293B] rounded-lg text-slate-300 hover:text-white"
                  title="Toggle Ascending/Descending"
                >
                  <ArrowUpDown className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            <div>
              <label className="block text-slate-400 mb-1">Start Date</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => {
                  setStartDate(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full p-2 bg-[#222735] border border-[#1E293B] rounded-lg text-slate-200 focus:outline-none focus:border-amber-500"
              />
            </div>

            <div>
              <label className="block text-slate-400 mb-1">End Date</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => {
                  setEndDate(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full p-2 bg-[#222735] border border-[#1E293B] rounded-lg text-slate-200 focus:outline-none focus:border-amber-500"
              />
            </div>

            <div>
              <label className="block text-slate-400 mb-1">Min Amount (₹)</label>
              <input
                type="number"
                placeholder="0"
                value={minAmount}
                onChange={(e) => {
                  setMinAmount(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full p-2 bg-[#222735] border border-[#1E293B] rounded-lg text-slate-200 focus:outline-none focus:border-amber-500"
              />
            </div>

            <div>
              <label className="block text-slate-400 mb-1">Max Amount (₹)</label>
              <input
                type="number"
                placeholder="Unlimited"
                value={maxAmount}
                onChange={(e) => {
                  setMaxAmount(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full p-2 bg-[#222735] border border-[#1E293B] rounded-lg text-slate-200 focus:outline-none focus:border-amber-500"
              />
            </div>

            <div className="sm:col-span-2 md:col-span-4 flex justify-end pt-1">
              <button
                onClick={resetFilters}
                className="text-xs text-rose-400 hover:text-rose-300 font-semibold"
              >
                Clear All Filters
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="rounded-xl bg-[#222735] border border-[#1E293B] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-[#0F172A] text-slate-400 text-xs uppercase font-semibold border-b border-[#1E293B]">
              <tr>
                <th className="px-5 py-3.5">Transaction / Merchant</th>
                <th className="px-5 py-3.5">Category</th>
                <th className="px-5 py-3.5">Date</th>
                <th className="px-5 py-3.5">Method</th>
                <th className="px-5 py-3.5 text-right">Amount</th>
                <th className="px-5 py-3.5 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1E293B]">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-16 text-center">
                    <div className="inline-block w-6 h-6 border-2 border-amber-500 border-t-transparent rounded-full animate-spin mb-3"></div>
                    <div className="text-slate-400 text-sm">Loading ledger from database...</div>
                  </td>
                </tr>
              ) : paginatedData.items.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-16 text-center">
                    <Receipt className="w-10 h-10 text-slate-700 mx-auto mb-3" />
                    <div className="text-slate-300 font-semibold text-sm">No transactions found</div>
                    <div className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">Adjust your filters, upload a bank statement, or record a transaction manually.</div>
                  </td>
                </tr>
              ) : (
                paginatedData.items.map((tx) => (
                  <tr key={tx.id} className="hover:bg-[#272F42]/40 transition-colors group">
                    <td className="px-5 py-3.5">
                      <div className="flex items-center space-x-3">
                        <div
                          className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                          style={{
                            backgroundColor: `${tx.category?.color || '#F59E0B'}18`,
                            color: tx.category?.color || '#F59E0B',
                          }}
                        >
                          <Receipt className="w-3.5 h-3.5" />
                        </div>
                        <div className="min-w-0">
                          <div className="font-medium text-slate-200 truncate text-sm">{tx.description}</div>
                          <div className="text-[11px] text-slate-400 flex items-center gap-1.5 mt-0.5">
                            {tx.merchant_name && <span>{tx.merchant_name}</span>}
                            {tx.subcategory && <span className="text-slate-500">· {tx.subcategory}</span>}
                            {tx.is_subscription && (
                              <span className="px-1.5 py-0.2 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20 text-[10px] font-medium">
                                Recurring
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-3.5">
                      <span
                        className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium border"
                        style={{
                          backgroundColor: `${tx.category?.color || '#8B5CF6'}12`,
                          color: tx.category?.color || '#8B5CF6',
                          borderColor: `${tx.category?.color || '#8B5CF6'}30`,
                        }}
                      >
                        {tx.category?.name || 'General'}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-slate-400 text-xs tabular-nums">
                      {formatDate(tx.transaction_date)}
                    </td>
                    <td className="px-5 py-3.5 text-slate-400 text-xs font-mono">
                      {tx.payment_method || 'UPI'}
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <span
                        className={`font-semibold tabular-nums text-sm ${
                          tx.transaction_type === 'credit' ? 'text-emerald-400' : 'text-slate-100'
                        }`}
                      >
                        {tx.transaction_type === 'credit' ? '+' : '-'}
                        {formatCurrency(tx.amount)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="flex items-center justify-center space-x-1.5 opacity-90 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={() => openDetailsModal(tx)}
                          className="p-1.5 text-slate-400 hover:text-amber-400 hover:bg-amber-500/10 rounded-lg transition-colors"
                          title="View Details"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => openEditModal(tx)}
                          className="p-1.5 text-slate-400 hover:text-emerald-400 hover:bg-emerald-500/10 rounded-lg transition-colors"
                          title="Edit Transaction"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(tx.id)}
                          className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                          title="Delete Transaction"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="px-6 py-4 bg-[#222735] border-t border-[#1E293B] flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-400">
          <div className="flex items-center space-x-4">
            <span>
              Showing <span className="font-semibold text-slate-200">{paginatedData.items.length}</span> of{' '}
              <span className="font-semibold text-slate-200">{paginatedData.total_count}</span> transactions
            </span>
            <div className="flex items-center space-x-1.5">
              <span>Per page:</span>
              <select
                value={pageSize}
                onChange={(e) => {
                  setPageSize(Number(e.target.value));
                  setCurrentPage(1);
                }}
                className="bg-[#0F172A] border border-[#1E293B] rounded-lg px-2 py-1 text-slate-200 focus:outline-none focus:border-amber-500"
              >
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={50}>50</option>
              </select>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              disabled={currentPage <= 1 || loading}
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              className="p-1.5 rounded-lg bg-[#0F172A] border border-[#1E293B] text-slate-300 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="px-2 font-medium text-slate-200">
              Page {paginatedData.page} of {paginatedData.total_pages}
            </span>
            <button
              disabled={currentPage >= paginatedData.total_pages || loading}
              onClick={() => setCurrentPage((p) => p + 1)}
              className="p-1.5 rounded-lg bg-[#0F172A] border border-[#1E293B] text-slate-300 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {(isCreateModalOpen || isEditModalOpen) && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0F172A] border border-[#1E293B] rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-white text-base flex items-center gap-2">
                <Receipt className="w-5 h-5 text-amber-400" />
                {isEditModalOpen ? 'Edit Transaction' : 'Record New Transaction'}
              </h3>
              <button
                onClick={() => {
                  setIsCreateModalOpen(false);
                  setIsEditModalOpen(false);
                }}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {formError && (
              <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-medium">
                {formError}
              </div>
            )}

            <form onSubmit={handleFormSubmit} className="space-y-3.5 text-xs">
              <div>
                <label className="text-slate-400 block mb-1 font-medium">Description *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Swiggy Lunch, Grocery Shopping"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full p-2.5 bg-[#222735] border border-[#1E293B] rounded-xl text-slate-100 focus:outline-none focus:border-amber-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1 font-medium">Merchant / Payee</label>
                  <input
                    type="text"
                    placeholder="e.g. Starbucks, Amazon"
                    value={formData.merchant_name}
                    onChange={(e) => setFormData({ ...formData, merchant_name: e.target.value })}
                    className="w-full p-2.5 bg-[#222735] border border-[#1E293B] rounded-xl text-slate-100 focus:outline-none focus:border-amber-500"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1 font-medium">Subcategory</label>
                  <input
                    type="text"
                    placeholder="e.g. Coffee, Office Supplies"
                    value={formData.subcategory}
                    onChange={(e) => setFormData({ ...formData, subcategory: e.target.value })}
                    className="w-full p-2.5 bg-[#222735] border border-[#1E293B] rounded-xl text-slate-100 focus:outline-none focus:border-amber-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div className="col-span-2">
                  <label className="text-slate-400 block mb-1 font-medium">Amount *</label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    placeholder="0.00"
                    value={formData.amount}
                    onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                    className="w-full p-2.5 bg-[#222735] border border-[#1E293B] rounded-xl text-slate-100 focus:outline-none focus:border-amber-500"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1 font-medium">Currency</label>
                  <select
                    value={formData.currency}
                    onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
                    className="w-full p-2.5 bg-[#222735] border border-[#1E293B] rounded-xl text-slate-100 focus:outline-none focus:border-amber-500"
                  >
                    <option value="INR">INR (₹)</option>
                    <option value="USD">USD ($)</option>
                    <option value="EUR">EUR (€)</option>
                    <option value="GBP">GBP (£)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1 font-medium">Transaction Type</label>
                  <select
                    value={formData.transaction_type}
                    onChange={(e) => setFormData({ ...formData, transaction_type: e.target.value })}
                    className="w-full p-2.5 bg-[#222735] border border-[#1E293B] rounded-xl text-slate-100 focus:outline-none focus:border-amber-500"
                  >
                    <option value="debit">Expense (Debit)</option>
                    <option value="credit">Income (Credit)</option>
                    <option value="transfer">Account Transfer</option>
                  </select>
                </div>
                <div>
                  <label className="text-slate-400 block mb-1 font-medium">Category</label>
                  <select
                    value={formData.category_id}
                    onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                    className="w-full p-2.5 bg-[#222735] border border-[#1E293B] rounded-xl text-slate-100 focus:outline-none focus:border-amber-500"
                  >
                    <option value="">Auto-Detect / General</option>
                    {categories.map((c) => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1 font-medium">Payment Method</label>
                  <select
                    value={formData.payment_method}
                    onChange={(e) => setFormData({ ...formData, payment_method: e.target.value })}
                    className="w-full p-2.5 bg-[#222735] border border-[#1E293B] rounded-xl text-slate-100 focus:outline-none focus:border-amber-500"
                  >
                    <option value="UPI">UPI</option>
                    <option value="Credit Card">Credit Card</option>
                    <option value="Debit Card">Debit Card</option>
                    <option value="Net Banking">Net Banking</option>
                    <option value="Cash">Cash</option>
                  </select>
                </div>
                <div>
                  <label className="text-slate-400 block mb-1 font-medium">Date</label>
                  <input
                    type="date"
                    value={formData.transaction_date}
                    onChange={(e) => setFormData({ ...formData, transaction_date: e.target.value })}
                    className="w-full p-2.5 bg-[#222735] border border-[#1E293B] rounded-xl text-slate-100 focus:outline-none focus:border-amber-500"
                  />
                </div>
              </div>

              <div>
                <label className="text-slate-400 block mb-1 font-medium">Notes / Remarks</label>
                <textarea
                  rows={2}
                  placeholder="Optional notes or context..."
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  className="w-full p-2.5 bg-[#222735] border border-[#1E293B] rounded-xl text-slate-100 focus:outline-none focus:border-amber-500 resize-none"
                />
              </div>

              <button
                type="submit"
                disabled={formSubmitting}
                className="w-full py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-[#0F172A] font-semibold shadow-lg shadow-amber-500/25 transition-all disabled:opacity-50"
              >
                {formSubmitting
                  ? 'Saving...'
                  : isEditModalOpen
                  ? 'Save Changes'
                  : 'Record Transaction'}
              </button>
            </form>
          </div>
        </div>
      )}

      {isDetailsModalOpen && selectedTx && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0F172A] border border-[#1E293B] rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-[#1E293B] pb-3">
              <div>
                <span className="text-xs text-amber-400 font-bold uppercase tracking-wider">Transaction Details</span>
                <h3 className="font-bold text-white text-lg">{selectedTx.description}</h3>
              </div>
              <button
                onClick={() => setIsDetailsModalOpen(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between items-center p-3 rounded-xl bg-[#222735] border border-[#1E293B]">
                <span className="text-slate-400">Total Amount:</span>
                <span
                  className={`text-base font-bold ${
                    selectedTx.transaction_type === 'credit' ? 'text-emerald-400' : 'text-slate-100'
                  }`}
                >
                  {selectedTx.transaction_type === 'credit' ? '+' : '-'}
                  {formatCurrency(selectedTx.amount, selectedTx.currency || 'INR')}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-slate-300">
                <div className="p-2.5 rounded-lg bg-[#222735]">
                  <span className="text-[10px] text-slate-500 block">Category</span>
                  <span className="font-semibold text-slate-200">{selectedTx.category?.name || 'General'}</span>
                </div>
                <div className="p-2.5 rounded-lg bg-[#222735]">
                  <span className="text-[10px] text-slate-500 block">Subcategory</span>
                  <span className="font-semibold text-slate-200">{selectedTx.subcategory || 'None'}</span>
                </div>
                <div className="p-2.5 rounded-lg bg-[#222735]">
                  <span className="text-[10px] text-slate-500 block">Merchant / Payee</span>
                  <span className="font-semibold text-slate-200">{selectedTx.merchant_name || 'N/A'}</span>
                </div>
                <div className="p-2.5 rounded-lg bg-[#222735]">
                  <span className="text-[10px] text-slate-500 block">Payment Mode</span>
                  <span className="font-semibold text-slate-200">{selectedTx.payment_method || 'UPI'}</span>
                </div>
                <div className="p-2.5 rounded-lg bg-[#222735]">
                  <span className="text-[10px] text-slate-500 block">Date</span>
                  <span className="font-semibold text-slate-200">{formatDate(selectedTx.transaction_date)}</span>
                </div>
                <div className="p-2.5 rounded-lg bg-[#222735]">
                  <span className="text-[10px] text-slate-500 block">Source</span>
                  <span className="font-semibold text-slate-200 capitalize">{selectedTx.source || 'manual'}</span>
                </div>
              </div>

              {selectedTx.confidence_score !== undefined && (
                <div className="p-2.5 rounded-lg bg-[#222735] flex items-center justify-between">
                  <span className="text-slate-400">Confidence Score:</span>
                  <span className="font-semibold text-emerald-400">
                    {Math.round((selectedTx.confidence_score || 1) * 100)}%
                  </span>
                </div>
              )}

              {selectedTx.notes && (
                <div className="p-2.5 rounded-lg bg-[#222735]">
                  <span className="text-[10px] text-slate-500 block mb-1">Notes</span>
                  <p className="text-slate-300 italic">{selectedTx.notes}</p>
                </div>
              )}

              <div className="pt-2 text-[10px] text-slate-500 text-center font-mono">
                ID: {selectedTx.id}
              </div>
            </div>

            <div className="flex space-x-2 pt-2 border-t border-[#1E293B]">
              <button
                onClick={() => {
                  setIsDetailsModalOpen(false);
                  openEditModal(selectedTx);
                }}
                className="flex-1 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-[#0F172A] font-semibold text-xs transition-colors"
              >
                Edit Transaction
              </button>
              <button
                onClick={() => {
                  setIsDetailsModalOpen(false);
                  handleDelete(selectedTx.id);
                }}
                className="px-4 py-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 font-semibold text-xs border border-rose-500/20 transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}