export function roundDisplay(value: number | null | undefined): number {
  return Math.round(Number(value ?? 0));
}

export function percentDisplay(value: number | null | undefined): string {
  return `${roundDisplay(value)}%`;
}

export function 平台文案(value: string | null | undefined): string {
  if (!value) {
    return "暂无";
  }
  const mapping: Record<string, string> = {
    deepseek: "DeepSeek",
    doubao: "豆包",
    yuanbao: "腾讯元宝",
    tongyi: "通义千问",
    kimi: "Kimi",
    wenxin: "文心一言",
    zhipu: "智谱清言"
  };
  return mapping[String(value).toLowerCase()] ?? String(value);
}
