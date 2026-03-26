# Family Home App

A warm, pleasant household task manager for the whole family. Connected to Notion as your family command center, with a delightful mobile experience layer.

## Architecture

```
Notion (source of truth)
    ↓
Sync Service
    ↓
FastAPI Backend (Python)
    ↓
SQLite (app state: points, streaks, reminders)
    ↓
React Native + Expo (mobile app)
```

## Project Structure

```
family-home-app/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Environment settings
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── models/              # DB models + Pydantic schemas
│   │   │   ├── task.py
│   │   │   ├── family_member.py
│   │   │   └── reminder.py
│   │   ├── routers/             # API endpoints
│   │   │   ├── tasks.py
│   │   │   ├── family.py
│   │   │   ├── reminders.py
│   │   │   └── sync.py
│   │   └── services/            # Business logic
│   │       ├── notion_sync.py
│   │       ├── task_service.py
│   │       └── reminder_engine.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── App.tsx                  # Entry point
│   ├── src/
│   │   ├── screens/             # Today, My Tasks, Family Board, Settings
│   │   ├── components/          # TaskCard, Avatar, ReminderBanner
│   │   ├── services/api.ts      # Backend API client
│   │   ├── theme/index.ts       # Warm design system
│   │   ├── types/index.ts       # TypeScript types
│   │   └── navigation/          # Bottom tab navigator
│   ├── package.json
│   └── app.json
└── CLAUDE.md
```

## Setup Instructions

### 1. Backend

```bash
cd family-home-app/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Notion API key and database IDs

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API docs will be at http://localhost:8000/docs

### 2. Frontend

```bash
cd family-home-app/frontend

# Install dependencies
npm install

# Start Expo
npx expo start
```

### 3. Notion Database Setup

Create a Notion database called **Household Tasks** with these properties:

| Property | Type | Notes |
|---|---|---|
| Task Name | Title | Required |
| Assigned To | Person | Family member |
| Mode | Select | Options: Adult, Kid, Family |
| Category | Select | Kitchen, Laundry, Toys, Cleaning, Bedtime, School, Outdoor, Admin |
| Status | Select | Not Started, In Progress, Done, Skipped |
| Recurrence | Select | Daily, Weekly, Monthly, Once |
| Due Date | Date | When it's due |
| Time Window | Select | Morning, After School, Evening, Anytime |
| Difficulty | Number | 1-3 |
| Points | Number | Reward points |
| Kid Friendly | Checkbox | Show in kid mode |
| Needs Parent Help | Checkbox | Flag for supervision |
| Icon Key | Text | Emoji or icon name |
| Voice Prompt URL | URL | Audio prompt for kids |
| Active | Checkbox | Is task currently active |

Then create a Notion integration:
1. Go to https://www.notion.so/my-integrations
2. Create a new integration
3. Copy the API key to your `.env` file
4. Share your database with the integration
5. Copy the database ID (from the URL) to your `.env` file

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/tasks/` | List all tasks |
| GET | `/api/tasks/today` | Today's tasks |
| GET | `/api/tasks/board` | Family board (grouped by person) |
| POST | `/api/tasks/` | Create a task |
| PATCH | `/api/tasks/{id}` | Update a task |
| POST | `/api/tasks/{id}/complete` | Mark task done |
| GET | `/api/family/` | List family members |
| POST | `/api/family/` | Add family member |
| GET | `/api/reminders/generate` | Get a contextual reminder |
| GET | `/api/reminders/history` | Reminder history |
| POST | `/api/sync/notion` | Trigger Notion sync |

## What's Complete (Phase 1)

- [x] FastAPI backend with typed models
- [x] Notion sync service
- [x] Task CRUD with filtering
- [x] Family member management
- [x] Reminder engine with kind, contextual messages
- [x] React Native frontend with Expo
- [x] Warm, cozy design system
- [x] Today view with reminder banner
- [x] My Tasks view
- [x] Family Board view (grouped by person)
- [x] Settings with Notion sync trigger
- [x] Bottom tab navigation

## What's Next

### Phase 2 — Zelda Mode
- Icon-based task cards (no reading required)
- Audio prompts (tap to hear)
- Big "Done" button with celebration animation
- Stars and progress tracking
- Cheerful, game-like interface

### Phase 3 — Smart Reminders
- Time-window-based scheduling (morning, after school, evening)
- Gentle overdue nudges
- Celebration notifications
- Weekly home reset flows
- Configurable tone: calm, playful, coach-like

### Phase 4 — Gamification
- Streaks for consecutive helpful days
- Badges (Toy Tidy Hero, Bedtime Helper, etc.)
- Reward shop (points for privileges/treats)
- Digital pet or garden that grows with chores
