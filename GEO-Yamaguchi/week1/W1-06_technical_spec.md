Audience: Internal
Language: zh-CN
Last Updated: 2026-03-12
Owner: Shared

# W1-06 技术实施规格（SEO + 追踪 + 可回滚）

## 1) 目标与范围
- 目标：修复当前站点在 SEO 基础设施（canonical/hreflang/robots/sitemap/schema）和数据追踪（GA4）上的缺口，形成可上线、可验证、可回滚的实施方案。
- 范围：`/`、`/en`、`/tw` 及后续新增页面模板（服务页、FAQ Hub、资源页、案例页、落地页）。
- 非范围：视觉改版、广告投放执行、第三方目录注册执行。

## 2) 当前基线与 W1-03 对标结论

### 2.1 审计基线（W1-02）
- `GET /robots.txt` 返回 404。
- `GET /sitemap.xml` 返回 404。
- `/`、`/en`、`/tw` 页面 head 未发现 canonical。
- `/`、`/en`、`/tw` 页面 head 未发现 hreflang。
- 页面未发现稳定注入的 JSON-LD（Organization/Service/FAQ/Breadcrumb）。
- GA4 事件映射缺失统一字典。

### 2.2 对标增补项（W1-03）
- FAQ Hub 缺口：缺少可回答结构化问题页（P0）。
- 资源中心缺口：缺少问题词内容承接与长尾覆盖（P0）。
- 服务页层级偏浅：渠道化服务页不足（P1）。
- 案例页模板不统一：量化结果字段不稳定（P1）。
- 首页到服务/案例/资源/FAQ 显式入口不足（P1）。

## 3) 技术栈假设与实施落点
- 假设：当前站点为 Nuxt SSR（审计结果含 `__NUXT__` 标识）。
- 若为 Nuxt2，默认落点：
  - `nuxt.config.js`：全局 head、插件与中间件注册。
  - `plugins/seo-meta.js`：canonical/hreflang/schema 生成器。
  - `serverMiddleware/robots.ts`：robots 输出。
  - `serverMiddleware/sitemap.ts`：sitemap index 与子 sitemap 输出。
  - `plugins/ga4.client.ts`：GA4 初始化与事件上报。
- 若为 Nuxt3/其他 SSR：实现等价能力，验收标准不变。

## 4) URL 架构与 canonical 规则

### 4.1 URL 架构（含 W1-03 增补）
- 语言根路径：
  - 简体中文：`/`
  - 英文：`/en`
  - 繁体中文：`/tw`
- 核心栏目（简体示例，英文/繁体加前缀）：
  - 服务中心：`/services`
  - 渠道服务页：`/services/baidu-ads`、`/services/xiaohongshu`、`/services/wechat`、`/services/full-funnel`
  - FAQ Hub：`/faq`
  - FAQ 详情：`/faq/<topic-slug>`
  - 资源中心：`/resources`
  - 资源详情：`/resources/<slug>`
  - 案例中心：`/cases`
  - 案例详情：`/cases/<slug>`
- 统一规范：全小写、短横线分词、非根路径不带结尾斜杠。

### 4.2 历史路径迁移
- `旧服务路径` -> `新服务路径` 301（例如 `/redbook` -> `/services/xiaohongshu`）。
- `旧案例路径` -> `新案例路径` 301（若从 `/work/*` 迁移到 `/cases/*`）。
- 迁移期至少保留 90 天并持续监控 404。

### 4.3 canonical 规则
- 每个可索引页面仅输出 1 条 canonical。
- canonical 指向“当前语言版本”的标准 URL，不跨语言互指。
- 清洗参数：剔除 `utm_*`、`gclid`、`fbclid`、`spm`。
- 分页页仅保留 `page` 参数（如存在），其余参数不进入 canonical。
- 预览/测试/内部页：`noindex`，不输出 canonical。

## 5) `/` `/en` `/tw` 及后续页面 hreflang 规则

### 5.1 基础规则
- 每个可索引页面输出：`zh-CN`、`en`、`zh-TW`、`x-default`。
- `x-default` 指向简体页面（默认语言落地页）。
- hreflang 必须双向回指并与 canonical 一致。

