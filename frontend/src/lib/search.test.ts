import { filterOpportunities } from './search';
import { Opportunity } from './data';

const mockOpportunities: Opportunity[] = [
  {
    id: '1',
    category: 'Equity',
    title: 'Startup Fund',
    institution: 'VC Alpha',
    closing_date: '2026-01-01',
    link: '#',
    path: 'path/1',
    verified: true,
    new: true,
  },
  {
    id: '2',
    category: 'Grants',
    title: 'Research Grant',
    institution: 'Gov Beta',
    closing_date: '2026-02-02',
    link: '#',
    path: 'path/2',
    verified: false,
    new: true,
  },
  {
    id: '3',
    category: 'Tenders',
    title: 'Construction Project',
    institution: 'City Gamma',
    closing_date: '2026-03-03',
    link: '#',
    path: 'path/3',
    verified: true,
    new: false,
  },
];

function runTests() {
  console.log('Running Search Filter Tests...');

  // Test 1: Search query
  const test1 = filterOpportunities(mockOpportunities, 'Startup', [], false, false);
  console.assert(test1.length === 1 && test1[0].id === '1', 'Test 1 Failed');

  // Test 2: Category filter
  const test2 = filterOpportunities(mockOpportunities, '', ['Grants'], false, false);
  console.assert(test2.length === 1 && test2[0].id === '2', 'Test 2 Failed');

  // Test 3: Verified filter
  const test3 = filterOpportunities(mockOpportunities, '', [], true, false);
  console.assert(test3.length === 2, 'Test 3 Failed');

  // Test 4: New filter
  const test4 = filterOpportunities(mockOpportunities, '', [], false, true);
  console.assert(test4.length === 2, 'Test 4 Failed');

  // Test 5: Combined filters
  const test5 = filterOpportunities(mockOpportunities, 'Alpha', ['Equity'], true, true);
  console.assert(test5.length === 1 && test5[0].id === '1', 'Test 5 Failed');

  console.log('All Search Filter Tests Passed!');
}

runTests();
