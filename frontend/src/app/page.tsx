import { getOpportunities, getPublishedReports } from '@/lib/data';
import SearchClient from '@/components/SearchClient';

export default async function SearchPage() {
  const opportunities = getOpportunities();
  const reports = getPublishedReports();

  return <SearchClient initialOpportunities={opportunities} initialReports={reports} />;
}
