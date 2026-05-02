import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';
import { remark } from 'remark';
import remarkRehype from 'remark-rehype';
import rehypeSanitize from 'rehype-sanitize';
import rehypeStringify from 'rehype-stringify';

const repoRoot = path.join(process.cwd(), '..');
const dataFile = path.join(repoRoot, 'docs', 'data.json');

export interface Opportunity {
  id: string;
  category: string;
  title: string;
  institution: string;
  closing_date: string;
  link: string;
  path: string;
  verified: boolean;
  new: boolean;
}

export interface DataJson {
  last_updated: string;
  stats: Record<string, { total: number; verified: number; new: number }>;
  opportunities: Opportunity[];
}

export function getOpportunities(): Opportunity[] {
  if (!fs.existsSync(dataFile)) {
    return [];
  }
  const fileContents = fs.readFileSync(dataFile, 'utf8');
  const data = JSON.parse(fileContents) as DataJson;
  return data.opportunities;
}

export async function getOpportunityDetail(id: string) {
  const opportunities = getOpportunities();
  const opportunity = opportunities.find((o) => o.id === id);

  if (!opportunity) {
    return null;
  }

  const fullPath = path.join(repoRoot, opportunity.path);
  if (!fs.existsSync(fullPath)) {
    return {
      ...opportunity,
      contentHtml: '<p>Content file not found.</p>',
    };
  }

  const fileContents = fs.readFileSync(fullPath, 'utf8');
  let data = {};
  let content = '';

  try {
    const parsed = matter(fileContents);
    data = parsed.data;
    content = parsed.content;
  } catch (e) {
    console.warn(`Failed to parse frontmatter for ${id}, using raw content`);
    content = fileContents;
  }

  const processedContent = await remark()
    .use(remarkRehype)
    .use(rehypeSanitize)
    .use(rehypeStringify)
    .process(content);
  const contentHtml = processedContent.toString();

  return {
    ...opportunity,
    ...data,
    contentHtml,
  };
}
