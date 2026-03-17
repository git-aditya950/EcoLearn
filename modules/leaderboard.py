"""
Leaderboard Module for EcoLearn.
Manages global, class-wise, and school-wise leaderboards.
"""

from sqlalchemy.orm import Session
from database.db_setup import User, QuizAttempt, Enrollment, Course, Session
from config import LEVELS


class LeaderboardManager:
    """Manages leaderboard calculations and rankings."""
    
    @staticmethod
    def _calculate_user_xp(user_id: int) -> int:
        """Calculate total XP for a user based on quiz performance."""
        session = Session()
        try:
            attempts = session.query(QuizAttempt).filter(
                QuizAttempt.user_id == user_id,
                QuizAttempt.score.isnot(None)
            ).all()
            
            total_xp = 0
            for attempt in attempts:
                # Award XP based on score (10 points per percent)
                total_xp += int(attempt.score)
            
            return total_xp
        
        finally:
            session.close()
    
    @staticmethod
    def get_global_leaderboard(limit: int = 100) -> dict:
        """Get top users globally ranked by level and XP."""
        session = Session()
        try:
            users = session.query(User).filter(User.is_active == True).all()
            
            rankings = []
            
            for user in users:
                xp = LeaderboardManager._calculate_user_xp(user.id)
                xp_per_level = 100
                level = (xp // xp_per_level) + 1
                level_name = LEVELS[min(level - 1, len(LEVELS) - 1)]
                
                attempts = session.query(QuizAttempt).filter(
                    QuizAttempt.user_id == user.id,
                    QuizAttempt.score.isnot(None)
                ).all()
                
                quizzes_completed = len([a for a in attempts if a.completed_at])
                
                rankings.append({
                    'user_id': user.id,
                    'username': user.username,
                    'level': level,
                    'level_name': level_name,
                    'xp': xp,
                    'quizzes_completed': quizzes_completed,
                    'avatar_url': user.avatar_url
                })
            
            # Sort by level (desc) then XP (desc)
            rankings.sort(key=lambda x: (-x['level'], -x['xp']))
            
            # Add ranks
            for idx, entry in enumerate(rankings[:limit], 1):
                entry['rank'] = idx
            
            return {
                'success': True,
                'leaderboard_type': 'global',
                'total_users': len(rankings),
                'leaderboard': rankings[:limit]
            }
        
        finally:
            session.close()
    
    @staticmethod
    def get_course_leaderboard(course_id: int, limit: int = 50) -> dict:
        """Get leaderboard for students in a specific course."""
        session = Session()
        try:
            # Get course
            course = session.query(Course).filter(Course.id == course_id).first()
            
            if not course:
                return {'success': False, 'message': 'Course not found'}
            
            # Get enrolled students
            enrollments = session.query(Enrollment).filter(
                Enrollment.course_id == course_id
            ).all()
            
            rankings = []
            
            for enrollment in enrollments:
                user = enrollment.user
                
                # Get quiz attempts for this user
                attempts = session.query(QuizAttempt).filter(
                    QuizAttempt.user_id == user.id,
                    QuizAttempt.score.isnot(None)
                ).all()
                
                avg_score = 0
                if attempts:
                    valid_scores = [a.score for a in attempts if a.score is not None]
                    avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0
                
                rankings.append({
                    'user_id': user.id,
                    'username': user.username,
                    'average_score': round(avg_score, 2),
                    'quizzes_completed': len([a for a in attempts if a.completed_at]),
                    'progress': enrollment.progress_percentage
                })
            
            # Sort by average score (desc)
            rankings.sort(key=lambda x: -x['average_score'])
            
            # Add ranks
            for idx, entry in enumerate(rankings[:limit], 1):
                entry['rank'] = idx
            
            return {
                'success': True,
                'leaderboard_type': 'course',
                'course': course.title,
                'total_students': len(rankings),
                'leaderboard': rankings[:limit]
            }
        
        finally:
            session.close()
    
    @staticmethod
    def get_user_rank(user_id: int) -> dict:
        """Get a user's rank on the global leaderboard."""
        result = LeaderboardManager.get_global_leaderboard(limit=10000)
        
        if not result['success']:
            return {'success': False, 'message': 'Failed to fetch leaderboard'}
        
        for user_data in result['leaderboard']:
            if user_data['user_id'] == user_id:
                return {
                    'success': True,
                    'rank': user_data['rank'],
                    'level': user_data['level'],
                    'level_name': user_data['level_name'],
                    'xp': user_data['xp'],
                    'total_users': result['total_users']
                }
        
        return {'success': False, 'message': 'User not ranked yet'}
    
    @staticmethod
    def get_friends_leaderboard(user_id: int, friend_ids: list, limit: int = 20) -> dict:
        """Get leaderboard for a user's friends."""
        session = Session()
        try:
            rankings = []
            
            # Include the user themselves
            all_user_ids = [user_id] + friend_ids
            
            for uid in all_user_ids:
                user = session.query(User).filter(User.id == uid).first()
                
                if not user:
                    continue
                
                xp = LeaderboardManager._calculate_user_xp(uid)
                xp_per_level = 100
                level = (xp // xp_per_level) + 1
                level_name = LEVELS[min(level - 1, len(LEVELS) - 1)]
                
                rankings.append({
                    'user_id': uid,
                    'username': user.username,
                    'level': level,
                    'level_name': level_name,
                    'xp': xp,
                    'is_self': uid == user_id
                })
            
            # Sort by level (desc) then XP (desc)
            rankings.sort(key=lambda x: (-x['level'], -x['xp']))
            
            # Add ranks
            for idx, entry in enumerate(rankings[:limit], 1):
                entry['rank'] = idx
            
            return {
                'success': True,
                'leaderboard_type': 'friends',
                'total_friends': len(rankings),
                'leaderboard': rankings[:limit]
            }
        
        finally:
            session.close()
    
    @staticmethod
    def get_monthly_leaderboard(limit: int = 50) -> dict:
        """Get leaderboard filtered to current month performance."""
        from datetime import datetime, timedelta
        
        session = Session()
        try:
            # Get all users active this month
            month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            users = session.query(User).filter(User.is_active == True).all()
            
            rankings = []
            
            for user in users:
                # Get attempts this month
                attempts = session.query(QuizAttempt).filter(
                    QuizAttempt.user_id == user.id,
                    QuizAttempt.completed_at >= month_start,
                    QuizAttempt.score.isnot(None)
                ).all()
                
                if not attempts:
                    continue
                
                total_xp = sum(int(a.score) for a in attempts)
                
                rankings.append({
                    'user_id': user.id,
                    'username': user.username,
                    'monthly_xp': total_xp,
                    'quizzes': len([a for a in attempts if a.completed_at])
                })
            
            # Sort by monthly XP
            rankings.sort(key=lambda x: -x['monthly_xp'])
            
            # Add ranks
            for idx, entry in enumerate(rankings[:limit], 1):
                entry['rank'] = idx
            
            return {
                'success': True,
                'leaderboard_type': 'monthly',
                'month': month_start.strftime('%Y-%m'),
                'total_active_users': len(rankings),
                'leaderboard': rankings[:limit]
            }
        
        finally:
            session.close()
    
    @staticmethod
    def get_streak_leaderboard(limit: int = 50) -> dict:
        """Get leaderboard based on login streaks (placeholder)."""
        # This would require a UserLoginLog table to track daily logins
        return {
            'success': False,
            'message': 'Streak tracking requires additional database table (UserLoginLog)'
        }
