"use client";

import { useEffect, useState } from "react";
import {
  Legend,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip
} from "recharts";

import { apiFetch } from "@/lib/api";
import { useAppState } from "@/lib/app-state";
import { roundDisplay } from "@/lib/format";

type CapabilityRow = {
  category: string;
  display_name: string;
  definition: string;
  score: number;
  label: string;
  top_positive_claims: string[];
  top_negative_claims: string[];
};

type CapabilitiesResponse = {
  radar: Array<{ category: string; display_name: string; 品牌: number }>;
  categories: CapabilityRow[];
};

type Competitor = {
  id: number;
  name: string;
};

type CompetitorMetricsResponse = {
  comparisons: Array<{
    competitor_id: number;
    competitor_name: string;
    scores: CapabilityRow[];
  }>;
};

export default function CapabilitiesPage() {
  const { token, provider, range, selectedBrandId, dataVersion } = useAppState();
  const [capabilities, setCapabilities] = useState<CapabilitiesResponse | null>(null);
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [selectedCompetitorId, setSelectedCompetitorId] = useState<number | null>(null);
  const [selectedComparison, setSelectedComparison] =
    useState<CompetitorMetricsResponse["comparisons"][number] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token || !selectedBrandId) {
      setCapabilities(null);
      setCompetitors([]);
      return;
    }
    const loadBase = async () => {
      try {
        const params = new URLSearchParams({
          range,
          provider,
          brand_id: String(selectedBrandId)
        });
        const [capabilitiesPayload, competitorsPayload] = await Promise.all([
          apiFetch<CapabilitiesResponse>(`/metrics/capabilities?${params.toString()}`, { token }),
          apiFetch<Competitor[]>(`/competitors?brand_id=${selectedBrandId}`, { token })
        ]);
        setCapabilities(capabilitiesPayload);
        setCompetitors(competitorsPayload);
        setSelectedCompetitorId((current) =>
          competitorsPayload.some((item) => item.id === current)
            ? current
            : competitorsPayload[0]?.id ?? null
        );
        setError(null);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "加载失败");
      }
    };
    void loadBase();
  }, [token, provider, range, selectedBrandId, dataVersion]);

  useEffect(() => {
    if (
      !token ||
      !selectedCompetitorId ||
      !selectedBrandId ||
      !competitors.some((item) => item.id === selectedCompetitorId)
    ) {
      setSelectedComparison(null);
      return;
    }
    const loadComparison = async () => {
      try {
        const params = new URLSearchParams({
          competitor_id: String(selectedCompetitorId),
          range,
          provider,
          brand_id: String(selectedBrandId)
        });
        const payload = await apiFetch<CompetitorMetricsResponse>(
          `/metrics/competitors?${params.toString()}`,
          { token }
        );
        setSelectedComparison(payload.comparisons[0] ?? null);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "竞品对比加载失败");
      }
    };
    void loadComparison();
  }, [token, selectedCompetitorId, provider, range, selectedBrandId, dataVersion, competitors]);

  const radarData =
    capabilities?.radar.map((row) => {
      const comparisonScore = selectedComparison?.scores.find(
        (item) => item.category === row.category
      )?.score;
      return {
        category: row.display_name,
        品牌: row.品牌,
        竞品: comparisonScore ?? 0
      };
    }) ?? [];

  return (
    <div className="space-y-5">
      {error ? (
        <div className="panel rounded-3xl px-4 py-3 text-sm text-rose-700">{error}</div>
      ) : null}

      <section className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="panel rounded-[2rem] p-5">
          <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <div className="text-lg font-bold">品牌能力雷达图</div>
              <div className="text-sm text-slate-500">六大能力维度 0-100 分</div>
            </div>
            <select
              className="field md:w-56"
              value={selectedCompetitorId ?? ""}
              onChange={(event) => setSelectedCompetitorId(Number(event.target.value))}
              disabled={!competitors.length}
            >
              {!competitors.length ? <option value="">暂无竞品</option> : null}
              {competitors.map((competitor) => (
                <option key={competitor.id} value={competitor.id}>
                  {competitor.name}
                </option>
              ))}
            </select>
          </div>
          <div className="h-[420px]">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid stroke="#d6e3ea" />
                <PolarAngleAxis dataKey="category" tick={{ fill: "#365266", fontSize: 12 }} />
                <PolarRadiusAxis domain={[0, 100]} tick={{ fill: "#6a7d8f", fontSize: 11 }} />
                <Tooltip formatter={(value) => roundDisplay(Number(value))} />
                <Legend />
                <Radar name="品牌" dataKey="品牌" stroke="#154c79" fill="#154c79" fillOpacity={0.28} />
                <Radar name="竞品" dataKey="竞品" stroke="#b45309" fill="#b45309" fillOpacity={0.18} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="panel rounded-[2rem] p-5">
          <div className="text-lg font-bold">竞品对比摘要（行业维度）</div>
          <div className="mt-4 space-y-3">
            {(selectedComparison?.scores ?? []).map((score) => {
              const brandScore =
                capabilities?.categories.find((item) => item.category === score.category)?.score ?? 0;
              const gap = roundDisplay(brandScore - score.score);
              return (
                <div
                  key={score.category}
                  className="rounded-3xl border border-slate-200 bg-white/80 px-4 py-3"
                >
                  <div className="flex items-center justify-between">
                    <div className="font-semibold text-slate-800">{score.display_name}</div>
                    <div className="text-sm font-semibold text-amber-700">
                      品牌 {roundDisplay(brandScore)} / 竞品 {roundDisplay(score.score)}
                    </div>
                  </div>
                  <div className="mt-1 text-sm text-slate-500">{score.definition}</div>
                  <div className="mt-1 text-xs text-slate-400">
                    差值：{gap > 0 ? `品牌领先 ${gap}` : gap < 0 ? `竞品领先 ${Math.abs(gap)}` : "持平"}
                  </div>
                </div>
              );
            })}
            {competitors.length > 0 && !selectedComparison ? (
              <div className="rounded-3xl border border-slate-200 bg-white/80 px-4 py-3 text-sm text-slate-500">
                当前项目暂无可对比数据，请先点击“立即运行”完成一次采集。
              </div>
            ) : null}
            {!competitors.length ? (
              <div className="rounded-3xl border border-slate-200 bg-white/80 px-4 py-3 text-sm text-slate-500">
                当前项目暂无竞品，请在“设置”中先添加竞品后再对比。
              </div>
            ) : null}
          </div>
        </div>
      </section>

      <section className="panel rounded-[2rem] p-5">
        <div className="mb-4 text-lg font-bold">分类明细</div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>分类</th>
                <th>维度说明</th>
                <th>得分</th>
                <th>标签</th>
                <th>正向断言示例</th>
                <th>负向断言示例</th>
              </tr>
            </thead>
            <tbody>
              {(capabilities?.categories ?? []).map((row) => (
                <tr key={row.category}>
                  <td className="font-semibold text-slate-800">{row.display_name}</td>
                  <td className="max-w-[260px] text-slate-600">{row.definition}</td>
                  <td>{roundDisplay(row.score)}</td>
                  <td>{row.label}</td>
                  <td className="max-w-[320px] text-slate-600">
                    {row.top_positive_claims.length ? row.top_positive_claims.join("；") : "无"}
                  </td>
                  <td className="max-w-[320px] text-slate-600">
                    {row.top_negative_claims.length ? row.top_negative_claims.join("；") : "无"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
