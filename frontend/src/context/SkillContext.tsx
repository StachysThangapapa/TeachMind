"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { Skill, ActivityLog, TestRun, Correction } from "../types";

interface SkillContextType {
  skills: Skill[];
  activities: ActivityLog[];
  testRuns: TestRun[];
  corrections: Correction[];
  addSkill: (skillData: Omit<Skill, "id" | "createdAt" | "usageCount" | "accuracyRate">) => Skill;
  updateSkill: (id: string, updates: Partial<Skill>) => void;
  deleteSkill: (id: string) => void;
  addTestRun: (run: TestRun) => void;
  applyCorrection: (skillId: string, ruleTarget: string, userCorrection: string) => void;
  verifySkill: (skillId: string) => void;
  recordReuse: (skillId: string) => void;
  resetToDefaults: () => void;
}

const DEFAULT_SKILLS: Skill[] = [
  {
    id: "skill-1",
    title: "Process Monthly Sales Report",
    description: "Extract raw CRM deals, aggregate regional figures, deduplicate entries, and compile an executive summary.",
    category: "Sales",
    status: "Verified",
    method: "instructions",
    steps: [
      { id: "s1", order: 1, title: "Fetch CRM deals data for previous month", description: "Query active pipeline deals closing in the last calendar month.", actionType: "extract" },
      { id: "s2", order: 2, title: "Deduplicate and clean contacts", description: "Remove duplicate lead IDs and standardize currency to USD.", actionType: "transform" },
      { id: "s3", order: 3, title: "Calculate regional revenue & quotas", description: "Compute totals for North America, EMEA, and APAC against targets.", actionType: "validate" },
      { id: "s4", order: 4, title: "Format summary spreadsheet & notify", description: "Generate formatted workbook and post link to Slack #sales-exec.", actionType: "notify" }
    ],
    examples: [
      { id: "e1", input: "Monthly CRM export with 450 raw records (USD, EUR, GBP)", output: "Aggregated 3-tab workbook: Summary, Regional Splits, Top 10 Deals" }
    ],
    demonstrations: [],
    rules: [
      "Always convert non-USD currencies using the month-end exchange rate.",
      "Exclude internal test accounts with domain @company-test.internal.",
      "Flag any deal variance greater than 25% from forecast."
    ],
    edgeCases: [
      "Deals closed on the 31st with pending approval status.",
      "Multi-currency contracts with tiered milestones."
    ],
    usageCount: 14,
    accuracyRate: 98,
    createdAt: "2026-03-01T10:00:00Z",
    lastTestedAt: "2026-03-18T14:30:00Z"
  },
  {
    id: "skill-2",
    title: "Format Lead Qualification Data",
    description: "Parses incoming demo requests, enriches company domain info, and routes high-intent leads to Account Executives.",
    category: "Operations",
    status: "Verified",
    method: "instructions",
    steps: [
      { id: "s2-1", order: 1, title: "Extract inbound form submissions", description: "Poll inbound webhook for company name, work email, and employee count.", actionType: "extract" },
      { id: "s2-2", order: 2, title: "Enrich firmographic data", description: "Fetch industry, revenue band, and tech stack details.", actionType: "transform" },
      { id: "s2-3", order: 3, title: "Score lead tier (Tier 1 vs Tier 2)", description: "Mark as Tier 1 if employee count > 100 or ARR > $10M.", actionType: "validate" },
      { id: "s2-4", order: 4, title: "Route to calendar booking", description: "Send automated scheduling invite with assigned AE.", actionType: "dispatch" }
    ],
    examples: [
      { id: "e2", input: "Jane Doe, CTO at Acme Corp (500 employees), asking for enterprise security features", output: "Tier 1 Enterprise Lead routed to Enterprise AE Alex." }
    ],
    demonstrations: [],
    rules: [
      "Reject personal email domains (gmail, yahoo, hotmail).",
      "Route European timezones to EMEA AE pod."
    ],
    edgeCases: [
      "Company domains that redirect to parent conglomerates."
    ],
    usageCount: 9,
    accuracyRate: 95,
    createdAt: "2026-03-05T08:15:00Z",
    lastTestedAt: "2026-03-17T11:20:00Z"
  },
  {
    id: "skill-3",
    title: "Customer Support Ticket Triage",
    description: "Analyzes incoming support tickets, categorizes urgency, drafts initial contextual responses, and assigns tags.",
    category: "Customer Support",
    status: "Learning",
    method: "example",
    steps: [
      { id: "s3-1", order: 1, title: "Parse ticket subject & description", description: "Detect customer sentiment and primary issue category.", actionType: "extract" },
      { id: "s3-2", order: 2, title: "Identify severity level", description: "P0 (Service Down), P1 (Feature Blocked), P2 (General Query).", actionType: "validate" },
      { id: "s3-3", order: 3, title: "Draft suggested resolution", description: "Retrieve matching knowledge-base articles and compose response.", actionType: "transform" }
    ],
    examples: [
      { id: "e3", input: "Our login page is returning 504 Gateway Timeout for our team.", output: "Severity: P0. Alert On-Call Engineer. Suggested Draft: 'We are investigating the auth service latency...'" }
    ],
    demonstrations: [],
    rules: [
      "If user mentions 'billing error' or 'charged twice', escalate directly to Billing Ops.",
      "Check if user is on Enterprise SLA before setting priority."
    ],
    edgeCases: [
      "Tickets with foreign language attachments."
    ],
    usageCount: 4,
    accuracyRate: 84,
    createdAt: "2026-03-12T16:45:00Z",
    lastTestedAt: "2026-03-18T09:10:00Z"
  },
  {
    id: "skill-4",
    title: "Vendor Invoice Reconciliation",
    description: "Matches PDF invoice line items against purchase orders, flags price discrepancies, and queues approved bills.",
    category: "Finance",
    status: "Needs Correction",
    method: "demonstration",
    steps: [
      { id: "s4-1", order: 1, title: "OCR extract invoice PDF header & rows", description: "Parse PO number, vendor tax ID, total amount, line items.", actionType: "extract" },
      { id: "s4-2", order: 2, title: "Match against NetSuite PO line items", description: "Verify unit prices and quantity delivered.", actionType: "validate" },
      { id: "s4-3", order: 3, title: "Flag line discrepancies", description: "Highlight items with price difference > 2%.", actionType: "transform" }
    ],
    examples: [],
    demonstrations: [
      { id: "d1", timestamp: "00:01", actionType: "click", target: "Upload Invoice PDF button" },
      { id: "d2", timestamp: "00:04", actionType: "extract", target: "PO #88492 and Tax ID", value: "US-88492" },
      { id: "d3", timestamp: "00:08", actionType: "select", target: "ERP Match PO #88492" }
    ],
    rules: [
      "Allow up to $5 difference in total tax calculation due to state rounding.",
      "Do NOT auto-approve invoices from unverified first-time vendors."
    ],
    edgeCases: [
      "Invoices split across multiple freight deliveries.",
      "Currency mismatch between PO currency and invoice currency."
    ],
    usageCount: 6,
    accuracyRate: 76,
    createdAt: "2026-03-14T12:00:00Z",
    lastTestedAt: "2026-03-18T16:00:00Z"
  }
];

