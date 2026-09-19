"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Sidebar } from "@/components/Sidebar";
import { Header } from "@/components/Header";
import { SkillCard } from "@/components/SkillCard";
import { Icons } from "@/components/Icons";
import { getSkills } from "@/lib/api/skills";
import { CanonicalSkill } from "@/lib/types/skill";

export default function MySkillsPage() {
  const [skills, setSkills] = useState<CanonicalSkill[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    getSkills()
      .then((data) => setSkills(data))
      .catch((err) => console.error(err))
      .finally(() => setIsLoading(false));
  }, []);

  const filteredSkills = skills.filter((skill) => {
    const q = searchQuery.toLowerCase();
    return (
      skill.displayName.toLowerCase().includes(q) ||
      skill.name.toLowerCase().includes(q) ||
      skill.description.toLowerCase().includes(q) ||
      skill.category.toLowerCase().includes(q)
    );
  });

  return (
    <div className="flex min-h-screen bg-[#090d16] text-slate-100">
      <Sidebar />

      <main className="flex-1 min-w-0 flex flex-col">
        <Header
          title="My Skills"
          subtitle="Skill Repository"
          actionButton={
            <Link
              href="/teach"
              className="inline-flex items-center gap-1.5 rounded-xl bg-indigo-600 px-3.5 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 transition"
            >
              <Icons.Plus className="h-3.5 w-3.5" />
              <span>Teach Skill</span>
            </Link>
          }
        />

        <div className="mx-auto w-full max-w-6xl space-y-6 p-6 md:p-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h2 className="text-2xl font-extrabold tracking-tight text-white">
                My Skills
              </h2>
              <p className="mt-1 text-xs text-slate-400">
                Learned workflows remembered by TeachMind for autonomous execution.
              </p>
            </div>

            {/* Search field: [ Search skills... ] */}
            <div className="relative w-full sm:w-72">
              <Icons.Search className="absolute left-3.5 top-3 h-4 w-4 text-slate-500" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search skills..."
                className="w-full rounded-xl border border-slate-800 bg-[#0f172a] py-2.5 pl-10 pr-4 text-xs text-white placeholder-slate-500 outline-none focus:border-indigo-500 transition"
              />
            </div>
          </div>

          {/* Grid of Skill Cards */}
          {isLoading ? (
            <div className="py-16 text-center text-xs text-slate-500">
              <Icons.RotateCcw className="mx-auto h-5 w-5 animate-spin text-indigo-400" />
              <p className="mt-2">Loading skills from memory...</p>
            </div>
          ) : filteredSkills.length === 0 ? (
            <div className="rounded-3xl border border-slate-800 bg-[#0f172a] p-12 text-center">
              <Icons.Layers className="mx-auto h-8 w-8 text-slate-600" />
              <h4 className="mt-3 text-sm font-bold text-white">No matching skills found</h4>
              <p className="mt-1 text-xs text-slate-500">
                Try a different search term or teach TeachMind a new workflow.
              </p>
              <Link
                href="/teach"
                className="mt-4 inline-flex items-center gap-1.5 rounded-xl bg-indigo-600 px-4 py-2 text-xs font-bold text-white hover:bg-indigo-500 transition"
              >
                <Icons.Plus className="h-3.5 w-3.5" />
                <span>Teach a Skill</span>
              </Link>
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {filteredSkills.map((skill) => (
                <SkillCard key={skill.id} skill={skill} />
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
