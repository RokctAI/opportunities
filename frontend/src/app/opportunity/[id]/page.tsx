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
    <main className="max-w-4xl mx-auto px-4 py-12">
      <Link
        href="/"
        className="text-blue-600 hover:underline mb-8 inline-block"
      >
        ← Back to search
      </Link>

      <article>
        <header className="mb-8 pb-8 border-b border-gray-100">
          <div className="flex items-center gap-3 mb-4">
            <span className={cn(
              "px-3 py-1 rounded-full text-sm font-medium",
              opportunity.category === 'Equity' ? "bg-purple-100 text-purple-700" :
              opportunity.category === 'Grants' ? "bg-green-100 text-green-700" :
              "bg-orange-100 text-orange-700"
            )}>
              {opportunity.category}
            </span>
            {opportunity.verified && (
              <span className="text-blue-600 text-sm font-medium">✓ Verified</span>
            )}
            {opportunity.new && (
              <span className="text-red-600 text-sm font-medium font-bold italic">NEW</span>
            )}
          </div>

          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            {opportunity.title}
          </h1>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-gray-600">
            <div>
              <span className="font-semibold text-gray-900">Institution:</span> {opportunity.institution}
            </div>
            <div>
              <span className="font-semibold text-gray-900">Closing Date:</span> {opportunity.closing_date}
            </div>
            {opportunity.link && opportunity.link !== '#' && (
              <div className="md:col-span-2">
                <span className="font-semibold text-gray-900">Official Link:</span>{' '}
                <a
                  href={opportunity.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline break-all"
                >
                  {opportunity.link}
                </a>
              </div>
            )}
          </div>
        </header>

        <div
          className="prose prose-blue max-w-none
            prose-headings:text-gray-900 prose-headings:font-bold
            prose-p:text-gray-700 prose-li:text-gray-700
            prose-a:text-blue-600 prose-a:no-underline hover:prose-a:underline"
          dangerouslySetInnerHTML={{ __html: opportunity.contentHtml }}
        />
      </article>
    </main>
  );
}
