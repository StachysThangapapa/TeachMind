import { apiClient, IS_MOCK_MODE } from './client';
import {
  TaskExecutionRequest,
  TaskExecutionResult,
  ExecutionTimelineStep
} from '../types/agent';
import { MOCK_TASK_EXECUTION_RESULT } from './mockData';

export async function executeTask(
  request: TaskExecutionRequest,
  onTimelineUpdate?: (step: ExecutionTimelineStep) => void
): Promise<TaskExecutionResult> {
  if (IS_MOCK_MODE) {
    // Simulate real step-by-step reasoning timeline
    const steps: ExecutionTimelineStep[] = [
      {
        stage: 'searching_memory',
        label: 'Searching Skill Memory',
        status: 'active',
        detail: `Evaluating query against indexed skills...`
      },
      {
        stage: 'found_skill',
        label: 'Found relevant skill',
        status: 'pending',
        detail: 'Refund Processing (Similarity: 0.94)'
      },
      {
        stage: 'applying_rules',
        label: 'Applying learned rules',
        status: 'pending',
        detail: 'Evaluating 7-day policy & product classification'
      },
      {
        stage: 'checking_exceptions',
        label: 'Checking exceptions',
        status: 'pending',
        detail: 'Damaged-product exception check'
      },
      {
        stage: 'complete',
        label: 'Result',
        status: 'pending',
        detail: 'APPROVE ✓'
      }
    ];

    // Emit timeline events progressively
    for (let i = 0; i < steps.length; i++) {
      if (onTimelineUpdate) {
        steps[i].status = 'active';
        onTimelineUpdate({ ...steps[i] });
      }
      await new Promise((res) => setTimeout(res, 500));
      steps[i].status = 'completed';
      if (onTimelineUpdate) {
        onTimelineUpdate({ ...steps[i] });
      }
    }

    const q = request.query.toLowerCase();
    const isDamagedClearance = q.includes('damaged') && q.includes('clearance');

    if (isDamagedClearance) {
      return {
        ...MOCK_TASK_EXECUTION_RESULT,
        decision: 'APPROVE',
        reason: 'Damaged-product exception overrides the standard clearance restriction.',
        similarity: 0.94,
        confidence: 0.92,
        overrideApplied: true
      };
    }

    if (q.includes('clearance')) {
      return {
        ...MOCK_TASK_EXECUTION_RESULT,
        decision: 'REJECT',
        reason: 'Clearance items are marked as final sale and cannot be refunded after standard processing.',
        similarity: 0.91,
        confidence: 0.90,
        overrideApplied: false
      };
    }

    return {
      ...MOCK_TASK_EXECUTION_RESULT,
      decision: 'APPROVE',
      reason: 'Purchase within eligible 7-day return policy with verified customer receipt.',
      similarity: 0.95,
      confidence: 0.94,
      overrideApplied: false
    };
  }

  // Real backend call: POST /agent/execute
  return apiClient<TaskExecutionResult>('/agent/execute', {
    method: 'POST',
    body: JSON.stringify(request)
  });
}
