#!/usr/bin/env python3
"""Generate the careers pages in the site's four languages from one data table (language first, like the
home pages: the default language English has no prefix, every other language is one folder):
  careers/index.html,       careers/<slug>.html        English (site default)
  zh-cn/careers/index.html, zh-cn/careers/<slug>.html  简体中文 (zh-cn, not plain zh: Simplified only)
  fr/careers/…, de/careers/…                           Français / Deutsch (first-pass machine translation)
The old URLs (careers/ = 中文, careers/en|fr|de/, zh/) are kept as redirect stubs by gen-home-langs.py.
Header/footer markup mirrors index.html (asset paths rewritten with ../ or ../../). Every page links to
its siblings through the footer language menu and hreflang alternates; the <head> language-memory
script keeps a visitor inside the language they chose."""
import html, os, posixpath

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://learning-machine.ai"
REV = "figma-1617-19731-v48"
EMAIL = "careers@learning-machine.ai"

# Footer language menu, in display order: (html lang code, label, UI key).
LANGS = [("en", "English", "en"), ("zh-CN", "简体中文", "zh"), ("fr", "Français", "fr"), ("de", "Deutsch", "de")]

# Per-language UI strings. `dir` is the site-relative folder of that language's careers pages; `home` is the
# same-language home page relative to `dir`. Tuples: open_apply = (eyebrow, h2, note, button, mail subject);
# apply = (eyebrow, h2, note, button); footer = (blurb, explore, approach, careers, contact, copyright).
UI = {
    "zh": dict(html_lang="zh-CN", dir="zh-cn/careers", home="../",
               nav_careers="招聘", nav_contact="联系我们",
               intro="目前开放 {n} 个岗位。点击岗位查看职位要求与投递方式。",
               view="查看详情", back="返回职位列表", back_home="返回首页",
               open_apply=("Open application · 自荐", "没有合适的岗位？直接把简历发给我们", "邮件发送至 {email}，注明你感兴趣的方向。", "自荐投递", "自荐投递"),
               apply=("Apply · 简历投递", "简历投递", "邮件发送至 {email}，主题请注明「{subject}」。", "立即投递"),
               index_desc="Learning Machine 开放岗位：Agent 全栈研发、客户端研发。",
               role_title="{name}（{tag}）", role_desc="Learning Machine 招聘：{name}（{tag}）。",
               footer=("打造新一代能在推理时真正学习与适应的 AI 模型——让每家公司都拥有自适应的智能。", "探索", "我们的方法", "招聘", "联系我们", "© 2026 Learning Machine Co. 保留所有权利。")),
    "en": dict(html_lang="en", dir="careers", home="../",
               nav_careers="Careers", nav_contact="Contact",
               intro="{n} open roles. Open a role for requirements and how to apply.",
               view="View details", back="Back to open roles", back_home="Back to home",
               open_apply=("Open application", "No matching role? Send us your CV anyway", "Email {email} and tell us which direction interests you.", "Send open application", "Open application"),
               apply=("Apply", "Send your CV", "Email {email} with the subject line “{subject}”.", "Apply now"),
               index_desc="Open roles at Learning Machine: Agent full-stack engineering and client engineering.",
               role_title="{name} ({tag})", role_desc="Learning Machine is hiring: {name} ({tag}).",
               footer=("Building the next generation of AI models that truly learn and adapt at inference time — adaptive intelligence for every company.", "Explore", "Approach", "Careers", "Contact", "© 2026 Learning Machine Co. All rights reserved.")),
    "fr": dict(html_lang="fr", dir="fr/careers", home="../",
               nav_careers="Carrières", nav_contact="Contact",
               intro="{n} postes ouverts. Ouvrez un poste pour voir les exigences et comment postuler.",
               view="Voir le poste", back="Retour aux postes", back_home="Retour à l'accueil",
               open_apply=("Candidature spontanée", "Aucun poste ne vous correspond ? Envoyez-nous quand même votre CV", "Écrivez à {email} en précisant le domaine qui vous intéresse.", "Envoyer une candidature spontanée", "Candidature spontanée"),
               apply=("Postuler", "Envoyez votre CV", "Écrivez à {email} avec pour objet « {subject} ».", "Postuler"),
               index_desc="Postes ouverts chez Learning Machine : ingénierie full-stack Agent et ingénierie client.",
               role_title="{name} ({tag})", role_desc="Learning Machine recrute : {name} ({tag}).",
               footer=("Nous construisons la prochaine génération de modèles d'IA qui apprennent et s'adaptent vraiment au moment de l'inférence — une intelligence adaptative pour chaque entreprise.", "Explorer", "Approche", "Carrières", "Contact", "© 2026 Learning Machine Co. Tous droits réservés.")),
    "de": dict(html_lang="de", dir="de/careers", home="../",
               nav_careers="Karriere", nav_contact="Kontakt",
               intro="{n} offene Stellen. Öffne eine Stelle für Anforderungen und Bewerbung.",
               view="Details ansehen", back="Zurück zu den Stellen", back_home="Zur Startseite",
               open_apply=("Initiativbewerbung", "Keine passende Stelle? Schick uns trotzdem deinen Lebenslauf", "Schreib an {email} und nenne die Richtung, die dich interessiert.", "Initiativbewerbung senden", "Initiativbewerbung"),
               apply=("Bewerben", "Schick uns deinen Lebenslauf", "Schreib an {email} mit dem Betreff „{subject}“.", "Jetzt bewerben"),
               index_desc="Offene Stellen bei Learning Machine: Agent-Full-Stack-Engineering und Client-Engineering.",
               role_title="{name} ({tag})", role_desc="Learning Machine sucht: {name} ({tag}).",
               footer=("Wir bauen die nächste Generation von KI-Modellen, die zur Inferenzzeit wirklich lernen und sich anpassen — adaptive Intelligenz für jedes Unternehmen.", "Entdecken", "Ansatz", "Karriere", "Kontakt", "© 2026 Learning Machine Co. Alle Rechte vorbehalten.")),
}
for ui in UI.values():
    ui["prefix"] = "../" * (ui["dir"].count("/") + 1)

