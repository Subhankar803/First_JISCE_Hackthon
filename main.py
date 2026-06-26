from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, AliasChoices
from typing import List, Dict, Optional
import hashlib
from sqlalchemy.orm import Session
from sqlalchemy import func

from DataBase import SessionLocal, engine
from DataBase_Models import Base, Users, ScoreTable, Goal, ChatHistory

# Initialize Database tables
Base.metadata.create_all(bind=engine)

# Active chat sessions state machine for conversational score/subject configuration
active_chats: Dict[str, dict] = {}

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response

app = FastAPI(
    title="Student Progress Tracker API",
    description="Backend API for managing student registration, self-evaluation, study goals, and chatbot interaction.",
    version="1.0.0"
)

# Middleware to sanitize raw newlines inside JSON string fields (prevents 422 parser crashes)
class SanitizeJSONASGIMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["method"] == "POST":
            # Check content-type header
            headers = dict(scope.get("headers", []))
            content_type = headers.get(b"content-type", b"").decode("utf-8")
            if "application/json" in content_type:
                # Read all parts of the body
                body = b""
                more_body = True
                while more_body:
                    message = await receive()
                    body += message.get("body", b"")
                    more_body = message.get("more_body", False)
                
                try:
                    body_str = body.decode("utf-8")
                    in_quotes = False
                    escaped = False
                    res = []
                    for c in body_str:
                        if c == '"' and not escaped:
                            in_quotes = not in_quotes
                        if c == '\\' and not escaped:
                            escaped = True
                        else:
                            escaped = False
                        
                        if in_quotes and c in ('\n', '\r'):
                            if c == '\n':
                                res.append('\\n')
                        else:
                            res.append(c)
                    sanitized_body = "".join(res).encode("utf-8")
                except Exception:
                    sanitized_body = body
                
                # Create a new receive function that yields our sanitized body
                async def new_receive():
                    return {
                        "type": "http.request",
                        "body": sanitized_body,
                        "more_body": False
                    }
                
                await self.app(scope, new_receive, send)
                return

        await self.app(scope, receive, send)

app.add_middleware(SanitizeJSONASGIMiddleware)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production security if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB Session Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Password Hashing Helpers
def hash_password(password: str) -> str:
    salt = "jisce_hackathon_salt_2026"
    return hashlib.sha256((password + salt).encode()).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    return hash_password(password) == hashed_password


# --- Pydantic Schemas ---

class UserRegister(BaseModel):
    Name: str = Field(validation_alias=AliasChoices("Name", "name"))
    Email: str = Field(validation_alias=AliasChoices("Email", "email"))
    Password: str = Field(validation_alias=AliasChoices("Password", "password"))
    College_Name: str = Field(validation_alias=AliasChoices("College_Name", "college_name", "collegeName", "College_name"))
    Student_Id: str = Field(validation_alias=AliasChoices("Student_Id", "student_id", "studentId", "Student_ID", "student_ID", "studentID"))

class UserLogin(BaseModel):
    Student_Id: str = Field(validation_alias=AliasChoices("Student_Id", "student_id", "studentId", "Student_ID", "student_ID", "studentID"))
    Password: str = Field(validation_alias=AliasChoices("Password", "password"))

class ScoreInput(BaseModel):
    Subject_Name: str = Field(validation_alias=AliasChoices("Subject_Name", "subject_name", "subjectName", "Subject_name"))
    Score: float = Field(validation_alias=AliasChoices("Score", "score"))

class MultipleScoresInput(BaseModel):
    Student_Id: str = Field(validation_alias=AliasChoices("Student_Id", "student_id", "studentId", "Student_ID", "student_ID", "studentID"))
    Semester: int = Field(validation_alias=AliasChoices("Semester", "semester"))
    Scores: List[ScoreInput] = Field(validation_alias=AliasChoices("Scores", "scores"))

class GoalInput(BaseModel):
    Subject_Name: str = Field(validation_alias=AliasChoices("Subject_Name", "subject_name", "subjectName", "Subject_name"))
    Target_Score: float = Field(validation_alias=AliasChoices("Target_Score", "target_score", "targetScore", "Target_score"))

