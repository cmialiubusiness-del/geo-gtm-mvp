"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { apiFetch } from "@/lib/api";
import { useAppState } from "@/lib/app-state";
import { CUSTOM_INDUSTRY } from "@/lib/industry";
import {
  ALL_PROVIDERS,
  formatProviderFilterLabel,
  normalizeProviderFilter,
  parseProviderFilter,
  PROVIDER_OPTIONS,
  type ProviderKey
} from "@/lib/providers";

const navItems = [
  { href: "/dashboard", label: "品牌总览" },
  { href: "/capabilities", label: "品牌能力" },
  { href: "/claims", label: "风险断言" },
  { href: "/hijacks", label: "竞品分流" },
  { href: "/analysis", label: "分析模块" },
  { href: "/reports", label: "报告中心" },
  { href: "/settings", label: "设置" }
];

const 页面副标题映射: Record<string, string> = {
  "/projects": "组织级项目组合与资源调度",
  "/dashboard": "品牌总览",
  "/capabilities": "品牌能力",
  "/claims": "风险断言",
  "/hijacks": "竞品分流",
  "/analysis": "分析模块",
  "/reports": "报告中心",
  "/settings": "设置"
};

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const {
    hydrated,
    token,
    user,
    brands,
    industryOptions,
    selectedBrandId,
    setSelectedBrandId,
    provider,
    range,
    setProvider,
    setRange,
    logout,
    createBrand,
    refreshBrands,
    refreshData
  } = useAppState();
  const [running, setRunning] = useState(false);
  const [runMessage, setRunMessage] = useState<string | null>(null);
  const [showCreateProject, setShowCreateProject] = useState(false);
  const [newBrandName, setNewBrandName] = useState("");
  const [newBrandAliases, setNewBrandAliases] = useState("");
  const [newProjectIndustry, setNewProjectIndustry] = useState("通用行业");
  const [newProjectIndustryCustom, setNewProjectIndustryCustom] = useState("");

  const selectedBrand = brands.find((item) => item.id === selectedBrandId) ?? null;
  const 组织中心激活 = pathname === "/projects";
  const selectedProviders = parseProviderFilter(provider);
  const subTitle = 页面副标题映射[pathname] ?? "分析看板";
  const headerTitle = 组织中心激活
    ? "组织运营中心"
    : selectedBrand?.name
      ? `${selectedBrand.name} 品牌作战台`
      : "品牌增长分析中枢";
  const providerLabel = formatProviderFilterLabel(provider);

  useEffect(() => {
    if (industryOptions.length && !industryOptions.includes(newProjectIndustry)) {
      setNewProjectIndustry(industryOptions[0]);
    }
  }, [industryOptions, newProjectIndustry]);

  useEffect(() => {
    if (hydrated && !token) {
      router.replace("/login");
    }
  }, [hydrated, token, router]);

  const createProject = async () => {
    const brandName = newBrandName.trim();
    if (!brandName) {
      setRunMessage("请先输入主品牌名称");
      return;
    }
    const aliases = newBrandAliases
      .split(/[，,]/)
      .map((item) => item.trim())
      .filter(Boolean);
    const projectContext =
      newProjectIndustry === CUSTOM_INDUSTRY
        ? newProjectIndustryCustom.trim()
        : newProjectIndustry;
    if (!projectContext) {
      setRunMessage("请选择业务场景/行业");
      return;
    }
    try {
      const brand = await createBrand(brandName, aliases, projectContext);
      await refreshBrands();
      setRunMessage(brand.project_exists ? `项目已存在，已切换到：${brand.name}` : `已创建品牌项目：${brand.name}`);
      setShowCreateProject(false);
      setNewBrandName("");
      setNewBrandAliases("");
      setNewProjectIndustry("通用行业");
      setNewProjectIndustryCustom("");
    } catch (error) {
      setRunMessage(error instanceof Error ? error.message : "创建项目失败");
    }
  };

  const updateProviderSelection = (target: ProviderKey, checked: boolean) => {
    const nextSelected = checked
      ? [...selectedProviders, target]
      : selectedProviders.filter((item) => item !== target);
    const normalized = normalizeProviderFilter(nextSelected.join(","));
    setProvider(normalized);
  };

  const runNow = async () => {
    if (!token || !selectedBrandId) {
      return;
    }
    setRunning(true);
    setRunMessage(null);
    try {
      const payload = await apiFetch<{ status: string; runs: Array<Record<string, unknown>> }>(
        "/runs/run-now",
        {
          method: "POST",
          token,
          body: JSON.stringify({ provider, brand_id: selectedBrandId })
        }
      );
      setRunMessage(`已触发 ${payload.runs.length} 个采集任务`);
      refreshData();
      window.setTimeout(() => refreshData(), 3000);
      window.setTimeout(() => refreshData(), 7000);
    } catch (error) {
      setRunMessage(error instanceof Error ? error.message : "触发失败");
    } finally {
      setRunning(false);
    }
  };

  if (!hydrated || !token) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="panel rounded-3xl px-8 py-6 text-sm text-slate-600">正在验证登录状态...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-hero-grid">
      <div className="mx-auto flex min-h-screen max-w-[1600px] gap-5 px-4 py-4 lg:px-6">
        <aside className="panel hidden w-72 rounded-[2rem] p-5 lg:flex lg:flex-col">
          <div className="mb-10 rounded-3xl bg-gradient-to-br from-slateDeep to-tide p-5 text-white">
            <div className="text-xl font-bold">AI品牌增长决策平台</div>
            <div className="mt-3 text-sm text-white/80">
              面向管理层与增长团队，统一监测七大AI平台品牌提及、推荐、风险与竞品分流，输出可执行优化闭环
            </div>
          </div>
          <div className="mb-2 px-1 text-xs font-semibold tracking-[0.14em] text-slate-500">
            组织层
          </div>
          <Link
            href="/projects"
            className={`mb-4 block rounded-2xl px-4 py-3 text-sm font-semibold leading-6 transition ${
              组织中心激活
                ? "bg-slateDeep text-white shadow-lg"
                : "bg-white/80 text-slate-700 hover:bg-white"
            }`}
          >
            组织运营中心
          </Link>
          <div className="mb-2 mt-1 px-1 text-xs font-semibold tracking-[0.14em] text-slate-500">
            品牌洞察
          </div>
          <nav className="space-y-2">
            {navItems.map((item) => {
              const active = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`block whitespace-nowrap rounded-2xl px-4 py-3 text-sm font-semibold leading-6 transition ${
                    active
                      ? "bg-slateDeep text-white shadow-lg"
                      : "bg-white/70 text-slate-700 hover:bg-white"
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
          <div className="mt-auto rounded-3xl border border-slate-200 bg-sand px-4 py-4 text-sm text-slate-700">
            <div className="font-semibold">{user?.email}</div>
            <div className="mt-1 text-slate-500">
              当前组织：{user?.organization_name ?? `组织 #${user?.org_id ?? ""}`}
            </div>
          </div>
        </aside>

        <main className="flex-1">
          <header className="panel mb-5 rounded-[2rem] p-4">
            <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
              <div>
                <div className="mt-1 text-2xl font-bold text-ink">
                  {headerTitle}
                </div>
                {subTitle !== headerTitle ? (
                  <div className="mt-1 text-lg font-semibold text-slate-700">{subTitle}</div>
                ) : null}
                <div className="mt-1 text-sm text-slate-500">
                  {user ? `已登录：${user.email}` : "未登录"}
                </div>
              </div>

              <div className="flex flex-col gap-3 md:flex-row md:flex-wrap md:items-center">
                <details className="group relative min-w-[220px]">
                  <summary className="field list-none cursor-pointer text-sm font-semibold text-slate-700">
                    平台：{providerLabel}
                  </summary>
                  <div className="absolute z-20 mt-2 w-[280px] rounded-2xl border border-slate-200 bg-white p-3 shadow-xl">
                    <div className="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-2 text-xs text-slate-600">
                      <span>
                        已选 {selectedProviders.length}/{ALL_PROVIDERS.length}
                      </span>
                      <button
                        className="font-semibold text-slate-700"
                        type="button"
                        onClick={() => setProvider("all")}
                      >
                        全选平台
                      </button>
                    </div>
                    <div className="my-2 border-t border-slate-100" />
                    <div className="space-y-1">
                      {PROVIDER_OPTIONS.map((item) => (
                        <label
                          key={item.value}
                          className="flex items-center gap-2 rounded-xl px-2 py-2 text-sm text-slate-700 hover:bg-slate-50"
                        >
                          <input
                            type="checkbox"
                            checked={selectedProviders.includes(item.value)}
                            onChange={(event) => updateProviderSelection(item.value, event.target.checked)}
                          />
                          {item.label}
                        </label>
                      ))}
                    </div>
                  </div>
                </details>
                <select
                  className="field min-w-[140px]"
                  value={range}
                  onChange={(event) => setRange(event.target.value as typeof range)}
                >
                  <option value="last_run">最近一次</option>
                  <option value="7d">最近7天</option>
                  <option value="30d">最近30天</option>
                </select>
                <button className="btn btn-primary" onClick={runNow} disabled={running}>
                  {running ? "采集中..." : "立即运行"}
                </button>
                <button
                  className="btn btn-secondary"
                  onClick={() => setShowCreateProject((current) => !current)}
                  type="button"
                >
                  {showCreateProject ? "收起创建" : "新建品牌项目"}
                </button>
                <button
                  className="btn btn-secondary"
                  onClick={() => {
                    logout();
                    router.replace("/login");
                  }}
                >
                  退出
                </button>
              </div>
            </div>
            <div className="mt-4 grid gap-3 lg:grid-cols-[minmax(280px,420px)_1fr]">
              <div>
                <div className="text-xs font-semibold tracking-[0.12em] text-slate-500">项目切换</div>
                <select
                  className="field mt-1"
                  value={selectedBrandId ?? ""}
                  onChange={(event) => {
                    const value = event.target.value;
                    setSelectedBrandId(value ? Number(value) : null);
                  }}
                >
                  {brands.map((brand) => (
                    <option key={brand.id} value={brand.id}>
                      {brand.name} | {brand.project_context}
                    </option>
                  ))}
                </select>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">
                {selectedBrand ? (
                  <>
                    <span className="font-semibold text-slate-800">当前项目：</span>
                    {selectedBrand.name}
                    <span className="mx-2 text-slate-400">|</span>
                    <span className="font-semibold text-slate-800">行业：</span>
                    {selectedBrand.project_context}
                    <span className="mx-2 text-slate-400">|</span>
                    <span className="font-semibold text-slate-800">项目数：</span>
                    {brands.length}
                  </>
                ) : (
                  "当前无品牌项目，请先创建"
                )}
              </div>
            </div>
            {runMessage ? (
              <div className="mt-3 rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-600">
                {runMessage}
              </div>
            ) : null}
            {showCreateProject ? (
              <div className="mt-3 grid gap-3 rounded-2xl border border-slate-200 bg-slate-50 p-4 md:grid-cols-[1fr_1fr_220px_1fr_auto]">
                <input
                  className="field"
                  placeholder="主品牌名称，例如：港Y顾问"
                  value={newBrandName}
                  onChange={(event) => setNewBrandName(event.target.value)}
                />
                <input
                  className="field"
                  placeholder="品牌别名（可选，逗号分隔）"
                  value={newBrandAliases}
                  onChange={(event) => setNewBrandAliases(event.target.value)}
                />
                <select
                  className="field"
                  value={newProjectIndustry}
                  onChange={(event) => setNewProjectIndustry(event.target.value)}
                >
                  {industryOptions.map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
                <input
                  className="field"
                  placeholder="自定义行业（仅在选择“其他（自定义）”时填写）"
                  value={newProjectIndustryCustom}
                  onChange={(event) => setNewProjectIndustryCustom(event.target.value)}
                  disabled={newProjectIndustry !== CUSTOM_INDUSTRY}
                />
                <button className="btn btn-primary" type="button" onClick={createProject}>
                  创建项目
                </button>
              </div>
            ) : null}
          </header>

          <div className="space-y-5">{children}</div>
        </main>
      </div>
    </div>
  );
}
