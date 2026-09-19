export type ActivityEventType =
  | 'skill_learned'
  | 'skill_verified'
  | 'correction_added'
  | 'skill_reused'
  | 'version_updated';

export interface ActivityEvent {
  id: string;
  type: ActivityEventType;
  skillId?: string;
  skillName: string;
  description: string;
  timestamp: string;
  meta?: {
    version?: string;
    score?: string;
    similarity?: number;
    decision?: string;
  };
}

export interface MemoryItem {
  id: string;
  skillId: string;
  skillName: string;
  version: string;
  category: string;
  rulesCount: number;
  exceptionsCount: number;
  examplesCount: number;
  lastUpdated: string;
  recentCorrection?: string;
}
