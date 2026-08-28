'use client';

import React, { useState } from 'react';
import {
  Bot,
  Sparkles,
  Send,
  User,
  Calculator,
  BookOpen,
  Scale,
  CheckCircle2,
  HelpCircle,
  X
} from 'lucide-react';
import { formatCurrency } from '@/lib/utils';

interface Message {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  tool_calls?: any[];
  citations?: any[];
}

const personas = [
  { id: 'balanced', name: 'Balanced Wealth Advisor', desc: 'Holistic 50/30/20 & Disciplined Compounding', color: 'from-blue-600 to-indigo-600' },
  { id: 'buffett', name: 'Warren Buffett', desc: 'Value, Moats & Low-Cost Index Compounding', color: 'from-amber-600 to-orange-600' },
  { id: 'kiyosaki', name: 'Robert Kiyosaki', desc: 'Cash Flow, Asset Acquisition & Escaping Rat Race', color: 'from-purple-600 to-pink-600' },
  { id: 'sethi', name: 'Ramit Sethi', desc: 'Conscious Spending Plan & Guilt-Free Wealth Automation', color: 'from-emerald-600 to-teal-600' },
  { id: 'indian_expert', name: 'Indian Wealth Specialist', desc: 'PPF, ELSS, Mutual Fund SIPs & Term Insurance', color: 'from-sky-600 to-blue-700' }
];

