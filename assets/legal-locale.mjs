const LEGAL_LOCALES = Object.freeze({
  en: Object.freeze({
    languageLabel: 'English',
    home: '../',
    blurb: 'Building the next generation of AI models that truly learn and adapt at inference time — adaptive intelligence for every company.',
    explore: 'Explore',
    approach: 'Approach',
    careers: 'Careers',
    contact: 'Contact',
    copyright: '© 2026 Learning Machine, Inc. All rights reserved.',
    policyLabels: Object.freeze(['Privacy', 'Applicant Privacy', 'Terms']),
  }),
  'zh-CN': Object.freeze({
    languageLabel: '简体中文',
    home: '../zh-cn/',
    blurb: '打造新一代能在推理时真正学习与适应的 AI 模型——让每家公司都拥有自适应的智能。',
    explore: '探索',
    approach: '我们的方法',
    careers: '招聘',
    contact: '联系我们',
    copyright: '© 2026 Learning Machine, Inc. 保留所有权利。',
    policyLabels: Object.freeze(['隐私政策', '候选人隐私声明', '使用条款']),
  }),
  fr: Object.freeze({
    languageLabel: 'Français',
    home: '../fr/',
    blurb: "Nous construisons la prochaine génération de modèles d'IA qui apprennent et s'adaptent vraiment au moment de l'inférence — une intelligence adaptative pour chaque entreprise.",
    explore: 'Explorer',
    approach: 'Approche',
    careers: 'Carrières',
    contact: 'Contact',
    copyright: '© 2026 Learning Machine, Inc. Tous droits réservés.',
    policyLabels: Object.freeze(['Confidentialité', 'Confidentialité des candidats', 'Conditions d’utilisation']),
  }),
  de: Object.freeze({
    languageLabel: 'Deutsch',
    home: '../de/',
    blurb: 'Wir bauen die nächste Generation von KI-Modellen, die zur Inferenzzeit wirklich lernen und sich anpassen — adaptive Intelligenz für jedes Unternehmen.',
    explore: 'Entdecken',
    approach: 'Ansatz',
    careers: 'Karriere',
    contact: 'Kontakt',
    copyright: '© 2026 Learning Machine, Inc. Alle Rechte vorbehalten.',
    policyLabels: Object.freeze(['Datenschutz', 'Datenschutz für Bewerbende', 'Nutzungsbedingungen']),
  }),
});

const POLICY_PATHS = Object.freeze(['../privacy/', '../applicant-privacy/', '../terms/']);

export function resolveLegalLocale(search = '', storedLanguage = null) {
  let requestedLanguage = null;
  try {
    requestedLanguage = new URLSearchParams(search).get('lang');
  } catch (error) {}
  if (requestedLanguage && LEGAL_LOCALES[requestedLanguage]) return requestedLanguage;
  if (storedLanguage && LEGAL_LOCALES[storedLanguage]) return storedLanguage;
  return 'en';
}

export function getLegalLocale(language) {
  return LEGAL_LOCALES[language] || LEGAL_LOCALES.en;
}

export function localizedPolicyHref(href, language) {
  const baseHref = href.split('?')[0];
  const locale = LEGAL_LOCALES[language] ? language : 'en';
  return locale === 'en' ? baseHref : `${baseHref}?lang=${encodeURIComponent(locale)}`;
}

export function applyLegalLocale(
  doc = globalThis.document,
  search = globalThis.location?.search || '',
  storage = globalThis.localStorage,
) {
  if (!doc) return 'en';

  let storedLanguage = null;
  try {
    storedLanguage = storage?.getItem('lm-lang');
  } catch (error) {}

  const language = resolveLegalLocale(search, storedLanguage);
  const locale = getLegalLocale(language);
  try {
    storage?.setItem('lm-lang', language);
  } catch (error) {}

  doc.documentElement.dataset.uiLang = language;
  const footer = doc.querySelector('footer');
  if (!footer) return language;

  const footerMain = footer.querySelector('.footer-main');
  const brand = footerMain?.querySelector('.footer-brand');
  const blurb = brand?.nextElementSibling;
  const exploreNav = footerMain?.querySelector('nav');
  const exploreHeading = exploreNav?.querySelector('p');
  const exploreLinks = [...(exploreNav?.querySelectorAll('a') || [])];
  const copyright = footer.querySelector('.footer-bottom > span');

  if (brand) brand.href = locale.home;
  if (blurb) blurb.textContent = locale.blurb;
  if (exploreHeading) exploreHeading.textContent = locale.explore;
  if (exploreLinks[0]) {
    exploreLinks[0].textContent = locale.approach;
    exploreLinks[0].href = `${locale.home}#approach`;
  }
  if (exploreLinks[1]) {
    exploreLinks[1].textContent = locale.careers;
    exploreLinks[1].href = `${locale.home}careers/`;
  }
  if (exploreLinks[2]) exploreLinks[2].textContent = locale.contact;
  if (copyright) copyright.textContent = locale.copyright;

  const policyLinks = [...footer.querySelectorAll('.footer-legal-links a')];
  policyLinks.forEach((link, index) => {
    link.textContent = locale.policyLabels[index];
    link.href = localizedPolicyHref(POLICY_PATHS[index], language);
  });

  const languageItems = [...footer.querySelectorAll('.lang-menu-list a[lang]')];
  languageItems.forEach((link) => {
    link.removeAttribute('aria-current');
    if (link.lang === language) link.setAttribute('aria-current', 'page');
  });
  const languageLabel = footer.querySelector('.lang-menu-label');
  if (languageLabel) languageLabel.textContent = locale.languageLabel;

  return language;
}

if (typeof document !== 'undefined') applyLegalLocale();
