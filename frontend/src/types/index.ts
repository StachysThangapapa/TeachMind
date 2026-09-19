export type SkillStatus = 'Draft' | 'Learning' | 'Verified' | 'Needs Correction';

export type SkillCategory =
  | 'Operations'
  | 'Sales'
  | 'Finance'
  | 'Customer Support'
  | 'Data & Analytics'
  | 'General';

export type TeachingMethod = 'instructions' | 'demonstration' | 'example';

export interface SkillStep {
  id: string;
  order: number;
  title: string;
  description?: string;
  actionType?: 'extract' | 'transform' | 'validate' | 'dispatch' | 'notify';
}

export interface SkillExample {
  id: string;
  input: string;
  output: string;
  notes?: string;
}

export interface DemonstratedAction {
  id: string;
  timestamp: string;
  actionType: 'click' | 'input' | 'select' | 'extract' | 'verify';
  target: string;
  value?: string;
}

export interface Skill {
  id: string;
  title: string;
  description: string;
  category: SkillCategory;
  status: SkillStatus;
  method: TeachingMethod;
  steps: SkillStep[];
  examples: SkillExample[];
  demonstrations: DemonstratedAction[];
  rules: string[];
  edgeCases: string[];
  usageCount: number;
  accuracyRate: number;
  createdAt: string;
  lastTestedAt?: string;
}

export interface TestLog {
  stepIndex: number;
  stepTitle: string;
  message: string;
  timestamp: string;
  status: 'pending' | 'running' | 'success' | 'warning' | 'error';
}

export interface TestRun {
  id: string;
  skillId: string;
  skillTitle: string;
  inputData: Record<string, string>;
  logs: TestLog[];
  resultOutput: string;
  status: 'success' | 'failed' | 'running';
  durationMs: number;
  timestamp: string;
}

export interface Correction {
  id: string;
  skillId: string;
  ruleTarget: string;
  userCorrection: string;
  appliedAt: string;
}

export interface ActivityLog {
  id: string;
  type: 'teach' | 'test' | 'verify' | 'correct' | 'reuse';
  skillId?: string;
  skillTitle: string;
  description: string;
  timestamp: string;
}
