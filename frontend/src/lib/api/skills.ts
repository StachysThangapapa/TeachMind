import { apiClient, IS_MOCK_MODE } from './client';
import {
  CanonicalSkill,
  SkillSearchRequest,
  SkillSearchResponse,
  TeachSkillRequest,
  TeachSkillResponse
} from '../types/skill';
import {
  normalizeSkillSearchResponse,
  NormalizedSkillMatch
} from '../adapters/skillAdapter';
import { MOCK_SKILLS } from './mockData';

// Local storage cache for mock skills so user teachings persist across views in mock mode
const MOCK_STORAGE_KEY = 'teachmind_mock_skills_v2';

function getStoredMockSkills(): CanonicalSkill[] {
  if (typeof window === 'undefined') return MOCK_SKILLS;
  try {
    const raw = localStorage.getItem(MOCK_STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {}
  return MOCK_SKILLS;
}

function saveStoredMockSkills(skills: CanonicalSkill[]) {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(MOCK_STORAGE_KEY, JSON.stringify(skills));
  } catch {}
}

export async function searchSkills(
  query: string,
  topK = 3
): Promise<NormalizedSkillMatch[]> {
  if (IS_MOCK_MODE) {
    // Return mock search results matching query
    const skills = getStoredMockSkills();
    const q = query.toLowerCase();

    const matches = skills.map((skill) => {
      let sim = 0.65;
      if (skill.name.toLowerCase().includes(q) || skill.displayName.toLowerCase().includes(q)) {
        sim = 0.94;
      } else if (skill.description.toLowerCase().includes(q) || skill.category.toLowerCase().includes(q)) {
        sim = 0.88;
      } else if (q.includes('damaged') || q.includes('clearance') || q.includes('refund')) {
        sim = skill.name === 'refund_processing' ? 0.94 : 0.72;
      }

      return {
        skill,
        similarity: sim,
        similarityPercent: Math.round(sim * 100)
      };
    });

    matches.sort((a, b) => b.similarity - a.similarity);
    return matches.slice(0, topK);
  }

  // Real backend call: POST /skills/search
  const payload: SkillSearchRequest = { query, top_k: topK };
  const response = await apiClient<SkillSearchResponse>('/skills/search', {
    method: 'POST',
    body: JSON.stringify(payload)
  });

  return normalizeSkillSearchResponse(response);
}

export async function getSkills(): Promise<CanonicalSkill[]> {
  if (IS_MOCK_MODE) {
    return getStoredMockSkills();
  }

  return apiClient<CanonicalSkill[]>('/skills', { method: 'GET' });
}

export async function getSkillById(id: string): Promise<CanonicalSkill | null> {
  if (IS_MOCK_MODE) {
    const skills = getStoredMockSkills();
    return skills.find((s) => s.id === id) || skills[0] || null;
  }

  return apiClient<CanonicalSkill>(`/skills/${id}`, { method: 'GET' });
}

export async function teachSkill(
  request: TeachSkillRequest
): Promise<TeachSkillResponse> {
  if (IS_MOCK_MODE) {
    // Parse simulated skill from input
    const title = request.name || 'Refund Processing';
    const isRefund = request.input.toLowerCase().includes('refund') || request.input.toLowerCase().includes('clearance');

    const detectedSkill: CanonicalSkill = {
      id: `skill_${Date.now()}`,
      name: title.toLowerCase().replace(/\s+/g, '_'),
      displayName: title,
      description: request.input.slice(0, 120) + (request.input.length > 120 ? '...' : ''),
      category: request.category || (isRefund ? 'Customer Support' : 'Operations'),
      version: 'v1.0',
      confidence: 0.92,
      lastVerified: 'Just now',
      rules: isRefund
        ? [
            { id: 'r1', condition: 'Check purchase date', action: 'verify within 7 days', rawText: 'Check purchase date' },
            { id: 'r2', condition: 'Apply 7-day rule', action: 'approve if within window', rawText: 'Apply 7-day rule' },
            { id: 'r3', condition: 'Check product type', action: 'reject clearance items', rawText: 'Check product type' },
            { id: 'r4', condition: 'Handle damaged products', action: 'approve exception', rawText: 'Handle damaged products' }
          ]
        : [
            { id: 'r1', condition: 'Extract input parameters', action: 'validate payload', rawText: 'Extract input parameters' },
            { id: 'r2', condition: 'Execute business workflow', action: 'transform data', rawText: 'Execute business workflow' },
            { id: 'r3', condition: 'Validate constraints', action: 'ensure safety checks', rawText: 'Validate constraints' }
          ],
      examples: [
        { id: 'ex1', input: 'Sample case: standard purchase with receipt', output: 'APPROVE' },
        { id: 'ex2', input: 'Sample case: clearance purchase after 14 days', output: 'REJECT' }
      ],
      exceptions: isRefund
        ? [{ id: 'exc1', condition: 'Damaged item', override: 'Overrides clearance restriction', rawText: 'Damaged products override clearance restriction' }]
        : []
    };

    return {
      skill: detectedSkill,
      detected_rules_count: detectedSkill.rules.length,
      captured_examples_count: detectedSkill.examples.length,
      message: 'Skill successfully analyzed and extracted.'
    };
  }

  return apiClient<TeachSkillResponse>('/skills/teach', {
    method: 'POST',
    body: JSON.stringify(request)
  });
}

export async function saveSkill(skill: CanonicalSkill): Promise<CanonicalSkill> {
  if (IS_MOCK_MODE) {
    const existing = getStoredMockSkills();
    const filtered = existing.filter((s) => s.id !== skill.id);
    const updated = [skill, ...filtered];
    saveStoredMockSkills(updated);
    return skill;
  }

  return apiClient<CanonicalSkill>('/skills', {
    method: 'POST',
    body: JSON.stringify(skill)
  });
}
