#!/usr/bin/env python3
"""Build the translated home pages zh/, fr/ and de/ from index.html (English, the default).

Same markup, scripts, images and animations; only the copy changes, relative paths get a ../ prefix,
and the two language controls (header 中文 | EN pair, footer language menu) are re-pointed. Run it
after EVERY index.html change:

    python3 .claude/gen-home-langs.py

Every English snippet in KEYS must still exist verbatim in index.html, otherwise the script stops with
an error instead of silently shipping a half-translated page. All translations are a first-pass machine
translation (user 2026-09-04: 可以先机翻) — refine the translated columns here, never the generated files."""
import os, re, sys

ROOT = "/Users/zhangouqi/Documents/learning machine/deep-claw-main/official-website"

# Footer language menu, in display order: (html lang, label, directory under the site root; "" = English root).
LANGS = [("en", "English", ""), ("zh-CN", "中文", "zh/"), ("fr", "Français", "fr/"), ("de", "Deutsch", "de/")]

# (English snippet in index.html, 中文, Français, Deutsch). Keys carry enough surrounding markup to be unique
# to the live light-main page — the retired dark-main copy repeats several of these sentences.
T = [
    ('<html lang="en"', '<html lang="zh-CN"', '<html lang="fr"', '<html lang="de"'),
    ('<meta name="description" content="Learning Machine builds models that learn and adapt at inference time.">',
     '<meta name="description" content="Learning Machine 打造能在推理时持续学习、不断适应的模型。">',
     '<meta name="description" content="Learning Machine conçoit des modèles qui apprennent et s\'adaptent au moment de l\'inférence.">',
     '<meta name="description" content="Learning Machine entwickelt Modelle, die zur Inferenzzeit lernen und sich anpassen.">'),
    ('<title>Learning Machine | Build AI that truly Learns</title>',
     '<title>Learning Machine | 打造真正会学习的 AI</title>',
     '<title>Learning Machine | Une IA qui apprend vraiment</title>',
     '<title>Learning Machine | KI, die wirklich lernt</title>'),
    # hero
    ('<h1><span class="motion-line">Build AI</span><span class="motion-line">that truly <em>Learns</em></span></h1>',
     '<h1><span class="motion-line">打造真正</span><span class="motion-line">会<em>学习</em>的 AI</span></h1>',
     '<h1><span class="motion-line">Construire une IA</span><span class="motion-line">qui <em>apprend</em> vraiment</span></h1>',
     '<h1><span class="motion-line">KI bauen,</span><span class="motion-line">die wirklich <em>lernt</em></span></h1>'),
    ('data-words>The ability to learn is the only means to generalize artificial intelligence to all sectors of human intellectual work.</p>',
     'data-words>学习能力，是让人工智能推广到人类全部智力工作领域的唯一途径。</p>',
     'data-words>La capacité d\'apprendre est le seul moyen de généraliser l\'intelligence artificielle à tous les domaines du travail intellectuel humain.</p>',
     'data-words>Die Fähigkeit zu lernen ist der einzige Weg, künstliche Intelligenz auf alle Bereiche menschlicher geistiger Arbeit zu übertragen.</p>'),
    ('data-words>We are building the first generation of foundation models that can continuously learn, adapt, and improve.</p>',
     'data-words>我们正在打造第一代能够持续学习、适应并不断进步的基础模型。</p>',
     'data-words>Nous construisons la première génération de modèles de fondation capables d\'apprendre, de s\'adapter et de s\'améliorer en continu.</p>',
     'data-words>Wir bauen die erste Generation von Foundation-Modellen, die kontinuierlich lernen, sich anpassen und besser werden.</p>'),
    ('>See our approach <img src="assets/figma-107/',
     '>了解我们的方法 <img src="assets/figma-107/',
     '>Découvrir notre approche <img src="assets/figma-107/',
     '>Unser Ansatz <img src="assets/figma-107/'),
    ('light-btn-blue" href="mailto:contact@learning-machine.ai">Join us</a>',
     'light-btn-blue" href="mailto:contact@learning-machine.ai">加入我们</a>',
     'light-btn-blue" href="mailto:contact@learning-machine.ai">Nous rejoindre</a>',
     'light-btn-blue" href="mailto:contact@learning-machine.ai">Komm ins Team</a>'),
    # approach
    ('<p class="eyebrow kinetic-words" data-words>What makes us different</p><h2><span class="motion-line" data-scramble>Models</span><span class="motion-line">that adapt,</span><span class="motion-line h2-muted">not just respond</span></h2>',
     '<p class="eyebrow kinetic-words" data-words>我们的不同之处</p><h2><span class="motion-line" data-scramble>模型</span><span class="motion-line">会适应，</span><span class="motion-line h2-muted">而非只会回应</span></h2>',
     '<p class="eyebrow kinetic-words" data-words>Ce qui nous distingue</p><h2><span class="motion-line" data-scramble>Des modèles</span><span class="motion-line">qui s\'adaptent,</span><span class="motion-line h2-muted">au lieu de seulement répondre</span></h2>',
     '<p class="eyebrow kinetic-words" data-words>Was uns unterscheidet</p><h2><span class="motion-line" data-scramble>Modelle,</span><span class="motion-line">die sich anpassen,</span><span class="motion-line h2-muted">statt nur zu antworten</span></h2>'),
    ('<div class="light-inference light-inference-a"><p>Our models learn as they work—absorbing new knowledge and mastering new tasks through trial and error. No data pipelines, dedicated training infrastructure, or ML team required. Connect a model to a workflow, and it learns on the job.</p></div>',
     '<div class="light-inference light-inference-a"><p>我们的模型在工作中学习——一边吸收新知识，一边通过试错掌握新任务。无需数据管线、专用训练基础设施或机器学习团队。把模型接入工作流，它就能在岗位上边做边学。</p></div>',
     '<div class="light-inference light-inference-a"><p>Nos modèles apprennent en travaillant : ils absorbent de nouvelles connaissances et maîtrisent de nouvelles tâches par essais et erreurs. Aucun pipeline de données, aucune infrastructure d\'entraînement dédiée, aucune équipe ML. Connectez un modèle à un flux de travail, et il apprend sur le tas.</p></div>',
     '<div class="light-inference light-inference-a"><p>Unsere Modelle lernen während der Arbeit: Sie nehmen neues Wissen auf und meistern neue Aufgaben durch Versuch und Irrtum. Keine Datenpipelines, keine eigene Trainingsinfrastruktur, kein ML-Team nötig. Verbinde ein Modell mit einem Workflow, und es lernt im Einsatz.</p></div>'),
    # belief
    ('<span class="kinetic-words" data-words>We believe the future of AI should be diverse and inclusive.</span> <span class="belief-muted kinetic-words" data-words data-word-offset="11">Every business should be able to use its proprietary knowledge to build its own AI. Every person should have an AI experience tailored to them. And by default, their data should stay in their hands.</span>',
     '<span class="kinetic-words" data-words>我们相信，AI 的未来应当是多元且包容的。</span> <span class="belief-muted kinetic-words" data-words data-word-offset="10">每家企业都应能用自己的专有知识构建属于自己的 AI；每个人都应拥有为其量身定制的 AI 体验；而且在默认情况下，数据应始终掌握在他们自己手中。</span>',
     '<span class="kinetic-words" data-words>Nous croyons que l\'avenir de l\'IA doit être divers et inclusif.</span> <span class="belief-muted kinetic-words" data-words data-word-offset="12">Chaque entreprise devrait pouvoir utiliser son savoir propriétaire pour construire sa propre IA. Chaque personne devrait bénéficier d\'une expérience d\'IA taillée pour elle. Et, par défaut, ses données devraient rester entre ses mains.</span>',
     '<span class="kinetic-words" data-words>Wir glauben, dass die Zukunft der KI vielfältig und inklusiv sein sollte.</span> <span class="belief-muted kinetic-words" data-words data-word-offset="12">Jedes Unternehmen sollte sein eigenes Wissen nutzen können, um seine eigene KI zu bauen. Jeder Mensch sollte eine auf ihn zugeschnittene KI-Erfahrung haben. Und standardmäßig sollten die Daten in den eigenen Händen bleiben.</span>'),
    # join card (light-main only: the legacy dark-main h2 carries an id). Open roles → careers in the same
    # language; French and German fall back to the English careers pages.
    ('<h2>Join us</h2><p>We\'re building the future of AI, and we\'re hiring across research, engineering, and product. Come build it with us.</p><div class="join-actions"><a class="button button-dark" href="careers/en/">See open roles</a><a class="button button-blue" href="mailto:careers@learning-machine.ai">Get in touch</a></div>',
     '<h2>加入我们</h2><p>我们正在构建 AI 的未来，研究、工程与产品方向都在招人。来和我们一起创造。</p><div class="join-actions"><a class="button button-dark" href="careers/">查看开放岗位</a><a class="button button-blue" href="mailto:careers@learning-machine.ai">联系我们</a></div>',
     '<h2>Rejoignez-nous</h2><p>Nous construisons l\'avenir de l\'IA et nous recrutons en recherche, en ingénierie et en produit. Venez le bâtir avec nous.</p><div class="join-actions"><a class="button button-dark" href="careers/en/">Voir les postes ouverts</a><a class="button button-blue" href="mailto:careers@learning-machine.ai">Nous contacter</a></div>',
     '<h2>Komm ins Team</h2><p>Wir bauen die Zukunft der KI und suchen Verstärkung in Forschung, Engineering und Produkt. Bau sie mit uns.</p><div class="join-actions"><a class="button button-dark" href="careers/en/">Offene Stellen ansehen</a><a class="button button-blue" href="mailto:careers@learning-machine.ai">Kontakt aufnehmen</a></div>'),
    # footer
    ('Learning Machine</a><p>Building the next generation of AI models that truly learn and adapt at inference time — adaptive intelligence for every company.</p>',
     'Learning Machine</a><p>打造新一代能在推理时真正学习与适应的 AI 模型——让每家公司都拥有自适应的智能。</p>',
     'Learning Machine</a><p>Nous construisons la prochaine génération de modèles d\'IA qui apprennent et s\'adaptent vraiment au moment de l\'inférence — une intelligence adaptative pour chaque entreprise.</p>',
     'Learning Machine</a><p>Wir bauen die nächste Generation von KI-Modellen, die zur Inferenzzeit wirklich lernen und sich anpassen — adaptive Intelligenz für jedes Unternehmen.</p>'),
    ('<p>Explore</p><a href="#approach">Approach</a><a href="careers/en/">Careers</a><a href="mailto:contact@learning-machine.ai">Contact</a>',
     '<p>探索</p><a href="#approach">我们的方法</a><a href="careers/">招聘</a><a href="mailto:contact@learning-machine.ai">联系我们</a>',
     '<p>Explorer</p><a href="#approach">Approche</a><a href="careers/en/">Carrières</a><a href="mailto:contact@learning-machine.ai">Contact</a>',
     '<p>Entdecken</p><a href="#approach">Ansatz</a><a href="careers/en/">Karriere</a><a href="mailto:contact@learning-machine.ai">Kontakt</a>'),
    ('<span>© 2026 Learning Machine Co. All rights reserved.</span>',
     '<span>© 2026 Learning Machine Co. 保留所有权利。</span>',
     '<span>© 2026 Learning Machine Co. Tous droits réservés.</span>',
     '<span>© 2026 Learning Machine Co. Alle Rechte vorbehalten.</span>'),
]
COLUMN = {"zh-CN": 1, "fr": 2, "de": 3}


