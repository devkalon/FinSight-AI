'use client';

import React from 'react';
import Link from 'next/link';
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
    group: 'Management',
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
    group: 'Analytics & Models',
    items: [
      { name: 'Analytics', href: '/analytics', icon: TrendingUp },
      { name: 'Forecast', href: '/forecast', icon: LineChart, badge: 'ML' },
      { name: 'What-If Simulator', href: '/simulator', icon: Sliders },
    ]
  },
  {
    group: 'Intelligence & Reports',
    items: [
      { name: 'Insights & Health', href: '/insights', icon: Sparkles },
      { name: 'AI Advisor', href: '/advisor', icon: Bot, badge: 'Agent' },
      { name: 'Philosophies', href: '/philosophies', icon: Scale },
      { name: 'Monthly Report', href: '/reports', icon: FileText, badge: 'PDF' },
      { name: 'Documents & RAG', href: '/documents', icon: ShieldCheck },
    ]
  },
  {
    group: 'Account',
    items: [
      { name: 'Settings & Privacy', href: '/settings', icon: Settings },
    ]
  }
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-[#0A0E1A] border-r border-[#1D263B] flex flex-col h-screen fixed left-0 top-0 z-40">
      {/* Brand Header */}
      <div className="p-5 border-b border-[#1D263B] flex items-center space-x-3">
        <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center shadow-md shadow-blue-600/30">
          <Zap className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="font-bold text-base text-white tracking-tight">FinSight <span className="text-blue-400">AI</span></h1>
          <p className="text-[11px] text-slate-400 font-medium">Wealth Intelligence</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-5 overflow-y-auto custom-scrollbar">
        {navGroups.map((group, gIdx) => (
          <div key={gIdx} className="space-y-1">
            <div className="px-3 pb-1 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
              {group.group}
            </div>
            {group.items.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || (item.href === '/' && pathname === '/dashboard');
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center justify-between px-3 py-2 rounded-xl text-xs font-semibold transition-all duration-150 ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-sm shadow-blue-500/25'
                      : 'text-slate-400 hover:text-slate-100 hover:bg-[#12192B]'
                  }`}
                >
                  <div className="flex items-center space-x-2.5">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                    <span>{item.name}</span>
                  </div>
                  {item.badge && (
                    <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold ${
                      isActive ? 'bg-white/20 text-white' : 'bg-[#182238] text-slate-300 border border-[#23304E]'
                    }`}>
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
      <div className="p-3 m-3 rounded-xl bg-[#0F1626] border border-[#1D263B]">
        <div className="flex items-center space-x-1.5 text-emerald-400 text-[11px] font-bold mb-0.5">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Deterministic Audit Guarantee</span>
        </div>
        <p className="text-[10px] text-slate-400 leading-tight">
          Financial numbers computed by verifiable backend algorithms.
        </p>
      </div>
    </aside>
  );
}
