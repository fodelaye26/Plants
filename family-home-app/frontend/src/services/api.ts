import { FamilyBoard, FamilyMember, Reminder, ReminderTone, Task } from '../types';

// Set this via EXPO_PUBLIC_API_URL env var or update directly
const BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

// Tasks
export const getTasks = (assignedTo?: string) =>
  request<Task[]>(`/tasks/${assignedTo ? `?assigned_to=${assignedTo}` : ''}`);

export const getTodayTasks = (assignedTo?: string) =>
  request<Task[]>(`/tasks/today${assignedTo ? `?assigned_to=${assignedTo}` : ''}`);

export const getFamilyBoard = () =>
  request<FamilyBoard>('/tasks/board');

export const createTask = (task: Partial<Task>) =>
  request<Task>('/tasks/', { method: 'POST', body: JSON.stringify(task) });

export const updateTask = (taskId: number, updates: Partial<Task>) =>
  request<Task>(`/tasks/${taskId}`, { method: 'PATCH', body: JSON.stringify(updates) });

export const completeTask = (taskId: number) =>
  request<Task>(`/tasks/${taskId}/complete`, { method: 'POST' });

// Family
export const getFamilyMembers = () =>
  request<FamilyMember[]>('/family/');

export const addFamilyMember = (member: Partial<FamilyMember>) =>
  request<FamilyMember>('/family/', { method: 'POST', body: JSON.stringify(member) });

// Reminders
export const getReminder = (member?: string, tone: ReminderTone = 'calm') =>
  request<Reminder>(`/reminders/generate?tone=${tone}${member ? `&member=${member}` : ''}`);

// Sync
export const triggerNotionSync = () =>
  request<{ status: string; created: number; updated: number }>('/sync/notion', { method: 'POST' });
