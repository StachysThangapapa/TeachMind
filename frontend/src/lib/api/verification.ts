import { apiClient, IS_MOCK_MODE } from './client';
import {
  VerificationResult,
  CorrectionRequest,
  CorrectionResponse
} from '../types/verification';
import {
  INITIAL_VERIFICATION_RESULT_V1_0,
  VERIFICATION_RESULT_V1_1
} from './mockData';

const VERIFICATION_STORAGE_KEY = 'teachmind_verification_state_v2';

function isSkillCorrected(): boolean {
  if (typeof window === 'undefined') return false;
  return localStorage.getItem(VERIFICATION_STORAGE_KEY) === 'corrected';
}

function setSkillCorrectedState(corrected: boolean) {
  if (typeof window === 'undefined') return;
  localStorage.setItem(VERIFICATION_STORAGE_KEY, corrected ? 'corrected' : 'initial');
}

export async function getVerification(skillId: string): Promise<VerificationResult> {
  if (IS_MOCK_MODE) {
    return isSkillCorrected() ? VERIFICATION_RESULT_V1_1 : INITIAL_VERIFICATION_RESULT_V1_0;
  }

  // There's no specific /verification GET in the backend that returns test cases yet,
  // it just returns the skill. We will mock the test case results for the demo using the real skill's version.
  const skill = await apiClient<any>(`/skills/${skillId}`, { method: 'GET' });
  const isV2 = skill.version > 1;
  return isV2 ? VERIFICATION_RESULT_V1_1 : INITIAL_VERIFICATION_RESULT_V1_0;
}

export async function runVerification(skillId: string): Promise<VerificationResult> {
  if (IS_MOCK_MODE) {
    // Simulate test run delay
    await new Promise((res) => setTimeout(res, 800));
    return isSkillCorrected() ? VERIFICATION_RESULT_V1_1 : INITIAL_VERIFICATION_RESULT_V1_0;
  }

  // Hit the actual verify endpoint
  const skill = await apiClient<any>(`/skills/${skillId}/verify`, {
    method: 'PATCH'
  });
  
  const isV2 = skill.version > 1;
  return isV2 ? VERIFICATION_RESULT_V1_1 : INITIAL_VERIFICATION_RESULT_V1_0;
}

export async function submitCorrection(
  request: CorrectionRequest
): Promise<CorrectionResponse> {
  if (IS_MOCK_MODE) {
    // Simulate learning the new exception and updating version
    await new Promise((res) => setTimeout(res, 600));
    setSkillCorrectedState(true);

    return {
      skillId: request.skillId,
      skillName: 'Refund Processing',
      previousVersion: 'v1.0',
      newVersion: 'v1.1',
      newExceptionLearned:
        request.userCorrection || 'Damaged products override the standard clearance restriction.',
      updatedRulesCount: 4,
      message: 'Understanding updated. New exception registered in skill memory.',
      updatedAt: 'Just now'
    };
  }

  // Real backend correction via PATCH
  // Fetch the current skill to retain existing rules
  let updatedRules = [{ condition: request.mistakeDescription || "User Correction", action: request.userCorrection }];
  try {
    const current = await apiClient<any>(`/skills/${request.skillId}`, { method: 'GET' });
    if (current && Array.isArray(current.rules)) {
      updatedRules = [...current.rules, { condition: request.mistakeDescription || "User Correction", action: request.userCorrection }];
    }
  } catch {
    // If fetch fails, proceed with the new rule
  }

  const skill = await apiClient<any>(`/skills/${request.skillId}`, {
    method: 'PATCH',
    body: JSON.stringify({
      rules: updatedRules
    })
  });
  
  return {
    skillId: skill.skill_id,
    skillName: skill.name,
    previousVersion: `v${Math.max(1, skill.version - 1)}.0`,
    newVersion: `v${skill.version}.0`,
    newExceptionLearned: request.userCorrection,
    updatedRulesCount: skill.rules.length,
    message: 'Understanding updated. New exception registered in skill memory.',
    updatedAt: new Date().toISOString()
  };
}

export function resetVerificationDemoState() {
  setSkillCorrectedState(false);
}
