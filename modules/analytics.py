"""
Analytics Module for EcoLearn.
Provides data analysis, visualization, and reporting for students and teachers.
"""

import pandas as pd
import io
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.db_setup import User, QuizAttempt, Enrollment, Progress, Course, Lesson, Quiz, Session


class AnalyticsEngine:
    """Main analytics engine for data analysis and insights."""
    
    @staticmethod
    def get_student_progress_report(user_id: int) -> dict:
        """Generate a comprehensive progress report for a student."""
        session = Session()
        try:
            # Get user
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # Get quiz statistics
            attempts = session.query(QuizAttempt).filter(
                QuizAttempt.user_id == user_id
            ).all()
            
            # Get enrollments and progress
            enrollments = session.query(Enrollment).filter(
                Enrollment.user_id == user_id
            ).all()
            
            progress_records = session.query(Progress).filter(
                Progress.user_id == user_id
            ).all()
            
            # Calculate statistics
            total_quizzes = len(attempts)
            completed_quizzes = len([a for a in attempts if a.completed_at])
            passed_quizzes = len([a for a in attempts if a.passed])
            
            avg_score = 0
            if attempts and any(a.score for a in attempts):
                valid_scores = [a.score for a in attempts if a.score is not None]
                avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0
            
            total_time_spent = sum(a.time_spent_seconds for a in attempts if a.time_spent_seconds) or 0
            
            # Get completed courses
            completed_courses = len([e for e in enrollments if e.completed_at])
            
            return {
                'success': True,
                'student': {
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                },
                'quiz_stats': {
                    'total_attempted': total_quizzes,
                    'completed': completed_quizzes,
                    'passed': passed_quizzes,
                    'pass_rate': round((passed_quizzes / completed_quizzes * 100) if completed_quizzes else 0, 2),
                    'average_score': round(avg_score, 2)
                },
                'time_stats': {
                    'total_time_minutes': round(total_time_spent / 60, 2)
                },
                'course_stats': {
                    'total_enrolled': len(enrollments),
                    'completed_courses': completed_courses
                },
                'lesson_stats': {
                    'lessons_started': len(progress_records),
                    'lessons_completed': len([p for p in progress_records if p.is_completed])
                }
            }
        
        finally:
            session.close()
    
    @staticmethod
    def get_class_performance_report(course_id: int) -> dict:
        """Generate class performance report for a teacher."""
        session = Session()
        try:
            # Get course
            course = session.query(Course).filter(Course.id == course_id).first()
            if not course:
                return {'success': False, 'message': 'Course not found'}
            
            # Get enrollments
            enrollments = session.query(Enrollment).filter(
                Enrollment.course_id == course_id
            ).all()
            
            if not enrollments:
                return {
                    'success': True,
                    'course': course.title,
                    'message': 'No students enrolled yet'
                }
            
            # Build performance data
            student_performance = []
            
            for enrollment in enrollments:
                user = enrollment.user
                attempts = session.query(QuizAttempt).filter(
                    QuizAttempt.user_id == user.id
                ).all()
                
                avg_score = 0
                if attempts and any(a.score for a in attempts):
                    valid_scores = [a.score for a in attempts if a.score is not None]
                    avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0
                
                student_performance.append({
                    'username': user.username,
                    'quizzes_completed': len([a for a in attempts if a.completed_at]),
                    'average_score': round(avg_score, 2),
                    'pass_rate': round(len([a for a in attempts if a.passed]) / max(len(attempts), 1) * 100, 2),
                    'progress': enrollment.progress_percentage
                })
            
            return {
                'success': True,
                'course': course.title,
                'total_students': len(enrollments),
                'class_average': round(sum(s['average_score'] for s in student_performance) / len(student_performance), 2),
                'student_performance': student_performance
            }
        
        finally:
            session.close()
    
    @staticmethod
    def get_weak_topics(course_id: int) -> dict:
        """Identify weak topics/lessons where students struggle."""
        session = Session()
        try:
            # Get all quizzes in course
            course = session.query(Course).filter(Course.id == course_id).first()
            if not course:
                return {'success': False, 'message': 'Course not found'}
            
            lessons = session.query(Lesson).filter(
                Lesson.course_id == course_id
            ).all()
            
            weak_topics = []
            
            for lesson in lessons:
                quizzes = session.query(Quiz).filter(
                    Quiz.lesson_id == lesson.id
                ).all()
                
                if not quizzes:
                    continue
                
                # Get all attempts for quizzes in this lesson
                all_scores = []
                for quiz in quizzes:
                    attempts = session.query(QuizAttempt).filter(
                        QuizAttempt.quiz_id == quiz.id
                    ).all()
                    
                    for attempt in attempts:
                        if attempt.score is not None:
                            all_scores.append(attempt.score)
                
                if all_scores:
                    avg_score = sum(all_scores) / len(all_scores)
                    
                    weak_topics.append({
                        'lesson': lesson.title,
                        'average_score': round(avg_score, 2),
                        'total_attempts': len(all_scores),
                        'difficulty': 'High' if avg_score < 60 else 'Medium' if avg_score < 80 else 'Low'
                    })
            
            # Sort by average score (lowest first)
            weak_topics.sort(key=lambda x: x['average_score'])
            
            return {
                'success': True,
                'course': course.title,
                'weak_topics': weak_topics[:5]  # Top 5 weak topics
            }
        
        finally:
            session.close()