const DEFAULT_ACTIVITIES: ActivityLog[] = [
  {
    id: "act-1",
    type: "teach",
    skillTitle: "Process Monthly Sales Report",
    description: "Taught new workflow with 4 automated steps and 3 validation rules.",
    timestamp: "10 mins ago"
  },
  {
    id: "act-2",
    type: "test",
    skillTitle: "Customer Support Ticket Triage",
    description: "Simulated execution on 5 sample incoming tickets with 84% accuracy.",
    timestamp: "25 mins ago"
  },
  {
    id: "act-3",
    type: "correct",
    skillTitle: "Vendor Invoice Reconciliation",
    description: "Corrected rule: 'Do NOT auto-approve invoices from unverified first-time vendors'.",
    timestamp: "1 hour ago"
  },
  {
    id: "act-4",
    type: "verify",
    skillTitle: "Format Lead Qualification Data",
    description: "User verified understanding and promoted skill to production.",
    timestamp: "3 hours ago"
  },
  {
    id: "act-5",
    type: "reuse",
    skillTitle: "Process Monthly Sales Report",
    description: "Automated execution completed for Finance executive review.",
    timestamp: "Yesterday"
  }
];

const SkillContext = createContext<SkillContextType | undefined>(undefined);

const STORAGE_KEY_SKILLS = "teachmind_skills_v1";
const STORAGE_KEY_ACTIVITIES = "teachmind_activities_v1";
const STORAGE_KEY_TESTRUNS = "teachmind_testruns_v1";
const STORAGE_KEY_CORRECTIONS = "teachmind_corrections_v1";

