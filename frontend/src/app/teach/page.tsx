"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Sidebar } from "@/components/Sidebar";
import { Header } from "@/components/Header";
import { Icons } from "@/components/Icons";
import { teachSkill, saveSkill } from "@/lib/api/skills";
import { CanonicalSkill } from "@/lib/types/skill";

export default function TeachSkillPage() {
  const router = useRouter();
  const [tab, setTab] = useState<"describe" | "demonstrate">("describe");

  // Describe state
  const [describeInput, setDescribeInput] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [detectedSkill, setDetectedSkill] = useState<CanonicalSkill | null>(null);
  const [rulesCount, setRulesCount] = useState(0);
  const [examplesCount, setExamplesCount] = useState(0);
  const [isSaved, setIsSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  // Demonstrate state
  const [demoInput, setDemoInput] = useState("");
  const [demoSubmitting, setDemoSubmitting] = useState(false);
  const [demoResultSkill, setDemoResultSkill] = useState<CanonicalSkill | null>(null);

  const exampleDescribeText =
    "When a customer requests a refund, check whether the purchase was within 7 days. Clearance products are normally rejected, except when the product is damaged.";

  const handleTeachDescribe = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!describeInput.trim() || isSubmitting) return;

    setIsSubmitting(true);
    setError(null);
    setIsSaved(false);

    try {
      const response = await teachSkill({
        method: "describe",
        input: describeInput.trim()
      });

      setDetectedSkill(response.skill);
      setRulesCount(response.detected_rules_count);
      setExamplesCount(response.captured_examples_count);
    } catch (err: unknown) {
      setError((err as Error)?.message || "Failed to analyze skill with backend.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleTeachDemonstrate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!demoInput.trim() || demoSubmitting) return;

    setDemoSubmitting(true);
    setError(null);

    try {
      const response = await teachSkill({
        method: "demonstrate",
        input: demoInput.trim(),
        name: "Demonstrated Workflow"
      });
      setDemoResultSkill(response.skill);
    } catch (err: unknown) {
      setError((err as Error)?.message || "Demonstration extraction failed.");
    } finally {
      setDemoSubmitting(false);
    }
  };

  const handleSaveSkill = async () => {
    if (!detectedSkill) return;
    try {
      await saveSkill(detectedSkill);
      setIsSaved(true);
    } catch (err: unknown) {
      setError((err as Error)?.message || "Could not save skill to backend.");
    }
  };

  return (
    <div className="flex min-h-screen bg-[#090d16] text-slate-100">
      <Sidebar />

      <main className="flex-1 min-w-0 flex flex-col">
        <Header title="Teach a Skill" subtitle="Skill Acquisition" />

        <div className="mx-auto w-full max-w-4xl space-y-8 p-6 md:p-8">
          {/* Header & Subtitle */}
          <div>
            <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white">
              Teach TeachMind a New Skill
            </h2>
            <p className="mt-1 text-sm text-slate-400">
              Show it how you work. TeachMind will remember it and reuse it.
            </p>
          </div>

          {/* Mode Tabs: [ Describe ] [ Demonstrate ] */}
          <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
            <button
              onClick={() => setTab("describe")}
              className={`rounded-xl px-4 py-2 text-xs font-bold transition ${
                tab === "describe"
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "bg-slate-900 text-slate-400 hover:text-white"
              }`}
            >
              [ Describe ]
            </button>
            <button
              onClick={() => setTab("demonstrate")}
              className={`rounded-xl px-4 py-2 text-xs font-bold transition ${
                tab === "demonstrate"
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "bg-slate-900 text-slate-400 hover:text-white"
              }`}
            >
              [ Demonstrate ]
            </button>
          </div>

          {error && (
            <div className="rounded-xl border border-rose-900/50 bg-rose-950/40 p-3.5 text-xs text-rose-300">
              {error}
            </div>
          )}

          {/* TAB 1: DESCRIBE */}
          {tab === "describe" && (
            <div className="space-y-6">
              <div className="rounded-3xl border border-slate-800 bg-[#0f172a] p-6 shadow-xl space-y-4">
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400">
                  Tell TeachMind what you want it to learn...
                </label>

                <textarea
                  value={describeInput}
                  onChange={(e) => setDescribeInput(e.target.value)}
                  rows={5}
                  placeholder={`Example: "${exampleDescribeText}"`}
                  className="w-full rounded-2xl border border-slate-700 bg-slate-900/90 p-4 text-xs text-white placeholder-slate-500 outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition leading-relaxed"
                />

                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                  <button
                    type="button"
                    onClick={() => setDescribeInput(exampleDescribeText)}
                    className="text-[11px] text-indigo-400 hover:underline"
                  >
                    Insert example refund policy
                  </button>

                  <button
                    type="button"
                    onClick={handleTeachDescribe}
                    disabled={isSubmitting || !describeInput.trim()}
                    className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-6 py-2.5 text-xs font-bold text-white shadow-md hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition"
                  >
                    {isSubmitting ? (
                      <>
                        <Icons.RotateCcw className="h-4 w-4 animate-spin" />
                        <span>Analyzing Skill...</span>
                      </>
                    ) : (
                      <span>Teach Skill</span>
                    )}
                  </button>
                </div>
              </div>

              {/* SKILL DETECTED CARD */}
              {detectedSkill && (
                <div className="rounded-3xl border border-indigo-900/60 bg-[#0f172a] p-6 shadow-xl space-y-5">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                    <div>
                      <span className="text-[10px] font-bold uppercase tracking-widest text-indigo-400">
                        SKILL DETECTED
                      </span>
                      <h3 className="mt-1 text-xl font-bold text-white">
                        {detectedSkill.displayName || detectedSkill.name}
                      </h3>
                    </div>
                    <span className="rounded bg-indigo-950/80 border border-indigo-800/60 px-2.5 py-1 text-xs font-mono text-indigo-300">
                      {detectedSkill.version}
                    </span>
                  </div>

                  <div>
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                      Rules:
                    </p>
                    <div className="mt-3 space-y-2">
                      {detectedSkill.rules.map((rule) => (
                        <div key={rule.id} className="flex items-center gap-2 text-xs text-slate-200">
                          <span className="text-emerald-400 font-bold">✓</span>
                          <span>{rule.rawText || `${rule.condition} → ${rule.action}`}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center gap-4 text-xs text-slate-400 border-t border-slate-800/80 pt-4">
                    <span>
                      <strong className="text-white">{rulesCount}</strong> rules learned
                    </span>
                    <span>•</span>
                    <span>
                      <strong className="text-white">{examplesCount}</strong> examples captured
                    </span>
                  </div>

                  {isEditing && (
                    <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-4 text-xs space-y-2">
                      <p className="font-semibold text-slate-300">Edit Skill Title:</p>
                      <input
                        type="text"
                        value={detectedSkill.displayName}
                        onChange={(e) =>
                          setDetectedSkill({ ...detectedSkill, displayName: e.target.value })
                        }
                        className="w-full rounded-lg border border-slate-700 bg-slate-950 p-2 text-xs text-white"
                      />
                    </div>
                  )}

                  {isSaved ? (
                    <div className="rounded-2xl border border-emerald-900/60 bg-emerald-950/40 p-4 flex flex-col sm:flex-row items-center justify-between gap-3">
                      <div className="flex items-center gap-2 text-xs font-semibold text-emerald-300">
                        <Icons.Check className="h-4 w-4 text-emerald-400" />
                        <span>Skill saved to memory successfully!</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Link
                          href={`/verification?skillId=${detectedSkill.id}`}
                          className="rounded-xl bg-emerald-600 px-4 py-2 text-xs font-bold text-white hover:bg-emerald-500 transition"
                        >
                          Run Verification →
                        </Link>
                        <button
                          onClick={() => router.push("/skills")}
                          className="rounded-xl border border-slate-700 px-3 py-2 text-xs text-slate-300 hover:bg-slate-800"
                        >
                          View in Skills
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center gap-3 pt-2">
                      <button
                        type="button"
                        onClick={handleSaveSkill}
                        className="rounded-xl bg-indigo-600 px-5 py-2.5 text-xs font-bold text-white shadow-md hover:bg-indigo-500 transition"
                      >
                        Save Skill
                      </button>
                      <button
                        type="button"
                        onClick={() => setIsEditing(!isEditing)}
                        className="rounded-xl border border-slate-700 px-4 py-2.5 text-xs font-semibold text-slate-300 hover:bg-slate-800 transition"
                      >
                        {isEditing ? "Done Editing" : "Edit Understanding"}
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* TAB 2: DEMONSTRATE */}
          {tab === "demonstrate" && (
            <div className="space-y-6">
              <div className="rounded-3xl border border-slate-800 bg-[#0f172a] p-6 shadow-xl space-y-4">
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400">
                  Describe or demonstrate a workflow
                </label>
                <textarea
                  value={demoInput}
                  onChange={(e) => setDemoInput(e.target.value)}
                  rows={5}
                  placeholder="Describe the steps you perform in your tool: e.g. '1. Open customer dashboard. 2. Filter invoices by unpaid status. 3. Send payment reminder if due date > 30 days.'"
                  className="w-full rounded-2xl border border-slate-700 bg-slate-900/90 p-4 text-xs text-white placeholder-slate-500 outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition leading-relaxed"
                />

                <div className="flex justify-end">
                  <button
                    type="button"
                    onClick={handleTeachDemonstrate}
                    disabled={demoSubmitting || !demoInput.trim()}
                    className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-6 py-2.5 text-xs font-bold text-white shadow-md hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition"
                  >
                    {demoSubmitting ? (
                      <>
                        <Icons.RotateCcw className="h-4 w-4 animate-spin" />
                        <span>Extracting Workflow...</span>
                      </>
                    ) : (
                      <span>Extract Demonstrated Skill</span>
                    )}
                  </button>
                </div>
              </div>

              {demoResultSkill && (
                <div className="rounded-3xl border border-slate-800 bg-[#0f172a] p-6 shadow-xl space-y-4">
                  <div className="border-b border-slate-800 pb-3">
                    <span className="text-[10px] font-bold uppercase tracking-widest text-indigo-400">
                      EXTRACTED WORKFLOW STEPS & RULES
                    </span>
                    <h3 className="mt-1 text-lg font-bold text-white">
                      {demoResultSkill.displayName}
                    </h3>
                  </div>

                  <div className="space-y-2">
                    {demoResultSkill.rules.map((rule, idx) => (
                      <div key={rule.id} className="flex items-center gap-2 text-xs text-slate-300">
                        <span className="font-mono text-indigo-400 font-bold">Step {idx + 1}:</span>
                        <span>{rule.rawText || `${rule.condition} → ${rule.action}`}</span>
                      </div>
                    ))}
                  </div>

                  <div className="pt-3">
                    <button
                      type="button"
                      onClick={() => saveSkill(demoResultSkill).then(() => router.push("/skills"))}
                      className="rounded-xl bg-indigo-600 px-5 py-2 text-xs font-bold text-white hover:bg-indigo-500"
                    >
                      Save to My Skills
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}