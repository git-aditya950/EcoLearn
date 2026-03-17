"""
Gamification Engine for EcoLearn.
Handles XP, leveling, badges, daily rewards, and streaks.
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.db_setup import User, QuizAttempt, Session
from config import (
    XP_PER_CORRECT_ANSWER, STREAK_BONUS_MULTIPLIER, LEVELS, BADGES, INITIAL_XP
)


class GamificationEngine:
    """Manages gamification features."""
    
    @staticmethod
    def calculate_xp_earned(quiz_score: float, is_streak: bool = False, streak_count: int = 1) -> int:
        """
        Calculate XP earned from a quiz.
        
        Args:
            quiz_score: Score percentage (0-100)
            is_streak: Whether user has an active streak
            streak_count: Current streak count
            
        Returns:
            Total XP earned
        """
        # Base XP: 10 points per correct answer (assuming 10 questions)
        base_xp = int((quiz_score / 100) * 100)  # Max 100 XP per quiz
        
        # Streak bonus multiplier
        if is_streak and streak_count > 1:
            streak_multiplier = 1 + ((streak_count - 1) * 0.1)  # 10% per streak level
            base_xp = int(base_xp * min(streak_multiplier, 2.0))  # Cap at 2x multiplier
        
        return max(base_xp, 0)
    
    @staticmethod
    def add_xp_to_user(user_id: int, xp_amount: int) -> dict:
        """Add XP to a user."""
        session = Session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # Get current level and XP (using bio field as storage for now)
            # In production, would create separate UserProfile table
            current_level = 1
            current_xp = 0
            
            new_xp = current_xp + xp_amount
            
            # Check for level up (simplified: 100 XP per level)
            xp_per_level = 100
            new_level = (new_xp // xp_per_level) + 1
            
            level_up = new_level > current_level
            
            return {
                'success': True,
                'xp_gained': xp_amount,
                'total_xp': new_xp,
                'current_level': new_level,
                'level_up': level_up,
                'level_name': LEVELS[min(new_level - 1, len(LEVELS) - 1)]
            }
        
        finally:
            session.close()
    
    @staticmethod
    def get_user_level(user_id: int) -> dict:
        """Get user's current level and XP info."""
        session = Session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # Get all quiz attempts to calculate total XP
            attempts = session.query(QuizAttempt).filter(
                QuizAttempt.user_id == user_id,
                QuizAttempt.score.isnot(None)
            ).all()
            
            total_xp = 0
            for attempt in attempts:
                # Award XP based on score
                total_xp += GamificationEngine.calculate_xp_earned(attempt.score)
            
            xp_per_level = 100
            current_level = (total_xp // xp_per_level) + 1
            xp_in_current_level = total_xp % xp_per_level
            xp_needed_for_next = xp_per_level - xp_in_current_level
            
            level_name = LEVELS[min(current_level - 1, len(LEVELS) - 1)]
            
            return {
                'success': True,
                'level': current_level,
                'level_name': level_name,
                'total_xp': total_xp,
                'xp_in_current_level': xp_in_current_level,
                'xp_needed_for_next': xp_needed_for_next,
                'progress_percentage': (xp_in_current_level / xp_per_level) * 100
            }
        
        finally:
            session.close()
    
    @staticmethod
    def award_badge(user_id: int, badge_key: str) -> dict:
        """Award a badge to a user (placeholder for badge tracking)."""
        if badge_key not in BADGES:
            return {'success': False, 'message': 'Invalid badge'}
        
        badge = BADGES[badge_key]
        
        # In production, would create UserBadge table to track awarded badges
        return {
            'success': True,
            'badge_name': badge['name'],
            'badge_description': badge['description'],
            'badge_icon': badge['icon']
        }
    
    @staticmethod
    def check_badge_criteria(user_id: int) -> list:
        """Check which badges the user has earned."""
        session = Session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return []
            
            earned_badges = []
            
            # Get quiz attempts
            attempts = session.query(QuizAttempt).filter(
                QuizAttempt.user_id == user_id
            ).all()
            
            # Check badges criteria
            total_completed = len([a for a in attempts if a.completed_at])
            
            # Quiz Master: 50 quizzes
            if total_completed >= 50:
                earned_badges.append('QUIZ_MASTER')
            
            # First Blood: 1 quiz
            if total_completed >= 1:
                earned_badges.append('FIRST_BLOOD')
            
            # Perfect Score: 100% on any quiz
            if any(a.score == 100 for a in attempts if a.score):
                earned_badges.append('PERFECT_SCORE')
            
            return earned_badges
        
        finally:
            session.close()
    
    @staticmethod
    def track_login_streak(user_id: int) -> dict:
        """
        Track daily login streak.
        Note: This requires tracking login dates, which would need UserLoginLog table
        """
        # Placeholder implementation
        return {
            'success': True,
            'current_streak': 1,
            'max_streak': 1,
            'streak_reward_xp': 10
        }
    
    @staticmethod
    def get_daily_reward(user_id: int) -> dict:
        """Get daily login reward."""
        session = Session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # Check if user has claimed reward today
            # Would need to check UserLoginLog table
            
            daily_xp_reward = 5
            bonus_multiplier = 1  # Would be based on streak
            total_reward = int(daily_xp_reward * bonus_multiplier)
            
            return {
                'success': True,
                'xp_reward': total_reward,
                'message': f'Daily login reward: {total_reward} XP'
            }
        
        finally:
            session.close()


class Leaderboard:
    """Leaderboard functionality (level-based ranking)."""
    
    @staticmethod
    def get_global_leaderboard(limit: int = 100) -> dict:
        """Get global leaderboard based on level and XP."""
        session = Session()
        try:
            users = session.query(User).filter(User.is_active == True).all()
            
            user_rankings = []
            
            for user in users:
                attempts = session.query(QuizAttempt).filter(
                    QuizAttempt.user_id == user.id,
                    QuizAttempt.score.isnot(None)
                ).all()
                
                total_xp = 0
                for attempt in attempts:
                    total_xp += GamificationEngine.calculate_xp_earned(attempt.score)
                
                xp_per_level = 100
                current_level = (total_xp // xp_per_level) + 1
                level_name = LEVELS[min(current_level - 1, len(LEVELS) - 1)]
                
                user_rankings.append({
                    'user_id': user.id,
                    'username': user.username,
                    'level': current_level,
                    'level_name': level_name,
                    'total_xp': total_xp,
                    'quizzes_completed': len([a for a in attempts if a.completed_at])
                })
            
            # Sort by level (desc) then XP (desc)
            user_rankings.sort(key=lambda x: (-x['level'], -x['total_xp']))
            
            # Add rank
            for idx, user_data in enumerate(user_rankings[:limit], 1):
                user_data['rank'] = idx
            
            return {
                'success': True,
                'leaderboard': user_rankings[:limit]
            }
        
        finally:
            session.close()
    
    @staticmethod
    def get_user_rank(user_id: int) -> dict:
        """Get a user's rank on the global leaderboard."""
        leaderboard_result = Leaderboard.get_global_leaderboard(limit=10000)
        
        if not leaderboard_result['success']:
            return {'success': False, 'message': 'Failed to fetch leaderboard'}
        
        for user in leaderboard_result['leaderboard']:
            if user['user_id'] == user_id:
                return {
                    'success': True,
                    'rank': user['rank'],
                    'level': user['level'],
                    'level_name': user['level_name'],
                    'total_xp': user['total_xp']
                }
        
        return {'success': False, 'message': 'User not ranked yet'}
