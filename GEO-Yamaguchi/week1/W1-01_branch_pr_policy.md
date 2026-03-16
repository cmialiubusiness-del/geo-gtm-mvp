Audience: Internal
Language: zh-CN
Last Updated: 2026-03-11
Owner: Shared

# W1-01 分支与 PR 治理规范

## 1) 适用范围
- 适用于 `GEO-Yamaguchi` 仓库所有代码、配置、内容与数据分析变更。
- 生效前提：先完成仓库初始化与受保护分支配置。

## 2) 分支策略
- 主干模式：`main` 为唯一长期分支，功能分支短生命周期。
- 受保护分支：`main`、`release/*`、`hotfix/*`。
- 分支命名规范：
  - `feat/<ticket>-<short-desc>`
  - `fix/<ticket>-<short-desc>`
  - `docs/<ticket>-<short-desc>`
  - `chore/<ticket>-<short-desc>`
  - `release/<YYYYMMDD>-<version>`
  - `hotfix/<incident>-<short-desc>`
- 命名示例：
  - `feat/W1-12-repo-audit-log`
  - `hotfix/INC-20260311-login-timeout`

## 3) 提交规范
- 强制使用 Conventional Commits：
  - `feat(scope): 描述`
  - `fix(scope): 描述`
  - `docs(scope): 描述`
  - `chore(scope): 描述`
  - `refactor(scope): 描述`
  - `test(scope): 描述`
- 单次提交必须可回滚，禁止将无关改动混入同一提交。
- 提交信息尾部附任务号：`Refs: W1-xx` 或事件号：`Inc: INC-xxxx`。

## 4) PR 创建与检查要求
- PR 标题：`[类型] 简述 (ticket)`，示例：`[feat] 增加发布前校验脚本 (W1-21)`。
- PR 描述必须包含：
  - 变更背景
  - 影响范围
  - 验证步骤
  - 回滚方式
- 必须通过的检查项（全部绿色才可合并）：
  - `lint`
  - `unit-test`
  - `build`
  - `dependency-scan`
  - `secret-scan`
  - `policy-check`（分支命名、提交规范、PR 模板完整性）

## 5) 审核人规则
- 基线规则：
  - 至少 1 名非作者审核通过。
  - 作者不可自审自合并。
- 强制审批人规则：
  - 涉及 `infra/`、`ci/`、`deploy/`、权限配置：必须 Ema 审核通过。
  - 涉及 `content/`、`docs/`、产品策略文档：必须 Mia 审核通过。
  - 同时涉及技术与业务目录：Mia 与 Ema 均需通过。
- 评审 SLA：
  - 常规 PR：24 小时内首次反馈。
  - 紧急 PR：2 小时内首次反馈。

## 6) 合并规则
- 仅允许 `Squash and Merge`。
- 合并前必须满足：
  - 全部状态检查通过。
  - 全部强制审批人通过。
  - 所有对话已解决。
  - 分支与 `main` 已同步到最新。
- 禁止：
  - 直接 push 到受保护分支。
  - `force push` 到受保护分支。

## 7) 热修复规则
- 触发条件：生产故障、严重安全事件、核心业务阻断。
- 执行流程：
  - 从 `main` 创建 `hotfix/*` 分支。
  - 提交最小变更，仅修复故障本体。
  - 必须通过 `build`、`unit-test`、`secret-scan` 三项最低检查。
  - 审批要求：Ema 必审；若影响用户可见行为，Mia 必须业务确认。
  - 合并后立即打 Tag 并发布。
  - 24 小时内补充复盘与测试，确保变更回灌主线流程。

## 8) 落地任务
- TODO_REQUIRED_FROM_MIA：确认 PR 模板字段中的业务验收项。
- TODO_REQUIRED_FROM_MIA：确认紧急发布对外沟通是否需要额外签核节点。
- TODO_REQUIRED_FROM_EMA：提供 CI 检查任务真实名称并配置为 Required Checks。
- TODO_REQUIRED_FROM_EMA：提交 `CODEOWNERS` 与分支保护策略配置。

## 本周决策清单（Mia/Ema）
- [ ] 确认分支模型采用主干模式（Mia/Ema）。
- [ ] 确认受保护分支列表与检查项（Ema）。
- [ ] 确认强制审批目录与审批人映射（Mia/Ema）。
- [ ] 确认热修复最低检查项与应急 SLA（Mia/Ema）。
