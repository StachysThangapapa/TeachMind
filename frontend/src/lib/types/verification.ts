export interface TestCase {
  id: string;
  input: string;
  expected: 'APPROVE' | 'REJECT' | 'ESCALATE';
  actual?: 'APPROVE' | 'REJECT' | 'ESCALATE';
  status: 'PASSED' | 'FAILED' | 'PENDING';
  reason?: string;
}

export interface VerificationScore {
  total: number;
  passed: number;
  failed: number;
  accuracy: number; // 0 to 100
}

export interface VerificationResult {
  skillId: string;
  skillName: string;
  version: string;
  score: VerificationScore;
  testCases: TestCase[];
  lastRunAt: string;
}

export interface CorrectionRequest {
  skillId: string;
  failedTestCaseId?: string;
  inputContext?: string;
  mistakeDescription: string;
  userCorrection: string;
}

export interface CorrectionResponse {
  skillId: string;
  skillName: string;
  previousVersion: string;
  newVersion: string;
  newExceptionLearned: string;
  updatedRulesCount: number;
  message: string;
  updatedAt: string;
}
