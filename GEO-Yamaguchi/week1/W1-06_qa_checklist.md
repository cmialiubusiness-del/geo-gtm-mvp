Audience: Internal
Language: zh-CN
Last Updated: 2026-03-12
Owner: Shared

# W1-06 QA 检查清单（含 W1-03 对标增补）

## 1) 执行说明
- 适用阶段：上线前（Pre-Prod）、上线当日（Prod T+0）、上线后 24 小时（Prod T+24h）。
- 执行人：Ema 主执行，Mia 负责业务验收与内容正确性复核。
- 环境变量：
  - `DOMAIN=<主域名>`
  - `BASE=https://$DOMAIN`

## 2) 命令检查项（必须执行）

| 编号 | 检查项 | 命令 | 判定标准 | 责任人 | 失败处理 |
|---|---|---|---|---|---|
| Q-01 | 首页 canonical 唯一 | `curl -s "$BASE/" \| rg -o 'rel="canonical"' \| wc -l` | 返回 `1` | Ema | 修复 head 模板后重测 |
| Q-02 | `/en` canonical 正确 | `curl -s "$BASE/en" \| rg -o '<link[^>]+rel="canonical"[^>]*>'` | 包含 `$BASE/en` | Ema | 修复语言前缀映射 |
| Q-03 | `/tw` canonical 正确 | `curl -s "$BASE/tw" \| rg -o '<link[^>]+rel="canonical"[^>]*>'` | 包含 `$BASE/tw` | Ema | 修复语言前缀映射 |
| Q-04 | hreflang 齐全 | `curl -s "$BASE/en/services/baidu-ads" \| rg -o 'hreflang="[^"]+"'` | 包含 `zh-CN/en/zh-TW/x-default` | Ema | 修复 hreflang 生成器 |
| Q-05 | hreflang 回指闭环 | 检查 `/services/baidu-ads` `/en/services/baidu-ads` `/tw/services/baidu-ads` 的互链 | 三个版本互相可回指 | Ema | 修复缺失链接并复测 |
| Q-06 | robots 可访问 | `curl -sI "$BASE/robots.txt" \| head -n 1` | HTTP 200 | Ema | 修复静态挂载或路由 |
| Q-07 | robots 关键规则 | `curl -s "$BASE/robots.txt" \| rg 'Sitemap:|Disallow: /api/|Disallow: /preview/'` | 三条均命中 | Ema | 按策略文件重建 robots |
| Q-08 | sitemap index 可访问 | `curl -sI "$BASE/sitemap.xml" \| head -n 1` | HTTP 200 | Ema | 修复输出路径或网关 |
| Q-09 | sitemap XML 合法 | `curl -s "$BASE/sitemap.xml" \| xmllint --noout -` | 无报错 | Ema | 修复命名空间或非法字符 |
| Q-10 | sitemap 无坏链 | `for u in $(curl -s "$BASE/sitemap.xml" \| rg -o 'https://[^<]+'); do curl -sI "$u" \| head -n 1; done` | 不出现 404/500 | Ema | 下线坏链或修复路由 |
| Q-11 | FAQ 子图存在 | `curl -s "$BASE/sitemap.xml" \| rg 'sitemap-faq-zh.xml|sitemap-faq-en.xml|sitemap-faq-tw.xml'` | 全部命中 | Ema | 修复 sitemap index 引用 |
| Q-12 | 资源子图存在 | `curl -s "$BASE/sitemap.xml" \| rg 'sitemap-resources-zh.xml|sitemap-resources-en.xml|sitemap-resources-tw.xml'` | 全部命中 | Ema | 修复 sitemap index 引用 |
| Q-13 | FAQ 页面数量达标 | `curl -s "$BASE/sitemap-faq-zh.xml" \| rg -o '<loc>' \| wc -l` | `>= 12` | Ema | 补齐FAQ发布并重建子图 |
| Q-14 | 资源页面数量达标 | `curl -s "$BASE/sitemap-resources-zh.xml" \| rg -o '<loc>' \| wc -l` | `>= 8` | Ema | 补齐资源发布并重建子图 |
| Q-15 | 4条渠道服务页可访问 | `for p in /services/baidu-ads /services/xiaohongshu /services/wechat /services/full-funnel; do curl -sI "$BASE$p" \| head -n 1; done` | 全部 HTTP 200 | Ema | 修复路由或发布缺页 |
| Q-16 | 旧路径301迁移生效 | `curl -sI "$BASE/redbook" \| rg '301|location' -i` | 状态301且Location到新服务页 | Ema | 修复重定向规则 |
| Q-17 | 首页入口完整 | `curl -s "$BASE/" \| rg '/services|/cases|/resources|/faq'` | 四类入口均命中 | Ema | 修复导航和页脚模板 |
| Q-18 | Organization schema 命中 | `curl -s "$BASE/" \| rg '"@type":"Organization"|"@type": "Organization"'` | 至少命中1次 | Ema | 检查全局注入逻辑 |
| Q-19 | Service schema 命中 | `curl -s "$BASE/services/baidu-ads" \| rg '"@type":"Service"|"@type": "Service"'` | 命中1次 | Ema | 检查服务模板注入 |
| Q-20 | FAQ schema 命中 | `curl -s "$BASE/faq/what-is-xiaohongshu-marketing" \| rg '"@type":"FAQPage"|"@type": "FAQPage"'` | 命中1次 | Ema | 检查FAQ模板注入 |
| Q-21 | Breadcrumb schema 命中 | `curl -s "$BASE/resources/china-market-entry-guide" \| rg '"@type":"BreadcrumbList"|"@type": "BreadcrumbList"'` | 命中1次 | Ema | 检查面包屑生成器 |
| Q-22 | GA4 脚本存在 | `curl -s "$BASE/" \| rg 'gtag\(|GTM-|google-analytics|G-[A-Z0-9]+'` | 至少命中1项 | Ema | 检查GA4初始化与环境变量 |

