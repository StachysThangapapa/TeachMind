"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Icons } from "./Icons";

interface HeaderProps {
  title: string;
  subtitle?: string;
  actionButton?: React.ReactNode;
}

export const Header: React.FC<HeaderProps> = ({ title, subtitle, actionButton }) => {
  const [profileOpen, setProfileOpen] = useState(false);

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between border-b border-slate-800/80 bg-[#090d16]/90 px-6 py-3.5 backdrop-blur-md md:px-8">
      {/* Left: Current Page Title */}
      <div>
        {subtitle && (
          <p className="text-[10px] font-bold uppercase tracking-wider text-indigo-400">
            {subtitle}
          </p>
        )}
        <h1 className="text-lg font-bold tracking-tight text-white md:text-xl">{title}</h1>
      </div>

      {/* Right: ● Agent Ready, + Teach Skill, User/profile menu */}
      <div className="flex items-center gap-3">
        {/* Agent Ready Status */}
        <div className="flex items-center gap-2 rounded-full border border-emerald-900/50 bg-emerald-950/40 px-3 py-1 text-xs font-semibold text-emerald-400">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse-subtle" />
          <span className="hidden sm:inline">Agent Ready</span>
        </div>

        {/* Action Button or + Teach Skill */}
        {actionButton ? (
          actionButton
        ) : (
          <Link
            href="/teach"
            className="inline-flex items-center gap-1.5 rounded-xl bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 transition"
          >
            <Icons.Plus className="h-3.5 w-3.5" />
            <span>Teach Skill</span>
          </Link>
        )}

        {/* User / Profile Menu */}
        <div className="relative">
          <button
            onClick={() => setProfileOpen(!profileOpen)}
            className="flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900/80 py-1 pl-1.5 pr-2.5 hover:border-slate-700 transition"
            aria-label="User menu"
          >
            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-gradient-to-tr from-indigo-600 to-violet-500 text-[10px] font-bold text-white">
              TM
            </div>
            <span className="hidden text-xs font-medium text-slate-300 sm:inline-block">
              Engineer
            </span>
          </button>

          {profileOpen && (
            <>
              <div
                className="fixed inset-0 z-40"
                onClick={() => setProfileOpen(false)}
              />
              <div className="absolute right-0 top-10 z-50 w-52 rounded-2xl border border-slate-800 bg-[#0f172a] p-3 shadow-xl">
                <div className="border-b border-slate-800 pb-2">
                  <p className="text-xs font-bold text-white">TeachMind Workspace</p>
                  <p className="text-[10px] text-slate-400">Integration Engineer</p>
                </div>
                <div className="mt-2 space-y-1 text-xs text-slate-300">
                  <p className="px-2 py-1 rounded hover:bg-slate-800">Workspace Settings</p>
                  <p className="px-2 py-1 rounded hover:bg-slate-800">API Documentation</p>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
};