HEAD = """<!doctype html>
<html lang="{lang}" data-variant="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#F4F0ED">
  <meta name="description" content="{desc}">
  <title>{title} | Learning Machine</title>
{alternates}{langmem}
  <link rel="icon" href="{p}assets/icons/favicon-adaptive.svg?v=1" type="image/svg+xml">
  <link rel="icon" href="{p}assets/icons/favicon-32.png" type="image/png" sizes="32x32" media="(prefers-color-scheme: light)">
  <link rel="icon" href="{p}assets/icons/favicon-dark-32.png" type="image/png" sizes="32x32" media="(prefers-color-scheme: dark)">
  <link rel="apple-touch-icon" href="{p}assets/icons/apple-touch-icon.png">
  <link rel="preload" href="{p}assets/fonts/outfit-bold-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="{p}assets/fonts/gentium-plus-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="{p}assets/fonts/roboto-var-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="{p}styles.css?rev={rev}">
</head>
<body class="careers-page">
  <header class="light-header">
    <a href="{home}" class="light-brand" aria-label="Learning Machine home"><span class="brand-lockup"><span class="brand-mark" aria-hidden="true"><img class="brand-union" src="{p}assets/figma-106/0fc9ec76b79449656b5cb20fb65111dac0da7f74.svg" alt=""><img class="brand-base" src="{p}assets/figma-106/bb0bb4d59834c3b5c02cce512ab83e6722cc4dc8.svg" alt=""><img class="brand-vector" src="{p}assets/figma-106/e4e75da9be77e4b5d88637388247ffcbc5fbd42b.svg" alt=""></span><span class="brand-wordmark">Learning Machine</span></span></a>
    <nav class="light-nav" aria-label="Primary navigation"><a class="light-nav-contact" href="mailto:contact@learning-machine.ai">{nav_contact}</a></nav>
  </header>
  <main class="careers-main">
"""

FOOTER = """  </main>
  <footer><div class="footer-main"><div><a href="{home}" class="footer-brand"><img class="footer-brand-icon" src="{p}assets/icons/lm-icon-white.svg" alt="">Learning Machine</a><p>{f_blurb}</p><a class="footer-email" href="mailto:contact@learning-machine.ai"><span class="footer-email-icon-wrap" aria-hidden="true"><img class="footer-email-icon" src="{p}assets/figma-106/a4b3051739e035e1583a24a11a07115ada55bc08.svg" alt=""></span><span>contact@learning-machine.ai</span></a></div><nav aria-label="Footer navigation"><p>{f_explore}</p><a href="{home}#approach">{f_approach}</a><a href="./">{f_careers}</a><a href="mailto:contact@learning-machine.ai">{f_contact}</a></nav></div><div class="footer-bottom"><span>{f_copyright}</span>{langmenu}</div></footer>
{motion}
{scroll}
{langscript}
</body>
</html>
"""

MOTION = """  <script>
    (() => {
      if (matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) return;
      const targets = document.querySelectorAll('.careers-title > *, .role-row, .facts > li, .careers-section, .apply-card');
      document.documentElement.classList.add('careers-motion-ready');
      const observer = new IntersectionObserver((entries) => entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('careers-motion-visible');
        observer.unobserve(entry.target);
      }), { threshold:.08, rootMargin:'0px 0px -8% 0px' });
      targets.forEach((target, index) => {
        target.style.setProperty('--careers-reveal-delay', `${Math.min(index, 3) * 50}ms`);
        observer.observe(target);
      });
    })();
  </script>"""

SMOOTH_SCROLL = """  <script type="module">
    import Lenis from '{prefix}assets/vendor/lenis-1.3.26.mjs';
    window.lenis = new Lenis({{ autoRaf:true, lerp:.14, respectReducedMotion:true, smoothWheel:true, wheelMultiplier:1.5 }});
  </script>"""

