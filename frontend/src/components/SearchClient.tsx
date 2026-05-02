'use client';

import { useState, useMemo } from 'react';
import Link from 'next/link';
import { Opportunity } from '@/lib/data';
import { cn } from '@/lib/utils';
import { Search, ChevronDown, Check, X, Filter, Sparkles, FileText, Download } from 'lucide-react';
import RecipientCard from './RecipientCard';

interface Report {
  name: string;
  url: string;
  type: string;
}

export default function SearchClient({
  initialOpportunities,
  initialReports
}: {
  initialOpportunities: Opportunity[],
  initialReports: Report[]
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [showNewOnly, setShowNewOnly] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const categories = ['Equity', 'Grants', 'Tenders'];

  const filteredOpportunities = useMemo(() => {
    return initialOpportunities.filter((opp) => {
      const matchesSearch =
        opp.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        opp.institution.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesCategory = !selectedCategory || opp.category === selectedCategory;
      const matchesNew = !showNewOnly || opp.new;

      return matchesSearch && matchesCategory && matchesNew;
    });
  }, [initialOpportunities, searchQuery, selectedCategory, showNewOnly]);

  return (
    <div className="min-h-screen flex flex-col bg-[#0f1115] text-gray-200 font-sans">
      <main className="flex-grow max-w-4xl mx-auto w-full px-6 py-16">
        {/* Logo */}
        <div className="flex flex-col items-center mb-12">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-8 h-8 text-white" />
            <h1 className="text-4xl font-bold tracking-tight text-white">
              Rokct Nexus
            </h1>
          </div>
          <p className="text-gray-500 text-sm italic">Premium Opportunity Intelligence</p>
        </div>

        {/* Chat-box Search Container */}
        <div className="bg-[#1a1d23] rounded-3xl border border-gray-800 shadow-2xl overflow-hidden transition-all focus-within:border-gray-700 focus-within:ring-2 focus-within:ring-white/5">
          <div className="p-6 space-y-6">
            <div className="flex items-center gap-4 bg-[#0f1115] rounded-2xl px-5 py-4 border border-gray-800 transition-all focus-within:bg-black/40">
              <Search className="w-6 h-6 text-gray-600" />

              <div className="flex-grow flex items-center gap-2 flex-wrap">
                {selectedCategory && (
                  <div className="flex items-center gap-1.5 bg-white/10 text-white px-3 py-1.5 rounded-xl text-xs font-bold border border-white/10 group animate-in fade-in zoom-in duration-200">
                    <span>{selectedCategory}</span>
                    <button
                      onClick={() => setSelectedCategory(null)}
                      className="p-0.5 hover:bg-white/20 rounded-md transition-colors"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                )}
                <input
                  type="text"
                  placeholder={selectedCategory ? `Search in ${selectedCategory}...` : "Search premium opportunities..."}
                  className="bg-transparent border-none outline-none flex-grow min-w-[200px] text-white placeholder-gray-600 text-lg"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>

              {/* Category Dropdown inside Chat-box */}
              <div className="relative">
                <button
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all border",
                    selectedCategory
                      ? "bg-white text-black border-white"
                      : "bg-[#1a1d23] text-gray-400 border-gray-700 hover:text-white hover:border-gray-500"
                  )}
                >
                  {selectedCategory || 'Categories'}
                  <ChevronDown className={cn("w-4 h-4 transition-transform duration-300", isDropdownOpen && "rotate-180")} />
                </button>

                {isDropdownOpen && (
                  <>
                    <div
                      className="fixed inset-0 z-40"
                      onClick={() => setIsDropdownOpen(false)}
                    />
                    <div className="absolute right-0 mt-3 w-56 bg-[#1a1d23] border border-gray-700 rounded-2xl shadow-2xl z-50 overflow-hidden p-2 animate-in fade-in slide-in-from-top-2 duration-200">
                      <button
                        onClick={() => { setSelectedCategory(null); setIsDropdownOpen(false); }}
                        className="w-full text-left px-4 py-3 text-sm rounded-xl hover:bg-white/5 flex items-center justify-between transition-colors mb-1"
                      >
                        All Portals
                        {!selectedCategory && <Check className="w-4 h-4 text-white" />}
                      </button>
                      <div className="h-px bg-gray-800 my-1 mx-2" />
                      {categories.map((cat) => (
                        <button
                          key={cat}
                          onClick={() => { setSelectedCategory(cat); setIsDropdownOpen(false); }}
                          className={cn(
                            "w-full text-left px-4 py-3 text-sm rounded-xl flex items-center justify-between transition-colors",
                            selectedCategory === cat ? "bg-white/10 text-white" : "text-gray-400 hover:bg-white/5 hover:text-white"
                          )}
                        >
                          {cat}
                          {selectedCategory === cat && <Check className="w-4 h-4 text-white" />}
                        </button>
                      ))}
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Bottom Filters Bar */}
            <div className="flex items-center justify-between bg-[#0f1115]/30 rounded-2xl p-2 px-4 border border-gray-800/30">
              <div className="flex items-center gap-6">
                <div className="flex items-center gap-2 text-[10px] text-gray-500 uppercase tracking-widest font-black opacity-50">
                  <Filter className="w-3 h-3" /> Filters
                </div>

                <div className="flex items-center gap-4">
                  <label className="flex items-center gap-3 text-xs text-gray-400 cursor-pointer group hover:text-white transition-colors">
                    <div className={cn(
                      "w-5 h-5 rounded-lg border flex items-center justify-center transition-all duration-300",
                      showNewOnly ? "bg-white border-white scale-110" : "border-gray-700 group-hover:border-gray-500"
                    )}>
                      {showNewOnly && <Check className="w-3.5 h-3.5 text-black font-bold" />}
                    </div>
                    <input
                      type="checkbox"
                      checked={showNewOnly}
                      onChange={(e) => setShowNewOnly(e.target.checked)}
                      className="hidden"
                    />
                    <span className="font-semibold tracking-wide">Newly Listed</span>
                  </label>

                  {/* Additional dynamic filter hints could go here */}
                </div>
              </div>

              {selectedCategory && (
                <div className="text-[10px] text-gray-600 font-bold italic animate-pulse">
                  Viewing verified {selectedCategory.toLowerCase()} database
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Reports Download Section */}
        {initialReports.length > 0 && (
          <div className="mt-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {initialReports.map((report) => (
              <a
                key={report.name}
                href={report.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-between p-4 bg-[#1a1d23] rounded-2xl border border-gray-800 hover:border-gray-600 transition-all group"
              >
                <div className="flex items-center gap-3">
                  <div className={cn(
                    "p-2 rounded-lg",
                    report.type === 'PDF' ? "bg-red-900/20 text-red-400" : "bg-green-900/20 text-green-400"
                  )}>
                    <FileText className="w-4 h-4" />
                  </div>
                  <div className="flex flex-col">
                    <span className="text-xs font-bold text-white truncate max-w-[150px]">
                      {report.name.replace(/_/g, ' ')}
                    </span>
                    <span className="text-[10px] text-gray-500 uppercase font-black">
                      {report.type} Report
                    </span>
                  </div>
                </div>
                <Download className="w-4 h-4 text-gray-600 group-hover:text-white transition-colors" />
              </a>
            ))}
          </div>
        )}

        {/* Results */}
        <div className="mt-12 space-y-8 mb-20">
          {filteredOpportunities.length > 0 ? (
            <>
              <div className="flex justify-between items-center text-sm text-gray-500 border-b border-gray-800 pb-4">
                <span>Showing {filteredOpportunities.length} verified results</span>
                <span className="text-gray-600">Secure Database</span>
              </div>
              <div className="grid gap-6">
                {filteredOpportunities.map((opp) => (
                  <Link
                    key={opp.id}
                    href={`/opportunity/${opp.id}`}
                    className="group block bg-[#16191f] p-6 rounded-2xl border border-gray-800 hover:border-gray-600 hover:bg-[#1a1d23] transition-all"
                  >
                    <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                      <div className="space-y-2">
                        <div className="text-xs font-bold text-gray-500 uppercase tracking-wider">
                          {opp.institution}
                        </div>
                        <h2 className="text-xl font-semibold text-white group-hover:text-blue-400 transition-colors">
                          {opp.title}
                        </h2>
                        <div className="flex items-center gap-3">
                          <span className={cn(
                            "px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-tighter",
                            opp.category === 'Equity' ? "bg-purple-900/30 text-purple-400 border border-purple-800/50" :
                            opp.category === 'Grants' ? "bg-green-900/30 text-green-400 border border-green-800/50" :
                            "bg-orange-900/30 text-orange-400 border border-orange-800/50"
                          )}>
                            {opp.category}
                          </span>
                          <span className="text-xs text-gray-500">
                            Deadline: {opp.closing_date}
                          </span>
                          {opp.new && (
                            <span className="text-[10px] bg-red-900/20 text-red-400 border border-red-900/50 px-2 py-0.5 rounded-full font-bold">NEW</span>
                          )}
                        </div>
                      </div>
                      <div className="hidden md:block">
                        <div className="bg-[#0f1115] border border-gray-800 px-4 py-2 rounded-xl text-xs font-semibold text-gray-400 group-hover:border-gray-600 group-hover:text-white transition-all">
                          View Details
                        </div>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </>
          ) : (
            <div className="text-center py-20 bg-[#16191f] rounded-3xl border border-gray-800 border-dashed">
              <p className="text-gray-500 text-lg">No matches found in our verified database.</p>
              <button
                onClick={() => { setSearchQuery(''); setSelectedCategory(null); setShowNewOnly(false); }}
                className="mt-4 text-blue-400 hover:underline text-sm"
              >
                Reset all filters
              </button>
            </div>
          )}
        </div>

        {/* Join Registry Section */}
        <div className="mt-20 border-t border-gray-800 pt-12">
          <div className="max-w-2xl mx-auto">
            <RecipientCard />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="max-w-4xl mx-auto w-full px-6 py-12 border-t border-gray-800 text-center space-y-4">
        <div className="flex items-center justify-center gap-2 text-white/50 grayscale hover:grayscale-0 transition-all">
          <Sparkles className="w-5 h-5" />
          <span className="font-bold tracking-tight">Rokct Nexus</span>
        </div>
        <p className="text-xs text-gray-600 leading-relaxed">
          The information contained in this registry is for informational purposes only. Verified opportunities are vetted at the time of entry.
          Nexus is a platform by Rokct Intelligence.
        </p>
        <p className="text-xs text-gray-500">
          Copyright © 2024 Rokct Intelligence (pty) Ltd. All rights reserved.
        </p>
      </footer>
    </div>
  );
}
