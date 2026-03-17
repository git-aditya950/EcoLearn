"""
Configuration settings for EcoLearn application.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///ecolearn.db')

# API Keys
OPEN_METEO_API_URL = 'https://api.open-meteo.com/v1/forecast'
NASA_CLIMATE_API_URL = 'https://api.nasa.gov/api/v3/climate_anomalies'

# Gamification Settings
INITIAL_XP = 0
XP_PER_CORRECT_ANSWER = 10
STREAK_BONUS_MULTIPLIER = 1.5
LEVELS = [
    "Seedling", "Sprout", "Sapling", "Young Tree", "Tree",
    "Strong Oak", "Forest Friend", "Nature Advocate", "Eco Warrior", "Green Champion",
    "Climate Scholar", "Sustainability Expert", "Carbon Conscious", "Green Guardian", "Eco Hero",
    "Forest Protector", "Planet Defender", "Climate Leader", "Sustainability Master", "Eco Legend",
    "Environmental Visionary", "Green Pioneer", "Nature's Champion", "Climate Guardian", "Earth Protector",
    "Biosphere Defender", "Conservation Hero", "Planetary Guardian", "Eco Innovator", "Green Revolutionist",
    "Sustainability Champion", "Climate Advocate", "Nature's Voice", "Green Ambassador", "Ecosystem Expert",
    "Planetary Healer", "Environmental Leader", "Climate Scientists", "Green Philosopher", "Eco Enlightened",
    "Nature's Guardian", "Forest King", "Climate Master", "Green Legend", "Planetary Sage",
    "Earth's Champion", "Divine Guardian", "Cosmos Protector", "Living Legend", "Forest Guardian"
]

# Badges
BADGES = {
    'QUIZ_MASTER': {'name': 'Quiz Master', 'description': 'Complete 50 quizzes', 'icon': '🏆'},
    'STREAK_7': {'name': '7-Day Streak', 'description': 'Login 7 consecutive days', 'icon': '🔥'},
    'CARBON_EXPERT': {'name': 'Carbon Expert', 'description': 'Complete all Climate Change quizzes', 'icon': '💨'},
    'BIODIVERSITY_PRO': {'name': 'Biodiversity Pro', 'description': 'Complete all Biodiversity quizzes', 'icon': '🌿'},
    'RECYCLING_EXPERT': {'name': 'Recycling Expert', 'description': 'Complete all Recycling quizzes', 'icon': '♻️'},
    'RENEWABLE_GURU': {'name': 'Renewable Guru', 'description': 'Complete all Renewable Energy quizzes', 'icon': '⚡'},
    'PERFECT_SCORE': {'name': 'Perfect Score', 'description': 'Score 100% on a quiz', 'icon': '💯'},
    'SPEED_DEMON': {'name': 'Speed Demon', 'description': 'Complete a quiz in half the time', 'icon': '⚡'},
    'FIRST_BLOOD': {'name': 'First Blood', 'description': 'Complete your first quiz', 'icon': '🌱'},
    'LEVEL_10': {'name': 'Level 10', 'description': 'Reach level 10', 'icon': '📈'},
}

# Quiz Settings
QUIZ_CATEGORIES = ['Climate Change', 'Biodiversity', 'Recycling', 'Renewable Energy']
DIFFICULTY_LEVELS = ['Easy', 'Medium', 'Hard']

# Streamlit Configuration
STREAMLIT_PAGE_CONFIG = {
    'page_title': 'EcoLearn - Learn About Environment',
    'page_icon': '🌍',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded',
}

# Password hashing
BCRYPT_LOG_ROUNDS = 12
