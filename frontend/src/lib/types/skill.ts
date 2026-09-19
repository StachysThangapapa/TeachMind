// frontend/src/lib/types/skill.ts

export interface CanonicalSkill {
  id: string;
  name: string;
  displayName: string;
  description: string;
  category: string;

  triggers: string[];

  steps: {
    step: number;
    instruction: string;
  }[];

  rules: {
    id?: string;
    condition: string;
    action: string;
    rawText?: string;
  }[];

  examples: {
    id?: string;
    input: string;
    output?: string;
    notes?: string;
  }[];

  exceptions: {
    id?: string;
    condition: string;
    override: string;
    rawText?: string;
  }[];

  version: string;
  confidence: number;
  verified?: boolean;

  lastVerified?: string;
  createdAt?: string;
  updatedAt?: string;
}

/* ---------------- BACKEND CONTRACTS ---------------- */

export interface BackendSkillStep {
  step: number;
  instruction: string;
}

export interface BackendSkillRule {
  condition: string;
  action: string;
}

export interface BackendSkillExample {
  input: string;
  expected_behavior: string;
}

export interface BackendSkillMetadata {
  created_at: string;
  updated_at: string;
}

export interface BackendSkill {
  skill_id: string;
  name: string;
  description: string;
  triggers: string[];
  steps: BackendSkillStep[];
  rules: BackendSkillRule[];
  examples: BackendSkillExample[];
  version: number;
  verified: boolean;
  metadata: BackendSkillMetadata;
}

export interface SkillSummary {
  skill_id: string;
  name: string;
  verified: boolean;
  version: number;
}

export interface SkillListResponse {
  skills: SkillSummary[];
}

export interface SkillSearchResultItem {
  skill_id: string;
  name: string;
  similarity: number;
  skill: BackendSkill;
}

export interface SkillSearchRequest {
  query: string;
  top_k?: number;
}

export interface SkillSearchResponse {
  query: string;
  results: SkillSearchResultItem[];
}

/* ---------------- TEACHING ---------------- */

export interface TeachSkillRequest {
  method: "describe" | "demonstrate";
  input: string;
  name?: string;
  category?: string;
}

export interface TeachSkillResponse {
  skill: CanonicalSkill;
  detected_rules_count: number;
  captured_examples_count: number;
  message?: string;
}
