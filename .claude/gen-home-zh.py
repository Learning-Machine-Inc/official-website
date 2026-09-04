#!/usr/bin/env python3
"""Build zh/index.html (中文首页) from index.html.

Same markup, scripts, images and animations as the English home page; only the copy changes and
relative paths get a ../ prefix. Run it after EVERY index.html change:

    python3 .claude/gen-home-zh.py

Every English snippet in T must still exist verbatim in index.html, otherwise the script stops with
an error instead of silently shipping a half-translated page. Translation is a first-pass machine
translation (user 2026-09-04: 可以先机翻) — refine the 中文 side of T, never the generated file."""
import os, re, sys

ROOT = "/Users/zhangouqi/Documents/learning machine/deep-claw-main/official-website"

# (English snippet in index.html, 中文 replacement). Keys include enough surrounding markup to be unique
# to the live light-main page — the retired dark-main copy repeats several of these sentences.
T = [
    ('<html lang="en"', '<html lang="zh-CN"'),
    ('<meta name="description" content="Learning Machine builds models that learn and adapt at inference time.">',
     '<meta name="description" content="Learning Machine 打造能在推理时持续学习、不断适应的模型。">'),
    ('<title>Learning Machine | Build AI that truly Learns</title>', '<title>Learning Machine | 打造真正会学习的 AI</title>'),
    # header language pair: EN is current on index.html, 中文 is current here
    ('<a lang="zh-CN" hreflang="zh-CN" href="zh/">中文</a><a lang="en" hreflang="en" href="./" aria-current="page">EN</a>',
     '<a lang="zh-CN" hreflang="zh-CN" href="./" aria-current="page">中文</a><a lang="en" hreflang="en" href="../">EN</a>'),
    # hero
    ('<h1><span class="motion-line">Build AI</span><span class="motion-line">that truly <em>Learns</em></span></h1>',
     '<h1><span class="motion-line">打造真正</span><span class="motion-line">会<em>学习</em>的 AI</span></h1>'),
    ('data-words>The ability to learn is the only means to generalize artificial intelligence to all sectors of human intellectual work.</p>',
     'data-words>学习能力，是让人工智能推广到人类全部智力工作领域的唯一途径。</p>'),
    ('data-words>We are building the first generation of foundation models that can continuously learn, adapt, and improve.</p>',
     'data-words>我们正在打造第一代能够持续学习、适应并不断进步的基础模型。</p>'),
    ('>See our approach <img src="assets/figma-107/', '>了解我们的方法 <img src="assets/figma-107/'),
    ('light-btn-blue" href="mailto:contact@learning-machine.ai">Join us</a>', 'light-btn-blue" href="mailto:contact@learning-machine.ai">加入我们</a>'),
    # approach
    ('<p class="eyebrow kinetic-words" data-words>What makes us different</p><h2><span class="motion-line" data-scramble>Models</span><span class="motion-line">that adapt,</span><span class="motion-line h2-muted">not just respond</span></h2>',
     '<p class="eyebrow kinetic-words" data-words>我们的不同之处</p><h2><span class="motion-line" data-scramble>模型</span><span class="motion-line">会适应，</span><span class="motion-line h2-muted">而非只会回应</span></h2>'),
    ('<div class="light-inference light-inference-a"><p>Our models learn as they work—absorbing new knowledge and mastering new tasks through trial and error. No data pipelines, dedicated training infrastructure, or ML team required. Connect a model to a workflow, and it learns on the job.</p></div>',
     '<div class="light-inference light-inference-a"><p>我们的模型在工作中学习——一边吸收新知识，一边通过试错掌握新任务。无需数据管线、专用训练基础设施或机器学习团队。把模型接入工作流，它就能在岗位上边做边学。</p></div>'),
    # belief
    ('<span class="kinetic-words" data-words>We believe the future of AI should be diverse and inclusive.</span> <span class="belief-muted kinetic-words" data-words data-word-offset="11">Every business should be able to use its proprietary knowledge to build its own AI. Every person should have an AI experience tailored to them. And by default, their data should stay in their hands.</span>',
     '<span class="kinetic-words" data-words>我们相信，AI 的未来应当是多元且包容的。</span> <span class="belief-muted kinetic-words" data-words data-word-offset="10">每家企业都应能用自己的专有知识构建属于自己的 AI；每个人都应拥有为其量身定制的 AI 体验；而且在默认情况下，数据应始终掌握在他们自己手中。</span>'),
    # join card (light-main only: the legacy dark-main h2 carries an id)
    ('<h2>Join us</h2><p>We\'re building the future of AI, and we\'re hiring across research, engineering, and product. Come build it with us.</p><div class="join-actions"><a class="button button-dark" href="careers/en/">See open roles</a><a class="button button-blue" href="mailto:careers@learning-machine.ai">Get in touch</a></div>',
     '<h2>加入我们</h2><p>我们正在构建 AI 的未来，研究、工程与产品方向都在招人。来和我们一起创造。</p><div class="join-actions"><a class="button button-dark" href="careers/">查看开放岗位</a><a class="button button-blue" href="mailto:careers@learning-machine.ai">联系我们</a></div>'),
    # footer
    ('Learning Machine</a><p>Building the next generation of AI models that truly learn and adapt at inference time — adaptive intelligence for every company.</p>',
     'Learning Machine</a><p>打造新一代能在推理时真正学习与适应的 AI 模型——让每家公司都拥有自适应的智能。</p>'),
    ('<p>Explore</p><a href="#approach">Approach</a><a href="careers/en/">Careers</a><a href="mailto:contact@learning-machine.ai">Contact</a>',
     '<p>探索</p><a href="#approach">我们的方法</a><a href="careers/">招聘</a><a href="mailto:contact@learning-machine.ai">联系我们</a>'),
    ('<span>© 2026 Learning Machine Co. All rights reserved.</span>', '<span>© 2026 Learning Machine Co. 保留所有权利。</span>'),
]

src = open(f"{ROOT}/index.html", encoding="utf-8").read()
out = src
missing = [en for en, _ in T if en not in out]
if missing:
    sys.exit("gen-home-zh: these snippets are no longer in index.html — update T:\n  " + "\n  ".join(m[:90] for m in missing))
for en, zh in T:
    out = out.replace(en, zh, 1)

# zh/ lives one level down: prefix every relative URL (assets/, styles.css, careers/) with ../ but leave
# anchors, absolute URLs, mailto:, data: and the already-relative ./ and ../ alone.
out = re.sub(r'\b(href|src|srcset|data-a|data-b)="(?!https?:|mailto:|#|\.\.?/|/|data:)([^"]+)"', r'\1="../\2"', out)
out = out.replace("from './assets/", "from '../assets/")  # Lenis module import in the inline module script

assert out.count("../assets/") > 20 and 'href="../styles.css' in out, "path rewrite looks wrong"
os.makedirs(f"{ROOT}/zh", exist_ok=True)
with open(f"{ROOT}/zh/index.html", "w", encoding="utf-8") as f:
    f.write(out)
print("written: zh/index.html", f"({len(T)} snippets translated)")
