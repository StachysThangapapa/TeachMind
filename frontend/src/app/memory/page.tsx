"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Sidebar } from "@/components/Sidebar";
import { Header } from "@/components/Header";
import { getSkills } from "@/lib/api/skills";
import { CanonicalSkill } from "@/lib/types/skill";
import { MOCK_MEMORY_ITEMS } from "@/lib/api/mockData";

export default function MemoryPage() {
  const [skills, setSkills] = useState<CanonicalSkill[]>([]);

  useEffect(() => {
    getSkills()
      .then((data) => setSkills(data))
      .catch((err) => console.error(err));
  }, []);

  return (
    <div className="flex min-h-screen bg-[#090d16] text-slate-100">
      <Sidebar />

      <main className="flex-1 min-w-0 flex flex-col">
        <Header title="Memory" subtitle="Learned Knowledge Repository" />

        <div className="mx-auto w-full max-w-6xl space-y-10 p-6 md:p-8">
          <div>
            <h2 className="text-2xl font-extrabold tracking-tight text-white">
              Skill Memory
            </h2>
            <p className="mt-1 text-xs text-slate-400">
              Persistent memory store of learned rules, exceptions, and few-shot examples across tasks.
            </p>
          </div>

          {/* SECTION 1: RECENTLY LEARNED */}
          <section className="space-y-4">
            <div className="border-b border-slate-800 pb-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                RECENTLY LEARNED
              </h3>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {MOCK_MEMORY_ITEMS.map((item) => (
                <div
                  key={item.id}
                  className="rounded-2xl border border-slate-800 bg-[#0f172a] p-5 space-y-3"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="text-sm font-bold text-white">{item.skillName}</h4>
                      <span className="text-[11px] text-slate-400">{item.category}</span>
                    </div>
                    <span className="rounded bg-indigo-950/80 border border-indigo-800/50 px-2 py-0.5 font-mono text-[10px] text-indigo-300">
                      {item.version}
                    </span>
                  </div>

                  <div className="rounded-xl bg-slate-900/60 p-3 text-xs space-y-1 text-slate-300">
                    <p className="font-semibold text-slate-400">Learned:</p>
                    <p className="text-slate-200">
                      • {item.rulesCount} rules
                    </p>
                    <p className="text-slate-200">
                      • {item.exceptionsCount} exception
                    </p>
                    <p className="text-slate-200">
                      • {item.examplesCount} examples
                    </p>
                  </div>

                  <div className="flex items-center justify-between pt-1 text-[11px] text-slate-500">
                    <span>Updated: {item.lastUpdated}</span>
                    <Link
                      href={`/skills/${item.skillId}`}
                      className="text-indigo-400 hover:underline font-semibold"
                    >
                      View Skill →
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* SECTION 2: CORRECTIONS */}
          <section className="space-y-4">
            <div className="border-b border-slate-800 pb-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                CORRECTIONS
              </h3>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-[#0f172a] divide-y divide-slate-800/80">
              <div className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white">Refund Processing</span>
                    <span className="rounded bg-amber-950/60 border border-amber-800/40 px-1.5 py-0.2 text-[10px] text-amber-300">
                      v1.0 → v1.1
                    </span>
                  </div>
                  <p className="mt-1 text-slate-400">
                    Correction: &ldquo;Damaged products should always be approved regardless of clearance status.&rdquo;
                  </p>
                </div>
                <span className="text-[11px] text-slate-500 shrink-0">Today</span>
              </div>

              <div className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white">Report Formatting</span>
                    <span className="rounded bg-amber-950/60 border border-amber-800/40 px-1.5 py-0.2 text-[10px] text-amber-300">
                      v0.9 → v1.0
                    </span>
                  </div>
                  <p className="mt-1 text-slate-400">
                    Correction: &ldquo;Round tax percentage columns to 2 decimal places instead of whole numbers.&rdquo;
                  </p>
                </div>
                <span className="text-[11px] text-slate-500 shrink-0">Yesterday</span>
              </div>
            </div>
          </section>

          {/* SECTION 3: SKILL VERSIONS */}
          <section className="space-y-4">
            <div className="border-b border-slate-800 pb-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                SKILL VERSIONS
              </h3>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-[#0f172a] overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="border-b border-slate-800 text-[10px] uppercase tracking-wider text-slate-500 bg-slate-900/60">
                  <tr>
                    <th className="p-3.5">Skill</th>
                    <th className="p-3.5">Version</th>
                    <th className="p-3.5">Status</th>
                    <th className="p-3.5">Confidence</th>
                    <th className="p-3.5">Last Verified</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/80">
                  {skills.map((s) => (
                    <tr key={s.id} className="hover:bg-slate-900/40 transition">
                      <td className="p-3.5 font-bold text-white">{s.displayName || s.name}</td>
                      <td className="p-3.5 font-mono text-indigo-400">{s.version}</td>
                      <td className="p-3.5">
                        <span className="rounded bg-emerald-950/80 border border-emerald-800/40 px-2 py-0.5 text-[10px] font-semibold text-emerald-400">
                          Active
                        </span>
                      </td>
                      <td className="p-3.5 text-emerald-400 font-bold">
                        {Math.round((s.confidence || 0.9) * 100)}%
                      </td>
                      <td className="p-3.5 text-slate-400">{s.lastVerified || "Today"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {/* SECTION 4: EXAMPLES */}
          <section className="space-y-4">
            <div className="border-b border-slate-800 pb-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                EXAMPLES LIBRARY
              </h3>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-2xl border border-slate-800 bg-[#0f172a] p-4 text-xs space-y-2">
                <span className="rounded bg-indigo-950 border border-indigo-800 px-2 py-0.5 text-[10px] font-bold text-indigo-300">
                  Refund Processing
                </span>
                <p className="text-slate-300">
                  <strong>Input:</strong> Product purchased 3 days ago.
                </p>
                <p className="text-emerald-400 font-semibold">
                  <strong>Expected Result:</strong> APPROVE
                </p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-[#0f172a] p-4 text-xs space-y-2">
                <span className="rounded bg-indigo-950 border border-indigo-800 px-2 py-0.5 text-[10px] font-bold text-indigo-300">
                  Refund Processing
                </span>
                <p className="text-slate-300">
                  <strong>Input:</strong> Clearance product purchased 15 days ago.
                </p>
                <p className="text-rose-400 font-semibold">
                  <strong>Expected Result:</strong> REJECT
                </p>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