# One entry per role; slug=None means "no posting yet" (list row only, shows the `soon` text).
# No location / salary / benefits anywhere (user 2026-09-07): the former facts row is gone and metas carry only type · team.
# Copy approved 2026-09-08: three sections per role, aligned across zh / en / fr / de.
# PARKED_ROLES are not rendered anywhere: the design internship was taken down on 2026-09-07 (user: 先把设计的招聘信息下掉,
# 之后我再补上). When the posting is ready, move the entry back into ROLES, give it a slug + sections, and put
# "visual design" back into the four `index_desc` strings above.
PARKED_ROLES = [
    dict(slug=None,
         zh=dict(name="Agent 视觉设计实习生", tag="实习", meta="实习 · 设计", soon="招聘详情即将发布"),
         en=dict(name="Agent Visual Design Intern", tag="Intern", meta="Intern · Design", soon="Details coming soon"),
         fr=dict(name="Stagiaire Design Visuel Agent", tag="Stage", meta="Stage · Design", soon="Détails à venir"),
         de=dict(name="Praktikum Visual Design Agent", tag="Praktikum", meta="Praktikum · Design", soon="Details folgen")),
]
ROLES = [
    dict(slug="agent-fullstack-campus",
         zh=dict(name="Agent 全栈研发工程师", tag="校招 / 实习", meta="校招 / 实习 · 研发",
                 points=["开发自有模型的 Agent，有资深 Mentor 和团队协作", "全栈客户端功能开发，根据 Figma MCP 到 Coding Agent 进行前端页面开发"],
                 eyebrow="WE ARE HIRING · 校招 / 实习",
                 sections=[
                     ("WHAT YOU'LL DO", "岗位职责", [
                         "与资深导师及团队协作，基于自研模型开发 Agent 产品。",
                         "使用 Figma MCP 和 Coding Agents，将设计稿转化为客户端界面与交互功能。",
                         "对接后端服务，参与 Agent 架构设计与功能开发。",
                     ]),
                     ("WHO YOU ARE", "任职要求", [
                         "计算机、电子信息、软件工程、人工智能等相关专业，具备数据结构、算法、网络和操作系统基础。",
                         "熟练使用 Coding Agents，对 Agent 和大模型有浓厚兴趣，了解其基本工作原理。",
                         "熟悉至少一种客户端技术，如 iOS、Android、Flutter、React Native 或桌面应用开发，能独立实现基础界面与交互。",
                         "掌握至少一种后端语言，如 Java、Go、Python 或 Node.js，了解 RESTful API 和数据库，能开发与调试基础接口。",
                         "学习主动，善于分析和解决问题，具备良好的沟通与团队协作能力。",
                     ]),
                     ("NICE TO HAVE", "加分项", [
                         "有相关课程项目、Agent 产品、大模型 API 集成或 Prompt 设计实践。",
                         "有移动端与桌面端跨平台开发经验。",
                         "有开源项目贡献。",
                         "能使用英语开展日常工作。",
                     ]),
                 ]),
         en=dict(name="Agent Full-Stack Engineer", tag="Campus / Intern", meta="Campus / Intern · Engineering",
                 points=["Build Agents on our own models, with senior mentors and a collaborative team", "Full-stack client development: front-end pages built from Figma MCP through Coding Agent"],
                 eyebrow="WE ARE HIRING · Campus / Intern",
                 sections=[
                     ("WHAT YOU'LL DO", "Responsibilities", [
                         "Build Agent products powered by our own models, working with senior mentors and the team.",
                         "Turn designs into client interfaces and interactions using Figma MCP and Coding Agents.",
                         "Integrate back-end services and contribute to Agent architecture and feature development.",
                     ]),
                     ("WHO YOU ARE", "Requirements", [
                         "Studying computer science, electronic engineering, software engineering, AI or a related field, with solid foundations in data structures, algorithms, networking and operating systems.",
                         "Proficient with Coding Agents, with a strong interest in Agents and large language models and an understanding of how they work.",
                         "Familiar with at least one client stack, such as iOS, Android, Flutter, React Native or desktop development, and able to build basic interfaces and interactions independently.",
                         "Comfortable with at least one back-end language, such as Java, Go, Python or Node.js, and able to build and debug basic endpoints using RESTful APIs and databases.",
                         "A proactive learner and thoughtful problem solver who communicates clearly and works well with others.",
                     ]),
                     ("NICE TO HAVE", "Bonus points", [
                         "Relevant coursework or hands-on experience with Agent products, LLM API integration or prompt design.",
                         "Cross-platform development experience across mobile and desktop.",
                         "Contributions to open-source projects.",
                         "Comfortable working in English.",
                     ]),
                 ]),
         fr=dict(name="Ingénieur Full-Stack Agent", tag="Campus / Stage", meta="Campus / Stage · Ingénierie",
                 points=["Construire des Agents sur nos propres modèles, avec des mentors seniors et une équipe collaborative", "Développement client full-stack : des pages front-end construites de Figma MCP jusqu'au Coding Agent"],
                 eyebrow="WE ARE HIRING · Campus / Stage",
                 sections=[
                     ("WHAT YOU'LL DO", "Responsabilités", [
                         "Développer des produits Agent fondés sur nos propres modèles, aux côtés de mentors expérimentés et de l’équipe.",
                         "Transformer les maquettes en interfaces et interactions côté client à l’aide de Figma MCP et de Coding Agents.",
                         "Intégrer les services back-end et contribuer à l’architecture des Agents et au développement de leurs fonctionnalités.",
                     ]),
                     ("WHO YOU ARE", "Profil recherché", [
                         "Études en informatique, électronique, génie logiciel, IA ou dans un domaine connexe, avec de solides bases en structures de données, algorithmes, réseaux et systèmes d’exploitation.",
                         "Maîtrise des Coding Agents, avec un fort intérêt pour les Agents et les grands modèles de langage et une compréhension de leur fonctionnement.",
                         "Connaissance d’au moins une technologie client, comme iOS, Android, Flutter, React Native ou le développement d’applications de bureau, et capacité à réaliser de façon autonome des interfaces et interactions simples.",
                         "Maîtrise d’au moins un langage back-end, comme Java, Go, Python ou Node.js, et capacité à développer et déboguer des points d’accès simples à l’aide d’API RESTful et de bases de données.",
                         "Envie d’apprendre, capacité à analyser et résoudre les problèmes, communication claire et goût du travail en équipe.",
                     ]),
                     ("NICE TO HAVE", "Atouts", [
                         "Projets réalisés dans le cadre des études ou expérience pratique de produits Agent, d’intégration d’API LLM ou de conception de prompts.",
                         "Expérience du développement multiplateforme sur mobile et ordinateur.",
                         "Contributions à des projets open source.",
                         "Aisance pour travailler en anglais.",
                     ]),
                 ]),
         de=dict(name="Agent Full-Stack Engineer", tag="Campus / Praktikum", meta="Campus / Praktikum · Engineering",
                 points=["Agents auf unseren eigenen Modellen bauen, mit erfahrenen Mentoren und einem kollaborativen Team", "Full-Stack-Client-Entwicklung: Frontend-Seiten von Figma MCP über den Coding Agent bis zur Auslieferung"],
                 eyebrow="WE ARE HIRING · Campus / Praktikum",
                 sections=[
                     ("WHAT YOU'LL DO", "Aufgaben", [
                         "Agent-Produkte auf Basis unserer eigenen Modelle entwickeln, gemeinsam mit erfahrenen Mentoren und dem Team.",
                         "Mit Figma MCP und Coding Agents Designs in Client-Oberflächen und Interaktionen umsetzen.",
                         "Backend-Dienste integrieren und an der Agent-Architektur sowie der Entwicklung von Funktionen mitwirken.",
                     ]),
                     ("WHO YOU ARE", "Anforderungen", [
                         "Studium der Informatik, Elektrotechnik, Softwaretechnik, KI oder eines verwandten Fachs mit soliden Grundlagen in Datenstrukturen, Algorithmen, Netzwerken und Betriebssystemen.",
                         "Sicherer Umgang mit Coding Agents, großes Interesse an Agents und großen Sprachmodellen sowie Verständnis ihrer Funktionsweise.",
                         "Vertrautheit mit mindestens einer Client-Technologie wie iOS, Android, Flutter, React Native oder Desktop-Entwicklung und die Fähigkeit, einfache Oberflächen und Interaktionen selbstständig umzusetzen.",
                         "Beherrschung mindestens einer Backend-Sprache wie Java, Go, Python oder Node.js sowie die Fähigkeit, einfache Endpunkte mit RESTful APIs und Datenbanken zu entwickeln und zu debuggen.",
                         "Eigeninitiative beim Lernen, analytisches Denken und Problemlösungskompetenz sowie klare Kommunikation und Teamfähigkeit.",
                     ]),
                     ("NICE TO HAVE", "Pluspunkte", [
                         "Studienprojekte oder praktische Erfahrung mit Agent-Produkten, der Integration von LLM-APIs oder Prompt-Design.",
                         "Erfahrung mit plattformübergreifender Entwicklung für Mobile und Desktop.",
                         "Beiträge zu Open-Source-Projekten.",
                         "Sicheres Arbeiten auf Englisch.",
                     ]),
                 ])),
    dict(slug="agent-fullstack",
         zh=dict(name="Agent 全栈研发高级工程师", tag="社招", meta="社招 · 研发",
                 points=["负责 AI Agent 个人助理客户端全栈研发，端到端落地核心功能", "主导核心交互逻辑、任务调度与上下文管理，结合大模型能力"],
                 eyebrow="WE ARE HIRING · 社招",
                 sections=[
                     ("WHAT YOU'LL DO", "岗位职责", [
                         "负责 AI Agent 个人助理的全栈研发，覆盖客户端、后端服务与 AI 能力集成，端到端交付核心功能。",
                         "主导 Agent 交互、任务调度与上下文管理，实现智能对话、任务拆解、工具调用和个性化体验。",
                         "与产品和测试团队协作，推动技术方案、代码评审与产品迭代，优化跨端体验、性能和稳定性。",
                     ]),
                     ("WHO YOU ARE", "任职要求", [
                         "本科及以上学历，计算机、电子信息、软件工程等相关专业，具备 3 年及以上全栈研发经验，熟练使用 Coding Agents。",
                         "熟练掌握 Flutter、React Native 或原生 iOS 开发，能独立完成客户端界面与交互，熟悉组件化开发和 UI/UX 规范。",
                         "熟练掌握 Go、Python 或 Java 中至少一种语言，熟悉 RESTful API、微服务和数据库，了解缓存与消息队列。",
                         "理解大模型基本原理，熟悉大模型 API 集成、Prompt 设计及常见 Agent 框架。",
                         "能定位并解决客户端、后端与 AI 集成中的问题，具备良好的 Git、代码、文档和团队协作习惯。",
                     ]),
                     ("NICE TO HAVE", "加分项", [
                         "有 AI Agent 或个人助理产品研发经验，或主导过相关产品从零到上线。",
                         "有模型微调、Agent 调度策略或上下文记忆优化经验。",
                         "有移动端与桌面端跨平台开发、适配或性能优化经验。",
                         "有开源贡献、技术博客或可展示的技术作品。",
                     ]),
                 ]),
         en=dict(name="Senior Agent Full-Stack Engineer", tag="Experienced hire", meta="Experienced hire · Engineering",
                 points=["Own full-stack development of the AI Agent personal-assistant client and ship its core features end to end", "Lead core interaction logic, task scheduling and context management on top of large-model capabilities"],
                 eyebrow="WE ARE HIRING · Experienced hire",
                 sections=[
                     ("WHAT YOU'LL DO", "Responsibilities", [
                         "Own full-stack development of an AI Agent personal assistant, delivering core features across clients, back-end services and AI integrations.",
                         "Lead Agent interactions, task scheduling and context management to support conversation, task decomposition, tool use and personalized experiences.",
                         "Work with product and QA on technical design, code reviews and product iteration, improving cross-platform experience, performance and reliability.",
                     ]),
                     ("WHO YOU ARE", "Requirements", [
                         "A bachelor’s degree or above in computer science, electronic engineering, software engineering or a related field, with 3+ years of full-stack experience and proficiency with Coding Agents.",
                         "Proficient in Flutter, React Native or native iOS development, with the ability to build client interfaces and interactions independently using component-based design and UI/UX guidelines.",
                         "Proficient in at least one of Go, Python or Java; familiar with RESTful APIs, microservices and databases, with an understanding of caching and message queues.",
                         "Understand how large language models work and be familiar with LLM API integration, prompt design and common Agent frameworks.",
                         "Able to diagnose issues across clients, back-end services and AI integrations, with sound Git, coding, documentation and collaboration practices.",
                     ]),
                     ("NICE TO HAVE", "Bonus points", [
                         "Experience building AI Agent or personal-assistant products, or leading one from concept to launch.",
                         "Experience with model fine-tuning, Agent scheduling strategies or context-memory optimization.",
                         "Experience with mobile and desktop development, cross-platform adaptation or performance optimization.",
                         "Open-source contributions, a technical blog or a portfolio of technical work.",
                     ]),
                 ]),
         fr=dict(name="Ingénieur Full-Stack Agent Senior", tag="Expérimenté", meta="Expérimenté · Ingénierie",
                 points=["Piloter le développement full-stack du client assistant personnel AI Agent et livrer ses fonctionnalités clés de bout en bout", "Diriger la logique d'interaction, l'ordonnancement des tâches et la gestion du contexte, sur la base des grands modèles"],
                 eyebrow="WE ARE HIRING · Expérimenté",
                 sections=[
                     ("WHAT YOU'LL DO", "Responsabilités", [
                         "Piloter le développement full-stack d’un assistant personnel AI Agent et livrer ses fonctionnalités clés de bout en bout, des clients aux services back-end et aux intégrations IA.",
                         "Diriger le développement des interactions de l’Agent, de l’ordonnancement des tâches et de la gestion du contexte pour permettre la conversation, la décomposition des tâches, l’utilisation d’outils et des expériences personnalisées.",
                         "Collaborer avec les équipes produit et QA sur la conception technique, les revues de code et les évolutions du produit afin d’améliorer l’expérience multiplateforme, les performances et la fiabilité.",
                     ]),
                     ("WHO YOU ARE", "Profil recherché", [
                         "Licence ou diplôme supérieur en informatique, électronique, génie logiciel ou dans un domaine connexe, avec au moins 3 ans d’expérience full-stack et une maîtrise des Coding Agents.",
                         "Maîtrise de Flutter, React Native ou du développement iOS natif, avec la capacité à réaliser de façon autonome des interfaces et interactions client selon les principes de conception par composants et les recommandations UI/UX.",
                         "Maîtrise d’au moins un langage parmi Go, Python ou Java ; connaissance des API RESTful, des microservices et des bases de données, ainsi que des mécanismes de cache et des files de messages.",
                         "Compréhension du fonctionnement des grands modèles de langage et connaissance de l’intégration d’API LLM, de la conception de prompts et des principaux frameworks d’Agents.",
                         "Capacité à diagnostiquer les problèmes côté client, back-end et intégration IA, avec de bonnes pratiques de Git, de code, de documentation et de collaboration.",
                     ]),
                     ("NICE TO HAVE", "Atouts", [
                         "Expérience du développement de produits AI Agent ou d’assistants personnels, ou de leur pilotage de la conception au lancement.",
                         "Expérience du fine-tuning de modèles, des stratégies d’ordonnancement des Agents ou de l’optimisation de la mémoire contextuelle.",
                         "Expérience du développement sur mobile et ordinateur, de l’adaptation multiplateforme ou de l’optimisation des performances.",
                         "Contributions open source, blog technique ou portfolio de réalisations techniques.",
                     ]),
                 ]),
         de=dict(name="Senior Agent Full-Stack Engineer", tag="Berufserfahren", meta="Berufserfahren · Engineering",
                 points=["Die Full-Stack-Entwicklung des KI-Agent-Assistenten-Clients verantworten und seine Kernfunktionen Ende-zu-Ende ausliefern", "Interaktionslogik, Aufgabenplanung und Kontextverwaltung auf Basis großer Modelle leiten"],
                 eyebrow="WE ARE HIRING · Berufserfahren",
                 sections=[
                     ("WHAT YOU'LL DO", "Aufgaben", [
                         "Die Full-Stack-Entwicklung eines persönlichen KI-Agent-Assistenten verantworten und Kernfunktionen über Clients, Backend-Dienste und KI-Integrationen hinweg durchgängig ausliefern.",
                         "Die Entwicklung von Agent-Interaktionen, Aufgabenplanung und Kontextverwaltung leiten, um Dialoge, Aufgabenzerlegung, Werkzeugnutzung und personalisierte Erlebnisse zu ermöglichen.",
                         "Mit Produkt und QA an technischer Konzeption, Code-Reviews und Produktverbesserungen arbeiten, um plattformübergreifende Nutzererfahrung, Performance und Zuverlässigkeit zu verbessern.",
                     ]),
                     ("WHO YOU ARE", "Anforderungen", [
                         "Bachelorabschluss oder höher in Informatik, Elektrotechnik, Softwaretechnik oder einem verwandten Fach, mindestens 3 Jahre Full-Stack-Erfahrung und sicherer Umgang mit Coding Agents.",
                         "Sehr gute Kenntnisse in Flutter, React Native oder nativer iOS-Entwicklung sowie die Fähigkeit, Client-Oberflächen und Interaktionen selbstständig nach komponentenbasierten Designprinzipien und UI/UX-Richtlinien umzusetzen.",
                         "Sehr gute Kenntnisse in mindestens einer Sprache aus Go, Python oder Java; vertraut mit RESTful APIs, Microservices und Datenbanken sowie mit Caching und Message Queues.",
                         "Verständnis der Funktionsweise großer Sprachmodelle und Vertrautheit mit der Integration von LLM-APIs, Prompt-Design und gängigen Agent-Frameworks.",
                         "Fähigkeit, Probleme in Clients, Backend-Diensten und KI-Integrationen zu diagnostizieren, sowie gute Praktiken für Git, Code, Dokumentation und Zusammenarbeit.",
                     ]),
                     ("NICE TO HAVE", "Pluspunkte", [
                         "Erfahrung mit der Entwicklung von KI-Agent- oder Assistenten-Produkten oder mit deren Leitung vom Konzept bis zum Launch.",
                         "Erfahrung mit Modell-Fine-Tuning, Agent-Planungsstrategien oder der Optimierung des Kontextgedächtnisses.",
                         "Erfahrung mit Mobile- und Desktop-Entwicklung, plattformübergreifender Anpassung oder Performance-Optimierung.",
                         "Open-Source-Beiträge, ein technischer Blog oder ein Portfolio technischer Arbeiten.",
                     ]),
                 ])),
    dict(slug="agent-client",
         zh=dict(name="Agent 客户端工程师", tag="社招", meta="社招 · 客户端研发",
                 points=["开发自有模型的 Agent 客户端：Web、iOS、macOS", "从 Figma MCP 到 Coding Agent 的全栈客户端功能开发"],
                 eyebrow="WE ARE HIRING · 社招",
                 sections=[
                     ("WHAT YOU'LL DO", "岗位职责", [
                         "基于自研模型开发 Agent 客户端，覆盖 Web、iOS 和 macOS。",
                         "使用 Figma MCP 和 Coding Agents，将设计稿转化为客户端界面与交互功能。",
                         "对接后端服务与 Agent 能力，参与 Agent 架构设计与功能开发。",
                     ]),
                     ("WHO YOU ARE", "任职要求", [
                         "计算机、电子信息、软件工程、人工智能等相关专业背景，熟练使用 Coding Agents。",
                         "具备 1–3 年客户端项目经验，熟悉至少一种客户端技术，如 iOS、Android、Flutter、React Native 或桌面应用开发，能独立实现界面与交互。",
                         "对 Agent 和大模型有浓厚兴趣，了解其基本工作原理。",
                         "学习主动，善于分析和解决问题，具备良好的沟通与团队协作能力。",
                     ]),
                     ("NICE TO HAVE", "加分项", [
                         "有 Agent 产品研发经验。",
                         "有大模型 API 集成或 Prompt 设计实践。",
                         "能使用英语开展日常工作。",
                     ]),
                 ]),
         en=dict(name="Agent Client Engineer", tag="Experienced hire", meta="Experienced hire · Client engineering",
                 points=["Build the Agent client for our own models: Web, iOS and macOS", "Full-stack client development from Figma MCP to Coding Agent"],
                 eyebrow="WE ARE HIRING · Experienced hire",
                 sections=[
                     ("WHAT YOU'LL DO", "Responsibilities", [
                         "Build Agent clients powered by our own models across Web, iOS and macOS.",
                         "Turn designs into client interfaces and interactions using Figma MCP and Coding Agents.",
                         "Integrate back-end services and Agent capabilities, and contribute to Agent architecture and feature development.",
                     ]),
                     ("WHO YOU ARE", "Requirements", [
                         "A background in computer science, electronic engineering, software engineering, AI or a related field, with proficiency in Coding Agents.",
                         "1–3 years of client development experience with at least one stack, such as iOS, Android, Flutter, React Native or desktop development, and the ability to build interfaces and interactions independently.",
                         "A strong interest in Agents and large language models, with an understanding of how they work.",
                         "A proactive learner and thoughtful problem solver who communicates clearly and works well with others.",
                     ]),
                     ("NICE TO HAVE", "Bonus points", [
                         "Experience building Agent products.",
                         "Hands-on experience with LLM API integration or prompt design.",
                         "Comfortable working in English.",
                     ]),
                 ]),
         fr=dict(name="Ingénieur Client Agent", tag="Expérimenté", meta="Expérimenté · Ingénierie client",
                 points=["Construire le client Agent de nos propres modèles : Web, iOS et macOS", "Développement client full-stack, de Figma MCP au Coding Agent"],
                 eyebrow="WE ARE HIRING · Expérimenté",
                 sections=[
                     ("WHAT YOU'LL DO", "Responsabilités", [
                         "Développer des clients Agent fondés sur nos propres modèles pour le Web, iOS et macOS.",
                         "Transformer les maquettes en interfaces et interactions côté client à l’aide de Figma MCP et de Coding Agents.",
                         "Intégrer les services back-end et les capacités des Agents, et contribuer à leur architecture et au développement de leurs fonctionnalités.",
                     ]),
                     ("WHO YOU ARE", "Profil recherché", [
                         "Formation en informatique, électronique, génie logiciel, IA ou dans un domaine connexe, avec une maîtrise des Coding Agents.",
                         "1 à 3 ans d’expérience en développement client avec au moins une technologie, comme iOS, Android, Flutter, React Native ou le développement d’applications de bureau, et la capacité à réaliser de façon autonome des interfaces et interactions.",
                         "Fort intérêt pour les Agents et les grands modèles de langage, avec une compréhension de leur fonctionnement.",
                         "Envie d’apprendre, capacité à analyser et résoudre les problèmes, communication claire et goût du travail en équipe.",
                     ]),
                     ("NICE TO HAVE", "Atouts", [
                         "Expérience du développement de produits Agent.",
                         "Expérience pratique de l’intégration d’API LLM ou de la conception de prompts.",
                         "Aisance pour travailler en anglais.",
                     ]),
                 ]),
         de=dict(name="Agent Client Engineer", tag="Berufserfahren", meta="Berufserfahren · Client-Engineering",
                 points=["Den Agent-Client für unsere eigenen Modelle bauen: Web, iOS und macOS", "Full-Stack-Client-Entwicklung von Figma MCP bis zum Coding Agent"],
                 eyebrow="WE ARE HIRING · Berufserfahren",
                 sections=[
                     ("WHAT YOU'LL DO", "Aufgaben", [
                         "Agent-Clients auf Basis unserer eigenen Modelle für Web, iOS und macOS entwickeln.",
                         "Mit Figma MCP und Coding Agents Designs in Client-Oberflächen und Interaktionen umsetzen.",
                         "Backend-Dienste und Agent-Funktionen integrieren und an der Agent-Architektur sowie der Entwicklung von Funktionen mitwirken.",
                     ]),
                     ("WHO YOU ARE", "Anforderungen", [
                         "Hintergrund in Informatik, Elektrotechnik, Softwaretechnik, KI oder einem verwandten Fach und sicherer Umgang mit Coding Agents.",
                         "1–3 Jahre Erfahrung in der Client-Entwicklung mit mindestens einer Technologie wie iOS, Android, Flutter, React Native oder Desktop-Entwicklung sowie die Fähigkeit, Oberflächen und Interaktionen selbstständig umzusetzen.",
                         "Großes Interesse an Agents und großen Sprachmodellen sowie Verständnis ihrer Funktionsweise.",
                         "Eigeninitiative beim Lernen, analytisches Denken und Problemlösungskompetenz sowie klare Kommunikation und Teamfähigkeit.",
                     ]),
                     ("NICE TO HAVE", "Pluspunkte", [
                         "Erfahrung mit der Entwicklung von Agent-Produkten.",
                         "Praktische Erfahrung mit der Integration von LLM-APIs oder Prompt-Design.",
                         "Sicheres Arbeiten auf Englisch.",
                     ]),
                 ])),
]


