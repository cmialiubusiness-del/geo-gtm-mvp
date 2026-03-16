Audience: Internal
Language: zh-CN
Last Updated: 2026-03-16
Owner: Shared

# W1-04 GEO媒体试投方案（垂直细化版）

## 1. 先说明“保证”边界
- 任何AI平台（国内/海外）是否引用某篇内容，最终由其在线检索与排序机制决定，无法做“绝对引用保证”。
- 本方案可保证的是：
  1. 每个投放平台都配置“国内AI引用适配动作”和“海外AI引用适配动作”；
  2. 每周按固定问题集做抽样验收；
  3. 未达阈值的平台在下一周自动降级或替换。

## 2. 媒体池已收敛为“垂直且可投放”
- 总数：20个平台（中国10，海外10）。
- 全部有可执行入口（广告/投稿/合作/目录上架），已写入清单。
- 泛社交与高噪声渠道已剔除，集中在 SEO/GEO/AI/开发者/采购目录垂直媒体。

A层（立刻试投）：
- 中国：知乎、CSDN、站长之家、掘金
- 海外：Search Engine Journal、Search Engine Land、Search Engine Roundtable、Stack Overflow、Reddit、G2

B层（次轮测试）：
- SegmentFault、鸟哥笔记、人人都是产品经理、InfoQ中国、机器之心、雷峰网、MarTech、Capterra、EIN Presswire

C层（观察）：
- PR Newswire（仅重大节点）

## 3. 国内/海外 AI 引用双轨执行

### 3.1 国内AI引用轨（文心/元宝/Kimi等联网场景）
- 内容载体优先：知乎问答、CSDN技术文、站长之家SEO稿、掘金实操帖。
- 写作结构：
  - 标题必须含问题词（如“GEO如何提高AI引用率”）。
  - 正文必须有“定义-步骤-案例-结论”四段式。
  - 每篇至少1段可直接摘录的50-120字结论段。
- 分发节奏：每周至少4条中文首发 + 2条中文改写。

### 3.2 海外AI引用轨（Bing/Perplexity/Google AI）
- 内容载体优先：SEJ/SEL/SERoundtable类垂直媒体 + Stack Overflow + Reddit + G2/Capterra。
- 写作结构：
  - 英文长文中加入可验证数据点与出处链接。
  - Q&A内容优先“问题-答案-代码/步骤-限制条件”结构。
  - 每篇都加“Last Updated”与作者信息。
- 分发节奏：每周至少3条英文首发 + 2条英文问答/讨论贴。

## 4. 月预算（千元级）

| 档位 | 月预算 | A层占比 | B层占比 | C层占比 |
|---|---:|---:|---:|---:|
| 低预算 | RMB 6,000 | 85% | 15% | 0% |
| 中预算 | RMB 12,000 | 75% | 25% | 0% |

建议花法：
- 低预算：以“自然分发+问答运营”为主，不买高价新闻线。
- 中预算：在低预算基础上，增加 EIN Presswire（月1篇）和目录平台资料优化。

## 5. 4周动作（可直接执行）

### Week 1
- 建立问题词池：国内20个、海外20个。
- 完成4篇核心稿（CN2/EN2），形成标准模板。

### Week 2
- A层平台首发：国内4条、海外3条。
- 同步做 Stack Overflow/Reddit 的问答和讨论贴。

### Week 3
- 对前两周高表现内容做二次改写，投放到B层。
- 上线 G2/Capterra 资料页优化与评价引导。

### Week 4
- 按固定问题集抽样检测：
  - 国内AI：文心/元宝/Kimi
  - 海外AI：Bing/Perplexity/Google AI
- 输出“保留/降级/替换”清单，更新下月预算。

## 6. 验收指标（分国内/海外）

| 指标 | 低预算目标（6k/月） | 中预算目标（12k/月） |
|---|---:|---:|
| 国内AI引用次数（抽样问题集） | >= 18 | >= 35 |
| 海外AI引用次数（抽样问题集） | >= 15 | >= 32 |
| 新增可索引URL | >= 24 | >= 45 |
| 被引用域名数 | >= 10 | >= 18 |
| MQL | >= 12 | >= 26 |

降级规则：
- 连续2周“引用次数=0”且“互动低于中位数”的平台，自动降级到观察池。

## 7. 关键来源（含平台与AI引用机制）
1. Google AI features: https://developers.google.com/search/docs/appearance/ai-features
2. Google 链接属性（nofollow/ugc/sponsored）: https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links
3. Bing AI Search Performance: https://blogs.bing.com/webmaster/september-2025/introducing-ai-search-performance-in-bing-webmaster-tools
4. Bing AI Search Queries Report: https://blogs.bing.com/webmaster/august-2025/our-new-reporting-features-in-bing-webmaster-tools-ai-search-queries-report-and-heatmap
5. Perplexity 引用机制: https://www.perplexity.ai/hub/technical-faq/how-does-perplexity-work
6. 百度AI搜索（生成式AI检索能力）: https://cloud.baidu.com/product/ai-search.html
7. Kimi（Websites/Deep Research入口）: https://kimi.moonshot.cn/
8. 腾讯元宝（搜索入口）: https://yuanbao.tencent.com/
9. Tranco流量排名口径: https://tranco-list.eu/top-1m.csv.zip
10. EIN Presswire公开价格: https://www.einpresswire.com/pricing

