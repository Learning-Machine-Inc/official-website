# Learning Machine 官网 — 协作说明

## 项目概况
- 纯静态站点:只有 `index.html`、`styles.css`、`assets/`。无构建步骤、无依赖、无框架。
- 部署:GitHub Pages,`main` 分支发布到 learning-machine.ai。当前开发分支 `feat/website-local`。
- 本地预览(自带 live-reload,改文件浏览器自动刷新):

```bash
PORT=3002 node .claude/serve-official-website.js
```

浏览器打开 http://localhost:3002 (3001 已被其他进程占用,不要用)。

## 页面结构
- `<main class="light-main">`:**唯一在用的设计**(浅色手绘工程图风格),四个区块:
  `light-hero` → `light-approach` → `light-belief` → `light-join`。永久 `display:block`,
  不再受 `data-variant` 控制。
- `<main class="dark-main">`:旧版,整块代码保留在 DOM 里(历史参考),但永久 `display:none`,
  已从 CSS 显隐逻辑和 JS 滚动系统里完全解耦——**不要**恢复
  `html[data-variant="dark"] .light-main { display:none; }` 这类规则,那会重新显示旧版而不是
  真正的 B 版本。旧版相关 CSS(`html[data-variant="dark"]` 开头的一大段颜色/变量覆盖)也**勿动**,
  它们现在虽是死代码但不产生任何效果。
- **A/B 测试入口**(2026-09-02 起):header 左上角那个隐藏的 `#variant-toggle` 按钮
  (双击触发)切换 `root.dataset.abVariant`('a'/'b')。**页面加载默认是 B**(脚本里
  `setAbVariant('b')`),双击切回 A。B 版 = 青绿色系测试(Figma `tFncbEkPEyRqS4h7Su8ODE`):
  `styles.css` 末尾一段 `html[data-ab-variant="b"]` 规则(配色、hero/join 背景图、belief 两张
  卡片的位置角度),外加 `assets/figma-b-test/` 里的三张图。belief-p2 那张因为在 `<picture>`
  里,不能用 CSS `content:url()` 换,是 `setAbVariant` 里直接改 `img.src`。
  `html[data-variant]` 属性永久固定为 `"light"`,不要让这个入口再去改它。
- 本地开发服务器对所有响应发 `Cache-Control: no-store`(2026-09-02 加),本地改完直接刷新即可。
  改了 `serve-official-website.js` 本身要重启进程。
- **线上(GitHub Pages)有 10 分钟 CDN/浏览器缓存**(`Cache-Control: max-age=600`),而且
  `styles.css` 的 URL 不变就可能一直命中旧缓存。**每次合并含 styles.css 改动的 PR 前,把
  `index.html` 里 `styles.css?rev=…-vNN` 的版本号 +1**,否则用户刷新线上看不到新样式
  (2026-09-03 的按钮配色就是这样"没生效")。

## 招聘页(careers/,2026-09-03 起)
- `careers/index.html` = 二级页 Open roles(所有开放岗位列表),`careers/<slug>.html` = 三级岗位详情;
  首页 Join 区 "See open roles" 与页脚 Careers 都指向 `careers/`。Figma 对应「公司-产品官网」文件
  页「官网 1440 · 代码回同步 0831」里的 07(L2)/ 08–10(L3)画板。
- **这些页面由 `.claude/gen-careers.py` 生成**:岗位数据(名称/类型/亮点/地点待遇/各区块条目)都在
  脚本里的 `ROLES` 表。改岗位内容 → 改表 → `python3 .claude/gen-careers.py` 重出;不要手改
  生成出来的 HTML。新增岗位 = 加一条 `ROLES`(没有稿子的岗位 `slug=None`,列表页只显示"即将发布")。
- 样式在 styles.css 的「Careers pages」块,复用首页 header/footer 与令牌;字号层级按用户在 Figma
  调定的值(64/104 主标 · 32/48 标题 · 28/48 信息条 · 16/24 正文 · 14/22 眉题)。中文不额外下载
  字体,靠 `--careers-serif` / `--careers-sans` 栈按字形回退到系统 Songti / PingFang。
