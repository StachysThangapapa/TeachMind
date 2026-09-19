export type ExecutionTimelineStage =
  | 'idle'
  | 'searching_memory'
  | 'found_skill'
  | 'applying_rules'
  | 'checking_exceptions'
  | 'complete'
  | 'error';

export interface ExecutionTimelineStep {
  stage: ExecutionTimelineStage;
  label: string;
  status: 'pending' | 'active' | 'completed' | 'skipped' | 'failed';
  detail?: string;
  timestamp?: string;
}

export interface TaskExecutionResult {
  decision: 'APPROVE' | 'REJECT' | 'ESCALATE' | 'PROCESSED';
  reason: string;
  skillUsed: {
    id: string;
    name: string;
    displayName: string;
    version: string;
  };
  similarity: number; // e.g. 0.94
  confidence: number; // e.g. 0.92
  appliedRules: string[];
  exceptionsChecked: string[];
  overrideApplied?: boolean;
  timeline: ExecutionTimelineStep[];
}

export interface TaskExecutionRequest {
  query: string;
  context?: Record<string, unknown>;
  skillIdOverride?: string;
}
