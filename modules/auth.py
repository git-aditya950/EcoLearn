"""
Authentication module for EcoLearn.
Handles user registration, login, and password management.
"""

import bcrypt
from sqlalchemy.orm import Session
from database.db_setup import User, engine, Session
from config import BCRYPT_LOG_ROUNDS
import streamlit as st


class AuthManager:
    """Manages user authentication and registration."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt(rounds=BCRYPT_LOG_ROUNDS)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify a password against a hash.
        
        Args:
            password: Plain text password
            hashed_password: Hashed password from database
            
        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def register_user(username: str, email: str, password: str, first_name: str = '', 
                     last_name: str = '', role: str = 'student') -> dict:
        """
        Register a new user.
        
        Args:
            username: Username
            email: Email address
            password: Plain text password
            first_name: User's first name
            last_name: User's last name
            role: User role (student, teacher, admin)
            
        Returns:
            Dictionary with success status and message
        """
        session = Session()
        try:
            # Check if user already exists
            existing_user = session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                return {'success': False, 'message': 'Username or email already exists'}
            
            # Validate inputs
            if len(password) < 6:
                return {'success': False, 'message': 'Password must be at least 6 characters'}
            
            if not username or len(username) < 3:
                return {'success': False, 'message': 'Username must be at least 3 characters'}
            
            # Create new user
            hashed_password = AuthManager.hash_password(password)
            new_user = User(
                username=username,
                email=email,
                password_hash=hashed_password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                is_active=True
            )
            
            session.add(new_user)
            session.commit()
            
            return {'success': True, 'message': 'Registration successful!', 'user_id': new_user.id}
        
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f'Registration failed: {str(e)}'}
        
        finally:
            session.close()
    
    @staticmethod
    def login_user(username: str, password: str) -> dict:
        """
        Authenticate a user.
        
        Args:
            username: Username or email
            password: Plain text password
            
        Returns:
            Dictionary with success status and user data
        """
        session = Session()
        try:
            # Find user by username or email
            user = session.query(User).filter(
                (User.username == username) | (User.email == username)
            ).first()
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            if not user.is_active:
                return {'success': False, 'message': 'User account is inactive'}
            
            # Verify password
            if not AuthManager.verify_password(password, user.password_hash):
                return {'success': False, 'message': 'Invalid password'}
            
            return {
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'avatar_url': user.avatar_url
                }
            }
        
        except Exception as e:
            return {'success': False, 'message': f'Login failed: {str(e)}'}
        
        finally:
            session.close()
    
    @staticmethod
    def get_user_by_id(user_id: int) -> dict:
        """Get user data by ID."""
        session = Session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            return {
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'avatar_url': user.avatar_url,
                    'created_at': user.created_at.isoformat() if user.created_at else None
                }
            }
        
        finally:
            session.close()
    
    @staticmethod
    def update_user_profile(user_id: int, **kwargs) -> dict:
        """Update user profile information."""
        session = Session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # Update allowed fields
            allowed_fields = ['first_name', 'last_name', 'bio', 'avatar_url']
            for field in allowed_fields:
                if field in kwargs:
                    setattr(user, field, kwargs[field])
            
            session.commit()
            return {'success': True, 'message': 'Profile updated successfully'}
        
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f'Update failed: {str(e)}'}
        
        finally:
            session.close()


def init_auth_session():
    """Initialize session state for authentication."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user = None
    
    return st.session_state
