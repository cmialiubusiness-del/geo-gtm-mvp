Audience: Internal
Language: zh-CN
Last Updated: 2026-03-16
Owner: Shared

# GEO 长文版网站交付说明（团队直接执行）

## 你应该给团队的文件（优先级顺序）
1. 主说明（本文件）
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/24_geo_longform_website_handoff_internal_zh-CN.md`

2. 长文版文章（直接上站）
- 中文：`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles_longform/zh-CN/`
- 英文：`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/publish_articles_longform/en/`

3. 长文预览页（给你先审稿）
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/23_geo_longform_preview_index.html`

4. 来源与元信息
- 来源表：`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/18_publish_geo_source_register_zh-CN_en.tsv`
- Metadata：`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/15_publish_metadata_zh-CN_en.tsv`

## 长文版规模
- 文章数：12 篇 zh-CN + 12 篇 en
- 编号：`GEO-201` 到 `GEO-212`
- 定位：读者可直接阅读的完整专业文章（不是短纲）

## 统一页面结构（前端按此渲染）
- 标题
- 页面信息（slug/meta）
- TL;DR
- 背景与问题
- 方法论/框架
- 执行步骤
- 常见误区或风险
- FAQ
- 证据来源

## 内容与格式要求
1. 可读性
- 首屏必须出现结论
- 每段 3-5 行，避免大段密集文本
- 重要信息优先列表化

2. 专业性
- 每个关键观点都能追溯来源编号
- 不做收益承诺、不做绝对化结论
- 不引导读者进行法律边界不清的操作

3. 合规性
- 禁止大段复制第三方原文
- 未完整访问来源必须保留 `TODO_REQUIRED_FROM_MIA`
- 涉及政策/规则变化需保留时间上下文（截至日期）

## CMS 落站流程（建议）
1. 内容团队导入 Markdown
- 读取 `publish_articles_longform` 下同编号中英文件
- 确保 zh/en slug 一一对应

2. 前端渲染模板
- 使用统一 article 模板
- FAQ 段与证据来源段不能省略

3. SEO 设置
- 写入 title/meta/canonical/og
- 建议接入 FAQPage / HowTo 结构化数据（适用页面）

4. 发布前审核
- 抽检每篇 3 项：证据编号、更新时间、风险用语

## 预览与打包
- 预览文件：
`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi/week1/kb/23_geo_longform_preview_index.html`
- 如果需要对外发团队，可直接打包以下目录：
`publish_articles_longform/` + `18_publish_geo_source_register_zh-CN_en.tsv` + `15_publish_metadata_zh-CN_en.tsv` + 本说明

## 备注
- 标题中已去除 Yamaguchi 与小红书业务导向。
- 当前长文版适合作为“网站知识中心”第一批上线内容。
