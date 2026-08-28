'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  UploadCloud,
  FileText,
  Receipt,
  FileSpreadsheet,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  ShieldCheck,
  ArrowRight,
  RefreshCw,
  Edit2,
  Trash2,
  X,
  Check
} from 'lucide-react';
import {
  api,
  FinancialDocument,
  CandidateTransaction,
  Category,
  DocumentIngestionResponse
} from '@/lib/api';
import { formatCurrency, formatDate } from '@/lib/utils';

export default function UploadPage() {
  const [documents, setDocuments] = useState<FinancialDocument[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);

  // Ingestion States
  const [uploadMode, setUploadMode] = useState<'statement' | 'receipt'>('statement');
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStage, setProcessingStage] = useState('');
  const [uploadError, setUploadError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Candidate Review State
  const [activeIngestion, setActiveIngestion] = useState<DocumentIngestionResponse | null>(null);
  const [candidateList, setCandidateList] = useState<CandidateTransaction[]>([]);
  const [isConfirming, setIsConfirming] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    try {
      const [docs, cats] = await Promise.all([
        api.getDocuments(),
        api.getCategories()
      ]);
      setDocuments(docs || []);
      setCategories(cats || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsProcessing(true);
    setUploadError('');
    setSuccessMessage('');
    setProcessingStage('Pre-processing image and scanning ledger patterns...');

    try {
      let res: DocumentIngestionResponse;
      if (uploadMode === 'receipt') {
        setProcessingStage('Extracting receipt OCR bounding boxes and merchant data...');
        res = await api.uploadReceipt(file);
      } else {
        setProcessingStage('Parsing bank statement balance integrity and UPI narratives...');
        res = await api.uploadBankStatement(file);
      }

      setActiveIngestion(res);
      setCandidateList(res.candidates || []);
      setSuccessMessage(`Document scanned: ${res.candidates?.length || 0} candidate transactions extracted for review.`);
      loadData();
    } catch (err: any) {
      setUploadError(err.message || 'Ingestion failed. Please check file format.');
    } finally {
      setIsProcessing(false);
      setProcessingStage('');
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleCandidateChange = (index: number, field: keyof CandidateTransaction, value: any) => {
    const updated = [...candidateList];
    updated[index] = { ...updated[index], [field]: value };
    setCandidateList(updated);
  };

  const handleRemoveCandidate = (index: number) => {
    setCandidateList(candidateList.filter((_, i) => i !== index));
  };

  const handleConfirmAndCommit = async () => {
    if (!activeIngestion) return;
    setIsConfirming(true);
    try {
      await api.confirmCandidateTransactions(activeIngestion.document_id, candidateList);
      setSuccessMessage(`Successfully committed ${candidateList.length} transactions into verified ledger!`);
      setActiveIngestion(null);
      setCandidateList([]);
      loadData();
    } catch (err: any) {
      setUploadError(err.message || 'Commit failed');
    } finally {
      setIsConfirming(false);
    }
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#1D263B] pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Document Ingestion & OCR</h1>
          <p className="text-slate-400 text-xs mt-0.5">
            Extract, verify, and commit transactions from bank statements, UPI exports, and receipts.
          </p>
        </div>

        {/* Upload Mode Switcher */}
        <div className="flex items-center space-x-1.5 p-1 rounded-xl bg-[#0A0E1A] border border-[#1D263B] text-xs">
          <button
            onClick={() => setUploadMode('statement')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg font-semibold transition-all ${
              uploadMode === 'statement'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <FileSpreadsheet className="w-3.5 h-3.5" />
            <span>Bank Statement (CSV/PDF)</span>
          </button>
          <button
            onClick={() => setUploadMode('receipt')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg font-semibold transition-all ${
              uploadMode === 'receipt'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Receipt className="w-3.5 h-3.5" />
            <span>Receipt / Invoice (OCR)</span>
          </button>
        </div>
      </div>

      {/* Upload Dropzone */}
      <div className="p-8 rounded-2xl bg-[#0F1626] border-2 border-dashed border-[#1D263B] hover:border-blue-500/50 transition-all text-center space-y-4">
        <input
          ref={fileInputRef}
          type="file"
          accept={uploadMode === 'receipt' ? '.png,.jpg,.jpeg,.pdf' : '.csv,.pdf,.xlsx'}
          onChange={handleFileUpload}
          className="hidden"
          id="file-upload"
        />

        <label htmlFor="file-upload" className="cursor-pointer block space-y-3">
          <div className="w-14 h-14 rounded-2xl bg-blue-600/10 border border-blue-500/20 flex items-center justify-center mx-auto text-blue-400">
            <UploadCloud className="w-7 h-7" />
          </div>

          <div>
            <span className="font-bold text-white text-sm">
              Click to upload or drag and drop your {uploadMode === 'statement' ? 'Bank Statement' : 'Receipt / Bill'}
            </span>
            <p className="text-slate-400 text-xs mt-1">
              Supports HDFC, SBI, ICICI, PhonePe, Google Pay, Razorpay receipts & multi-page statements.
            </p>
          </div>

          <div className="flex items-center justify-center space-x-2 text-[11px] text-emerald-400 font-semibold pt-2">
            <ShieldCheck className="w-4 h-4" />
            <span>Local PII Scrubber Active: Sensitive account numbers redacted before processing</span>
          </div>
        </label>

        {isProcessing && (
          <div className="p-4 rounded-xl bg-[#0A0E1A] border border-[#1D263B] space-y-2 text-xs text-blue-400 animate-pulse">
            <RefreshCw className="w-4 h-4 animate-spin mx-auto text-blue-400" />
            <span>{processingStage}</span>
          </div>
        )}

        {uploadError && (
          <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-semibold">
            {uploadError}
          </div>
        )}

        {successMessage && (
          <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
            {successMessage}
          </div>
        )}
      </div>

      {/* Candidate Transactions Review Stage */}
      {activeIngestion && candidateList.length > 0 && (
        <div className="p-6 rounded-2xl bg-[#0F1626] border border-blue-500/30 space-y-4">
          <div className="flex items-center justify-between border-b border-[#1D263B] pb-3">
            <div>
              <h2 className="font-bold text-white text-base">Verify Candidate Transactions ({candidateList.length})</h2>
              <p className="text-slate-400 text-xs">Edit values if needed before committing into the permanent financial ledger.</p>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={() => setActiveIngestion(null)}
                className="px-3 py-1.5 rounded-lg bg-[#0A0E1A] hover:bg-[#12192B] border border-[#1D263B] text-slate-400 text-xs font-semibold transition-all"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmAndCommit}
                disabled={isConfirming}
                className="flex items-center space-x-1.5 px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-md shadow-emerald-500/20 transition-all"
              >
                <Check className="w-3.5 h-3.5" />
                <span>{isConfirming ? 'Committing...' : 'Commit to Ledger'}</span>
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-[#0A0E1A] text-slate-400 uppercase text-[10px]">
                <tr>
                  <th className="p-2.5 rounded-l-lg">Date</th>
                  <th className="p-2.5">Description</th>
                  <th className="p-2.5">Type</th>
                  <th className="p-2.5">Category</th>
                  <th className="p-2.5">Amount (₹)</th>
                  <th className="p-2.5 text-right rounded-r-lg">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1D263B]">
                {candidateList.map((c, idx) => (
                  <tr key={idx} className="hover:bg-[#12192B]/50">
                    <td className="p-2">
                      <input
                        type="date"
                        value={c.transaction_date ? String(c.transaction_date).split('T')[0] : ''}
                        onChange={(e) => handleCandidateChange(idx, 'transaction_date', e.target.value)}
                        className="bg-[#0A0E1A] border border-[#1D263B] rounded-lg p-1 text-slate-200 text-xs"
                      />
                    </td>
                    <td className="p-2">
                      <input
                        type="text"
                        value={c.description}
                        onChange={(e) => handleCandidateChange(idx, 'description', e.target.value)}
                        className="bg-[#0A0E1A] border border-[#1D263B] rounded-lg p-1 text-slate-200 text-xs w-48"
                      />
                    </td>
                    <td className="p-2">
                      <select
                        value={c.transaction_type}
                        onChange={(e) => handleCandidateChange(idx, 'transaction_type', e.target.value)}
                        className="bg-[#0A0E1A] border border-[#1D263B] rounded-lg p-1 text-slate-200 text-xs"
                      >
                        <option value="debit">Debit</option>
                        <option value="credit">Credit</option>
                      </select>
                    </td>
                    <td className="p-2">
                      <select
                        value={c.category_suggestion || ''}
                        onChange={(e) => handleCandidateChange(idx, 'category_suggestion', e.target.value)}
                        className="bg-[#0A0E1A] border border-[#1D263B] rounded-lg p-1 text-slate-200 text-xs"
                      >
                        {categories.map((cat) => (
                          <option key={cat.id} value={cat.name}>{cat.name}</option>
                        ))}
                      </select>
                    </td>
                    <td className="p-2">
                      <input
                        type="number"
                        value={c.amount}
                        onChange={(e) => handleCandidateChange(idx, 'amount', parseFloat(e.target.value) || 0)}
                        className="bg-[#0A0E1A] border border-[#1D263B] rounded-lg p-1 text-slate-200 text-xs w-24 font-bold"
                      />
                    </td>
                    <td className="p-2 text-right">
                      <button
                        onClick={() => handleRemoveCandidate(idx)}
                        className="p-1 rounded text-slate-400 hover:text-rose-400 transition-colors"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Uploaded Documents History */}
      <div className="p-6 rounded-2xl bg-[#0F1626] border border-[#1D263B] space-y-4">
        <h2 className="font-bold text-white text-base">Processed Statements & Receipts</h2>
        {documents.length === 0 ? (
          <p className="text-xs text-slate-400">No documents ingested yet. Upload your first statement or receipt above.</p>
        ) : (
          <div className="divide-y divide-[#1D263B]">
            {documents.map((doc) => (
              <div key={doc.id} className="py-3 flex items-center justify-between text-xs">
                <div className="flex items-center space-x-3">
                  <div className="p-2 rounded-xl bg-[#0A0E1A] border border-[#1D263B]">
                    <FileText className="w-4 h-4 text-blue-400" />
                  </div>
                  <div>
                    <span className="font-semibold text-white">{doc.filename}</span>
                    <div className="text-slate-400 text-[11px]">
                      {doc.file_type?.toUpperCase()} • Uploaded on {formatDate(doc.created_at)}
                    </div>
                  </div>
                </div>
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 font-semibold text-[10px] border border-emerald-500/20">
                  {doc.processing_status?.toUpperCase() || 'PROCESSED'}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
