import type { Metadata } from "next";
import { Noto_Sans_SC } from "next/font/google";

import "./globals.css";

const noto = Noto_Sans_SC({
  subsets: ["latin"],
  weight: ["400", "500", "700"]
});

export const metadata: Metadata = {
  title: "AI品牌增长决策平台",
  description: "覆盖七大模型的品牌提及、推荐、风险与竞品分流监测，输出可执行优化动作与管理层报告"
};

export default function RootLayout({
  children
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body className={noto.className}>{children}</body>
    </html>
  );
}
