# Classroom Assistant - Database Schema

## Overview
The application uses a **local JSON file** (`data/teachers.json`) for data storage. No external database is required.

---

## 📊 Database Tables/Collections

### 1. **Teachers Table** (teachers.json)

**Purpose:** Store teacher account information and authentication details

**Storage:** `data/teachers.json`

**Structure:**
```json
{
  "{email}": {
    "id": "string",
    "email": "string",
    "name": "string",
    "password_hash": "string",
    "auth_method": "string",
    "created_at": "string (ISO 8601)",
    "last_login": "string (ISO 8601) | null",
    "google_id": "string | null"
  }
}
```

**Fields:**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | String | Unique teacher identifier | `"T1000"` |
| `email` | String | Teacher email (lowercase, key in JSON) | `"teacher@example.com"` |
| `name` | String | Teacher's full name | `"Demo Teacher"` |
| `password_hash` | String | Bcrypt hashed password | `"$2b$12$K7m1k..."` |
| `auth_method` | String | Authentication method: `"email"` or `"google"` | `"email"` |
| `created_at` | ISO 8601 | Account creation timestamp | `"2025-12-15T00:00:00+00:00"` |
| `last_login` | ISO 8601 or null | Last login timestamp | `"2025-12-15T09:43:05.333277+00:00"` |
| `google_id` | String or null | Google OAuth ID (if registered with Google) | `"101215478498875101338"` |

**Primary Key:** `email` (used as JSON key, must be unique and lowercase)

**Indexes:** 
- Email (primary)
- ID (for lookups)

**Constraints:**
- Email must be unique
- Email must be lowercase
- ID must be unique
- Password hash must be non-empty for email auth
- Password hash can be empty for Google auth

---

### 2. **Active Sessions** (In-Memory, Not Persisted)

**Purpose:** Track active class sessions

**Storage:** Memory (Flask app variable `active_teacher_sessions`)

**Structure:**
```python
{
  "{join_code}": {
    "teacher_id": "string",
    "email": "string",
    "join_code": "string",
    "started_at": "string (ISO 8601)",
    "students": ["student_id_1", "student_id_2", ...]
  }
}
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `join_code` | String | 6-character join code (key) |
| `teacher_id` | String | Teacher ID who started the session |
| `email` | String | Teacher email |
| `started_at` | ISO 8601 | When session started |
| `students` | Array | List of connected student IDs |

**Notes:**
- Stored in memory only (lost on server restart)
- Not persisted to disk
- Automatically cleaned up when session ends

---

### 3. **Active Student Sessions** (In-Memory, Not Persisted)

**Purpose:** Track active student connections

**Storage:** Memory (Flask app variable `active_sessions`)

**Structure:**
```python
{
  "{student_id}": {
    "student_id": "string",
    "teacher_email": "string",
    "join_code": "string",
    "connected_at": "string (ISO 8601)",
    "connected_by_code": "boolean"
  }
}
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `student_id` | String | Unique student identifier |
| `teacher_email` | String | Connected teacher's email |
| `join_code` | String | 6-character join code used (or null) |
| `connected_at` | ISO 8601 | Connection timestamp |
| `connected_by_code` | Boolean | Whether joined by code or manually |

**Notes:**
- Stored in memory only
- Not persisted
- Cleared when session ends

---

## 🗂️ File Structure

```
d:\classroom-assistant\
├── data/
│   └── teachers.json          # Teacher data storage
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── auth_service.py        # Authentication logic
│   └── services/
│       ├── translation_service.py
│       └── speech_service.py
└── frontend/
    ├── src/
    │   ├── App.js
    │   └── pages/
    │       ├── LoginPage.js
    │       ├── StudentView.js
    │       └── TeacherDashboard.js
```

---

## 📝 Sample Data

