# Prompt for Building Next.js Site

## Goal
Build a Next.js website that replaces the current GitHub Pages site (docs/) and uses the data from this repository.
The site should have a search interface similar to Google's search page (but not AI) that allows users to search and filter opportunities.

## Data Structure
- The data is located in `docs/data.json` which contains:
    - last_updated: string
    - stats: object with counts for each category (Equity, Grants, Tenders)
    - opportunities: array of opportunity objects, each with:
        - id: string
        - category: string (one of "Equity", "Grants", "Tenders")
        - title: string
        - institution: string
        - closing_date: string
        - link: string (URL or "#")
        - path: string (relative path to the markdown file in the repo, e.g., "01_equity/83north.md")
        - verified: boolean
        - new: boolean

- Each opportunity has a corresponding markdown file at the path specified in the `path` field (relative to the repository root).
  The markdown file has a YAML frontmatter and then the content.

## Required Features
1. Home Page (Search Page):
    - A central search bar that allows users to type a query.
    - Below the search bar, buttons or checkboxes to filter by category (Equity, Grants, Tenders).
    - Additional filters: Verified, New (checkboxes).
    - The search should search through the title, institution, and possibly the content of the markdown files (but note: we are at build time, so we can only search the pre-loaded data; for full content search we might need to index, but let's start with the metadata).
    - Display the results in a list below the search bar.

2. Result List:
    - Each result item should show:
        - Title (as a link to the detail page)
        - Category (with a badge or color coding)
        - Institution
        - Closing date
        - Tags for "Verified" and "New" if applicable
    - When a result is clicked, navigate to the detail page for that opportunity.

3. Detail Page:
    - Show the title as the heading.
    - Show the metadata (institution, category, closing date, link, verified, new) in a structured way.
    - Show the content of the markdown file (converted to HTML) below the metadata.
    - Provide a link back to the search results.

4. Technical Implementation:
    - Use Next.js with static generation (preferred for Vercel).
    - Load the data from `docs/data.json` at build time (in `getStaticProps` for the home page and for generating the detail pages).
    - For each opportunity, during the build, read the markdown file from the file system (using the `path` field) and convert it to HTML (or keep as markdown and convert on the client? We'll convert to HTML at build time for security and performance).
    - We can use a library like `gray-matter` to parse the frontmatter and `remark` or `react-markdown` to convert markdown to HTML. However, note that we are at build time, so we can do the conversion during the build and store the HTML in the component's props.

5. Styling:
    - The look and feel should be similar to Google's search page: clean, minimal, with a central focus on the search bar.
    - Use a CSS framework or custom CSS. We can use Tailwind CSS for simplicity, or plain CSS.

6. Deployment:
    - The site should be deployable to Vercel with zero configuration (if we follow Next.js conventions).

## Files to Create
We expect the agent to create the following files (if they don't exist) in the repository:

- A Next.js application in the root of the repository (or in a new directory? Let's put it in the root to keep it simple, but note we have existing directories like 01_equity, etc. We can put the Next.js app in a directory named `web` or `site` to avoid confusion, but the user said to move away from GitHub Pages, so we can replace the `docs/` directory? However, the user said the docs/ is GitHub Pages and they want to move away. So we can keep the data in `docs/` and build the Next.js app in the root, and then the build output will be in `.next` and we can configure Vercel to serve that.

Alternatively, we can create the Next.js app in the root and then have the build output serve the site, and we can keep the `docs/` directory for data only.

Let's decide: We will keep the `docs/` directory as is (for data) and create the Next.js app in the root.

We will need to install dependencies: next, react, react-dom, and any markdown processing libraries.

## Steps for the Agent
1. Initialize a Next.js app (if not already present) by running `npx create-next-app@latest` or manually setting up the files.
2. Install required dependencies: `gray-matter`, `remark`, `remark-html` (or `react-markdown` if we want to do client-side rendering, but we prefer server-side for static generation).
3. Create the pages and components as described.
4. Implement the data loading and markdown conversion in the `getStaticProps` functions.
5. Implement the search and filter logic.
6. Style the pages to resemble Google's search page.
7. Ensure the site builds successfully with `next build` and can be exported or served with `next start`.

## Notes
- The agent should not modify the existing data files (in `docs/` and the category directories) unless necessary for the build process (like reading them).
- The agent should create a `README.md` for the Next.js app if they deem it necessary, but the main goal is to have a working Next.js site.
