"use client";

import { useEffect, useState } from "react";

import { apiFetch } from "@/lib/api";
import { useAppState } from "@/lib/app-state";
import { roundDisplay, 平台文案 } from "@/lib/format";

type HijackResponse = {
  items: Array<{
    id: number;
    created_at: string;
    provider: string;
    prompt_text: string;
    hijack_flag: boolean;
    hijack_strength: number;
    recommended_entities: string[];
    brand_present: boolean;
  }>;
  top_prompts: Array<{
    prompt_text: string;
    count: number;
  }>;
};

export default function HijacksPage() {
  const { token, provider, range, selectedBrandId, dataVersion } = useAppState();
  const [payload, setPayload] = useState<HijackResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token || !selectedBrandId) {
      setPayload({ items: [], top_prompts: [] });
      return;
    }
    const load = async () => {
      try {
        const params = new URLSearchParams({
          range,
          provider,
          brand_id: String(selectedBrandId)
        });
        const nextPayload = await apiFetch<HijackResponse>(
          `/hijacks?${params.toString()}`,
          { token }
        );
        setPayload(nextPayload);
        setError(null);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "加载失败");
      }
    };
    void load();
  }, [token, provider, range, selectedBrandId, dataVersion]);

  return (
    <div className="grid gap-5 xl:grid-cols-[1fr_340px]">
      <section className="panel rounded-[2rem] p-5">
        {error ? (
          <div className="mb-4 rounded-3xl bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div>
        ) : null}
        <div className="mb-4 text-lg font-bold">竞品分流事件台账</div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>时间</th>
                <th>平台</th>
                <th>问题</th>
                <th>分流强度</th>
                <th>是否分流</th>
                <th>推荐实体（前三）</th>
                <th>客户品牌是否出现</th>
              </tr>
            </thead>
            <tbody>
              {(payload?.items ?? []).map((item) => (
                <tr key={item.id}>
                  <td>{new Date(item.created_at).toLocaleString("zh-CN")}</td>
                  <td>{平台文案(item.provider)}</td>
                  <td className="max-w-[280px] text-slate-600">{item.prompt_text}</td>
                  <td>{roundDisplay(item.hijack_strength)}</td>
                  <td>{item.hijack_flag ? "是" : "否"}</td>
                  <td>{item.recommended_entities.join(" / ")}</td>
                  <td>{item.brand_present ? "是" : "否"}</td>
                </tr>
              ))}
              {payload && payload.items.length === 0 ? (
                <tr>
                  <td className="text-slate-500" colSpan={7}>
                    当前品牌暂无运行数据，请点击右上角“立即运行”后等待几秒自动刷新。
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>

      <aside className="panel rounded-[2rem] p-5">
        <div className="text-lg font-bold">高频分流问题</div>
        <div className="mt-4 space-y-3">
          {(payload?.top_prompts ?? []).map((item) => (
            <div key={item.prompt_text} className="rounded-3xl border border-slate-200 bg-white/80 p-4">
              <div className="font-semibold text-slate-800">{item.prompt_text}</div>
              <div className="mt-2 text-sm text-slate-500">累计分流次数：{item.count}</div>
            </div>
          ))}
          {payload && payload.top_prompts.length === 0 ? (
            <div className="rounded-3xl border border-slate-200 bg-white/80 p-4 text-sm text-slate-500">
              当前筛选条件下暂无明显竞品分流风险，明细已展示完整推荐记录。
            </div>
          ) : null}
        </div>
      </aside>
    </div>
  );
}
