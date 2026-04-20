# ChatProject — Real-Time Chat Application

A full-stack, real-time desktop chat application built with **Python** and **MySQL**, developed as a semester project for **Database Management Systems (DBMS)**.  
The project demonstrates core relational database concepts through a functional, modern messaging interface.

---

## Overview

| Login Screen | Chat Interface |
|:---:|:---:|
| Clean card-based authentication UI | Sidebar + live messaging panel |

- **Backend**: Pure Python with `mysql-connector-python` — no ORM, raw SQL everywhere.
- **Frontend**: Tkinter-based modern GUI with a purple-accented, card-layout design.
- **Database**: MySQL with a normalized schema spanning **7 tables**, **1 view**, and **2 indexes**.
- **Real-Time**: Background-threaded polling refreshes chats every 2 seconds.

---

## Features

- **User Registration & Login** — SHA-256 hashed passwords, parameterized queries
- **1-on-1 Chat** — Create new conversations by username lookup
- **Real-Time Messaging** — Threaded background polling for live message updates
- **Chat Sidebar** — Displays all conversations with latest message snippets
- **Modern UI** — Purple-themed card layout with avatar initials, smooth scrolling
- **One-Click Launch** — `start.bat` handles dependency install, schema loading, and app startup

---

## Project Structure

```
ChatProject/
├── sql/
│   └── schema.sql          # Full database schema (tables, views, indexes)
├── src/
│   ├── main.py             # Application entry point
│   ├── backend.py          # Database interaction layer (ChatDatabase class)
│   └── frontend.py         # Tkinter GUI (ChatApp class)
├── requirements.txt        # Python dependencies
├── start.bat               # One-click Windows launcher
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.x |
| GUI Framework | Tkinter |
| Database | MySQL 8.x |
| DB Connector | `mysql-connector-python` |
| Config | `python-dotenv` (`.env` file) |

---

## Getting Started

### Prerequisites

- **Python 3.8+** installed and available in PATH
- **MySQL Server** running locally (or accessible remotely)
- **MySQL Workbench** (optional, for manual schema execution)

### Option 1 — One-Click Launch (Windows)

Simply double-click `start.bat`. It will:
1. Install Python dependencies from `requirements.txt`
2. Load the SQL schema into MySQL (prompts for root password)
3. Launch the chat application

### Option 2 — Manual Setup

**1. Clone the repository**
```bash
git clone https://github.com/<your-username>/ChatProject.git
cd ChatProject
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set up the database**

Execute the schema file in MySQL Workbench or via terminal:
```bash
mysql -u root -p < sql/schema.sql
```

**4. Configure environment variables**

Create a `.env` file in the project root:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=chat_app_db
```

**5. Run the application**
```bash
python src/main.py
```

---

## Database Schema

The application uses a normalized relational schema with the following structure:

```
┌──────────┐     ┌──────────────┐     ┌──────────┐
│  users   │────▶│  profiles    │     │  chats   │
│          │     └──────────────┘     │          │
│  id (PK) │                          │  id (PK) │
│  username│──┐  ┌──────────────┐  ┌──│ is_group │
│  email   │  └─▶│ friendships  │  │  └──────────┘
│  password│     │ (user1,user2)│  │
└──────────┘     └──────────────┘  │  ┌───────────────────┐
      │                            ├─▶│chat_participants   │
      │    ┌───────────┐           │  │ (chat_id, user_id) │
      └───▶│ messages   │◀─────────┘  └───────────────────┘
           │ id (PK)    │
           │ chat_id(FK)│──▶ ┌─────────────────┐
           │ sender (FK)│    │ message_status   │
           │ content    │    │(msg_id, user_id) │
           └────────────┘    └─────────────────┘
                 │
                 ▼
           ┌─────────────┐
           │ attachments  │
           │ id (PK)      │
           │ message_id   │
           └─────────────┘
```

### Tables

| Table | Purpose |
|---|---|
| `users` | Core user accounts (username, email, hashed password) |
| `profiles` | Extended user profiles (bio, avatar) |
| `friendships` | User-to-user relationships with status tracking |
| `chats` | Chat rooms (supports group flag) |
| `chat_participants` | Junction table linking users to chats |
| `messages` | All messages with type classification (text/image/file) |
| `message_status` | Per-user delivery tracking (sent/delivered/read) |
| `attachments` | File attachments linked to messages |

---

## DBMS Concepts Demonstrated

This project was built to showcase practical implementation of the following SQL and database concepts:

| Concept | Where It's Used |
|---|---|
| **DDL** — `CREATE TABLE`, `CREATE VIEW`, `CREATE INDEX` | `schema.sql` — full schema definition |
| **DML** — `INSERT`, `SELECT`, `UPDATE`, `DELETE` | `backend.py` — all CRUD operations |
| **Primary Keys** (Single & Composite) | `users.id`, `(chat_id, user_id)` in `chat_participants` |
| **Foreign Keys** with `ON DELETE CASCADE` | All child tables reference parent tables |
| **CHECK Constraints** | `friendships.status`, `messages.message_type`, `message_status.status` |
| **UNIQUE Constraints** | `users.username`, `users.email` |
| **Views** | `view_latest_messages` — aggregates latest message per chat |
| **Window Functions** | `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)` in the view |
| **Common Table Expressions (CTEs)** | `backend.py → get_chat_history()` uses `WITH FormattedMessages AS (...)` |
| **JOINs** | Multi-table JOINs across `messages`, `users`, `chats`, `chat_participants` |
| **Indexes** | `idx_messages_chat_id`, `idx_messages_sender_id` for query optimization |
| **Transactions** | Explicit `COMMIT` / `ROLLBACK` in `send_message()` and `register_user()` |
| **Connection Pooling** | `MySQLConnectionPool` with pool size of 5 |
| **Parameterized Queries** | All queries use `%s` placeholders to prevent SQL injection |
| **Aggregate Queries** | `UNION ALL` with `COUNT(*)` for table statistics |
| **Password Hashing** | SHA-256 hashing before storage (security best practice) |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   main.py                           │
│         (Entry Point & Config Loader)               │
│  • Loads .env variables                             │
│  • Initializes DB connection pool                   │
│  • Launches Tkinter main loop                       │
└──────────┬──────────────────────┬───────────────────┘
           │                      │
           ▼                      ▼
┌─────────────────────┐  ┌────────────────────────────┐
│    backend.py       │  │      frontend.py           │
│  (ChatDatabase)     │  │      (ChatApp)             │
│                     │  │                            │
│ • Connection Pool   │◀─│ • Login / Register Screen  │
│ • register_user()   │  │ • Sidebar (chat list)      │
│ • login_user()      │  │ • Chat panel (messages)    │
│ • send_message()    │  │ • Background thread poll   │
│ • get_chat_history()│  │ • ScrollableFrame widget   │
│ • get_recent_chats()│  │ • New Chat dialog          │
│ • setup_new_chat()  │  └────────────────────────────┘
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   MySQL Database    │
│   (chat_app_db)     │
│  7 Tables, 1 View   │
│  2 Indexes           │
└─────────────────────┘
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DB_HOST` | `localhost` | MySQL server hostname |
| `DB_USER` | `root` | MySQL username |
| `DB_PASSWORD` | `password` | MySQL password |
| `DB_NAME` | `chat_app_db` | Target database name |

---

## License

This project is developed for academic purposes as part of the **DBMS (Semester 4)** coursework.

---

> Built with Python, MySQL, and lots of caffeine.
