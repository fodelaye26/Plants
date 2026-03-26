import React, { useCallback, useState } from 'react';
import { Alert, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { triggerNotionSync } from '../services/api';
import { borderRadius, colors, shadows, spacing, typography } from '../theme';

export default function SettingsScreen() {
  const [syncing, setSyncing] = useState(false);
  const [lastSync, setLastSync] = useState<string | null>(null);

  const handleSync = useCallback(async () => {
    setSyncing(true);
    try {
      const result = await triggerNotionSync();
      setLastSync(new Date().toLocaleTimeString());
      Alert.alert(
        'Sync Complete',
        `Created ${result.created} new tasks, updated ${result.updated} existing tasks.`
      );
    } catch {
      Alert.alert('Sync Failed', 'Could not connect to Notion. Check your API key and database ID.');
    } finally {
      setSyncing(false);
    }
  }, []);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Settings</Text>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Notion Sync</Text>
        <Text style={styles.sectionDesc}>
          Pull the latest tasks from your Notion household database.
        </Text>
        <Pressable
          style={({ pressed }) => [styles.syncButton, pressed && styles.syncButtonPressed]}
          onPress={handleSync}
          disabled={syncing}
        >
          <Text style={styles.syncButtonText}>
            {syncing ? 'Syncing...' : 'Sync Now'}
          </Text>
        </Pressable>
        {lastSync && (
          <Text style={styles.lastSync}>Last synced at {lastSync}</Text>
        )}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>
        <Text style={styles.sectionDesc}>
          Family Home App v0.1.0{'\n'}
          A warm, cozy household task manager for the whole family.
        </Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Coming Soon</Text>
        <View style={styles.comingSoonList}>
          <Text style={styles.comingSoonItem}>🌟  Zelda Mode — icon-based kid tasks</Text>
          <Text style={styles.comingSoonItem}>⭐  Stars, streaks, and badges</Text>
          <Text style={styles.comingSoonItem}>🔔  Smart reminder scheduling</Text>
          <Text style={styles.comingSoonItem}>🎮  Gamified rewards system</Text>
        </View>
      </View>
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
    marginBottom: spacing.lg,
  },
  section: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.lg,
    ...shadows.soft,
  },
  sectionTitle: {
    ...typography.subtitle,
    marginBottom: spacing.sm,
  },
  sectionDesc: {
    ...typography.body,
    color: colors.textSecondary,
    lineHeight: 22,
    marginBottom: spacing.md,
  },
  syncButton: {
    backgroundColor: colors.primary,
    borderRadius: borderRadius.md,
    paddingVertical: spacing.md,
    alignItems: 'center',
  },
  syncButtonPressed: {
    backgroundColor: colors.primaryDark,
  },
  syncButtonText: {
    color: '#FFFFFF',
    fontWeight: '700',
    fontSize: 16,
  },
  lastSync: {
    ...typography.caption,
    textAlign: 'center',
    marginTop: spacing.sm,
  },
  comingSoonList: {
    gap: spacing.sm,
  },
  comingSoonItem: {
    ...typography.body,
    color: colors.textSecondary,
  },
});
