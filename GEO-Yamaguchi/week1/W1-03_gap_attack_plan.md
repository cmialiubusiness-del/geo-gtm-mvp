Audience: Internal
Language: zh-CN
Last Updated: 2026-03-16
Owner: Shared

# W1-03 差距地图与 4 周攻坚计划（GEO 业务线优先）

## 一、目标与边界
- 目标A：在官网新增并做强 GEO 业务线，让“GEO/AEO/AI 搜索优化”词有可承接页面。
- 目标B：用 GEO 业务线带动整体业务（尤其中国市场增长服务）在 SEO 与 GEO 的可见性。
- 目标C：4 周内完成低成本快补，8-12 周完成中期结构化提升。

## 二、差距地图（基于 CN+Global 直接竞品）

| 差距项 | Yamaguchi 当前状态 | 竞品对标证据 | 影响判断 | 优先级 |
|---|---|---|---|---|
| GEO 服务承接缺失 | 未见独立 GEO/AEO 服务页 | [NoGood AEO](https://nogood.io/answer-engine-optimization-service/) · [Omnius GEO](https://www.omnius.so/geo-agency) · [AIPOGEO](https://www.aipogeo.com/en/) | 服务词无法承接，新增业务线难进入高意图漏斗 | P0 |
| 抓取与索引基础薄弱 | `robots.txt` 与 `sitemap.xml` 返回 404（样本） | [Yamaguchi robots](https://yamaguchitech.cn/robots.txt) · [Yamaguchi sitemap](https://yamaguchitech.cn/sitemap.xml) | 新页面收录与更新反馈不稳定 | P0 |
| 可引用结构不足 | FAQ结构与 schema 信号弱 | [Victorious AEO](https://victorious.com/services/answer-engine-optimization/) · [NoGood AEO](https://nogood.io/answer-engine-optimization-service/) | 在 AI 摘要/答案场景中被引用概率低 | P0 |
| GEO 与中国渠道协同弱 | GEO 与小红书/Baidu/Wechat服务线未形成联动矩阵 | [Charlesworth GEO](https://www.charlesworth-group.com/aeo-geo-optimisation-services) · [Marketing to China](https://marketingtochina.com/xiaohongshu-agency-china/) | 难以放大整体业务协同价值 | P1 |
| 品牌词防混淆不足 | `YamaguchiTech GEO` 出现非同类结果 | [SERP样本](https://search.brave.com/search?q=YamaguchiTech%20GEO&source=web) | 品牌检索转化效率低 | P1 |
| 海外候选池覆盖不系统 | 过去仅少量海外样本 | [Concurate候选池](https://concurate.com/best-generative-engine-optimization-companies-ai-visibility/) | 监控面不足，策略易滞后 | P1 |

## 三、4 周低成本快补（可直接转 Jira）

| Jira ID | 攻坚点 | Owner | 周期 | 交付物 | DoD（验收标准） | 证据依据 |
|---|---|---|---|---|---|---|
| GEO-W1-101 | GEO 信息架构上线（Hub+子页） | Ema | Week 1 | `/geo/` 主页 + `/geo/chatgpt/` + `/geo/perplexity/` + `/geo/gemini/` | 4 个页面可访问且可索引；每页有明确服务CTA | [Omnius GEO](https://www.omnius.so/geo-agency) · [WebFX AI Search](https://www.webfx.com/seo/services/ai-search-optimization/) |
| GEO-W1-102 | 抓取基础修复（robots/sitemap/canonical） | Ema | Week 1 | `robots.txt`、`sitemap.xml`、canonical 规范 | robots 与 sitemap 返回 200；Search Console 可提交 | [Yamaguchi robots](https://yamaguchitech.cn/robots.txt) · [Yamaguchi sitemap](https://yamaguchitech.cn/sitemap.xml) |
| GEO-W1-103 | GEO 服务页模板化（服务/FAQ/案例/资源） | Mia | Week 1-2 | 统一页面组件模板与内容框架 | 每个 GEO 服务页至少包含 4 大结构块 | [NoGood AEO](https://nogood.io/answer-engine-optimization-service/) · [First Page HK](https://www.firstpage.hk/seo-for-ai/) |
| GEO-W1-104 | FAQ 可回答化 + FAQPage schema | Ema | Week 2 | 20 条 GEO FAQ（中英各10）+ FAQPage JSON-LD | 抽检 10 条 FAQ 可直接回答；结构化数据校验通过 | [Victorious AEO](https://victorious.com/services/answer-engine-optimization/) |
| GEO-W1-105 | 案例证据卡快补（GEO×中国渠道） | Mia | Week 2 | 6 张案例卡（含行业/问题/动作/结果） | 每张案例卡含量化指标与来源说明 | [Charlesworth GEO](https://www.charlesworth-group.com/aeo-geo-optimisation-services) · [Marketing to China](https://marketingtochina.com/xiaohongshu-agency-china/) |
| GEO-W1-106 | 引擎词集内容补位（ChatGPT/Gemini/Perplexity） | Mia | Week 2-3 | 3 篇引擎专项文章 + 内链到服务页 | 引擎专项词进入可抓取页并形成内链闭环 | [Omnius GEO](https://www.omnius.so/geo-agency) |
| GEO-W1-107 | 品牌防混淆页（Brand+GEO） | Ema | Week 3 | `About YamaguchiTech GEO` 说明页 + FAQ | 品牌词 SERP 可稳定召回官方说明页（待确认） | [YamaguchiTech SERP](https://search.brave.com/search?q=YamaguchiTech%20GEO&source=web) |
| GEO-W1-108 | 第三方分发起步（LinkedIn+行业目录+PR） | Mia | Week 3-4 | 4 篇外部分发内容 + 2 个目录资料页 | 每条分发回链到 GEO Hub，形成首轮外部触点 | [Clutch GEO目录](https://clutch.co/seo-firms/generative-engine-optimization) |
| GEO-W1-109 | CN+Global SERP 监控看板 | Ema | Week 1-4 | 固定关键词集监控TSV + 周报 | 每周输出份额变化与新增域名预警 | [Global样本](https://search.brave.com/search?q=GEO%20optimization%20services%20hong%20kong&source=web) · [CN样本](https://search.brave.com/search?q=%E7%94%9F%E6%88%90%E5%BC%8F%E5%BC%95%E6%93%8E%E4%BC%98%E5%8C%96%20%E6%9C%8D%E5%8A%A1%20%E5%95%86&source=web&country=cn&lang=zh-hans) |
| GEO-W1-110 | Concurate 候选池滚动复筛机制 | Mia | Week 4 | 海外候选池复筛表（月更） | Concurate 17家公司至少完成 10 家深度复核 | [Concurate候选池](https://concurate.com/best-generative-engine-optimization-companies-ai-visibility/) |

## 四、8-12 周中期提升项

| Jira ID | 提升项 | Owner | 周期 | 目标 | 核心KPI | 证据依据 |
|---|---|---|---|---|---|---|
| GEO-M1-201 | 行业场景页矩阵（行业×引擎×渠道） | Ema | 8-12周 | 建立可规模化的 GEO 长尾入口 | 新增 30+ 可索引场景页 | [WebFX AI Search](https://www.webfx.com/seo/services/ai-search-optimization/) |
| GEO-M1-202 | GEO 数据资产（基准报告+数据卡） | Mia | 8-12周 | 提升被引用概率与外链吸附力 | 2 份报告 + 20 条数据卡 | [First Page Sage GEO](https://firstpagesage.com/generative-engine-optimization/) |
| GEO-M1-203 | 结构化数据体系升级（Service/FAQ/Article） | Ema | 8-12周 | 让核心页可引用结构覆盖 >90% | 核心模板页 schema 校验通过率 >90% | [Victorious AEO](https://victorious.com/services/answer-engine-optimization/) |
| GEO-M1-204 | 官网-第三方-线索回流闭环 | Mia | 8-12周 | 扩展分发面并提升回流线索 | 每月新增 6+ 有效外部触点 | [NoGood AEO](https://nogood.io/answer-engine-optimization-service/) |
| GEO-M1-205 | GEO 服务转化链 AB 测试 | Ema | 8-12周 | 提升 GEO 线索转化效率 | GEO 线索转化率目标 +20%（内部目标） | [AIPOGEO](https://www.aipogeo.com/en/) |

## 五、风险与待确认
- `firstpage.hk` 在当前环境下有间歇性抓取波动，相关技术结论标记为“待确认”，建议人工复核一次。
- CN 环境下 GEO/AEO 术语搜索结果媒体占比高，建议 Week 2 增加人工抽样，避免纯自动抓取偏差。