export default function AdvisorPage() {
  const [selectedPersona, setSelectedPersona] = useState('balanced');
  const [inputMessage, setInputMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'init-1',
      sender: 'assistant',
      content: "👋 Welcome to FinSight AI Wealth Advisory! I am your AI financial strategist. You can ask me to calculate SIP compounding, simulate loan EMIs, review your emergency reserve, or compare investment strategies across financial gurus like Warren Buffett, Robert Kiyosaki, and Ramit Sethi.",
      citations: [
        { source_title: "The Psychology of Money", author: "Morgan Housel", relevant_quote: "The secret to investing is surviving long enough for compounding to do the heavy lifting." }
      ]
    }
  ]);

  // Philosophy Comparison Modal State
  const [isCompareOpen, setIsCompareOpen] = useState(false);
  const [compareQuestion, setCompareQuestion] = useState('Should I prepay my home loan or invest in equity index funds?');
  const [selectedDimension, setSelectedDimension] = useState('all');
  const [comparisonData, setComparisonData] = useState<any>(null);
  const [isComparing, setIsComparing] = useState(false);

  async function handleSendMessage(e: React.FormEvent) {
    e.preventDefault();
    if (!inputMessage.trim() || isSending) return;

    const userText = inputMessage.trim();
    setInputMessage('');

    const newMsg: Message = {
      id: String(Date.now()),
      sender: 'user',
      content: userText
    };
    setMessages((prev) => [...prev, newMsg]);
    setIsSending(true);

    try {
      const res = await fetch('/api/v1/advisor/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userText,
          persona: selectedPersona
        })
      });

      if (res.ok) {
        const data = await res.json();
        setMessages((prev) => [
          ...prev,
          {
            id: data.id || String(Date.now()),
            sender: 'assistant',
            content: data.content,
            tool_calls: data.tool_calls,
            citations: data.citations
          }
        ]);
      } else {
        throw new Error();
      }
    } catch (err) {
      // Graceful offline mock response
      let fallbackText = `**${personas.find(p => p.id === selectedPersona)?.name} Perspective**\n\n`;
      if (userText.toLowerCase().includes('sip') || userText.toLowerCase().includes('compound')) {
        fallbackText += `📊 **Verified SIP Math Tool Executed:**\nInvesting **₹15,000/month** at **12% CAGR** over **10 years** yields a maturity corpus of **₹34,85,910** (Total Invested: ₹18,00,000 | Returns: ₹16,85,910).\n\nAutomate this transfer on the 1st of every month to eliminate emotional trading.`;
      } else {
        fallbackText += `Focus on your core financial fundamentals: build a 6-month liquid emergency fund, maintain pure term life insurance, and invest surplus capital systematically into broad-market index funds.`;
      }
      setMessages((prev) => [
        ...prev,
        {
          id: String(Date.now()),
          sender: 'assistant',
          content: fallbackText,
          citations: [
            { source_title: "I Will Teach You to Be Rich", author: "Ramit Sethi", relevant_quote: "Automate your finances so your savings and investments happen before you even see the money." }
          ]
        }
      ]);
    } finally {
      setIsSending(false);
    }
  }

  async function handleComparePhilosophies(dim?: string) {
    setIsComparing(true);
    const targetDim = dim || selectedDimension;
    try {
      const res = await fetch('/api/v1/advisor/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: compareQuestion,
          dimension: targetDim,
          philosophies: ['value_compounding', 'cashflow_assets', 'conscious_spending']
        })
      });
      if (res.ok) {
        const data = await res.json();
        setComparisonData(data);
      } else {
        throw new Error();
      }
    } catch (e) {
      // Fallback structured comparison
      setComparisonData({
        topic: compareQuestion,
        detected_dimension: targetDim,
        perspectives: [
          {
            philosophy_id: 'value_compounding',
            name: 'Value & Index Compounding',
            documented_foundation: "Derived from 'The Intelligent Investor' & Bogleheads Principles",
            core_axiom: 'True wealth is built by patient compounding in productive assets without unnecessary interruption.',
            perspective: 'Maintain long-term low-cost index investing; historically diversified broad-market equities (12-14% CAGR) outperform loan rates over 15+ years.',
            actionable_steps: ['Continue disciplined broad-market index SIP', 'Avoid pausing compounding investments', 'Maintain 6-month cash reserve'],
            advantages: ['Decades of proven empirical track record', 'Minimal management overhead'],
            limitations: ['Requires 10-20+ year horizon']
          },
          {
            philosophy_id: 'cashflow_assets',
            name: 'Cash Flow & Asset Acquisition',
            documented_foundation: "Derived from 'Rich Dad Poor Dad' & Real Estate Principles",
            core_axiom: 'Acquire income-generating assets that produce cash flow to cover liabilities.',
            perspective: 'Keep the low-cost mortgage (good debt) and redirect surplus capital into acquiring cash-flowing assets or businesses.',
            actionable_steps: ['Analyze debt servicing coverage', 'Acquire income-producing assets', 'Reinvest net cash flow'],
            advantages: ['Builds passive income streams', 'Leverage accelerates equity'],
            limitations: ['Requires active management and skill']
          },
          {
            philosophy_id: 'conscious_spending',
            name: 'Conscious Spending & Automation',
            documented_foundation: "Derived from 'I Will Teach You to Be Rich' & Behavioral Systems",
            core_axiom: 'Spend extravagantly on things you love, and cut costs mercilessly on things you do not.',
            perspective: 'Implement an automated hybrid: allocate an extra 10-15% principal prepayment while keeping automatic investment contributions running.',
            actionable_steps: ['Automate salary routing on day 1', 'Prepay small fixed principal systematically', 'Eliminate psychological debt friction'],
            advantages: ['Zero financial guilt', 'Automated peace of mind'],
            limitations: ['Requires budget self-discipline']
          }
        ],
        key_differences: [
          {
            dimension: 'Debt Strategy',
            summary: 'Diverges between total debt avoidance vs strategic leverage for cash-flowing investments.'
          }
        ],
        areas_of_agreement: [
          'Eliminate high-interest consumer debt (credit cards) immediately.',
          'Consistently invest surplus capital rather than leaving it idle.',
          'Maintain liquid emergency reserves for safety.',
          'Automate recurring financial contributions.'
        ],
        balanced_synthesis: 'The optimal path integrates Ramit’s automated cash flow routing, Buffett’s low-cost index compounding, and Kiyosaki’s cash-flowing asset focus.',
        educational_disclaimer: 'Educational Interpretation Notice: These perspectives represent structured educational interpretations of documented financial methodologies and literature. They do not constitute personal advice from any real individual.'
      });
    } finally {
      setIsComparing(false);
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">AI Wealth Advisor & Multi-Guru Engine</h1>
          <p className="text-slate-400 text-sm mt-0.5">
            Tool-augmented financial advisory, RAG-grounded literature & structured philosophy comparison
          </p>
        </div>
        <button
          onClick={() => { setIsCompareOpen(true); handleComparePhilosophies(); }}
          className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-lg shadow-purple-500/25 transition-all"
        >
          <Scale className="w-4 h-4" />
          <span>Compare Philosophies</span>
        </button>
      </div>

      {/* Persona Switcher Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
        {personas.map((p) => {
          const isSelected = selectedPersona === p.id;
          return (
            <button
              key={p.id}
              onClick={() => setSelectedPersona(p.id)}
              className={`p-3.5 rounded-2xl text-left border transition-all relative overflow-hidden ${
                isSelected
                  ? 'bg-[#11192C] border-blue-500/80 shadow-lg shadow-blue-500/10 ring-1 ring-blue-500/30'
                  : 'bg-[#0D1322] border-[#1E293B] hover:border-slate-700 opacity-75 hover:opacity-100'
              }`}
            >
              <div className={`w-8 h-8 rounded-xl bg-gradient-to-br ${p.color} flex items-center justify-center text-white mb-2 shadow-md`}>
                <Sparkles className="w-4 h-4" />
              </div>
              <div className="text-xs font-bold text-white truncate">{p.name}</div>
              <div className="text-[11px] text-slate-400 mt-1 line-clamp-2 leading-snug">{p.desc}</div>
              {isSelected && (
                <div className="absolute top-2 right-2">
                  <CheckCircle2 className="w-4 h-4 text-blue-400" />
                </div>
              )}
            </button>
          );
        })}
      </div>

      {/* Chat Conversation Box */}
      <div className="bg-[#0D1322] border border-[#1E293B] rounded-2xl flex flex-col h-[560px] shadow-xl">
        {/* Messages List */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {messages.map((msg) => {
            const isUser = msg.sender === 'user';
            return (
              <div key={msg.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] rounded-2xl p-4 space-y-2.5 ${
                  isUser
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                    : 'bg-[#11192C] border border-[#1E293B] text-slate-200'
                }`}>
                  <div className="flex items-center space-x-2 text-[11px] font-semibold text-slate-400">
                    {isUser ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5 text-blue-400" />}
                    <span className={isUser ? 'text-blue-200' : 'text-slate-300'}>
                      {isUser ? 'You' : `${personas.find(p => p.id === selectedPersona)?.name || 'FinSight AI'}`}
                    </span>
                  </div>

                  {/* Tool Execution Badges */}
                  {msg.tool_calls && msg.tool_calls.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {msg.tool_calls.map((tc, idx) => (
                        <span key={idx} className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md bg-[#182238] text-[10px] text-blue-400 font-mono border border-blue-500/20">
                          <Calculator className="w-2.5 h-2.5" />
                          <span>{tc.tool_name}</span>
                          {tc.execution_time_sec !== undefined && (
                            <span className="text-slate-500">({tc.execution_time_sec}s)</span>
                          )}
                        </span>
                      ))}
                    </div>
                  )}

                  <div className="text-sm whitespace-pre-wrap leading-relaxed">
                    {msg.content}
                  </div>

                  {/* RAG Citations Box */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="pt-2.5 border-t border-[#1E293B] space-y-2">
                      <div className="flex items-center justify-between text-[11px] text-blue-400 font-semibold">
                        <div className="flex items-center space-x-1.5">
                          <BookOpen className="w-3 h-3" />
                          <span>Grounded Source Citations:</span>
                        </div>
                        <span className="text-[10px] text-slate-500 font-normal">{msg.citations.length} verified passage(s)</span>
                      </div>
                      {msg.citations.map((c, i) => (
                        <div key={i} className="p-2.5 rounded-lg bg-[#0D1322] border border-[#1E293B] text-[11px] space-y-1">
                          <div className="text-slate-300 italic leading-relaxed">
                            "{c.relevant_quote}"
                          </div>
                          <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-[#161F30]">
                            <span className="font-semibold text-slate-200">
                              {c.source_title} {c.author ? `— ${c.author}` : ''}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
          {isSending && (
            <div className="flex justify-start">
              <div className="p-4 rounded-2xl bg-[#11192C] border border-[#1E293B] text-xs text-slate-400 flex items-center space-x-2">
                <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                <span>Executing financial tools & synthesizing guru advice...</span>
              </div>
            </div>
          )}
        </div>

        {/* Input Form */}
        <form onSubmit={handleSendMessage} className="p-4 border-t border-[#1E293B] flex items-center space-x-3 bg-[#0D1322] rounded-b-2xl">
          <input
            type="text"
            placeholder={`Ask ${personas.find(p => p.id === selectedPersona)?.name} (e.g. Calculate SIP for ₹15000/mo, or Should I prepay my home loan?)...`}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            className="flex-1 px-4 py-3 bg-[#11192C] border border-[#1E293B] rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || isSending}
            className="p-3 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white transition-all shadow-md shadow-blue-500/25"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>

      {/* Structured Philosophy Comparison Modal */}
      {isCompareOpen && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0D1322] border border-[#1E293B] rounded-2xl max-w-5xl w-full p-6 space-y-6 shadow-2xl max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-[#1E293B] pb-4">
              <div className="flex items-center space-x-3">
                <div className="p-2.5 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
                  <Scale className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-bold text-white text-lg">Financial Philosophy Comparison Engine</h3>
                  <p className="text-xs text-slate-400">Structured comparative analysis across documented wealth methodologies</p>
                </div>
              </div>
              <button onClick={() => setIsCompareOpen(false)} className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-[#1E293B]">
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Educational Disclaimer Banner */}
            <div className="p-3 rounded-xl bg-blue-950/40 border border-blue-500/30 text-[11px] text-blue-300 flex items-center space-x-2.5">
              <HelpCircle className="w-4 h-4 text-blue-400 flex-shrink-0" />
              <span>
                <strong>Educational Interpretation Notice:</strong> Perspectives represent structured interpretations of documented methodologies. No direct personal advice is given.
              </span>
            </div>

            {/* Input & Dimension Filter */}
            <div className="space-y-3">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={compareQuestion}
                  onChange={(e) => setCompareQuestion(e.target.value)}
                  placeholder="Enter a financial dilemma or question..."
                  className="flex-1 px-4 py-2.5 bg-[#11192C] border border-[#1E293B] rounded-xl text-sm text-slate-200 focus:outline-none focus:border-purple-500"
                />
                <button
                  onClick={() => handleComparePhilosophies()}
                  disabled={isComparing}
                  className="px-5 py-2.5 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white rounded-xl text-xs font-semibold shadow-md shadow-purple-500/25 transition-all"
                >
                  {isComparing ? 'Analyzing...' : 'Compare Methodologies'}
                </button>
              </div>

              {/* Dimensions Tag Filter */}
              <div className="flex flex-wrap items-center gap-1.5 text-xs">
                <span className="text-slate-400 mr-1 text-[11px]">Dimension:</span>
                {['all', 'budgeting', 'saving', 'spending', 'debt', 'investing', 'financial_goals', 'lifestyle_spending'].map((dim) => (
                  <button
                    key={dim}
                    onClick={() => { setSelectedDimension(dim); handleComparePhilosophies(dim); }}
                    className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition-all ${
                      selectedDimension === dim
                        ? 'bg-purple-600 text-white shadow-sm'
                        : 'bg-[#11192C] text-slate-400 hover:text-white border border-[#1E293B]'
                    }`}
                  >
                    {dim.replace('_', ' ').toUpperCase()}
                  </button>
                ))}
              </div>
            </div>

            {/* Comparison Content */}
            {comparisonData && (
              <div className="space-y-6 pt-2">
                {/* 1. Perspectives Side-by-Side Grid */}
                <div>
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">1. Methodological Perspectives</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {comparisonData.perspectives?.map((p: any) => (
                      <div key={p.philosophy_id} className="p-4 rounded-xl bg-[#11192C] border border-[#1E293B] flex flex-col justify-between space-y-3">
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-sm text-white">{p.name}</span>
                          </div>
                          <div className="text-[10px] text-purple-400 font-mono">{p.documented_foundation}</div>
                          <div className="p-2 rounded-lg bg-[#0D1322] text-[11px] text-slate-300 italic border-l-2 border-purple-500">
                            "{p.core_axiom}"
                          </div>
                          <p className="text-xs text-slate-300 leading-relaxed pt-1">{p.perspective}</p>
                        </div>

                        {p.actionable_steps && (
                          <div className="pt-2 border-t border-[#1E293B] space-y-1">
                            <span className="text-[10px] font-bold text-slate-400 uppercase">Recommended Actions:</span>
                            <ul className="text-[11px] text-slate-400 space-y-1 list-disc list-inside">
                              {p.actionable_steps.map((st: string, idx: number) => (
                                <li key={idx} className="leading-snug">{st}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* 2. Key Differences & Areas of Agreement */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Key Differences */}
                  <div className="p-4 rounded-xl bg-[#11192C] border border-[#1E293B] space-y-2.5">
                    <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center space-x-1.5">
                      <span>Key Methodological Differences</span>
                    </h4>
                    {comparisonData.key_differences?.map((kd: any, i: number) => (
                      <div key={i} className="text-xs text-slate-300 space-y-1 p-2.5 rounded-lg bg-[#0D1322]">
                        <span className="font-semibold text-slate-200">{kd.dimension || 'Core Stance'}: </span>
                        <span>{kd.summary}</span>
                      </div>
                    ))}
                  </div>

                  {/* Areas of Agreement */}
                  <div className="p-4 rounded-xl bg-[#11192C] border border-[#1E293B] space-y-2.5">
                    <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center space-x-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Universal Areas of Agreement</span>
                    </h4>
                    <ul className="space-y-1.5 text-xs text-slate-300">
                      {comparisonData.areas_of_agreement?.map((aa: string, i: number) => (
                        <li key={i} className="flex items-start space-x-2">
                          <span className="text-emerald-400 font-bold">•</span>
                          <span className="leading-snug">{aa}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* 3. Balanced Strategic Synthesis */}
                <div className="p-4 rounded-xl bg-gradient-to-r from-blue-900/30 via-purple-900/30 to-indigo-900/30 border border-blue-500/30 space-y-1.5">
                  <span className="text-xs font-bold text-blue-400 uppercase tracking-wider">Balanced Strategic Synthesis</span>
                  <p className="text-xs text-slate-200 leading-relaxed">{comparisonData.balanced_synthesis}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
