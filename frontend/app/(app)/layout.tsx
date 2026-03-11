"use client";

import { AppShell } from "@/components/app-shell";
import { AppStateProvider } from "@/lib/app-state";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <AppStateProvider>
      <AppShell>{children}</AppShell>
    </AppStateProvider>
  );
}
