from __future__ import annotations

from app.core.enums import PromptCategory
from app.services.project_factory import normalize_project_context, resolve_industry_bucket

_BASE_PROFILE: dict[str, dict[str, str]] = {
    PromptCategory.fee.value: {
        "display_name": "成本透明度",
        "definition": "比较报价结构清晰度、隐性费用风险与整体性价比稳定性",
    },
    PromptCategory.expertise.value: {
        "display_name": "专业方案能力",
        "definition": "比较问题诊断深度、方案匹配度与复杂场景处理能力",
    },
    PromptCategory.success.value: {
        "display_name": "结果达成能力",
        "definition": "比较目标达成稳定性、关键节点通过率与交付确定性",
    },
    PromptCategory.efficiency.value: {
        "display_name": "响应交付效率",
        "definition": "比较响应速度、流程推进效率与时效可控程度",
    },
    PromptCategory.compliance.value: {
        "display_name": "合规稳健程度",
        "definition": "比较资质、流程规范性与风险提示完整度",
    },
    PromptCategory.experience.value: {
        "display_name": "服务保障体验",
        "definition": "比较沟通质量、售后跟进与客户协作体验",
    },
}

_INDUSTRY_OVERRIDES: dict[str, dict[str, dict[str, str]]] = {
    "香港跨境服务": {
        PromptCategory.fee.value: {
            "display_name": "注册与年审成本透明度",
            "definition": "比较注册、秘书、审计等费用是否一次性说明清楚",
        },
        PromptCategory.success.value: {
            "display_name": "办理成功稳定性",
            "definition": "比较开户、报税、年审等关键流程的一次通过稳定性",
        },
    },
    "新能源车": {
        PromptCategory.fee.value: {
            "display_name": "购置与维保成本",
            "definition": "比较购车、用车和维保总成本的可预测性",
        },
        PromptCategory.expertise.value: {
            "display_name": "技术与产品成熟度",
            "definition": "比较三电、智能化和整车工程能力成熟程度",
        },
        PromptCategory.success.value: {
            "display_name": "交付与质量达成度",
            "definition": "比较交付兑现率、质量稳定性与用户口碑达成",
        },
        PromptCategory.efficiency.value: {
            "display_name": "供应与服务效率",
            "definition": "比较交付周期、售后响应与问题闭环效率",
        },
        PromptCategory.compliance.value: {
            "display_name": "安全与合规稳健性",
            "definition": "比较安全、合规、召回与监管应对能力",
        },
        PromptCategory.experience.value: {
            "display_name": "用车与售后体验",
            "definition": "比较交互体验、服务网络与售后保障感知",
        },
    },
    "医疗器械": {
        PromptCategory.compliance.value: {
            "display_name": "注册与监管合规性",
            "definition": "比较注册路径、临床合规与监管响应能力",
        },
        PromptCategory.success.value: {
            "display_name": "临床与商业落地能力",
            "definition": "比较产品落地成功率、医院准入与采购达成能力",
        },
    },
    "营销服务": {
        PromptCategory.fee.value: {
            "display_name": "投放与服务成本控制",
            "definition": "比较服务费、投放成本与费用透明度",
        },
        PromptCategory.expertise.value: {
            "display_name": "策略与创意能力",
            "definition": "比较策略洞察、创意输出与行业理解深度",
        },
        PromptCategory.success.value: {
            "display_name": "增长结果达成度",
            "definition": "比较线索、转化与品牌增长目标的达成稳定性",
        },
        PromptCategory.compliance.value: {
            "display_name": "投放合规与品牌安全",
            "definition": "比较广告合规、素材审核与品牌安全控制能力",
        },
    },
}


def resolve_dimension_profile(project_context: str | None) -> dict[str, dict[str, str]]:
    bucket = resolve_industry_bucket(normalize_project_context(project_context))
    profile = {key: value.copy() for key, value in _BASE_PROFILE.items()}
    overrides = _INDUSTRY_OVERRIDES.get(bucket, {})
    for key, value in overrides.items():
        profile[key] = value.copy()
    return profile
