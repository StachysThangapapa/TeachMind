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
    const steps: ExecutionTimelineStep[] = [
      {
        stage: 'searching_memory',
        label: 'Searching Skill Memory (Mock)',
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

    for (let i = 0; i < steps.length; i++) {
      if (onTimelineUpdate) {
        steps[i].status = 'active';
        onTimelineUpdate({ ...steps[i] });
      }
      await new Promise((res) => setTimeout(res, 400));
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

    return {
      ...MOCK_TASK_EXECUTION_RESULT,
      decision: 'APPROVE',
      reason: 'Standard workflow execution approved.',
      similarity: 0.91,
      confidence: 0.90,
      overrideApplied: false
    };
  }

  // Initial timeline notification
  if (onTimelineUpdate) {
    onTimelineUpdate({
      stage: 'searching_memory',
      label: 'Searching Skill Memory (pgvector)',
      status: 'active',
      detail: `Calling unified backend /agent/execute for "${request.query}"...`
    });
  }

  try {
    const raw = await apiClient<any>('/agent/execute', {
      method: 'POST',
      body: JSON.stringify(request)
    });

    // Stream backend timeline steps if provided
    if (Array.isArray(raw.timeline) && onTimelineUpdate) {
      raw.timeline.forEach((step: ExecutionTimelineStep) => {
        onTimelineUpdate(step);
      });
    }

    const skillObj = raw.skill_used || {};
    const appliedRules: string[] = (skillObj.rules || []).map((r: any) =>
      typeof r === 'string' ? r : `${r.condition || ''} → ${r.action || ''}`.trim()
    );
    const exceptionsChecked: string[] = (skillObj.exceptions || []).map((e: any) =>
      typeof e === 'string' ? e : e.condition || ''
    );

    const displayName = skillObj.name
      ? skillObj.name.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase())
      : 'General Assistant Task';

    return {
      decision: (raw.decision === 'PROCESSED' || raw.decision === 'APPROVE') ? 'APPROVE' : (raw.decision || 'PROCESSED'),
      reason: raw.message || raw.reason || 'Task executed successfully.',
      skillUsed: {
        id: skillObj.id || raw.action_id || 'skill_generic',
        name: skillObj.name || 'generic_task',
        displayName: displayName,
        version: skillObj.version ? (skillObj.version.startsWith('v') ? skillObj.version : `v${skillObj.version}`) : 'v1.0'
      },
      similarity: typeof raw.similarity === 'number' ? raw.similarity : 0.0,
      confidence: typeof raw.confidence === 'number' ? raw.confidence : 0.90,
      appliedRules: appliedRules,
      exceptionsChecked: exceptionsChecked,
      overrideApplied: Boolean(raw.personalization && Object.keys(raw.personalization).length > 0),
      timeline: raw.timeline || []
    };
  } catch (err: unknown) {
    if (onTimelineUpdate) {
      onTimelineUpdate({
        stage: 'error',
        label: 'Agent Execution Failed',
        status: 'failed',
        detail: (err as Error)?.message || 'Failed to communicate with unified backend.'
      });
    }
    throw err;
  }
}
