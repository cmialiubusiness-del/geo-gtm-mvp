Audience: Internal
Language: zh-CN
Last Updated: 2026-03-16
Owner: Shared

# W1-03D 直接竞品复核（重做版：高维度 + Concurate参考池）

## 0) 本次重做说明（针对你的反馈）
- 你提出的问题：
1. 维度太少，不够精准。
2. 海外 GEO 竞品需参考 Concurate 文章，但不限于该文。
- 本次改动：
1. 分析维度从“单一服务比较”升级为 `14 维`。
2. 海外竞品先从 Concurate 候选池抽取，再用官方站点与 SERP 二次筛选。
3. 输出改为“候选池 -> 筛选规则 -> 最终 Top5（CN/Global）-> 未入围原因”，保证可复核。

## 1) 分析维度（14维）
1. 业务定位（GEO/AEO/AI SEO）
2. ICP 与行业聚焦
3. 服务产品化（审计/方案/持续代运营）
4. AI 引擎覆盖声明（ChatGPT/Gemini/Perplexity/Claude/AIO）
5. 页面结构（服务/FAQ/案例/资源）
6. 内容证明强度（案例与数据）
7. 转化设计（CTA/表单/入口密度）
8. Schema 与可引用结构（FAQPage 等）
9. llms.txt / robots / sitemap 信号
10. 多语言与地域能力
11. 分发足迹（官网 + 社媒/第三方）
12. 公司主体透明度（成立/总部/实体）
13. 更新活跃度（lastmod/dateModified）
14. 对 Yamaguchi 的威胁等级

