from __future__ import annotations

from app.core.enums import RunProvider

_PROVIDER_ORDER = [provider.value for provider in RunProvider]


def normalize_provider_selector(provider: str | None) -> str:
    raw_value = (provider or "all").strip().lower()
    if not raw_value or raw_value == "all":
        return "all"

    candidates = [item.strip().lower() for item in raw_value.split(",") if item.strip()]
    if not candidates or "all" in candidates:
        return "all"

    invalid = [item for item in candidates if item not in _PROVIDER_ORDER]
    if invalid:
        raise ValueError(f"不支持的平台：{', '.join(sorted(set(invalid)))}")

    selected = [item for item in _PROVIDER_ORDER if item in candidates]
    return ",".join(selected) if selected else "all"


def provider_values_from_selector(provider: str | None) -> list[str]:
    normalized = normalize_provider_selector(provider)
    if normalized == "all":
        return _PROVIDER_ORDER.copy()
    return normalized.split(",")


def provider_enums_from_selector(provider: str | None) -> list[RunProvider] | None:
    normalized = normalize_provider_selector(provider)
    if normalized == "all":
        return None
    return [RunProvider(item) for item in normalized.split(",")]


def provider_selector_contains(provider: str | None, provider_value: str) -> bool:
    normalized = normalize_provider_selector(provider)
    if normalized == "all":
        return True
    return provider_value.lower() in normalized.split(",")
