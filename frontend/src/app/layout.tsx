import type { Metadata } from "next";
import { Montserrat } from "next/font/google";
import "./globals.css";

const montserrat = Montserrat({
  subsets: ["latin"],
  variable: "--font-montserrat",
  weight: ["300", "400", "500", "600", "700", "800"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "TeachMind — Teachable AI Assistant That Learns How You Work",
  description:
    "TeachMind learns user-specific workflows from instructions, demonstrations, and corrections without retraining the underlying LLM.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${montserrat.variable} h-full antialiased dark`}>
      <body className="min-h-full flex flex-col font-sans bg-[#090d16] text-slate-100">
        {children}
      </body>
    </html>
  );
}
