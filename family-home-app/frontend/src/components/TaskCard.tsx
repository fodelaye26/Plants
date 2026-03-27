import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { borderRadius, colors, shadows, spacing, typography } from '../theme';
import { Task, TaskCategory } from '../types';

const CATEGORY_EMOJI: Record<TaskCategory, string> = {
  kitchen: '🍳',
  dining_room: '🍽️',
  living_room: '🛋️',
  master_bedroom: '🛏️',
  master_bathroom: '🚿',
  bathroom: '🪥',
  office: '💻',
  stairwell: '🪜',
  outdoor: '🌿',
  general: '📋',
};

const CATEGORY_COLOR: Record<TaskCategory, string> = {
  kitchen: colors.kitchen,
  dining_room: '#FFB347',
  living_room: '#FF8B8B',
  master_bedroom: colors.bedtime,
  master_bathroom: colors.laundry,
  bathroom: '#87CEEB',
  office: '#8BB8FF',
  stairwell: '#AEB6BF',
  outdoor: colors.outdoor,
  general: colors.cleaning,
};

interface TaskCardProps {
  task: Task;
  onComplete: (taskId: number) => void;
}

export default function TaskCard({ task, onComplete }: TaskCardProps) {
  const isDone = task.status === 'done';
  const categoryColor = CATEGORY_COLOR[task.category] || colors.primary;
  const emoji = CATEGORY_EMOJI[task.category] || '📌';

  return (
    <View style={[styles.card, isDone && styles.cardDone]}>
      <View style={[styles.categoryStripe, { backgroundColor: categoryColor }]} />
      <View style={styles.content}>
        <View style={styles.header}>
          <Text style={styles.emoji}>{emoji}</Text>
          <View style={styles.titleArea}>
            <Text style={[styles.title, isDone && styles.titleDone]}>{task.title}</Text>
            {task.assigned_to && (
              <Text style={styles.assignee}>{task.assigned_to}</Text>
            )}
          </View>
          {task.points > 0 && (
            <View style={styles.pointsBadge}>
              <Text style={styles.pointsText}>+{task.points}</Text>
            </View>
          )}
        </View>
        <View style={styles.footer}>
          {task.due_date && (
            <Text style={styles.dueDate}>{task.due_date}</Text>
          )}
          {task.time_window !== 'anytime' && (
            <View style={styles.timeTag}>
              <Text style={styles.timeTagText}>{task.time_window.replace('_', ' ')}</Text>
            </View>
          )}
          <View style={{ flex: 1 }} />
          {!isDone && (
            <Pressable
              style={({ pressed }) => [styles.doneButton, pressed && styles.doneButtonPressed]}
              onPress={() => onComplete(task.id)}
            >
              <Text style={styles.doneButtonText}>Done ✓</Text>
            </Pressable>
          )}
          {isDone && (
            <View style={styles.completedBadge}>
              <Text style={styles.completedText}>Completed ✓</Text>
            </View>
          )}
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    marginBottom: spacing.md,
    overflow: 'hidden',
    ...shadows.card,
  },
  cardDone: {
    opacity: 0.6,
  },
  categoryStripe: {
    width: 5,
  },
  content: {
    flex: 1,
    padding: spacing.md,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  emoji: {
    fontSize: 24,
    marginRight: spacing.sm,
  },
  titleArea: {
    flex: 1,
  },
  title: {
    ...typography.body,
    fontWeight: '600',
  },
  titleDone: {
    textDecorationLine: 'line-through',
    color: colors.textLight,
  },
  assignee: {
    ...typography.caption,
    marginTop: 2,
  },
  pointsBadge: {
    backgroundColor: colors.warning,
    borderRadius: borderRadius.full,
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
  },
  pointsText: {
    fontSize: 12,
    fontWeight: '700',
    color: colors.text,
  },
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  dueDate: {
    ...typography.caption,
    fontSize: 12,
  },
  timeTag: {
    backgroundColor: colors.surfaceWarm,
    borderRadius: borderRadius.sm,
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
  },
  timeTagText: {
    ...typography.caption,
    fontSize: 11,
    textTransform: 'capitalize',
  },
  doneButton: {
    backgroundColor: colors.accent,
    borderRadius: borderRadius.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  doneButtonPressed: {
    backgroundColor: colors.accentDark,
  },
  doneButtonText: {
    color: '#FFFFFF',
    fontWeight: '600',
    fontSize: 14,
  },
  completedBadge: {
    backgroundColor: colors.accentLight,
    borderRadius: borderRadius.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  completedText: {
    color: colors.accentDark,
    fontWeight: '600',
    fontSize: 13,
  },
});
