"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Icons } from "./Icons";

export const Sidebar: React.FC = () => {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  const navItems = [
    { label: "Assistant", href: "/", icon: Icons.Sparkles },
    { label: "Teach a Skill", href: "/teach", icon: Icons.Plus },
    { label: "My Skills", href: "/skills", icon: Icons.Layers },
    { label: "Verification", href: "/verification", icon: Icons.CheckCircle2 },
    { label: "Memory", href: "/memory", icon: Icons.Cpu },
    { label: "Activity", href: "/activity", icon: Icons.History },
  ];

  const sidebarContent = (
    <div className="flex h-full flex-col justify-between p-4 sm:p-5">
      <div>
        {/* Brand Header */}
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-5">
          <Link href="/" className="group flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-sm shadow-indigo-500/20 transition-transform group-hover:scale-105">
              <Icons.Sparkles className="h-4 w-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-base font-bold tracking-tight text-white">TeachMind</span>
                <span className="rounded bg-indigo-950/80 px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wider text-indigo-300 border border-indigo-800/50">
                  AI
                </span>
              </div>
              <p className="text-[11px] text-slate-400">Workflow Automation</p>
            </div>
          </Link>
          <button
            onClick={() => setMobileOpen(false)}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 md:hidden"
            aria-label="Close menu"
          >
            <Icons.X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="mt-6 space-y-1">
          {navItems.map((item) => {
            const isActive =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(item.href);
            const Icon = item.icon;

            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileOpen(false)}
                className={`group flex items-center gap-3 rounded-xl px-3 py-2.5 text-xs font-semibold transition-all ${
                  isActive
                    ? "bg-slate-800/90 text-white shadow-sm border border-slate-700/80"
                    : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
                }`}
              >
                <Icon
                  className={`h-4 w-4 transition-colors ${
                    isActive ? "text-indigo-400" : "text-slate-500 group-hover:text-slate-300"
                  }`}
                />
                <span>{item.label}</span>
                {isActive && (
                  <span className="ml-auto h-1.5 w-1.5 rounded-full bg-indigo-400" />
                )}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Bottom of Sidebar: Settings & System Status */}
      <div className="space-y-4 pt-4 border-t border-slate-800/80">
        <button
          type="button"
          onClick={() => alert("TeachMind Settings: Connected to local workspace runtime.")}
          className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-xs font-semibold text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 transition"
        >
          <Icons.Sliders className="h-4 w-4 text-slate-500" />
          <span>Settings</span>
        </button>

        {/* Learning Loop Badge */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-3 text-[11px]">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse-subtle" />
            <span className="font-semibold text-slate-200">Core Product Loop</span>
          </div>
          <p className="mt-1 text-[10px] leading-relaxed text-slate-400">
            TEACH → STORE → TEST → VERIFY → CORRECT → UPDATE → REUSE
          </p>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile Top Bar Toggle */}
      <div className="flex items-center justify-between border-b border-slate-800 bg-[#0b0f19] px-4 py-3 md:hidden">
        <Link href="/" className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-white">
            <Icons.Sparkles className="h-4 w-4" />
          </div>
          <span className="text-base font-bold text-white">TeachMind</span>
        </Link>
        <button
          onClick={() => setMobileOpen(true)}
          className="rounded-lg border border-slate-800 p-2 text-slate-400 hover:bg-slate-800"
          aria-label="Open menu"
        >
          <Icons.Menu className="h-5 w-5" />
        </button>
      </div>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 flex md:hidden">
          <div
            className="fixed inset-0 bg-black/70 backdrop-blur-xs"
            onClick={() => setMobileOpen(false)}
          />
          <div className="relative z-10 w-72 max-w-[80vw] bg-[#0b0f19] border-r border-slate-800">
            {sidebarContent}
          </div>
        </div>
      )}

      {/* Desktop Sidebar */}
      <aside className="hidden w-60 shrink-0 border-r border-slate-800/80 bg-[#0b0f19] md:block">
        {sidebarContent}
      </aside>
    </>
  );
};
