#!/usr/bin/env python3
"""Generate careers/index.html (L2 Open roles) and the L3 role pages from one data table.
Header/footer markup mirrors index.html (paths rewritten with ../)."""
import html, os, textwrap

ROOT = "/Users/zhangouqi/Documents/learning machine/deep-claw-main/official-website"
REV = "figma-1617-19731-v37"
EMAIL = "careers@learning-machine.ai"

HEAD = """<!doctype html>
<html lang="zh-CN" data-variant="light" data-ab-variant="b">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#F4F0ED">
  <meta name="description" content="{desc}">
  <title>{title} | Learning Machine</title>
  <link rel="icon" href="../assets/icons/favicon-adaptive.svg?v=1" type="image/svg+xml">
  <link rel="icon" href="../assets/icons/favicon-32.png" type="image/png" sizes="32x32" media="(prefers-color-scheme: light)">
  <link rel="icon" href="../assets/icons/favicon-dark-32.png" type="image/png" sizes="32x32" media="(prefers-color-scheme: dark)">
  <link rel="apple-touch-icon" href="../assets/icons/apple-touch-icon.png">
  <link rel="preload" href="../assets/fonts/outfit-bold-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="../assets/fonts/gentium-plus-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="../assets/fonts/roboto-var-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="../styles.css?rev={rev}">
</head>
<body class="careers-page">
  <header class="light-header">
    <a href="../" class="light-brand" aria-label="Learning Machine home"><span class="brand-lockup"><span class="brand-mark" aria-hidden="true"><img class="brand-union" src="../assets/figma-106/0fc9ec76b79449656b5cb20fb65111dac0da7f74.svg" alt=""><img class="brand-base" src="../assets/figma-106/bb0bb4d59834c3b5c02cce512ab83e6722cc4dc8.svg" alt=""><img class="brand-vector" src="../assets/figma-106/e4e75da9be77e4b5d88637388247ffcbc5fbd42b.svg" alt=""></span><span class="brand-wordmark">Learning Machine</span></span></a>
    <nav class="light-nav" aria-label="Primary navigation"><a href="./">Careers</a><a class="light-nav-contact" href="mailto:contact@learning-machine.ai">Contact</a></nav>
  </header>
  <main class="careers-main">
"""

FOOTER = """  </main>
  <footer><div class="footer-main"><div><a href="../" class="footer-brand"><img class="footer-brand-icon" src="../assets/icons/lm-icon-white.svg" alt="">Learning Machine</a><p>Building the next generation of AI models that truly learn and adapt at inference time — adaptive intelligence for every company.</p><a class="footer-email" href="mailto:contact@learning-machine.ai"><span class="footer-email-icon-wrap" aria-hidden="true"><img class="footer-email-icon" src="../assets/figma-106/a4b3051739e035e1583a24a11a07115ada55bc08.svg" alt=""></span><span>contact@learning-machine.ai</span></a></div><nav aria-label="Footer navigation"><p>Explore</p><a href="../#approach">Approach</a><a href="./">Careers</a><a href="mailto:contact@learning-machine.ai">Contact</a></nav></div><div class="footer-bottom"><span>© 2026 Learning Machine Co. All rights reserved.</span></div></footer>
</body>
</html>
"""

def esc(s):
    return html.escape(s, quote=False)

def items(lst):
    return "\n".join(f'          <li class="careers-item">{esc(t)}</li>' for t in lst)

def apply_card(eyebrow, h2, note, btn_label, subject, top=False):
    band = "apply-band apply-band-top" if top else "apply-band"
    mail = f"mailto:{EMAIL}?subject={html.escape(subject)}"
    return f"""    <section class="careers-band {band}">
      <div class="apply-card">
        <p class="careers-eyebrow">{esc(eyebrow)}</p>
        <h2>{esc(h2)}</h2>
        <p>{esc(note)}</p>
        <div class="apply-actions"><a class="btn-primary" href="{mail}">{esc(btn_label)}&nbsp;&nbsp;→</a><a class="btn-black" href="mailto:{EMAIL}">{EMAIL}</a></div>
      </div>
    </section>
"""

