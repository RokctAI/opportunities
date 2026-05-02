import { Opportunity } from './data';

export function filterOpportunities(
  opportunities: Opportunity[],
  query: string,
  categories: string[],
  verifiedOnly: boolean,
  newOnly: boolean
) {
  return opportunities.filter((opp) => {
    const matchesSearch =
      opp.title.toLowerCase().includes(query.toLowerCase()) ||
      opp.institution.toLowerCase().includes(query.toLowerCase());

    const matchesCategory =
      categories.length === 0 || categories.includes(opp.category);

    const matchesVerified = !verifiedOnly || opp.verified;
    const matchesNew = !newOnly || opp.new;

    return matchesSearch && matchesCategory && matchesVerified && matchesNew;
  });
}
