# 移动端适配调研与修改计划

> **进度(2026-08-27)**:P0-1/2/3/4、P1-5/6/7、P2-10 已完成并验收(375×812 实测 + 桌面 1280 回归);
> P1-8 已实现(matchMedia 守卫 + 跨断点自动 reload);P1-9(iPad 触屏)已预防性禁用 snap,待真机实测;
> P2-11/12 未做。剩余:多档视口(375×667 / 414×896 / 768×1024)与真机复测。

> 调研方式:375×812(iPhone)视口仿真实测 + 全量 CSS/JS 通读 + 资源体积审计。
> 结论:移动端当前处于**布局崩坏**状态(非细节打磨问题),P0 四项不修复不可上线移动端。
> 执行约定:全部改动只影响 `max-width:1023px` 媒体查询与 light-main 相关代码,遵守 AGENTS.md。

---

## P0 — 布局崩坏(必须修)

### 1. light-approach 区块塌陷,内容全部压到 join/footer 上
- **现象**:A/B 卡片堆、"No operation overhead" 等文字直接叠在 join 区和黑色 footer 上,join 区几乎不可见。
- **根因**:旧版(dark-main)的全局选择器 `.approach-stage { height:100%; inset:0; position:absolute; }`(styles.css 约 71 行)没有作用域限定,同时命中 light-main 的 `.approach-stage`。桌面端被 `@media (min-width:1024px)` 的 `position:sticky` 覆盖而幸免;移动端无覆盖 → stage 脱离文档流,section 实际高度只剩 padding-top 的 130px。
- **修法**:在 `@media (max-width:1023px)` 内加 `.light-approach .approach-stage { position:static; height:auto; inset:auto; }`(或把旧版选择器改为 `.dark-main .approach-stage`,注意别破坏桌面端)。
- **验收**:375px 视口下 approach 区完整包住全部卡片与文字;join 卡片完整可见;footer 上没有任何叠加内容。

### 2. light-belief 文字与卡片重叠,p2 卡片右侧溢出
- **现象**:文案顶在区块最上方,两张 polaroid 卡片(absolute,top 60~335px)直接盖在文字上;p2 卡片右边缘到 430px,超出 375px 视口 55px;文字下方 ~500px 空白。
- **根因**:移动端规则 `.light-belief-copy { left:32px; top:355px; ... }` 写了 top/left 但**缺 `position:absolute`**(computed 为 static,top/left 完全无效)。p2 的 `right:calc(11% - 95.98px)` 在 375px 下为负值。
- **修法**:补 `position:absolute`,让文字回到 top:355px 预留位;p2 的 right 改为不为负的值(如 `right:12px`)并确认两张卡在 60~335px 带内不与 355px 起的文字相撞;或整体改为流式(卡片区块在上、文字在下,间距 32px)。
- **验收**:文字与卡片零重叠;无横向溢出(`document.documentElement.scrollWidth === 375`);区块无大片空白。

### 3. light-header 顶栏放不下,导航溢出
- **现象/根因**:brand 固定 222px + 两个导航 pill 约 228px + 左右 padding 40px = 490px > 375px,必然溢出或换行。light-header 没有移动端专属布局(旧版 header 有汉堡菜单,新版没有)。
- **修法**(任选,建议 a):
  a. 移动端缩小 brand(参照旧版 `transform:scale(.82)`)+ 只保留 Contact 一个 pill,Careers 收进页内锚点;
  b. 复用旧版汉堡菜单模式;
  c. pill 改为纯图标/更窄字号。
- **验收**:375px 下 logo 与导航同行不换行不溢出、点击区 ≥44px 高。

### 4. hero 文案与按钮溢出到下一屏
- **现象**:hero 高度 760px,但文案块 top:390px + 内容高约 392px → 按钮 bottom 到 782px,伸出区块 21px,紧贴/压住 belief 区第一行文字。小屏(iPhone SE 667px 高)会更严重。
- **根因**:移动端 copy 用固定 top:390px 绝对定位 + 内容自然高度,无溢出保护。
- **修法**:`top:390px` 改为 `bottom:24px`(从底部锚定),hero 高度改 `min-height:760px; height:auto` 或 `100svh`;校验 iPhone SE(375×667)不溢出。
- **验收**:375×812 和 375×667 两档下按钮完整在 hero 内,与 belief 区有 ≥24px 间距。

---

## P1 — 明显缺陷(上线前应修)

### 5. hero 插画 min-width 未覆盖,横向溢出 + 裁切错位
- **根因**:`.light-hero-art { min-width:1583px }` 移动端只覆盖了 width:100%,min-width 仍生效 → 元素实际 1638px 宽,视口只露出左侧 24%,`background-position:70% top` 的构图意图完全失效;body 靠 overflow-x:hidden 兜底(iOS Safari 上偶发可横向拖动)。
- **修法**:移动端加 `min-width:0`,再按 375px 宽重调 background-position 构图。
- **验收**:无横向溢出;hero 可见构图与设计意图一致(主体机械结构在画面内)。

