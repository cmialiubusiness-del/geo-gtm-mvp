function resolveApiBase() {
  if (typeof window !== "undefined") {
    return `${window.location.protocol}//${window.location.hostname}:8000/api`;
  }
  return process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";
}

type ApiOptions = RequestInit & {
  token?: string | null;
};

export async function apiFetch<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const apiBase = resolveApiBase();
  const headers = new Headers(options.headers ?? {});
  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }
  if (options.token) {
    headers.set("Authorization", `Bearer ${options.token}`);
  }

  let response: Response;
  try {
    response = await fetch(`${apiBase}${path}`, {
      ...options,
      headers,
      cache: "no-store"
    });
  } catch {
    throw new Error(`无法连接 API：${apiBase}`);
  }

  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: "请求失败" }));
    throw new Error(payload.detail ?? "请求失败");
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export async function downloadWithAuth(path: string, token: string, filename: string) {
  const apiBase = resolveApiBase();
  let response: Response;
  try {
    response = await fetch(`${apiBase}${path}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
  } catch {
    throw new Error(`无法连接 API：${apiBase}`);
  }
  if (!response.ok) {
    throw new Error("下载失败");
  }
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  window.URL.revokeObjectURL(url);
}
