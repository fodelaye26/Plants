/**
 * Family Home App — warm, cozy design system.
 * Soft colors, rounded shapes, gentle feel.
 */

export const colors = {
  // Primary palette — warm and inviting
  primary: '#FF9F6B',       // warm orange
  primaryLight: '#FFD4B8',  // peach
  primaryDark: '#E07B42',   // deep orange

  // Accent
  accent: '#7EC8B8',        // sage green
  accentLight: '#B8E6D9',   // mint
  accentDark: '#5AA898',    // forest

  // Backgrounds
  background: '#FFF8F0',    // warm cream
  surface: '#FFFFFF',
  surfaceWarm: '#FFF3E8',   // light peach

  // Text
  text: '#3D3027',          // warm dark brown
  textSecondary: '#8B7D6B', // muted brown
  textLight: '#B8A99A',     // light brown

  // Status
  success: '#7EC8B8',       // sage green
  warning: '#FFD166',       // sunny yellow
  error: '#FF8B8B',         // soft red
  info: '#8BB8FF',          // sky blue

  // Category colors
  kitchen: '#FFB347',
  laundry: '#87CEEB',
  toys: '#DDA0DD',
  cleaning: '#98D8C8',
  bedtime: '#B8A9C9',
  school: '#F7DC6F',
  outdoor: '#82E0AA',
  admin: '#AEB6BF',

  // Misc
  border: '#F0E6D8',
  shadow: 'rgba(61, 48, 39, 0.08)',
  overlay: 'rgba(61, 48, 39, 0.4)',
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

export const borderRadius = {
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  full: 999,
};

export const typography = {
  title: {
    fontSize: 28,
    fontWeight: '700' as const,
    color: colors.text,
  },
  subtitle: {
    fontSize: 20,
    fontWeight: '600' as const,
    color: colors.text,
  },
  body: {
    fontSize: 16,
    fontWeight: '400' as const,
    color: colors.text,
  },
  caption: {
    fontSize: 13,
    fontWeight: '400' as const,
    color: colors.textSecondary,
  },
  label: {
    fontSize: 12,
    fontWeight: '600' as const,
    color: colors.textSecondary,
    textTransform: 'uppercase' as const,
    letterSpacing: 0.8,
  },
};

export const shadows = {
  card: {
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 1,
    shadowRadius: 8,
    elevation: 3,
  },
  soft: {
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 1,
    shadowRadius: 4,
    elevation: 1,
  },
};

const theme = { colors, spacing, borderRadius, typography, shadows };
export default theme;
