import { CanonicalSkill } from '../types/skill';
import { VerificationResult } from '../types/verification';
import { ActivityEvent, MemoryItem } from '../types/activity';
import { TaskExecutionResult } from '../types/agent';

export const MOCK_SKILLS: CanonicalSkill[] = [
  {
    id: 'skill_001',
    name: 'refund_processing',
    displayName: 'Refund Processing',
    description: 'Autonomous customer support workflow for returns, purchase windows, and clearance exceptions.',
    category: 'Customer Support',
    version: 'v1.1',
    confidence: 0.92,
    lastVerified: 'Today',
    rules: [
      { id: 'r1', condition: 'Refund within 7 days', action: 'approve', rawText: 'Refund within 7 days → approve' },
      { id: 'r2', condition: 'Clearance products', action: 'reject', rawText: 'Clearance → reject' },
      { id: 'r3', condition: 'Damaged product verified', action: 'approve', rawText: 'Damaged product → approve' }
    ],
    examples: [
      { id: 'ex1', input: 'Product purchased 3 days ago', output: 'APPROVE' },
      { id: 'ex2', input: 'Clearance product purchased 15 days ago', output: 'REJECT' },
      { id: 'ex3', input: 'Damaged clearance product purchased 4 days ago', output: 'APPROVE' }
    ],
    exceptions: [
      { id: 'exc1', condition: 'Damaged product condition', override: 'Overrides clearance rule', rawText: 'Damaged products override clearance rule' }
    ]
  },
  {
    id: 'skill_002',
    name: 'report_formatting',
    displayName: 'Report Formatting',
    description: 'Extracts tabular figures, calculates variance, and compiles markdown executive digests.',
    category: 'Technical Reports',
    version: 'v1.0',
    confidence: 0.87,
    lastVerified: 'Yesterday',
    rules: [
      { id: 'r2-1', condition: 'Raw CSV upload', action: 'deduplicate & aggregate', rawText: 'Deduplicate rows & compute column sums' },
      { id: 'r2-2', condition: 'Variance > 15%', action: 'flag for review', rawText: 'Flag variance > 15%' }
    ],
    examples: [
      { id: 'ex2-1', input: 'Monthly pipeline CSV with 240 rows', output: 'Formatted Executive Markdown Digest' }
    ],
    exceptions: []
  },
  {
    id: 'skill_003',
    name: 'email_workflow',
    displayName: 'Email Workflow',
    description: 'Inbound communication triage, urgency scoring, and automated account executive assignment.',
    category: 'Communication',
    version: 'v2.1',
    confidence: 0.94,
    lastVerified: '2 days ago',
    rules: [
      { id: 'r3-1', condition: 'Enterprise lead inquiry', action: 'route to Tier 1 AE', rawText: 'Enterprise lead → assign Tier 1 AE' },
      { id: 'r3-2', condition: 'Churn risk signal', action: 'notify CS Director', rawText: 'Urgent churn indicator → alert CS Director' }
    ],
    examples: [
      { id: 'ex3-1', input: 'Inquiry from Fortune 500 CTO', output: 'Tier 1 Priority Routed' }
    ],
    exceptions: [
      { id: 'exc3-1', condition: 'Weekend inbound', override: 'Hold for Monday 8 AM dispatch' }
    ]
  }
];

export const MOCK_ACTIVITIES: ActivityEvent[] = [
  {
    id: 'act-1',
    type: 'skill_learned',
    skillId: 'skill_001',
    skillName: 'Refund Processing',
    description: 'Learned "Refund Processing"',
    timestamp: '2 minutes ago'
  },
  {
    id: 'act-2',
    type: 'correction_added',
    skillId: 'skill_001',
    skillName: 'Refund Processing',
    description: 'Correction added to Refund Processing',
    timestamp: '4 minutes ago'
  },
  {
    id: 'act-3',
    type: 'skill_verified',
    skillId: 'skill_001',
    skillName: 'Refund Processing',
    description: 'Verification completed (5/5 tests passed)',
    timestamp: '12 minutes ago'
  },
  {
    id: 'act-4',
    type: 'skill_reused',
    skillId: 'skill_001',
    skillName: 'Refund Processing',
    description: 'Autonomous execution completed (APPROVE)',
    timestamp: '28 minutes ago'
  }
];

export const MOCK_MEMORY_ITEMS: MemoryItem[] = [
  {
    id: 'mem-1',
    skillId: 'skill_001',
    skillName: 'Refund Processing',
    version: 'v1.1',
    category: 'Customer Support',
    rulesCount: 3,
    exceptionsCount: 1,
    examplesCount: 3,
    lastUpdated: 'Today',
    recentCorrection: 'Damaged products override the standard clearance restriction.'
  },
  {
    id: 'mem-2',
    skillId: 'skill_002',
    skillName: 'Report Formatting',
    version: 'v1.0',
    category: 'Technical Reports',
    rulesCount: 2,
    exceptionsCount: 0,
    examplesCount: 1,
    lastUpdated: 'Yesterday'
  },
  {
    id: 'mem-3',
    skillId: 'skill_003',
    skillName: 'Email Workflow',
    version: 'v2.1',
    category: 'Communication',
    rulesCount: 2,
    exceptionsCount: 1,
    examplesCount: 1,
    lastUpdated: '2 days ago'
  }
];

