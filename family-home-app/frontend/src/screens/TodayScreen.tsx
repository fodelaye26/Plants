import React, { useCallback, useEffect, useState } from 'react';
import { FlatList, RefreshControl, StyleSheet, Text, View } from 'react-native';
import ReminderBanner from '../components/ReminderBanner';
import TaskCard from '../components/TaskCard';
import { completeTask as apiCompleteTask, getReminder, getTodayTasks } from '../services/api';
import { colors, spacing, typography } from '../theme';
import { Reminder, Task } from '../types';

export default function TodayScreen() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [reminder, setReminder] = useState<Reminder | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const [tasksData, reminderData] = await Promise.all([
        getTodayTasks(),
        getReminder(),
      ]);
      setTasks(tasksData);
      setReminder(reminderData);
    } catch {
      // Silently handle — user sees empty state
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  }, [loadData]);

  const handleComplete = useCallback(async (taskId: number) => {
    try {
      await apiCompleteTask(taskId);
      setTasks(prev => prev.map(t => t.id === taskId ? { ...t, status: 'done' as const } : t));
    } catch {
      // Handle error gracefully
    }
  }, []);

  const pendingTasks = tasks.filter(t => t.status !== 'done');
  const doneTasks = tasks.filter(t => t.status === 'done');

  return (
    <View style={styles.container}>
      <FlatList
        data={[...pendingTasks, ...doneTasks]}
        keyExtractor={item => item.id.toString()}
        renderItem={({ item }) => <TaskCard task={item} onComplete={handleComplete} />}
        contentContainerStyle={styles.list}
        ListHeaderComponent={
          <View>
            <Text style={styles.greeting}>Today</Text>
            <ReminderBanner reminder={reminder} />
            {pendingTasks.length > 0 && (
              <Text style={styles.sectionLabel}>
                {pendingTasks.length} task{pendingTasks.length !== 1 ? 's' : ''} remaining
              </Text>
            )}
          </View>
        }
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text style={styles.emptyIcon}>🌻</Text>
            <Text style={styles.emptyText}>Nothing to do right now!</Text>
            <Text style={styles.emptySubtext}>Enjoy your free time.</Text>
          </View>
        }
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary} />}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  list: {
    padding: spacing.lg,
    paddingTop: spacing.xl,
  },
  greeting: {
    ...typography.title,
    marginBottom: spacing.md,
  },
  sectionLabel: {
    ...typography.label,
    marginBottom: spacing.md,
  },
  empty: {
    alignItems: 'center',
    paddingTop: spacing.xxl,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: spacing.md,
  },
  emptyText: {
    ...typography.subtitle,
  },
  emptySubtext: {
    ...typography.caption,
    marginTop: spacing.xs,
  },
});
