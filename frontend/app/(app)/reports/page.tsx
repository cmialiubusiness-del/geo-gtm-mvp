"use client";

import { useEffect, useMemo, useState } from "react";

import { apiFetch, downloadWithAuth } from "@/lib/api";
import { useAppState } from "@/lib/app-state";

type Report = {
  id: number;
  report_type: string;
  period_start: string;
  period_end: string;
  created_at: string;
};

function reportTypeLabel(reportType: string): string {
  if (reportType === "weekly_brief") {
    return "周报（作战简报）";
  }
  if (reportType === "monthly_strategy") {
    return "月报（战略报告）";
  }
  return reportType;
}

function reportTypeTagClass(reportType: string): string {
  if (reportType === "weekly_brief") {
    return "bg-emerald-50 text-emerald-700 border-emerald-100";
  }
  return "bg-indigo-50 text-indigo-700 border-indigo-100";
}

export default function ReportsPage() {
  const { token, selectedBrandId } = useAppState();
  const [reports, setReports] = useState<Report[]>([]);
  const [weekStart, setWeekStart] = useState(() => {
    const now = new Date();
    return now.toISOString().slice(0, 10);
  });
  const [month, setMonth] = useState(() => new Date().toISOString().slice(0, 7));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadReports = async () => {
    if (!token || !selectedBrandId) {
      setReports([]);
      return;
    }
    try {
      const payload = await apiFetch<Report[]>(`/reports?brand_id=${selectedBrandId}`, { token });
      setReports(payload);
      setError(null);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "加载失败");
    }
  };

  useEffect(() => {
    void loadReports();
  }, [token, selectedBrandId]);

  const reportStats = useMemo(() => {
    const weeklyCount = reports.filter((item) => item.report_type === "weekly_brief").length;
    const monthlyCount = reports.filter((item) => item.report_type === "monthly_strategy").length;
    const latestCreatedAt = reports[0]?.created_at;
    return {
      total: reports.length,
      weeklyCount,
      monthlyCount,
      latestCreatedAt: latestCreatedAt
        ? new Date(latestCreatedAt).toLocaleString("zh-CN")
        : "暂无"
    };
  }, [reports]);

  const generateWeekly = async () => {
    if (!token || !selectedBrandId) {
      return;
    }
    setLoading(true);
    try {
      await apiFetch(`/reports/weekly?brand_id=${selectedBrandId}`, {
        method: "POST",
        token,
        body: JSON.stringify({ week_start: weekStart })
      });
      await loadReports();
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "周报生成失败");
    } finally {
      setLoading(false);
    }
  };

  const generateMonthly = async () => {
    if (!token || !selectedBrandId) {
      return;
    }
    setLoading(true);
    try {
      await apiFetch(`/reports/monthly?brand_id=${selectedBrandId}`, {
        method: "POST",
        token,
        body: JSON.stringify({ month })
      });
      await loadReports();
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "月报生成失败");
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = async (report: Report) => {
    if (!token) {
      return;
    }
    try {
      const fileName = `${report.report_type}_${report.period_start}_${report.period_end}.pdf`;
      await downloadWithAuth(`/reports/${report.id}/download`, token, fileName);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "下载失败");
    }
  };

  return (
    <div className="space-y-5">
      {error ? (
        <div className="panel rounded-3xl px-4 py-3 text-sm text-rose-700">{error}</div>
      ) : null}

      <section className="panel rounded-[2rem] p-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="text-xs font-semibold tracking-[0.16em] text-slate-500">REPORT PLAYBOOK</div>
            <div className="mt-1 text-2xl font-bold text-ink">周报/月报管理层交付中心</div>
            <div className="mt-2 max-w-3xl text-sm text-slate-600">
              统一生成咨询风格报告，突出管理摘要、竞品差距、主题分层、风险清单和行动闭环追踪。
            </div>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-2xl border border-slate-200 bg-white/80 px-4 py-3">
              <div className="text-xs text-slate-500">报告总数</div>
              <div className="mt-1 text-xl font-bold text-slate-900">{reportStats.total}</div>
            </div>
            <div className="rounded-2xl border border-slate-200 bg-white/80 px-4 py-3">
              <div className="text-xs text-slate-500">周报数</div>
              <div className="mt-1 text-xl font-bold text-emerald-700">{reportStats.weeklyCount}</div>
            </div>
            <div className="rounded-2xl border border-slate-200 bg-white/80 px-4 py-3">
              <div className="text-xs text-slate-500">月报数</div>
              <div className="mt-1 text-xl font-bold text-indigo-700">{reportStats.monthlyCount}</div>
            </div>
            <div className="rounded-2xl border border-slate-200 bg-white/80 px-4 py-3">
              <div className="text-xs text-slate-500">最近生成</div>
              <div className="mt-1 text-sm font-semibold text-slate-900">{reportStats.latestCreatedAt}</div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-2">
        <div className="panel rounded-[2rem] p-5">
          <div className="text-lg font-bold">生成周报（作战简报）</div>
          <div className="mt-2 text-sm text-slate-500">
            聚焦当周提及率、推荐率、风险断言、分流主题与优化动作闭环。
          </div>
          <ul className="mt-4 space-y-1 text-sm text-slate-600">
            <li>• 管理摘要与关键指标看板</li>
            <li>• 高风险主题去重与处理优先级</li>
            <li>• 分流拦截动作与下周复测计划</li>
          </ul>
          <input
            className="field mt-4"
            type="date"
            value={weekStart}
            onChange={(event) => setWeekStart(event.target.value)}
          />
          <button className="btn btn-primary mt-4" onClick={generateWeekly} disabled={loading}>
            生成周报
          </button>
        </div>

        <div className="panel rounded-[2rem] p-5">
          <div className="text-lg font-bold">生成月报（战略报告）</div>
          <div className="mt-2 text-sm text-slate-500">
            聚焦平台分布对比、竞品差距拆解、主题词分层和季度策略专题。
          </div>
          <ul className="mt-4 space-y-1 text-sm text-slate-600">
            <li>• 品牌叙事一致性与风险预警清单</li>
            <li>• 跨平台趋势与季度策略专题</li>
            <li>• 管理层决策摘要与资源建议</li>
          </ul>
          <input
            className="field mt-4"
            type="month"
            value={month}
            onChange={(event) => setMonth(event.target.value)}
          />
          <button className="btn btn-primary mt-4" onClick={generateMonthly} disabled={loading}>
            生成月报
          </button>
        </div>
      </section>

      <section className="panel rounded-[2rem] p-5">
        <div className="mb-4 text-lg font-bold">历史报告清单</div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>类型</th>
                <th>周期开始</th>
                <th>周期结束</th>
                <th>结构亮点</th>
                <th>生成时间</th>
                <th>下载</th>
              </tr>
            </thead>
            <tbody>
              {reports.map((report) => (
                <tr key={report.id}>
                  <td>
                    <span
                      className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${reportTypeTagClass(report.report_type)}`}
                    >
                      {reportTypeLabel(report.report_type)}
                    </span>
                  </td>
                  <td>{report.period_start}</td>
                  <td>{report.period_end}</td>
                  <td className="max-w-[280px] text-slate-600">
                    {report.report_type === "weekly_brief"
                      ? "风险主题去重、竞品分流拦截、周度行动闭环"
                      : "平台分布对比、竞品差距拆解、季度战略专题"}
                  </td>
                  <td>{new Date(report.created_at).toLocaleString("zh-CN")}</td>
                  <td>
                    <button className="btn btn-secondary" onClick={() => downloadReport(report)}>
                      下载报告
                    </button>
                  </td>
                </tr>
              ))}
              {!reports.length ? (
                <tr>
                  <td colSpan={6} className="text-slate-500">
                    当前暂无报告，可先生成周报或月报。
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