- 布局类名 `.careers-band` 负责左右内距 = header 内容带再向内(桌面 +40px:`max(112px, 50%-688px)`;
  移动 +20px:36px,手机上再缩文字列就太窄了),任何窗口宽度下都保持这个关系;其他区块**只写上下 padding 的 longhand**,别用
  `padding` 简写把左右覆盖成 0(踩过)。列宽/字号按 1440 画布用 `min(400px, 27.778vw)`、
  `clamp(…, 4.444vw, 64px)` 这类公式写,768–1199 之间岗位行改成"名称 | 按钮"两列、亮点落到名称下方。

## 动效架构(重要,改之前先读完)
所有动效都在 `index.html` 底部的两个 `<script>` 里,没有外部动画库(Lenis 除外):

1. **第一个 script**:IntersectionObserver 驱动的一次性入场体系
   (`motion-reveal` / `motion-line` / `kinetic-words` + `word-reveal` 关键帧),时间驱动。
2. **第二个 module script**:Lenis 平滑滚动 + 滚动位置逐帧驱动(scrub)的动效:
   hero 退场视差、approach 单组(A)四卡分镜(IN_A/OUT_A 时间窗,卡片堆入→停留→散开退场,
   标题随后用 headingUnits 逐行退场)、belief 的墨水渐变与离场。approach 在前、belief 在后
   (2026-09-01 起,B 分镜已整体移除);两个 pin 场景的 snap 停靠点合并在 `snapScene()`
   一个数组里(`allStops`/`allTriggers`),按页面顺序拼接,不要拆回两套独立逻辑。
   belief 里的 p1/p2 两张图是例外:不是 scrub,是`beliefCardsActive` 驱动的"每次进入区间
   重播入场、离开就向上淡出"状态机(桌面独有,带滚动方向不同的迟滞阈值防抖)。这两张图已
   从第一个 script 的通用一次性 `motionObserver` 里排除(仅桌面排除,移动端仍用那套),
   避免两套系统抢同一个 `is-visible` class。(`window.resetBeliefCards()` 曾用于旧版切换时
   重置这套状态机,2026-09-02 随 A/B 入口解耦一起删除——现在 `data-variant` 永久是
   `"light"`,不会再冻结,不需要这个 resync 了。)

修改动效请在现有体系内调参数/时间窗,**不要引入新动画库、不要另起一套并行系统**。

## 已知坑(都真实踩过)
- **favicon 深浅模式**:Chrome 忽略 `<link rel="icon">` 上的 `media="(prefers-color-scheme)"`,
  两个 SVG 分开挂无效。现在用 `assets/icons/favicon-adaptive.svg` 一个文件装两套图形,靠 SVG
  内部的 `@media (prefers-color-scheme: dark)` 切换;PNG 版仍按 media 挂着给不支持 SVG favicon 的
  浏览器。改图标要同时更新这个自适应文件。
- `.kinetic-word` 的基础 CSS 是 `opacity:0`,靠 `word-reveal` 动画补到 1。JS 里一旦
  `style.animation='none'`,**必须同时** `style.opacity='1'`,否则整段文字直接消失。
