"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Sidebar } from "@/components/Sidebar";
import { Header } from "@/components/Header";
import { Icons } from "@/components/Icons";
import {
  getVerification,
  runVerification,
  submitCorrection,
  resetVerificationDemoState
} from "@/lib/api/verification";
import { getSkills } from "@/lib/api/skills";
import { executeTask } from "@/lib/api/agent";
import { CanonicalSkill } from "@/lib/types/skill";
import {
  VerificationResult,
  CorrectionResponse
} from "@/lib/types/verification";
import { TaskExecutionResult } from "@/lib/types/agent";

function VerificationPageContent() {
  const searchParams = useSearchParams();
  const [skills, setSkills] = useState<CanonicalSkill[]>([]);
  const [selectedSkillId, setSelectedSkillId] = useState<string>("skill_001");
  const [verificationResult, setVerificationResult] = useState<VerificationResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Correction state
  const [correctionText, setCorrectionText] = useState(
    "Damaged products should always be approved regardless of clearance status."
  );
  const [isCorrecting, setIsCorrecting] = useState(false);
  const [correctionResult, setCorrectionResult] = useState<CorrectionResponse | null>(null);

  // Reuse / Test similar case state
  const [reuseQuery, setReuseQuery] = useState(
    "A damaged clearance product was purchased 4 days ago."
  );
  const [isReusing, setIsReusing] = useState(false);
  const [reuseResult, setReuseResult] = useState<TaskExecutionResult | null>(null);

  useEffect(() => {
    getSkills()
      .then((data) => {
        setSkills(data);
        const paramId = searchParams.get("skillId");
        if (paramId) {
          setSelectedSkillId(paramId);
        } else if (data.length > 0) {
          setSelectedSkillId(data[0].id);
        }
      })
      .catch((err) => console.error(err));
  }, [searchParams]);

  useEffect(() => {
    let isMounted = true;
    if (selectedSkillId) {
      getVerification(selectedSkillId)
        .then((res) => {
          if (isMounted) setVerificationResult(res);
        })
        .catch((err) => {
          if (isMounted) setError(err.message);
        });
    }
    return () => {
      isMounted = false;
    };
  }, [selectedSkillId]);

  const handleRunVerification = async () => {
    if (!selectedSkillId || isRunning) return;
    setIsRunning(true);
    setError(null);
    setCorrectionResult(null);

    try {
      const res = await runVerification(selectedSkillId);
      setVerificationResult(res);
    } catch (err: unknown) {
      setError((err as Error)?.message || "Failed to run verification.");
    } finally {
      setIsRunning(false);
    }
  };

  const handleCorrectTeachMind = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!correctionText.trim() || isCorrecting) return;
    setIsCorrecting(true);
    setError(null);

    try {
      const res = await submitCorrection({
        skillId: selectedSkillId,
        failedTestCaseId: "tc-5",
        mistakeDescription: "Rejected damaged clearance item",
        userCorrection: correctionText.trim()
      });
      setCorrectionResult(res);

      // Re-fetch verification result to reflect updated status
      const updatedVerification = await getVerification(selectedSkillId);
      setVerificationResult(updatedVerification);
    } catch (err: unknown) {
      setError((err as Error)?.message || "Could not submit correction.");
    } finally {
      setIsCorrecting(false);
    }
  };

  const handleRunReuseTest = async () => {
    if (!reuseQuery.trim() || isReusing) return;
    setIsReusing(true);
    try {
      const res = await executeTask({ query: reuseQuery });
      setReuseResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsReusing(false);
    }
  };

  const handleResetToFailureCase = async () => {
    resetVerificationDemoState();
    setCorrectionResult(null);
    setReuseResult(null);
    const res = await getVerification(selectedSkillId);
    setVerificationResult(res);
  };

  const activeSkill = skills.find((s) => s.id === selectedSkillId) || skills[0];
  const failedCase = verificationResult?.testCases.find((tc) => tc.status === "FAILED");

  return (
    <div className="flex min-h-screen bg-[#090d16] text-slate-100">
      <Sidebar />

      <main className="flex-1 min-w-0 flex flex-col">
        <Header title="Skill Verification" subtitle="Evaluation & Correction" />

        <div className="mx-auto w-full max-w-5xl space-y-8 p-6 md:p-8">
          {/* Header & Skill Selector */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-6">
            <div>
              <h2 className="text-2xl font-extrabold tracking-tight text-white">
                Skill Verification
              </h2>
              <p className="mt-1 text-xs text-slate-400">
                Evaluate learned rules against synthetic test suites to verify accuracy.
              </p>
            </div>

            <div className="flex items-center gap-3">
              {/* Reset to uncorrected state for live judge demo */}
              <button
                type="button"
                onClick={handleResetToFailureCase}
                title="Reset to v1.0 failure state to demonstrate correction flow"
                className="text-[11px] text-slate-400 hover:text-white underline"
              >
                Reset Demo to v1.0
              </button>

              {/* Skill Selector: [ Refund Processing ▼ ] */}
              <select
                value={selectedSkillId}
                onChange={(e) => setSelectedSkillId(e.target.value)}
                className="rounded-xl border border-slate-700 bg-[#0f172a] px-3.5 py-2 text-xs font-bold text-white outline-none focus:border-indigo-500 transition"
              >
                {skills.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.displayName || s.name}
                  </option>
                ))}
              </select>

              <span className="rounded-lg border border-slate-800 bg-slate-900 px-2.5 py-1 text-xs font-mono text-indigo-400 font-bold">
                {verificationResult?.version || activeSkill?.version || "v1.1"}
              </span>
            </div>
          </div>

          {error && (
            <div className="rounded-xl border border-rose-900/50 bg-rose-950/40 p-3.5 text-xs text-rose-300">
              {error}
            </div>
          )}

          {/* VERIFICATION SCORE */}
          {verificationResult && (
            <section className="rounded-3xl border border-slate-800 bg-[#0f172a] p-6 shadow-xl space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  VERIFICATION SCORE
                </span>
                <span className="text-xs font-bold text-white">
                  {verificationResult.score.passed} / {verificationResult.score.total} passed
                </span>
              </div>

              {/* Progress Bar */}
              <div className="h-3 w-full overflow-hidden rounded-full bg-slate-800">
                <div
                  className={`h-full transition-all duration-500 ${
                    verificationResult.score.accuracy === 100
                      ? "bg-emerald-500 shadow-sm shadow-emerald-500/50"
                      : "bg-amber-500"
                  }`}
                  style={{ width: `${verificationResult.score.accuracy}%` }}
                />
              </div>

              <div className="flex items-center justify-between text-xs pt-1">
                <div className="flex items-center gap-4">
                  <span className="text-emerald-400 font-semibold">
                    Passed: {verificationResult.score.passed}
                  </span>
                  <span
                    className={
                      verificationResult.score.failed > 0
                        ? "text-rose-400 font-semibold"
                        : "text-slate-500"
                    }
                  >
                    Failed: {verificationResult.score.failed}
                  </span>
                </div>

                <div className="font-bold text-white text-sm">
                  {verificationResult.score.accuracy}% accuracy
                </div>
              </div>

              <div className="flex justify-end pt-2">
                <button
                  type="button"
                  onClick={handleRunVerification}
                  disabled={isRunning}
                  className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-xs font-bold text-white shadow-md hover:bg-indigo-500 disabled:opacity-50 transition"
                >
                  {isRunning ? (
                    <>
                      <Icons.RotateCcw className="h-4 w-4 animate-spin" />
                      <span>Running Verification...</span>
                    </>
                  ) : (
                    <span>Run Verification</span>
                  )}
                </button>
              </div>
            </section>
          )}

          {/* CORRECTION UI (WHEN A TEST FAILS) */}
          {failedCase && !correctionResult && (
            <section className="rounded-3xl border border-rose-900/60 bg-rose-950/20 p-6 shadow-xl space-y-4">
              <div className="flex items-center gap-2 text-rose-400">
                <Icons.AlertTriangle className="h-5 w-5" />
                <h3 className="text-sm font-bold uppercase tracking-widest text-rose-300">
                  TEACHMIND MADE A MISTAKE
                </h3>
              </div>

              <div className="rounded-2xl border border-rose-900/40 bg-[#0f172a] p-4 text-xs space-y-2">
                <p className="text-slate-400">
                  <strong>Input:</strong> &ldquo;{failedCase.input}&rdquo;
                </p>
                <div className="flex items-center gap-6 pt-1">
                  <span className="text-rose-400 font-bold">
                    TeachMind: {failedCase.actual} ❌
                  </span>
                  <span className="text-emerald-400 font-bold">
                    Expected: {failedCase.expected}
                  </span>
                </div>
              </div>

              <form onSubmit={handleCorrectTeachMind} className="space-y-3 pt-2">
                <label className="block text-xs font-bold text-slate-300">
                  Teach TeachMind what it got wrong:
                </label>
                <textarea
                  value={correctionText}
                  onChange={(e) => setCorrectionText(e.target.value)}
                  rows={3}
                  className="w-full rounded-2xl border border-slate-700 bg-slate-900 p-3.5 text-xs text-white placeholder-slate-500 outline-none focus:border-indigo-500 transition"
                />

                <button
                  type="submit"
                  disabled={isCorrecting || !correctionText.trim()}
                  className="inline-flex items-center gap-2 rounded-xl bg-amber-600 px-5 py-2.5 text-xs font-bold text-white shadow-md hover:bg-amber-500 disabled:opacity-50 transition"
                >
                  {isCorrecting ? (
                    <>
                      <Icons.RotateCcw className="h-4 w-4 animate-spin" />
                      <span>Updating Understanding...</span>
                    </>
                  ) : (
                    <span>Correct TeachMind</span>
                  )}
                </button>
              </form>
            </section>
          )}

          {/* UNDERSTANDING UPDATED BANNER */}
          {correctionResult && (
            <section className="rounded-3xl border border-emerald-900/60 bg-emerald-950/20 p-6 shadow-xl space-y-3">
              <div className="flex items-center justify-between border-b border-emerald-900/40 pb-3">
                <div className="flex items-center gap-2">
                  <span className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500 text-black font-bold text-xs">
                    ✓
                  </span>
                  <h3 className="text-sm font-bold uppercase tracking-widest text-emerald-300">
                    UNDERSTANDING UPDATED
                  </h3>
                </div>
                <span className="rounded bg-emerald-900/60 px-2.5 py-0.5 text-xs font-mono text-emerald-200">
                  {correctionResult.previousVersion} → {correctionResult.newVersion}
                </span>
              </div>

              <div className="text-xs text-slate-300 space-y-1">
                <p className="font-semibold text-slate-400">New exception learned:</p>
                <p className="rounded-xl border border-emerald-900/30 bg-slate-900/80 p-3 text-emerald-200 font-mono">
                  &ldquo;{correctionResult.newExceptionLearned}&rdquo;
                </p>
              </div>

              <div className="flex items-center justify-between pt-2 text-xs">
                <span className="text-emerald-400 font-semibold">✓ Skill memory updated</span>
                <button
                  type="button"
                  onClick={handleRunVerification}
                  className="text-xs font-bold text-indigo-400 hover:underline"
                >
                  Re-run verification now →
                </button>
              </div>
            </section>
          )}

          {/* TEST CASES TABLE */}
          {verificationResult && (
            <section className="space-y-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                TEST CASES
              </h3>

              <div className="space-y-3">
                {verificationResult.testCases.map((tc, idx) => (
                  <div
                    key={tc.id}
                    className={`rounded-2xl border p-4 text-xs transition ${
                      tc.status === "PASSED"
                        ? "border-slate-800 bg-[#0f172a]"
                        : "border-rose-900/60 bg-rose-950/20"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-indigo-400 font-bold">Case {idx + 1}</span>
                      <span
                        className={`rounded-md px-2 py-0.5 text-[10px] font-bold ${
                          tc.status === "PASSED"
                            ? "bg-emerald-950/80 text-emerald-300 border border-emerald-800/50"
                            : "bg-rose-950/80 text-rose-300 border border-rose-800/50"
                        }`}
                      >
                        {tc.status === "PASSED" ? "✓ PASSED" : "❌ FAILED"}
                      </span>
                    </div>

                    <p className="mt-2 text-slate-300">
                      <strong>Input:</strong> &ldquo;{tc.input}&rdquo;
                    </p>

                    <div className="mt-2 flex items-center gap-6 text-[11px]">
                      <span className="text-slate-400">
                        Expected: <strong className="text-white">{tc.expected}</strong>
                      </span>
                      <span className="text-slate-400">
                        Actual:{" "}
                        <strong
                          className={
                            tc.status === "PASSED" ? "text-emerald-400" : "text-rose-400"
                          }
                        >
                          {tc.actual || "PENDING"}
                        </strong>
                      </span>
                      {tc.reason && (
                        <span className="text-slate-500 italic">({tc.reason})</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* SECTION 13: REUSE / EXECUTION RESULT DEMO BOX */}
          <section className="rounded-3xl border border-slate-800 bg-[#0f172a] p-6 shadow-xl space-y-4">
            <div className="border-b border-slate-800 pb-3">
              <span className="text-[10px] font-bold uppercase tracking-widest text-indigo-400">
                REUSE & VERIFIED EXECUTION
              </span>
              <h3 className="mt-1 text-lg font-bold text-white">
                Test a New Similar Case (Reuse Loop)
              </h3>
              <p className="text-xs text-slate-400">
                Confirm that TeachMind applies its updated understanding to new incoming tasks.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-3">
              <input
                type="text"
                value={reuseQuery}
                onChange={(e) => setReuseQuery(e.target.value)}
                placeholder="Enter a task to test..."
                className="flex-1 rounded-2xl border border-slate-700 bg-slate-900 p-3 text-xs text-white outline-none focus:border-indigo-500 transition"
              />
              <button
                type="button"
                onClick={handleRunReuseTest}
                disabled={isReusing || !reuseQuery.trim()}
                className="rounded-2xl bg-indigo-600 px-6 py-3 text-xs font-bold text-white hover:bg-indigo-500 disabled:opacity-50 transition"
              >
                {isReusing ? "Executing..." : "Test Case"}
              </button>
            </div>

            {reuseResult && (
              <div className="mt-4 rounded-2xl border border-emerald-900/60 bg-emerald-950/20 p-5 space-y-3">
                <div className="space-y-1 font-mono text-xs text-slate-300">
                  <p className="text-indigo-400 font-bold">Searching Skill Memory</p>
                  <p className="text-emerald-400">
                    ✓ Found {reuseResult.skillUsed.displayName || reuseResult.skillUsed.name} (Similarity: {reuseResult.similarity})
                  </p>
                  <p className="text-emerald-400">Applying learned rules ✓</p>
                  <p className="text-emerald-400">Checking exception ✓</p>
                </div>

                <div className="border-t border-slate-800 pt-3">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    RESULT
                  </span>
                  <div className="mt-1 flex items-center gap-2">
                    <span className="rounded-lg bg-emerald-500/20 border border-emerald-500/40 px-2.5 py-1 text-xs font-bold text-emerald-300">
                      {reuseResult.decision} ✓
                    </span>
                  </div>
                  <p className="mt-2 text-xs text-slate-200">
                    <strong>Reason: </strong> {reuseResult.reason}
                  </p>
                </div>
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}

export default function VerificationPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-xs text-slate-500">Loading verification...</div>}>
      <VerificationPageContent />
    </Suspense>
  );
}
