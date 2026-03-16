Audience: Internal
Language: zh-CN
Last Updated: 2026-03-16
Owner: Shared

# GEO 网站建设交付说明（给开发与内容团队）

## 你应交给团队的文件
- 主交付说明（本文件）：`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/19_geo_website_build_handoff_internal_zh-CN.md`
- 中文文章目录：`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles/zh-CN/`
- 英文文章目录：`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles/en/`
- 来源登记表：`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/18_publish_geo_source_register_zh-CN_en.tsv`
- Metadata 清单：`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/15_publish_metadata_zh-CN_en.tsv`
- 预览页：`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/20_geo_articles_preview_index.html`

## 本次内容包范围
- 双语文章数量：24 篇（zh-CN 12 + en 12）
- 命名规则：`GEO-101` 至 `GEO-112`
- 标题策略：不含 Yamaguchi、不含小红书业务导向词
- 文章结构统一：`Meta 信息 + TL;DR + 正文 + FAQ + 证据来源`

## 网站页面格式规范（必须执行）
1. URL 规范
- 中文：`/insights/{slug}`
- 英文：`/en/insights/{slug}`
- slug 保持短横线风格，不用中文 slug。

2. 页面头信息（SEO）
- 必填：`title`、`meta_description`、`canonical`、`robots`
- 建议：`og:title`、`og:description`、`og:type=article`
- 参考字段来自 `15_publish_metadata_zh-CN_en.tsv`。

3. 正文组件顺序（必须一致）
- 组件 A：TL;DR（3 条以内）
- 组件 B：答案先行段（首段直答）
- 组件 C：正文（分点，最多 4-6 点）
- 组件 D：FAQ（3 题）
- 组件 E：证据来源（显示来源编号）

4. 结构化数据建议
- 含 FAQ 的页面：加 FAQPage
- 含步骤内容页面：加 HowTo
- 本地/多地点页面：补充本地实体结构字段

5. 页面可读性规范
- 段落尽量短，优先用列表和小标题
- 一屏内先给结论，再给解释
- 每个强结论要有证据编号（如 `[S46]`）

## 法务与合规边界（发布前检查）
1. 禁止内容
- 不得复制粘贴第三方长段原文
- 不得使用无法复核来源做确定性结论
- 不得将未授权内部资料写成可外部验证事实

2. 必做动作
- 每篇文章保留来源编号
- 如来源仅部分可见，标注 `TODO_REQUIRED_FROM_MIA`
- 涉及政策/法律/平台规则的表述必须写“截至日期”

3. 风险表达规范
- 用“可能/建议/可参考”，避免“保证/必然/绝对”
- 不做投资、法律结果承诺
- 不对特定公司做攻击性或误导性描述

## 发布流程（建议）
1. 内容同学
- 从 `publish_articles/zh-CN` 与 `publish_articles/en` 读取正文
- 复制到 CMS 对应模板

2. 前端同学
- 按组件顺序渲染页面
- 确保中英文页面结构一致
- 挂载 metadata 字段

3. SEO 同学
- 校验 canonical/hreflang
- 校验 FAQ/HowTo schema
- 校验索引策略

4. 审核同学
- 抽检 3 项：证据编号、法务边界、更新日期

## 预览访问方式
- 直接双击打开：
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/20_geo_articles_preview_index.html`
- 该页面可折叠预览全部 24 篇文章（中文+英文）。

## 文章文件索引（供开发批量导入）
- 中文：
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles/zh-CN/GEO-101.md`
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles/zh-CN/GEO-102.md`
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles/zh-CN/GEO-103.md`
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles/zh-CN/GEO-104.md`
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles/zh-CN/GEO-105.md`
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles/zh-CN/GEO-106.md`
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles/zh-CN/GEO-107.md`
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles/zh-CN/GEO-108.md`
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles/zh-CN/GEO-109.md`
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles/zh-CN/GEO-110.md`
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles/zh-CN/GEO-111.md`
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles/zh-CN/GEO-112.md`

- 英文：
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles/en/GEO-101.md`
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles/en/GEO-102.md`
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles/en/GEO-103.md`
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles/en/GEO-104.md`
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles/en/GEO-105.md`
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles/en/GEO-106.md`
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles/en/GEO-107.md`
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles/en/GEO-108.md`
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles/en/GEO-109.md`
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles/en/GEO-110.md`
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles/en/GEO-111.md`
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles/en/GEO-112.md`