ROLES = [
    dict(slug="agent-fullstack-campus", name="Agent 全栈研发工程师", tag="校招 / 实习", meta="校招 / 实习 · 北京 · 研发",
         points=["开发自有模型的 Agent，有资深 Mentor 和团队协作", "全栈客户端功能开发，根据 Figma MCP 到 Coding Agent 进行前端页面开发"],
         eyebrow="WE ARE HIRING · 校招 / 实习",
         facts=[("LOCATION · 地点", "北京 · 中关村"), ("OFFER · 校招待遇", "对标国内一线大厂"), ("INTERNSHIP · 实习工资", "RMB 500+ / 天，具体面议")],
         sections=[
             ("WHAT YOU'LL DO", "职位要求", ["开发自有模型的 Agent，有资深 Mentor 和团队协作", "全栈客户端功能开发，根据 Figma MCP 到 Coding Agent 进行前端页面开发", "服务端逻辑对接，承接 Agentic 架构，也可参与到 Agentic 架构设计和开发中"]),
             ("WHO YOU ARE", "希望你是", ["计算机、电子信息、软件工程、人工智能等相关专业，熟练使用 Coding Agent，在校期间有相关课程设计、项目实践经验者优先。", "具备扎实的计算机基础知识，掌握数据结构、算法、计算机网络、操作系统等核心知识点。", "对 Agentic 架构、大模型有浓厚兴趣，了解其基本工作原理，有大模型 API 集成、Prompt 设计相关实践经验者优先。", "具备一定的客户端研发能力，熟悉至少一种客户端开发技术（iOS / Android / Flutter / React Native / PC 端桌面应用），能独立完成简单界面、交互逻辑开发。", "具备基础的后端研发能力，熟悉至少一种后端语言（Java / Go / Python / Node.js），了解 RESTful API、数据库基础，能完成简单后端接口开发与调试。", "具备良好的学习能力、问题排查能力和逻辑思维，积极主动，乐于接受新挑战，有较强的沟通能力和团队协作意识。"]),
             ("NICE TO HAVE", "加分项", ["英文办公", "有 Agent 类产品研发经验", "有跨端（移动端 + PC 端）研发经验", "开源项目贡献者"]),
         ]),
    dict(slug="agent-fullstack", name="Agent 全栈研发工程师", tag="社招", meta="社招 · 北京 · 研发",
         points=["负责 AI Agent 个人助理客户端全栈研发，端到端落地核心功能", "主导核心交互逻辑、任务调度与上下文管理，结合大模型能力"],
         eyebrow="WE ARE HIRING · 社招",
         facts=[("LOCATION · 地点", "北京 · 中关村"), ("SALARY · 年薪", "30–60 万"), ("BENEFITS · 福利", "六险一金")],
         sections=[
             ("WHAT YOU'LL DO", "岗位职责", ["负责 AI Agent 个人助理客户端全栈研发，涵盖前端 / 移动端、后端接口、AI 能力集成，端到端实现个人助理的核心功能落地，确保产品流畅性、稳定性和用户体验。", "主导 Agent 个人助理的核心交互逻辑、任务调度、上下文管理研发，结合大模型能力，实现智能对话、任务拆解、多工具调用（日程、邮件、文件管理等）、个性化推荐等核心场景。", "负责客户端与大模型 API、第三方工具（办公软件、生活服务接口等）的对接与调试，优化接口性能、数据传输效率，解决跨端兼容、网络异常等问题。", "参与产品需求评审、技术方案设计，结合 AI Agent 特性提出客户端技术优化建议，推动产品迭代升级；负责技术文档编写、代码评审，保障研发质量。", "关注 AI Agent、大模型应用、客户端研发前沿技术，将新技术、新方案融入产品研发，提升产品竞争力和研发效率。", "配合测试、产品团队，完成功能测试、Bug 修复、用户反馈优化，确保产品上线质量；协助搭建客户端研发规范和流程。"]),
             ("CORE REQUIREMENTS", "核心要求", ["本科及以上学历，计算机、电子信息、软件工程等相关专业，3 年及以上全栈研发经验，熟练使用 Coding Agent，有 AI Agent、个人助理类产品研发经验者优先。", "具备扎实的客户端研发能力，熟练掌握至少一种客户端开发技术，能独立完成客户端界面、交互逻辑开发。", "具备后端研发能力，熟练掌握至少一种后端语言，熟悉 RESTful API、微服务架构，能独立开发、调试后端接口，处理数据存储与交互。", "了解大模型的工作原理，有大模型 API 集成、Prompt 工程、Agent 任务调度、上下文管理相关经验者优先。", "具备良好的问题排查能力，能快速定位并解决客户端、后端、AI 集成过程中的技术问题，有跨端开发、性能优化经验者优先。"]),
             ("SKILLS", "技能要求", ["前端 / 客户端：熟练掌握 Flutter / React Native，或 iOS（Swift / OC），熟悉组件化、工程化开发，了解 UI/UX 设计规范。", "后端：熟练掌握 Go / Python / Java 中的一种或多种，熟悉 MySQL、MongoDB 等数据库，了解 Redis 缓存、消息队列等中间件，具备接口设计、性能优化能力。", "AI 相关：熟悉大模型 API 调用、Prompt 设计，了解 Agent 框架（如 LangChain、LlamaIndex），有智能对话、任务拆解、多工具集成经验者加分。", "其他：熟悉 Git 版本控制，具备良好的代码规范和文档编写习惯；具备较强的学习能力、沟通能力和团队协作能力，能快速适应 AI 技术迭代节奏。"]),
             ("NICE TO HAVE", "加分项", ["有个人助理类、AI Agent 类产品全栈研发经验，或主导过相关产品从 0 到 1 落地。", "熟悉大模型微调、Agent 智能调度策略、上下文记忆优化等相关技术。", "有跨端（移动端 + PC 端）研发经验，能独立完成全平台客户端适配。", "开源项目贡献者，或有个人技术博客、相关技术成果展示。"]),
         ]),
    dict(slug=None, name="Agent 视觉设计实习生", tag="实习", meta="实习 · 北京 · 设计", points=None, soon="招聘详情即将发布"),
    dict(slug="agent-client", name="Agent 客户端工程师", tag="社招", meta="社招 · 北京 · 客户端研发",
         points=["开发自有模型的 Agent 客户端：Web、iOS、macOS", "从 Figma MCP 到 Coding Agent 的全栈客户端功能开发"],
         eyebrow="WE ARE HIRING · 社招",
         facts=[("LOCATION · 地点", "北京 · 中关村"), ("TYPE · 类型", "社招 · 全职"), ("COMPENSATION · 待遇", "面议")],
         sections=[
             ("WHAT YOU'LL DO", "职位要求", ["开发自有模型的 Agent 客户端，包括 Web、iOS、macOS", "全栈客户端功能开发，根据 Figma MCP 到 Coding Agent 进行前端页面开发", "服务端逻辑对接，承接 Agentic 架构，也可参与到 Agentic 架构设计和开发中"]),
             ("WHO YOU ARE", "希望你是", ["计算机、电子信息、软件工程、人工智能等相关专业，熟练使用 Coding Agent。", "1–3 年客户端项目经验，熟悉至少一种客户端开发技术（iOS / Android / Flutter / React Native / PC 端桌面应用），能独立完成简单界面、交互逻辑开发。", "对 Agentic 架构、大模型有浓厚兴趣，了解其基本工作原理，有大模型 API 集成、Prompt 设计相关实践经验者优先。", "具备良好的学习能力、问题排查能力和逻辑思维，积极主动，乐于接受新挑战，有较强的沟通能力和团队协作意识。"]),
             ("NICE TO HAVE", "加分项", ["英文办公", "有 Agent 类产品研发经验"]),
         ]),
]

