import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { borderRadius, colors, shadows, spacing, typography } from '../theme';
import { FamilyMember } from '../types';

interface AvatarProps {
  member: FamilyMember;
  size?: number;
  showName?: boolean;
}

export default function FamilyMemberAvatar({ member, size = 48, showName = true }: AvatarProps) {
  const initial = member.name.charAt(0).toUpperCase();

  return (
    <View style={styles.container}>
      <View
        style={[
          styles.avatar,
          {
            width: size,
            height: size,
            borderRadius: size / 2,
            backgroundColor: member.color_theme || colors.primary,
          },
        ]}
      >
        <Text style={[styles.initial, { fontSize: size * 0.4 }]}>{initial}</Text>
      </View>
      {showName && <Text style={styles.name}>{member.name}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    marginHorizontal: spacing.sm,
  },
  avatar: {
    justifyContent: 'center',
    alignItems: 'center',
    ...shadows.soft,
  },
  initial: {
    color: '#FFFFFF',
    fontWeight: '700',
  },
  name: {
    ...typography.caption,
    marginTop: spacing.xs,
    textAlign: 'center',
  },
});
