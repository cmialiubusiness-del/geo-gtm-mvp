"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { apiFetch } from "@/lib/api";
import { AppStateProvider, useAppState } from "@/lib/app-state";
import { CUSTOM_INDUSTRY } from "@/lib/industry";

function LoginForm() {
  const router = useRouter();
  const { hydrated, token, setToken, industryOptions } = useAppState();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("demo@example.com");
  const [password, setPassword] = useState("demo1234");
  const [organizationName, setOrganizationName] = useState("新组织");
  const [brandName, setBrandName] = useState("我的主品牌");
  const [brandIndustry, setBrandIndustry] = useState("通用行业");
  const [brandIndustryCustom, setBrandIndustryCustom] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const resolvedIndustry =
        brandIndustry === CUSTOM_INDUSTRY ? brandIndustryCustom.trim() : brandIndustry;
      const path = mode === "login" ? "/auth/login" : "/auth/register";
      const payload =
        mode === "login"
          ? { email, password }
          : {
              email,
              password,
              organization_name: organizationName,
              brand_name: brandName,
              brand_context: resolvedIndustry || "通用行业"
            };
      const result = await apiFetch<{ access_token: string }>(path, {
        method: "POST",
        body: JSON.stringify(payload)
      });
      setToken(result.access_token);
      router.replace("/projects");
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : "登录失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (hydrated && token) {
      router.replace("/projects");
    }
  }, [hydrated, token, router]);

  return (
    <div className="min-h-screen bg-hero-grid px-4 py-8">
      <div className="mx-auto grid max-w-6xl gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <section className="panel rounded-[2rem] bg-gradient-to-br from-slateDeep to-tide p-8 text-white">
          <h1 className="mt-3 max-w-xl text-4xl font-bold leading-tight">
            AI品牌增长决策平台
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-8 text-white/85">
            面向多行业品牌场景，持续监控 DeepSeek、通义千问、豆包、Kimi、腾讯元宝、文心一言、智谱清言回答内容，完成断言级情绪判断、影响度评分、风险分级、竞品分流识别与管理层报告生成
          </p>
          <div className="mt-8 grid gap-4 md:grid-cols-3">
            {[
              ["多模型全景监测", "一次运行即可覆盖七大主流平台并统一口径对比"],
              ["断言级风险引擎", "非关键词粗暴判负，支持 + / 0 / - 与 0-100 影响度"],
              ["管理层决策报告", "自动生成周报、月报并输出季度复盘视角"]
            ].map(([title, body]) => (
              <div key={title} className="rounded-3xl bg-white/10 p-4 backdrop-blur-sm">
                <div className="font-semibold">{title}</div>
                <div className="mt-2 text-sm leading-6 text-white/75">{body}</div>
              </div>
            ))}
          </div>
        </section>

        <section className="panel rounded-[2rem] p-8">
          <div className="mb-6 flex rounded-full bg-slate-100 p-1 text-sm font-semibold">
            <button
              className={`flex-1 rounded-full px-4 py-2 ${mode === "login" ? "bg-white text-slate-900 shadow" : "text-slate-500"}`}
              onClick={() => setMode("login")}
              type="button"
            >
              登录
            </button>
            <button
              className={`flex-1 rounded-full px-4 py-2 ${mode === "register" ? "bg-white text-slate-900 shadow" : "text-slate-500"}`}
              onClick={() => setMode("register")}
              type="button"
            >
              注册
            </button>
          </div>

          <form className="space-y-4" onSubmit={onSubmit}>
            {mode === "register" ? (
              <>
                <label className="block text-sm text-slate-600">
                  组织名称
                  <input
                    className="field mt-2"
                    value={organizationName}
                    onChange={(event) => setOrganizationName(event.target.value)}
                  />
                </label>
                <label className="block text-sm text-slate-600">
                  主品牌名称
                  <input
                    className="field mt-2"
                    value={brandName}
                    onChange={(event) => setBrandName(event.target.value)}
                    placeholder="例如：港Y顾问"
                  />
                </label>
                <label className="block text-sm text-slate-600">
                  业务场景/行业
                  <select
                    className="field mt-2"
                    value={brandIndustry}
                    onChange={(event) => setBrandIndustry(event.target.value)}
                  >
                    {industryOptions.map((item) => (
                      <option key={item} value={item}>
                        {item}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="block text-sm text-slate-600">
                  自定义行业（仅在选择“其他（自定义）”时填写）
                  <input
                    className="field mt-2"
                    value={brandIndustryCustom}
                    onChange={(event) => setBrandIndustryCustom(event.target.value)}
                    disabled={brandIndustry !== CUSTOM_INDUSTRY}
                    placeholder="例如：工业自动化"
                  />
                </label>
              </>
            ) : null}
            <label className="block text-sm text-slate-600">
              邮箱
              <input
                className="field mt-2"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
              />
            </label>
            <label className="block text-sm text-slate-600">
              密码
              <input
                className="field mt-2"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </label>
            {error ? (
              <div className="rounded-2xl bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div>
            ) : null}
            <button className="btn btn-primary w-full" disabled={loading} type="submit">
              {loading ? "处理中..." : mode === "login" ? "登录并进入看板" : "创建组织并进入"}
            </button>
          </form>

          <div className="mt-6 rounded-3xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
            <div className="font-semibold text-slate-900">演示账号</div>
            <div className="mt-2">邮箱：demo@example.com</div>
            <div>密码：demo1234</div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <AppStateProvider>
      <LoginForm />
    </AppStateProvider>
  );
}
