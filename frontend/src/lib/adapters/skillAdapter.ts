import {
  CanonicalSkill,
  SkillSearchResponse,
  SkillSearchResultItem,
  BackendSkillPayload
} from '../types/skill';

/**
 * Normalizes an AI Agent / Backend search response into a stable frontend list of CanonicalSkills
 * along with similarity rankings.
 */
export interface NormalizedSkillMatch {
  skill: CanonicalSkill;
  similarity: number;
  similarityPercent: number; // e.g. 94 for 0.94
}

export function adaptBackendSkillToCanonical(
  skillId: string,
  name: string,
  payload: BackendSkillPayload,
  version = '1.0',
  confidence = 0.9
): CanonicalSkill {
  const formatName = (str: string) => {
    return str
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (c) => c.toUpperCase());
  };

  return {
    id: skillId,
    name: name,
    displayName: formatName(name),
    description: payload.description || `Workflow for ${formatName(name)}`,
    category: 'Workflow Automation',
    rules: (payload.rules || []).map((r, i) => ({
      id: `rule-${i + 1}`,
      condition: r.condition,
      action: r.action,
      rawText: `${r.condition} → ${r.action}`
    })),
    examples: (payload.examples || []).map((ex, i) => {
      if (typeof ex === 'string') {
        return { id: `ex-${i + 1}`, input: ex };
      }
      return { id: `ex-${i + 1}`, input: ex.input, output: ex.output };
    }),
    exceptions: (payload.exceptions || []).map((exc, i) => ({
      id: `exc-${i + 1}`,
      condition: exc,
      override: 'Override standard restriction',
      rawText: exc
    })),
    version: version,
    confidence: confidence,
    lastVerified: 'Recently'
  };
}

export function normalizeSkillSearchResponse(
  response: SkillSearchResponse
): NormalizedSkillMatch[] {
  if (!response || !Array.isArray(response.results)) {
    return [];
  }

  return response.results.map((item: SkillSearchResultItem) => {
    const canonical = adaptBackendSkillToCanonical(
      item.skill_id,
      item.name,
      item.skill,
      '1.1',
      Math.min(0.99, Math.max(0.7, item.similarity || 0.9))
    );

    const sim = typeof item.similarity === 'number' ? item.similarity : 0.92;

    return {
      skill: canonical,
      similarity: sim,
      similarityPercent: Math.round(sim * 100)
    };
  });
}