class DataFrameBuilder:
    """Helper class to convert database records to pandas DataFrames."""
    
    @staticmethod
    def user_quiz_performance_df(user_id: int) -> pd.DataFrame:
        """Build DataFrame of user's quiz attempts."""
        session = Session()
        try:
            attempts = session.query(QuizAttempt).filter(
                QuizAttempt.user_id == user_id
            ).all()
            
            data = []
            for attempt in attempts:
                quiz = session.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
                
                data.append({
                    'Date': attempt.started_at,
                    'Quiz': quiz.title if quiz else 'Unknown',
                    'Score': attempt.score,
                    'Passed': attempt.passed,
                    'Time (min)': attempt.time_spent_seconds // 60 if attempt.time_spent_seconds else 0
                })
            
            if not data:
                return pd.DataFrame()
            
            df = pd.DataFrame(data)
            df['Date'] = pd.to_datetime(df['Date'])
            
            return df
        
        finally:
            session.close()
    
    @staticmethod
    def class_performance_df(course_id: int) -> pd.DataFrame:
        """Build DataFrame of class performance."""
        session = Session()
        try:
            enrollments = session.query(Enrollment).filter(
                Enrollment.course_id == course_id
            ).all()
            
            data = []
            for enrollment in enrollments:
                user = enrollment.user
                attempts = session.query(QuizAttempt).filter(
                    QuizAttempt.user_id == user.id
                ).all()
                
                avg_score = 0
                if attempts and any(a.score for a in attempts):
                    valid_scores = [a.score for a in attempts if a.score is not None]
                    avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0
                
                data.append({
                    'Student': user.username,
                    'Quizzes': len([a for a in attempts if a.completed_at]),
                    'Avg Score': round(avg_score, 2),
                    'Progress': enrollment.progress_percentage
                })
            
            if not data:
                return pd.DataFrame()
            
            return pd.DataFrame(data)
        
        finally:
            session.close()


class ReportGenerator:
    """Generate PDF and other reports."""
    
    @staticmethod
    def export_student_report_csv(user_id: int) -> io.BytesIO:
        """Export student report as CSV."""
        session = Session()
        try:
            df = DataFrameBuilder.user_quiz_performance_df(user_id)
            
            output = io.BytesIO()
            df.to_csv(output, index=False)
            output.seek(0)
            
            return output
        
        finally:
            session.close()
    
    @staticmethod
    def export_class_report_csv(course_id: int) -> io.BytesIO:
        """Export class performance report as CSV."""
        session = Session()
        try:
            df = DataFrameBuilder.class_performance_df(course_id)
            
            output = io.BytesIO()
            df.to_csv(output, index=False)
            output.seek(0)
            
            return output
        
        finally:
            session.close()