def header_pair(lang):
    """The header 中文 | EN pair as seen from a translated page (one level below the root)."""
    zh_cur = ' aria-current="page"' if lang == "zh-CN" else ""
    zh_href = "./" if lang == "zh-CN" else "../zh/"
    return (f'<a lang="zh-CN" hreflang="zh-CN" href="{zh_href}"{zh_cur}>中文</a>'
            f'<a lang="en" hreflang="en" href="../">EN</a>')


def footer_menu_list(lang):
    """Footer language menu items as seen from a translated page (one level below the root)."""
    items = []
    for code, label, folder in LANGS:
        href = "./" if code == lang else ("../" if folder == "" else f"../{folder}")
        cur = ' aria-current="page"' if code == lang else ""
        items.append(f'<li><a role="menuitem" lang="{code}" hreflang="{code}" href="{href}"{cur}>{label}</a></li>')
    return '<ul class="lang-menu-list" id="lang-menu-list" role="menu" hidden>' + "".join(items) + "</ul>"


src = open(f"{ROOT}/index.html", encoding="utf-8").read()
missing = [row[0] for row in T if row[0] not in src]
en_pair = '<a lang="zh-CN" hreflang="zh-CN" href="zh/">中文</a><a lang="en" hreflang="en" href="./" aria-current="page">EN</a>'
if en_pair not in src: missing.append(en_pair)
if not re.search(r'<ul class="lang-menu-list".*?</ul>', src, re.S): missing.append("<ul class=\"lang-menu-list\"…")
if '<span class="lang-menu-label">English</span>' not in src: missing.append('<span class="lang-menu-label">English</span>')
if missing:
    sys.exit("gen-home-langs: these snippets are no longer in index.html — update T / the language controls:\n  " + "\n  ".join(m[:90] for m in missing))

