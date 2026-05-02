import Link from 'next/link';
import { getOpportunities, getOpportunityDetail } from '@/lib/data';
import { notFound } from 'next/navigation';
import { cn } from '@/lib/utils';

export async function generateStaticParams() {
  const opportunities = getOpportunities();
  return opportunities.map((opp) => ({
    id: opp.id,
  }));
}

import { Sparkles, Check } from 'lucide-react';

export default async function OpportunityDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const opportunity = await getOpportunityDetail(id);

  if (!opportunity) {
    notFound();
  }

  return (
    <div className="min-h-screen bg-[#0f1115] text-gray-200 font-sans">
      <main className="max-w-4xl mx-auto px-6 py-16">
        <Link
          href="/"
          className="group flex items-center gap-2 text-gray-500 hover:text-white mb-12 transition-colors"
        >
          <span className="text-lg group-hover:-translate-x-1 transition-transform">←</span>
          <span>Return to Nexus</span>
        </Link>

        <article className="bg-[#16191f] rounded-3xl border border-gray-800 overflow-hidden shadow-2xl">
          <header className="p-8 md:p-12 border-b border-gray-800 bg-[#1a1d23]">
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-3">
                <span className={cn(
                  "px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider",
                  opportunity.category === 'Equity' ? "bg-purple-900/30 text-purple-400 border border-purple-800/50" :
                  opportunity.category === 'Grants' ? "bg-green-900/30 text-green-400 border border-green-800/50" :
                  "bg-orange-900/30 text-orange-400 border border-orange-800/50"
                )}>
                  {opportunity.category}
                </span>
                {opportunity.verified && (
                  <span className="text-blue-400 text-xs font-semibold flex items-center gap-1">
                    <Check className="w-3 h-3" /> Verified
                  </span>
                )}
              </div>
              <Sparkles className="w-6 h-6 text-white/20" />
            </div>

            <h1 className="text-3xl md:text-5xl font-bold text-white mb-8 leading-tight">
              {opportunity.title}
            </h1>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-y-6 gap-x-12 p-6 rounded-2xl bg-[#0f1115]/50 border border-gray-800/50">
              <div className="space-y-1">
                <div className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Institution</div>
                <div className="text-gray-200 font-medium">{opportunity.institution}</div>
              </div>
              <div className="space-y-1">
                <div className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Closing Date</div>
                <div className="text-gray-200 font-medium">{opportunity.closing_date}</div>
              </div>
              {opportunity.link && opportunity.link !== '#' && (
                <div className="md:col-span-2 space-y-1">
                  <div className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Official Portal</div>
                  <a
                    href={opportunity.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300 hover:underline break-all font-medium transition-colors"
                  >
                    {opportunity.link}
                  </a>
                </div>
              )}
            </div>
          </header>

          <div className="p-8 md:p-12">
            <div
              className="prose prose-invert max-w-none
                prose-headings:text-white prose-headings:font-bold prose-headings:tracking-tight
                prose-p:text-gray-400 prose-p:leading-relaxed
                prose-li:text-gray-400
                prose-strong:text-gray-200
                prose-a:text-blue-400 prose-a:no-underline hover:prose-a:underline transition-all"
              dangerouslySetInnerHTML={{ __html: opportunity.contentHtml }}
            />
          </div>
        </article>

        <footer className="mt-16 text-center">
           <div className="flex items-center justify-center gap-2 text-white/20 mb-4">
            <Sparkles className="w-4 h-4" />
            <span className="text-sm font-bold tracking-tight">Rokct Nexus</span>
          </div>
          <p className="text-[10px] text-gray-600 uppercase tracking-[0.2em]">
            Copyright © 2024 Rokct Intelligence (pty) Ltd
          </p>
        </footer>
      </main>
    </div>
  );
}
