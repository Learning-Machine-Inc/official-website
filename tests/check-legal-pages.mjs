import assert from 'node:assert/strict';
import { copyFileSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const legalPages = {
  'privacy/index.html': [
    'Privacy Policy',
    'Learning Machine, Inc.',
    'GitHub Pages',
    'Google Workspace',
    'localStorage',
    'privacy@learning-machine.ai',
  ],
  'applicant-privacy/index.html': [
    'Applicant Privacy Notice',
    'four years',
    '12 months',
    'legal hold',
    'European Union',
    'China',
    'United States',
    'privacy@learning-machine.ai',
  ],
  'terms/index.html': [
    'Terms of Use',
    'Learning Machine, Inc.',
    'intellectual property',
    'employment',
    'official@learning-machine.ai',
  ],
};

const legalHrefs = ['privacy/', 'applicant-privacy/', 'terms/'];
const sensitiveCompanyDetails = [
  'RGVsYXdhcmUgRmlsZSBOby4gMTA0NjE1MzA=',
  'SmFudWFyeSA2LCAyMDI2',
  'WWlrYW5nIFNoZW4=',
  'Q2hpZWYgRXhlY3V0aXZlIE9mZmljZXIgYW5kIENoaWVmIFNjaWVudGlzdA==',
  'SGFydmFyZCBCdXNpbmVzcyBTZXJ2aWNlcywgSW5jLg==',
  'MTYxOTIgQ29hc3RhbCBIaWdod2F5',
  'MzAwMCBFbCBDYW1pbm8gUmVhbA==',
  'UGFsbyBBbHRvLCBDQSA5NDMwNg==',
].map((value) => Buffer.from(value, 'base64').toString('utf8'));
const retiredContactAddress = ['contact', 'learning-machine.ai'].join('@');
const stylesheet = read('styles.css');
const careersGenerator = read('.claude/gen-careers.py');
const homeGenerator = read('.claude/gen-home-langs.py');

assert.equal(existsSync(resolve(root, 'legal/index.html')), false, 'the public company-information page must be removed');

function read(relativePath) {
  const absolutePath = resolve(root, relativePath);
  assert.ok(existsSync(absolutePath), `${relativePath} must exist`);
  return readFileSync(absolutePath, 'utf8');
}

function assertNoExternalResources(html, relativePath) {
  const resourcePattern = /<(script|img|iframe|link)\b[^>]*?\b(?:src|href)=["']([^"']+)["'][^>]*>/gi;
  for (const match of html.matchAll(resourcePattern)) {
    const [tag, resource] = [match[1].toLowerCase(), match[2]];
    if (!/^(?:https?:)?\/\//i.test(resource)) continue;
    const isMetadataLink = tag === 'link'
      && /\brel=["'](?:canonical|alternate)["']/i.test(match[0])
      && /^https:\/\/learning-machine\.ai\//i.test(resource);
    assert.ok(isMetadataLink, `${relativePath} must not load external resource ${resource}`);
  }
  for (const match of html.matchAll(/<script\b(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)) {
    assert.doesNotMatch(match[1], /(?:https?:)?\/\/[^\s"'`)]+|\b(?:fetch|sendBeacon|XMLHttpRequest|WebSocket)\b|createElement\s*\(\s*["'](?:script|img|iframe|link)["']/i, `${relativePath} must not send data or load resources from inline scripts`);
  }
}

function assertVisibleElement(html, relativePath, pattern, label) {
  const match = html.match(pattern);
  assert.ok(match, `${relativePath} must include ${label}`);
  const attributes = match[1] || '';
  assert.doesNotMatch(attributes, /\b(?:hidden|inert)\b|\baria-hidden=["']true["']/i, `${relativePath}: ${label} must remain visible`);
}

for (const [relativePath, requiredText] of Object.entries(legalPages)) {
  const html = read(relativePath);
  const pageSlug = relativePath.split('/')[0];
  assert.match(html, /<html lang="en"/i, `${relativePath} must be the English canonical page`);
  assert.match(html, /<meta name="viewport"/i, `${relativePath} must be responsive`);
  assert.ok(
    html.includes(`<link rel="canonical" href="https://learning-machine.ai/${pageSlug}/">`),
    `${relativePath} must declare its public canonical URL`,
  );
  assert.ok(html.includes('href="../styles.css?rev=legal-v1"'), `${relativePath} must load the legal-page stylesheet`);
  assert.doesNotMatch(html, /\b(?:TODO|TBD)\b|\[[A-Z][A-Z _-]+\]/, `${relativePath} must not expose review placeholders`);
  assertNoExternalResources(html, relativePath);
  assertVisibleElement(html, relativePath, /<main class="legal-main"([^>]*)>/i, 'legal main content');
  assertVisibleElement(html, relativePath, /<article class="legal-shell"([^>]*)>/i, 'legal document');
  assertVisibleElement(html, relativePath, /<div class="legal-content"([^>]*)>/i, 'legal policy content');
  assertVisibleElement(html, relativePath, /<div class="footer-bottom"([^>]*)>/i, 'footer bottom');
  assertVisibleElement(html, relativePath, /<div class="footer-bottom-actions"([^>]*)>/i, 'footer actions');
  assertVisibleElement(html, relativePath, /<nav class="footer-legal-links"([^>]*)>[\s\S]*?<\/nav>/i, 'footer legal navigation');
  assertVisibleElement(html, relativePath, /<div class="lang-menu"([^>]*)\sdata-lang-menu>/i, 'footer language menu');
  for (const text of requiredText) {
    assert.ok(html.includes(text), `${relativePath} must include ${JSON.stringify(text)}`);
  }
  for (const href of legalHrefs) {
    const expectedHref = `../${href}`;
    assert.ok(html.includes(`href="${expectedHref}"`), `${relativePath} must link to ${expectedHref}`);
    assert.ok(existsSync(resolve(root, dirname(relativePath), expectedHref)), `${relativePath}: ${expectedHref} must resolve on disk`);
  }
  assert.ok(!html.includes('href="../legal/"'), `${relativePath} must not link to the retired company-information page`);
  assert.ok(
    html.includes(`href="../${pageSlug}/" aria-current="page"`),
    `${relativePath} must identify the current legal page in its footer navigation`,
  );
  for (const href of ['../', '../zh-cn/', '../fr/', '../de/']) {
    assert.ok(html.includes(`href="${href}"`), `${relativePath} language menu must link to ${href}`);
  }
  assert.match(html, /localStorage\.setItem\(['"]lm-lang['"]/, `${relativePath} language menu must remember the selected language`);
  assert.ok(html.includes('official@learning-machine.ai'), `${relativePath} must expose the official contact address`);
  assert.ok(!html.includes(retiredContactAddress), `${relativePath} must not expose the retired contact address`);
  for (const detail of sensitiveCompanyDetails) {
    assert.ok(!html.includes(detail), `${relativePath} must not expose ${JSON.stringify(detail)}`);
  }
  assert.doesNotMatch(html, /Where required, we use legally recognized safeguards/i, `${relativePath} must not claim unverified transfer safeguards are already in place`);
}

assert.match(
  read('applicant-privacy/index.html'),
  /<h2>1\. Who this notice covers<\/h2>[\s\S]*?Contact us at <a href="mailto:official@learning-machine\.ai">official@learning-machine\.ai<\/a>\./i,
  'the applicant notice introduction must use the official contact address',
);
assert.match(
  read('terms/index.html'),
  /<h2>12\. Changes, severability, and contact<\/h2>[\s\S]*?Questions may be sent to <a href="mailto:official@learning-machine\.ai">official@learning-machine\.ai<\/a>\./i,
  'the terms contact section must use the official contact address',
);

for (const selector of ['.footer-bottom-actions', '.footer-legal-links', '.applicant-privacy-note', '.legal-main', '.legal-shell', '.legal-content']) {
  assert.ok(stylesheet.includes(selector), `styles.css must retain ${selector} styling`);
}
for (const selector of ['footer-bottom', 'footer-bottom-actions', 'footer-legal-links', 'careers-main', 'applicant-privacy-note', 'light-join-card', 'join-privacy-note', 'legal-main', 'legal-shell', 'legal-content']) {
  const hidingRule = new RegExp(`\\.${selector}\\s*\\{[^}]*(?:display\\s*:\\s*none|visibility\\s*:\\s*hidden|opacity\\s*:\\s*0(?:[;}]|\\s))`, 'i');
  assert.doesNotMatch(stylesheet, hidingRule, `styles.css must not hide .${selector}`);
}

assert.match(careersGenerator, /REV = "figma-1617-19731-v49"/, 'the careers generator must emit the current stylesheet revision');
assert.match(careersGenerator, /class="applicant-privacy-note"[\s\S]*\{applicant_notice\}/, 'the careers generator must emit the localized applicant notice');
assert.doesNotMatch(careersGenerator, /Learning Machine Co\./, 'the careers generator must not restore the former company name');
assert.doesNotMatch(homeGenerator, /Learning Machine Co\./, 'the home-page generator must not restore the former company name');
assert.ok(!careersGenerator.includes(retiredContactAddress), 'the careers generator must not restore the retired contact address');
assert.ok(!homeGenerator.includes(retiredContactAddress), 'the home-page generator must not restore the retired contact address');
assert.match(careersGenerator, /official@learning-machine\.ai/, 'the careers generator must emit the official contact address');
assert.match(homeGenerator, /official@learning-machine\.ai/, 'the home-page generator must emit the official contact address');
for (const href of legalHrefs) {
  assert.ok(careersGenerator.includes(`href="{p}${href}"`), `the careers generator must emit ${href} links`);
}
assert.ok(!careersGenerator.includes('href="{p}legal/"'), 'the careers generator must not emit the retired Legal link');
assert.ok(!homeGenerator.includes('<a href="legal/">Legal</a>'), 'the home generator must not emit the retired Legal link');

const pageGroups = [
  { files: ['index.html'], prefix: '' },
  { files: ['zh-cn/index.html', 'fr/index.html', 'de/index.html'], prefix: '../' },
  {
    files: [
      'careers/index.html',
      'careers/agent-client.html',
      'careers/agent-fullstack.html',
      'careers/agent-fullstack-campus.html',
    ],
    prefix: '../',
  },
  {
    files: [
      'zh-cn/careers/index.html',
      'zh-cn/careers/agent-client.html',
      'zh-cn/careers/agent-fullstack.html',
      'zh-cn/careers/agent-fullstack-campus.html',
      'fr/careers/index.html',
      'fr/careers/agent-client.html',
      'fr/careers/agent-fullstack.html',
      'fr/careers/agent-fullstack-campus.html',
      'de/careers/index.html',
      'de/careers/agent-client.html',
      'de/careers/agent-fullstack.html',
      'de/careers/agent-fullstack-campus.html',
    ],
    prefix: '../../',
  },
];

for (const group of pageGroups) {
  for (const relativePath of group.files) {
    const html = read(relativePath);
    assert.ok(html.includes('Learning Machine, Inc.'), `${relativePath} must use the legal company name`);
    assert.match(html, /styles\.css\?rev=figma-1617-19731-v49/, `${relativePath} must use the current stylesheet revision`);
    assertNoExternalResources(html, relativePath);
    assertVisibleElement(html, relativePath, /<div class="footer-bottom"([^>]*)>/i, 'footer bottom');
    assertVisibleElement(html, relativePath, /<div class="footer-bottom-actions"([^>]*)>/i, 'footer actions');
    assertVisibleElement(html, relativePath, /<nav class="footer-legal-links"([^>]*)>[\s\S]*?<\/nav>/i, 'footer legal navigation');
    assert.ok(html.includes(`${group.prefix}applicant-privacy/`), `${relativePath} must link to the Applicant Privacy Notice`);
    assert.ok(html.includes('official@learning-machine.ai'), `${relativePath} must expose the official contact address`);
    assert.ok(!html.includes(retiredContactAddress), `${relativePath} must not expose the retired contact address`);
    assert.ok(!html.includes(`${group.prefix}legal/`), `${relativePath} must not link to the retired company-information page`);
    for (const href of legalHrefs) {
      const expectedHref = `${group.prefix}${href}`;
      assert.ok(html.includes(`href="${expectedHref}"`), `${relativePath} must link to ${expectedHref}`);
      assert.ok(existsSync(resolve(root, dirname(relativePath), expectedHref)), `${relativePath}: ${expectedHref} must resolve on disk`);
    }
  }
}

const applicantNotices = {
  'careers/': 'Applicant Privacy Notice',
  'zh-cn/careers/': '候选人隐私声明',
  'fr/careers/': 'Avis de confidentialité des candidats',
  'de/careers/': 'Datenschutzhinweis für Bewerbende',
};

for (const group of pageGroups.slice(2)) {
  for (const relativePath of group.files) {
    const html = read(relativePath);
    const [directory, expectedNotice] = Object.entries(applicantNotices).find(([prefix]) => relativePath.startsWith(prefix));
    assert.ok(directory, `${relativePath} must have a localized applicant notice expectation`);
    assertVisibleElement(html, relativePath, /<main class="careers-main"([^>]*)>/i, 'careers application content');
    assertVisibleElement(html, relativePath, /<p class="applicant-privacy-note"([^>]*)>[\s\S]*?<\/p>/i, 'applicant privacy notice');
    assert.match(
      html,
      new RegExp(`<p class="applicant-privacy-note">[\\s\\S]*${expectedNotice}[\\s\\S]*<\\/p>[\\s\\S]*mailto:careers@learning-machine\\.ai`, 'i'),
      `${relativePath} must show the applicant notice before the application action`,
    );
  }
}

for (const group of pageGroups.slice(0, 2)) {
  for (const relativePath of group.files) {
    const html = read(relativePath);
    assertVisibleElement(html, relativePath, /<div class="[^"]*\blight-join-card\b[^"]*"([^>]*)>/i, 'homepage join card');
    assertVisibleElement(html, relativePath, /<p class="join-privacy-note"([^>]*)>[\s\S]*?<\/p>/i, 'homepage applicant privacy notice');
    assert.match(
      html,
      /<section id="join"[\s\S]*?class="join-privacy-note"[\s\S]*?applicant-privacy\/[\s\S]*?mailto:careers@learning-machine\.ai/i,
      `${relativePath} must show the applicant notice before its direct careers email CTA`,
    );
  }
}

for (const relativePath of ['zh-cn/index.html', 'fr/index.html', 'de/index.html']) {
  const html = read(relativePath);
  assert.match(html, /href="careers\/"/, `${relativePath} must link to its localized careers directory`);
  assert.doesNotMatch(html, /href="\.\.\/careers\/"/, `${relativePath} must not route careers traffic to the English root`);
}

const generatedOutputs = pageGroups.flatMap((group) => group.files).concat([
  'zh/index.html',
  'careers/en/index.html',
  'careers/fr/index.html',
  'careers/de/index.html',
  ...['agent-client', 'agent-fullstack', 'agent-fullstack-campus'].flatMap((slug) => [
    `careers/en/${slug}.html`,
    `careers/fr/${slug}.html`,
    `careers/de/${slug}.html`,
  ]),
]);
const generatedRoot = mkdtempSync(join(tmpdir(), 'learning-machine-generators-'));
try {
  mkdirSync(resolve(generatedRoot, '.claude'), { recursive: true });
  copyFileSync(resolve(root, 'index.html'), resolve(generatedRoot, 'index.html'));
  for (const script of ['gen-home-langs.py', 'gen-careers.py']) {
    copyFileSync(resolve(root, '.claude', script), resolve(generatedRoot, '.claude', script));
    const result = spawnSync('python3', [resolve(generatedRoot, '.claude', script)], { encoding: 'utf8' });
    assert.equal(result.status, 0, `${script} must run successfully in isolation:\n${result.stderr || result.stdout}`);
  }
  for (const relativePath of generatedOutputs) {
    assert.equal(
      readFileSync(resolve(generatedRoot, relativePath), 'utf8'),
      read(relativePath),
      `${relativePath} must match the deterministic generator output`,
    );
  }
} finally {
  rmSync(generatedRoot, { recursive: true, force: true });
}

console.log(`Legal pages and links verified across ${Object.keys(legalPages).length} policies and ${pageGroups.flatMap((group) => group.files).length} site pages.`);
