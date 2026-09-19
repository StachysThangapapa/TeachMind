"use client";

import React, { useState, useEffect, use } from "react";
import Link from "next/link";
import { Sidebar } from "@/components/Sidebar";
import { Header } from "@/components/Header";
import { Icons } from "@/components/Icons";
import { getSkillById } from "@/lib/api/skills";
import { CanonicalSkill } from "@/lib/types/skill";

export default function SkillDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const resolvedParams = use(params);
  const [skill, setSkill] = useState<CanonicalSkill | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    getSkillById(resolvedParams.id)
      .then((data) => setSkill(data))
      .catch((err) => console.error(err))
      .finally(() => setIsLoading(false));
  }, [resolvedParams.id]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen bg-[#090d16] text-slate-100">
        <Sidebar />
        <main className="flex-1 p-8 text-center text-xs text-slate-500">
          Loading skill details...
        </main>
      </div>
    );
  }

  if (!skill) {
    return (
      <div className="flex min-h-screen bg-[#090d16] text-slate-100">
        <Sidebar />
        <main className="flex-1 p-8 text-center text-xs text-slate-400">
          <p>Skill not found.</p>
          <Link href="/skills" className="mt-4 inline-block text-indigo-400 underline">
            Return to My Skills
          </Link>
        </main>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-[#090d16] text-slate-100">
      <Sidebar />

      <main className="flex-1 min-w-0 flex flex-col">
        <Header
          title={skill.displayName || skill.name}
          subtitle="Skill Detail"
          actionButton={
            <Link
              href="/skills"
              className="inline-flex items-center gap-1.5 rounded-xl border border-slate-800 bg-[#0f172a] px-3.5 py-1.5 text-xs font-semibold text-slate-300 hover:bg-slate-800 transition"
            >
              <Icons.ArrowRight className="h-3.5 w-3.5 rotate-180" />
              <span>Back to Skills</span>
            </Link>
          }
        />

        <div className="mx-auto w-full max-w-4xl space-y-8 p-6 md:p-8">
          {/* Main Skill Header Card */}
          <div className="rounded-3xl border border-slate-800 bg-[#0f172a] p-6 md:p-8 shadow-xl">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-6">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-widest text-indigo-400">
                  CANONICAL SKILL
                </span>
                <h2 className="mt-1 text-2xl md:text-3xl font-extrabold uppercase tracking-tight text-white">
                  {skill.displayName || skill.name}
                </h2>
                <p className="mt-1 text-xs text-slate-400">{skill.description}</p>
              </div>

              <div className="flex items-center gap-4 text-xs">
                <div className="rounded-xl border border-slate-800 bg-slate-900/90 p-3 text-center">
                  <span className="text-slate-400 text-[10px] uppercase font-bold block">Confidence</span>
                  <span className="text-emerald-400 font-bold text-sm">
                    {Math.round((skill.confidence || 0.9) * 100)}%
                  </span>
                </div>
                <div className="rounded-xl border border-slate-800 bg-slate-900/90 p-3 text-center">
                  <span className="text-slate-400 text-[10px] uppercase font-bold block">Version</span>
                  <span className="text-white font-mono font-bold text-sm">{skill.version}</span>
                </div>
                <div className="rounded-xl border border-slate-800 bg-slate-900/90 p-3 text-center">
                  <span className="text-slate-400 text-[10px] uppercase font-bold block">Last Verified</span>
                  <span className="text-slate-200 font-semibold text-xs">{skill.lastVerified || "Today"}</span>
                </div>
              </div>
            </div>

            {/* WHAT I LEARNED SECTION */}
            <div className="mt-8 space-y-8">
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  WHAT I LEARNED
                </h3>
              </div>

              {/* RULES */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-400">
                  RULES
                </h4>
                <div className="space-y-2">
                  {skill.rules.map((rule) => (
                    <div
                      key={rule.id}
                      className="flex items-center gap-2.5 rounded-xl border border-slate-800/80 bg-slate-900/60 p-3 text-xs text-slate-200"
                    >
                      <span className="text-emerald-400 font-bold">✓</span>
                      <span>{rule.rawText || `${rule.condition} → ${rule.action}`}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* EXAMPLES */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-400">
                  EXAMPLES
                </h4>
                <div className="space-y-2">
                  {skill.examples.map((ex) => (
                    <div
                      key={ex.id}
                      className="flex items-center gap-2.5 rounded-xl border border-slate-800/80 bg-slate-900/60 p-3 text-xs text-slate-300"
                    >
                      <span className="text-slate-500 font-bold">•</span>
                      <span>{ex.input}</span>
                      {ex.output && (
                        <span className="ml-auto rounded bg-slate-800 px-2 py-0.5 text-[10px] font-mono text-emerald-400">
                          {ex.output}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* EXCEPTIONS */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-amber-400">
                  EXCEPTIONS
                </h4>
                {skill.exceptions && skill.exceptions.length > 0 ? (
                  <div className="space-y-2">
                    {skill.exceptions.map((exc) => (
                      <div
                        key={exc.id}
                        className="flex items-center gap-2.5 rounded-xl border border-amber-900/40 bg-amber-950/20 p-3 text-xs text-amber-200"
                      >
                        <span className="text-amber-400 font-bold">⚠</span>
                        <span>{exc.rawText || exc.condition}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-500 italic">No exceptions currently registered.</p>
                )}
              </div>
            </div>

            {/* Action Buttons: [ Test Skill ] [ Teach Correction ] */}
            <div className="mt-10 flex items-center gap-3 border-t border-slate-800 pt-6">
              <Link
                href={`/verification?skillId=${skill.id}`}
                className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-xs font-bold text-white shadow-md hover:bg-indigo-500 transition"
              >
                <Icons.Play className="h-4 w-4" />
                <span>Test Skill</span>
              </Link>

              <Link
                href={`/verification?skillId=${skill.id}&correct=true`}
                className="inline-flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-800 px-5 py-2.5 text-xs font-semibold text-slate-200 hover:bg-slate-700 transition"
              >
                <Icons.Sliders className="h-4 w-4 text-amber-400" />
                <span>Teach Correction</span>
              </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
