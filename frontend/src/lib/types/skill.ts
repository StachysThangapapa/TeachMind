// Canonical Skill representation
export interface CanonicalSkill {
  id: string;
  name: string;
  displayName: string;
  description: string;
  category: string;
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
  confidence: number; // 0.0 to 1.0 (e.g. 0.92)
  lastVerified?: string;
  createdAt?: string;
  updatedAt?: string;
}

// Backend Skill representation (from AI Agent / backend contract)
export interface BackendSkillRule {
  condition: string;
  action: string;
}

export interface BackendSkillStep {
  step: number;
  instruction: string;
}

export interface BackendSkillPayload {
  description: string;
  triggers: string[];
  steps: BackendSkillStep[];
  rules: BackendSkillRule[];
  examples: string[] | { input: string; output?: string }[];
  exceptions?: string[];
}

export interface SkillSearchResultItem {
  skill_id: string;
  name: string;
  similarity: number; // e.g. 0.91 or 0.94
  skill: BackendSkillPayload;
}

export interface SkillSearchRequest {
  query: string;
  top_k?: number;
}

export interface SkillSearchResponse {
  query: string;
  results: SkillSearchResultItem[];
}

export interface TeachSkillRequest {
  method: 'describe' | 'demonstrate';
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
