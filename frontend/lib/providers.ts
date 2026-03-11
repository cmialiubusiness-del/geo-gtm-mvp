export const PROVIDER_OPTIONS = [
  { value: "deepseek", label: "DeepSeek" },
  { value: "tongyi", label: "通义千问" },
  { value: "doubao", label: "豆包" },
  { value: "kimi", label: "Kimi" },
  { value: "yuanbao", label: "腾讯元宝" },
  { value: "wenxin", label: "文心一言" },
  { value: "zhipu", label: "智谱清言" }
] as const;

export type ProviderKey = (typeof PROVIDER_OPTIONS)[number]["value"];
export const ALL_PROVIDERS = PROVIDER_OPTIONS.map((item) => item.value);

export function normalizeProviderFilter(value: string | null | undefined): string {
  const rawValue = (value ?? "all").trim().toLowerCase();
  if (!rawValue || rawValue === "all") {
    return "all";
  }
  const selected = rawValue
    .split(",")
    .map((item) => item.trim())
    .filter((item): item is ProviderKey =>
      ALL_PROVIDERS.includes(item as ProviderKey)
    );
  if (!selected.length || selected.length === ALL_PROVIDERS.length) {
    return "all";
  }
  const deduped = ALL_PROVIDERS.filter((item) => selected.includes(item));
  return deduped.join(",");
}

export function parseProviderFilter(value: string | null | undefined): ProviderKey[] {
  const normalized = normalizeProviderFilter(value);
  if (normalized === "all") {
    return [...ALL_PROVIDERS];
  }
  return normalized.split(",").filter((item): item is ProviderKey =>
    ALL_PROVIDERS.includes(item as ProviderKey)
  );
}

export function formatProviderFilterLabel(value: string | null | undefined): string {
  const selected = parseProviderFilter(value);
  if (selected.length === ALL_PROVIDERS.length) {
    return "全部平台";
  }
  const labels = selected
    .map((key) => PROVIDER_OPTIONS.find((item) => item.value === key)?.label ?? key)
    .filter(Boolean);
  if (labels.length <= 2) {
    return labels.join("、");
  }
  return `${labels.slice(0, 2).join("、")} +${labels.length - 2}`;
}
