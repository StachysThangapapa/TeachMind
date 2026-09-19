import {
  CanonicalSkill,
  BackendSkill,
  SkillSummary,
  SkillSearchResponse,
} from "../types/skill";

export interface NormalizedSkillMatch {
  skill: CanonicalSkill;
  similarity: number;
  similarityPercent: number;
}

/**
 * Convert a complete backend SkillResponse into the frontend's
 * CanonicalSkill representation.
 */
export function adaptBackendSkillToCanonical(
  backendSkill: BackendSkill,
): CanonicalSkill {
  return {
    id: backendSkill.skill_id,
    name: backendSkill.name,
    displayName: backendSkill.name,
    description: backendSkill.description || "",
    category: inferCategory(backendSkill),

    triggers: backendSkill.triggers || [],

    steps: backendSkill.steps || [],

    rules: (backendSkill.rules || []).map((rule, index) => ({
      id: `rule-${index + 1}`,
      condition: rule.condition,
      action: rule.action,
      rawText: `${rule.condition} → ${rule.action}`,
    })),

    examples: (backendSkill.examples || []).map((example, index) => ({
      id: `example-${index + 1}`,
      input: example.input,
      output: example.expected_behavior,
    })),

    exceptions: [],

    version: `v${backendSkill.version}`,
    confidence: backendSkill.verified ? 1 : 0.8,
    verified: backendSkill.verified,

    lastVerified: backendSkill.verified
      ? backendSkill.metadata?.updated_at
      : undefined,

    createdAt: backendSkill.metadata?.created_at,
    updatedAt: backendSkill.metadata?.updated_at,
  };
}

/**
 * Convert the lightweight GET /skills summary into a CanonicalSkill.
 *
 * IMPORTANT:
 * GET /skills intentionally returns summaries only.
 * Detailed information should be loaded through GET /skills/{id}.
 */
export function adaptSkillSummaryToCanonical(
  summary: SkillSummary,
): CanonicalSkill {
  return {
    id: summary.skill_id,
    name: summary.name,
    displayName: summary.name,

    description: "",
    category: "General",

    triggers: [],
    steps: [],
    rules: [],
    examples: [],
    exceptions: [],

    version: `v${summary.version}`,
    confidence: summary.verified ? 1 : 0.8,
    verified: summary.verified,
  };
}

function inferCategory(skill: BackendSkill): string {
  const text = [skill.name, skill.description, ...(skill.triggers || [])]
    .join(" ")
    .toLowerCase();

  if (
    text.includes("email") ||
    text.includes("customer") ||
    text.includes("support")
  ) {
    return "Communication";
  }

  if (
    text.includes("report") ||
    text.includes("excel") ||
    text.includes("spreadsheet")
  ) {
    return "Technical Reports";
  }

  if (
    text.includes("file") ||
    text.includes("folder") ||
    text.includes("project")
  ) {
    return "File Management";
  }

  return "General";
}

/**
 * Normalize POST /skills/search.
 *
 * Backend response:
 *
 * {
 *   query: string,
 *   results: [
 *     {
 *       skill_id: string,
 *       name: string,
 *       similarity: number,
 *       skill: BackendSkill
 *     }
 *   ]
 * }
 */
export function normalizeSkillSearchResponse(
  response: SkillSearchResponse,
): NormalizedSkillMatch[] {
  if (!response || !Array.isArray(response.results)) {
    return [];
  }

  return response.results
    .filter((item) => item && item.skill)
    .map((item) => {
      const skill = adaptBackendSkillToCanonical(item.skill);

      return {
        skill,
        similarity: item.similarity,
        similarityPercent: Math.round(item.similarity * 100),
      };
    });
}
