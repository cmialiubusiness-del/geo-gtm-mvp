"use client";

import { createContext, useContext, useEffect, useState } from "react";

import { apiFetch } from "@/lib/api";
import { FALLBACK_INDUSTRY_OPTIONS } from "@/lib/industry";
import { normalizeProviderFilter } from "@/lib/providers";

type ProviderFilter = string;
type RangeFilter = "last_run" | "7d" | "30d";
type BrandProject = {
  id: number;
  org_id: number;
  name: string;
  aliases: string[];
  project_context: string;
  created_at: string;
  project_exists?: boolean;
};

type User = {
  id: number;
  org_id: number;
  organization_name: string;
  email: string;
  role: string;
  created_at: string;
};

type AppStateValue = {
  token: string | null;
  user: User | null;
  brands: BrandProject[];
  industryOptions: string[];
  selectedBrandId: number | null;
  dataVersion: number;
  hydrated: boolean;
  provider: ProviderFilter;
  range: RangeFilter;
  setToken: (token: string | null) => void;
  setSelectedBrandId: (brandId: number | null) => void;
  setProvider: (provider: ProviderFilter) => void;
  setRange: (range: RangeFilter) => void;
  logout: () => void;
  refreshUser: () => Promise<void>;
  refreshBrands: () => Promise<void>;
  refreshIndustryOptions: () => Promise<void>;
  refreshData: () => void;
  createBrand: (name: string, aliases: string[], projectContext?: string) => Promise<BrandProject>;
};

const AppStateContext = createContext<AppStateValue | null>(null);

export function AppStateProvider({ children }: { children: React.ReactNode }) {
  const [token, setTokenState] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [brands, setBrands] = useState<BrandProject[]>([]);
  const [industryOptions, setIndustryOptions] = useState<string[]>(FALLBACK_INDUSTRY_OPTIONS);
  const [selectedBrandId, setSelectedBrandIdState] = useState<number | null>(null);
  const [dataVersion, setDataVersion] = useState(0);
  const [hydrated, setHydrated] = useState(false);
  const [provider, setProviderState] = useState<ProviderFilter>("all");
  const [range, setRange] = useState<RangeFilter>("last_run");

  useEffect(() => {
    const storedToken = window.localStorage.getItem("geo-gtm-token");
    if (storedToken) {
      setTokenState(storedToken);
    }
    setHydrated(true);
  }, []);

  const refreshUser = async () => {
    if (!token) {
      setUser(null);
      return;
    }
    try {
      const nextUser = await apiFetch<User>("/auth/me", { token });
      setUser(nextUser);
    } catch {
      setUser(null);
      window.localStorage.removeItem("geo-gtm-token");
      setTokenState(null);
    }
  };

  const refreshBrands = async () => {
    if (!token) {
      setBrands([]);
      setSelectedBrandIdState(null);
      return;
    }
    const items = await apiFetch<BrandProject[]>("/brands", { token });
    setBrands(items);
    const stored = window.localStorage.getItem("geo-gtm-brand-id");
    const storedId = stored ? Number(stored) : null;
    if (storedId && items.some((item) => item.id === storedId)) {
      setSelectedBrandIdState(storedId);
      return;
    }
    const next = items[0]?.id ?? null;
    setSelectedBrandIdState(next);
    if (next) {
      window.localStorage.setItem("geo-gtm-brand-id", String(next));
    }
  };

  const refreshIndustryOptions = async () => {
    try {
      const payload = await apiFetch<{ items: string[] }>("/meta/industries");
      if (payload.items.length) {
        setIndustryOptions(payload.items);
      }
    } catch {
      setIndustryOptions(FALLBACK_INDUSTRY_OPTIONS);
    }
  };

  const createBrand = async (name: string, aliases: string[], projectContext?: string) => {
    if (!token) {
      throw new Error("未登录");
    }
    const brand = await apiFetch<BrandProject>("/brands", {
      method: "POST",
      token,
      body: JSON.stringify({ name, aliases, project_context: projectContext })
    });
    await refreshBrands();
    setSelectedBrandIdState(brand.id);
    window.localStorage.setItem("geo-gtm-brand-id", String(brand.id));
    return brand;
  };

  useEffect(() => {
    void refreshUser();
    void refreshBrands();
  }, [token]);

  useEffect(() => {
    void refreshIndustryOptions();
  }, []);

  const setToken = (nextToken: string | null) => {
    if (nextToken) {
      window.localStorage.setItem("geo-gtm-token", nextToken);
    } else {
      window.localStorage.removeItem("geo-gtm-token");
      window.localStorage.removeItem("geo-gtm-brand-id");
      setUser(null);
      setBrands([]);
      setSelectedBrandIdState(null);
    }
    setTokenState(nextToken);
  };

  const setSelectedBrandId = (brandId: number | null) => {
    setSelectedBrandIdState(brandId);
    if (brandId) {
      window.localStorage.setItem("geo-gtm-brand-id", String(brandId));
    } else {
      window.localStorage.removeItem("geo-gtm-brand-id");
    }
  };

  const logout = () => setToken(null);
  const refreshData = () => setDataVersion((current) => current + 1);
  const setProvider = (nextProvider: ProviderFilter) =>
    setProviderState(normalizeProviderFilter(nextProvider));

  const value: AppStateValue = {
    token,
    user,
    brands,
    industryOptions,
    selectedBrandId,
    dataVersion,
    hydrated,
    provider,
    range,
    setToken,
    setSelectedBrandId,
    setProvider,
    setRange,
    logout,
    refreshUser,
    refreshBrands,
    refreshIndustryOptions,
    refreshData,
    createBrand
  };

  return <AppStateContext.Provider value={value}>{children}</AppStateContext.Provider>;
}

export function useAppState() {
  const context = useContext(AppStateContext);
  if (!context) {
    throw new Error("useAppState must be used inside AppStateProvider");
  }
  return context;
}
