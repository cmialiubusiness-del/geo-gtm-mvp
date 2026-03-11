"use client";

import { useEffect, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

import { apiFetch } from "@/lib/api";
import { useAppState } from "@/lib/app-state";
import { percentDisplay, roundDisplay, 平台文案 } from "@/lib/format";

type OverviewResponse = {
  range: string;
  provider: string;
  kpis: {
    mention_rate: number;
    top3_rate: number;
    first_pick_rate: number;
    competitor_appearance_rate: number;
    risk_claim_count: number;
  };
  trend: Array<{
    run_id: number;
    provider: string;
    started_at: string;
    mention_rate: number;
    risk_claim_count: number;
  }>;
};

type Run = {
  id: number;
  provider: string;
  started_at: string;
  finished_at: string | null;
  status: string;
};

function 运行状态文案(status: string): string {
  const mapping: Record<string, string> = {
    queued: "排队中",
    running: "运行中",
    completed: "已完成",
    failed: "失败"
  };
  return mapping[status] ?? status;
}

export default function DashboardPage() {
  const { token, provider, range, selectedBrandId, dataVersion } = useAppState();
  const [overview, setOverview] = useState<OverviewResponse | null>(null);
  const [runs, setRuns] = useState<Run[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token || !selectedBrandId) {
      setOverview(null);
      setRuns([]);
      return;
    }
    const load = async () => {
      try {
        const params = new URLSearchParams({
          range,
          provider,
          brand_id: String(selectedBrandId)
        });
        const query = params.toString();
        const [overviewPayload, runsPayload] = await Promise.all([
          apiFetch<OverviewResponse>(`/metrics/overview?${query}`, { token }),
          apiFetch<Run[]>(`/runs?brand_id=${selectedBrandId}`, { token })
        ]);
        setOverview(overviewPayload);
        setRuns(runsPayload);
        setError(null);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "加载失败");
      }
    };
    void load();
  }, [token, provider, range, selectedBrandId, dataVersion]);

  const cards = [
    ["提及率", percentDisplay(overview?.kpis.mention_rate)],
    ["前三占位率", percentDisplay(overview?.kpis.top3_rate)],
    ["首推率", percentDisplay(overview?.kpis.first_pick_rate)],
    ["竞品出现率", percentDisplay(overview?.kpis.competitor_appearance_rate)],
    ["风险断言数", `${roundDisplay(overview?.kpis.risk_claim_count)}`]
  ];

  return (
    <div className="space-y-5">
      {error ? (
        <div className="panel rounded-3xl px-4 py-3 text-sm text-rose-700">{error}</div>
      ) : null}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        {cards.map(([label, value]) => (
          <div key={label} className="panel rounded-3xl p-5">
            <div className="text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">
              {label}
            </div>
            <div className="mt-3 text-3xl font-bold text-ink">{value}</div>
          </div>
        ))}
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.4fr_0.8fr]">
        <div className="panel rounded-[2rem] p-5">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <div className="text-lg font-bold">最近4次运行趋势</div>
              <div className="text-sm text-slate-500">提及率与高风险断言数量</div>
            </div>
          </div>
          <div className="h-[340px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={overview?.trend ?? []}>
                <CartesianGrid stroke="#d8e4eb" strokeDasharray="3 3" />
                <XAxis
                  dataKey="started_at"
                  tickFormatter={(value) =>
                    new Date(value).toLocaleDateString("zh-CN", { month: "numeric", day: "numeric" })
                  }
                  stroke="#718096"
                />
                <YAxis yAxisId="left" stroke="#154c79" />
                <YAxis yAxisId="right" orientation="right" stroke="#9f1239" />
                <Tooltip
                  labelFormatter={(value) => new Date(String(value)).toLocaleString("zh-CN")}
                  formatter={(value, name) => {
                    if (name === "提及率") {
                      return [`${roundDisplay(Number(value))}%`, name];
                    }
                    return [roundDisplay(Number(value)), name];
                  }}
                />
                <Legend />
                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="mention_rate"
                  name="提及率"
                  stroke="#154c79"
                  strokeWidth={3}
                />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="risk_claim_count"
                  name="风险断言数"
                  stroke="#9f1239"
                  strokeWidth={3}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="panel rounded-[2rem] p-5">
          <div className="text-lg font-bold">最近运行记录</div>
          <div className="mt-4 space-y-3">
            {runs.slice(0, 6).map((run) => (
              <div
                key={run.id}
                className="rounded-3xl border border-slate-200 bg-white/80 px-4 py-3"
              >
                <div className="flex items-center justify-between">
                  <div className="font-semibold text-slate-800">#{run.id}</div>
                  <div className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
                    {平台文案(run.provider)}
                  </div>
                </div>
                <div className="mt-2 text-sm text-slate-500">
                  开始：{new Date(run.started_at).toLocaleString("zh-CN")}
                </div>
                <div className="mt-1 text-sm text-slate-500">
                  状态：{运行状态文案(run.status)}{" "}
                  {run.finished_at ? `· 完成 ${new Date(run.finished_at).toLocaleTimeString("zh-CN")}` : ""}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
