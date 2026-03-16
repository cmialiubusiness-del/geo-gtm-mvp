Audience: Internal
Language: zh-CN
Last Updated: 2026-03-11
Owner: Shared
Audit Datetime: 2026-03-11 16:18:57 HKT (+0800)

# W1-02 品牌 SEO + GEO 基线审计（决策版）

## 0) 审计范围与方法
- 审计范围：
  - https://yamaguchitech.cn
  - https://yamaguchitech.cn/en
  - https://yamaguchitech.cn/tw
- 执行方式：
  - 站点技术项使用 `curl` + 页面源码实测。
  - 搜索可见度使用公开搜索结果页面与实时查询。
  - GEO 使用 20 个问题进行代理基线（SERP 代理）；真实大模型回答端到端测量因环境限制为 `N/A`。

## 1) 执行摘要（给决策层）
【事实】当前站点存在 3 个高优先级阻塞项：`robots.txt` 404、`sitemap.xml` 404、三语页面缺失 `canonical/hreflang`。这三项会直接拉低抓取效率与多语言索引质量。  
【事实】三语页面 `title/description/keywords` 完全重复（唯一值均为 1），且 `h1=0`、结构化数据为 0。  
【事实】页面可抓取文本内容存在，但内链极弱（每页仅 1 条站内 `<a>` 链接），图片可引用语义弱（33 张图中仅 6 张非空 alt）。  
【推断】在不修复抓取与多语言标注前，品牌词能见度会继续依赖品牌名精确匹配，核心服务词竞争下可见性难提升。  

## 2) 技术审计结果（事实）

### 2.1 robots / sitemap / 状态码
- `https://yamaguchitech.cn/robots.txt`：HTTP 404
- `https://yamaguchitech.cn/sitemap.xml`：HTTP 404
- 三个审计页面均为 HTTP 200：
  - `/`、`/en`、`/tw`

### 2.2 canonical / hreflang
- `/`、`/en`、`/tw` 的 HTML 中：
  - `rel="canonical"` 数量均为 0
  - `hreflang` 链接数量均为 0

### 2.3 各语言 metadata 唯一性
- 三页 `title` 完全相同：`亚孖酷奇-小红书营销全链路服务`
- 三页 `meta description` 完全相同
- 三页 `meta keywords` 完全相同
- 元数据唯一值统计：
  - `title` 唯一值 = 1
  - `description` 唯一值 = 1
  - `keywords` 唯一值 = 1

### 2.4 可索引性阻塞项
- 页面层面：
  - 未发现 `meta robots=noindex`（为空）
  - 未发现 `X-Robots-Tag` 响应头
- 抓取层面阻塞：
  - `robots.txt` 不存在（404）
  - `sitemap.xml` 不存在（404）

### 2.5 标题结构与图片 alt
- 三页一致：
  - `h1=0`
  - `h2=8`
  - `img=33`
  - 非空 alt=6，空 alt=20，缺失 alt=7

### 2.6 Schema 存在性
- 三页 `application/ld+json` 数量均为 0
- 未发现 `schema.org` / `itemtype` 标记

### 2.7 内链基线
- 每页 `<a>` 链接总数=2：
  - 站内链接=1（语言首页自链）
  - 站外链接=1（工信部备案链接）
- 站内信息架构主要依赖前端交互元素，不利于抓取器发现更深层页面。

## 3) 搜索可见度基线（事实 + 推断）

### 3.1 品牌词与核心服务词（CN / Global）
【事实】品牌词可见性（精确品牌词）高于核心服务词。  
【事实】`YamaguchiTech` 英文品牌词检索结果存在品牌混淆（非本域结果占比高）。  
【推断】品牌保护不足（英文品牌实体弱、同名干扰）会影响 Global 端品牌召回效率。  

抽样结论（人工审阅实时结果）：
- 品牌词（CN）：`亚孖酷奇`
  - 可见到品牌相关页面（含 `yamaguchitech.cn` / `admin.yunshanggroup.cn`）。
- 品牌词（Global）：`YamaguchiTech`
  - 结果中出现与目标品牌无关的实体页面，品牌歧义明显。
- 服务词（CN）：`小红书营销代理`
  - 结果以第三方平台/代理列表为主，目标域优势不明显。
