#!/usr/bin/env python3
"""Generate the careers pages in both languages from one data table:
  careers/index.html, careers/<slug>.html          中文 (default)
  careers/en/index.html, careers/en/<slug>.html    English
Header/footer markup mirrors index.html (asset paths rewritten with ../ or ../../). The header
carries the 中文 | EN switch, which links to the same page in the other language."""
import html, os

ROOT = "/Users/zhangouqi/Documents/learning machine/deep-claw-main/official-website"
SITE = "https://learning-machine.ai"
REV = "figma-1617-19731-v42"
EMAIL = "careers@learning-machine.ai"

# Per-language UI strings. Tuples: open_apply = (eyebrow, h2, note, button, mail subject);
# apply = (eyebrow, h2, note, button).
UI = {
    "zh": dict(html_lang="zh-CN", prefix="../", outdir="careers",
               intro="目前开放 {n} 个岗位 · 北京研发中心。点击岗位查看职位要求、待遇与投递方式。",
               view="查看详情", back="返回职位列表",
               open_apply=("Open application · 自荐", "没有合适的岗位？直接把简历发给我们", "邮件发送至 {email}，注明你感兴趣的方向。", "自荐投递", "自荐投递"),
               apply=("Apply · 简历投递", "简历投递", "邮件发送至 {email}，主题请注明「{subject}」。", "立即投递"),
               index_desc="Learning Machine 北京研发中心开放岗位：Agent 全栈研发、客户端、视觉设计。",
               role_title="{name}（{tag}）", role_desc="Learning Machine 招聘：{name}（{tag}），北京 · 中关村。"),
    "en": dict(html_lang="en", prefix="../../", outdir="careers/en",
               intro="{n} open roles at our Beijing R&D center. Open a role for requirements, package and how to apply.",
               view="View details", back="Back to open roles",
               open_apply=("Open application", "No matching role? Send us your CV anyway", "Email {email} and tell us which direction interests you.", "Send open application", "Open application"),
               apply=("Apply", "Send your CV", "Email {email} with the subject line “{subject}”.", "Apply now"),
               index_desc="Open roles at Learning Machine's Beijing R&D center: Agent full-stack engineering, client engineering, visual design.",
               role_title="{name} ({tag})", role_desc="Learning Machine is hiring: {name} ({tag}), Beijing · Zhongguancun."),
}

HEAD = """<!doctype html>
<html lang="{lang}" data-variant="light" data-ab-variant="b">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#F4F0ED">
  <meta name="description" content="{desc}">
  <title>{title} | Learning Machine</title>
{alternates}  <link rel="icon" href="{p}assets/icons/favicon-adaptive.svg?v=1" type="image/svg+xml">
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
    <a href="{p}" class="light-brand" aria-label="Learning Machine home"><span class="brand-lockup"><span class="brand-mark" aria-hidden="true"><img class="brand-union" src="{p}assets/figma-106/0fc9ec76b79449656b5cb20fb65111dac0da7f74.svg" alt=""><img class="brand-base" src="{p}assets/figma-106/bb0bb4d59834c3b5c02cce512ab83e6722cc4dc8.svg" alt=""><img class="brand-vector" src="{p}assets/figma-106/e4e75da9be77e4b5d88637388247ffcbc5fbd42b.svg" alt=""></span><span class="brand-wordmark">Learning Machine</span></span></a>
    <nav class="light-nav" aria-label="Primary navigation">{switch}<a href="./">Careers</a><a class="light-nav-contact" href="mailto:contact@learning-machine.ai">Contact</a></nav>
  </header>
  <main class="careers-main">
"""

FOOTER = """  </main>
  <footer><div class="footer-main"><div><a href="{p}" class="footer-brand"><img class="footer-brand-icon" src="{p}assets/icons/lm-icon-white.svg" alt="">Learning Machine</a><p>Building the next generation of AI models that truly learn and adapt at inference time — adaptive intelligence for every company.</p><a class="footer-email" href="mailto:contact@learning-machine.ai"><span class="footer-email-icon-wrap" aria-hidden="true"><img class="footer-email-icon" src="{p}assets/figma-106/a4b3051739e035e1583a24a11a07115ada55bc08.svg" alt=""></span><span>contact@learning-machine.ai</span></a></div><nav aria-label="Footer navigation"><p>Explore</p><a href="{p}#approach">Approach</a><a href="./">Careers</a><a href="mailto:contact@learning-machine.ai">Contact</a></nav></div><div class="footer-bottom"><span>© 2026 Learning Machine Co. All rights reserved.</span></div></footer>
{motion}
{scroll}
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
# Copy is the user's postings verbatim (zh) and a faithful translation (en) — do not paraphrase.
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
                 ])),
    dict(slug=None,
         zh=dict(name="Agent 视觉设计实习生", tag="实习", meta="实习 · 北京 · 设计", soon="招聘详情即将发布"),
         en=dict(name="Agent Visual Design Intern", tag="Intern", meta="Intern · Beijing · Design", soon="Details coming soon")),
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
                 ])),
]


def esc(s):
    return html.escape(s, quote=False)


def attr(s):
    return html.escape(s, quote=True)


def items(lst):
    return "\n".join(f'          <li class="careers-item">{esc(t)}</li>' for t in lst)


def lang_switch(L, pagefile):
    """The header pill. pagefile is "" for the index or "<slug>.html"; each link targets the same page
    in the other language (zh lives in careers/, en in careers/en/)."""
    if L == "zh":
        zh, en = (pagefile or "./"), ("en/" + pagefile)
    else:
        zh, en = ("../" + pagefile), (pagefile or "./")
    cur = ' aria-current="page"'
    return (f'<div class="lang-switch" aria-label="Language / 语言">'
            f'<a lang="zh-CN" hreflang="zh-CN" href="{zh}"{cur if L == "zh" else ""}>中文</a>'
            f'<a lang="en" hreflang="en" href="{en}"{cur if L == "en" else ""}>EN</a></div>')


def page(L, pagefile, title, desc, body):
    ui = UI[L]
    alternates = (f'  <link rel="alternate" hreflang="zh-CN" href="{SITE}/careers/{pagefile}">\n'
                  f'  <link rel="alternate" hreflang="en" href="{SITE}/careers/en/{pagefile}">\n')
    head = HEAD.format(lang=ui["html_lang"], p=ui["prefix"], title=esc(title), desc=attr(desc), rev=REV,
                       alternates=alternates, switch=lang_switch(L, pagefile))
    return head + body + FOOTER.format(p=ui["prefix"], motion=MOTION,
                                       scroll=SMOOTH_SCROLL.format(prefix=ui["prefix"]))


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
    body = f"""    <section class="careers-band careers-title">
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
    out = f"{ROOT}/{ui['outdir']}"
    os.makedirs(out, exist_ok=True)
    with open(f"{out}/index.html", "w") as f:
        f.write(build_index(L))
    for r in ROLES:
        if r["slug"]:
            with open(f"{out}/{r['slug']}.html", "w") as f:
                f.write(build_role(r, L))
    print(L, "→", sorted(os.listdir(out)))