### 5.2 Hub 与详情页规则
- FAQ Hub、资源中心、服务页、案例页全部纳入 hreflang。
- 若某语言版本暂未上线：
  - 不输出不存在 URL。
  - 当前页仅输出已存在语言 + `x-default`。
  - sitemap 中同步剔除缺失语言 URL。

## 6) robots 规则与爬虫策略

### 6.1 robots.txt 目标内容
- 生产环境示例：
  - `User-agent: *`
  - `Disallow: /api/`
  - `Disallow: /preview/`
  - `Disallow: /internal/`
  - `Disallow: /*?*utm_`
  - `Allow: /_nuxt/`
  - `Sitemap: https://<主域>/sitemap.xml`
- 预发/测试环境：`Disallow: /` 全站禁止抓取。

### 6.2 爬虫策略（对标补充）
- FAQ/资源/服务/案例页面默认可抓取可索引。
- 参数页、内部工具页、实验页强制 `noindex,nofollow`。
- 对高频无价值参数页做路径级阻断，降低抓取预算浪费。

## 7) sitemap 结构与更新触发机制

### 7.1 结构
- `sitemap.xml` 为 sitemap index。
- 子 sitemap 拆分：
  - `sitemap-pages-zh.xml`、`sitemap-pages-en.xml`、`sitemap-pages-tw.xml`
  - `sitemap-services-zh.xml`、`sitemap-services-en.xml`、`sitemap-services-tw.xml`
  - `sitemap-faq-zh.xml`、`sitemap-faq-en.xml`、`sitemap-faq-tw.xml`
  - `sitemap-resources-zh.xml`、`sitemap-resources-en.xml`、`sitemap-resources-tw.xml`
  - `sitemap-cases-zh.xml`、`sitemap-cases-en.xml`、`sitemap-cases-tw.xml`
- URL 节点必须包含 `<loc>`、`<lastmod>`，并支持多语言等价关系。

### 7.2 更新触发
- 触发事件：发布/下线、slug 变更、noindex 变更、语言版本新增/删除。
- 触发机制：CMS webhook 或 CI 合并后任务。
- 原子发布：新文件校验通过后替换，失败不覆盖旧版本。

### 7.3 对标增补验收口径
- FAQ 详情页（三语合计）>= 12 条可索引 URL。
- 资源详情页（三语合计）>= 8 条可索引 URL。
- 渠道化服务页至少 4 条（每种语言均可访问）。

## 8) schema 注入方案（Organization / Service / FAQ / Breadcrumb）

### 8.1 Organization（全站）
- 注入所有可索引页面；`@id` 全站稳定唯一。
- 核心字段：`name`、`url`、`logo`、`sameAs`、`contactPoint`。

### 8.2 Service（服务页）
- 渠道服务页必须注入 Service。
- 核心字段：`name`、`description`、`provider`、`areaServed`、`serviceType`。

### 8.3 FAQ（FAQ Hub 与详情页）
- FAQ 详情页必须注入 FAQPage。
- 问答内容需与页面可见内容一致，不允许隐藏问答。

### 8.4 Breadcrumb（内容页）
- 首页以外的服务页、FAQ、资源页、案例页都必须注入 BreadcrumbList。
- 面包屑路径需与实际导航一致。

### 8.5 注入约束
- 统一 schema 工厂生成，禁止组件散落硬编码。
- 单页同类型 schema 仅出现 1 次（FAQPage 除多问答实体）。
- 生成失败不中断渲染，但必须上报错误日志。

## 9) GA4 事件映射（表单、CTA、关键交互）

### 9.1 公共参数
- `page_lang`、`page_type`、`page_path`、`component`。

### 9.2 事件字典（对标增补）

