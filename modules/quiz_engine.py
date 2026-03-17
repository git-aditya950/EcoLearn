"""
Quiz Engine for EcoLearn.
Handles quiz logic, question management, scoring, and streak tracking.
"""

import json
import random
from datetime import datetime
from sqlalchemy.orm import Session
from database.db_setup import Quiz, Question, Answer, QuizAttempt, Lesson, Session
from config import QUIZ_CATEGORIES, DIFFICULTY_LEVELS


class QuizEngine:
    """Main quiz engine for managing quizzes and scoring."""
    
    @staticmethod
    def create_quiz(lesson_id: int, title: str, description: str = '', 
                   passing_score: float = 70.0) -> dict:
        """
        Create a new quiz.
        
        Args:
            lesson_id: Parent lesson ID
            title: Quiz title
            description: Quiz description
            passing_score: Minimum percentage to pass
            
        Returns:
            Dictionary with success status and quiz data
        """
        session = Session()
        try:
            quiz = Quiz(
                lesson_id=lesson_id,
                title=title,
                description=description,
                passing_score=passing_score,
                is_published=False
            )
            session.add(quiz)
            session.commit()
            
            return {
                'success': True,
                'message': 'Quiz created successfully',
                'quiz_id': quiz.id
            }
        
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f'Failed to create quiz: {str(e)}'}
        
        finally:
            session.close()
    
    @staticmethod
    def add_question(quiz_id: int, question_text: str, question_type: str,
                    options: list, correct_answer: str, points: float = 1.0) -> dict:
        """
        Add a question to a quiz.
        
        Args:
            quiz_id: Parent quiz ID
            question_text: The question text
            question_type: Type of question (multiple_choice, true_false, short_answer)
            options: List of answer options (JSON format)
            correct_answer: The correct answer
            points: Points for this question
            
        Returns:
            Dictionary with success status
        """
        session = Session()
        try:
            # Get the next order number
            last_question = session.query(Question).filter(
                Question.quiz_id == quiz_id
            ).order_by(Question.order.desc()).first()
            
            next_order = (last_question.order + 1) if last_question else 1
            
            question = Question(
                quiz_id=quiz_id,
                question_text=question_text,
                question_type=question_type,
                options=json.dumps(options) if isinstance(options, list) else options,
                correct_answer=correct_answer,
                order=next_order,
                points=points
            )
            
            session.add(question)
            session.commit()
            
            return {
                'success': True,
                'message': 'Question added successfully',
                'question_id': question.id
            }
        
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f'Failed to add question: {str(e)}'}
        
        finally:
            session.close()
    
    @staticmethod
    def get_quiz_questions(quiz_id: int) -> dict:
        """Get all questions for a quiz."""
        session = Session()
        try:
            quiz = session.query(Quiz).filter(Quiz.id == quiz_id).first()
            
            if not quiz:
                return {'success': False, 'message': 'Quiz not found'}
            
            questions = session.query(Question).filter(
                Question.quiz_id == quiz_id
            ).order_by(Question.order).all()
            
            questions_data = []
            for q in questions:
                questions_data.append({
                    'id': q.id,
                    'question_text': q.question_text,
                    'question_type': q.question_type,
                    'options': json.loads(q.options) if q.options else [],
                    'points': q.points,
                    'order': q.order
                })
            
            return {
                'success': True,
                'quiz': {
                    'id': quiz.id,
                    'title': quiz.title,
                    'description': quiz.description,
                    'passing_score': quiz.passing_score
                },
                'questions': questions_data
            }
        
        finally:
            session.close()
    
    @staticmethod
    def start_quiz_attempt(user_id: int, quiz_id: int) -> dict:
        """Start a new quiz attempt."""
        session = Session()
        try:
            attempt = QuizAttempt(
                user_id=user_id,
                quiz_id=quiz_id,
                started_at=datetime.utcnow()
            )
            session.add(attempt)
            session.commit()
            
            return {
                'success': True,
                'attempt_id': attempt.id,
                'started_at': attempt.started_at.isoformat()
            }
        
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f'Failed to start quiz: {str(e)}'}
        
        finally:
            session.close()
    
    @staticmethod
    def submit_answer(attempt_id: int, question_id: int, user_answer: str, 
                     is_correct: bool, score: float = 0.0) -> dict:
        """Record a user's answer to a question."""
        session = Session()
        try:
            answer = Answer(
                question_id=question_id,
                quiz_attempt_id=attempt_id,
                user_answer=user_answer,
                is_correct=is_correct,
                score=score if is_correct else 0.0
            )
            session.add(answer)
            session.commit()
            
            return {
                'success': True,
                'answer_id': answer.id,
                'score': score if is_correct else 0.0
            }
        
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f'Failed to submit answer: {str(e)}'}
        
        finally:
            session.close()
    
    @staticmethod
    def finish_quiz_attempt(attempt_id: int, time_spent_seconds: int) -> dict:
        """Finalize a quiz attempt and calculate score."""
        session = Session()
        try:
            attempt = session.query(QuizAttempt).filter(
                QuizAttempt.id == attempt_id
            ).first()
            
            if not attempt:
                return {'success': False, 'message': 'Quiz attempt not found'}
            
            # Get all answers for this attempt
            answers = session.query(Answer).filter(
                Answer.quiz_attempt_id == attempt_id
            ).all()
            
            # Calculate total score
            total_points_earned = sum(a.score for a in answers)
            
            # Get total possible points
            questions = session.query(Question).filter(
                Question.quiz_id == attempt.quiz_id
            ).all()
            total_possible_points = sum(q.points for q in questions)
            
            # Calculate percentage score
            score_percentage = (total_points_earned / total_possible_points * 100) if total_possible_points > 0 else 0
            
            # Check if passed
            quiz = session.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
            passed = score_percentage >= quiz.passing_score
            
            # Update attempt
            attempt.score = score_percentage
            attempt.passed = passed
            attempt.completed_at = datetime.utcnow()
            attempt.time_spent_seconds = time_spent_seconds
            
            session.commit()
            
            return {
                'success': True,
                'attempt_id': attempt_id,
                'score': round(score_percentage, 2),
                'passed': passed,
                'time_spent': time_spent_seconds,
                'total_questions': len(questions)
            }
        
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f'Failed to complete quiz: {str(e)}'}
        
        finally:
            session.close()
    
    @staticmethod
    def get_user_quiz_stats(user_id: int) -> dict:
        """Get user's quiz statistics."""
        session = Session()
        try:
            attempts = session.query(QuizAttempt).filter(
                QuizAttempt.user_id == user_id
            ).all()
            
            if not attempts:
                return {
                    'success': True,
                    'total_attempts': 0,
                    'average_score': 0,
                    'total_passed': 0,
                    'quiz_attempts': []
                }
            
            total_attempts = len(attempts)
            total_passed = sum(1 for a in attempts if a.passed)
            average_score = sum(a.score for a in attempts if a.score is not None) / total_attempts if total_attempts > 0 else 0
            
            attempts_data = []
            for attempt in attempts:
                quiz = session.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
                attempts_data.append({
                    'quiz_id': attempt.quiz_id,
                    'quiz_title': quiz.title if quiz else 'Unknown',
                    'score': attempt.score,
                    'passed': attempt.passed,
                    'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None,
                    'time_spent': attempt.time_spent_seconds
                })
            
            return {
                'success': True,
                'total_attempts': total_attempts,
                'average_score': round(average_score, 2),
                'total_passed': total_passed,
                'quiz_attempts': attempts_data
            }
        
        finally:
            session.close()


class QuestionBank:
    """Manages the question database and filtering."""
    
    @staticmethod
    def get_questions_by_category(category: str, difficulty: str = None) -> list:
        """Get questions filtered by category and optionally difficulty."""
        session = Session()
        try:
            # This is a placeholder - would need to extend Question model with category/difficulty
            return []
        finally:
            session.close()
    
    @staticmethod
    def get_random_questions(quiz_id: int, count: int = 10) -> list:
        """Get random questions from a quiz."""
        session = Session()
        try:
            questions = session.query(Question).filter(
                Question.quiz_id == quiz_id
            ).all()
            
            return random.sample(questions, min(count, len(questions)))
        
        finally:
            session.close()
