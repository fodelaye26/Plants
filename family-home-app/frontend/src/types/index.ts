export type TaskStatus = 'not_started' | 'in_progress' | 'done' | 'archived' | 'skipped';
export type TaskMode = 'adult' | 'kid' | 'family';
export type TaskSource = 'tasks' | 'chores' | 'manual';
export type TaskCategory =
  | 'kitchen' | 'dining_room' | 'living_room'
  | 'master_bedroom' | 'master_bathroom' | 'bathroom'
  | 'office' | 'stairwell' | 'outdoor' | 'general';
export type TimeWindow = 'morning' | 'after_school' | 'evening' | 'anytime';
export type Recurrence = 'daily' | 'weekly' | 'bi_weekly' | 'monthly' | 'seasonally' | 'semi_annually' | 'annually' | 'once';
export type Priority = 'low' | 'medium' | 'high';
export type MemberRole = 'adult' | 'kid';
export type ReminderTone = 'calm' | 'playful' | 'coach';

export interface Task {
  id: number;
  notion_id?: string;
  source: TaskSource;
  title: string;
  assigned_to?: string;
  mode: TaskMode;
  category: TaskCategory;
  status: TaskStatus;
  priority: Priority;
  recurrence: Recurrence;
  due_date?: string;
  time_window: TimeWindow;
  project_name?: string;
  rooms?: string;  // JSON array of room names
  difficulty: number;
  points: number;
  kid_friendly: boolean;
  needs_parent_help: boolean;
  icon_key?: string;
  voice_prompt_url?: string;
  active: boolean;
  last_completed?: string;
  created_at?: string;
  updated_at?: string;
}

export interface FamilyMember {
  id: number;
  notion_id?: string;
  name: string;
  role: MemberRole;
  avatar?: string;
  color_theme: string;
  points_total: number;
  level: number;
  created_at?: string;
}

export interface Reminder {
  message: string;
  tone: ReminderTone;
  time_window: TimeWindow;
  task_count: number;
}

export interface FamilyBoard {
  [memberName: string]: Task[];
}
