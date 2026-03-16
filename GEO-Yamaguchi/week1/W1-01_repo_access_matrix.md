Audience: Internal
Language: zh-CN
Last Updated: 2026-03-11
Owner: Shared

# W1-01 仓库权限矩阵（最小权限原则）

## 1) 当前工作区检查结果
- 检查路径：`/Users/mia/Documents/Codex/GEO/GEO-Yamaguchi`
- 是否为 git 仓库：否（未检测到 `.git`）
- 分支现状：N/A
- 提交现状：N/A
- CI/CD 配置：未发现（无 `.github/workflows/`、`gitlab-ci.yml`、`Jenkinsfile` 等）
- 结论：当前无法执行受控协作与发布，需先完成仓库初始化与权限治理落地。

## 2) 权限定义
- `read`：可查看代码、PR、流水线与发布记录。
- `write`：可推送到非受保护分支并创建 PR。
- `review`：可执行代码评审并提交审批结论。
- `merge`：可将已通过检查的 PR 合并到受保护分支。
- `release`：可触发生产发布与回滚流程。
- `admin`：可修改仓库保护规则、成员权限、密钥与集成配置。

## 3) 角色权限矩阵

| 角色 | read | write | review | merge | release | admin | 约束说明 |
|---|---|---|---|---|---|---|---|
| Mia（规划/统筹/GEO产品） | Y | Y | Y | Y(仅产品/内容类PR) | Y(业务放行) | N | 不参与仓库管理，保留业务放行权 |
| Ema（技术负责人） | Y | Y | Y | Y | Y | Y | 唯一默认管理员；负责技术放行与回滚决策 |
| Engineer | Y | Y | Y | N | N | N | 可提交与评审，不可直接合并受保护分支 |
| Content Editor | Y | Y(仅内容目录) | Y(仅内容变更) | N | N | N | 仅能修改 `content/`、`docs/` 等白名单路径 |
| Analyst | Y | Y(仅分析目录) | Y(仅数据分析变更) | N | N | N | 仅能修改 `analytics/`、`reports/` 等白名单路径 |

## 4) 平台权限落地建议
- 仓库角色组：
  - `Repo Admin`: Ema
  - `Maintainer-Biz`: Mia
  - `Contributors-Eng`: Engineer
  - `Contributors-Content`: Content Editor
  - `Contributors-Data`: Analyst
- 分支保护目标：
  - `main`、`release/*`、`hotfix/*` 设为受保护分支。
  - 禁止直接 push 到受保护分支。
  - 必须通过状态检查后才能合并。
- 代码所有权：
  - 使用 `CODEOWNERS` 强制目录级审批人。
  - `content/` 与 `docs/` 需 Mia 或其指定代理审批。
  - `infra/`、`ci/`、`deploy/` 需 Ema 审批。

## 5) 当前缺失治理项
- 缺失远程仓库与组织权限模型。
- 缺失分支保护、CODEOWNERS、PR 模板与提交规范。
- 缺失 CI/CD 流水线、密钥管理与发布审计链路。

## 6) 待补充信息
- TODO_REQUIRED_FROM_MIA：确认代码托管平台（GitHub/GitLab）与组织命名规则。
- TODO_REQUIRED_FROM_MIA：确认 `Content Editor`、`Analyst` 的人员名单与替补。
- TODO_REQUIRED_FROM_EMA：确定仓库管理员备份人（避免单点）。
- TODO_REQUIRED_FROM_EMA：确认目录白名单（`content/`、`analytics/`、`infra/` 的实际路径）。

## 本周决策清单（Mia/Ema）
- [ ] 决定代码托管平台与组织（Mia，截止 2026-03-12）。
- [ ] 决定管理员与备份管理员（Ema，截止 2026-03-12）。
- [ ] 决定角色到成员映射表（Mia/Ema，截止 2026-03-13）。
- [ ] 批准并执行权限矩阵落地（Mia/Ema，截止 2026-03-14）。
