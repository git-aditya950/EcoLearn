# EcoLearn Codebase - Comprehensive Overview
**A platform for environmental science education with gamification, quizzes, and progress tracking**

---

## 1. DATABASE SCHEMA (database/db_setup.py)

### Core Tables

#### **users** (`User` class)
```python
Fields:
- id (Primary Key)
- username (String, unique, indexed)
- email (String, unique, indexed)
- password_hash (String, 255)
- role (String) - 'student', 'teacher', 'admin'
- first_name, last_name (String)
- bio (Text)
- avatar_url (String)
- is_active (Boolean)
- created_at, updated_at (DateTime)

Relationships:
- enrollments (1-to-many with Enrollment)
- progress_records (1-to-many with Progress)
- quiz_attempts (1-to-many with QuizAttempt)
- courses_created (1-to-many with Course as instructor)
```

#### **quiz_attempts** (`QuizAttempt` class)
```python
Fields:
- id (Primary Key)
- user_id (Foreign Key → users.id)
- quiz_id (Foreign Key → quizzes.id)
- score (Float) - percentage score (0-100)
- passed (Boolean)
- started_at (DateTime, default=now)
- completed_at (DateTime)
- time_spent_seconds (Integer)

Relationships:
- user (many-to-one with User)
- quiz (many-to-one with Quiz)
- answers (1-to-many with Answer)
```

#### **progress** (`Progress` class)
```python
Fields:
- id (Primary Key)
- user_id (Foreign Key → users.id)
- lesson_id (Foreign Key → lessons.id)
- started_at (DateTime, default=now)
- completed_at (DateTime)
- is_completed (Boolean)
- time_spent_seconds (Integer)

Relationships:
- user (many-to-one with User)
- lesson (many-to-one with Lesson)
```

#### **achievements** (`Achievement` class)
```python
Fields:
- id (Primary Key)
- name (String, 100)
- description (Text)
- badge_url (String)
- criteria (Text) - description of achievement requirements
- created_at (DateTime)
```

#### **Additional Tables (Course Structure)**

**courses** (`Course` class)
```python
Fields:
- id, title, description (Text)
- instructor_id (FK → users.id)
- category (e.g., 'Climate Change', 'Biodiversity', 'Sustainability')
- difficulty_level ('beginner', 'intermediate', 'advanced')
- thumbnail_url, is_published, created_at, updated_at
Relationships: instructor, lessons, enrollments
```

**lessons** (`Lesson` class)
```python
Fields:
- id, course_id (FK), title, content (Text)
- order (position), video_url, duration_minutes
- is_published, created_at, updated_at
Relationships: course, quizzes, progress_records
```

**quizzes** (`Quiz` class)
```python
Fields:
- id, lesson_id (FK), title, description
- passing_score (Float, default=70.0%)
- is_published, created_at, updated_at
Relationships: lesson, questions, attempts
```

**questions** (`Question` class)
```python
Fields:
- id, quiz_id (FK), question_text (Text)
- question_type ('multiple_choice', 'short_answer', 'true_false')
- options (JSON array), correct_answer (Text)
- order, points (Float)
Relationships: quiz, answers
```

**answers** (`Answer` class)
```python
Fields:
- id, question_id (FK), quiz_attempt_id (FK)
- user_answer (Text), is_correct (Boolean)
- score (Float), created_at
Relationships: question, quiz_attempt
```

**enrollments** (`Enrollment` class)
```python
Fields:
- id, user_id (FK), course_id (FK)
- enrolled_at, completed_at (DateTime)
- is_active (Boolean)
- progress_percentage (Float)
Relationships: user, course
```

**Schema Initialization:**
- `init_db()` - Creates all tables
- `drop_db()` - Drops all tables (caution)
- Database URL: SQLite by default (`sqlite:///ecolearn.db`)

---

## 2. APP.PY STRUCTURE & DASHBOARDS

### File: [app.py](app.py)

**Key Imports:**
```python
from modules.auth import AuthManager, init_auth_session
from modules.gamification import GamificationEngine, Leaderboard
from modules.quiz_engine import QuizEngine
from modules.analytics import AnalyticsEngine
from api.climate_data import ClimateDataFetcher
from database.db_setup import init_db
```

### Main Functions