for lang, label, folder in LANGS[1:]:
    out = src
    for row in T:
        out = out.replace(row[0], row[COLUMN[lang]], 1)
    out = out.replace(en_pair, header_pair(lang), 1)
    out = re.sub(r'<ul class="lang-menu-list".*?</ul>', footer_menu_list(lang), out, count=1, flags=re.S)
    out = out.replace('<span class="lang-menu-label">English</span>', f'<span class="lang-menu-label">{label}</span>', 1)
    # One level below the root: prefix every relative URL (assets/, styles.css, careers/) with ../ but leave
    # anchors, absolute URLs, mailto:, data: and the already-relative ./ and ../ alone.
    out = re.sub(r'\b(href|src|srcset|data-a|data-b)="(?!https?:|mailto:|#|\.\.?/|/|data:)([^"]+)"', r'\1="../\2"', out)
    out = out.replace("from './assets/", "from '../assets/")  # Lenis module import in the inline module script
    assert out.count("../assets/") > 20 and 'href="../styles.css' in out, f"{lang}: path rewrite looks wrong"
    os.makedirs(f"{ROOT}/{folder}", exist_ok=True)
    with open(f"{ROOT}/{folder}index.html", "w", encoding="utf-8") as f:
        f.write(out)
    print(f"written: {folder}index.html ({len(T)} snippets translated)")
