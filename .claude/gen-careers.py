#!/usr/bin/env python3
"""Generate the careers pages in the site's four languages from one data table:
  careers/index.html,    careers/<slug>.html     中文
  careers/en/index.html, careers/en/<slug>.html  English (site default)
  careers/fr/…, careers/de/…                     Français / Deutsch (first-pass machine translation)
Header/footer markup mirrors index.html (asset paths rewritten with ../ or ../../). Every page links to
its siblings through the footer language menu and hreflang alternates; the <head> language-memory
script keeps a visitor inside the language they chose."""
import html, os, posixpath

ROOT = "/Users/zhangouqi/Documents/learning machine/deep-claw-main/official-website"
SITE = "https://learning-machine.ai"
REV = "figma-1617-19731-v45"
EMAIL = "careers@learning-machine.ai"

# Footer language menu, in display order: (html lang code, label, UI key).
LANGS = [("en", "English", "en"), ("zh-CN", "中文", "zh"), ("fr", "Français", "fr"), ("de", "Deutsch", "de")]

# Per-language UI strings. `dir` is the site-relative folder of that language's careers pages; `home` is the
# same-language home page relative to `dir`. Tuples: open_apply = (eyebrow, h2, note, button, mail subject);
# apply = (eyebrow, h2, note, button); footer = (blurb, explore, approach, careers, contact, copyright).
UI = {
    "zh": dict(html_lang="zh-CN", dir="careers", home="../zh/",
               nav_careers="招聘", nav_contact="联系我们",
               intro="目前开放 {n} 个岗位 · 北京研发中心。点击岗位查看职位要求、待遇与投递方式。",
               view="查看详情", back="返回职位列表", back_home="返回首页",
               open_apply=("Open application · 自荐", "没有合适的岗位？直接把简历发给我们", "邮件发送至 {email}，注明你感兴趣的方向。", "自荐投递", "自荐投递"),
               apply=("Apply · 简历投递", "简历投递", "邮件发送至 {email}，主题请注明「{subject}」。", "立即投递"),
               index_desc="Learning Machine 北京研发中心开放岗位：Agent 全栈研发、客户端、视觉设计。",
               role_title="{name}（{tag}）", role_desc="Learning Machine 招聘：{name}（{tag}），北京 · 中关村。",
               footer=("打造新一代能在推理时真正学习与适应的 AI 模型——让每家公司都拥有自适应的智能。", "探索", "我们的方法", "招聘", "联系我们", "© 2026 Learning Machine Co. 保留所有权利。")),
    "en": dict(html_lang="en", dir="careers/en", home="../../",
               nav_careers="Careers", nav_contact="Contact",
               intro="{n} open roles at our Beijing R&D center. Open a role for requirements, package and how to apply.",
               view="View details", back="Back to open roles", back_home="Back to home",
               open_apply=("Open application", "No matching role? Send us your CV anyway", "Email {email} and tell us which direction interests you.", "Send open application", "Open application"),
               apply=("Apply", "Send your CV", "Email {email} with the subject line “{subject}”.", "Apply now"),
               index_desc="Open roles at Learning Machine's Beijing R&D center: Agent full-stack engineering, client engineering, visual design.",
               role_title="{name} ({tag})", role_desc="Learning Machine is hiring: {name} ({tag}), Beijing · Zhongguancun.",
               footer=("Building the next generation of AI models that truly learn and adapt at inference time — adaptive intelligence for every company.", "Explore", "Approach", "Careers", "Contact", "© 2026 Learning Machine Co. All rights reserved.")),
    "fr": dict(html_lang="fr", dir="careers/fr", home="../../fr/",
               nav_careers="Carrières", nav_contact="Contact",
               intro="{n} postes ouverts dans notre centre de R&D de Pékin. Ouvrez un poste pour voir les exigences, la rémunération et comment postuler.",
               view="Voir le poste", back="Retour aux postes", back_home="Retour à l'accueil",
               open_apply=("Candidature spontanée", "Aucun poste ne vous correspond ? Envoyez-nous quand même votre CV", "Écrivez à {email} en précisant le domaine qui vous intéresse.", "Envoyer une candidature spontanée", "Candidature spontanée"),
               apply=("Postuler", "Envoyez votre CV", "Écrivez à {email} avec pour objet « {subject} ».", "Postuler"),
               index_desc="Postes ouverts au centre de R&D de Learning Machine à Pékin : ingénierie full-stack Agent, ingénierie client, design visuel.",
               role_title="{name} ({tag})", role_desc="Learning Machine recrute : {name} ({tag}), Pékin · Zhongguancun.",
               footer=("Nous construisons la prochaine génération de modèles d'IA qui apprennent et s'adaptent vraiment au moment de l'inférence — une intelligence adaptative pour chaque entreprise.", "Explorer", "Approche", "Carrières", "Contact", "© 2026 Learning Machine Co. Tous droits réservés.")),
    "de": dict(html_lang="de", dir="careers/de", home="../../de/",
               nav_careers="Karriere", nav_contact="Kontakt",
               intro="{n} offene Stellen in unserem F&E-Zentrum in Peking. Öffne eine Stelle für Anforderungen, Vergütung und Bewerbung.",
               view="Details ansehen", back="Zurück zu den Stellen", back_home="Zur Startseite",
               open_apply=("Initiativbewerbung", "Keine passende Stelle? Schick uns trotzdem deinen Lebenslauf", "Schreib an {email} und nenne die Richtung, die dich interessiert.", "Initiativbewerbung senden", "Initiativbewerbung"),
               apply=("Bewerben", "Schick uns deinen Lebenslauf", "Schreib an {email} mit dem Betreff „{subject}“.", "Jetzt bewerben"),
               index_desc="Offene Stellen im Pekinger F&E-Zentrum von Learning Machine: Agent-Full-Stack-Engineering, Client-Engineering, Visual Design.",
               role_title="{name} ({tag})", role_desc="Learning Machine sucht: {name} ({tag}), Peking · Zhongguancun.",
               footer=("Wir bauen die nächste Generation von KI-Modellen, die zur Inferenzzeit wirklich lernen und sich anpassen — adaptive Intelligenz für jedes Unternehmen.", "Entdecken", "Ansatz", "Karriere", "Kontakt", "© 2026 Learning Machine Co. Alle Rechte vorbehalten.")),
}
for ui in UI.values():
    ui["prefix"] = "../" * (ui["dir"].count("/") + 1)

