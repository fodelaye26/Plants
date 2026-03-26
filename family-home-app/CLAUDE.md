# Project: Family Home App

Build a mobile-first family household task app connected to Notion.

## Product goal
Create a visually pleasant, proactive household app for a family of 4 with 2 young kids.

The app should:
- sync household tasks from Notion
- show simple daily tasks for each person
- send proactive, kind reminders
- include a child-friendly mode for Zelda (Phase 2)
- support gamification with stars, streaks, badges, and rewards (Phase 2+)
- be visually warm, calm, and delightful

## Core modes
1. Parent mode (Phase 1)
2. Kid mode (Phase 2)
3. Automation/reminder engine (Phase 3)

## Constraints
- Zelda cannot read yet, so her mode must be icon-based and audio-friendly
- Large buttons, minimal text, strong visual feedback, no clutter

## Architecture
- Frontend: React Native with Expo
- Backend: FastAPI (Python)
- Data: Notion API for household tasks + SQLite/PostgreSQL for app state
- Notion = planning + content, App DB = behavior + experience

## Engineering rules
- Clear modular architecture
- Typed APIs with Pydantic models
- Strong sync reliability with Notion
- Safe handling of notification timing
- Build MVP first and keep it runnable