- `light-belief` 的文字是两层结构,职责不同,不要合并:
  - 词级 span(`.kinetic-word`)= 入场动画(逐行上浮+淡入,时间过渡,一次性触发)+ 滚动驱动的逐行离场;
  - 字母级 span(运行时拆出)= 滚动驱动的墨水渐变(30% → 100% opacity,颜色 #242E6F,20 字母宽过渡带,双向可逆)。
- 把词拆成字母 span 会轻微改变词宽(字距/连字断开),可能挪动换行点——任何按行分组的
  测量必须在拆分并强制回流**之后**做。
- 滚动进度用 offsetTop 链(代码里的 `chain()` 函数)算文档坐标。sticky 区块
  (`belief-stage` / `approach-stage`)pin 住时 `getBoundingClientRect().top` 恒定不变,
  **不能**拿它当滚动进度,否则动效会"卡死"。
- 桌面端 scrub/snap 逻辑统一由 `desktopMQ = matchMedia('(min-width:768px)')` 守卫(与 CSS
  断点严格一致,勿改回 innerWidth 判断);跨断点会自动 location.reload()。≤767 走文件末尾
  媒体查询里的简化布局,改桌面端时确认没有破坏移动端兜底。

## 设计规范(用户的强规则,不可妥协)
- **Figma 是唯一事实来源**:file `ZT09P2VnDxzakgLyVmMXlE`(公司-产品官网)。实现必须逐节点
  读取精确 px 值(位置/尺寸/颜色/字号/行距/字距)1:1 还原;**禁止**按截图目测比例、
  禁止"取整求美观"、禁止用近似百分比布局替代。
- Figma 1440px 画布绝对坐标 → 响应式的既有惯例(沿用,别发明新写法):
  `left:max(<Xpx>, calc(50% - <内容半宽>)); width:min(<Wpx>, calc(100% - 边距*2))`
- 字体全部自托管在 `assets/fonts/`(`@font-face` 在 styles.css 顶部):Gentium Plus(标题衬线)、
  Roboto 可变字重 300–600(正文/按钮/眉题/页脚)、Outfit 700(页脚品牌)、Inter(body 兜底)。
  要用新字体/字重,下载 woff2 放进去并加 `@font-face`,不要接 Google Fonts(用户网络极慢)。
- **桌面端和移动端是同一套设计系统**(2026-09-03 起):字体族、颜色、字重、大小写这些"令牌"只写在
  基础规则里,`@media (min-width:768px)` / `@media (max-width:767.98px)` 两个块**只放字号、行高、
  宽度、布局**。改字体/颜色一律改基础规则,不要在媒体查询里覆盖 `font-family`/`color`,否则另一端
  会掉队(之前 Roboto、青绿色等桌面更新没同步到移动端就是这个原因)。
- belief 段落文案:`#242E6F`,Inria Serif 300,32px/43px,浅态 = 30% opacity。

## 图片资源(2026-09-02 起)
- 页面里的照片类资源一律 **AVIF + WebP**,CSS 背景用 `image-set(url() type(), …)`(前面先写一条
  普通 `url()` 兜底),`<img>` 用 `<picture><source type>`。桌面头图分 1920w(1x)/ 2752w
  (≥1.5dppx,`@media (min-resolution:1.5dppx)`)两档,移动端 1440w;`<head>` 里的头图 preload
  必须和 CSS 的 media/尺寸拆分**一一对应**,且指向默认变体(B),否则会重复下载。
- 头图底层还叠了一张内联的 48px WebP(LQIP,base64 在 CSS 里),大图到之前先有画面。
- **换图/加图流程**:把源图放到原位置 → 在 `.claude/encode-images.py` 的 `JOBS` 里登记 →
  `python3 .claude/encode-images.py` 重出全部格式 → 引用新文件名。不要再直接引用几 MB 的
  PNG(原 `hero-group-48.png` 6.4MB 就是线上首屏慢的原因;它已换成无损 WebP 母版
  `hero-group-48.webp`,仅作编码源,页面不引用)。
- belief-p2 在 A/B 间切换:`<picture>` 里每个 `<source>`/`<img>` 带 `data-a`/`data-b`,
  `setAbVariant()` 逐个换 `srcset`/`src`;初始值写 B(默认),避免预加载扫描器先抓 A。

## 验收标准(每个改动都要过)
1. 在 3002 端口实际滚一遍:入场、滚动 scrub(正向+反向)、离场都正常;
2. 浏览器控制台无报错;
3. 没有恢复 `dark-main` 的显示逻辑;A/B 两态都滚一遍,滚动动效一致,B 态的图片/配色/卡片位置
   只通过 `html[data-ab-variant="b"]` 规则生效;
4. git 小步提交在 `feat/website-local`,提交信息说清楚改了哪个区块的什么。