| 事件名 | 触发时机 | 关键参数 | 是否转化 | Owner |
|---|---|---|---|---|
| `cta_click` | 点击模块 CTA | `cta_id`,`cta_text`,`position`,`target_url` | 否 | Ema |
| `lang_switch` | 语言切换 | `from_lang`,`to_lang`,`from_path`,`to_path` | 否 | Ema |
| `form_start` | 表单首次聚焦 | `form_id`,`entry_section` | 否 | Ema |
| `form_submit` | 表单提交发起 | `form_id`,`field_count` | 否 | Ema |
| `form_submit_success` | 表单提交成功 | `form_id`,`lead_type`,`response_ms` | 是 | Ema |
| `form_submit_error` | 表单提交失败 | `form_id`,`error_code`,`error_stage` | 否 | Ema |
| `faq_expand` | FAQ 折叠项展开 | `faq_id`,`faq_topic`,`page_lang` | 否 | Ema |
| `resource_card_click` | 点击资源卡片 | `resource_id`,`position`,`page_lang` | 否 | Ema |
| `case_card_click` | 点击案例卡片 | `case_id`,`position`,`page_lang` | 否 | Ema |
| `nav_hub_click` | 点击导航Hub入口 | `hub_type`,`from_section`,`page_lang` | 否 | Ema |

## 10) QA 验收门槛
- canonical：抽检页面 100% 单值正确。
- hreflang：三语互链闭环通过率 100%。
- robots：生产 200 且包含 sitemap。
- sitemap：index 与子图可访问、可解析、无 404 URL。
- schema：四类 schema 在对应模板命中且无重复。
- GA4：关键事件在 DebugView 可见，参数完整率 >= 95%。
- 对标增补：
  - FAQ Hub + FAQ 详情页达到计划数量并被 sitemap 收录。
  - 资源中心达到计划数量并被 sitemap 收录。
  - 首页到服务/案例/资源/FAQ 的显式入口完整。

## 11) 责任边界（Mia / Ema）

| 模块 | Mia 职责 | Ema 职责 |
|---|---|---|
| 信息架构与栏目策略 | 确认 FAQ/资源/服务/案例栏目结构与优先级 | 落地路由、重定向、canonical/hreflang |
| robots 与 sitemap | 确认索引白名单/黑名单 | 实现 robots/sitemap 与自动更新 |
| Schema | 提供业务字段映射与文案来源 | 实现 JSON-LD 模板与日志 |
| GA4 | 确认转化口径与事件优先级 | 实现埋点、调试、监控 |
| 上线与回滚 | 业务放行与恢复确认 | 技术放行、值守、回滚执行 |

## 12) W1-03 对标对齐清单（纳入 W1-06）
- FAQ Hub + 12 个 FAQ 详情页（中英繁路径齐全）。
- 资源中心 + 8 篇问题词内容页（中英繁路径齐全）。
- 渠道化服务页 4 条（Baidu/Xiaohongshu/Wechat/Full-funnel）。
- 案例页模板统一并补齐量化结果字段。
- 首页与页脚加入服务/案例/资源/FAQ 入口。
- SERP 周报自动化接入并形成周度产出。

## 13) 里程碑（W1-06）
- D1：完成 URL 架构、栏目路径、重定向与 canonical/hreflang 规则冻结。
- D2：完成 robots/sitemap 落地（含 FAQ/资源/服务/案例子图）。
- D3：完成 schema 注入与 GA4 对标事件联调。
- D4：完成 FAQ/资源/服务/案例对标页面技术验收。
- D5：执行上线、24h 观察与复盘。

## 14) 待确认决策清单
- [ ] 主域名固定 `www` 还是裸域（Owner: Mia，截止 2026-03-13）。
- [ ] `/tw` 是否长期保留，不改为 `/zh-tw`（Owner: Mia，截止 2026-03-13）。
- [ ] FAQ 与资源页 slug 命名规范（按主题还是按问题句）（Owner: Mia，截止 2026-03-13）。
- [ ] 历史路径迁移保留时长（90 天或 180 天）（Owner: Ema，截止 2026-03-13）。
- [ ] GA4 接入方式（GTM 还是原生 gtag）与 Measurement ID（Owner: Ema，截止 2026-03-13）。
- [ ] `form_submit_success` 之外是否追加 `resource_card_click` 为辅助转化（Owner: Mia，截止 2026-03-14）。
- [ ] SERP 周报产物归档路径与查看权限（Owner: Mia / Ema，截止 2026-03-14）。
