# AI品牌风险与可见性分析平台

一个可本地运行的 MVP 全栈产品，用于监控 DeepSeek / 豆包 / 元宝在“品牌项目场景”问题上的回答表现，完成断言级品牌风险分析、竞品分流识别、能力评分聚合，并生成 PDF 周报 / 月报。

## 技术栈

- 后端：FastAPI + SQLAlchemy + Alembic + Celery + Redis
- 数据库：PostgreSQL
- 前端：Next.js + TypeScript + Tailwind + Recharts
- 报告：ReportLab PDF
- 容器：Docker Compose（`api` / `web` / `db` / `redis` / `worker` / `scheduler`）

## 一键运行

在项目根目录执行：

```bash
docker compose up --build
```

服务地址：

- 前端：[http://localhost:3000](http://localhost:3000)
- 后端 API：[http://localhost:8000](http://localhost:8000)
- 健康检查：[http://localhost:8000/health](http://localhost:8000/health)

首次启动时，`api` 容器会自动：

1. 执行 Alembic 迁移
2. 写入 Demo 租户 / 品牌 / 竞品 / 50 条 prompts
3. 生成 3 个平台各 2 次历史运行（共 6 次）

## 演示账号

- 邮箱：`demo@example.com`
- 密码：`demo1234`
- Demo 组织：`Demo香港跨境服务`
- Demo 主品牌：`港X顾问`

登录后可在顶部点击“新建品牌项目”，输入主品牌名称并创建多个品牌项目，再通过顶部“项目切换”下拉框切换项目看板。
创建新品牌项目时，系统会自动生成：
- 该品牌专属的 50 条 prompts（包含品牌名 + 行业/场景）
- 3 个真实品牌竞品（行业匹配自动生成，可继续扩展到最多 12 个）

## 主要功能

- 多租户 JWT 登录，所有查询按 `org_id` 严格隔离
- 每品牌 50 条专属 Prompt Library（按 6 大能力分类 + 意图类型）
- Mock AI Provider（DeepSeek / 豆包 / 元宝）确定性回答生成
- 断言级分析：
  - 句子切分（支持中文标点）
  - 实体识别（品牌 + 3 个竞品）
  - 情绪分类（`+ / 0 / -`）
  - 影响度评分（`0-100`）
  - 风险分级（`Critical / High / Medium / Low`）
  - 竞品分流识别（Hijack flag + strength）
- 聚合：
  - 提及率 / Top3 占位率 / 首推率 / 竞品出现率
  - 品牌能力雷达
  - 竞品分类对比
- 报告（专业模板，中文字体可读）：
  - 每周 `AI品牌风险作战简报`
  - 每月 `AI品牌战略报告`

## API 概览

关键接口（均在 `/api` 下）：

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `GET /brand`
- `PUT /brand`
- `GET /brands`
- `POST /brands`
- `GET /competitors`
- `POST /competitors`
- `DELETE /competitors/{id}`
- `GET /competitors/suggestions?brand_id=...`
- `GET /competitors/search?brand_id=...&q=关键词`
- `GET /prompts`
- `GET /prompts?brand_id=...`
- `GET /meta/industries`
- `POST /runs/run-now`
- `GET /runs`
- `GET /metrics/overview?range=last_run|7d|30d&provider=all|deepseek|doubao|yuanbao`
- `GET /metrics/capabilities?...`
- `GET /metrics/competitors?...`
- `GET /claims?...`
- `GET /hijacks?...`
- `POST /reports/weekly`
- `POST /reports/monthly`
- `GET /reports`
- `GET /reports/{id}/download`

## 手动触发采集

登录前端后可直接点击顶部“立即运行”。

也可以手动调用 API：

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"demo1234"}'
```

拿到 `access_token` 后：

```bash
curl -X POST http://localhost:8000/api/runs/run-now \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"provider":"all","brand_id":1}'
```

多品牌相关：

- `GET /api/brands`：获取当前组织的所有品牌项目
- `POST /api/brands`：创建品牌项目（主品牌名 + aliases）
- 大部分查询接口支持 `brand_id` 参数（如 `/runs`、`/metrics/*`、`/claims`、`/hijacks`、`/reports`）
- `POST /api/brands` 支持 `project_context`，用于生成行业相关 prompts
- 设置页支持“系统推荐竞品 + 关键词搜索竞品 + 手动新增竞品”

## 报告文件位置

- 容器内：`/app/generated_reports`
- 本地映射目录：`./backend/generated_reports`

在前端“报告中心”页面可以生成并下载 PDF。

## 运行测试

如果你在本地直接运行后端（非 Docker），可在 `backend` 目录执行：

```bash
PYTHONPATH=. pytest
```

当前测试覆盖：

- 情绪分类
- 影响度评分
- 竞品分流识别
- 能力评分

## 目录结构

```text
/backend
  /alembic
  /app
  /tests
/frontend
docker-compose.yml
README.md
```