HEAD = """<!doctype html>
<html lang="{lang}" data-variant="light" data-ab-variant="b">
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
    <nav class="light-nav" aria-label="Primary navigation"><a href="./">{nav_careers}</a><a class="light-nav-contact" href="mailto:contact@learning-machine.ai">{nav_contact}</a></nav>
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
# Copy is the user's postings verbatim (zh) and faithful translations (en / fr / de) — do not paraphrase.
ROLES = [
    dict(slug="agent-fullstack-campus",
         zh=dict(name="Agent 全栈研发工程师", tag="校招 / 实习", meta="校招 / 实习 · 北京 · 研发",
                 points=["开发自有模型的 Agent，有资深 Mentor 和团队协作", "全栈客户端功能开发，根据 Figma MCP 到 Coding Agent 进行前端页面开发"],
                 eyebrow="WE ARE HIRING · 校招 / 实习",
                 facts=[("LOCATION · 地点", "北京 · 中关村"), ("OFFER · 校招待遇", "对标国内一线大厂"), ("INTERNSHIP · 实习工资", "RMB 500+ / 天，具体面议")],
                 sections=[
                     ("WHAT YOU'LL DO", "职位要求", ["开发自有模型的 Agent，有资深 Mentor 和团队协作", "全栈客户端功能开发，根据 Figma MCP 到 Coding Agent 进行前端页面开发", "服务端逻辑对接，承接 Agentic 架构，也可参与到 Agentic 架构设计和开发中"]),
                     ("WHO YOU ARE", "希望你是", ["计算机、电子信息、软件工程、人工智能等相关专业，熟练使用 Coding Agent，在校期间有相关课程设计、项目实践经验者优先。", "具备扎实的计算机基础知识，掌握数据结构、算法、计算机网络、操作系统等核心知识点。", "对 Agentic 架构、大模型有浓厚兴趣，了解其基本工作原理，有大模型 API 集成、Prompt 设计相关实践经验者优先。", "具备一定的客户端研发能力，熟悉至少一种客户端开发技术（iOS / Android / Flutter / React Native / PC 端桌面应用），能独立完成简单界面、交互逻辑开发。", "具备基础的后端研发能力，熟悉至少一种后端语言（Java / Go / Python / Node.js），了解 RESTful API、数据库基础，能完成简单后端接口开发与调试。", "具备良好的学习能力、问题排查能力和逻辑思维，积极主动，乐于接受新挑战，有较强的沟通能力和团队协作意识。"]),
                     ("NICE TO HAVE", "加分项", ["英文办公", "有 Agent 类产品研发经验", "有跨端（移动端 + PC 端）研发经验", "开源项目贡献者"]),
                 ]),
         en=dict(name="Agent Full-Stack Engineer", tag="Campus / Intern", meta="Campus / Intern · Beijing · Engineering",
                 points=["Build Agents on our own models, with senior mentors and a collaborative team", "Full-stack client development: front-end pages built from Figma MCP through Coding Agent"],
                 eyebrow="WE ARE HIRING · Campus / Intern",
                 facts=[("LOCATION", "Beijing · Zhongguancun"), ("OFFER", "Matches top-tier tech companies"), ("INTERNSHIP", "RMB 500+ / day, negotiable")],
                 sections=[
                     ("WHAT YOU'LL DO", "Responsibilities", ["Build Agents on our own models, working with senior mentors and the team", "Full-stack client feature development: front-end pages built from Figma MCP through Coding Agent", "Integrate server-side logic and carry the Agentic architecture; you can also take part in designing and building it"]),
                     ("WHO YOU ARE", "Requirements", ["Majoring in computer science, electronic information, software engineering, AI or a related field; fluent with Coding Agents. Relevant coursework or project experience is a plus.", "Solid computer-science fundamentals: data structures, algorithms, networking and operating systems.", "Strong interest in Agentic architectures and large models, with an understanding of how they work. Hands-on experience with LLM API integration or prompt design is a plus.", "Some client-side development ability: at least one client stack (iOS / Android / Flutter / React Native / desktop) and able to build simple UI and interaction logic on your own.", "Basic back-end ability: at least one back-end language (Java / Go / Python / Node.js), familiar with RESTful APIs and database basics, able to build and debug simple endpoints.", "A fast learner and a capable debugger with clear logical thinking; proactive, open to new challenges, a strong communicator and team player."]),
                     ("NICE TO HAVE", "Bonus points", ["Comfortable working in English", "Experience building Agent products", "Cross-platform (mobile + desktop) development experience", "Open-source contributor"]),
                 ]),
         fr=dict(name="Ingénieur Full-Stack Agent", tag="Campus / Stage", meta="Campus / Stage · Pékin · Ingénierie",
                 points=["Construire des Agents sur nos propres modèles, avec des mentors seniors et une équipe collaborative", "Développement client full-stack : des pages front-end construites de Figma MCP jusqu'au Coding Agent"],
                 eyebrow="WE ARE HIRING · Campus / Stage",
                 facts=[("LIEU", "Pékin · Zhongguancun"), ("OFFRE", "Alignée sur les grands groupes tech"), ("STAGE", "500+ RMB / jour, négociable")],
                 sections=[
                     ("WHAT YOU'LL DO", "Responsabilités", ["Construire des Agents sur nos propres modèles, aux côtés de mentors seniors et de l'équipe", "Développement full-stack de fonctionnalités client : pages front-end construites de Figma MCP jusqu'au Coding Agent", "Intégrer la logique serveur et porter l'architecture agentique ; vous pouvez aussi participer à sa conception et à son développement"]),
                     ("WHO YOU ARE", "Profil recherché", ["Études en informatique, électronique et information, génie logiciel, IA ou domaine proche ; à l'aise avec les Coding Agents. Projets ou cours pertinents appréciés.", "Bases solides en informatique : structures de données, algorithmes, réseaux et systèmes d'exploitation.", "Fort intérêt pour les architectures agentiques et les grands modèles, avec une compréhension de leur fonctionnement. Une expérience d'intégration d'API LLM ou de conception de prompts est un plus.", "Une certaine capacité de développement client : au moins une stack (iOS / Android / Flutter / React Native / desktop) et savoir réaliser seul des interfaces et des interactions simples.", "Bases back-end : au moins un langage (Java / Go / Python / Node.js), connaissance des API RESTful et des bases de données, capacité à développer et déboguer des endpoints simples.", "Apprentissage rapide, bon sens du débogage et esprit logique ; proactif, ouvert aux nouveaux défis, bon communicant et esprit d'équipe."]),
                     ("NICE TO HAVE", "Atouts", ["À l'aise pour travailler en anglais", "Expérience de développement de produits Agent", "Expérience de développement multiplateforme (mobile + desktop)", "Contributeur open source"]),
                 ]),
         de=dict(name="Agent Full-Stack Engineer", tag="Campus / Praktikum", meta="Campus / Praktikum · Peking · Engineering",
                 points=["Agents auf unseren eigenen Modellen bauen, mit erfahrenen Mentoren und einem kollaborativen Team", "Full-Stack-Client-Entwicklung: Frontend-Seiten von Figma MCP über den Coding Agent bis zur Auslieferung"],
                 eyebrow="WE ARE HIRING · Campus / Praktikum",
                 facts=[("STANDORT", "Peking · Zhongguancun"), ("ANGEBOT", "Auf dem Niveau der großen Tech-Konzerne"), ("PRAKTIKUM", "500+ RMB / Tag, verhandelbar")],
                 sections=[
                     ("WHAT YOU'LL DO", "Aufgaben", ["Agents auf unseren eigenen Modellen bauen, gemeinsam mit erfahrenen Mentoren und dem Team", "Full-Stack-Entwicklung von Client-Funktionen: Frontend-Seiten von Figma MCP über den Coding Agent", "Serverseitige Logik anbinden und die agentische Architektur tragen; du kannst auch an ihrem Entwurf und Aufbau mitwirken"]),
                     ("WHO YOU ARE", "Profil", ["Studium der Informatik, Elektronik und Informationstechnik, Softwaretechnik, KI oder eines verwandten Fachs; sicher im Umgang mit Coding Agents. Passende Kurse oder Projekte sind ein Plus.", "Solide Informatik-Grundlagen: Datenstrukturen, Algorithmen, Netzwerke und Betriebssysteme.", "Starkes Interesse an agentischen Architekturen und großen Modellen und ein Verständnis ihrer Funktionsweise. Praxis mit LLM-API-Integration oder Prompt-Design ist ein Plus.", "Etwas Client-Entwicklungserfahrung: mindestens ein Client-Stack (iOS / Android / Flutter / React Native / Desktop), einfache Oberflächen und Interaktionen selbstständig umsetzbar.", "Backend-Grundlagen: mindestens eine Backend-Sprache (Java / Go / Python / Node.js), vertraut mit RESTful APIs und Datenbank-Grundlagen, einfache Endpunkte bauen und debuggen.", "Schnell lernend, gut im Debuggen und logisch denkend; proaktiv, offen für neue Herausforderungen, kommunikationsstark und teamorientiert."]),
                     ("NICE TO HAVE", "Pluspunkte", ["Sicheres Arbeiten auf Englisch", "Erfahrung im Bau von Agent-Produkten", "Erfahrung in plattformübergreifender Entwicklung (Mobile + Desktop)", "Open-Source-Beiträge"]),
                 ])),
    dict(slug="agent-fullstack",
         zh=dict(name="Agent 全栈研发工程师", tag="社招", meta="社招 · 北京 · 研发",
                 points=["负责 AI Agent 个人助理客户端全栈研发，端到端落地核心功能", "主导核心交互逻辑、任务调度与上下文管理，结合大模型能力"],
                 eyebrow="WE ARE HIRING · 社招",
                 facts=[("LOCATION · 地点", "北京 · 中关村"), ("SALARY · 年薪", "30–60 万"), ("BENEFITS · 福利", "六险一金")],
                 sections=[
                     ("WHAT YOU'LL DO", "岗位职责", ["负责 AI Agent 个人助理客户端全栈研发，涵盖前端 / 移动端、后端接口、AI 能力集成，端到端实现个人助理的核心功能落地，确保产品流畅性、稳定性和用户体验。", "主导 Agent 个人助理的核心交互逻辑、任务调度、上下文管理研发，结合大模型能力，实现智能对话、任务拆解、多工具调用（日程、邮件、文件管理等）、个性化推荐等核心场景。", "负责客户端与大模型 API、第三方工具（办公软件、生活服务接口等）的对接与调试，优化接口性能、数据传输效率，解决跨端兼容、网络异常等问题。", "参与产品需求评审、技术方案设计，结合 AI Agent 特性提出客户端技术优化建议，推动产品迭代升级；负责技术文档编写、代码评审，保障研发质量。", "关注 AI Agent、大模型应用、客户端研发前沿技术，将新技术、新方案融入产品研发，提升产品竞争力和研发效率。", "配合测试、产品团队，完成功能测试、Bug 修复、用户反馈优化，确保产品上线质量；协助搭建客户端研发规范和流程。"]),
                     ("CORE REQUIREMENTS", "核心要求", ["本科及以上学历，计算机、电子信息、软件工程等相关专业，3 年及以上全栈研发经验，熟练使用 Coding Agent，有 AI Agent、个人助理类产品研发经验者优先。", "具备扎实的客户端研发能力，熟练掌握至少一种客户端开发技术，能独立完成客户端界面、交互逻辑开发。", "具备后端研发能力，熟练掌握至少一种后端语言，熟悉 RESTful API、微服务架构，能独立开发、调试后端接口，处理数据存储与交互。", "了解大模型的工作原理，有大模型 API 集成、Prompt 工程、Agent 任务调度、上下文管理相关经验者优先。", "具备良好的问题排查能力，能快速定位并解决客户端、后端、AI 集成过程中的技术问题，有跨端开发、性能优化经验者优先。"]),
                     ("SKILLS", "技能要求", ["前端 / 客户端：熟练掌握 Flutter / React Native，或 iOS（Swift / OC），熟悉组件化、工程化开发，了解 UI/UX 设计规范。", "后端：熟练掌握 Go / Python / Java 中的一种或多种，熟悉 MySQL、MongoDB 等数据库，了解 Redis 缓存、消息队列等中间件，具备接口设计、性能优化能力。", "AI 相关：熟悉大模型 API 调用、Prompt 设计，了解 Agent 框架（如 LangChain、LlamaIndex），有智能对话、任务拆解、多工具集成经验者加分。", "其他：熟悉 Git 版本控制，具备良好的代码规范和文档编写习惯；具备较强的学习能力、沟通能力和团队协作能力，能快速适应 AI 技术迭代节奏。"]),
                     ("NICE TO HAVE", "加分项", ["有个人助理类、AI Agent 类产品全栈研发经验，或主导过相关产品从 0 到 1 落地。", "熟悉大模型微调、Agent 智能调度策略、上下文记忆优化等相关技术。", "有跨端（移动端 + PC 端）研发经验，能独立完成全平台客户端适配。", "开源项目贡献者，或有个人技术博客、相关技术成果展示。"]),
                 ]),
         en=dict(name="Agent Full-Stack Engineer", tag="Experienced hire", meta="Experienced hire · Beijing · Engineering",
                 points=["Own full-stack development of the AI Agent personal-assistant client and ship its core features end to end", "Lead core interaction logic, task scheduling and context management on top of large-model capabilities"],
                 eyebrow="WE ARE HIRING · Experienced hire",
                 facts=[("LOCATION", "Beijing · Zhongguancun"), ("SALARY", "RMB 300–600K / year"), ("BENEFITS", "Full insurance & housing fund")],
                 sections=[
                     ("WHAT YOU'LL DO", "Responsibilities", ["Own full-stack development of the AI Agent personal-assistant client — front-end / mobile, back-end APIs and AI capability integration — delivering the assistant's core features end to end with a smooth, stable experience.", "Lead development of the assistant's core interaction logic, task scheduling and context management; use large-model capabilities to deliver intelligent conversation, task decomposition, multi-tool calling (calendar, email, file management and more) and personalised recommendations.", "Integrate and debug the client against large-model APIs and third-party tools (office software, lifestyle-service APIs and others); optimise API performance and data transfer, and resolve cross-platform compatibility and network-failure issues.", "Take part in requirement reviews and technical design; propose client-side improvements grounded in how AI Agents work and drive product iteration. Write technical documentation and review code to keep engineering quality high.", "Follow the frontier of AI Agents, large-model applications and client engineering, and bring new techniques and approaches into the product to raise competitiveness and engineering efficiency.", "Work with QA and product on feature testing, bug fixing and user-feedback improvements to ensure release quality; help establish client engineering standards and processes."]),
                     ("CORE REQUIREMENTS", "Requirements", ["Bachelor's degree or above in computer science, electronic information, software engineering or a related field; 3+ years of full-stack experience; fluent with Coding Agents. Experience building AI Agent or personal-assistant products is a plus.", "Solid client-side skills: expert in at least one client stack and able to build client UI and interaction logic independently.", "Back-end skills: expert in at least one back-end language, familiar with RESTful APIs and microservice architecture, able to build and debug endpoints and handle data storage and exchange independently.", "Understand how large models work; experience with LLM API integration, prompt engineering, Agent task scheduling or context management is a plus.", "Strong debugging skills: quick to locate and fix issues across client, back-end and AI integration. Cross-platform development or performance-optimisation experience is a plus."]),
                     ("SKILLS", "Skills", ["Front-end / client: proficient in Flutter / React Native or iOS (Swift / Objective-C); familiar with component-based, engineered development and UI/UX design guidelines.", "Back-end: proficient in one or more of Go / Python / Java; familiar with MySQL, MongoDB and other databases, plus middleware such as Redis caching and message queues; able to design APIs and optimise performance.", "AI: familiar with LLM API calls and prompt design; know Agent frameworks such as LangChain and LlamaIndex. Experience with intelligent conversation, task decomposition or multi-tool integration is a plus.", "Other: fluent with Git; good coding standards and documentation habits; strong learning, communication and teamwork skills, able to keep pace with fast AI iteration."]),
                     ("NICE TO HAVE", "Bonus points", ["Full-stack experience on personal-assistant or AI Agent products, or having led such a product from zero to launch.", "Familiar with large-model fine-tuning, Agent scheduling strategies or context-memory optimisation.", "Cross-platform (mobile + desktop) experience, able to adapt a client to every platform independently.", "Open-source contributor, or a personal tech blog / portfolio of technical work."]),
                 ]),
         fr=dict(name="Ingénieur Full-Stack Agent", tag="Expérimenté", meta="Expérimenté · Pékin · Ingénierie",
                 points=["Piloter le développement full-stack du client assistant personnel AI Agent et livrer ses fonctionnalités clés de bout en bout", "Diriger la logique d'interaction, l'ordonnancement des tâches et la gestion du contexte, sur la base des grands modèles"],
                 eyebrow="WE ARE HIRING · Expérimenté",
                 facts=[("LIEU", "Pékin · Zhongguancun"), ("SALAIRE", "300–600 K RMB / an"), ("AVANTAGES", "Assurances complètes et fonds logement")],
                 sections=[
                     ("WHAT YOU'LL DO", "Responsabilités", ["Piloter le développement full-stack du client assistant personnel AI Agent — front-end / mobile, API back-end et intégration des capacités IA — en livrant ses fonctionnalités clés de bout en bout avec une expérience fluide et stable.", "Diriger le développement de la logique d'interaction, de l'ordonnancement des tâches et de la gestion du contexte ; s'appuyer sur les grands modèles pour offrir conversation intelligente, décomposition des tâches, appels multi-outils (agenda, e-mail, gestion de fichiers, etc.) et recommandations personnalisées.", "Intégrer et déboguer le client avec les API des grands modèles et les outils tiers (logiciels bureautiques, services du quotidien, etc.) ; optimiser les performances des API et les transferts de données, résoudre les problèmes de compatibilité multiplateforme et de réseau.", "Participer aux revues de besoins et à la conception technique ; proposer des améliorations côté client fondées sur le fonctionnement des AI Agents et faire avancer le produit. Rédiger la documentation technique et relire le code pour garantir la qualité.", "Suivre l'état de l'art des AI Agents, des applications de grands modèles et du développement client, et intégrer les nouvelles techniques au produit pour renforcer sa compétitivité et l'efficacité de l'équipe.", "Collaborer avec les équipes QA et produit sur les tests fonctionnels, la correction de bugs et les retours utilisateurs pour garantir la qualité des mises en production ; contribuer aux standards et processus de développement client."]),
                     ("CORE REQUIREMENTS", "Exigences", ["Licence ou plus en informatique, électronique et information, génie logiciel ou domaine proche ; 3 ans et plus d'expérience full-stack ; à l'aise avec les Coding Agents. Une expérience sur des produits AI Agent ou assistant personnel est un plus.", "Solides compétences client : maîtrise d'au moins une stack client et capacité à réaliser seul interfaces et logique d'interaction.", "Compétences back-end : maîtrise d'au moins un langage back-end, connaissance des API RESTful et des architectures microservices, capacité à développer et déboguer des endpoints et à gérer le stockage et les échanges de données.", "Compréhension du fonctionnement des grands modèles ; une expérience d'intégration d'API LLM, de prompt engineering, d'ordonnancement de tâches d'Agent ou de gestion du contexte est un plus.", "Bonnes capacités de débogage : localiser et corriger rapidement les problèmes côté client, back-end et intégration IA. Une expérience multiplateforme ou d'optimisation des performances est un plus."]),
                     ("SKILLS", "Compétences", ["Front-end / client : maîtrise de Flutter / React Native ou d'iOS (Swift / Objective-C) ; familiarité avec le développement par composants et industrialisé, ainsi qu'avec les règles de design UI/UX.", "Back-end : maîtrise d'un ou plusieurs langages parmi Go / Python / Java ; connaissance de MySQL, MongoDB et autres bases de données, ainsi que de middlewares comme le cache Redis et les files de messages ; capacité à concevoir des API et à optimiser les performances.", "IA : familiarité avec les appels d'API LLM et la conception de prompts ; connaissance de frameworks d'Agent comme LangChain et LlamaIndex. Une expérience en conversation intelligente, décomposition de tâches ou intégration multi-outils est un plus.", "Autres : maîtrise de Git ; bonnes pratiques de code et de documentation ; fortes capacités d'apprentissage, de communication et de travail en équipe, pour suivre le rythme rapide de l'IA."]),
                     ("NICE TO HAVE", "Atouts", ["Expérience full-stack sur des produits assistant personnel ou AI Agent, ou avoir mené un tel produit de zéro au lancement.", "Connaissance du fine-tuning des grands modèles, des stratégies d'ordonnancement d'Agent ou de l'optimisation de la mémoire de contexte.", "Expérience multiplateforme (mobile + desktop), capacité à adapter seul un client à toutes les plateformes.", "Contributeur open source, ou blog technique personnel / portfolio de réalisations techniques."]),
                 ]),
         de=dict(name="Agent Full-Stack Engineer", tag="Berufserfahren", meta="Berufserfahren · Peking · Engineering",
                 points=["Die Full-Stack-Entwicklung des KI-Agent-Assistenten-Clients verantworten und seine Kernfunktionen Ende-zu-Ende ausliefern", "Interaktionslogik, Aufgabenplanung und Kontextverwaltung auf Basis großer Modelle leiten"],
                 eyebrow="WE ARE HIRING · Berufserfahren",
                 facts=[("STANDORT", "Peking · Zhongguancun"), ("GEHALT", "300–600 T RMB / Jahr"), ("LEISTUNGEN", "Volle Sozialversicherung & Wohnungsfonds")],
                 sections=[
                     ("WHAT YOU'LL DO", "Aufgaben", ["Die Full-Stack-Entwicklung des KI-Agent-Assistenten-Clients verantworten — Frontend / Mobile, Backend-APIs und Integration der KI-Fähigkeiten — und die Kernfunktionen des Assistenten Ende-zu-Ende mit flüssiger, stabiler Nutzererfahrung ausliefern.", "Die Entwicklung von Interaktionslogik, Aufgabenplanung und Kontextverwaltung leiten; mit großen Modellen intelligente Dialoge, Aufgabenzerlegung, Multi-Tool-Aufrufe (Kalender, E-Mail, Dateiverwaltung u. a.) und personalisierte Empfehlungen umsetzen.", "Den Client an LLM-APIs und Drittanbieter-Tools (Office-Software, Alltagsdienste u. a.) anbinden und debuggen; API-Performance und Datenübertragung optimieren, Kompatibilitäts- und Netzwerkprobleme lösen.", "An Anforderungs-Reviews und technischem Design mitwirken; clientseitige Verbesserungen aus der Funktionsweise von KI-Agents ableiten und die Produktentwicklung vorantreiben. Technische Dokumentation schreiben und Code reviewen, um die Qualität zu sichern.", "Die Entwicklung bei KI-Agents, LLM-Anwendungen und Client-Engineering verfolgen und neue Techniken ins Produkt bringen, um Wettbewerbsfähigkeit und Effizienz zu steigern.", "Mit QA und Produkt an Funktionstests, Bugfixes und Nutzerfeedback arbeiten, um die Release-Qualität zu sichern; beim Aufbau von Standards und Prozessen für die Client-Entwicklung mithelfen."]),
                     ("CORE REQUIREMENTS", "Anforderungen", ["Bachelor oder höher in Informatik, Elektronik und Informationstechnik, Softwaretechnik oder einem verwandten Fach; 3+ Jahre Full-Stack-Erfahrung; sicher im Umgang mit Coding Agents. Erfahrung mit KI-Agent- oder Assistenten-Produkten ist ein Plus.", "Solide Client-Kompetenz: mindestens einen Client-Stack beherrschen und Oberflächen sowie Interaktionslogik selbstständig umsetzen.", "Backend-Kompetenz: mindestens eine Backend-Sprache beherrschen, vertraut mit RESTful APIs und Microservice-Architekturen, Endpunkte selbstständig bauen und debuggen, Datenspeicherung und -austausch handhaben.", "Verständnis der Funktionsweise großer Modelle; Erfahrung mit LLM-API-Integration, Prompt Engineering, Agent-Aufgabenplanung oder Kontextverwaltung ist ein Plus.", "Gutes Debugging: Probleme in Client, Backend und KI-Integration schnell finden und beheben. Erfahrung mit plattformübergreifender Entwicklung oder Performance-Optimierung ist ein Plus."]),
                     ("SKILLS", "Kenntnisse", ["Frontend / Client: sicher in Flutter / React Native oder iOS (Swift / Objective-C); vertraut mit komponentenbasierter, industrialisierter Entwicklung und UI/UX-Richtlinien.", "Backend: sicher in einer oder mehreren Sprachen aus Go / Python / Java; vertraut mit MySQL, MongoDB und anderen Datenbanken sowie Middleware wie Redis-Cache und Message Queues; API-Design und Performance-Optimierung.", "KI: vertraut mit LLM-API-Aufrufen und Prompt-Design; Kenntnis von Agent-Frameworks wie LangChain und LlamaIndex. Erfahrung mit intelligenten Dialogen, Aufgabenzerlegung oder Multi-Tool-Integration ist ein Plus.", "Sonstiges: sicher mit Git; gute Code- und Dokumentationsstandards; starke Lern-, Kommunikations- und Teamfähigkeit, um mit dem schnellen KI-Tempo Schritt zu halten."]),
                     ("NICE TO HAVE", "Pluspunkte", ["Full-Stack-Erfahrung mit Assistenten- oder KI-Agent-Produkten oder ein solches Produkt von null bis zum Launch geführt.", "Vertraut mit LLM-Fine-Tuning, Agent-Planungsstrategien oder Optimierung des Kontextgedächtnisses.", "Plattformübergreifende Erfahrung (Mobile + Desktop), einen Client selbstständig auf alle Plattformen bringen.", "Open-Source-Beiträge oder ein eigener Tech-Blog / ein Portfolio technischer Arbeiten."]),
                 ])),
    dict(slug=None,
         zh=dict(name="Agent 视觉设计实习生", tag="实习", meta="实习 · 北京 · 设计", soon="招聘详情即将发布"),
         en=dict(name="Agent Visual Design Intern", tag="Intern", meta="Intern · Beijing · Design", soon="Details coming soon"),
         fr=dict(name="Stagiaire Design Visuel Agent", tag="Stage", meta="Stage · Pékin · Design", soon="Détails à venir"),
         de=dict(name="Praktikum Visual Design Agent", tag="Praktikum", meta="Praktikum · Peking · Design", soon="Details folgen")),
    dict(slug="agent-client",
         zh=dict(name="Agent 客户端工程师", tag="社招", meta="社招 · 北京 · 客户端研发",
                 points=["开发自有模型的 Agent 客户端：Web、iOS、macOS", "从 Figma MCP 到 Coding Agent 的全栈客户端功能开发"],
                 eyebrow="WE ARE HIRING · 社招",
                 facts=[("LOCATION · 地点", "北京 · 中关村"), ("TYPE · 类型", "社招 · 全职"), ("COMPENSATION · 待遇", "面议")],
                 sections=[
                     ("WHAT YOU'LL DO", "职位要求", ["开发自有模型的 Agent 客户端，包括 Web、iOS、macOS", "全栈客户端功能开发，根据 Figma MCP 到 Coding Agent 进行前端页面开发", "服务端逻辑对接，承接 Agentic 架构，也可参与到 Agentic 架构设计和开发中"]),
                     ("WHO YOU ARE", "希望你是", ["计算机、电子信息、软件工程、人工智能等相关专业，熟练使用 Coding Agent。", "1–3 年客户端项目经验，熟悉至少一种客户端开发技术（iOS / Android / Flutter / React Native / PC 端桌面应用），能独立完成简单界面、交互逻辑开发。", "对 Agentic 架构、大模型有浓厚兴趣，了解其基本工作原理，有大模型 API 集成、Prompt 设计相关实践经验者优先。", "具备良好的学习能力、问题排查能力和逻辑思维，积极主动，乐于接受新挑战，有较强的沟通能力和团队协作意识。"]),
                     ("NICE TO HAVE", "加分项", ["英文办公", "有 Agent 类产品研发经验"]),
                 ]),
         en=dict(name="Agent Client Engineer", tag="Experienced hire", meta="Experienced hire · Beijing · Client engineering",
                 points=["Build the Agent client for our own models: Web, iOS and macOS", "Full-stack client development from Figma MCP to Coding Agent"],
                 eyebrow="WE ARE HIRING · Experienced hire",
                 facts=[("LOCATION", "Beijing · Zhongguancun"), ("TYPE", "Experienced hire · Full-time"), ("COMPENSATION", "Negotiable")],
                 sections=[
                     ("WHAT YOU'LL DO", "Responsibilities", ["Build the Agent client for our own models, including Web, iOS and macOS", "Full-stack client feature development: front-end pages built from Figma MCP through Coding Agent", "Integrate server-side logic and carry the Agentic architecture; you can also take part in designing and building it"]),
                     ("WHO YOU ARE", "Requirements", ["Background in computer science, electronic information, software engineering, AI or a related field; fluent with Coding Agents.", "1–3 years of client-side project experience with at least one client stack (iOS / Android / Flutter / React Native / desktop); able to build simple UI and interaction logic on your own.", "Strong interest in Agentic architectures and large models, with an understanding of how they work. Hands-on experience with LLM API integration or prompt design is a plus.", "A fast learner and a capable debugger with clear logical thinking; proactive, open to new challenges, a strong communicator and team player."]),
                     ("NICE TO HAVE", "Bonus points", ["Comfortable working in English", "Experience building Agent products"]),
                 ]),
         fr=dict(name="Ingénieur Client Agent", tag="Expérimenté", meta="Expérimenté · Pékin · Ingénierie client",
                 points=["Construire le client Agent de nos propres modèles : Web, iOS et macOS", "Développement client full-stack, de Figma MCP au Coding Agent"],
                 eyebrow="WE ARE HIRING · Expérimenté",
                 facts=[("LIEU", "Pékin · Zhongguancun"), ("TYPE", "Expérimenté · Temps plein"), ("RÉMUNÉRATION", "À négocier")],
                 sections=[
                     ("WHAT YOU'LL DO", "Responsabilités", ["Construire le client Agent de nos propres modèles, y compris Web, iOS et macOS", "Développement full-stack de fonctionnalités client : pages front-end construites de Figma MCP jusqu'au Coding Agent", "Intégrer la logique serveur et porter l'architecture agentique ; vous pouvez aussi participer à sa conception et à son développement"]),
                     ("WHO YOU ARE", "Profil recherché", ["Formation en informatique, électronique et information, génie logiciel, IA ou domaine proche ; à l'aise avec les Coding Agents.", "1 à 3 ans d'expérience sur des projets client avec au moins une stack (iOS / Android / Flutter / React Native / desktop) ; capacité à réaliser seul interfaces et interactions simples.", "Fort intérêt pour les architectures agentiques et les grands modèles, avec une compréhension de leur fonctionnement. Une expérience d'intégration d'API LLM ou de conception de prompts est un plus.", "Apprentissage rapide, bon sens du débogage et esprit logique ; proactif, ouvert aux nouveaux défis, bon communicant et esprit d'équipe."]),
                     ("NICE TO HAVE", "Atouts", ["À l'aise pour travailler en anglais", "Expérience de développement de produits Agent"]),
                 ]),
         de=dict(name="Agent Client Engineer", tag="Berufserfahren", meta="Berufserfahren · Peking · Client-Engineering",
                 points=["Den Agent-Client für unsere eigenen Modelle bauen: Web, iOS und macOS", "Full-Stack-Client-Entwicklung von Figma MCP bis zum Coding Agent"],
                 eyebrow="WE ARE HIRING · Berufserfahren",
                 facts=[("STANDORT", "Peking · Zhongguancun"), ("ART", "Berufserfahren · Vollzeit"), ("VERGÜTUNG", "Verhandelbar")],
                 sections=[
                     ("WHAT YOU'LL DO", "Aufgaben", ["Den Agent-Client für unsere eigenen Modelle bauen, einschließlich Web, iOS und macOS", "Full-Stack-Entwicklung von Client-Funktionen: Frontend-Seiten von Figma MCP über den Coding Agent", "Serverseitige Logik anbinden und die agentische Architektur tragen; du kannst auch an ihrem Entwurf und Aufbau mitwirken"]),
                     ("WHO YOU ARE", "Profil", ["Hintergrund in Informatik, Elektronik und Informationstechnik, Softwaretechnik, KI oder einem verwandten Fach; sicher im Umgang mit Coding Agents.", "1–3 Jahre Erfahrung in Client-Projekten mit mindestens einem Client-Stack (iOS / Android / Flutter / React Native / Desktop); einfache Oberflächen und Interaktionen selbstständig umsetzbar.", "Starkes Interesse an agentischen Architekturen und großen Modellen und ein Verständnis ihrer Funktionsweise. Praxis mit LLM-API-Integration oder Prompt-Design ist ein Plus.", "Schnell lernend, gut im Debuggen und logisch denkend; proaktiv, offen für neue Herausforderungen, kommunikationsstark und teamorientiert."]),
                     ("NICE TO HAVE", "Pluspunkte", ["Sicheres Arbeiten auf Englisch", "Erfahrung im Bau von Agent-Produkten"]),
                 ])),
]


def esc(s):
    return html.escape(s, quote=False)


def attr(s):
    return html.escape(s, quote=True)


def items(lst):
    return "\n".join(f'          <li class="careers-item">{esc(t)}</li>' for t in lst)


def rel(from_dir, to_dir):
    """Relative URL prefix from one careers folder to another: "" for the same folder, else "en/", "../fr/", "../"."""
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
                       nav_careers=esc(ui["nav_careers"]), nav_contact=esc(ui["nav_contact"]))
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
    body = f"""    <a class="careers-back" href="{ui['home']}" aria-label="{attr(ui['back_home'])}" title="{attr(ui['back_home'])}"><span aria-hidden="true">←</span></a>
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
    facts = "\n".join(f'        <li><p class="fact-label">{esc(l)}</p><p class="fact-value">{esc(v)}</p></li>' for l, v in d["facts"])
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
    <section class="careers-band">
      <ul class="facts">
{facts}
      </ul>
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
