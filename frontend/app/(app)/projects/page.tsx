"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { apiFetch } from "@/lib/api";
import { percentDisplay, roundDisplay, 平台文案 } from "@/lib/format";
import { useAppState } from "@/lib/app-state";

type 项目条目 = {
  brand_id: number;
  brand_name: string;
  project_context: string;
  competitor_count: number;
  active_prompt_count: number;
  run_count_30d: number;
  high_risk_claim_count_30d: number;
  hijack_count_30d: number;
  mention_rate_last_run: number;
  last_run_provider: string | null;
  last_run_status: string | null;
  last_run_started_at: string | null;
};

type 项目总览 = {
  total_projects: number;
  healthy_projects: number;
  warning_projects: number;
  items: 项目条目[];
};

function 状态文案(status: string | null): string {
  if (!status) return "暂无运行";
  const mapping: Record<string, string> = {
    queued: "排队中",
    running: "运行中",
    completed: "已完成",
    failed: "失败"
  };
  return mapping[status] ?? status;
}

export default function ProjectsPage() {
  const router = useRouter();
  const { token, setSelectedBrandId, dataVersion } = useAppState();
  const [payload, setPayload] = useState<项目总览 | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      setPayload(null);
      return;
    }
    const load = async () => {
      try {
        const result = await apiFetch<项目总览>("/projects/overview", { token });
        setPayload(result);
        setError(null);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "加载失败");
      }
    };
    void load();
  }, [token, dataVersion]);

  return (
    <div className="space-y-5">
      {error ? (
        <div className="panel rounded-3xl px-4 py-3 text-sm text-rose-700">{error}</div>
      ) : null}
      <section className="grid gap-4 md:grid-cols-3">
        <div className="panel rounded-3xl p-5">
          <div className="text-sm text-slate-500">项目总数</div>
          <div className="mt-2 text-3xl font-bold text-ink">{roundDisplay(payload?.total_projects)}</div>
        </div>
        <div className="panel rounded-3xl p-5">
          <div className="text-sm text-slate-500">运行健康项目</div>
          <div className="mt-2 text-3xl font-bold text-emerald-700">{roundDisplay(payload?.healthy_projects)}</div>
        </div>
        <div className="panel rounded-3xl p-5">
          <div className="text-sm text-slate-500">需关注项目</div>
          <div className="mt-2 text-3xl font-bold text-amber-700">{roundDisplay(payload?.warning_projects)}</div>
        </div>
      </section>

      <section className="panel rounded-[2rem] p-5">
        <div className="mb-4 text-lg font-bold">全项目运营状态</div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>项目</th>
                <th>行业</th>
                <th>竞品数</th>
                <th>问题数</th>
                <th>近30天运行</th>
                <th>近30天高风险</th>
                <th>近30天分流</th>
                <th>最近提及率</th>
                <th>最近平台</th>
                <th>最近状态</th>
                <th>最近运行时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {(payload?.items ?? []).map((item) => (
                <tr key={item.brand_id}>
                  <td className="font-semibold text-slate-800">{item.brand_name}</td>
                  <td>{item.project_context}</td>
                  <td>{roundDisplay(item.competitor_count)}</td>
                  <td>{roundDisplay(item.active_prompt_count)}</td>
                  <td>{roundDisplay(item.run_count_30d)}</td>
                  <td>{roundDisplay(item.high_risk_claim_count_30d)}</td>
                  <td>{roundDisplay(item.hijack_count_30d)}</td>
                  <td>{percentDisplay(item.mention_rate_last_run)}</td>
                  <td>{平台文案(item.last_run_provider)}</td>
                  <td>{状态文案(item.last_run_status)}</td>
                  <td>
                    {item.last_run_started_at
                      ? new Date(item.last_run_started_at).toLocaleString("zh-CN")
                      : "暂无"}
                  </td>
                  <td>
                    <button
                      className="btn btn-secondary"
                      onClick={() => {
                        setSelectedBrandId(item.brand_id);
                        router.push("/dashboard");
                      }}
                    >
                      查看
                    </button>
                  </td>
                </tr>
              ))}
              {payload && payload.items.length === 0 ? (
                <tr>
                  <td colSpan={12} className="text-slate-500">
                    当前暂无项目
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