export const INITIAL_VERIFICATION_RESULT_V1_0: VerificationResult = {
  skillId: 'skill_001',
  skillName: 'Refund Processing',
  version: 'v1.0',
  score: {
    total: 5,
    passed: 4,
    failed: 1,
    accuracy: 80
  },
  testCases: [
    {
      id: 'tc-1',
      input: 'Product purchased 3 days ago.',
      expected: 'APPROVE',
      actual: 'APPROVE',
      status: 'PASSED',
      reason: 'Within 7-day refund window.'
    },
    {
      id: 'tc-2',
      input: 'Clearance product purchased 15 days ago.',
      expected: 'REJECT',
      actual: 'REJECT',
      status: 'PASSED',
      reason: 'Clearance products are non-refundable.'
    },
    {
      id: 'tc-3',
      input: 'Regular product purchased 12 days ago.',
      expected: 'REJECT',
      actual: 'REJECT',
      status: 'PASSED',
      reason: 'Outside 7-day refund window.'
    },
    {
      id: 'tc-4',
      input: 'Unopened accessory purchased 2 days ago.',
      expected: 'APPROVE',
      actual: 'APPROVE',
      status: 'PASSED',
      reason: 'Within 7-day refund window.'
    },
    {
      id: 'tc-5',
      input: 'Clearance product purchased 2 days ago and arrived damaged.',
      expected: 'APPROVE',
      actual: 'REJECT',
      status: 'FAILED',
      reason: 'Clearance restriction triggered before damage check.'
    }
  ],
  lastRunAt: 'Just now'
};

export const VERIFICATION_RESULT_V1_1: VerificationResult = {
  skillId: 'skill_001',
  skillName: 'Refund Processing',
  version: 'v1.1',
  score: {
    total: 5,
    passed: 5,
    failed: 0,
    accuracy: 100
  },
  testCases: [
    {
      id: 'tc-1',
      input: 'Product purchased 3 days ago.',
      expected: 'APPROVE',
      actual: 'APPROVE',
      status: 'PASSED',
      reason: 'Within 7-day refund window.'
    },
    {
      id: 'tc-2',
      input: 'Clearance product purchased 15 days ago.',
      expected: 'REJECT',
      actual: 'REJECT',
      status: 'PASSED',
      reason: 'Clearance products are non-refundable.'
    },
    {
      id: 'tc-3',
      input: 'Regular product purchased 12 days ago.',
      expected: 'REJECT',
      actual: 'REJECT',
      status: 'PASSED',
      reason: 'Outside 7-day refund window.'
    },
    {
      id: 'tc-4',
      input: 'Unopened accessory purchased 2 days ago.',
      expected: 'APPROVE',
      actual: 'APPROVE',
      status: 'PASSED',
      reason: 'Within 7-day refund window.'
    },
    {
      id: 'tc-5',
      input: 'Clearance product purchased 2 days ago and arrived damaged.',
      expected: 'APPROVE',
      actual: 'APPROVE',
      status: 'PASSED',
      reason: 'Damaged-product exception overrides clearance restriction.'
    }
  ],
  lastRunAt: 'Just now'
};

export const MOCK_TASK_EXECUTION_RESULT: TaskExecutionResult = {
  decision: 'APPROVE',
  reason: 'Damaged-product exception overrides the standard clearance restriction.',
  skillUsed: {
    id: 'skill_001',
    name: 'refund_processing',
    displayName: 'Refund Processing',
    version: 'v1.1'
  },
  similarity: 0.94,
  confidence: 0.92,
  appliedRules: [
    'Check purchase date (within 7 days)',
    'Check clearance product status',
    'Evaluate damaged-product exception'
  ],
  exceptionsChecked: [
    'Damaged products override clearance restriction (ACTIVE)'
  ],
  overrideApplied: true,
  timeline: [
    { stage: 'searching_memory', label: 'Searching Skill Memory', status: 'completed', detail: 'Query matched "refund_processing"' },
    { stage: 'found_skill', label: 'Found relevant skill', status: 'completed', detail: 'Refund Processing (Similarity: 0.94)' },
    { stage: 'applying_rules', label: 'Applying learned rules', status: 'completed', detail: '3 rules evaluated' },
    { stage: 'checking_exceptions', label: 'Checking exceptions', status: 'completed', detail: 'Damaged-product exception applied' },
    { stage: 'complete', label: 'Result', status: 'completed', detail: 'APPROVE ✓' }
  ]
};