def esc(s):
    return html.escape(s, quote=False)


def attr(s):
    return html.escape(s, quote=True)


def items(lst):
    return "\n".join(f'          <li class="careers-item">{esc(t)}</li>' for t in lst)


def rel(from_dir, to_dir):
    """Relative URL prefix from one careers folder to another: "" for the same folder, else e.g. "../zh-cn/careers/"
    (from careers/) or "../../careers/" (from zh-cn/careers/)."""
    r = posixpath.relpath(to_dir, from_dir)
    return "" if r == "." else r + "/"


# Same two snippets as index.html (keep them in sync): the <head> language-memory redirect and the footer menu.
LANG_MEMORY_SCRIPT = """  <script>
    // Language memory. The footer menu stores the chosen language (localStorage "lm-lang"); from then on any
    // page served in another language jumps to its version in that language, resolved through the hreflang
    // alternates above (English when no version exists). No stored choice = first visit = the page as served.
    (() => { try {
      const pref = localStorage.getItem('lm-lang');
      if (!pref || pref === document.documentElement.lang) return;
      const alt = (code) => document.querySelector(`link[rel="alternate"][hreflang="${code}"]`);
      const target = alt(pref) || alt('en');
      if (!target) return;
      const path = new URL(target.href).pathname;
      const strip = (p) => p.replace(/index\\.html$/, '');
      if (strip(path) !== strip(location.pathname)) location.replace(path + location.search + location.hash);
    } catch (error) {} })();
  </script>"""

