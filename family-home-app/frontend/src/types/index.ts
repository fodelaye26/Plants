export type TaskStatus = 'not_started' | 'in_progress' | 'done' | 'skipped';
export type TaskMode = 'adult' | 'kid' | 'family';
export type TaskCategory = 'kitchen' | 'laundry' | 'toys' | 'cleaning' | 'bedtime' | 'school' | 'outdoor' | 'admin';
export type TimeWindow = 'morning' | 'after_school' | 'evening' | 'anytime';
export type Recurrence = 'daily' | 'weekly' | 'monthly' | 'once';
export type MemberRole = 'adult' | 'kid';
export type ReminderTone = 'calm' | 'playful' | 'coach';

export interface Task {
  id: number;
  notion_id?: string;
  title: string;
  assigned_to?: string;
  mode: TaskMode;
  category: TaskCategory;
  status: TaskStatus;
  recurrence: Recurrence;
  due_date?: string;
  time_window: TimeWindow;
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
