# GEO Pricing (MVP) - March 2026

## 1) Pricing Design Principles

- Charge on a value-aligned unit, not just seats.
- Keep the first package simple enough for fast sales.
- Preserve gross margin while allowing heavy usage growth.
- Match your current MVP capabilities: multi-brand projects, prompt runs, competitor/risk analysis, reporting.

## 2) Primary Billable Unit

Use a single consumption unit:

`1 GEO Check = 1 prompt x 1 model x 1 locale x 1 run`

Monthly usage formula:

`Monthly GEO Checks = Prompt Count x Model Count x Locale Count x Runs per Month`

This maps directly to your workflow and can be metered in backend jobs.

## 3) Recommended Packages (USD)

### Starter - $399/month
- 1 brand project
- 20,000 GEO Checks / month
- Up to 200 active prompts
- Up to 3 models
- Weekly scheduled reports
- Core dashboard, sentiment, mention/risk monitoring
- 5 seats

### Growth - $1,290/month
- 3 brand projects
- 100,000 GEO Checks / month
- Up to 800 active prompts
- Up to 5 models
- Daily monitoring + risk alerts
- Competitor benchmarking + monthly strategy report
- API/CSV export
- 15 seats

### Scale - $3,490/month
- 10 brand projects
- 400,000 GEO Checks / month
- Up to 3,000 active prompts
- Full model matrix + multi-locale runs
- Priority processing queue
- Weekly + monthly executive reporting
- SSO/SAML and audit logs
- 40 seats

### Enterprise - From $8,000/month
- Custom brand/project volume
- 1M+ GEO Checks / month
- Private deployment / VPC options
- Custom SLA, security review, dedicated support
- Custom connectors and BI integration

## 4) Overage and Add-ons

### Overage
- Standard checks: $10 per 1,000 checks
- Premium-model checks: +$6 per 1,000 checks

### Optional add-ons
- Extra brand project: $180/month each
- Extra 100,000 standard checks: $850/month
- White-label reporting: $300/month
- Premium onboarding (taxonomy + prompt design): one-time $2,000

## 5) Why These Price Points

Benchmarks show your buyers are already used to paying monthly SaaS subscriptions in this range:

- Semrush core plans are publicly listed around $139.95 / $249.95 / $499.95 per month.
- Semrush AI Toolkit is listed at $99/month as an add-on.
- Brand24 plans are listed around $199 / $299 / $399 per month.
- Ahrefs has publicly listed tiered pricing (localized by currency/region).

GEO is a higher-touch, model-cost-bearing workflow (simulation + analysis + reporting), so pricing above pure monitoring tools is defensible, especially for multi-brand teams.

## 6) Unit Economics Guardrails

Set internal targets:

- Gross margin target: >= 75%
- Alert threshold: COGS exceeds 30% of MRR in any account
- Soft throttle warning: 80% quota
- Hard overage billing: 100% quota

Track per-account:
- Model token spend
- Queue/runtime cost
- Storage + report generation cost
- Support time

## 7) Packaging Rules for Sales

- Annual contract discount: 18% (standard), 22% for Enterprise multi-year.
- Minimum contract for agencies: Growth tier.
- Keep "premium model mode" as a paid toggle to protect margin.
- Offer a 14-day paid pilot ($600 credit) rather than a fully free trial.

## 8) Fast Rollout Plan (Next 30 Days)

1. Launch only Starter + Growth publicly; keep Scale/Enterprise as "Talk to Sales".
2. Meter and expose `checks_used / checks_limit` in dashboard and billing API.
3. Run 8-12 pilot accounts and measure:
   - Actual checks/month
   - Conversion to paid after pilot
   - Overage acceptance rate
4. Reprice after 60 days based on realized COGS and close rates.

## 9) Pricing References (Public Pages)

- OpenAI API pricing: https://openai.com/api/pricing/
- Anthropic pricing: https://docs.anthropic.com/en/docs/about-claude/pricing
- Google Gemini API pricing: https://ai.google.dev/gemini-api/docs/pricing
- DeepSeek API pricing: https://api-docs.deepseek.com/quick_start/pricing
- Semrush plans/toolkits: https://www.semrush.com/kb/1370-subscription-plans-and-available-toolkits
- Semrush pricing tiers: https://www.semrush.com/kb/1283-semrush-pricing-plans
- Semrush AI Toolkit: https://www.semrush.com/kb/1678-ai-toolkit-subscription
- Ahrefs pricing: https://ahrefs.com/pricing
- Brand24 pricing: https://brand24.com/pricing/
