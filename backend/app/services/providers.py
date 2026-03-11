from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.core.config import settings
from app.core.enums import PromptCategory, PromptIntentType, RunProvider
from app.models import Brand, Competitor, Prompt

PROVIDER_OFFSETS = {
    RunProvider.deepseek: 1,
    RunProvider.doubao: 3,
    RunProvider.yuanbao: 5,
    RunProvider.tongyi: 7,
    RunProvider.kimi: 9,
    RunProvider.wenxin: 11,
    RunProvider.zhipu: 13,
}

PROVIDER_STYLE = {
    RunProvider.deepseek: "更偏向结构化比较，会额外提醒资料完整度。",
    RunProvider.doubao: "更偏向营销推荐，强调体验和响应速度。",
    RunProvider.yuanbao: "更偏向风险规避，会主动提示合规与投诉风险。",
    RunProvider.tongyi: "更偏向均衡评估，通常先给关键结论再展开对比理由。",
    RunProvider.kimi: "更偏向长文解释，常强调过程细节和可执行建议。",
    RunProvider.wenxin: "更偏向框架化表达，常从能力、风险、成本三层展开。",
    RunProvider.zhipu: "更偏向要点归纳，通常先给结论并保留审慎提示。",
}


@dataclass(frozen=True)
class ProviderAnswer:
    raw_text: str


class ProviderClient(Protocol):
    def generate_answer(self, prompt: Prompt, brand: Brand, competitors: list[Competitor]) -> ProviderAnswer: ...


def _score_variant(prompt: Prompt, provider: RunProvider) -> int:
    return (prompt.id * 7 + PROVIDER_OFFSETS[provider]) % 6


def _rotated_competitors(prompt: Prompt, competitors: list[Competitor], provider: RunProvider) -> list[Competitor]:
    if not competitors:
        return []
    offset = (prompt.id + PROVIDER_OFFSETS[provider]) % len(competitors)
    return competitors[offset:] + competitors[:offset]


def _ranked_entities(prompt: Prompt, brand: Brand, competitors: list[Competitor], provider: RunProvider) -> tuple[list[str], int | None]:
    variant = _score_variant(prompt, provider)
    rotated = _rotated_competitors(prompt, competitors, provider)
    brand_intent = brand.name in prompt.text or any(alias in prompt.text for alias in brand.aliases)
    if len(rotated) < 3:
        padded = list(rotated)
        while len(padded) < 3:
            padded.append(rotated[len(padded) % len(rotated)] if rotated else brand)
        rotated = padded

    if variant in (0, 4):
        top3 = [brand.name, rotated[0].name, rotated[1].name]
        return top3, None
    if variant == 1:
        top3 = [rotated[0].name, brand.name, rotated[1].name]
        return top3, None
    if variant == 2:
        top3 = [rotated[0].name, rotated[1].name, brand.name]
        return top3, None
    if brand_intent and variant in (3, 5):
        top3 = [rotated[0].name, rotated[1].name, rotated[2].name]
        return top3, 4
    top3 = [rotated[0].name, rotated[1].name, rotated[2].name]
    return top3, None


def _positive_claim(entity_name: str, category: PromptCategory) -> str:
    mapping = {
        PromptCategory.fee: f"{entity_name} 报价透明，收费结构清晰，适合先做预算评估。",
        PromptCategory.expertise: f"{entity_name} 团队经验丰富，处理复杂业务场景更专业。",
        PromptCategory.success: f"{entity_name} 预审流程更细，关键目标达成率通常更稳。",
        PromptCategory.efficiency: f"{entity_name} 资料清单清晰，推进节奏高效，适合赶时间的项目。",
        PromptCategory.compliance: f"{entity_name} 合规说明完整，持牌流程表达更稳妥，风险提示更到位。",
        PromptCategory.experience: f"{entity_name} 售后跟进及时，沟通细致，整体服务体验更省心。",
    }
    return mapping[category]


