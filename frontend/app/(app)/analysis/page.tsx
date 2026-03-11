"use client";

import { useEffect, useState } from "react";

import { apiFetch } from "@/lib/api";
import { useAppState } from "@/lib/app-state";

type AnalysisLayer = {
  level: string;
  goal: string;
  modules: string[];
};

type DeliveryStage = {
  stage: string;
  report_focus: string;
  core_outputs: string;
  management_view: string;
};

type AnalysisFramework = {
  module_layers: AnalysisLayer[];
  delivery_stages: DeliveryStage[];
};

type DimensionAuditRow = {
  category: string;
  data_source_dimension: string;
  page_dimension: string;
  report_dimension: string;
  expected_definition: string;
  page_definition: string;
  is_consistent: boolean;
};

type DimensionAuditPayload = {
  overall_consistent: boolean;
  mismatch_categories: string[];
  rows: DimensionAuditRow[];
};

export default function AnalysisPage() {
  const { token, selectedBrandId, dataVersion } = useAppState();
  const [framework, setFramework] = useState<AnalysisFramework | null>(null);
  const [dimensionAudit, setDimensionAudit] = useState<DimensionAuditPayload | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const [frameworkPayload, dimensionAuditPayload] = await Promise.all([
          apiFetch<AnalysisFramework>("/meta/analysis-framework", {
            token: token ?? undefined
          }),
          selectedBrandId
            ? apiFetch<DimensionAuditPayload>(`/metrics/dimension-audit?brand_id=${selectedBrandId}`, {
                token: token ?? undefined
              })
            : Promise.resolve<DimensionAuditPayload | null>(null)
        ]);
        setFramework(frameworkPayload);
        setDimensionAudit(dimensionAuditPayload);
        setError(null);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "分析模块加载失败");
      }
    };
    void load();
  }, [token, selectedBrandId, dataVersion]);

  return (
    <div className="space-y-5">
      {error ? (
        <div className="panel rounded-3xl px-4 py-3 text-sm text-rose-700">{error}</div>
      ) : null}

      <section className="panel rounded-[2rem] p-5">
        <div className="text-lg font-bold">分析模块路线图</div>
        <div className="mt-1 text-sm text-slate-500">
          以“基础建设 → 增长优化 → 战略治理”分层推进，确保页面分析与周报、月报、季度复盘保持统一口径
        </div>
        <div className="mt-4 grid gap-3 lg:grid-cols-3">
          {(framework?.delivery_stages ?? []).map((item, index) => (
            <article
              key={item.stage}
              className="rounded-3xl border border-slate-200 bg-white/85 px-4 py-3"
            >
              <div className="text-xs font-semibold tracking-[0.16em] text-slate-500">
                阶段 {index + 1}
              </div>
              <div className="mt-1 font-semibold text-slate-800">{item.stage}</div>
              <div className="mt-2 text-sm text-slate-600">{item.report_focus}</div>
            </article>
          ))}
          {!framework ? (
            <div className="rounded-3xl border border-slate-200 bg-white/85 px-4 py-3 text-sm text-slate-500">
              正在加载分析模块配置...
            </div>
          ) : null}
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="panel rounded-[2rem] p-5">
          <div className="text-lg font-bold">分析模块分层（深入浅出）</div>
          <div className="mt-4 space-y-4">
            {(framework?.module_layers ?? []).map((layer) => (
              <article
                key={layer.level}
                className="rounded-3xl border border-slate-200 bg-white/85 px-4 py-4"
              >
                <div className="flex flex-col gap-1 md:flex-row md:items-center md:justify-between">
                  <div className="font-semibold text-slate-900">{layer.level}</div>
                  <div className="text-sm font-semibold text-slate-600">{layer.goal}</div>
                </div>
                <div className="mt-3 grid gap-2 md:grid-cols-2">
                  {layer.modules.map((module) => (
                    <div
                      key={module}
                      className="rounded-2xl border border-slate-100 bg-slate-50 px-3 py-2 text-sm text-slate-700"
                    >
                      {module}
                    </div>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </div>

        <div className="panel rounded-[2rem] p-5">
          <div className="text-lg font-bold">交付检查点</div>
          <div className="mt-4 space-y-3">
            {(framework?.delivery_stages ?? []).map((item) => (
              <article
                key={`check-${item.stage}`}
                className="rounded-3xl border border-slate-200 bg-white/85 px-4 py-3"
              >
                <div className="font-semibold text-slate-900">{item.stage}</div>
                <div className="mt-1 text-sm text-slate-600">核心输出：{item.core_outputs}</div>
                <div className="mt-1 text-sm text-slate-500">管理层视角：{item.management_view}</div>
              </article>
            ))}
            <article className="rounded-3xl border border-slate-200 bg-white/85 px-4 py-3 text-sm text-slate-600">
              指标看板统一口径：提及率、推荐率、情感分布、竞品差距、风险预警清单、跨季度趋势摘要
            </article>
          </div>
        </div>
      </section>

      <section className="panel rounded-[2rem] p-5">
        <div className="mb-1 text-lg font-bold">竞品对比维度一致性审计（数据源/页面/报告）</div>
        <div className="mb-4 text-sm text-slate-500">
          逐项核对“分类名称 + 维度定义”，避免前后口径不一致。
          {dimensionAudit?.overall_consistent
            ? " 当前状态：已对齐。"
            : ` 当前状态：发现 ${dimensionAudit?.mismatch_categories.length ?? 0} 项待修正。`}
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>分类</th>
                <th>数据源维度</th>
                <th>页面维度</th>
                <th>报告维度</th>
                <th>定义一致性</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              {(dimensionAudit?.rows ?? []).map((row) => (
                <tr key={`audit-${row.category}`}>
                  <td className="font-semibold text-slate-800">{row.category}</td>
                  <td>{row.data_source_dimension}</td>
                  <td>{row.page_dimension}</td>
                  <td>{row.report_dimension}</td>
                  <td className="max-w-[320px] text-slate-600">
                    {row.page_definition === row.expected_definition ? "已一致" : "存在差异"}
                  </td>
                  <td className={row.is_consistent ? "text-emerald-700" : "text-rose-700"}>
                    {row.is_consistent ? "通过" : "待修正"}
                  </td>
                </tr>
              ))}
              {dimensionAudit && dimensionAudit.rows.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-slate-500">
                    当前品牌暂无可审计维度数据
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>

      <section className="panel rounded-[2rem] p-5">
        <div className="mb-4 text-lg font-bold">报告交付路径（与周报/月报一致）</div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>适用阶段</th>
                <th>报告聚焦</th>
                <th>核心输出</th>
                <th>管理层视角</th>
              </tr>
            </thead>
            <tbody>
              {(framework?.delivery_stages ?? []).map((item) => (
                <tr key={`stage-${item.stage}`}>
                  <td className="font-semibold text-slate-800">{item.stage}</td>
                  <td>{item.report_focus}</td>
                  <td className="max-w-[320px] text-slate-600">{item.core_outputs}</td>
                  <td className="max-w-[280px] text-slate-600">{item.management_view}</td>
                </tr>
              ))}
              {framework && framework.delivery_stages.length === 0 ? (
                <tr>
                  <td colSpan={4} className="text-slate-500">
                    当前暂无交付阶段配置
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