## 3) 交互与业务检查项（人工）

| 编号 | 检查项 | 操作步骤 | 判定标准 | 责任人 |
|---|---|---|---|---|
| M-01 | 语言切换事件 | 首页切换 简体->英文->繁体 | DebugView 出现 `lang_switch` | Ema |
| M-02 | CTA 点击事件 | 点击首屏 CTA 与服务页 CTA | 出现 `cta_click` 且 `cta_id` 不为空 | Ema |
| M-03 | FAQ 交互事件 | 在 FAQ 详情页展开问答 | 出现 `faq_expand` 且 `faq_id` 不为空 | Ema |
| M-04 | 资源点击事件 | 在资源中心点击资源卡片 | 出现 `resource_card_click` | Ema |
| M-05 | 表单开始事件 | 联系表单任一字段首次聚焦 | 出现 `form_start` | Ema |
| M-06 | 表单成功事件 | 提交有效测试表单 | 出现 `form_submit_success` 且标记转化 | Ema |
| M-07 | 表单失败事件 | 构造无效必填并提交 | 出现 `form_submit_error` 且有 `error_code` | Ema |
| M-08 | 服务页内容复核 | Mia 检查4条渠道服务页结构 | 每页含流程案例FAQ锚点CTA | Mia |
| M-09 | FAQ与资源复核 | Mia 检查FAQ与资源文案准确性 | 无错语种无跨语言混写 | Mia |
| M-10 | 案例页量化字段复核 | Mia 抽检6个案例页 | 每页>=3个量化结果字段 | Mia |

## 4) 上线后 24 小时观察项

| 编号 | 指标 | 判定阈值 | 责任人 | 处置策略 |
|---|---|---|---|---|
| O-01 | 5xx 错误率 | 连续5分钟 > 2% | Ema | 暂停推进并评估回滚 |
| O-02 | 页面 P95 | 连续10分钟 > 2.5s | Ema | 降级非关键脚本或回滚 |
| O-03 | 表单成功率 | 较近7日均值下降 > 30% | Ema + Mia | 排查埋点和接口后决策 |
| O-04 | FAQ 访问与交互 | FAQ PV 或 `faq_expand` 异常归零 | Ema | 检查FAQ路由与埋点 |
| O-05 | 资源页点击率 | `resource_card_click` 较预期下降 > 30% | Mia + Ema | 排查入口位与卡片渲染 |
| O-06 | Search Console 异常 | canonical/hreflang 冲突激增 | Ema | 热修复标签与子图 |

## 5) 缺陷分级与处理时限
- P0：全站不可用或关键入口不可达（30分钟内处置）。
- P1：三语路由异常或表单链路中断（2小时内修复或回滚）。
- P2：schema 与部分页面标签异常（24小时内修复）。
- P3：文案与参数轻微问题（48小时内修复）。

## 6) 验收输出物
- `qa_command_log_<date>.txt`
- `qa_manual_check_<date>.md`
- `ga4_debug_screenshot_<date>.png`
- `qa_signoff_<date>.md`（Ema 技术签字 + Mia 业务签字）

## 7) 待确认决策清单
- [ ] FAQ 详情页正式slug清单是否固定（Owner: Mia）。
- [ ] 资源中心达标数量按中文还是三语总量统计（Owner: Mia / Ema）。
- [ ] `xmllint` 缺失时替代校验命令是否统一（Owner: Ema）。
