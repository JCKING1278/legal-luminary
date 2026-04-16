import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const ROOT = process.cwd();
const CANDIDATES_DIR = path.join(ROOT, '_candidates');
const AUDIT_PATH = path.join(ROOT, '_data', 'audit_sources.json');
const SEARCH_AGENTS_PATH = path.join(ROOT, 'config', 'web_search_agents.json');

function loadCandidateFrontMatter(filePath: string): Record<string, string> {
  const raw = fs.readFileSync(filePath, 'utf-8');
  const lines = raw.split(/\r?\n/);
  if (!lines.length || lines[0].trim() !== '---') return {};
  const out: Record<string, string> = {};
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i];
    if (line.trim() === '---') break;
    const idx = line.indexOf(':');
    if (idx > 0) {
      const key = line.slice(0, idx).trim();
      const value = line.slice(idx + 1).trim().replace(/^["']|["']$/g, '');
      out[key] = value;
    }
  }
  return out;
}

function isGoogleSearchUrl(url: string): boolean {
  try {
    const u = new URL(url);
    return (
      (u.hostname === 'www.google.com' || u.hostname === 'google.com' || u.hostname === 'news.google.com') &&
      u.pathname.startsWith('/search')
    );
  } catch {
    return false;
  }
}

function getSearchQuery(url: string): string {
  try {
    const u = new URL(url);
    return u.searchParams.get('q') || u.searchParams.get('query') || u.searchParams.get('p') || '';
  } catch {
    return '';
  }
}

test.describe('Source audit and search policy', () => {
  test('audit_sources.json excludes google search URLs from effective count', async () => {
    expect(fs.existsSync(AUDIT_PATH)).toBeTruthy();
    const audit = JSON.parse(fs.readFileSync(AUDIT_PATH, 'utf-8'));
    const entries = Object.entries<any>(audit);
    expect(entries.length).toBeGreaterThan(0);

    for (const [slug, row] of entries) {
      const total = Number(row.source_count_total || 0);
      const effective = Number(row.source_count_effective || 0);
      const googleSearch = Number(row.google_search_url_count || 0);
      expect(effective, `${slug}: effective should be total - google_search`).toBe(Math.max(0, total - googleSearch));

      // Penalize each google search result URL in grading.
      const penalties = row.grading_penalties || {};
      expect(Number(penalties.google_search_urls || 0), `${slug}: missing grading penalty for google search URLs`).toBe(
        googleSearch * 10
      );
    }
  });

  test('candidate search URLs include geo context (central texas or municipality)', async () => {
    const files = fs.readdirSync(CANDIDATES_DIR).filter((f) => f.endsWith('.md'));
    expect(files.length).toBeGreaterThan(0);

    const violations: string[] = [];
    for (const file of files) {
      const fm = loadCandidateFrontMatter(path.join(CANDIDATES_DIR, file));
      const city = (fm.city || '').toLowerCase();
      const website = fm.candidate_website || '';

      if (website.includes('/search')) {
        const q = getSearchQuery(website).toLowerCase();
        const hasGeo = q.includes('central texas') || (!!city && q.includes(city));
        if (!hasGeo) {
          violations.push(`${file}: candidate_website search query must include "central texas" or city "${city}"`);
        }
      }
    }

    expect(violations, violations.join('\n')).toEqual([]);
  });

  test('search agent config includes required engines', async () => {
    expect(fs.existsSync(SEARCH_AGENTS_PATH)).toBeTruthy();
    const cfg = JSON.parse(fs.readFileSync(SEARCH_AGENTS_PATH, 'utf-8'));
    const engines = new Set((cfg.search_agents || []).filter((a: any) => a.enabled).map((a: any) => a.engine));
    const required = ['duckduckgo', 'brave', 'ecosia', 'bing', 'yahoo', 'wikipedia', 'ballotpedia'];
    for (const engine of required) {
      expect(engines.has(engine), `Missing web search agent for ${engine}`).toBeTruthy();
    }
  });

  test('google search URLs are not accepted as final sources', async () => {
    const audit = JSON.parse(fs.readFileSync(AUDIT_PATH, 'utf-8'));
    for (const [slug, row] of Object.entries<any>(audit)) {
      const googleUrls: string[] = row.google_search_urls || [];
      for (const url of googleUrls) {
        expect(isGoogleSearchUrl(url), `${slug}: malformed google search URL tracking`).toBeTruthy();
      }
      // If google search URLs exist, score should be reduced below perfect.
      if (googleUrls.length > 0) {
        expect(Number(row.quality_score || 0), `${slug}: quality score should be reduced`).toBeLessThan(100);
      }
    }
  });
});