```json
{
  "teacher@example.com": {
    "id": "T1000",
    "email": "teacher@example.com",
    "name": "Demo Teacher",
    "password_hash": "$2b$12$K7m1kOcRKGNjqZKdqR8h0O7jbXVzVzEqZ0q8QqQqQqQqQqQqQqQq",
    "auth_method": "email",
    "created_at": "2025-12-15T00:00:00+00:00",
    "last_login": "2025-12-15T09:43:05.333277+00:00",
    "google_id": "google_wctaoxrqv"
  },
  "lakshmitaruntarun@gmail.com": {
    "id": "T1001",
    "email": "lakshmitaruntarun@gmail.com",
    "name": "PALIVELA LAKSHMI TARUN",
    "password_hash": "$2b$12$ceJyQmLPzWXfXH.TTJMTFOPVO4zNOz2n54v2Pv9MygRq5hYI18Apq",
    "auth_method": "email",
    "created_at": "2025-12-15T09:34:27.665507+00:00",
    "last_login": "2025-12-19T06:09:59.73463+00:00",
    "google_id": "101215478498875101338"
  }
}
```

---

## 🔐 Authentication Flow

### Email/Password Authentication
1. Teacher registers with email and password
2. Password hashed with bcrypt (cost: 12)
3. Teacher data stored in `teachers.json`
4. On login: password verified against hash
5. JWT token generated (30-day expiry)

### Google OAuth
1. Teacher clicks "Sign in with Google"
2. Google credential verified on backend
3. Teacher account created/updated with `google_id`
4. JWT token generated
5. No password stored for Google auth accounts

---

## 🔄 Data Operations

### CREATE (Register)
```python
# Input
email: "newteacher@example.com"
password: "password123"
name: "New Teacher"

# Output (stored in teachers.json)
{
  "id": "T1002",
  "email": "newteacher@example.com",
  "name": "New Teacher",
  "password_hash": "$2b$12$...",
  "auth_method": "email",
  "created_at": "2025-12-19T10:00:00",
  "last_login": null,
  "google_id": null
}
```

### READ (Login)
```python
# Input
email: "newteacher@example.com"
password: "password123"

# Output
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "teacher": {
    "id": "T1002",
    "email": "newteacher@example.com",
    "name": "New Teacher",
    "role": "teacher"
  }
}
```

### UPDATE (Last Login)
```python
# Triggered on successful login
# Updates last_login timestamp
teacher['last_login'] = datetime.utcnow().isoformat()
```

### DELETE
- Not implemented (data retention for records)
- Teachers can only update profile via login

---

## 💾 Data Persistence

### Save to Disk
```python
def _save_teachers(self):
    with open(self.teachers_file, 'w', encoding='utf-8') as f:
        json.dump(self.teachers_db, f, indent=2, ensure_ascii=False)
```

**When saved:**
- After registration
- After first/subsequent logins
- After Google OAuth

**File location:** `d:\classroom-assistant\data\teachers.json`

---

## 🔒 Security Features

| Feature | Implementation |
|---------|-----------------|
| **Password Hashing** | bcrypt (cost: 12 rounds) |
| **Authentication** | JWT tokens (30-day expiry) |
| **Token Verification** | HS256 signature validation |
| **Email Normalization** | Lowercase, stripped whitespace |
| **OAuth Integration** | Google ID verification |
| **CORS** | Configured for localhost & Vercel |

---

## 📈 Migration from Supabase (If Needed)

If switching to a real database later (PostgreSQL, MongoDB, etc.):

1. Export `teachers.json` as backup
2. Create equivalent table with same schema
3. Map JSON fields to database columns
4. Update `auth_service.py` to use database queries
5. Implement connection pooling
6. Add transaction support

**Example PostgreSQL migration:**
```sql
CREATE TABLE teachers (
  id VARCHAR(20) PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  password_hash VARCHAR(255),
  auth_method VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_login TIMESTAMP,
  google_id VARCHAR(255)
);

CREATE INDEX idx_email ON teachers(email);
CREATE INDEX idx_id ON teachers(id);
```

---

## 📊 Current Data Stats

| Metric | Value |
|--------|-------|
| **Total Teachers** | 3 |
| **Storage Format** | JSON (human-readable) |
| **File Size** | ~1-2 KB |
| **Scalability** | Up to ~10,000 records (then consider migration) |

---

## 🚀 Next Steps (If Scaling)

1. **Switch to PostgreSQL** (when users > 100)
2. **Add read replicas** (for load balancing)
3. **Implement caching** (Redis for sessions)
4. **Add backup strategy** (daily snapshots)
5. **Monitor performance** (response time tracking)

---

**Schema Last Updated:** December 19, 2025
**Version:** 1.0 (Local JSON-based)
