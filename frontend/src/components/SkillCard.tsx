"use client";

import React from "react";
import Link from "next/link";
import { CanonicalSkill } from "@/lib/types/skill";
import { Icons } from "./Icons";

interface SkillCardProps {
  skill: CanonicalSkill;
}

export const SkillCard: React.FC<SkillCardProps> = ({ skill }) => {
  const confidencePercent = Math.round((skill.confidence || 0.9) * 100);

  return (
    <Link
      href={`/skills/${skill.id}`}
      className="group flex flex-col justify-between rounded-2xl border border-slate-800 bg-[#0f172a] p-5 transition-all duration-200 hover:-translate-y-0.5 hover:border-slate-700 hover:shadow-lg hover:shadow-indigo-500/5"
    >
      <div>
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="rounded-md border border-indigo-900/60 bg-indigo-950/40 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-indigo-400">
              {skill.category}
            </span>
            <span className="rounded-md border border-slate-800 bg-slate-900/80 px-1.5 py-0.5 text-[10px] font-mono text-slate-400">
              {skill.version || "v1.0"}
            </span>
          </div>

          <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-400">
            <Icons.Zap className="h-3.5 w-3.5" />
            <span>{confidencePercent}%</span>
          </div>
        </div>

        <h3 className="mt-3 text-base font-bold text-white group-hover:text-indigo-400 transition-colors line-clamp-1">
          {skill.displayName || skill.name}
        </h3>

        <p className="mt-1.5 text-xs leading-relaxed text-slate-400 line-clamp-2">
          {skill.description}
        </p>

        {/* Rules & Exceptions counts */}
        <div className="mt-4 flex items-center gap-3 text-xs text-slate-400">
          <div className="flex items-center gap-1">
            <Icons.Check className="h-3.5 w-3.5 text-slate-500" />
            <span>{skill.rules?.length || 0} rules</span>
          </div>
          {skill.exceptions && skill.exceptions.length > 0 && (
            <div className="flex items-center gap-1 text-amber-400/90">
              <Icons.AlertTriangle className="h-3.5 w-3.5" />
              <span>{skill.exceptions.length} exception</span>
            </div>
          )}
        </div>
      </div>

      {/* Footer Info */}
      <div className="mt-5 flex items-center justify-between border-t border-slate-800/80 pt-3 text-[11px] text-slate-500">
        <span>Verified: {skill.lastVerified || "Today"}</span>
        <span className="flex items-center gap-1 text-indigo-400 group-hover:translate-x-0.5 transition-transform font-semibold">
          View details
          <Icons.ArrowRight className="h-3 w-3" />
        </span>
      </div>
    </Link>
  );
};