export const SkillProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [skills, setSkills] = useState<Skill[]>(DEFAULT_SKILLS);
  const [activities, setActivities] = useState<ActivityLog[]>(DEFAULT_ACTIVITIES);
  const [testRuns, setTestRuns] = useState<TestRun[]>([]);
  const [corrections, setCorrections] = useState<Correction[]>([]);
  const [isLoaded, setIsLoaded] = useState(false);

  // Load from localStorage on mount
  useEffect(() => {
    const timer = setTimeout(() => {
      try {
        const savedSkills = localStorage.getItem(STORAGE_KEY_SKILLS);
        const savedActivities = localStorage.getItem(STORAGE_KEY_ACTIVITIES);
        const savedTestRuns = localStorage.getItem(STORAGE_KEY_TESTRUNS);
        const savedCorrections = localStorage.getItem(STORAGE_KEY_CORRECTIONS);

        if (savedSkills) {
          setSkills(JSON.parse(savedSkills));
        }
        if (savedActivities) {
          setActivities(JSON.parse(savedActivities));
        }
        if (savedTestRuns) {
          setTestRuns(JSON.parse(savedTestRuns));
        }
        if (savedCorrections) {
          setCorrections(JSON.parse(savedCorrections));
        }
      } catch (err) {
        console.warn("Could not read TeachMind store from localStorage:", err);
      } finally {
        setIsLoaded(true);
      }
    }, 0);

    return () => clearTimeout(timer);
  }, []);

  // Save changes to localStorage
  useEffect(() => {
    if (!isLoaded) return;
    try {
      localStorage.setItem(STORAGE_KEY_SKILLS, JSON.stringify(skills));
      localStorage.setItem(STORAGE_KEY_ACTIVITIES, JSON.stringify(activities));
      localStorage.setItem(STORAGE_KEY_TESTRUNS, JSON.stringify(testRuns));
      localStorage.setItem(STORAGE_KEY_CORRECTIONS, JSON.stringify(corrections));
    } catch (err) {
      console.warn("Could not save TeachMind store to localStorage:", err);
    }
  }, [skills, activities, testRuns, corrections, isLoaded]);

  const addSkill = (skillData: Omit<Skill, "id" | "createdAt" | "usageCount" | "accuracyRate">): Skill => {
    const newSkill: Skill = {
      ...skillData,
      id: `skill-${Date.now()}`,
      createdAt: new Date().toISOString(),
      usageCount: 0,
      accuracyRate: 90
    };

    setSkills((prev) => [newSkill, ...prev]);

    const newActivity: ActivityLog = {
      id: `act-${Date.now()}`,
      type: "teach",
      skillId: newSkill.id,
      skillTitle: newSkill.title,
      description: `Taught skill via ${newSkill.method} with ${newSkill.steps.length} steps.`,
      timestamp: "Just now"
    };
    setActivities((prev) => [newActivity, ...prev.slice(0, 19)]);

    return newSkill;
  };

  const updateSkill = (id: string, updates: Partial<Skill>) => {
    setSkills((prev) =>
      prev.map((skill) => (skill.id === id ? { ...skill, ...updates } : skill))
    );
  };

  const deleteSkill = (id: string) => {
    const target = skills.find((s) => s.id === id);
    setSkills((prev) => prev.filter((s) => s.id !== id));
    if (target) {
      const newActivity: ActivityLog = {
        id: `act-${Date.now()}`,
        type: "correct",
        skillTitle: target.title,
        description: `Removed skill from workspace.`,
        timestamp: "Just now"
      };
      setActivities((prev) => [newActivity, ...prev.slice(0, 19)]);
    }
  };

  const addTestRun = (run: TestRun) => {
    setTestRuns((prev) => [run, ...prev]);
    // update skill lastTestedAt and usage count
    setSkills((prev) =>
      prev.map((s) =>
        s.id === run.skillId
          ? {
              ...s,
              lastTestedAt: new Date().toISOString(),
              usageCount: s.usageCount + 1,
              status: s.status === "Draft" ? "Learning" : s.status
            }
          : s
      )
    );

    const newActivity: ActivityLog = {
      id: `act-${Date.now()}`,
      type: "test",
      skillId: run.skillId,
      skillTitle: run.skillTitle,
      description: `Ran simulated test (${run.status.toUpperCase()}) across ${run.logs.length} execution steps.`,
      timestamp: "Just now"
    };
    setActivities((prev) => [newActivity, ...prev.slice(0, 19)]);
  };

  const applyCorrection = (skillId: string, ruleTarget: string, userCorrection: string) => {
    const correction: Correction = {
      id: `corr-${Date.now()}`,
      skillId,
      ruleTarget,
      userCorrection,
      appliedAt: new Date().toISOString()
    };
    setCorrections((prev) => [correction, ...prev]);

    setSkills((prev) =>
      prev.map((s) => {
        if (s.id !== skillId) return s;
        const updatedRules = [...s.rules, userCorrection];
        return {
          ...s,
          rules: updatedRules,
          status: "Verified",
          accuracyRate: Math.min(99, s.accuracyRate + 6)
        };
      })
    );

    const targetSkill = skills.find((s) => s.id === skillId);
    const newActivity: ActivityLog = {
      id: `act-${Date.now()}`,
      type: "correct",
      skillId,
      skillTitle: targetSkill ? targetSkill.title : "Skill",
      description: `Applied correction: "${userCorrection.slice(0, 50)}${userCorrection.length > 50 ? "..." : ""}"`,
      timestamp: "Just now"
    };
    setActivities((prev) => [newActivity, ...prev.slice(0, 19)]);
  };

  const verifySkill = (skillId: string) => {
    setSkills((prev) =>
      prev.map((s) => (s.id === skillId ? { ...s, status: "Verified", accuracyRate: Math.max(95, s.accuracyRate) } : s))
    );
    const target = skills.find((s) => s.id === skillId);
    if (target) {
      const newActivity: ActivityLog = {
        id: `act-${Date.now()}`,
        type: "verify",
        skillId,
        skillTitle: target.title,
        description: `Verified AI understanding and promoted to production workflow.`,
        timestamp: "Just now"
      };
      setActivities((prev) => [newActivity, ...prev.slice(0, 19)]);
    }
  };

  const recordReuse = (skillId: string) => {
    setSkills((prev) =>
      prev.map((s) => (s.id === skillId ? { ...s, usageCount: s.usageCount + 1 } : s))
    );
    const target = skills.find((s) => s.id === skillId);
    if (target) {
      const newActivity: ActivityLog = {
        id: `act-${Date.now()}`,
        type: "reuse",
        skillId,
        skillTitle: target.title,
        description: `Autonomous execution completed successfully.`,
        timestamp: "Just now"
      };
      setActivities((prev) => [newActivity, ...prev.slice(0, 19)]);
    }
  };

  const resetToDefaults = () => {
    setSkills(DEFAULT_SKILLS);
    setActivities(DEFAULT_ACTIVITIES);
    setTestRuns([]);
    setCorrections([]);
    localStorage.removeItem(STORAGE_KEY_SKILLS);
    localStorage.removeItem(STORAGE_KEY_ACTIVITIES);
    localStorage.removeItem(STORAGE_KEY_TESTRUNS);
    localStorage.removeItem(STORAGE_KEY_CORRECTIONS);
  };

  return (
    <SkillContext.Provider
      value={{
        skills,
        activities,
        testRuns,
        corrections,
        addSkill,
        updateSkill,
        deleteSkill,
        addTestRun,
        applyCorrection,
        verifySkill,
        recordReuse,
        resetToDefaults
      }}
    >
      {children}
    </SkillContext.Provider>
  );
};

export const useSkills = () => {
  const context = useContext(SkillContext);
  if (!context) {
    throw new Error("useSkills must be used within a SkillProvider");
  }
  return context;
};