def _neutral_claim(entity_name: str, category: PromptCategory) -> str:
    mapping = {
        PromptCategory.fee: f"{entity_name} 通常会提供基础报价清单，但仍需要核对年费与附加项。",
        PromptCategory.expertise: f"{entity_name} 提供标准顾问方案，适合常规业务需求。",
        PromptCategory.success: f"{entity_name} 流程包含材料预审，最终结果仍要看客户条件匹配度。",
        PromptCategory.efficiency: f"{entity_name} 会先给资料清单，流程通常分阶段推进。",
        PromptCategory.compliance: f"{entity_name} 提供合规步骤说明，签约前仍需要复核资质与合同。",
        PromptCategory.experience: f"{entity_name} 售后流程包含群内跟进，整体体验取决于顾问对接人。",
    }
    return mapping[category]


def _negative_claim(entity_name: str, category: PromptCategory, variant: int) -> str:
    if variant % 4 == 0:
        return f"{entity_name} 曾被提到存在无牌照风险，若材料处理失误可能被查，签约前要谨慎。"
    if variant % 4 == 1:
        return f"{entity_name} 近期有投诉称存在隐形收费和服务差的问题，口碑承压。"
    if variant % 4 == 2:
        return f"{entity_name} 收费高且报价偏贵，预算敏感客户容易觉得不如其他机构。"
    return f"{entity_name} 响应一般，部分客户反馈推进偏慢，未必适合急单。"


class MockProviderClient:
    def __init__(self, provider: RunProvider) -> None:
        self.provider = provider

    def generate_answer(self, prompt: Prompt, brand: Brand, competitors: list[Competitor]) -> ProviderAnswer:
        ranked, brand_rank_override = _ranked_entities(prompt, brand, competitors, self.provider)
        variant = _score_variant(prompt, self.provider)
        scene = brand.project_context or "目标业务场景"

        lines = [
            f"平台：{self.provider.value}",
            f"基于 {scene} 的常见反馈，当前推荐顺序如下：",
        ]
        for index, entity in enumerate(ranked, start=1):
            lines.append(f"{index}. {entity}")
        if brand_rank_override:
            lines.append(f"{brand_rank_override}. {brand.name}")

        lines.append(_positive_claim(ranked[0], prompt.category))
        lines.append(_neutral_claim(ranked[1], prompt.category))
        lines.append(_negative_claim(ranked[2], prompt.category, variant))

        if brand_rank_override:
            lines.append(
                f"{brand.name} 目前仅列在第{brand_rank_override}位，原因是近期被讨论收费高且响应一般。"
            )
        elif ranked[0] != brand.name and (brand.name in prompt.text or any(alias in prompt.text for alias in brand.aliases)):
            lines.append(
                f"{ranked[0]} 在这一题上更常被首选，{brand.name} 没有排到最前。"
            )
        else:
            lines.append(
                f"{brand.name} 的表现会受具体顾问配置影响，签约前仍建议对比合同条款。"
            )

        if prompt.intent_type in {PromptIntentType.risk, PromptIntentType.complaint}:
            lines.append(
                f"额外提醒：如遇到无牌照、隐形收费或差评集中出现，优先规避相关机构。"
            )
        elif prompt.intent_type == PromptIntentType.fee:
            lines.append("预算有限时，重点对比年费、秘书费和开户辅导费是否一次性写清。")
        else:
            lines.append("建议先比对方案适配度，再确认牌照、交付节奏和售后责任边界。")

        lines.append(PROVIDER_STYLE[self.provider])
        return ProviderAnswer(raw_text="\n".join(lines))


class RealProviderClient:
    def __init__(self, provider: RunProvider) -> None:
        self.provider = provider

    def generate_answer(self, prompt: Prompt, brand: Brand, competitors: list[Competitor]) -> ProviderAnswer:
        if not settings.real_provider_enabled or not settings.real_provider_api_key:
            raise RuntimeError("Real provider mode is not configured")
        fallback = MockProviderClient(self.provider)
        return fallback.generate_answer(prompt, brand, competitors)


def get_provider_client(provider: RunProvider, use_real: bool = False) -> ProviderClient:
    if use_real:
        return RealProviderClient(provider)
    return MockProviderClient(provider)