LANG_MENU_SCRIPT = """  <script>
    // Footer language menu (bottom right): opens upward over the button, closes on outside click / Escape.
    document.querySelectorAll('[data-lang-menu]').forEach((menu) => {
      const button = menu.querySelector('.lang-menu-button');
      const list = menu.querySelector('.lang-menu-list');
      const setOpen = (open) => { menu.dataset.open = String(open); button.setAttribute('aria-expanded', String(open)); list.hidden = !open; };
      button.addEventListener('click', () => setOpen(list.hidden));
      // Remember the choice before the link navigates; the <head> script in every page enforces it later.
      list.addEventListener('click', (event) => { const link = event.target.closest('a[lang]'); if (link) { try { localStorage.setItem('lm-lang', link.lang); } catch (error) {} } });
      addEventListener('click', (event) => { if (!menu.contains(event.target)) setOpen(false); });
      addEventListener('keydown', (event) => { if (event.key === 'Escape' && !list.hidden) { setOpen(false); button.focus(); } });
    });
  </script>"""


def footer_lang_menu(L, pagefile):
    """Footer language menu: every language links to the same page (index or role) in its own careers folder."""
    current = ' aria-current="page"'
    lis = []
    for code, label, key in LANGS:
        href = rel(UI[L]["dir"], UI[key]["dir"]) + pagefile
        lis.append(f'<li><a role="menuitem" lang="{code}" hreflang="{code}" href="{href or "./"}"{current if key == L else ""}>{label}</a></li>')
    label = next(label for code, label, key in LANGS if key == L)
    return ('<div class="lang-menu" data-lang-menu><ul class="lang-menu-list" id="lang-menu-list" role="menu" hidden>' + "".join(lis) + '</ul>'
            '<button class="lang-menu-button" type="button" aria-haspopup="menu" aria-expanded="false" aria-controls="lang-menu-list">'
            '<svg class="lang-menu-globe" aria-hidden="true" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/></svg>'
            f'<span class="lang-menu-label">{label}</span>'
            '<svg class="lang-menu-chevron" aria-hidden="true" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 9l6 6 6-6"/></svg></button></div>')


