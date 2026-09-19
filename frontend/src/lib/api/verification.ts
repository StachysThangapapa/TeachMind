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

  return apiClient<VerificationResult>(`/verification/${skillId}`, { method: 'GET' });
}

export async function runVerification(skillId: string): Promise<VerificationResult> {
  if (IS_MOCK_MODE) {
    // Simulate test run delay
    await new Promise((res) => setTimeout(res, 800));
    return isSkillCorrected() ? VERIFICATION_RESULT_V1_1 : INITIAL_VERIFICATION_RESULT_V1_0;
  }

  return apiClient<VerificationResult>('/verification/run', {
    method: 'POST',
    body: JSON.stringify({ skillId })
  });
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

  return apiClient<CorrectionResponse>(`/skills/${request.skillId}/correct`, {
    method: 'POST',
    body: JSON.stringify(request)
  });
}

export function resetVerificationDemoState() {
  setSkillCorrectedState(false);
}
