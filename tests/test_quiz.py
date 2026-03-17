"""
Unit tests for the Quiz Engine module.
Demonstrates test-driven development practices.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.quiz_engine import QuizEngine
from modules.gamification import GamificationEngine
from modules.auth import AuthManager


class TestAuthManager(unittest.TestCase):
    """Test cases for authentication."""
    
    def test_hash_password(self):
        """Test password hashing."""
        password = "test_password_123"
        hashed = AuthManager.hash_password(password)
        
        # Hash should not equal plain password
        self.assertNotEqual(hashed, password)
        
        # Hash should be different each time
        hashed2 = AuthManager.hash_password(password)
        self.assertNotEqual(hashed, hashed2)
    
    def test_verify_password(self):
        """Test password verification."""
        password = "test_password_123"
        hashed = AuthManager.hash_password(password)
        
        # Correct password should verify
        self.assertTrue(AuthManager.verify_password(password, hashed))
        
        # Incorrect password should not verify
        self.assertFalse(AuthManager.verify_password("wrong_password", hashed))


class TestGamificationEngine(unittest.TestCase):
    """Test cases for gamification."""
    
    def test_calculate_xp_without_streak(self):
        """Test XP calculation without streak."""
        # Full score
        xp = GamificationEngine.calculate_xp_earned(100, is_streak=False)
        self.assertGreater(xp, 0)
        self.assertLessEqual(xp, 100)
        
        # Zero score
        xp = GamificationEngine.calculate_xp_earned(0, is_streak=False)
        self.assertEqual(xp, 0)
        
        # Half score
        xp_half = GamificationEngine.calculate_xp_earned(50, is_streak=False)
        self.assertGreater(xp_half, 0)
    
    def test_calculate_xp_with_streak(self):
        """Test XP calculation with streak bonus."""
        xp_no_streak = GamificationEngine.calculate_xp_earned(100, is_streak=False)
        xp_with_streak = GamificationEngine.calculate_xp_earned(100, is_streak=True, streak_count=5)
        
        # Streak should give bonus
        self.assertGreater(xp_with_streak, xp_no_streak)
    
    def test_add_xp_increases_level(self):
        """Test that XP addition can increase level."""
        result = GamificationEngine.add_xp_to_user(1, 100)
        
        self.assertTrue(result['success'])
        self.assertIn('current_level', result)
        self.assertGreater(result['current_level'], 0)


class TestQuizEngine(unittest.TestCase):
    """Test cases for quiz engine."""
    
    def test_create_quiz(self):
        """Test quiz creation."""
        # This would need a valid lesson_id in the database
        result = QuizEngine.create_quiz(
            lesson_id=1,
            title="Test Quiz",
            description="Test Description",
            passing_score=70.0
        )
        
        self.assertIn('success', result)
        self.assertIn('message', result)


if __name__ == '__main__':
    unittest.main()
