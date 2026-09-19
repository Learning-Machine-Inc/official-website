import assert from 'node:assert/strict';
import { copyFileSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const legalPages = {
  'privacy/index.html': [
    'Privacy Policy',
    'Learning Machine, Inc.',
    'GitHub Pages',
    'Google Workspace',
    'localStorage',
    'privacy@learningmachine.ai',
  ],
  'applicant-privacy/index.html': [
    'Applicant Privacy Notice',
    'four years',
    '12 months',
    'legal hold',
    'European Union',
    'China',
    'United States',
    'privacy@learningmachine.ai',
  ],
  'terms/index.html': [
    'Terms of Use',
    'Learning Machine, Inc.',
    'intellectual property',
    'employment',
    'official@learningmachine.ai',
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
const legacyDomain = 'learning-machine.ai';
const stylesheet = read('styles.css');
const careersGenerator = read('.claude/gen-careers.py');
const homeGenerator = read('.claude/gen-home-langs.py');

assert.equal(existsSync(resolve(root, 'legal/index.html')), false, 'the public company-information page must be removed');

function read(relativePath) {
  const absolutePath = resolve(root, relativePath);
  assert.ok(existsSync(absolutePath), `${relativePath} must exist`);
  return readFileSync(absolutePath, 'utf8');
}

assert.equal(read('CNAME').trim(), 'learningmachine.ai', 'GitHub Pages must publish the new primary domain');

function assertNoExternalResources(html, relativePath) {
  const resourcePattern = /<(script|img|iframe|link)\b[^>]*?\b(?:src|href)=["']([^"']+)["'][^>]*>/gi;
  for (const match of html.matchAll(resourcePattern)) {
    const [tag, resource] = [match[1].toLowerCase(), match[2]];
    if (!/^(?:https?:)?\/\//i.test(resource)) continue;
    const isMetadataLink = tag === 'link'
      && /\brel=["'](?:canonical|alternate)["']/i.test(match[0])
      && /^https:\/\/learningmachine\.ai\//i.test(resource);
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

const legalLocaleModulePath = resolve(root, 'assets/legal-locale.mjs');
assert.ok(existsSync(legalLocaleModulePath), 'the shared legal-page locale module must exist');
const legalLocaleModule = read('assets/legal-locale.mjs');
const {
  applyLegalLocale,
  getLegalLocale,
  localizedPolicyHref,
  resolveLegalLocale,
  setupLegalLanguageMenus,
} = await import(pathToFileURL(legalLocaleModulePath));
assert.equal(resolveLegalLocale('?lang=zh-CN', 'fr'), 'zh-CN', 'the URL language must override the stored preference');
assert.equal(resolveLegalLocale('', 'de'), 'de', 'the stored preference must apply when the URL has no language');
assert.equal(resolveLegalLocale('?lang=unsupported', 'fr'), 'fr', 'an unsupported URL language must fall back to the stored preference');
assert.equal(resolveLegalLocale('', null), 'en', 'English must remain the fallback when no preference exists');
assert.equal(resolveLegalLocale(Symbol('invalid search'), 'fr'), 'fr', 'an unreadable URL query must fall back to the stored preference');
assert.equal(localizedPolicyHref('../terms/', 'zh-CN'), '../terms/?lang=zh-CN', 'policy links must retain Chinese context');
assert.equal(localizedPolicyHref('../terms/', 'en'), '../terms/', 'English policy links must keep their clean URL');
assert.equal(localizedPolicyHref('../terms/?lang=de', 'fr'), '../terms/?lang=fr', 'policy links must replace stale language queries');
assert.equal(localizedPolicyHref('../terms/', 'unsupported'), '../terms/', 'unsupported languages must use the clean English URL');
assert.deepEqual(
  getLegalLocale('zh-CN').policyLabels,
  ['隐私政策', '候选人隐私声明', '使用条款'],
  'the legal page must expose the Chinese policy-entry labels',
);
assert.equal(getLegalLocale('unsupported').languageLabel, 'English', 'unsupported locale data must fall back to English');
assert.equal(applyLegalLocale(null), 'en', 'locale application must tolerate a missing document');

function fakeElement({ href = '', lang = '', nextElementSibling = null } = {}) {
  const attributes = new Map();
  return {
    href,
    lang,
    nextElementSibling,
    textContent: '',
    attributes,
    getAttribute(name) { return name === 'href' ? this.href : attributes.get(name); },
    setAttribute(name, value) { attributes.set(name, value); },
    removeAttribute(name) { attributes.delete(name); },
  };
}

{
  const blurb = fakeElement();
  const brand = fakeElement({ nextElementSibling: blurb });
  const exploreHeading = fakeElement();
  const exploreLinks = [fakeElement(), fakeElement(), fakeElement()];
  const copyright = fakeElement();
  const policyLinks = [fakeElement(), fakeElement(), fakeElement()];
  const languageItems = ['en', 'zh-CN', 'fr', 'de'].map((lang) => fakeElement({ lang }));
  languageItems[0].setAttribute('aria-current', 'page');
  const languageLabel = fakeElement();
  const headerBrand = fakeElement();
  const contentPolicyLinks = [
    fakeElement({ href: '../privacy/' }),
    fakeElement({ href: '../applicant-privacy/?lang=de' }),
  ];
  const exploreNav = {
    querySelector: (selector) => selector === 'p' ? exploreHeading : null,
    querySelectorAll: (selector) => selector === 'a' ? exploreLinks : [],
  };
  const footerMain = {
    querySelector: (selector) => selector === '.footer-brand' ? brand : selector === 'nav' ? exploreNav : null,
  };
  const footer = {
    querySelector: (selector) => ({
      '.footer-main': footerMain,
      '.footer-bottom > span': copyright,
      '.lang-menu-label': languageLabel,
    })[selector] || null,
    querySelectorAll: (selector) => selector === '.footer-legal-links a'
      ? policyLinks
      : selector === '.lang-menu-list a[lang]' ? languageItems : [],
  };
  const doc = {
    documentElement: { dataset: {} },
    querySelector: (selector) => selector === 'footer' ? footer : selector === '.light-brand' ? headerBrand : null,
    querySelectorAll: (selector) => selector.startsWith('.legal-content a[') ? contentPolicyLinks : [],
  };
  const writes = [];
  const storage = {
    getItem: () => 'de',
    setItem: (key, value) => writes.push([key, value]),
  };

  assert.equal(applyLegalLocale(doc, '?lang=fr', storage), 'fr', 'the legal footer must apply the URL-selected locale');
  assert.equal(doc.documentElement.dataset.uiLang, 'fr', 'the active UI locale must be exposed on the document root');
  assert.deepEqual(writes, [], 'loading a localized URL must not store a preference without a menu selection');
  assert.equal(headerBrand.href, '../fr/', 'the header brand must preserve the selected locale without storage');
  assert.deepEqual(
    contentPolicyLinks.map(({ href }) => href),
    ['../privacy/?lang=fr', '../applicant-privacy/?lang=fr'],
    'inline policy links must preserve the selected locale without storage',
  );
  assert.equal(brand.href, '../fr/', 'the footer brand must return to the localized home page');
  assert.equal(blurb.textContent, getLegalLocale('fr').blurb, 'the footer blurb must be localized');
  assert.equal(exploreHeading.textContent, 'Explorer', 'the footer section heading must be localized');
  assert.deepEqual(exploreLinks.map(({ textContent }) => textContent), ['Approche', 'Carrières', 'Contact']);
  assert.deepEqual(exploreLinks.map(({ href }) => href), ['../fr/#approach', '../fr/careers/', '']);
  assert.equal(copyright.textContent, getLegalLocale('fr').copyright, 'the footer copyright must be localized');
  assert.deepEqual(policyLinks.map(({ textContent }) => textContent), getLegalLocale('fr').policyLabels);
  assert.deepEqual(policyLinks.map(({ href }) => href), [
    '../privacy/?lang=fr',
    '../applicant-privacy/?lang=fr',
    '../terms/?lang=fr',
  ]);
  assert.equal(languageItems[0].attributes.has('aria-current'), false, 'the stale language selection must be cleared');
  assert.equal(languageItems[2].attributes.has('aria-current'), false, 'homepage links must not claim to be the current legal page');
  assert.equal(languageLabel.textContent, 'Français', 'the language-menu label must show the active locale');
}

{
  const doc = { documentElement: { dataset: {} }, querySelector: () => null, querySelectorAll: () => [] };
  const unavailableStorage = {
    getItem() { throw new Error('blocked read'); },
    setItem() { throw new Error('blocked write'); },
  };
  assert.equal(applyLegalLocale(doc, '', unavailableStorage), 'en', 'blocked storage and a missing footer must degrade to English');
  assert.equal(doc.documentElement.dataset.uiLang, 'en', 'the no-footer path must still expose the resolved locale');
}

{
  const descriptor = Object.getOwnPropertyDescriptor(globalThis, 'localStorage');
  Object.defineProperty(globalThis, 'localStorage', {
    configurable: true,
    get() { throw new Error('blocked property access'); },
  });
  try {
    const doc = { documentElement: { dataset: {} }, querySelector: () => null, querySelectorAll: () => [] };
    assert.doesNotThrow(
      () => applyLegalLocale(doc, ''),
      'locale initialization must tolerate browsers that block access to the localStorage property',
    );
    assert.equal(setupLegalLanguageMenus({ querySelectorAll: () => [] }), 0);
  } finally {
    if (descriptor) Object.defineProperty(globalThis, 'localStorage', descriptor);
    else delete globalThis.localStorage;
  }
}

{
  const sparseFooter = { querySelector: () => null, querySelectorAll: () => [] };
  const doc = {
    documentElement: { dataset: {} },
    querySelector: (selector) => selector === 'footer' ? sparseFooter : null,
    querySelectorAll: () => [],
  };
  assert.equal(
    applyLegalLocale(doc, '?lang=de', null),
    'de',
    'missing optional footer nodes must not prevent locale resolution',
  );
}

{
  function interactiveElement({ hidden = false } = {}) {
    const listeners = new Map();
    const attributes = new Map();
    return {
      hidden,
      attributes,
      focusCount: 0,
      addEventListener(type, listener) { listeners.set(type, listener); },
      dispatch(type, event = {}) { listeners.get(type)?.(event); },
      focus() { this.focusCount += 1; },
      setAttribute(name, value) { attributes.set(name, value); },
    };
  }

  const button = interactiveElement();
  const list = interactiveElement({ hidden: true });
  const insideTarget = {};
  const menu = {
    dataset: {},
    querySelector: (selector) => selector === '.lang-menu-button' ? button : selector === '.lang-menu-list' ? list : null,
    contains: (target) => target === insideTarget,
  };
  const windowListeners = new Map();
  const writes = [];
  const storage = {
    blocked: false,
    setItem(key, value) {
      if (this.blocked) throw new Error('blocked write');
      writes.push([key, value]);
    },
  };
  const doc = { querySelectorAll: (selector) => selector === '[data-lang-menu]' ? [menu] : [] };
  const eventTarget = { addEventListener: (type, listener) => windowListeners.set(type, listener) };
  assert.equal(setupLegalLanguageMenus(doc, storage, eventTarget), 1, 'the shared module must initialize the legal-page language menu');

  button.dispatch('click');
  assert.equal(list.hidden, false, 'clicking the language button must open the menu');
  assert.equal(button.attributes.get('aria-expanded'), 'true', 'the open menu must expose its expanded state');
  windowListeners.get('click')({ target: insideTarget });
  assert.equal(list.hidden, false, 'clicking inside the menu must leave it open');
  list.dispatch('click', { target: { closest: () => ({ lang: 'de' }) } });
  assert.deepEqual(writes, [['lm-lang', 'de']], 'choosing a language must persist it before navigation');
  storage.blocked = true;
  assert.doesNotThrow(
    () => list.dispatch('click', { target: { closest: () => ({ lang: 'fr' }) } }),
    'language selection must tolerate blocked browser storage',
  );
  windowListeners.get('click')({ target: {} });
  assert.equal(list.hidden, true, 'clicking outside the language menu must close it');
  button.dispatch('click');
  windowListeners.get('keydown')({ key: 'Escape' });
  assert.equal(list.hidden, true, 'Escape must close the language menu');
  assert.equal(button.focusCount, 1, 'Escape must restore focus to the language button');
}

for (const [relativePath, requiredText] of Object.entries(legalPages)) {
  const html = read(relativePath);
  const pageSlug = relativePath.split('/')[0];
  assert.match(html, /<html lang="en"/i, `${relativePath} must be the English canonical page`);
  assert.match(html, /<meta name="viewport"/i, `${relativePath} must be responsive`);
  assert.ok(
    html.includes(`<link rel="canonical" href="https://learningmachine.ai/${pageSlug}/">`),
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
  assert.ok(html.includes('<script type="module" src="../assets/legal-locale.mjs"></script>'), `${relativePath} must apply the shared legal-page locale state`);
  assert.ok(html.includes('official@learningmachine.ai'), `${relativePath} must expose the official contact address`);
  assert.ok(!html.includes(legacyDomain), `${relativePath} must not expose the legacy domain`);
  assert.ok(!html.includes(retiredContactAddress), `${relativePath} must not expose the retired contact address`);
  for (const detail of sensitiveCompanyDetails) {
    assert.ok(!html.includes(detail), `${relativePath} must not expose ${JSON.stringify(detail)}`);
  }
  assert.doesNotMatch(html, /Where required, we use legally recognized safeguards/i, `${relativePath} must not claim unverified transfer safeguards are already in place`);
}

assert.match(legalLocaleModule, /setItem\(['"]lm-lang['"]/, 'the shared language menu must remember the selected language');

assert.match(
  read('applicant-privacy/index.html'),
  /<h2>1\. Who this notice covers<\/h2>[\s\S]*?Contact us at <a href="mailto:official@learningmachine\.ai">official@learningmachine\.ai<\/a>\./i,
  'the applicant notice introduction must use the official contact address',
);
assert.match(
  read('terms/index.html'),
  /<h2>12\. Changes, severability, and contact<\/h2>[\s\S]*?Questions may be sent to <a href="mailto:official@learningmachine\.ai">official@learningmachine\.ai<\/a>\./i,
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
assert.match(careersGenerator, /official@learningmachine\.ai/, 'the careers generator must emit the official contact address');
assert.match(homeGenerator, /official@learningmachine\.ai/, 'the home-page generator must emit the official contact address');
assert.ok(!careersGenerator.includes(legacyDomain), 'the careers generator must not emit the legacy domain');
assert.ok(!homeGenerator.includes(legacyDomain), 'the home-page generator must not emit the legacy domain');
for (const href of legalHrefs) {
  assert.ok(careersGenerator.includes(`href="{p}${href}{lang_query}"`), `the careers generator must emit language-aware ${href} links`);
}
assert.ok(!careersGenerator.includes('href="{p}legal/"'), 'the careers generator must not emit the retired Legal link');
assert.ok(!homeGenerator.includes('<a href="legal/">Legal</a>'), 'the home generator must not emit the retired Legal link');
for (const detail of sensitiveCompanyDetails) {
  assert.ok(!careersGenerator.includes(detail), `the careers generator must not expose ${JSON.stringify(detail)}`);
  assert.ok(!homeGenerator.includes(detail), `the home generator must not expose ${JSON.stringify(detail)}`);
}

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

const localizedLegalLabels = [
  { pathPrefix: 'zh-cn/', langQuery: '?lang=zh-CN', labels: ['隐私政策', '候选人隐私声明', '使用条款'] },
  { pathPrefix: 'fr/', langQuery: '?lang=fr', labels: ['Confidentialité', 'Confidentialité des candidats', 'Conditions d’utilisation'] },
  { pathPrefix: 'de/', langQuery: '?lang=de', labels: ['Datenschutz', 'Datenschutz für Bewerbende', 'Nutzungsbedingungen'] },
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
    assert.ok(html.includes('official@learningmachine.ai'), `${relativePath} must expose the official contact address`);
    assert.ok(!html.includes(legacyDomain), `${relativePath} must not expose the legacy domain`);
    assert.ok(!html.includes(retiredContactAddress), `${relativePath} must not expose the retired contact address`);
    assert.ok(!html.includes(`${group.prefix}legal/`), `${relativePath} must not link to the retired company-information page`);
    for (const detail of sensitiveCompanyDetails) {
      assert.ok(!html.includes(detail), `${relativePath} must not expose ${JSON.stringify(detail)}`);
    }
    const localizedLabels = localizedLegalLabels.find(({ pathPrefix }) => relativePath.startsWith(pathPrefix));
    for (const href of legalHrefs) {
      const expectedHref = `${group.prefix}${href}${localizedLabels?.langQuery || ''}`;
      assert.ok(html.includes(`href="${expectedHref}"`), `${relativePath} must link to ${expectedHref}`);
      assert.ok(existsSync(resolve(root, dirname(relativePath), `${group.prefix}${href}`)), `${relativePath}: ${expectedHref} must resolve on disk`);
    }
    if (localizedLabels) {
      const legalNav = html.match(/<nav class="footer-legal-links"[^>]*>[\s\S]*?<\/nav>/i)?.[0] || '';
      for (const [index, label] of localizedLabels.labels.entries()) {
        const expectedHref = `${group.prefix}${legalHrefs[index]}${localizedLabels.langQuery}`;
        assert.ok(
          legalNav.includes(`<a href="${expectedHref}">${label}</a>`),
          `${relativePath} must label ${expectedHref} as ${JSON.stringify(label)}`,
        );
      }
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
      new RegExp(`<p class="applicant-privacy-note">[\\s\\S]*${expectedNotice}[\\s\\S]*<\\/p>[\\s\\S]*mailto:careers@learningmachine\\.ai`, 'i'),
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
      /<section id="join"[\s\S]*?class="join-privacy-note"[\s\S]*?applicant-privacy\/[\s\S]*?mailto:careers@learningmachine\.ai/i,
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
