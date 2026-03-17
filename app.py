"""
EcoLearn Dashboard - Main Streamlit Application
A comprehensive educational platform for learning about environmental science and sustainability.
"""

import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import STREAMLIT_PAGE_CONFIG
from modules.auth import AuthManager, init_auth_session
from modules.gamification import GamificationEngine, Leaderboard
from modules.quiz_engine import QuizEngine
from modules.analytics import AnalyticsEngine
from api.climate_data import ClimateDataFetcher
from database.db_setup import init_db


def configure_page():
    """Configure Streamlit page settings."""
    st.set_page_config(**STREAMLIT_PAGE_CONFIG)
    
    # Custom CSS
    st.markdown("""
    <style>
    .main {
        padding: 20px;
    }
    .stButton>button {
        width: 100%;
        background-color: #27AE60;
        color: white;
    }
    .stButton>button:hover {
        background-color: #229954;
    }
    .metric-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #ecf0f1;
    }
    </style>
    """, unsafe_allow_html=True)


def render_login_page():
    """Render the login/registration page."""
    st.title("🌍 Welcome to EcoLearn")
    st.markdown("### Learn about Environment. Save the Planet!")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        
        username = st.text_input("Username or Email", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", key="login_button"):
            if username and password:
                result = AuthManager.login_user(username, password)
                
                if result['success']:
                    st.session_state.authenticated = True
                    st.session_state.user = result['user']
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error(result['message'])
            else:
                st.warning("Please enter username and password")
    
    with tab2:
        st.subheader("Create New Account")
        
        username = st.text_input("Username", key="reg_username")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
        first_name = st.text_input("First Name (optional)", key="reg_first")
        last_name = st.text_input("Last Name (optional)", key="reg_last")
        
        role = st.selectbox("I am a...", ["Student", "Teacher"], key="reg_role")
        
        if st.button("Register", key="register_button"):
            if not username or not email or not password:
                st.error("Username, email, and password are required")
            elif password != confirm_password:
                st.error("Passwords do not match")
            else:
                result = AuthManager.register_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    role=role.lower()
                )
                
                if result['success']:
                    st.success("Registration successful! Please login.")
                else:
                    st.error(result['message'])


def render_student_dashboard():
    """Render student dashboard."""
    st.title(f"👋 Welcome, {st.session_state.user['username']}!")
    
    col1, col2, col3 = st.columns(3)
    
    # Get user level
    level_info = GamificationEngine.get_user_level(st.session_state.user['id'])
    
    with col1:
        st.metric(
            "Level",
            level_info['level_name'],
            f"Lvl {level_info['level']}"
        )
    
    with col2:
        st.metric(
            "Total XP",
            level_info['total_xp'],
            f"{level_info['progress_percentage']}% to next"
        )
    
    with col3:
        rank_info = Leaderboard.get_user_rank(st.session_state.user['id'])
        if rank_info['success']:
            st.metric(
                "Global Rank",
                f"#{rank_info['rank']}",
                "Leaderboard"
            )
    
    st.divider()
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Take Quiz", "My Progress", "Leaderboard", "Climate Data"])
    
    with tab1:
        st.subheader("📝 Take a Quiz")
        st.write("Quiz feature coming soon! Select a quiz to get started.")
    
    with tab2:
        st.subheader("📊 My Progress")
        progress_report = AnalyticsEngine.get_student_progress_report(st.session_state.user['id'])
        
        if progress_report['success']:
            quiz_stats = progress_report['quiz_stats']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Quizzes Completed", quiz_stats['completed'])
            
            with col2:
                st.metric("Average Score", f"{quiz_stats['average_score']}%")
            
            with col3:
                st.metric("Pass Rate", f"{quiz_stats['pass_rate']}%")
            
            with col4:
                st.metric("Time Spent", f"{progress_report['time_stats']['total_time_minutes']} min")
        else:
            st.info("No quiz data yet. Start by taking a quiz!")
    
    with tab3:
        st.subheader("🏆 Global Leaderboard")
        lb_result = Leaderboard.get_global_leaderboard(limit=10)
        
        if lb_result['success']:
            st.dataframe(
                lb_result['leaderboard'],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("Could not load leaderboard")
    
    with tab4:
        st.subheader("🌍 Climate Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            city = st.text_input("Enter your city")
        
        with col2:
            if st.button("Get Air Quality Data"):
                if city:
                    # Search for city coordinates
                    coords = ClimateDataFetcher.search_city_coordinates(city)
                    
                    if coords['success']:
                        st.success(f"Found: {coords['city']}, {coords['country']}")
                        
                        # Fetch air quality
                        air_quality = ClimateDataFetcher.get_air_quality_data(
                            coords['latitude'],
                            coords['longitude']
                        )
                        
                        if air_quality['success']:
                            aq = air_quality['air_quality']
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("AQI", int(aq['us_aqi']), aq['pm2_5'])
                            
                            with col2:
                                st.metric("Category", air_quality['air_quality']['category'])
                            
                            with col3:
                                st.info(air_quality['health_recommendation'])
                        else:
                            st.error(air_quality['message'])
                    else:
                        st.error(coords['message'])
                else:
                    st.warning("Please enter a city name")


def render_teacher_dashboard():
    """Render teacher dashboard."""
    st.title(f"👨‍🏫 Teacher Dashboard - {st.session_state.user['username']}")
    
    tab1, tab2, tab3 = st.tabs(["My Courses", "Class Performance", "Analytics"])
    
    with tab1:
        st.subheader("My Courses")
        st.write("Course management coming soon!")
    
    with tab2:
        st.subheader("Class Performance")
        st.write("Class analytics coming soon!")
    
    with tab3:
        st.subheader("Analytics")
        st.write("Detailed analytics coming soon!")


def render_admin_dashboard():
    """Render admin dashboard."""
    st.title("⚙️ Admin Dashboard")
    
    st.write("Admin panel coming soon!")


def main():
    """Main application entry point."""
    configure_page()
    
    # Initialize database on first run
    if not os.path.exists('ecolearn.db'):
        init_db()
    
    # Initialize session state
    init_auth_session()
    
    # Sidebar
    if st.session_state.authenticated:
        with st.sidebar:
            st.title("🌍 EcoLearn")
            st.write(f"User: **{st.session_state.user['username']}**")
            st.write(f"Role: **{st.session_state.user['role'].title()}**")
            
            if st.button("Logout", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.rerun()
        
        # Render dashboard based on role
        if st.session_state.user['role'] == 'student':
            render_student_dashboard()
        elif st.session_state.user['role'] == 'teacher':
            render_teacher_dashboard()
        elif st.session_state.user['role'] == 'admin':
            render_admin_dashboard()
    else:
        render_login_page()


if __name__ == '__main__':
    main()
