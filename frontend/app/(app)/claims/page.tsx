"use client";

import { useEffect, useState } from "react";

import { apiFetch } from "@/lib/api";
import { useAppState } from "@/lib/app-state";
import { roundDisplay, 平台文案 } from "@/lib/format";

type Claim = {
  id: number;
  created_at: string;
  provider: string;
  prompt_text: string;
  category: string;
  subject_type: string;
  subject_name: string;
  claim_text: string;
  sentiment: string;
  impact_score: number;
  risk_level: string;
  raw_text: string;
};

type CategoryOption = {
  value: string;
  label: string;
};

type DimensionAuditPayload = {
  rows: Array<{
    category: string;
    data_source_dimension: string;
  }>;
};

const DEFAULT_CATEGORY_OPTIONS: CategoryOption[] = [
  { value: "费用", label: "费用" },
  { value: "专业能力", label: "专业能力" },
  { value: "成功率", label: "成功率" },
  { value: "效率", label: "效率" },
  { value: "合规", label: "合规" },
  { value: "服务体验", label: "服务体验" }
];

function 风险等级文案(level: string): string {
  const mapping: Record<string, string> = {
    Critical: "严重",
    High: "高",
    Medium: "中",
    Low: "低"
  };
  return mapping[level] ?? level;
}

export default function ClaimsPage() {
  const { token, provider, selectedBrandId, dataVersion } = useAppState();
  const [claims, setClaims] = useState<Claim[]>([]);
  const [selectedClaim, setSelectedClaim] = useState<Claim | null>(null);
  const [categoryOptions, setCategoryOptions] = useState<CategoryOption[]>(DEFAULT_CATEGORY_OPTIONS);
  const [filters, setFilters] = useState({
    category: "",
    riskLevel: "",
    subjectType: "",
    search: ""
  });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token || !selectedBrandId) {
      setClaims([]);
      return;
    }
    const params = new URLSearchParams();
    params.set("provider", provider);
    params.set("brand_id", String(selectedBrandId));
    if (filters.category) params.set("category", filters.category);
    if (filters.riskLevel) params.set("risk_level", filters.riskLevel);
    if (filters.subjectType) params.set("subject_type", filters.subjectType);
    if (filters.search) params.set("search", filters.search);

    const load = async () => {
      try {
        const payload = await apiFetch<Claim[]>(`/claims?${params.toString()}`, { token });
        setClaims(payload);
        setError(null);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "加载失败");
      }
    };
    void load();
  }, [token, provider, selectedBrandId, filters, dataVersion]);

  useEffect(() => {
    if (!token || !selectedBrandId) {
      setCategoryOptions(DEFAULT_CATEGORY_OPTIONS);
      return;
    }
    const loadCategories = async () => {
      try {
        const payload = await apiFetch<DimensionAuditPayload>(
          `/metrics/dimension-audit?brand_id=${selectedBrandId}`,
          { token }
        );
        const rows = payload.rows.map((row) => ({
          value: row.category,
          label:
            row.data_source_dimension === row.category
              ? row.category
              : `${row.category}（${row.data_source_dimension}）`
        }));
        setCategoryOptions(rows.length ? rows : DEFAULT_CATEGORY_OPTIONS);
      } catch {
        setCategoryOptions(DEFAULT_CATEGORY_OPTIONS);
      }
    };
    void loadCategories();
  }, [token, selectedBrandId, dataVersion]);

  return (
    <div className="grid gap-5 xl:grid-cols-[1fr_360px]">
      <div className="space-y-5">
        {error ? (
          <div className="panel rounded-3xl px-4 py-3 text-sm text-rose-700">{error}</div>
        ) : null}

        <section className="panel rounded-[2rem] p-5">
          <div className="mb-4 grid gap-3 md:grid-cols-4">
            <select
              className="field"
              value={filters.category}
              onChange={(event) =>
                setFilters((current) => ({ ...current, category: event.target.value }))
              }
            >
              <option value="">全部分类</option>
              {categoryOptions.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
            <select
              className="field"
              value={filters.riskLevel}
              onChange={(event) =>
                setFilters((current) => ({ ...current, riskLevel: event.target.value }))
              }
            >
              <option value="">全部风险等级</option>
              <option value="Critical">严重</option>
              <option value="High">高</option>
              <option value="Medium">中</option>
              <option value="Low">低</option>
            </select>
            <select
              className="field"
              value={filters.subjectType}
              onChange={(event) =>
                setFilters((current) => ({ ...current, subjectType: event.target.value }))
              }
            >
              <option value="">全部主体</option>
              <option value="brand">客户品牌</option>
              <option value="competitor">竞品品牌</option>
            </select>
            <input
              className="field"
              placeholder="关键词搜索"
              value={filters.search}
              onChange={(event) =>
                setFilters((current) => ({ ...current, search: event.target.value }))
              }
            />
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>时间</th>
                  <th>平台</th>
                  <th>问题</th>
                  <th>分类</th>
                  <th>主体</th>
                  <th>断言内容</th>
                  <th>褒贬义</th>
                  <th>影响度</th>
                  <th>风险等级</th>
                </tr>
              </thead>
              <tbody>
                {claims.map((claim) => (
                  <tr
                    key={claim.id}
                    className="cursor-pointer hover:bg-slate-50"
                    onClick={() => setSelectedClaim(claim)}
                  >
                    <td>{new Date(claim.created_at).toLocaleString("zh-CN")}</td>
                    <td>{平台文案(claim.provider)}</td>
                    <td className="max-w-[220px] text-slate-600">{claim.prompt_text}</td>
                    <td>{claim.category}</td>
                    <td>
                      {claim.subject_type === "brand" ? "品牌" : "竞品"} / {claim.subject_name}
                    </td>
                    <td className="max-w-[300px] text-slate-600">{claim.claim_text}</td>
                    <td>{claim.sentiment}</td>
                    <td>{roundDisplay(claim.impact_score)}</td>
                    <td>{风险等级文案(claim.risk_level)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>

      <aside className="panel sticky top-5 h-fit rounded-[2rem] p-5">
        <div className="text-lg font-bold">断言详情</div>
        {selectedClaim ? (
          <div className="mt-4 space-y-4">
            <div>
              <div className="text-xs font-semibold tracking-[0.12em] text-slate-400">
                问题
              </div>
              <div className="mt-2 text-sm leading-7 text-slate-700">{selectedClaim.prompt_text}</div>
            </div>
            <div>
              <div className="text-xs font-semibold tracking-[0.12em] text-slate-400">
                断言
              </div>
              <div className="mt-2 rounded-3xl bg-slate-50 p-4 text-sm leading-7 text-slate-700">
                {selectedClaim.claim_text}
              </div>
            </div>
            <div>
              <div className="text-xs font-semibold tracking-[0.12em] text-slate-400">
                原始回答片段
              </div>
              <div className="mt-2 rounded-3xl bg-slate-50 p-4 text-sm leading-7 text-slate-700">
                {selectedClaim.raw_text}
              </div>
            </div>
          </div>
        ) : (
          <div className="mt-4 rounded-3xl bg-slate-50 p-4 text-sm text-slate-500">
            点击任一行查看详情。
          </div>
        )}
      </aside>
    </div>
  );
}
