'use client';

import { useState, useMemo, useEffect } from 'react';
import Link from 'next/link';
import { Opportunity } from '@/lib/data';
import { cn } from '@/lib/utils';

export default function SearchPage() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [showVerifiedOnly, setShowVerifiedOnly] = useState(false);
  const [showNewOnly, setShowNewOnly] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetch('/data.json')
      .then((res) => res.json())
      .then((data) => {
        setOpportunities(data.opportunities);
        setIsLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load data', err);
        setIsLoading(false);
      });
  }, []);

  const filteredOpportunities = useMemo(() => {
    return opportunities.filter((opp) => {
      const matchesSearch =
        opp.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        opp.institution.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesCategory =
        selectedCategories.length === 0 || selectedCategories.includes(opp.category);

      const matchesVerified = !showVerifiedOnly || opp.verified;
      const matchesNew = !showNewOnly || opp.new;

      return matchesSearch && matchesCategory && matchesVerified && matchesNew;
    });
  }, [opportunities, searchQuery, selectedCategories, showVerifiedOnly, showNewOnly]);

  const toggleCategory = (category: string) => {
    setSelectedCategories((prev) =>
      prev.includes(category)
        ? prev.filter((c) => c !== category)
        : [...prev, category]
    );
  };

  return (
    <main className="max-w-4xl mx-auto px-4 py-8">
      {/* Header / Logo */}
      <div className="flex flex-col items-center mb-8">
        <h1 className="text-6xl font-bold mb-8">
          <span className="text-blue-500">O</span>
          <span className="text-red-500">p</span>
          <span className="text-yellow-500">p</span>
          <span className="text-blue-500">s</span>
          <span className="text-green-500">e</span>
          <span className="text-red-500">a</span>
          <span className="text-blue-500">r</span>
          <span className="text-green-500">c</span>
          <span className="text-yellow-500">h</span>
        </h1>

        {/* Search Bar */}
        <div className="w-full relative max-w-2xl">
          <input
            type="text"
            placeholder="Search opportunities..."
            className="w-full px-6 py-3 rounded-full border border-gray-200 shadow-sm focus:shadow-md focus:outline-none transition-shadow"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 justify-center mb-12">
        {['Equity', 'Grants', 'Tenders'].map((cat) => (
          <button
            key={cat}
            onClick={() => toggleCategory(cat)}
            className={cn(
              "px-4 py-2 rounded-full border text-sm transition-colors",
              selectedCategories.includes(cat)
                ? "bg-blue-500 text-white border-blue-500"
                : "bg-white text-gray-700 border-gray-200 hover:bg-gray-50"
            )}
          >
            {cat}
          </button>
        ))}
        <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
          <input
            type="checkbox"
            checked={showVerifiedOnly}
            onChange={(e) => setShowVerifiedOnly(e.target.checked)}
            className="rounded text-blue-500"
          />
          Verified
        </label>
        <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
          <input
            type="checkbox"
            checked={showNewOnly}
            onChange={(e) => setShowNewOnly(e.target.checked)}
            className="rounded text-blue-500"
          />
          New
        </label>
      </div>

      {/* Results */}
      <div className="space-y-6">
        {isLoading ? (
          <div className="text-center py-10 text-gray-500">Loading opportunities...</div>
        ) : filteredOpportunities.length > 0 ? (
          <>
            <div className="text-sm text-gray-500 mb-4">
              About {filteredOpportunities.length} results
            </div>
            {filteredOpportunities.map((opp) => (
              <div key={opp.id} className="group">
                <div className="text-sm text-gray-600 truncate mb-1">
                  {opp.institution}
                </div>
                <Link
                  href={`/opportunity/${opp.id}`}
                  className="text-xl text-blue-800 hover:underline group-hover:text-blue-900 block mb-1"
                >
                  {opp.title}
                </Link>
                <div className="flex items-center gap-3 text-sm">
                  <span className={cn(
                    "px-2 py-0.5 rounded text-xs font-medium",
                    opp.category === 'Equity' ? "bg-purple-100 text-purple-700" :
                    opp.category === 'Grants' ? "bg-green-100 text-green-700" :
                    "bg-orange-100 text-orange-700"
                  )}>
                    {opp.category}
                  </span>
                  <span className="text-gray-500">
                    Closing: {opp.closing_date}
                  </span>
                  {opp.verified && (
                    <span className="text-blue-600 font-medium">✓ Verified</span>
                  )}
                  {opp.new && (
                    <span className="text-red-600 font-medium">New</span>
                  )}
                </div>
              </div>
            ))}
          </>
        ) : (
          <div className="text-center py-10 text-gray-500">
            No results found for "{searchQuery}"
          </div>
        )}
      </div>
    </main>
  );
}
