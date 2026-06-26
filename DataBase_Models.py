from sqlalchemy import Column, Float, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Users(Base):
    __tablename__ = "Registered_Users"
    Sl_No = Column(Integer, unique=True, nullable=True)
    Name = Column(String(100), nullable=False)
    Email = Column(String(100), nullable=False, unique=True)
    Password = Column(String(100), nullable=False)
    College_Name = Column(String(100), nullable=False)
    Student_Id = Column(String(100), nullable=False, unique=True, primary_key=True)
    Registration_time = Column(DateTime, default=func.now())

class ScoreTable(Base):
    __tablename__ = "Score_Table"
    Sl_No = Column(Integer, autoincrement=True, primary_key=True)
    Student_Id = Column(String(100), ForeignKey("Registered_Users.Student_Id"))
    Subject_Name = Column(String(100), nullable=False)
    Score = Column(Float, nullable=False)
    Average_Score = Column(Float, nullable=False)
    Semester = Column(Integer, nullable=False)

class ChatHistory(Base):
    __tablename__ = "Chat_History"
    Student_Id = Column(String(100), ForeignKey("Registered_Users.Student_Id"))
    Previous_Chat = Column(LONGTEXT, nullable=False)
    Time = Column(DateTime, default=func.now())
    Chat_Id = Column(Integer, autoincrement=True, primary_key=True)

class Goal(Base):
    __tablename__ = "Goal_Table"
    Sl_No = Column(Integer, autoincrement=True, primary_key=True)
    Student_Id = Column(String(100), ForeignKey("Registered_Users.Student_Id"))
    Subject_Name = Column(String(100), nullable=False)
    Semester = Column(Integer, nullable=False)
    Target_Score = Column(Float, nullable=False)