### 6. A/B 卡片堆:7 张图全叠在同一位置,只有最上层可见
- **现象**:移动端 stack 内所有 card-wrap 被强制 `inset:0` 全尺寸重叠、全部 opacity:1,只看得到最上面一张(a4/b3),下层旋转卡片的边角从四周穿帮;同时白白下载 7 张共约 2.5MB 的图。
- **修法**:移动端每组只保留最终完整态那张(`.card-wrap-a4`、`.card-wrap-b3`),其余 `display:none`(display:none 的背景图不会下载);去掉保留那张的 rotate 或保留轻微角度但加 overflow 处理。
- **验收**:每组只见一张完整插图、无穿帮边角;Network 面板确认未下载隐藏卡片的图。

### 7. 移动端流量:首页要下载 10MB+ 图片/视频
- **明细**:hero-group-48.png **6.3MB**(且 `<link rel=preload fetchpriority=high>` 强制最先加载)、belief-p1.png 1.5MB、belief-p2.png 1.9MB、stack 图 2.5MB、join 背景 900KB;另外 dark-main 虽然 display:none,里面的 `<img>` 仍会被下载(约 600KB)+ video preload=metadata。
- **修法**(按收益排序):
  a. hero-group-48.png 压缩/转 WebP(线稿图 WebP 有损 80 质量预计 <800KB),并出一张 ~800px 宽移动版,用 CSS media query 或 `image-set()` 切换;preload 标签加 `media="(min-width:1024px)"`;
  b. belief-p1/p2 转 WebP + 提供移动尺寸(移动端显示宽仅 ~170/300px,现在的图是 4 倍以上冗余);
  c. dark-main 里的 `<img>` 全部加 `loading="lazy"`,video 的 `preload` 改 `none`;
  d. stack 图配合第 6 条,移动端只下载 2 张。
- **验收**:移动端首屏(hero)网络传输 <1.5MB,整页 <4MB。

### 8. JS 桌面守卫 `innerWidth > 1023` 只在加载时求值一次
- **现象**:手机横竖屏切换、iPad 旋转/分屏跨过 1024px 阈值时,CSS 已切换但 JS 场景状态不重算(pin 高度、内联样式残留),页面错乱。
- **修法**:监听 resize/orientationchange,跨过 1023 阈值时 `location.reload()`(简单可靠,静态站可接受);或改用 `matchMedia('(min-width:1024px)')` 并在变化时清理内联样式重新初始化。
- **验收**:仿真中 375↔1280 来回切换并旋转,布局始终正确。

### 9. iPad 横屏(≥1024 触屏)走桌面路径,需实测
- **风险点**:snap 逻辑依赖 wheel 事件(触屏无 wheel,只走 scroll 分支的 160ms 定时 snap),触摸惯性滚动与 scrollTo snap 可能互相争抢;Lenis 触屏默认原生滚动,pin/scrub 应可用。
- **修法**:iPad 仿真(1024×768 横屏 + 触摸)实测;若 snap 抖动,对触屏设备(`navigator.maxTouchPoints > 0`)禁用 snap、保留 scrub。
- **验收**:iPad 横屏仿真下滚动顺滑、无来回拉扯。

---

## P2 — 打磨项(可延后)

### 10. 标题打字机乱码效果无完成兜底
- rAF 驱动、无终止兜底:动画期间页面切后台会永久定格乱码(实测定格为 "Bu834 P4")。修法:动画结束用 setTimeout 兜底强制还原原文。

### 11. 移动端动效全无(当前为简化设计)
- 卡片无入场、文字无墨水渐变、区块间无衔接。可选:用 IntersectionObserver 给各区块加轻量淡入(CSS transition,不引入 scrub),尊重 prefers-reduced-motion。

### 12. 触控目标与细节
- light-nav pill 高约 38px,建议 ≥44px;fixed 顶栏浮在黑色 footer 上时白色 pill 观感突兀,可在 footer 段隐藏或加深;`100vh`(light-hero 桌面)在 iOS 建议换 `100svh`(移动端当前用固定 760px,暂不受影响)。

---

## 建议执行顺序与验收基线

1. P0-1 → P0-2 → P0-4 → P0-3(先解重叠,再顶栏)
2. P1-5 → P1-6 → P1-7(视觉+流量)
3. P1-8 → P1-9(状态与平板)
4. P2 择机

**每项完成后统一跑一遍验收基线**:
- 视口:375×667、375×812、414×896、768×1024(竖)、1024×768(横)
- 检查:无横向滚动(`scrollWidth === clientWidth`)、无区块间重叠、控制台无报错、桌面端(1280+)回归不受影响
