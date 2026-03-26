import React, { useCallback, useEffect, useState } from 'react';
import { FlatList, RefreshControl, ScrollView, StyleSheet, Text, View } from 'react-native';
import TaskCard from '../components/TaskCard';
import { completeTask as apiCompleteTask, getFamilyBoard } from '../services/api';
import { borderRadius, colors, spacing, typography } from '../theme';
import { FamilyBoard } from '../types';

const MEMBER_COLORS = ['#FF9F6B', '#7EC8B8', '#87CEEB', '#DDA0DD', '#FFD166', '#82E0AA'];

export default function FamilyBoardScreen() {
  const [board, setBoard] = useState<FamilyBoard>({});
  const [refreshing, setRefreshing] = useState(false);

  const loadBoard = useCallback(async () => {
    try {
      const data = await getFamilyBoard();
      setBoard(data);
    } catch {
      // Handle silently
    }
  }, []);

  useEffect(() => {
    loadBoard();
  }, [loadBoard]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadBoard();
    setRefreshing(false);
  }, [loadBoard]);

  const handleComplete = useCallback(async (taskId: number) => {
    try {
      await apiCompleteTask(taskId);
      setBoard(prev => {
        const updated: FamilyBoard = {};
        for (const [member, tasks] of Object.entries(prev)) {
          updated[member] = tasks.map(t =>
            t.id === taskId ? { ...t, status: 'done' as const } : t
          );
        }
        return updated;
      });
    } catch {
      // Handle error
    }
  }, []);

  const members = Object.keys(board);

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary} />}
    >
      <Text style={styles.title}>Family Board</Text>
      <Text style={styles.subtitle}>Everyone's tasks at a glance</Text>

      {members.length === 0 ? (
        <View style={styles.empty}>
          <Text style={styles.emptyIcon}>👨‍👩‍👧‍👦</Text>
          <Text style={styles.emptyText}>No tasks yet!</Text>
          <Text style={styles.emptySubtext}>Sync from Notion or add tasks to get started.</Text>
        </View>
      ) : (
        members.map((member, idx) => {
          const tasks = board[member];
          const pending = tasks.filter(t => t.status !== 'done');
          const color = MEMBER_COLORS[idx % MEMBER_COLORS.length];

          return (
            <View key={member} style={styles.memberSection}>
              <View style={styles.memberHeader}>
                <View style={[styles.avatar, { backgroundColor: color }]}>
                  <Text style={styles.avatarText}>{member.charAt(0).toUpperCase()}</Text>
                </View>
                <View>
                  <Text style={styles.memberName}>{member}</Text>
                  <Text style={styles.memberCount}>
                    {pending.length} task{pending.length !== 1 ? 's' : ''} open
                  </Text>
                </View>
              </View>
              {tasks.map(task => (
                <TaskCard key={task.id} task={task} onComplete={handleComplete} />
              ))}
            </View>
          );
        })
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
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
  memberSection: {
    marginBottom: spacing.xl,
  },
  memberHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  avatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.sm,
  },
  avatarText: {
    color: '#FFFFFF',
    fontWeight: '700',
    fontSize: 18,
  },
  memberName: {
    ...typography.subtitle,
    fontSize: 18,
  },
  memberCount: {
    ...typography.caption,
    fontSize: 12,
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
    textAlign: 'center',
  },
});
