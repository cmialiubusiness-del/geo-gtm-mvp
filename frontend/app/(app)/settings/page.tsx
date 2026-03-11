"use client";

import { FormEvent, useEffect, useState } from "react";

import { apiFetch } from "@/lib/api";
import { useAppState } from "@/lib/app-state";
import { CUSTOM_INDUSTRY } from "@/lib/industry";

type Brand = {
  id: number;
  name: string;
  aliases: string[];
  project_context: string;
};

type Competitor = {
  id: number;
  name: string;
  aliases: string[];
};

type Prompt = {
  id: number;
  text: string;
  category: string;
  intent_type: string;
  is_active: boolean;
};

type CompetitorSuggestion = {
  name: string;
  aliases: string[];
  reason: string;
  industry: string;
};

const PROMPT_CATEGORY_OPTIONS = ["费用", "专业能力", "成功率", "效率", "合规", "服务体验"] as const;
const PROMPT_INTENT_OPTIONS = ["选择", "风险", "费用", "投诉", "对比"] as const;

export default function SettingsPage() {
  const { token, selectedBrandId, industryOptions, refreshData } = useAppState();
  const [brandName, setBrandName] = useState("");
  const [brandAliases, setBrandAliases] = useState("");
  const [projectIndustry, setProjectIndustry] = useState("通用行业");
  const [projectIndustryCustom, setProjectIndustryCustom] = useState("");
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [suggestions, setSuggestions] = useState<CompetitorSuggestion[]>([]);
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [newCompetitorName, setNewCompetitorName] = useState("");
  const [newCompetitorAliases, setNewCompetitorAliases] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchedCandidates, setSearchedCandidates] = useState<CompetitorSuggestion[]>([]);
  const [searching, setSearching] = useState(false);
  const [newPromptText, setNewPromptText] = useState("");
  const [newPromptCategory, setNewPromptCategory] = useState<string>(PROMPT_CATEGORY_OPTIONS[0]);
  const [newPromptIntent, setNewPromptIntent] = useState<string>(PROMPT_INTENT_OPTIONS[0]);
  const [newPromptActive, setNewPromptActive] = useState(true);
  const [submittingPrompt, setSubmittingPrompt] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    if (!token || !selectedBrandId) {
      setBrandName("");
      setBrandAliases("");
      setProjectIndustry("通用行业");
      setProjectIndustryCustom("");
      setCompetitors([]);
      setSuggestions([]);
      setPrompts([]);
      return;
    }
    try {
      const [brand, competitorList, promptList, suggestionPayload] = await Promise.all([
        apiFetch<Brand>(`/brand?brand_id=${selectedBrandId}`, { token }).catch(() => null),
        apiFetch<Competitor[]>(`/competitors?brand_id=${selectedBrandId}`, { token }),
        apiFetch<Prompt[]>(`/prompts?brand_id=${selectedBrandId}`, { token }),
        apiFetch<{ items: CompetitorSuggestion[] }>(
          `/competitors/suggestions?brand_id=${selectedBrandId}`,
          { token }
        )
      ]);
      setBrandName(brand?.name ?? "");
      setBrandAliases((brand?.aliases ?? []).join("，"));
      const context = brand?.project_context ?? "通用行业";
      if (industryOptions.includes(context)) {
        setProjectIndustry(context);
        setProjectIndustryCustom("");
      } else {
        setProjectIndustry(CUSTOM_INDUSTRY);
        setProjectIndustryCustom(context);
      }
      setCompetitors(competitorList);
      setSuggestions(suggestionPayload.items);
      setSearchedCandidates([]);
      setPrompts(promptList);
      setError(null);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "加载失败");
    }
  };

  useEffect(() => {
    void load();
  }, [token, selectedBrandId, industryOptions]);

  const saveBrand = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!token || !selectedBrandId) {
      return;
    }
    const projectContext =
      projectIndustry === CUSTOM_INDUSTRY ? projectIndustryCustom.trim() : projectIndustry;
    if (!projectContext) {
      setError("请选择业务场景/行业");
      return;
    }
    try {
      await apiFetch(`/brand?brand_id=${selectedBrandId}`, {
        method: "PUT",
        token,
        body: JSON.stringify({
          name: brandName,
          project_context: projectContext,
          aliases: brandAliases
            .split(/[，,]/)
            .map((item) => item.trim())
            .filter(Boolean)
        })
      });
      setMessage("品牌配置已更新");
      await load();
      refreshData();
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "保存失败");
    }
  };

  const addCompetitor = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!token || !selectedBrandId) {
      return;
    }
    try {
      await apiFetch(`/competitors?brand_id=${selectedBrandId}`, {
        method: "POST",
        token,
        body: JSON.stringify({
          name: newCompetitorName,
          aliases: newCompetitorAliases
            .split(/[，,]/)
            .map((item) => item.trim())
            .filter(Boolean)
        })
      });
      setNewCompetitorName("");
      setNewCompetitorAliases("");
      setMessage("竞品已添加");
      await load();
      refreshData();
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "新增失败");
    }
  };

  const addSuggestedCompetitor = async (suggestion: CompetitorSuggestion) => {
    if (!token || !selectedBrandId) {
      return;
    }
    try {
      await apiFetch(`/competitors?brand_id=${selectedBrandId}`, {
        method: "POST",
        token,
        body: JSON.stringify({
          name: suggestion.name,
          aliases: suggestion.aliases
        })
      });
      setMessage(`已添加建议竞品：${suggestion.name}`);
      await load();
      refreshData();
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "添加建议竞品失败");
    }
  };

  const searchCompetitorCandidates = async () => {
    if (!token || !selectedBrandId) {
      return;
    }
    if (!searchQuery.trim()) {
      setSearchedCandidates([]);
      return;
    }
    setSearching(true);
    try {
      const payload = await apiFetch<{ items: CompetitorSuggestion[] }>(
        `/competitors/search?brand_id=${selectedBrandId}&q=${encodeURIComponent(searchQuery)}&limit=10`,
        { token }
      );
      setSearchedCandidates(payload.items);
      setError(null);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "搜索失败");
    } finally {
      setSearching(false);
    }
  };

  const deleteCompetitor = async (id: number) => {
    if (!token || !selectedBrandId) {
      return;
    }
    try {
      await apiFetch(`/competitors/${id}?brand_id=${selectedBrandId}`, { method: "DELETE", token });
      setMessage("竞品已删除");
      await load();
      refreshData();
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "删除失败");
    }
  };

  const addPrompt = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!token || !selectedBrandId) {
      return;
    }
    if (!newPromptText.trim()) {
      setError("请先输入问题内容");
      return;
    }
    setSubmittingPrompt(true);
    try {
      await apiFetch(`/prompts?brand_id=${selectedBrandId}`, {
        method: "POST",
        token,
        body: JSON.stringify({
          text: newPromptText.trim(),
          category: newPromptCategory,
          intent_type: newPromptIntent,
          is_active: newPromptActive
        })
      });
      setNewPromptText("");
      setNewPromptCategory(PROMPT_CATEGORY_OPTIONS[0]);
      setNewPromptIntent(PROMPT_INTENT_OPTIONS[0]);
      setNewPromptActive(true);
      setMessage("问题已添加到问题库");
      await load();
      refreshData();
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "添加问题失败");
    } finally {
      setSubmittingPrompt(false);
    }
  };

  return (
    <div className="space-y-5">
      {message ? (
        <div className="panel rounded-3xl px-4 py-3 text-sm text-emerald-700">{message}</div>
      ) : null}
      {error ? (
        <div className="panel rounded-3xl px-4 py-3 text-sm text-rose-700">{error}</div>
      ) : null}

      <section className="grid gap-5 xl:grid-cols-2">
        <form className="panel rounded-[2rem] p-5" onSubmit={saveBrand}>
          <div className="text-lg font-bold">品牌配置</div>
          <label className="mt-4 block text-sm text-slate-600">
            品牌名称
            <input
              className="field mt-2"
              value={brandName}
              onChange={(event) => setBrandName(event.target.value)}
            />
          </label>
          <label className="mt-4 block text-sm text-slate-600">
            别名（用逗号分隔）
            <input
              className="field mt-2"
              value={brandAliases}
              onChange={(event) => setBrandAliases(event.target.value)}
            />
          </label>
          <label className="mt-4 block text-sm text-slate-600">
            业务场景/行业
            <select
              className="field mt-2"
              value={projectIndustry}
              onChange={(event) => setProjectIndustry(event.target.value)}
            >
              {industryOptions.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
          <label className="mt-4 block text-sm text-slate-600">
            自定义行业（仅在选择“其他（自定义）”时填写）
            <input
              className="field mt-2"
              value={projectIndustryCustom}
              onChange={(event) => setProjectIndustryCustom(event.target.value)}
              disabled={projectIndustry !== CUSTOM_INDUSTRY}
              placeholder="例如：工业自动化"
            />
          </label>
          <button className="btn btn-primary mt-4" type="submit">
            保存品牌
          </button>
        </form>

        <form className="panel rounded-[2rem] p-5" onSubmit={addCompetitor}>
          <div className="text-lg font-bold">竞品配置（建议 3-8 个）</div>
          <label className="mt-4 block text-sm text-slate-600">
            竞品名称
            <input
              className="field mt-2"
              value={newCompetitorName}
              onChange={(event) => setNewCompetitorName(event.target.value)}
            />
          </label>
          <label className="mt-4 block text-sm text-slate-600">
            别名（用逗号分隔）
            <input
              className="field mt-2"
              value={newCompetitorAliases}
              onChange={(event) => setNewCompetitorAliases(event.target.value)}
            />
          </label>
          <button className="btn btn-primary mt-4" type="submit">
            新增竞品
          </button>

          <div className="mt-5">
            <div className="mb-2 text-sm font-semibold text-slate-700">系统推荐竞品（按行业）</div>
            <div className="space-y-2">
              {suggestions.map((suggestion) => (
                <div
                  key={suggestion.name}
                  className="rounded-2xl border border-slate-200 bg-white/80 px-3 py-2"
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="text-sm font-semibold text-slate-800">{suggestion.name}</div>
                    <button
                      className="btn btn-secondary"
                      type="button"
                      onClick={() => addSuggestedCompetitor(suggestion)}
                    >
                      添加
                    </button>
                  </div>
                  <div className="mt-1 text-xs text-slate-500">{suggestion.reason}</div>
                </div>
              ))}
              {!suggestions.length ? (
                <div className="rounded-2xl border border-slate-200 bg-white/80 px-3 py-2 text-xs text-slate-500">
                  当前暂无可补充的推荐竞品。
                </div>
              ) : null}
            </div>
          </div>

          <div className="mt-5">
            <div className="mb-2 text-sm font-semibold text-slate-700">竞品搜索（按品牌/行业关键词）</div>
            <div className="flex flex-col gap-2 md:flex-row">
              <input
                className="field"
                placeholder="输入关键词，例如：CRM / 新能源 / 医疗影像"
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
              />
              <button
                className="btn btn-secondary"
                type="button"
                onClick={searchCompetitorCandidates}
                disabled={searching}
              >
                {searching ? "搜索中..." : "搜索竞品"}
              </button>
            </div>
            <div className="mt-2 space-y-2">
              {searchedCandidates.map((suggestion) => (
                <div
                  key={`search-${suggestion.name}`}
                  className="rounded-2xl border border-slate-200 bg-white/80 px-3 py-2"
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="text-sm font-semibold text-slate-800">{suggestion.name}</div>
                    <button
                      className="btn btn-secondary"
                      type="button"
                      onClick={() => addSuggestedCompetitor(suggestion)}
                    >
                      添加
                    </button>
                  </div>
                  <div className="mt-1 text-xs text-slate-500">{suggestion.reason}</div>
                </div>
              ))}
              {searchQuery.trim() && !searchedCandidates.length && !searching ? (
                <div className="rounded-2xl border border-slate-200 bg-white/80 px-3 py-2 text-xs text-slate-500">
                  没有匹配到可新增竞品，请换关键词或手动新增。
                </div>
              ) : null}
            </div>
          </div>

          <div className="mt-5 space-y-3">
            {competitors.map((competitor) => (
              <div
                key={competitor.id}
                className="flex items-center justify-between rounded-3xl border border-slate-200 bg-white/80 px-4 py-3"
              >
                <div>
                  <div className="font-semibold text-slate-800">{competitor.name}</div>
                  <div className="text-sm text-slate-500">{competitor.aliases.join("，") || "无别名"}</div>
                </div>
                <button
                  className="btn btn-secondary"
                  type="button"
                  onClick={() => deleteCompetitor(competitor.id)}
                >
                  删除
                </button>
              </div>
            ))}
          </div>
        </form>
      </section>

      <section className="panel rounded-[2rem] p-5">
        <div className="mb-4 text-lg font-bold">问题库（50条）</div>
        <form
          className="mb-5 rounded-3xl border border-slate-200 bg-slate-50 px-4 py-4"
          onSubmit={addPrompt}
        >
          <div className="text-sm font-semibold text-slate-800">手动添加问题</div>
          <div className="mt-3 grid gap-3 lg:grid-cols-[1.8fr_0.7fr_0.7fr_0.6fr_auto]">
            <input
              className="field"
              placeholder="输入要加入问题库的问题文本"
              value={newPromptText}
              onChange={(event) => setNewPromptText(event.target.value)}
            />
            <select
              className="field"
              value={newPromptCategory}
              onChange={(event) => setNewPromptCategory(event.target.value)}
            >
              {PROMPT_CATEGORY_OPTIONS.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
            <select
              className="field"
              value={newPromptIntent}
              onChange={(event) => setNewPromptIntent(event.target.value)}
            >
              {PROMPT_INTENT_OPTIONS.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
            <label className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-600">
              <input
                type="checkbox"
                checked={newPromptActive}
                onChange={(event) => setNewPromptActive(event.target.checked)}
              />
              启用
            </label>
            <button className="btn btn-primary" type="submit" disabled={submittingPrompt}>
              {submittingPrompt ? "添加中..." : "添加问题"}
            </button>
          </div>
        </form>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>编号</th>
                <th>问题</th>
                <th>分类</th>
                <th>意图类型</th>
                <th>启用</th>
              </tr>
            </thead>
            <tbody>
              {prompts.map((prompt) => (
                <tr key={prompt.id}>
                  <td>{prompt.id}</td>
                  <td className="max-w-[520px] text-slate-600">{prompt.text}</td>
                  <td>{prompt.category}</td>
                  <td>{prompt.intent_type}</td>
                  <td>{prompt.is_active ? "是" : "否"}</td>
                </tr>
              ))}
              {!prompts.length ? (
                <tr>
                  <td colSpan={5} className="text-slate-500">
                    当前问题库为空，请先手动添加问题
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