def page(L, pagefile, title, desc, body):
    ui = UI[L]
    alternates = "".join(f'  <link rel="alternate" hreflang="{code}" href="{SITE}/{UI[key]["dir"]}/{pagefile}">\n' for code, _, key in LANGS)
    alternates += f'  <link rel="alternate" hreflang="x-default" href="{SITE}/{UI["en"]["dir"]}/{pagefile}">\n'
    blurb, explore, approach, careers, contact, copyright = ui["footer"]
    head = HEAD.format(lang=ui["html_lang"], p=ui["prefix"], home=ui["home"], title=esc(title), desc=attr(desc), rev=REV,
                       alternates=alternates, langmem=LANG_MEMORY_SCRIPT,
                       nav_contact=esc(ui["nav_contact"]))
    return head + body + FOOTER.format(p=ui["prefix"], home=ui["home"], motion=MOTION,
                                       scroll=SMOOTH_SCROLL.format(prefix=ui["prefix"]),
                                       langmenu=footer_lang_menu(L, pagefile), langscript=LANG_MENU_SCRIPT,
                                       f_blurb=esc(blurb), f_explore=esc(explore), f_approach=esc(approach),
                                       f_careers=esc(careers), f_contact=esc(contact), f_copyright=esc(copyright))


def apply_card(eyebrow, h2, note, btn_label, subject, top=False):
    band = "apply-band apply-band-top" if top else "apply-band"
    mail = f"mailto:{EMAIL}?subject={attr(subject)}"
    eyebrow_html = f'        <p class="careers-eyebrow">{esc(eyebrow)}</p>\n' if eyebrow else ""
    return f"""    <section class="careers-band {band}">
      <div class="apply-card">
{eyebrow_html}        <h2>{esc(h2)}</h2>
        <p>{esc(note)}</p>
        <div class="apply-actions"><a class="btn-primary" href="{mail}">{esc(btn_label)}&nbsp;&nbsp;→</a></div>
      </div>
    </section>
"""


