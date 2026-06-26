# First_JISCE_Hackthon

# 🎓 SemBot — AI-Powered Student Progress Chatbot

> Built for the **1st JISCE Hackathon** by Team [Your Team Name]

SemBot is an interactive AI chatbot that helps college students track their subject scores, set semester goals, and receive personalized study suggestions — all through a conversational interface.

---

## 💡 The Problem

Students often lose track of their academic performance mid-semester. They lack a simple, personalized tool that can look at their current scores, understand their goals, and tell them *exactly* what they need to do to hit their target.

## ✅ Our Solution

SemBot lets a student:
1. Register and log in with their college credentials
2. Enter their subject scores for the semester
3. Set target scores for each subject
4. Chat with an AI that reads their score data and gives tailored, actionable advice

---

## 🖼️ Architecture Overview

```
Home Page
├── Register → Collects Name, College, Email, Password, Student ID → Stored in DB
└── Login    → Validates credentials → Redirects to Dashboard

Dashboard
├── Enter Scores (per subject, per semester)
├── Set Goals   (target score per subject)
└── Chat        → AI reads score + goal data → gives progress suggestions
                → All chats stored in Chat History DB
```

---

## 🗄️ Database Schema

### `users` — Registered Students
| Column | Type | Description |
|---|---|---|
| Sl_No | Integer | Auto-increment serial |
| Name | String | Student's full name |
| Email | String | Unique email address |
| Password | String | SHA-256 hashed password |
| College_Name | String | College/Institution name |
| Student_Id | String (PK) | Unique student roll number |
| Registration_time | DateTime | Timestamp of registration |

### `score_table` — Subject Scores
| Column | Type | Description |
|---|---|---|
| Id | Integer (PK) | Auto-increment |
| Student_Id | String (FK) | Links to Users |
| Subject_Name | String | Subject name |
| Score | Float | Score obtained |
| Average_Score | Float | Semester average (auto-calculated) |
| Semester | Integer | Semester number |

### `goal` — Target Scores
| Column | Type | Description |
|---|---|---|
| Id | Integer (PK) | Auto-increment |
| Student_Id | String (FK) | Links to Users |
| Subject_Name | String | Subject name |
| Target_Score | Float | Student's target score |
| Semester | Integer | Semester number |

### `chat_history` — Conversation Logs
| Column | Type | Description |
|---|---|---|
| Chat_Id | Integer (PK) | Auto-increment |
| Student_Id | String (FK) | Links to Users |
| Previous_Chat | Text | Full conversation stored as text |
| Time | DateTime | Timestamp of message |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| ORM | SQLAlchemy |
| Database | SQLite (dev) |
| Auth | SHA-256 password hashing |
| Frontend | HTML, CSS, JavaScript (Vanilla / Tailwind) |
| AI/Chatbot | Custom-trained model / LLM API integration |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/Subhankar803/First_JISCE_Hackthon.git
cd First_JISCE_Hackthon

# Install dependencies
pip install fastapi uvicorn sqlalchemy pydantic

# Run the server
uvicorn main:app --reload
```

The API will be live at `http://localhost:8000`

### API Documentation

FastAPI auto-generates interactive docs. Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/register` | Register a new student |
| POST | `/login` | Authenticate a student |
| POST | `/score` | Submit subject scores for a semester |
| POST | `/goals` | Set target scores for subjects |
| POST | `/chat` | Send a message to the AI chatbot |
| GET | `/chat/history/{student_id}` | Retrieve full chat history |
| GET | `/dashboard/{student_id}` | Get profile, scores, goals & stats |

---

## 🔄 User Flow

```
Register ──► Login ──► Submit Scores ──► Set Goals ──► Chat with SemBot
                             │                               │
                             └── Stored in score_table       └── AI reads scores + goals
                                                                 → Gives suggestions
                                                                 → Saved in chat_history
```

---

## 🤖 How the Chatbot Works

On first interaction, SemBot reads the student's score and goal data from the database. It compares current scores against target scores for each subject and generates personalized suggestions — which subjects need more focus, how much improvement is needed, and a motivational push to keep going.

> Chat history is persisted per user so the bot can refer to past conversations in future sessions.

---

## 👥 Team

| Name | Role |
|---|---|
| Subhankar | Backend & Database |
| Gopu | Frontend & Integration |
| [Add teammate] | [Role] |

*Built at the 1st JISCE Hackathon, 2026*

---

## 📄 License

This project is open-source and free to use for educational purposes.