- 服务词（Global）：`Xiaohongshu marketing agency`
  - 头部结果多为第三方服务商页；目标域可见度偏弱。

### 3.2 site: 收录基线
【事实】`site:yamaguchitech.cn` 查询在本次实时采样中未获得稳定可复用结果，记为 `N/A`（避免伪精确）。  
【推断】结合 `robots/sitemap` 缺失与服务词弱可见，当前索引覆盖大概率不足，需要在修复后复测。

## 4) GEO 基线（20 问题）

### 4.1 测试问题集（中英）
1. 亚孖酷奇是做什么的
2. 亚孖酷奇提供哪些小红书营销服务
3. 如何在中国市场做小红书品牌投放
4. 小红书企业号认证流程是什么
5. 小红书信息流广告和搜索广告区别
6. 小红书KOL KOC组合策略怎么做
7. 出海品牌进入小红书的第一步是什么
8. 小红书营销代理商怎么选
9. 亚孖酷奇是否提供数据分析报告
10. 小红书品牌专区广告适合哪些场景
11. What does YamaguchiTech do
12. What services does YamaguchiTech provide for Rednote marketing
13. How to launch a Rednote marketing campaign in China
14. What is the process for Rednote business account verification
15. Difference between Rednote feed ads and search ads
16. How to choose a Rednote marketing agency
17. Does YamaguchiTech provide KOL KOC strategy
18. Best agency for Xiaohongshu marketing in China
19. How to improve brand awareness on Rednote
20. Does YamaguchiTech have case studies

### 4.2 基线指标
- 真实大模型品牌提及率（ChatGPT/Perplexity/Gemini 直接问答）：`N/A`
  - 原因：本次环境无法稳定调用带引用的对话式答案接口进行可复验批量采样。
- SERP 代理（低置信）：
  - 品牌域命中率（20 问 top10）：`0/20`（低置信）
  - 引用 URL 质量（top3 平均）：`1.67/3`（低置信）
  - 答案准确性代理（意图匹配）：`0%`（低置信）

【事实】该批量代理结果出现明显查询污染（返回与问题意图无关的词典/论坛页），不适合直接作为季度 KPI。  
【建议】将 GEO 真值采样纳入 W2：固定模型、固定提示词、固定地理与语言参数，手工复核 20 问后再作为正式基线。

## 5) 评分卡（0-100）
- 技术SEO：28
- 页面SEO：42
- 收录与抓取：22
- GEO可引用准备度：18
- 内容权威信号：46
- 综合参考分（等权）：31.2

## 6) 优先级修复建议（按周）
- W1：补 `robots.txt`、发布 `sitemap.xml`、补三语 `canonical+hreflang`
- W2：三语元数据重写（标题/描述/关键词去重本地化）、补 H1、补结构化数据
- W3：补站内可抓取内链（服务页、案例页、关于页）、系统化修复图片 alt
- W4：执行 GEO 真值复测并冻结 KPI 基线

## 7) 事实与来源链接

### 7.1 站内实测来源
- 首页：https://yamaguchitech.cn
- 英文页：https://yamaguchitech.cn/en
- 繁体页：https://yamaguchitech.cn/tw
- robots：https://yamaguchitech.cn/robots.txt
- sitemap：https://yamaguchitech.cn/sitemap.xml

### 7.2 外部搜索来源（用于可见度结论）
- 品牌词 CN（亚孖酷奇）：https://www.bing.com/search?q=%E4%BA%9A%E5%AD%96%E9%85%B7%E5%A5%87
- 品牌词 Global（YamaguchiTech）：https://www.bing.com/search?q=YamaguchiTech
- 服务词 CN（小红书营销代理）：https://www.bing.com/search?q=%E5%B0%8F%E7%BA%A2%E4%B9%A6%E8%90%A5%E9%94%80%E4%BB%A3%E7%90%86
- 服务词 Global（Xiaohongshu marketing agency）：https://www.bing.com/search?q=Xiaohongshu+marketing+agency
- site 查询：https://www.bing.com/search?q=site%3Ayamaguchitech.cn

### 7.3 相关结果页样本
- https://yamaguchitech.cn
- https://www.yunshangtech.com/en/redbook
- https://admin.yunshanggroup.cn/website/yamaguchi/tw

