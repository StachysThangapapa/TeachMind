"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Sidebar } from "@/components/Sidebar";
import { Header } from "@/components/Header";
import { ActivityEvent, ActivityEventType } from "@/lib/types/activity";

const ALL_ACTIVITIES: ActivityEvent[] = [
  {
    id: "act-1",
    type: "skill_learned",
    skillId: "skill_001",
    skillName: "Refund Processing",
    description: "Taught new workflow via Describe with 4 procedural rules and 2 examples.",
    timestamp: "2 minutes ago"
  },
  {
    id: "act-2",
    type: "correction_added",
    skillId: "skill_001",
    skillName: "Refund Processing",
    description: "Correction added: 'Damaged products override the standard clearance restriction.'",
    timestamp: "4 minutes ago"
  },
  {
    id: "act-3",
    type: "version_updated",
    skillId: "skill_001",
    skillName: "Refund Processing",
    description: "Skill version bumped from v1.0 to v1.1 following exception registration.",
    timestamp: "4 minutes ago"
  },
  {
    id: "act-4",
    type: "skill_verified",
    skillId: "skill_001",
    skillName: "Refund Processing",
    description: "Verification completed with 5/5 test cases passed (100% accuracy).",
    timestamp: "12 minutes ago"
  },
  {
    id: "act-5",
    type: "skill_reused",
    skillId: "skill_001",
    skillName: "Refund Processing",
    description: "Autonomous execution completed for customer task (Decision: APPROVE).",
    timestamp: "28 minutes ago"
  },
  {
    id: "act-6",
    type: "skill_learned",
    skillId: "skill_002",
    skillName: "Report Formatting",
    description: "Learned markdown digest generation from monthly CSV pipeline.",
    timestamp: "Yesterday"
  },
  {
    id: "act-7",
    type: "skill_verified",
    skillId: "skill_003",
    skillName: "Email Workflow",
    description: "Verification test suite verified 10 incoming priority lead triage rules.",
    timestamp: "2 days ago"
  }
];

export default function ActivityPage() {
  const [selectedType, setSelectedType] = useState<ActivityEventType | "all">("all");

  const filtered = ALL_ACTIVITIES.filter((a) => {
    if (selectedType === "all") return true;
    return a.type === selectedType;
  });

  const getEventBadge = (type: ActivityEventType) => {
    switch (type) {
      case "skill_learned":
        return { label: "Skill Learned", color: "bg-indigo-950/80 text-indigo-300 border-indigo-800/50" };
      case "skill_verified":
        return { label: "Skill Verified", color: "bg-emerald-950/80 text-emerald-300 border-emerald-800/50" };
      case "correction_added":
        return { label: "Correction Added", color: "bg-amber-950/80 text-amber-300 border-amber-800/50" };
      case "skill_reused":
        return { label: "Skill Reused", color: "bg-purple-950/80 text-purple-300 border-purple-800/50" };
      case "version_updated":
        return { label: "Version Updated", color: "bg-blue-950/80 text-blue-300 border-blue-800/50" };
      default:
        return { label: "Event", color: "bg-slate-800 text-slate-300 border-slate-700" };
    }
  };

  return (
    <div className="flex min-h-screen bg-[#090d16] text-slate-100">
      <Sidebar />

      <main className="flex-1 min-w-0 flex flex-col">
        <Header title="Activity" subtitle="Audit Trail" />

        <div className="mx-auto w-full max-w-4xl space-y-8 p-6 md:p-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h2 className="text-2xl font-extrabold tracking-tight text-white">
                Activity Stream
              </h2>
              <p className="mt-1 text-xs text-slate-400">
                Chronological record of skill learning, verification, corrections, and autonomous reuses.
              </p>
            </div>

            {/* Filter Pills */}
            <div className="flex items-center gap-1.5 overflow-x-auto">
              {(
                [
                  ["all", "All"],
                  ["skill_learned", "Learned"],
                  ["skill_verified", "Verified"],
                  ["correction_added", "Corrected"],
                  ["skill_reused", "Reused"],
                  ["version_updated", "Updated"],
                ] as const
              ).map(([val, label]) => (
                <button
                  key={val}
                  onClick={() => setSelectedType(val)}
                  className={`rounded-xl px-3 py-1.5 text-xs font-semibold transition ${
                    selectedType === val
                      ? "bg-indigo-600 text-white"
                      : "bg-slate-900 border border-slate-800 text-slate-400 hover:text-white"
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Chronological Timeline */}
          <div className="rounded-3xl border border-slate-800 bg-[#0f172a] p-6 shadow-xl space-y-6">
            <div className="space-y-6">
              {filtered.map((item, idx) => {
                const badge = getEventBadge(item.type);
                return (
                  <div key={item.id} className="relative flex items-start gap-4">
                    {/* Timeline Line */}
                    {idx < filtered.length - 1 && (
                      <span className="absolute left-2.5 top-6 bottom-0 w-0.5 bg-slate-800" />
                    )}

                    {/* Dot */}
                    <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-indigo-400 ring-4 ring-slate-900" />

                    <div className="flex-1 rounded-2xl border border-slate-800/80 bg-slate-900/60 p-4 text-xs">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 border-b border-slate-800/60 pb-2">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-bold text-white text-sm">
                            {item.skillName}
                          </span>
                          <span
                            className={`rounded-md border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider ${badge.color}`}
                          >
                            ● {badge.label}
                          </span>
                        </div>
                        <span className="text-[11px] text-slate-500 font-mono">
                          {item.timestamp}
                        </span>
                      </div>

                      <p className="mt-2 text-slate-300 leading-relaxed">
                        {item.description}
                      </p>

                      {item.skillId && (
                        <div className="mt-3 pt-2 border-t border-slate-800/40">
                          <Link
                            href={`/skills/${item.skillId}`}
                            className="text-[11px] text-indigo-400 hover:underline font-semibold"
                          >
                            Inspect Skill →
                          </Link>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
