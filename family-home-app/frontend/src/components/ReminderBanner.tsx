import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { borderRadius, colors, shadows, spacing, typography } from '../theme';
import { Reminder } from '../types';

interface ReminderBannerProps {
  reminder: Reminder | null;
}

export default function ReminderBanner({ reminder }: ReminderBannerProps) {
  if (!reminder) return null;

  const isAllDone = reminder.task_count === 0;

  return (
    <View style={[styles.banner, isAllDone && styles.bannerCelebrate]}>
      <Text style={styles.icon}>{isAllDone ? '🎉' : '💛'}</Text>
      <Text style={styles.message}>{reminder.message}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  banner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surfaceWarm,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    marginBottom: spacing.lg,
    ...shadows.soft,
  },
  bannerCelebrate: {
    backgroundColor: colors.accentLight,
  },
  icon: {
    fontSize: 24,
    marginRight: spacing.sm,
  },
  message: {
    ...typography.body,
    flex: 1,
    lineHeight: 22,
  },
});
