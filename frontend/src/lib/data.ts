import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';
import { remark } from 'remark';
import remarkRehype from 'remark-rehype';
import rehypeSanitize from 'rehype-sanitize';
import rehypeStringify from 'rehype-stringify';

const repoRoot = path.join(process.cwd(), '..');

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

const CATEGORIES = {
  '01_equity': 'Equity',
  '02_grants': 'Grants',
  '03_tenders': 'Tenders',
};

function extractTitle(text: string, defaultTitle: string): string {
  const match = text.match(/^# (?:Tender Opportunity|Grant Opportunity|Equity Opportunity|Grant Opportunity):?\s*(.*)/m);
  if (match && match[1]) return match[1].trim();

  const h1Match = text.match(/^#\s*(.*)/m);
  if (h1Match && h1Match[1]) return h1Match[1].trim();

  return defaultTitle;
}

function extractMetadata(text: string, key: string, defaultValue: string = 'N/A'): string {
  const regex = new RegExp(`-?\\s*\\*\\*(?:${key})\\*\\*:\\s*(.*)`, 'i');
  const match = text.match(regex);
  return match && match[1] ? match[1].trim() : defaultValue;
}

export function getOpportunities(): Opportunity[] {
  const opportunities: Opportunity[] = [];
  const weekAgo = new Date();
  weekAgo.setDate(weekAgo.getDate() - 7);

  for (const [dir, catName] of Object.entries(CATEGORIES)) {
    const dirPath = path.join(repoRoot, dir);
    if (!fs.existsSync(dirPath)) continue;

    const files = fs.readdirSync(dirPath);
    for (const fileName of files) {
      if (!fileName.endsWith('.md')) continue;
      if (['template.md', 'registry_audit_log.md', 'global_audit_log.md'].includes(fileName)) continue;

      const fullPath = path.join(dirPath, fileName);
      const stats = fs.statSync(fullPath);
      const fileContents = fs.readFileSync(fullPath, 'utf8');

      const title = extractTitle(fileContents, fileName.replace('.md', ''));
      const closingDate = extractMetadata(fileContents, 'Closing Date|Deadline');
      const institution = extractMetadata(fileContents, 'Institution|Organization');
      const link = extractMetadata(fileContents, 'Direct Link|Applying Link|Website', '#');
      const verified = fileContents.includes('VERIFIED');
      if (!verified) continue; // Only show verified data

      const isNew = stats.mtime > weekAgo;

      opportunities.push({
        id: fileName.replace('.md', ''),
        category: catName,
        title,
        institution,
        closing_date: closingDate,
        link,
        path: path.join(dir, fileName),
        verified,
        new: isNew,
      });
    }
  }

  return opportunities;
}

export function getPublishedReports() {
  const publishedPath = path.join(repoRoot, 'published');
  if (!fs.existsSync(publishedPath)) return [];

  return fs.readdirSync(publishedPath)
    .filter(file => file.endsWith('.pdf') || file.endsWith('.xlsx'))
    .map(file => ({
      name: file,
      url: `/published/${file}`,
      type: file.endsWith('.pdf') ? 'PDF' : 'Excel'
    }));
}

export async function getOpportunityDetail(id: string) {
  // We need to find which directory it's in
  let foundPath = '';
  let category = '';

  for (const [dir, catName] of Object.entries(CATEGORIES)) {
    const p = path.join(repoRoot, dir, `${id}.md`);
    if (fs.existsSync(p)) {
      foundPath = p;
      category = catName;
      break;
    }
  }

  if (!foundPath) return null;

  const stats = fs.statSync(foundPath);
  const fileContents = fs.readFileSync(foundPath, 'utf8');

  let data: any = {};
  let content = '';

  try {
    const parsed = matter(fileContents);
    data = parsed.data;
    content = parsed.content;
  } catch (e) {
    content = fileContents;
  }

  const processedContent = await remark()
    .use(remarkRehype)
    .use(rehypeSanitize)
    .use(rehypeStringify)
    .process(content);

  const contentHtml = processedContent.toString();

  const title = extractTitle(fileContents, id);
  const closingDate = extractMetadata(fileContents, 'Closing Date|Deadline');
  const institution = extractMetadata(fileContents, 'Institution|Organization');
  const link = extractMetadata(fileContents, 'Direct Link|Applying Link|Website', '#');
  const verified = fileContents.includes('VERIFIED');
  const weekAgo = new Date();
  weekAgo.setDate(weekAgo.getDate() - 7);
  const isNew = stats.mtime > weekAgo;

  return {
    id,
    category,
    title,
    institution,
    closing_date: closingDate,
    link,
    verified,
    new: isNew,
    contentHtml,
    ...data,
  };
}
