'use client';

import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Receipt,
  UploadCloud,
  PiggyBank,
  Target,
  RefreshCcw,
  TrendingUp,
  LineChart,
  Sliders,
  Sparkles,
  Bot,
  Scale,
  FileText,
  ShieldCheck,
  Settings,
  Zap
} from 'lucide-react';

interface NavGroup {
  group: string;
  items: {
    name: string;
    href: string;
    icon: React.ElementType;
    badge?: string;
  }[];
}

const navGroups: NavGroup[] = [
  {
    group: 'Ledger & Operations',
    items: [
      { name: 'Dashboard', href: '/', icon: LayoutDashboard },
      { name: 'Transactions', href: '/transactions', icon: Receipt },
      { name: 'Upload & OCR', href: '/upload', icon: UploadCloud, badge: 'OCR' },
      { name: 'Budgets & Limits', href: '/budgets', icon: PiggyBank },
      { name: 'Goals & SIPs', href: '/goals', icon: Target },
      { name: 'Subscriptions', href: '/subscriptions', icon: RefreshCcw },
    ]
  },
  {
    group: 'Predictive & Strategy',
    items: [
      { name: 'Analytics', href: '/analytics', icon: TrendingUp },
      { name: 'Forecast', href: '/forecast', icon: LineChart, badge: 'ML' },
      { name: 'What-If Simulator', href: '/simulator', icon: Sliders },
    ]
  },
  {
    group: 'Intelligence & Audit',
    items: [
      { name: 'Health & Insights', href: '/insights', icon: Sparkles },
      { name: 'AI Advisor', href: '/advisor', icon: Bot, badge: 'Agent' },
      { name: 'Philosophies', href: '/philosophies', icon: Scale },
      { name: 'Monthly Report', href: '/reports', icon: FileText, badge: 'PDF' },
      { name: 'Documents & RAG', href: '/documents', icon: ShieldCheck },
    ]
  },
  {
    group: 'Configuration',
    items: [
      { name: 'Settings & Security', href: '/settings', icon: Settings },
    ]
  }
];

export function Sidebar({ isOpen, onClose }: { isOpen?: boolean; onClose?: () => void }) {
  const pathname = usePathname();

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 bg-black/60 backdrop-blur-xs z-40 lg:hidden"
        />
      )}

      <aside
        className={`w-64 bg-[#0B1120] border-r border-[#1E293B] flex flex-col h-screen fixed left-0 top-0 z-50 transition-transform duration-200 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="h-16 px-5 border-b border-[#1E293B] flex items-center justify-between">
          <Link href="/" className="flex items-center group">
            <Image
              src="/logo.png"
              alt="FinSight AI"
              width={140}
              height={38}
              className="object-contain"
              priority
            />
          </Link>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 px-3 py-4 space-y-5 overflow-y-auto custom-scrollbar">
          {navGroups.map((group, gIdx) => (
            <div key={gIdx} className="space-y-0.5">
              <div className="px-3 pb-1.5 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                {group.group}
              </div>
              {group.items.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href || (item.href === '/' && pathname === '/dashboard');
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={onClose}
                    className={`flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                      isActive
                        ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30 font-semibold'
                        : 'text-slate-300 hover:text-white hover:bg-[#1E293B] border border-transparent'
                    }`}
                  >
                    <div className="flex items-center space-x-2.5">
                      <Icon className={`w-4 h-4 ${isActive ? 'text-amber-400' : 'text-slate-400'}`} />
                      <span>{item.name}</span>
                    </div>
                    {item.badge && (
                      <span
                        className={`text-[9px] px-1.5 py-0.2 rounded font-semibold tracking-wide ${
                          isActive
                            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                            : 'bg-[#272F42] text-slate-300 border border-[#1E293B]'
                        }`}
                      >
                        {item.badge}
                      </span>
                    )}
                  </Link>
                );
              })}
            </div>
          ))}
        </nav>

        {/* Footer Security Badge */}
        <div className="p-3 m-3 rounded-lg bg-[#222735] border border-[#1E293B]">
          <div className="flex items-center space-x-1.5 text-emerald-400 text-[11px] font-semibold mb-0.5">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Deterministic Math Guard</span>
          </div>
          <p className="text-[10px] text-slate-400 leading-tight">
            Zero LLM financial hallucinations. Scoped tenant isolation.
          </p>
        </div>
      </aside>
    </>
  );
}