class MultipleGoalsInput(BaseModel):
    Student_Id: str = Field(validation_alias=AliasChoices("Student_Id", "student_id", "studentId", "Student_ID", "student_ID", "studentID"))
    Semester: int = Field(validation_alias=AliasChoices("Semester", "semester"))
    Goals: List[GoalInput] = Field(validation_alias=AliasChoices("Goals", "goals"))

class ChatInput(BaseModel):
    Student_Id: str = Field(validation_alias=AliasChoices("Student_Id", "student_id", "studentId", "Student_ID", "student_ID", "studentID"))
    Message: str = Field(validation_alias=AliasChoices("Message", "message"))


# --- API Routes ---

@app.get("/")
def read_root():
    return {"message": "Welcome to the Student Progress Tracker API!"}


@app.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    # Check if student already registered
    db_user = db.query(Users).filter(Users.Student_Id == user.Student_Id).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student ID is already registered."
        )
    
    # Check if email exists
    db_email = db.query(Users).filter(Users.Email == user.Email).first()
    if db_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already registered."
        )

    # Create new user
    hashed_pwd = hash_password(user.Password)
    max_sl = db.query(func.max(Users.Sl_No)).scalar() or 0
    new_user = Users(
        Sl_No=max_sl + 1,
        Name=user.Name,
        Email=user.Email,
        Password=hashed_pwd,
        College_Name=user.College_Name,
        Student_Id=user.Student_Id
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "message": "User registered successfully"
    }


@app.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(Users).filter(Users.Student_Id == user.Student_Id).first()
    if not db_user or not verify_password(user.Password, db_user.Password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Student ID or Password."
        )
    
    return {
        "message": "Login successful",
        "student_id": db_user.Student_Id,
        "name": db_user.Name,
        "email": db_user.Email
    }


@app.post("/score")
def submit_scores(payload: MultipleScoresInput, db: Session = Depends(get_db)):
    # Verify student exists
    db_user = db.query(Users).filter(Users.Student_Id == payload.Student_Id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found."
        )

    # Upsert subject scores
    # First calculate what the new average would be. Let's delete existing entries for these subjects first to avoid duplicates
    subject_names = [s.Subject_Name for s in payload.Scores]
    
    db.query(ScoreTable).filter(
        ScoreTable.Student_Id == payload.Student_Id,
        ScoreTable.Semester == payload.Semester,
        ScoreTable.Subject_Name.in_(subject_names)
    ).delete(synchronize_session=False)

    for item in payload.Scores:
        new_score = ScoreTable(
            Student_Id=payload.Student_Id,
            Subject_Name=item.Subject_Name,
            Score=item.Score,
            Average_Score=0.0,  # Will update in next step
            Semester=payload.Semester
        )
        db.add(new_score)
    
    db.commit()

    # Ensure corresponding Goal entries exist in the Goal Table
    for item in payload.Scores:
        existing_goal = db.query(Goal).filter(
            Goal.Student_Id == payload.Student_Id,
            Goal.Semester == payload.Semester,
            func.lower(Goal.Subject_Name) == item.Subject_Name.lower()
        ).first()
        
        if not existing_goal:
            new_goal = Goal(
                Student_Id=payload.Student_Id,
                Subject_Name=item.Subject_Name,
                Semester=payload.Semester,
                Target_Score=0.0
            )
            db.add(new_goal)
    db.commit()

    # Recalculate average score for this semester
    scores_query = db.query(ScoreTable).filter(
        ScoreTable.Student_Id == payload.Student_Id,
        ScoreTable.Semester == payload.Semester
    ).all()
    
    if scores_query:
        avg_score = sum(sq.Score for sq in scores_query) / len(scores_query)
        # Update all records for this student/semester to the new average score
        for sq in scores_query:
            sq.Average_Score = avg_score
        db.commit()
    else:
        avg_score = 0.0

    return {
        "message": "Scores updated successfully",
        "semester": payload.Semester,
        "new_average_score": round(avg_score, 2)
    }


