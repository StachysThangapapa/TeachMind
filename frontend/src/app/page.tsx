"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Sidebar } from "@/components/Sidebar";
import { Header } from "@/components/Header";
import { Icons } from "@/components/Icons";
import { executeTask } from "@/lib/api/agent";
import { getSkills } from "@/lib/api/skills";
import { CanonicalSkill } from "@/lib/types/skill";
import { TaskExecutionResult, ExecutionTimelineStep } from "@/lib/types/agent";
import { ActivityEvent } from "@/lib/types/activity";
import { MOCK_ACTIVITIES } from "@/lib/api/mockData";

export default function AssistantDashboardPage() {
  const [query, setQuery] = useState("");
  const [skills, setSkills] = useState<CanonicalSkill[]>([]);
  const [activities] = useState<ActivityEvent[]>(MOCK_ACTIVITIES);
  const [isLoading, setIsLoading] = useState(false);
  const [timelineSteps, setTimelineSteps] = useState<ExecutionTimelineStep[]>([]);
  const [result, setResult] = useState<TaskExecutionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getSkills()
      .then((data) => setSkills(data))
      .catch((err) => console.error("Could not fetch skills:", err));
  }, []);

  const handleSendQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

    setIsLoading(true);
    setError(null);
    setResult(null);
    setTimelineSteps([]);

    try {
      const executionResult = await executeTask(
        { query: query.trim() },
        (step) => {
          setTimelineSteps((prev) => {
            const index = prev.findIndex((s) => s.stage === step.stage);
            if (index >= 0) {
              const updated = [...prev];
              updated[index] = step;
              return updated;
            }
            return [...prev, step];
          });
        }
      );
      setResult(executionResult);
    } catch (err: unknown) {
      setError((err as Error)?.message || "Execution failed. Could not reach backend.");
    } finally {
      setIsLoading(false);
    }
  };

  const samplePrompt = "A customer bought a damaged clearance product 4 days ago. What should I do?";

  return (
    <div className="flex min-h-screen bg-[#090d16] text-slate-100">
      <Sidebar />

      <main className="flex-1 min-w-0 flex flex-col">
        <Header title="Assistant" subtitle="Workflow Execution" />

        <div className="mx-auto w-full max-w-6xl space-y-10 p-6 md:p-8">
          {/* Top Greeting & Input Section */}
          <section className="rounded-3xl border border-slate-800 bg-[#0f172a] p-6 md:p-8 shadow-xl">
            <div className="max-w-3xl">
              <span className="text-xs font-bold uppercase tracking-widest text-indigo-400">
                TEACHMIND
              </span>
              <h2 className="mt-2 text-2xl md:text-3xl font-extrabold tracking-tight text-white">
                Good morning
              </h2>
              <p className="mt-1 text-sm text-slate-400">
                Your AI that learns how you work.
              </p>

              {/* Ask Input Form */}
              <form onSubmit={handleSendQuery} className="mt-6 flex flex-col sm:flex-row gap-3">
                <div className="relative flex-1">
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ask TeachMind to do something..."
                    className="w-full rounded-2xl border border-slate-700 bg-slate-900/90 px-4 py-3.5 text-sm text-white placeholder-slate-500 outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition"
                  />
                </div>
                <button
                  type="submit"
                  disabled={isLoading || !query.trim()}
                  className="inline-flex items-center justify-center gap-2 rounded-2xl bg-indigo-600 px-6 py-3.5 text-xs font-bold text-white shadow-md hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  {isLoading ? (
                    <>
                      <Icons.RotateCcw className="h-4 w-4 animate-spin" />
                      <span>Processing...</span>
                    </>
                  ) : (
                    <span>Send</span>
                  )}
                </button>
              </form>

              {/* Sample Prompt Pill for Judges */}
              <div className="mt-3 flex items-center gap-2 flex-wrap">
                <span className="text-[11px] text-slate-500">Quick Test Case:</span>
                <button
                  type="button"
                  onClick={() => setQuery(samplePrompt)}
                  className="rounded-full border border-slate-800 bg-slate-900/60 px-3 py-1 text-[11px] text-slate-300 hover:border-slate-700 hover:text-white transition"
                >
                  &ldquo;{samplePrompt}&rdquo;
                </button>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mt-4 rounded-xl border border-rose-900/50 bg-rose-950/40 p-3 text-xs text-rose-300">
                {error}
              </div>
            )}

            {/* Live Execution Timeline */}
            {(timelineSteps.length > 0 || isLoading) && (
              <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-950/80 p-5">
                <p className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Execution Timeline
                </p>

                <div className="mt-4 space-y-3">
                  {timelineSteps.map((step, idx) => (
                    <div key={step.stage} className="flex items-start gap-3">
                      <div className="mt-0.5 flex flex-col items-center">
                        <span
                          className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[10px] font-bold ${
                            step.status === "completed"
                              ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40"
                              : step.status === "active"
                              ? "bg-indigo-500/20 text-indigo-400 border border-indigo-500/40 animate-pulse"
                              : "bg-slate-800 text-slate-500"
                          }`}
                        >
                          {step.status === "completed" ? "✓" : idx + 1}
                        </span>
                        {idx < timelineSteps.length - 1 && (
                          <span className="h-3 w-0.5 bg-slate-800 my-0.5" />
                        )}
                      </div>

                      <div className="flex-1">
                        <div className="flex items-center justify-between text-xs">
                          <span
                            className={`font-semibold ${
                              step.status === "active"
                                ? "text-indigo-300"
                                : step.status === "completed"
                                ? "text-slate-200"
                                : "text-slate-500"
                            }`}
                          >
                            {step.label}
                          </span>
                        </div>
                        {step.detail && (
                          <p className="text-[11px] text-slate-400">{step.detail}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Execution Result Card */}
            {result && (
              <div className="mt-6 rounded-2xl border border-emerald-900/60 bg-emerald-950/20 p-5 shadow-lg">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <span
                      className={`inline-flex items-center gap-1 rounded-xl px-3 py-1 text-xs font-extrabold tracking-wider ${
                        result.decision === "APPROVE"
                          ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                          : "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                      }`}
                    >
                      {result.decision} {result.decision === "APPROVE" ? "✓" : "❌"}
                    </span>
                  </div>

                  <div className="text-right text-xs text-slate-400">
                    <span>Similarity: </span>
                    <strong className="text-white">{result.similarity}</strong>
                  </div>
                </div>

                <div className="mt-4">
                  <p className="text-xs font-semibold text-slate-400">Reason:</p>
                  <p className="mt-0.5 text-sm font-medium text-slate-200 leading-relaxed">
                    {result.reason}
                  </p>
                </div>

                <div className="mt-4 flex items-center justify-between border-t border-slate-800/80 pt-3 text-xs text-slate-400">
                  <div>
                    <span>Skill Used: </span>
                    <strong className="text-indigo-400">
                      {result.skillUsed.displayName || result.skillUsed.name}
                    </strong>
                    <span className="ml-2 font-mono text-[10px] text-slate-500">
                      ({result.skillUsed.version})
                    </span>
                  </div>
                  {result.overrideApplied && (
                    <span className="rounded bg-amber-950/60 border border-amber-800/50 px-2 py-0.5 text-[10px] font-bold text-amber-300">
                      Exception Override Applied
                    </span>
                  )}
                </div>
              </div>
            )}
          </section>

          {/* Section: RECENT LEARNED SKILLS */}
          <section>
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                RECENT LEARNED SKILLS
              </h3>
              <Link href="/skills" className="text-xs font-semibold text-indigo-400 hover:underline">
                View all skills →
              </Link>
            </div>

            <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {skills.slice(0, 3).map((skill) => (
                <Link
                  key={skill.id}
                  href={`/skills/${skill.id}`}
                  className="rounded-2xl border border-slate-800 bg-[#0f172a] p-4 hover:border-slate-700 transition"
                >
                  <div className="flex items-start justify-between">
                    <h4 className="text-sm font-bold text-white">{skill.displayName || skill.name}</h4>
                    <span className="rounded bg-slate-800 px-1.5 py-0.5 font-mono text-[10px] text-slate-400">
                      {skill.version}
                    </span>
                  </div>
                  <p className="mt-1 text-xs text-slate-400">{skill.category}</p>
                  <div className="mt-3 flex items-center gap-1 text-xs font-semibold text-emerald-400">
                    <Icons.Zap className="h-3 w-3" />
                    <span>{Math.round((skill.confidence || 0.9) * 100)}% confidence</span>
                  </div>
                </Link>
              ))}
            </div>
          </section>

          {/* Section: LEARNING ACTIVITY */}
          <section>
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                LEARNING ACTIVITY
              </h3>
              <Link href="/activity" className="text-xs font-semibold text-indigo-400 hover:underline">
                Full activity log →
              </Link>
            </div>

            <div className="mt-4 divide-y divide-slate-800/80 rounded-2xl border border-slate-800 bg-[#0f172a] p-4">
              {activities.slice(0, 3).map((act) => (
                <div key={act.id} className="flex items-start gap-3 py-3 first:pt-1 last:pb-1">
                  <span className="mt-1 flex h-2 w-2 shrink-0 rounded-full bg-indigo-400" />
                  <div>
                    <p className="text-xs font-semibold text-slate-200">{act.description}</p>
                    <span className="text-[10px] text-slate-500">{act.timestamp}</span>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Section: OVERVIEW */}
          <section>
            <div className="border-b border-slate-800/80 pb-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                OVERVIEW
              </h3>
            </div>

            <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="rounded-2xl border border-slate-800 bg-[#0f172a] p-5">
                <p className="text-2xl font-bold text-white">12</p>
                <p className="mt-1 text-xs font-semibold text-slate-400">Skills Learned</p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-[#0f172a] p-5">
                <p className="text-2xl font-bold text-white">8</p>
                <p className="mt-1 text-xs font-semibold text-slate-400">Corrections</p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-[#0f172a] p-5">
                <p className="text-2xl font-bold text-white">94%</p>
                <p className="mt-1 text-xs font-semibold text-slate-400">Average Confidence</p>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}