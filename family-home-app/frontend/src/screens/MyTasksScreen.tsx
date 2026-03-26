import React, { useCallback, useEffect, useState } from 'react';
import { FlatList, RefreshControl, StyleSheet, Text, View } from 'react-native';
import TaskCard from '../components/TaskCard';
import { completeTask as apiCompleteTask, getTasks } from '../services/api';
import { colors, spacing, typography } from '../theme';
import { Task } from '../types';

export default function MyTasksScreen() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  // TODO: Replace with actual current user from auth/settings
  const currentUser: string | undefined = undefined;

  const loadTasks = useCallback(async () => {
    try {
      const data = await getTasks(currentUser);
      setTasks(data);
    } catch {
      // Handle silently
    }
  }, [currentUser]);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadTasks();
    setRefreshing(false);
  }, [loadTasks]);

  const handleComplete = useCallback(async (taskId: number) => {
    try {
      await apiCompleteTask(taskId);
      setTasks(prev => prev.map(t => t.id === taskId ? { ...t, status: 'done' as const } : t));
    } catch {
      // Handle error
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
            <Text style={styles.title}>My Tasks</Text>
            <Text style={styles.subtitle}>
              {pendingTasks.length} open · {doneTasks.length} completed
            </Text>
          </View>
        }
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text style={styles.emptyIcon}>✨</Text>
            <Text style={styles.emptyText}>All clear!</Text>
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
  title: {
    ...typography.title,
    marginBottom: spacing.xs,
  },
  subtitle: {
    ...typography.caption,
    marginBottom: spacing.lg,
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
});