def role_row(r, L):
    d, ui = r[L], UI[L]
    if r["slug"]:
        body = (f'        <ul class="role-points">\n{items(d["points"])}\n        </ul>\n'
                f'        <div class="role-action"><a class="btn-outline" href="{r["slug"]}.html">{esc(ui["view"])} <span aria-hidden="true">→</span></a></div>')
    else:
        body = f'        <p class="role-soon">{esc(d["soon"])}</p>\n        <div class="role-action"></div>'
    return f"""      <li class="role-row">
        <div class="role-heading"><h2 class="role-name">{esc(d["name"])}</h2><p class="role-meta">{esc(d["meta"])}</p></div>
{body}
      </li>
"""


def build_index(L):
    ui = UI[L]
    rows = "".join(role_row(r, L) for r in ROLES)
    eyebrow, h2, note, btn, subject = ui["open_apply"]
    # The eyebrow and "Open roles" stay English in every language, as designed for the 中文 page in Figma.
    # Back from the list lands on the home page's Join section (where "See open roles" lives), not the top.
    body = f"""    <a class="careers-back" href="{ui['home']}#join" aria-label="{attr(ui['back_home'])}" title="{attr(ui['back_home'])}"><span aria-hidden="true">←</span></a>
    <section class="careers-band careers-title">
      <p class="careers-eyebrow">Careers · We are hiring</p>
      <h1>Open roles</h1>
      <p class="careers-intro">{esc(ui["intro"].format(n=len(ROLES)))}</p>
    </section>
    <section class="careers-band">
      <ul class="roles-list">
{rows}      </ul>
    </section>
""" + apply_card(eyebrow, h2, note.format(email=EMAIL), btn, subject, top=True)
    return page(L, "", "Open roles", ui["index_desc"], body)


