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

  const response = await apiClient<{ skills: any[] }>('/skills', { method: 'GET' });
  if (!response || !Array.isArray(response.skills)) {
    return [];
  }

  // Hydrate each skill summary with full canonical details from PostgreSQL
  const fullSkills = await Promise.all(
    response.skills.map(async (s) => {
      try {
        const full = await getSkillById(s.skill_id);
        if (full) return full;
      } catch {
        // Fallback to summary if detail fetch fails
      }
      return {
        id: s.skill_id,
        name: s.name,
        displayName: s.name.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase()),
        description: '',
        category: 'Workflow Automation',
        rules: [],
        examples: [],
        exceptions: [],
        version: `v${s.version}.0`,
        confidence: s.verified ? 0.95 : 0.8,
        lastVerified: s.verified ? 'Verified' : 'Unverified'
      };
    })
  );

  return fullSkills;
}

export async function getSkillById(id: string): Promise<CanonicalSkill | null> {
  if (IS_MOCK_MODE) {
    const skills = getStoredMockSkills();
    return skills.find((s) => s.id === id) || skills[0] || null;
  }

  // Backend returns full SkillResponse
  const res = await apiClient<any>(`/skills/${id}`, { method: 'GET' });
  if (!res) return null;

  return {
    id: res.skill_id,
    name: res.name,
    displayName: res.name.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase()),
    description: res.description || '',
    category: 'Workflow Automation',
    rules: (res.rules || []).map((r: any, i: number) => ({
      id: `r${i + 1}`,
      condition: r.condition,
      action: r.action,
      rawText: `${r.condition} → ${r.action}`
    })),
    examples: (res.examples || []).map((ex: any, i: number) => ({
      id: `ex${i + 1}`,
      input: ex.input,
      output: ex.expected_behavior
    })),
    exceptions: [],
    version: `v${res.version}.0`,
    confidence: res.verified ? 0.95 : 0.85,
    lastVerified: res.verified ? 'Verified' : 'Unverified'
  };
}

export async function teachSkill(
  request: TeachSkillRequest
): Promise<TeachSkillResponse> {
  if (IS_MOCK_MODE) {
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

  // Real Cohere extraction via backend: POST /skills/extract (30s timeout specifically for LLM extraction)
  const response = await apiClient<{ skill: any }>('/skills/extract', {
    method: 'POST',
    body: JSON.stringify({ text: request.input }),
    timeoutMs: 30000
  });

  const backendSkill = response.skill;
  const canonical: CanonicalSkill = {
    id: backendSkill.skill_id,
    name: backendSkill.name,
    displayName: backendSkill.name.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase()),
    description: backendSkill.description || '',
    category: request.category || 'Workflow Automation',
    version: `v${backendSkill.version}.0`,
    confidence: backendSkill.verified ? 0.95 : 0.90,
    lastVerified: backendSkill.verified ? 'Verified' : 'Extracted',
    rules: (backendSkill.rules || []).map((r: any, i: number) => ({
      id: `rule-${i + 1}`,
      condition: r.condition,
      action: r.action,
      rawText: `${r.condition} → ${r.action}`
    })),
    examples: (backendSkill.examples || []).map((ex: any, i: number) => ({
      id: `ex-${i + 1}`,
      input: ex.input,
      output: ex.expected_behavior || ex.output
    })),
    exceptions: [],
    createdAt: backendSkill.metadata?.created_at,
    updatedAt: backendSkill.metadata?.updated_at
  };

  // Preserve raw triggers and steps for accurate persistence
  (canonical as any).triggers = backendSkill.triggers || [];
  (canonical as any).steps = backendSkill.steps || [];

  return {
    skill: canonical,
    detected_rules_count: canonical.rules.length,
    captured_examples_count: canonical.examples.length,
    message: 'Skill successfully analyzed and extracted via Cohere.'
  };
}

export async function saveSkill(skill: CanonicalSkill): Promise<CanonicalSkill> {
  if (IS_MOCK_MODE) {
    const existing = getStoredMockSkills();
    const filtered = existing.filter((s) => s.id !== skill.id);
    const updated = [skill, ...filtered];
    saveStoredMockSkills(updated);
    return skill;
  }

  const backendPayload = {
    skill_id: skill.id,
    name: skill.name,
    description: skill.description || '',
    triggers: (skill as any).triggers && (skill as any).triggers.length > 0
      ? (skill as any).triggers
      : [skill.name.replace(/_/g, ' '), skill.displayName.toLowerCase()],
    steps: (skill as any).steps && (skill as any).steps.length > 0
      ? (skill as any).steps
      : [{ step: 1, instruction: `Execute ${skill.displayName}` }],
    rules: skill.rules.map((r) => ({ condition: r.condition, action: r.action })),
    examples: skill.examples.map((ex) => ({
      input: ex.input,
      expected_behavior: ex.output || ''
    })),
    version: 1,
    verified: false
  };

  await apiClient<any>('/skills', {
    method: 'POST',
    body: JSON.stringify(backendPayload)
  });

  return skill;
}

export async function getSkillVersions(id: string): Promise<any[]> {
  if (IS_MOCK_MODE) {
    return [
      {
        skill_id: id,
        version: 1,
        name: "Mock Skill",
        description: "Initial version",
        created_at: new Date().toISOString()
      }
    ];
  }
  return apiClient<any[]>(`/skills/${id}/versions`, { method: 'GET' });
}
