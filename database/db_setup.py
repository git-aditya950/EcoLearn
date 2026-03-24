"""
Database setup and schema configuration for EcoLearn.
This module initializes the database with SQLAlchemy ORM models.
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///ecolearn.db')
engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class User(Base):
    """User model for students, teachers, and admins."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default='student')  # 'student', 'teacher', 'admin'
    first_name = Column(String(80))
    last_name = Column(String(80))
    bio = Column(Text)
    avatar_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    enrollments = relationship('Enrollment', back_populates='user', cascade='all, delete-orphan')
    progress_records = relationship('Progress', back_populates='user', cascade='all, delete-orphan')
    quiz_attempts = relationship('QuizAttempt', back_populates='user', cascade='all, delete-orphan')
    courses_created = relationship('Course', back_populates='instructor', foreign_keys='Course.instructor_id')
    
    def __repr__(self):
        return f'<User {self.username}>'


class Course(Base):
    """Course model for educational programs."""
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    instructor_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category = Column(String(100))  # e.g., 'Climate Change', 'Biodiversity', 'Sustainability'
    difficulty_level = Column(String(20), default='beginner')  # 'beginner', 'intermediate', 'advanced'
    thumbnail_url = Column(String(255))
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    instructor = relationship('User', back_populates='courses_created', foreign_keys=[instructor_id])
    lessons = relationship('Lesson', back_populates='course', cascade='all, delete-orphan')
    enrollments = relationship('Enrollment', back_populates='course', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Course {self.title}>'


class Lesson(Base):
    """Lesson model for course content."""
    __tablename__ = 'lessons'
    
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    order = Column(Integer)  # Position in the course
    video_url = Column(String(255))
    duration_minutes = Column(Integer)  # Duration in minutes
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = relationship('Course', back_populates='lessons')
    quizzes = relationship('Quiz', back_populates='lesson', cascade='all, delete-orphan')
    progress_records = relationship('Progress', back_populates='lesson', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Lesson {self.title}>'


class Quiz(Base):
    """Quiz model for assessments."""
    __tablename__ = 'quizzes'
    
    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey('lessons.id'), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    passing_score = Column(Float, default=70.0)  # Percentage
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lesson = relationship('Lesson', back_populates='quizzes')
    questions = relationship('Question', back_populates='quiz', cascade='all, delete-orphan')
    attempts = relationship('QuizAttempt', back_populates='quiz', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Quiz {self.title}>'


class Question(Base):
    """Question model for quiz questions."""
    __tablename__ = 'questions'
    
    id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer, ForeignKey('quizzes.id'), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), default='multiple_choice')  # 'multiple_choice', 'short_answer', 'true_false'
    options = Column(Text)  # JSON array of options
    correct_answer = Column(Text)  # Correct answer or answer key
    order = Column(Integer)
    points = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    quiz = relationship('Quiz', back_populates='questions')
    answers = relationship('Answer', back_populates='question', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Question {self.id}>'


class Answer(Base):
    """Answer model for user responses to quiz questions."""
    __tablename__ = 'answers'
    
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    quiz_attempt_id = Column(Integer, ForeignKey('quiz_attempts.id'), nullable=False)
    user_answer = Column(Text)
    is_correct = Column(Boolean)
    score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    question = relationship('Question', back_populates='answers')
    quiz_attempt = relationship('QuizAttempt', back_populates='answers')
    
    def __repr__(self):
        return f'<Answer {self.id}>'


class QuizAttempt(Base):
    """QuizAttempt model to track user quiz attempts."""
    __tablename__ = 'quiz_attempts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    quiz_id = Column(Integer, ForeignKey('quizzes.id'), nullable=False)
    score = Column(Float)  # Final score in percentage
    passed = Column(Boolean, default=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    time_spent_seconds = Column(Integer)  # Time spent on quiz in seconds
    
    # Relationships
    user = relationship('User', back_populates='quiz_attempts')
    quiz = relationship('Quiz', back_populates='attempts')
    answers = relationship('Answer', back_populates='quiz_attempt', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<QuizAttempt user={self.user_id} quiz={self.quiz_id}>'


class Enrollment(Base):
    """Enrollment model for course enrollment."""
    __tablename__ = 'enrollments'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    progress_percentage = Column(Float, default=0.0)
    
    # Relationships
    user = relationship('User', back_populates='enrollments')
    course = relationship('Course', back_populates='enrollments')
    
    def __repr__(self):
        return f'<Enrollment user={self.user_id} course={self.course_id}>'


class Progress(Base):
    """Progress model to track user progress on lessons."""
    __tablename__ = 'progress'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    lesson_id = Column(Integer, ForeignKey('lessons.id'), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    is_completed = Column(Boolean, default=False)
    time_spent_seconds = Column(Integer, default=0)
    
    # Relationships
    user = relationship('User', back_populates='progress_records')
    lesson = relationship('Lesson', back_populates='progress_records')
    
    def __repr__(self):
        return f'<Progress user={self.user_id} lesson={self.lesson_id}>'


class Achievement(Base):
    """Achievement model for badges and rewards."""
    __tablename__ = 'achievements'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    badge_url = Column(String(255))
    criteria = Column(Text)  # Description of how to earn this achievement
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Achievement {self.name}>'


class PasswordReset(Base):
    """PasswordReset model for password reset tokens."""
    __tablename__ = 'password_resets'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    reset_token = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(120), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)  # Token expires after 24 hours
    used_at = Column(DateTime)  # When the token was used
    
    # Relationships
    user = relationship('User')
    
    def __repr__(self):
        return f'<PasswordReset user={self.user_id}>'



def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(engine)
    print("[+] Database initialized successfully!")
    print(f"[+] Database URL: {DATABASE_URL}")


def drop_db():
    """Drop all tables from the database (use with caution)."""
    Base.metadata.drop_all(engine)
    print("[+] All tables dropped!")


if __name__ == '__main__':
    init_db()
