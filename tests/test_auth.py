"""
Unit tests for authentication and user management.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.auth import AuthManager


class TestUserRegistration(unittest.TestCase):
    """Test user registration functionality."""
    
    def test_register_user_success(self):
        """Test successful user registration."""
        result = AuthManager.register_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User"
        )
        
        self.assertIn('success', result)
        if result['success']:
            self.assertIn('user_id', result)
    
    def test_register_user_weak_password(self):
        """Test registration with weak password."""
        result = AuthManager.register_user(
            username="testuser2",
            email="test2@example.com",
            password="123",  # Too short
            first_name="Test"
        )
        
        self.assertFalse(result['success'])
        self.assertIn('password', result['message'].lower())
    
    def test_register_user_short_username(self):
        """Test registration with short username."""
        result = AuthManager.register_user(
            username="ab",  # Too short
            email="test3@example.com",
            password="password123"
        )
        
        self.assertFalse(result['success'])


class TestUserLogin(unittest.TestCase):
    """Test user login functionality."""
    
    def setUp(self):
        """Set up test user before each test."""
        AuthManager.register_user(
            username="logintest",
            email="logintest@example.com",
            password="testpass123"
        )
    
    def test_login_success(self):
        """Test successful login."""
        result = AuthManager.login_user("logintest", "testpass123")
        
        self.assertTrue(result.get('success', False))
        if result['success']:
            self.assertIn('user', result)
            self.assertEqual(result['user']['username'], 'logintest')
    
    def test_login_wrong_password(self):
        """Test login with wrong password."""
        result = AuthManager.login_user("logintest", "wrongpassword")
        
        self.assertFalse(result['success'])
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent user."""
        result = AuthManager.login_user("nonexistent", "password")
        
        self.assertFalse(result['success'])


if __name__ == '__main__':
    unittest.main()