#### **configure_page()**
- Streamlit page config (wide layout, no sidebar initially)
- Comprehensive Mentimeter-inspired design system with CSS variables
- Typography: Plus Jakarta Sans (headings), DM Sans (body)
- Color scheme: Primary (#1A1A2E), Secondary (#635BFF), Accent (#FF6B6B), Success (#00C48C)
- Responsive grid layout for mobile/desktop
- Custom button, card, input field, and tab styling

#### **render_login_page()**
- Tab-based authentication (Login / Register)
- **Login Form:** Username/Email + Password, Forgot Password link
- **Register Form:** First/Last Name + Username + Email + Role Selection (Student/Teacher) + Password confirmation
- Input validation (6+ char password, username 3+ chars, matching passwords)
- Session state tracking (`st.session_state.auth_mode`, `st.session_state.authenticated`)

#### **render_student_dashboard()**
Primary user interface for students

**Components:**
1. **Top Navigation Bar**
   - Logo: "🌍 EcoLearn"
   - User info display (username, email)
   - Logout button

2. **Hero Greeting Section**
   - Gradient background (#1A1A2E → #2D1B69)
   - Dynamic welcome message with username

3. **Stats Cards Row** (4 columns)
   - **Level Card** (Yellow gradient): Current level + level name
   - **XP Card** (Green gradient): Total XP + % to next level
   - **Rank Card** (Red/Orange gradient): Global rank (`#rank`)
   - **Streak Card** (Purple gradient): Login streak (7 days)

4. **Main Content Tabs**
   - Quiz selection and attempt functionality
   - Analytics/progress view
   - Leaderboard view
   - Profile/settings view

5. **Quiz Selection & Attempt**
   - Display available quizzes (title, question count, passing score)
   - Quiz cards (responsive grid, max 4 per row)
   - Quiz session flow (quiz_engine integration)

### Session State Variables
- `st.session_state.authenticated` - Login status
- `st.session_state.user` - User object (id, username, email, role, avatar_url)
- `st.session_state.auth_mode` - 'login' or 'register'
- `st.session_state.show_welcome` - Welcome banner display
- `st.session_state.selected_quiz_id` - Currently selected quiz

### Key Design Features
- **Mentimeter-inspired:** Modern UI with gradient backgrounds, smooth animations
- **Responsive:** Mobile-friendly grid layouts
- **State management:** Streamlit session state for navigation
- **Accessibility:** Clear hierarchy, good color contrast, semantic HTML

---

## 3. MODULES DIRECTORY

### [modules/auth.py](modules/auth.py)

**AuthManager Class** - Handles all authentication

Key Methods:

```python
hash_password(password: str) → str
- Uses bcrypt (BCRYPT_LOG_ROUNDS = 12)
- Returns base64-decoded hash

verify_password(password: str, hashed_password: str) → bool
- Bcrypt checkpw comparison

register_user(username, email, password, first_name='', last_name='', role='student') → dict
- Validates: username ≥3 chars, password ≥6 chars
- Checks for duplicate username/email
- Creates User record with hashed password
- Returns: {'success': bool, 'message': str, 'user_id': int}

login_user(username: str, password: str) → dict
- Accepts username OR email
- Verifies password
- Checks account is active
- Returns: {'success': bool, 'message': str, 'user': {...}}

get_user_by_id(user_id: int) → dict
- Returns full user profile data

update_user_profile(user_id: int, **kwargs) → dict
- Allowed fields: first_name, last_name, bio, avatar_url
- Session-scoped database operations
```

**Session Management:**
- Uses SQLAlchemy Session() for database transactions
- Bcrypt for password hashing (12 rounds)
- **No JWT tokens mentioned** - relies on Streamlit session state

---

### [modules/quiz_engine.py](modules/quiz_engine.py)

**QuizEngine Class** - Core quiz logic and scoring

Key Methods:

```python
seed_sample_quizzes() → dict
- Populates 4 sample quizzes if not present:
  1. Climate Change Basics (5 questions, 70% passing)
  2. Biodiversity and Ecosystems (5 questions)
  3. Recycling and Waste Management (5 questions)
  4. Renewable Energy Essentials (questions not shown in excerpt)

_normalize_answer(answer: str) → str
- Case-insensitive answer comparison (strip(), lower())

Question Types Supported:
- 'multiple_choice' - Select from options
- 'true_false' - Boolean answer
- 'short_answer' - Free text response

Sample Quiz Questions:
- "Which gas is the largest contributor to human-driven global warming?"
  Options: CO2, N2, O2, Ar | Correct: CO2 | Points: 1.0
- "True or False: Deforestation can increase atmospheric CO2 levels?"
  Options: True, False | Correct: True
```

**Scoring Logic:**
- Passing score threshold defined per quiz (default 70%)
- Questions have individual point values
- Total score calculated as percentage
- Tracks time spent (seconds)

---

### [modules/gamification.py](modules/gamification.py)

**GamificationEngine Class** - XP, leveling, badges, streaks

Key Methods:

```python
calculate_xp_earned(quiz_score: float, is_streak: bool=False, streak_count: int=1) → int
- Base XP: (score / 100) * 100 (max 100 XP per quiz)
- Streak bonus: multiplier = 1 + ((streak_count-1) * 0.1)
  - 10% per streak level (capped at 2x)
- Example: 80 score, 5-day streak → 80 * 1.4 = 112 XP

add_xp_to_user(user_id: int, xp_amount: int) → dict
- Calculates new XP total
- Leveling: 100 XP per level
- Returns: {'xp_gained', 'total_xp', 'current_level', 'level_up': bool, 'level_name'}

get_user_level(user_id: int) → dict
- Aggregates XP from all quiz attempts
- Returns: {
    'level': int,
    'level_name': str (from LEVELS array),
    'total_xp': int,
    'xp_in_current_level': int,
    'xp_needed_for_next': int,
    'progress_percentage': float
  }

award_badge(user_id: int, badge_key: str) → dict
- Validates badge key exists in BADGES config
- Returns badge metadata

check_badge_criteria(user_id: int) → list
- Checks quiz attempt history
- Returns earned badge keys:
  - 'FIRST_BLOOD' (1+ quiz)
  - 'QUIZ_MASTER' (50+ quizzes)
  - 'PERFECT_SCORE' (100% score)

track_login_streak(user_id: int) → dict
- Placeholder (needs UserLoginLog table)
- Returns: {'current_streak', 'max_streak', 'streak_reward_xp'}

get_daily_reward(user_id: int) → dict
- Daily XP reward (5 XP base)
- Bonus multiplier based on streak
```

**Level System:** 50 levels (from config.LEVELS)
```
Seedling → Sprout → Sapling → ... → Earth's Champion 
→ Divine Guardian → Cosmos Protector → Living Legend 
→ Forest Guardian (Level 50)
```

**Badge System (10 badges):**
- QUIZ_MASTER: 50 quizzes (🏆)
- STREAK_7: 7 consecutive days (🔥)
- CARBON_EXPERT: All Climate quizzes (💨)
- BIODIVERSITY_PRO: All Biodiversity quizzes (🌿)
- RECYCLING_EXPERT: All Recycling quizzes (♻️)
- RENEWABLE_GURU: All Renewable quizzes (⚡)
- PERFECT_SCORE: 100% score (💯)
- SPEED_DEMON: Half-time completion (⚡)
- FIRST_BLOOD: First quiz (🌱)
- LEVEL_10: Reach level 10 (📈)

---

### [modules/leaderboard.py](modules/leaderboard.py)

**LeaderboardManager Class** - Ranking and competition

Key Methods:

```python
_calculate_user_xp(user_id: int) → int
- Sums score from all completed quiz attempts
- (10 points per percent score)

get_global_leaderboard(limit: int = 100) → dict
- Ranks all active users by (level DESC, xp DESC)
- Returns:
  {
    'leaderboard_type': 'global',
    'total_users': int,
    'leaderboard': [
      {
        'rank': int,
        'user_id': int,
        'username': str,
        'level': int,
        'level_name': str,
        'xp': int,
        'quizzes_completed': int,
        'avatar_url': str
      },
      ...
    ]
  }

get_course_leaderboard(course_id: int, limit: int = 50) → dict
- Course-specific rankings (enrolled students only)
- Sorted by average_score DESC
- Returns rank, username, average_score, quizzes_completed, progress%

get_user_rank(user_id: int) → dict
- Returns user's global rank position
- Fields: rank, level, level_name, xp, total_users

get_friends_leaderboard(user_id: int, friend_ids: list, limit: int = 20) → dict
- Includes user + friends list
- Marks self with 'is_self': bool flag
```

---

### [modules/analytics.py](modules/analytics.py)

**AnalyticsEngine Class** - Performance tracking and insights

Key Methods:

```python
get_student_progress_report(user_id: int) → dict
- Comprehensive individual progress report
- Returns:
  {
    'student': {username, email, first_name, last_name},
    'quiz_stats': {
      'total_attempted': int,
      'completed': int,
      'passed': int,
      'pass_rate': float (percentage),
      'average_score': float
    },
    'time_stats': {'total_time_minutes': float},
    'course_stats': {
      'total_enrolled': int,
      'completed_courses': int
    },
    'lesson_stats': {
      'lessons_started': int,
      'lessons_completed': int
    }
  }

get_class_performance_report(course_id: int) → dict
- Teacher view of all students in a course
- Aggregates per-student metrics
- Returns:
  {
    'course': str,
    'total_students': int,
    'class_average': float,
    'student_performance': [
      {
        'username': str,
        'quizzes_completed': int,
        'average_score': float,
        'pass_rate': float,
        'progress': float
      },
      ...
    ]
  }

get_weak_topics(course_id: int) → dict
- Identifies struggling areas
- Analyzes quiz performance per lesson
- Difficulty classification: 'High' (<60%), 'Medium' (<80%), 'Low' (80%+)
- Returns top 5 weak topics sorted by average score

DataFrameBuilder (helper class)
- Converts database records to pandas DataFrames
- (Implementation not shown in excerpt)
```

---

## 4. UI FOLDER

### File: [ui/__init__.py](ui/__init__.py)
**Status:** Empty file (no UI components defined yet)

**Likely intended for:**
- Reusable Streamlit components
- Custom widget definitions
- UI helper functions

---

## 5. AUTHENTICATION FLOW & SESSION MANAGEMENT

### Login/Registration Flow

```
[User] 
  ↓
Login/Register Form (render_login_page)
  ↓
AuthManager.login_user() or AuthManager.register_user()
  ↓
Bcrypt password verification
  ↓
Set st.session_state.authenticated = True
Set st.session_state.user = {id, username, email, role, ...}
  ↓
Conditional render: render_student_dashboard()
```

### Session State Architecture

**Client-side (Streamlit):**
- `st.session_state.authenticated` - Boolean flag
- `st.session_state.user` - User dict from login response
- `st.session_state.auth_mode` - Tab selector ('login'/'register')
- `st.session_state.selected_quiz_id` - Quiz session

**Database-side:**
- SQLAlchemy ORM with SQLite backend
- Password stored as bcrypt hash (12 rounds)
- `is_active` field gates account access

### Potential Session Issues

⚠️ **No persistent server-side sessions:**
- Streami state resets on page refresh
- No token refresh mechanism
- Authentication tied to browser session only
- **Recommendation:** Implement JWT tokens or Streamlit secret management for production

### Password Security

```
Registration:
  password → bcrypt.gensalt(12) → salt
           → bcrypt.hashpw(password, salt)
           → Store hash in user.password_hash

Login:
  user_input → bcrypt.checkpw(user_input, stored_hash)
            → Boolean result
```

---

## 6. API & EXTERNAL INTEGRATIONS

### File: [api/climate_data.py](api/climate_data.py)
**Class:** `ClimateDataFetcher`

**Configured APIs:**
```python
OPEN_METEO_API_URL = 'https://api.open-meteo.com/v1/forecast'
NASA_CLIMATE_API_URL = 'https://api.nasa.gov/api/v3/climate_anomalies'
```

*(Implementation not fully shown in provided excerpts)*

---

## 7. CONFIGURATION SETTINGS

### File: [config.py](config.py)

**Database:**
```python
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///ecolearn.db')
```

**Gamification Constants:**
```python
INITIAL_XP = 0
XP_PER_CORRECT_ANSWER = 10
STREAK_BONUS_MULTIPLIER = 1.5
BCRYPT_LOG_ROUNDS = 12
```

**Level Progression (50 levels):**
```
Levels: Seedling → Sprout → ... → Living Legend (Level 50)
XP per level: 100 (e.g., Level 1: 0-99 XP, Level 2: 100-199 XP)
```

**Quiz Categories:**
```
QUIZ_CATEGORIES = ['Climate Change', 'Biodiversity', 'Recycling', 'Renewable Energy']
DIFFICULTY_LEVELS = ['Easy', 'Medium', 'Hard']
```

**Badges (10 total):**
All defined in BADGES dictionary with name, description, icon

**Streamlit Config:**
```python
STREAMLIT_PAGE_CONFIG = {
    'page_title': 'EcoLearn - Learn About Environment',
    'page_icon': '🌍',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded',
}
```

---

## 8. KEY FUNCTION SIGNATURES REFERENCE

### Authentication
- `AuthManager.hash_password(password) → str`
- `AuthManager.verify_password(password, hashed) → bool`
- `AuthManager.register_user(...) → dict`
- `AuthManager.login_user(username, password) → dict`
- `AuthManager.get_user_by_id(user_id) → dict`
- `AuthManager.update_user_profile(user_id, **kwargs) → dict`

### Quiz Engine
- `QuizEngine.seed_sample_quizzes() → dict`
- `QuizEngine._normalize_answer(answer) → str`

### Gamification
- `GamificationEngine.calculate_xp_earned(score, is_streak, streak_count) → int`
- `GamificationEngine.add_xp_to_user(user_id, xp_amount) → dict`
- `GamificationEngine.get_user_level(user_id) → dict`
- `GamificationEngine.award_badge(user_id, badge_key) → dict`
- `GamificationEngine.check_badge_criteria(user_id) → list`
- `GamificationEngine.track_login_streak(user_id) → dict`
- `GamificationEngine.get_daily_reward(user_id) → dict`

### Leaderboard
- `LeaderboardManager._calculate_user_xp(user_id) → int`
- `LeaderboardManager.get_global_leaderboard(limit) → dict`
- `LeaderboardManager.get_course_leaderboard(course_id, limit) → dict`
- `LeaderboardManager.get_user_rank(user_id) → dict`
- `LeaderboardManager.get_friends_leaderboard(user_id, friend_ids, limit) → dict`

### Analytics
- `AnalyticsEngine.get_student_progress_report(user_id) → dict`
- `AnalyticsEngine.get_class_performance_report(course_id) → dict`
- `AnalyticsEngine.get_weak_topics(course_id) → dict`

---

## 9. ARCHITECTURE SUMMARY

```
┌─────────────────────────────────────────────────────┐
│          Streamlit Web Interface (app.py)           │
│  - Login/Register Page                              │
│  - Student Dashboard (stats, quizzes, leaderboard)  │
│  - Teacher Dashboard (class analytics)              │
│  - Admin Panel (optional)                           │
└──────────────┬──────────────────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌─────▼──────────────┐  │  ┌──────────────────────┐
│  Modules/Business   │  │  │  External APIs       │
│  Logic Layer        │  │  │  - Open-Meteo       │
├─────────────────────┤  │  │  - NASA Climate     │
│ auth.py             │  │  └──────────────────────┘
│ quiz_engine.py      │  │
│ gamification.py     │  │
│ leaderboard.py      │  │
│ analytics.py        │  │
└─────────┬───────────┘  │
          │              │
          └──────┬───────┘
                 │
        ┌────────▼────────────────┐
        │  SQLAlchemy ORM Layer    │
        │  (database/db_setup.py)  │
        └────────┬────────────────┘
                 │
        ┌────────▼────────────────┐
        │  SQLite Database         │
        │  - 10 tables             │
        │  - users, quizzes,       │
        │  - quiz_attempts, etc    │
        └─────────────────────────┘
```

### Role-Based Access
- **Students:** Quizzes, progress tracking, leaderboard, profile
- **Teachers:** Class performance reports, weak topics analysis
- **Admin:** User management, content management (implied)

---

## 10. CRITICAL NOTES & TODO

### ✅ Implemented
- User authentication (registration, login, password hashing)
- Quiz engine with scoring and multiple question types
- Gamification system (XP, levels, badges, streaks)
- Leaderboard rankings (global, course-specific, friends)
- Analytics for student progress and class performance
- Streamlit dashboard with responsive design

### ⚠️ Partially Implemented
- UI folder empty (no custom components yet)
- Session management relies on Streamlit state (no persistent sessions)
- Login streak tracking is placeholder (needs UserLoginLog table)
- Admin panel not visible in code
- Teacher dashboard functions referenced but not in app.py excerpt
- Climate data API integration incomplete

### ❌ Missing/TODO
- Email verification
- Password reset functionality
- OAuth/Social login
- User roles enforcement (teacher/admin features)
- Real-time notifications
- Course creation UI (forms for teachers)
- Advanced analytics dashboards
- Export/reporting features
- Search functionality
- Commenting/discussion forums

---

## 11. STARTING THE APPLICATION

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python database/db_setup.py

# Run Streamlit app
streamlit run app.py

# App opens at: http://localhost:8501
```

---

**Last Updated:** March 24, 2026
**Framework:** Streamlit + SQLAlchemy + SQLite
**Python Version:** 3.8+
