from __future__ import annotations

from enum import Enum


class StrEnum(str, Enum):
    def __str__(self) -> str:
        return str(self.value)


class UserRole(StrEnum):
    admin = "admin"
    analyst = "analyst"


class PromptCategory(StrEnum):
    fee = "费用"
    expertise = "专业能力"
    success = "成功率"
    efficiency = "效率"
    compliance = "合规"
    experience = "服务体验"


class PromptIntentType(StrEnum):
    selection = "选择"
    risk = "风险"
    fee = "费用"
    complaint = "投诉"
    comparison = "对比"


class RunProvider(StrEnum):
    deepseek = "deepseek"
    doubao = "doubao"
    yuanbao = "yuanbao"
    tongyi = "tongyi"
    kimi = "kimi"
    wenxin = "wenxin"
    zhipu = "zhipu"


class RunStatus(StrEnum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class ClaimSubjectType(StrEnum):
    brand = "brand"
    competitor = "competitor"


class ClaimSentiment(StrEnum):
    positive = "+"
    neutral = "0"
    negative = "-"


class ClaimRiskLevel(StrEnum):
    critical = "Critical"
    high = "High"
    medium = "Medium"
    low = "Low"


class ReportType(StrEnum):
    weekly_brief = "weekly_brief"
    monthly_strategy = "monthly_strategy"