## 2) 海外候选池（参考来源）
- 参考文献：Concurate《17 Best Generative Engine Optimization Companies That Get You Visible on AI Search Results》
- 链接：[Concurate文章](https://concurate.com/best-generative-engine-optimization-companies-ai-visibility/)
- 文中发布时间：2026-01-14（页面显示 Last Updated: January 14, 2026）
- 文中候选公司（17）：Concurate、Avenue Z、Grow and Convert、Omnius、Skale、Epic Slope Partners、Omniscient Digital、iPullRank、First Page Sage、Victorious SEO、WebFX、Siege Media、Ignite Visibility、Spicy Margarita、Intero Digital、Single Grain、Seer Interactive。

## 3) 最终筛选规则（用于“直接竞品”）
必须满足以下 4 条中的至少 3 条：
1. 有官方可访问的 GEO/AEO/AI 搜索优化服务页。
2. 在品牌+服务词 SERP 中可稳定召回本域。
3. 服务页具备至少两类交付证明结构（FAQ/案例/资源/方法论）。
4. 有可追溯公司信息（about/company/地址/成立时间/版权主体等）。

## 4) 中国市场 Top5 直接竞品（高维摘要）

| 竞品 | 业务与模式 | 网站设计与转化 | 技术与更新 | 公司信息 | 威胁等级 | 证据 |
|---|---|---|---|---|---|---|
| YouFind AIPOGEO | GEO/AI SEO 专项，含评估报告与方案（产品化明显） | 长页服务 + FAQ + 强 CTA（转化导向） | sitemap 有最新 `lastmod=2026-03-16`；llms/robots 当前为 404（待确认全域） | about页可见香港地址与 YouFind 品牌体系 | P1 | [服务页](https://www.aipogeo.com/en/) · [关于页](https://www.youfind.hk/about) · [SERP](https://search.brave.com/search?q=YouFind%20AIPOGEO&source=web) · [Sitemap](https://www.aipogeo.com/sitemap.xml) |
| First Page HK | SEO for AI 服务化交付（框架+咨询） | FAQ/案例/资源结构完整（样本抓取历史值）；当前环境抓取波动（待复核） | sitemap 有持续更新信号（历史样本）；llms/robots 本轮请求超时（待确认） | 主页含 LocalBusiness 地址信号（HK） | P1 | [服务页](https://www.firstpage.hk/seo-for-ai/) · [主页](https://www.firstpage.hk/) · [SERP](https://search.brave.com/search?q=First%20Page%20SEO%20for%20AI%20Hong%20Kong&source=web) · [Sitemap](https://www.firstpage.hk/sitemap.xml) |
| AI SEO+ HK | AI SEO 与品牌增长组合服务 | 内容密度高、CTA 密度高、案例与资源并存 | schema 信号较多；sitemap 更新到 2026-03-12 | 页脚版权显示 `AI SEO+ By JPG Group Limited` | P1 | [服务页](https://aimarketing.com.hk/en/seo-service/) · [关于页](https://aimarketing.com.hk/en/about-us/) · [Sitemap](https://aimarketing.com.hk/sitemap.xml) · [SERP](https://search.brave.com/search?q=aimarketing%20ai%20seo%20hong%20kong&source=web) |
| Charlesworth | AEO/GEO 与中国渠道服务（Baidu/Wechat/XHS）联动 | 企业级服务架构，资源与渠道页并行 | robots 可访问；sitemap 为 weekly（无 lastmod） | about 明确 `Since 1998` 与多地办公室 | P1 | [GEO服务页](https://www.charlesworth-group.com/aeo-geo-optimisation-services) · [关于页](https://www.charlesworth-group.com/about-us) · [Sitemap](https://www.charlesworth-group.com/sitemap.xml) · [SERP](https://search.brave.com/search?q=Charlesworth%20AEO%20GEO&source=web) |
| Marketing to China (GMA) | 中国渠道增长服务强，适合作为 GEO 协同对手 | 长页咨询型，FAQ+表单完整 | sitemap index 最近更新可见 | about 页公开办公城市与创始人信息 | P1 | [服务页](https://marketingtochina.com/xiaohongshu-agency-china/) · [关于页](https://marketingtochina.com/about-us/) · [SERP](https://search.brave.com/search?q=Marketing%20to%20China%20xiaohongshu%20agency&source=web) · [Sitemap](https://marketingtochina.com/sitemap_index.xml) |

## 5) 海外市场 Top5 直接竞品（基于 Concurate池 + 二次筛选）

| 竞品 | 来源 | 业务与模式 | 网站设计与转化 | 技术与更新 | 公司信息 | 威胁等级 | 证据 |
|---|---|---|---|---|---|---|---|
| NoGood | Concurate外补充（SERP强） | AEO 专项服务 + 内容飞轮 | FAQ/资源密度高，强咨询导向 | llms/robots 均可访问；sitemap 与 dateModified 都较新 | 主页可见 NY 总部描述，版权主体 Berma LLC DBA NoGood | P1 | [服务页](https://nogood.io/answer-engine-optimization-service/) · [主页](https://nogood.io/) · [SERP](https://search.brave.com/search?q=NoGood%20answer%20engine%20optimization%20service&source=web) · [Sitemap](https://nogood.io/sitemap.xml) |
| Omnius | Concurate候选 | GEO/AI SEO/引擎专项页（geo-agency、chatgpt/gemini/perplexity等） | 服务集群化，资源与案例量高 | llms/robots 均 200；sitemap 有最近更新时间 | about 页有 Founded 信号（细节待确认） | P1 | [GEO页](https://www.omnius.so/geo-agency) · [关于页](https://www.omnius.so/about) · [SERP](https://search.brave.com/search?q=Omnius%20GEO%20agency&source=web) · [Sitemap](https://www.omnius.so/sitemap.xml) |
| First Page Sage | Concurate候选 | Generative Engine Optimization 独立服务 | 服务页结构清晰，CTA 明确 | robots 200，llms 404；页面有 dateModified，sitemap lastmod 信号弱（待确认） | 公司页透明度中等（about细节较少，待确认） | P2 | [服务页](https://firstpagesage.com/generative-engine-optimization/) · [联系页](https://firstpagesage.com/contact/) · [SERP](https://search.brave.com/search?q=First%20Page%20Sage%20generative%20engine%20optimization&source=web) · [Sitemap](https://firstpagesage.com/sitemap.xml) |
| Victorious | Concurate候选 | AEO 独立服务，偏企业 SEO 体系延展 | FAQ + 强 CTA 结构，服务化明显 | FAQPage schema 可见；sitemap lastmod 新；robots 200 | company 页可见城市信号（Chicago/New York） | P1 | [AEO服务页](https://victorious.com/services/answer-engine-optimization/) · [公司页](https://victorious.com/company/) · [SERP](https://search.brave.com/search?q=Victorious%20answer%20engine%20optimization%20service&source=web) · [Sitemap](https://victorious.com/sitemap.xml) |
| WebFX | Concurate候选 | AI Search Optimization / OmniSEO 路线 | 资源与案例体量巨大，转化入口密集 | llms/robots 200；sitemap 更新快；页面有 dateModified | about 页面完整（组织信息细节需二次抽样） | P1 | [AI Search服务页](https://www.webfx.com/seo/services/ai-search-optimization/) · [关于页](https://www.webfx.com/about/) · [SERP](https://search.brave.com/search?q=WebFX%20ai%20search%20optimization%20services&source=web) · [Sitemap](https://www.webfx.com/sitemap_index.xml) |

## 6) 未入围但在海外需持续跟踪
- Intero Digital：在 Concurate 候选中，但部分页面受防护（403/挑战页），本轮自动证据不足，先列待确认。
  - 证据：[Intero sitemap_index](https://interodigital.com/sitemap_index.xml)
- Siege Media / Ignite Visibility / Single Grain / Seer：候选池中存在，但本轮按“官方服务页可验证 + 直接业务重叠”优先级暂未进入 Top5。
  - 证据：[Concurate文章](https://concurate.com/best-generative-engine-optimization-companies-ai-visibility/)

## 7) 对 Yamaguchi 的更精准结论
1. 海外直接竞品已形成“GEO/AEO 专项服务页 + 高频资源更新 + 技术可引用结构 + 强转化入口”的四件套。
2. 中国市场竞品并非纯 GEO 公司，而是“GEO + 中国渠道交付”组合，这是你当前最该对齐的竞争形态。
3. Yamaguchi 若要冲前列，优先级应是：
   - `GEO主服务页产品化`（审计包/执行包/复盘包）
   - `FAQPage+Service schema` 批量化
   - `GEO × 小红书/Baidu/Wechat` 联动页矩阵
   - `品牌词防混淆`（尤其英文品牌检索）

## 8) 待确认项
- First Page HK 在当前抓取环境中存在间歇性超时，部分技术字段需人工二次复核。
- 海外部分公司的法律主体与融资背景未在公开页完整披露，标注为“待确认”。