def role_row(r):
    if r.get("slug"):
        body = f'        <ul class="role-points">\n{items(r["points"])}\n        </ul>\n        <div class="role-action"><a class="btn-outline" href="{r["slug"]}.html">查看详情 <span aria-hidden="true">→</span></a></div>'
    else:
        body = f'        <p class="role-soon">{esc(r["soon"])}</p>\n        <div class="role-action"></div>'
    return f"""      <li class="role-row">
        <div class="role-heading"><h2 class="role-name">{esc(r["name"])}</h2><p class="role-meta">{esc(r["meta"])}</p></div>
{body}
      </li>
"""

def build_index():
    rows = "".join(role_row(r) for r in ROLES)
    n = len(ROLES)
    body = f"""    <section class="careers-band careers-title">
      <p class="careers-eyebrow">Careers · We are hiring</p>
      <h1>Open roles</h1>
      <p class="careers-intro">目前开放 {n} 个岗位 · 北京研发中心。点击岗位查看职位要求、待遇与投递方式。</p>
    </section>
    <section class="careers-band">
      <ul class="roles-list">
{rows}      </ul>
    </section>
""" + apply_card("Open application · 自荐", "没有合适的岗位？直接把简历发给我们", f"邮件发送至 {EMAIL}，注明你感兴趣的方向。", "自荐投递", "自荐投递", top=True)
    return HEAD.format(title="Open roles", desc="Learning Machine 北京研发中心开放岗位：Agent 全栈研发、客户端、视觉设计。", rev=REV) + body + FOOTER

def build_role(r):
    facts = "\n".join(f'        <li><p class="fact-label">{esc(l)}</p><p class="fact-value">{esc(v)}</p></li>' for l, v in r["facts"])
    secs = "\n".join(f"""      <section class="careers-section">
        <div class="section-heading"><p class="careers-eyebrow">{esc(en)}</p><h2>{esc(zh)}</h2></div>
        <ul>
{items(lst)}
        </ul>
      </section>""" for en, zh, lst in r["sections"])
    subject = f"{r['name']} · {r['tag']}"
    body = f"""    <section class="careers-band careers-title">
      <p class="careers-eyebrow">{esc(r["eyebrow"])}</p>
      <h1>{esc(r["name"])}</h1>
    </section>
    <section class="careers-band">
      <ul class="facts">
{facts}
      </ul>
    </section>
    <div class="careers-band careers-sections">
{secs}
    </div>
""" + apply_card("Apply · 简历投递", "简历投递", f"邮件发送至 {EMAIL}，主题请注明「{subject}」。", "立即投递", subject)
    return HEAD.format(title=f"{r['name']}（{r['tag']}）", desc=f"Learning Machine 招聘：{r['name']}（{r['tag']}），北京 · 中关村。", rev=REV) + body + FOOTER

os.makedirs(f"{ROOT}/careers", exist_ok=True)
with open(f"{ROOT}/careers/index.html", "w") as f:
    f.write(build_index())
for r in ROLES:
    if r.get("slug"):
        with open(f"{ROOT}/careers/{r['slug']}.html", "w") as f:
            f.write(build_role(r))
print("written:", sorted(os.listdir(f"{ROOT}/careers")))