@app.post("/goals")
def set_goals(payload: MultipleGoalsInput, db: Session = Depends(get_db)):
    # Verify student exists
    db_user = db.query(Users).filter(Users.Student_Id == payload.Student_Id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found."
        )

    # Verify that all requested goal subjects exist in the student's subjects list (ScoreTable) for that semester
    for item in payload.Goals:
        exists = db.query(ScoreTable).filter(
            ScoreTable.Student_Id == payload.Student_Id,
            ScoreTable.Semester == payload.Semester,
            func.lower(ScoreTable.Subject_Name) == item.Subject_Name.lower()
        ).first() is not None
        
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Subject '{item.Subject_Name}' is not in your current semester subjects. Please submit scores for it first."
            )

    # Update target scores for these subjects (since they are guaranteed to exist in Goal, we update them)
    for item in payload.Goals:
        db_goal = db.query(Goal).filter(
            Goal.Student_Id == payload.Student_Id,
            Goal.Semester == payload.Semester,
            func.lower(Goal.Subject_Name) == item.Subject_Name.lower()
        ).first()
        
        if db_goal:
            db_goal.Target_Score = item.Target_Score
        else:
            new_goal = Goal(
                Student_Id=payload.Student_Id,
                Subject_Name=item.Subject_Name,
                Semester=payload.Semester,
                Target_Score=item.Target_Score
            )
            db.add(new_goal)
            
    db.commit()

    return {"message": "Goals updated successfully", "semester": payload.Semester}

def generate_ai_response(student_id: str, message: str, db: Session) -> str:
    """
    Placeholder function for AI response generation.
    You can train and integrate your custom ML/AI model or API (like OpenAI, Ollama, custom LLM, etc.) here.
    
    Access student scores/history via the `db` session if needed.
    """
    # TODO: Replace with your actual trained model inference or API call.
    return f"Hello! This is a placeholder AI response to: '{message}'. Integrate your custom trained ML model here."


@app.post("/chat")
def chat_with_bot(payload: ChatInput, db: Session = Depends(get_db)):
    # Verify student exists
    student = db.query(Users).filter(Users.Student_Id == payload.Student_Id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not registered."
        )

    # Generate response using the custom/trained AI model
    bot_response = generate_ai_response(payload.Student_Id, payload.Message, db)

    # Save to Chat History
    chat_entry = ChatHistory(
        Student_Id=payload.Student_Id,
        Previous_Chat=f"User: {payload.Message}\nBot: {bot_response}"
    )
    db.add(chat_entry)
    db.commit()

    return {
        "bot_response": bot_response,
        "time": chat_entry.Time
    }


@app.get("/chat/history/{student_id:path}", response_model=List[Dict])
def get_chat_history(student_id: str, db: Session = Depends(get_db)):
    # Check if student exists
    student = db.query(Users).filter(Users.Student_Id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found."
        )

    history = db.query(ChatHistory).filter(
        ChatHistory.Student_Id == student_id
    ).order_by(ChatHistory.Time.asc()).all()

    return [
        {
            "chat_id": h.Chat_Id,
            "previous_chat": h.Previous_Chat,
            "time": h.Time
        }
        for h in history
    ]


@app.get("/dashboard/{student_id:path}")
def get_dashboard_data(student_id: str, db: Session = Depends(get_db)):
    student = db.query(Users).filter(Users.Student_Id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found."
        )

    scores = db.query(ScoreTable).filter(ScoreTable.Student_Id == student_id).all()
    goals = db.query(Goal).filter(Goal.Student_Id == student_id).all()

    # Formulate output structure
    scores_list = [
        {
            "subject_name": s.Subject_Name,
            "score": s.Score,
            "average_score": s.Average_Score,
            "semester": s.Semester
        }
        for s in scores
    ]

    goals_list = [
        {
            "subject_name": g.Subject_Name,
            "semester": g.Semester,
            "target_score": g.Target_Score
        }
        for g in goals
    ]

    # Calculate overall stats
    total_subjects = len(scores_list)
    average_of_averages = 0.0
    if total_subjects > 0:
        unique_sems = set(s["semester"] for s in scores_list)
        averages = []
        for sem in unique_sems:
            sem_scores = [s["score"] for s in scores_list if s["semester"] == sem]
            averages.append(sum(sem_scores) / len(sem_scores))
        average_of_averages = sum(averages) / len(averages)

    return {
        "profile": {
            "name": student.Name,
            "email": student.Email,
            "college_name": student.College_Name,
            "student_id": student.Student_Id,
            "registration_time": student.Registration_time
        },
        "scores": scores_list,
        "goals": goals_list,
        "stats": {
            "total_subjects_tracked": total_subjects,
            "overall_average_score": round(average_of_averages, 2)
        }
    }
