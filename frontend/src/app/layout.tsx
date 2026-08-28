import type { Metadata } from 'next';
import './globals.css';
import { Sidebar } from '@/components/Sidebar';
import { Navbar } from '@/components/Navbar';
import { AuthProvider } from '@/context/AuthContext';

export const metadata: Metadata = {
  title: 'FinSight AI — Wealth Intelligence & Personal Finance Platform',
  description: 'AI-Powered Personal Finance & Wealth Management Platform with OCR, RAG, Multi-Guru Advisor and Predictive Analytics.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#090D16] text-slate-100 min-h-screen flex">
        <AuthProvider>
          <Sidebar />
          <div className="flex-1 ml-64 flex flex-col min-h-screen">
            <Navbar />
            <main className="flex-1 p-8 pt-24 max-w-7xl w-full mx-auto">
              {children}
            </main>
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}