def build_role(r, L):
    d, ui = r[L], UI[L]
    secs = "\n".join(f"""      <section class="careers-section">
        <div class="section-heading"><p class="careers-eyebrow">{esc(eb)}</p><h2>{esc(h)}</h2></div>
        <ul>
{items(lst)}
        </ul>
      </section>""" for eb, h, lst in d["sections"])
    subject = f"{d['name']} · {d['tag']}"
    _, h2, note, btn = ui["apply"]
    body = f"""    <a class="careers-back" href="./" aria-label="{attr(ui['back'])}" title="{attr(ui['back'])}"><span aria-hidden="true">←</span></a>
    <section class="careers-band careers-title">
      <p class="careers-eyebrow">{esc(d["eyebrow"])}</p>
      <h1>{esc(d["name"])}</h1>
    </section>
    <div class="careers-band careers-sections">
{secs}
    </div>
""" + apply_card(None, h2, note.format(email=EMAIL, subject=subject), btn, subject)
    return page(L, f"{r['slug']}.html", ui["role_title"].format(name=d["name"], tag=d["tag"]),
                ui["role_desc"].format(name=d["name"], tag=d["tag"]), body)


for L, ui in UI.items():
    out = f"{ROOT}/{ui['dir']}"
    os.makedirs(out, exist_ok=True)
    with open(f"{out}/index.html", "w") as f:
        f.write(build_index(L))
    for r in ROLES:
        if r["slug"]:
            with open(f"{out}/{r['slug']}.html", "w") as f:
                f.write(build_role(r, L))
    print(L, "→", sorted(os.listdir(out)))
