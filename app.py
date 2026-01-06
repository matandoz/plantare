# -*- coding: utf-8 -*-

import streamlit as st
from google import genai
import os
from google.genai import types
import json
from dotenv import load_dotenv
import random
from datetime import datetime, timedelta
import re
import pytz

# -------------------------------------
# Load Gemini API Key
# -------------------------------------
# For local development: uses .env file
# For Streamlit Cloud: uses st.secrets
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

# -------------------------------------
# THEME CONFIGURATION
# -------------------------------------
THEME = {
    "primary": "#4A7C59",       # Sage Green
    "primary_hover": "#3a6346",
    "secondary": "#E07A5F",     # Terra Cotta
    "earth": "#D4A373",         # Sand/Earth
    "forest": "#2D4A36",        # Deep Forest Green
    "bg": "#F9F8F6",            # Off-White
    "card_bg": "#FFFFFF",
    "text": "#2C3E50",          # Dark Slate
    "subtext": "#607D8B",
    "success": "#81B29A",
    "warning": "#F2CC8F",
    "locked": "#CFD8DC",        # Grey for locked items
    "gold": "#FFD700",          # Gold for locks/trophies
    "error": "#E57373",         # Error Red
    "info": "#64B5F6",          # Info Blue
    "focus": "#2196F3",         # Focus Blue
    "border": "#E0E0E0"         # Border Gray
}

# Dark mode theme
DARK_THEME = {
    "primary": "#66BB6A",
    "primary_hover": "#4CAF50",
    "secondary": "#FF8A65",
    "earth": "#BCAAA4",
    "forest": "#388E3C",
    "bg": "#121212",
    "card_bg": "#1E1E1E",
    "text": "#E0E0E0",
    "subtext": "#B0BEC5",
    "success": "#66BB6A",
    "warning": "#FFB74D",
    "locked": "#424242",
    "gold": "#FFD54F",
    "error": "#EF5350",
    "info": "#42A5F5",
    "focus": "#64B5F6",
    "border": "#424242"
}

# Typography scale
TYPOGRAPHY = {
    "h1": "32px",
    "h2": "28px",
    "h3": "24px",
    "h4": "20px",
    "h5": "18px",
    "h6": "16px",
    "body": "14px",
    "small": "12px",
    "font_family": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif"
}

# Spacing system (8px grid)
SPACING = {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px",
    "xxl": "48px"
}

# -------------------------------------
# XP Thresholds
# -------------------------------------
LEVEL_THRESHOLDS = [0, 20, 50, 100, 150, 250, 500, 800, 1200, 1700, 2500]

def get_next_level_threshold(level):
    idx = level
    if idx >= len(LEVEL_THRESHOLDS):
        return LEVEL_THRESHOLDS[-1] + (level * 500)
    return LEVEL_THRESHOLDS[idx]

def generate(prompt):
    try:
        client = genai.Client(api_key=api_key)
        model = "gemini-2.5-flash"

        contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]

        full_response = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        ):
            full_response += chunk.text
        return full_response
    except Exception as e:
        return f"Error: {str(e)}"

# -------------------------------------
# Helpers: Detailed AI Insights Logic
# -------------------------------------
def get_plant_insight(plant_name, plant_type):
    name_lower = plant_name.lower()
    insights = {
        "clean": "Dust leaves gently with a soft cloth.",
        "repot": "Check roots every 12 months.",
        "prune": "Remove yellow leaves.",
        "harvest": "N/A",
        "fertilize": "Standard balanced fertilizer monthly."
    }

    if "Herbs" in plant_type or any(x in name_lower for x in ['basil', 'mint', 'tomato', 'pepper', 'lettuce']):
        insights["clean"] = "Check under leaves for pests."
        insights["repot"] = "Repot if roots circle the bottom (approx 4-6 months)."
        insights["prune"] = "Pinch top leaves to encourage bushing."
        insights["fertilize"] = "High-nitrogen feed every 2 weeks."
        if any(x in name_lower for x in ['tomato', 'pepper']):
             insights["harvest"] = "Harvest when color changes fully."
        else:
             insights["harvest"] = "Harvest outer leaves, leave center growing."
    elif "Ornamental" in plant_type or any(x in name_lower for x in ['monstera', 'pothos', 'fern', 'snake']):
        if "monstera" in name_lower:
             insights["clean"] = "Wipe large leaves with damp cloth weekly."
             insights["repot"] = "Move to larger pot every 18-24 months."
             insights["prune"] = "Cut aerial roots if unruly."
        elif "snake" in name_lower:
             insights["clean"] = "Light dusting only."
             insights["repot"] = "Likes being root-bound; repot every 3 years."
             insights["fertilize"] = "Light feed only in spring/summer."
    elif "Germination" in plant_type:
         insights["clean"] = "Ensure soil surface is free of mold."
         insights["repot"] = "Transplant when second set of true leaves appear."
         insights["prune"] = "Thin out weaker seedlings."
         insights["fertilize"] = "Diluted fertilizer after 4 weeks."

    return insights

# -------------------------------------
# Configuration & Icons
# -------------------------------------
PLANT_EXAMPLES = {
    "🥬 Herbs, vegetables, and fruits": "e.g., Basil, Tomatoes, Mint, Rosemary...",
    "🌺 Ornamental plants and home decor": "e.g., Monstera, Pothos, Snake Plant...",
    "🌱 Germination, cuttings, growing from scratch": "e.g., Avocado seed, Tomato seedlings..."
}

CATEGORY_ICONS = {
    "🥬 Herbs, vegetables, and fruits": "🥬",
    "🌺 Ornamental plants and home decor": "🌺",
    "🌱 Germination, cuttings, growing from scratch": "🌱"
}

BASE_OPTIONS = list(PLANT_EXAMPLES.keys())
MIXED_OPTION = "🥗 Mixed Garden (Various Types)"
USAGE_OPTIONS = BASE_OPTIONS + [MIXED_OPTION]

PLANT_PET_NAMES = [
    "Sprout", "Leafy", "Bloom", "Petal", "Fern", "Ivy", "Clover", "Sage",
    "Willow", "Flora", "Bud", "Moss", "Reed", "Basil", "Rosie", "Sunny",
    "Dewdrop", "Thistle", "Cedar", "Maple", "Daisy", "Oliver", "Luna", "Charlie"
]

# -------------------------------------
# Leaderboard Mock Data
# -------------------------------------
def get_mock_leaderboard():
    friends = [
        {"name": "👩 Sarah G.", "points": 2450, "streak": 14, "level": 8, "pet_name": "Rose"},
        {"name": "🌿 Mike R.", "points": 1890, "streak": 7, "level": 6, "pet_name": "Thor"},
        {"name": "🌸 Emma L.", "points": 1650, "streak": 21, "level": 5, "pet_name": "Lily"},
        {"name": "🍀 David K.", "points": 1200, "streak": 5, "level": 4, "pet_name": "Lucky"},
        {"name": "🎋 Anna P.", "points": 500, "streak": 1, "level": 2, "pet_name": "Bamboo"},
        {"name": "👨 Tom H.", "points": 40, "streak": 2, "level": 1, "pet_name": "Coco"},
    ]
    return friends

# -------------------------------------
# Visual Components (Styled)
# -------------------------------------
def inject_custom_css():
    # Get current theme based on dark mode setting
    theme = DARK_THEME if st.session_state.get("dark_mode", False) else THEME

    st.markdown(f"""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* Typography System */
        * {{
            font-family: {TYPOGRAPHY['font_family']};
        }}

        h1 {{
            font-size: {TYPOGRAPHY['h1']};
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: {SPACING['md']};
            color: {theme['text']};
        }}

        h2 {{
            font-size: {TYPOGRAPHY['h2']};
            font-weight: 600;
            line-height: 1.3;
            margin-bottom: {SPACING['sm']};
            color: {theme['text']};
        }}

        h3 {{
            font-size: {TYPOGRAPHY['h3']};
            font-weight: 600;
            line-height: 1.4;
            margin-bottom: {SPACING['sm']};
            color: {theme['text']};
        }}

        h4 {{
            font-size: {TYPOGRAPHY['h4']};
            font-weight: 500;
            line-height: 1.5;
            margin-bottom: {SPACING['xs']};
            color: {theme['text']};
        }}

        body, p, div {{
            font-size: {TYPOGRAPHY['body']};
            line-height: 1.6;
            color: {theme['text']};
        }}

        .stApp {{
            background-color: {theme['bg']};
            transition: background-color 0.3s ease;
        }}

        /* Card System with 8px Grid */
        .nature-card {{
            background-color: {theme['card_bg']};
            padding: {SPACING['lg']};
            border-radius: {SPACING['md']};
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
            margin-bottom: {SPACING['md']};
            border: 1px solid {theme['border']};
            transition: all 0.3s ease;
        }}

        .nature-card:hover {{
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
            transform: translateY(-2px);
        }}

        /* Button Animations & States */
        div.stButton > button {{
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            font-weight: 500;
            border-radius: {SPACING['sm']};
            padding: {SPACING['sm']} {SPACING['md']};
            position: relative;
            overflow: hidden;
        }}

        div.stButton > button::before {{
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }}

        div.stButton > button:active::before {{
            width: 300px;
            height: 300px;
        }}

        div.stButton > button[kind="primary"] {{
            background-color: {theme['primary']};
            color: white;
            border: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        div.stButton > button[kind="primary"]:hover {{
            background-color: {theme['primary_hover']};
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}

        div.stButton > button[kind="primary"]:active {{
            transform: translateY(0);
        }}

        div.stButton > button[kind="secondary"] {{
            background-color: {theme['card_bg']};
            color: {theme['text']};
            border: 2px solid {theme['border']};
        }}

        div.stButton > button[kind="secondary"]:hover {{
            border-color: {theme['primary']};
            background-color: {theme['bg']};
        }}

        /* Ensure consistent button heights */
        div.stButton > button {{
            height: 40px;
            min-height: 40px;
            padding: 0 {SPACING['md']};
            display: flex;
            align-items: center;
            justify-content: center;
            line-height: 1;
        }}

        /* Text input consistent height */
        .stTextInput input {{
            height: 40px;
            min-height: 40px;
            padding: 8px 12px;
        }}

        .stTextInput label {{
            margin-bottom: 4px;
        }}

        /* Focus States for Accessibility */
        div.stButton > button:focus,
        input:focus,
        textarea:focus,
        select:focus {{
            outline: 3px solid {theme['focus']};
            outline-offset: 2px;
            box-shadow: 0 0 0 3px {theme['focus']}33;
        }}

        /* Keyboard Navigation Indicators */
        *:focus-visible {{
            outline: 3px solid {theme['focus']};
            outline-offset: 2px;
        }}

        /* Sticky Header */
        .sticky-header {{
            position: sticky;
            top: 0;
            z-index: 100;
            background: {theme['card_bg']};
            padding: {SPACING['md']};
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: {SPACING['md']};
            border-radius: 0 0 {SPACING['md']} {SPACING['md']};
        }}

        /* Bottom Navigation - Enhanced */
        .bottom-nav {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: {theme['card_bg']};
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
            padding: {SPACING['sm']};
            display: flex;
            justify-content: space-around;
            z-index: 1000;
            border-top: 2px solid {theme['border']};
        }}

        .nav-item {{
            flex: 1;
            text-align: center;
            padding: {SPACING['sm']};
            cursor: pointer;
            transition: all 0.3s ease;
            border-radius: {SPACING['sm']};
            position: relative;
        }}

        .nav-item:hover {{
            background: {theme['bg']};
            transform: scale(1.05);
        }}

        .nav-item.active {{
            color: {theme['primary']};
            font-weight: 600;
        }}

        .nav-item.active::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 40px;
            height: 3px;
            background: {theme['primary']};
            border-radius: {SPACING['xs']} {SPACING['xs']} 0 0;
        }}

        /* Breadcrumbs */
        .breadcrumb {{
            display: flex;
            align-items: center;
            gap: {SPACING['sm']};
            padding: {SPACING['sm']} 0;
            font-size: {TYPOGRAPHY['small']};
            color: {theme['subtext']};
            margin-bottom: {SPACING['md']};
        }}

        .breadcrumb-item {{
            cursor: pointer;
            transition: color 0.2s;
        }}

        .breadcrumb-item:hover {{
            color: {theme['primary']};
        }}

        .breadcrumb-separator {{
            color: {theme['subtext']};
        }}

        /* Collapsible/Accordion Sections */
        .accordion {{
            background: {theme['card_bg']};
            border: 1px solid {theme['border']};
            border-radius: {SPACING['sm']};
            margin-bottom: {SPACING['sm']};
            overflow: hidden;
            transition: all 0.3s ease;
        }}

        .accordion-header {{
            padding: {SPACING['md']};
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: {theme['card_bg']};
            transition: background 0.3s ease;
            user-select: none;
        }}

        .accordion-header:hover {{
            background: {theme['bg']};
        }}

        .accordion-icon {{
            transition: transform 0.3s ease;
        }}

        .accordion-icon.expanded {{
            transform: rotate(180deg);
        }}

        .accordion-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
            padding: 0 {SPACING['md']};
        }}

        .accordion-content.expanded {{
            max-height: 2000px;
            padding: {SPACING['md']};
        }}

        /* Empty States */
        .empty-state {{
            text-align: center;
            padding: {SPACING['xxl']} {SPACING['md']};
            background: {theme['card_bg']};
            border-radius: {SPACING['md']};
            border: 2px dashed {theme['border']};
            margin: {SPACING['lg']} 0;
        }}

        .empty-state-icon {{
            font-size: 64px;
            margin-bottom: {SPACING['md']};
            opacity: 0.5;
        }}

        .empty-state-title {{
            font-size: {TYPOGRAPHY['h3']};
            font-weight: 600;
            color: {theme['text']};
            margin-bottom: {SPACING['sm']};
        }}

        .empty-state-description {{
            font-size: {TYPOGRAPHY['body']};
            color: {theme['subtext']};
            margin-bottom: {SPACING['lg']};
            max-width: 400px;
            margin-left: auto;
            margin-right: auto;
        }}

        /* Achievement Animation */
        @keyframes achievement-pop {{
            0% {{
                transform: scale(0) rotate(-180deg);
                opacity: 0;
            }}
            50% {{
                transform: scale(1.2) rotate(10deg);
            }}
            100% {{
                transform: scale(1) rotate(0);
                opacity: 1;
            }}
        }}

        .achievement-popup {{
            animation: achievement-pop 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            background: linear-gradient(135deg, {theme['gold']} 0%, {theme['warning']} 100%);
            padding: {SPACING['lg']};
            border-radius: {SPACING['md']};
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            text-align: center;
        }}

        /* Bounce Animation for Virtual Plant */
        @keyframes bounce {{
            0%, 100% {{
                transform: translateY(0);
            }}
            50% {{
                transform: translateY(-10px);
            }}
        }}

        /* Loading Skeleton */
        @keyframes skeleton-loading {{
            0% {{
                background-position: -200px 0;
            }}
            100% {{
                background-position: calc(200px + 100%) 0;
            }}
        }}

        .skeleton {{
            background: linear-gradient(90deg, {theme['bg']} 0%, {theme['border']} 50%, {theme['bg']} 100%);
            background-size: 200px 100%;
            animation: skeleton-loading 1.5s ease-in-out infinite;
            border-radius: {SPACING['xs']};
        }}

        /* Badge Styles with Animations */
        .badge {{
            padding: {SPACING['xs']} {SPACING['sm']};
            border-radius: {SPACING['xs']};
            font-size: {TYPOGRAPHY['small']};
            font-weight: 600;
            display: inline-block;
            margin: {SPACING['xs']};
            transition: all 0.3s ease;
        }}

        .badge-success {{
            background: {theme['success']};
            color: white;
        }}

        .badge-warning {{
            background: {theme['warning']};
            color: {theme['text']};
        }}

        .badge-error {{
            background: {theme['error']};
            color: white;
        }}

        .badge-info {{
            background: {theme['info']};
            color: white;
        }}

        /* Mobile Touch Optimizations */
        @media (max-width: 768px) {{
            h1 {{ font-size: 28px; }}
            h2 {{ font-size: 24px; }}
            h3 {{ font-size: 20px; }}

            div.stButton > button {{
                min-height: 48px;
                font-size: 16px;
                padding: {SPACING['md']} {SPACING['lg']};
            }}

            .nature-card {{
                padding: {SPACING['md']};
            }}

            .swipeable-container {{
                overflow-x: auto;
                scroll-snap-type: x mandatory;
                -webkit-overflow-scrolling: touch;
                display: flex;
                scrollbar-width: none;
            }}

            .swipeable-container::-webkit-scrollbar {{
                display: none;
            }}

            .pull-refresh {{
                text-align: center;
                padding: {SPACING['sm']};
                color: {theme['subtext']};
                font-size: {TYPOGRAPHY['small']};
            }}
        }}

        /* Haptic feedback simulation */
        .haptic-button {{
            transition: transform 0.1s ease;
        }}

        .haptic-button:active {{
            transform: scale(0.95);
        }}

        /* Smooth Transitions */
        * {{
            transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
        }}

        /* Improved Input Fields */
        input, textarea, select {{
            border: 2px solid {theme['border']};
            border-radius: {SPACING['sm']};
            padding: {SPACING['sm']} {SPACING['md']};
            font-size: {TYPOGRAPHY['body']};
            transition: all 0.3s ease;
            background: {theme['card_bg']};
            color: {theme['text']};
        }}

        input:hover, textarea:hover, select:hover {{
            border-color: {theme['primary']};
        }}

        /* Streamlit Selectbox Dark Mode Fix */
        [data-baseweb="select"] {{
            background-color: {theme['card_bg']};
        }}

        [data-baseweb="select"] > div {{
            background-color: {theme['card_bg']};
            border-color: {theme['border']};
        }}

        [data-baseweb="popover"] {{
            background-color: {theme['card_bg']};
        }}

        [data-baseweb="menu"] {{
            background-color: {theme['card_bg']};
        }}

        [role="option"] {{
            background-color: {theme['card_bg']};
            color: {theme['text']};
        }}

        [role="option"]:hover {{
            background-color: {theme['bg']};
        }}

        /* Streamlit Input Dark Mode */
        .stTextInput input {{
            background-color: {theme['card_bg']};
            color: {theme['text']};
            border-color: {theme['border']};
        }}

        /* Streamlit Checkbox Dark Mode */
        .stCheckbox label {{
            color: {theme['text']};
        }}

        /* Streamlit Slider Dark Mode */
        .stSlider label {{
            color: {theme['text']};
        }}

        /* Slider value display */
        [data-baseweb="slider"] {{
            color: {theme['text']};
        }}

        /* Metric cards dark mode */
        [data-testid="stMetric"] {{
            background-color: {theme['card_bg']};
            color: {theme['text']};
        }}

        [data-testid="stMetricLabel"] {{
            color: {theme['text']};
        }}

        [data-testid="stMetricValue"] {{
            color: {theme['text']};
        }}

        /* Streamlit Expander Dark Mode */
        [data-testid="stExpander"] {{
            background-color: {theme['card_bg']};
            border: 1px solid {theme['border']};
            border-radius: {SPACING['sm']};
        }}

        [data-testid="stExpander"] details {{
            background-color: {theme['card_bg']};
        }}

        [data-testid="stExpander"] summary {{
            background-color: {theme['card_bg']};
            color: {theme['text']};
        }}

        [data-testid="stExpander"] summary:hover {{
            background-color: {theme['bg']};
        }}

        /* Task Card Enhancements */
        .task-card {{
            background: {theme['card_bg']};
            border: 2px solid {theme['border']};
            border-radius: {SPACING['md']};
            padding: {SPACING['md']};
            margin-bottom: {SPACING['sm']};
            transition: all 0.3s ease;
            cursor: pointer;
        }}

        .task-card:hover {{
            border-color: {theme['primary']};
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transform: translateX(4px);
        }}

        .task-card.completed {{
            opacity: 0.7;
            border-color: {theme['success']};
            background: linear-gradient(135deg, {theme['success']}10 0%, {theme['card_bg']} 100%);
        }}
    </style>
    """, unsafe_allow_html=True)

def get_plant_status(completion_rate):
    if completion_rate >= 80: return "🌿", "Thriving & Happy!", THEME['success']
    elif completion_rate >= 60: return "🌱", "Growing Well", "#66BB6A"
    elif completion_rate >= 40: return "🍂", "Needs Attention", THEME['warning']
    elif completion_rate >= 20: return "🥀", "Sad & Thirsty", THEME['secondary']
    else: return "💀", "Wilting...", "#EF5350"

def display_virtual_plant(completion_rate, pet_name="Sprout"):
    theme = DARK_THEME if st.session_state.get("dark_mode", False) else THEME
    emoji, status, color = get_plant_status(completion_rate)

    # More detailed growth stages based on completion rate
    if completion_rate >= 95:
        plant_display = "🌺🌸🌿🌸🌺"
        mood = "🤩"
        speech = "I'm flourishing! You're amazing! 💚✨"
        background = "linear-gradient(135deg, #C8E6C9 0%, #A5D6A7 100%)"
        border_color = "#66BB6A"
        growth_stage = "Perfect Bloom"
        particles = "✨🌟💫"
    elif completion_rate >= 80:
        plant_display = "🌸🌿🌸"
        mood = "😊"
        speech = "I'm so happy! Thank you! 💚"
        background = "linear-gradient(135deg, #F1F8E9 0%, #DCEDC8 100%)"
        border_color = "#81C784"
        growth_stage = "Thriving"
        particles = "✨💚"
    elif completion_rate >= 65:
        plant_display = "🌿🌱🌿"
        mood = "🙂"
        speech = "Feeling good! Keep it up! 🌤️"
        background = "linear-gradient(135deg, #F1F8E9 0%, #E8F5E9 100%)"
        border_color = "#AED581"
        growth_stage = "Growing Well"
        particles = "🌱"
    elif completion_rate >= 50:
        plant_display = "🌱🍃🌱"
        mood = "😌"
        speech = "I'm growing steadily! 🌿"
        background = "linear-gradient(135deg, #F9FBE7 0%, #F0F4C3 100%)"
        border_color = "#C5E1A5"
        growth_stage = "Steady Growth"
        particles = "🍃"
    elif completion_rate >= 35:
        plant_display = "🍂🌱🍂"
        mood = "😐"
        speech = "I could use some attention... 💧"
        background = "linear-gradient(135deg, #FFF9C4 0%, #FFF59D 100%)"
        border_color = "#FFE082"
        growth_stage = "Needs Care"
        particles = "💧"
    elif completion_rate >= 20:
        plant_display = "🥀🍂🥀"
        mood = "😢"
        speech = "I'm getting thirsty... 💦"
        background = "linear-gradient(135deg, #FFECB3 0%, #FFE082 100%)"
        border_color = "#FFB74D"
        growth_stage = "Wilting"
        particles = "💦"
    elif completion_rate >= 10:
        plant_display = "🥀💔🥀"
        mood = "😰"
        speech = "Help! I need water! 🆘"
        background = "linear-gradient(135deg, #FFCCBC 0%, #FFAB91 100%)"
        border_color = "#FF8A65"
        growth_stage = "Critical"
        particles = "🆘"
    else:
        plant_display = "💀🥀💀"
        mood = "😵"
        speech = "Emergency! Water me now! 🚨"
        background = "linear-gradient(135deg, #FFCDD2 0%, #EF9A9A 100%)"
        border_color = "#E57373"
        growth_stage = "Dying"
        particles = "🚨"

    # Add level-based bonuses
    level = st.session_state.get("level", 1)
    if level >= 10 and completion_rate >= 80:
        plant_display += " 👑"
    elif level >= 5 and completion_rate >= 80:
        plant_display += " ⭐"

    st.markdown(f"""<div style="text-align: center; padding: {SPACING['lg']}; background: {background}; border-radius: {SPACING['lg']}; margin: {SPACING['sm']} 0; box-shadow: 0 8px 20px rgba(0,0,0,0.1); border: 2px solid {border_color}; position: relative; overflow: hidden;">
        <div style="position: absolute; top: 10px; right: 10px; font-size: 10px; background: rgba(255,255,255,0.9); padding: 4px 8px; border-radius: 12px; font-weight: bold; color: {theme['text']};">{growth_stage}</div>
        <div style="font-size: {TYPOGRAPHY['small']}; color: {theme['primary']}; margin-bottom: {SPACING['xs']}; font-weight: 600;">Your Plant Buddy</div>
        <div style="font-size: {TYPOGRAPHY['h4']}; font-weight: bold; color: {theme['text']}; margin-bottom: {SPACING['sm']};">✨ {pet_name} ✨</div>
        <div style="font-size: 60px; margin: {SPACING['sm']} 0; animation: bounce 2s ease-in-out infinite;">{mood}</div>
        <div style="font-size: 50px; margin: {SPACING['sm']} 0; letter-spacing: 5px;">{plant_display}</div>
        <div style="font-size: 20px; margin: {SPACING['xs']} 0; opacity: 0.7;">{particles}</div>
        <h3 style="color: {color}; margin-top: {SPACING['sm']}; margin-bottom: {SPACING['xs']}; font-size: {TYPOGRAPHY['h5']};">{status}</h3>
        <div style="background: rgba(255,255,255,0.9); padding: {SPACING['sm']} {SPACING['md']}; border-radius: {SPACING['md']}; margin-top: {SPACING['sm']}; font-style: italic; color: {theme['subtext']}; display: inline-block; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">"{speech}"</div>
        <div style="margin-top: {SPACING['md']}; font-size: {TYPOGRAPHY['small']}; color: {theme['subtext']}; opacity: 0.8;">Completion: {int(completion_rate)}% • Level {level}</div>
    </div>""", unsafe_allow_html=True)

def display_daily_progress(completion_rate):
    theme = DARK_THEME if st.session_state.get("dark_mode", False) else THEME

    if completion_rate < 40:
        bar_color = theme['secondary']
        status_text = "Plants need water!"
    else:
        bar_color = theme['primary']
        status_text = "Looking Good!"

    st.markdown(f"""
    <div style="margin: 20px 0; padding: 15px; background: {theme['card_bg']}; border-radius: 16px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); border: 1px solid {theme['border']};">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span style="font-weight: bold; color: {theme['text']};">{status_text}</span>
            <span style="font-weight: bold; color: {theme['text']}; opacity: 0.8;">{int(completion_rate)}%</span>
        </div>
        <div style="background: {theme['border']}; border-radius: 12px; height: 16px; overflow: hidden;">
            <div style="
                background: {bar_color};
                height: 100%;
                width: {completion_rate}%;
                border-radius: 12px;
                transition: width 0.6s ease-in-out;
            "></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_circular_progress(current_xp, next_threshold, label="XP Progress"):
    """Circular progress bar for XP/level visualization"""
    if next_threshold == 0:
        progress_percent = 100
    else:
        progress_percent = min((current_xp / next_threshold) * 100, 100)

    circumference = 2 * 3.14159 * 50
    dash_offset = circumference - (progress_percent / 100 * circumference)

    st.markdown(f"""
    <div style="text-align: center; margin: 15px 0;">
        <svg width="120" height="120" style="transform: rotate(-90deg);">
            <circle cx="60" cy="60" r="50" fill="none"
                    stroke="#E0E0E0" stroke-width="10"/>
            <circle cx="60" cy="60" r="50" fill="none"
                    stroke="{THEME['primary']}" stroke-width="10"
                    stroke-dasharray="{circumference}"
                    stroke-dashoffset="{dash_offset}"
                    stroke-linecap="round"
                    style="transition: stroke-dashoffset 0.5s ease;"/>
        </svg>
        <div style="margin-top: -75px; padding-top: 25px;">
            <div style="font-size: 24px; font-weight: bold; color: {THEME['text']};">
                {int(progress_percent)}%
            </div>
            <div style="font-size: 11px; color: {THEME['subtext']};">{label}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_progress_history():
    """Shows daily, weekly, and monthly progress bars"""
    st.markdown("### 📈 Your Progress History")

    # Get current date
    from datetime import datetime, timedelta
    import calendar
    today = datetime.now().date()
    
    # Calculate date ranges
    week_start = today  # Start of current week period (today)
    week_end = today + timedelta(days=6)  # End of 7-day period (today + 6 days)
    month_start = today.replace(day=1)  # First day of current month
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    
    # Get tasks and completion data
    tasks = st.session_state.get("tasks", [])
    task_completed = st.session_state.get("task_completed", {})
    completion_history = st.session_state.get("task_completion_history", [])
    total_daily_tasks = len(tasks) if tasks else 1
    
    # Daily: percentage of today's tasks completed
    completed_today = sum(1 for v in task_completed.values() if v)
    daily_progress = min(int((completed_today / total_daily_tasks) * 100), 100) if total_daily_tasks > 0 else 0
    
    # Weekly: tasks completed in next 7 days (today + next 6 days) / (daily tasks * 7)
    tasks_completed_weekly = 0
    for entry in completion_history:
        entry_date = entry.get("date")
        # Handle both date objects and date strings
        if isinstance(entry_date, str):
            entry_date = datetime.strptime(entry_date, "%Y-%m-%d").date()
        elif hasattr(entry_date, 'date'):
            entry_date = entry_date.date()
        # Count tasks completed within the 7-day window (today to today+6)
        if week_start <= entry_date <= week_end:
            tasks_completed_weekly += 1
    weekly_total = total_daily_tasks * 7
    weekly_progress = min(int((tasks_completed_weekly / weekly_total) * 100), 100) if weekly_total > 0 else 0
    
    # Monthly: tasks completed this month / (daily tasks * days in month)
    tasks_completed_monthly = 0
    for entry in completion_history:
        entry_date = entry.get("date")
        # Handle both date objects and date strings
        if isinstance(entry_date, str):
            entry_date = datetime.strptime(entry_date, "%Y-%m-%d").date()
        elif hasattr(entry_date, 'date'):
            entry_date = entry_date.date()
        if entry_date >= month_start:
            tasks_completed_monthly += 1
    monthly_total = total_daily_tasks * days_in_month
    monthly_progress = min(int((tasks_completed_monthly / monthly_total) * 100), 100) if monthly_total > 0 else 0
    
    # Store for display
    st.session_state.daily_progress = daily_progress
    st.session_state.weekly_progress = weekly_progress
    st.session_state.monthly_progress = monthly_progress

    progress_data = [
        {"period": "📅 Daily", "completion": daily_progress},
        {"period": "📆 Weekly", "completion": weekly_progress},
        {"period": "📅 Monthly", "completion": monthly_progress}
    ]

    theme = DARK_THEME if st.session_state.get("dark_mode", False) else THEME

    for period in progress_data:
        st.markdown(f"""
        <div style="margin: 10px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                <span style="font-size: 12px; font-weight: bold; color: {theme['text']};">{period['period']}</span>
                <span style="font-size: 12px; color: {theme['text']}; opacity: 0.8;">{int(period['completion'])}%</span>
            </div>
            <div style="background: {theme['border']}; border-radius: 8px; height: 8px;">
                <div style="background: {theme['primary']}; height: 100%; width: {period['completion']}%; border-radius: 8px; transition: width 0.3s ease;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# -------------------------------------
# Badges System
# -------------------------------------
BADGES = {
    "first_drop": {"icon": "💧", "name": "First Drop", "desc": "Completed your first watering task!"},
    "daily_champion": {"icon": "👑", "name": "Daily Champion", "desc": "Finished all tasks for today!"},
    "week_streak": {"icon": "🔥", "name": "Week Streak", "desc": "7 days of consistent watering!"},
    "plant_master": {"icon": "🏆", "name": "Plant Master", "desc": "Earned 500 points!"},
    "early_bird": {"icon": "🌅", "name": "Early Bird", "desc": "Watered before 8 AM!"},
    "green_thumb": {"icon": "👍", "name": "Green Thumb", "desc": "All plants are healthy!"},
    "perfect_week": {"icon": "⭐", "name": "Perfect Week", "desc": "Completed all weekly tasks!"},
    "variety_lover": {"icon": "🥗", "name": "Variety Lover", "desc": "Growing 5+ different plants!"},
}

USAGE_BADGES = {
    "🥬 Herbs, vegetables, and fruits": {
        "first_harvest": {"icon": "🥬", "name": "First Harvest", "desc": "Harvested your first vegetable!"},
        "herb_master": {"icon": "🌿", "name": "Herb Master", "desc": "Successfully grew 3 different herbs!"},
        "organic_gardener": {"icon": "🌱", "name": "Organic Gardener", "desc": "Maintained organic garden for 30 days!"},
    },
    "🌺 Ornamental plants and home decor": {
        "interior_designer": {"icon": "🏠", "name": "Interior Designer", "desc": "Arranged 5 plants in your home!"},
        "bloom_master": {"icon": "🌸", "name": "Bloom Master", "desc": "Got your first flower to bloom!"},
        "air_purifier": {"icon": "💨", "name": "Air Purifier", "desc": "Growing 3 air-purifying plants!"},
    },
    "🌱 Germination, cuttings, growing from scratch": {
        "seed_starter": {"icon": "🫘", "name": "Seed Starter", "desc": "Successfully germinated your first seed!"},
        "propagation_pro": {"icon": "✂️", "name": "Propagation Pro", "desc": "Rooted 3 successful cuttings!"},
        "patient_grower": {"icon": "⏳", "name": "Patient Grower", "desc": "Waited 30 days for germination!"},
    }
}

# -------------------------------------
# Rewards System (Coins & Shop)
# -------------------------------------
COINS_PER_TASK = {
    "Easy": 5,
    "Medium": 10,
    "Hard": 15
}

SHOP_ITEMS = {
    "cosmetic": [
        {
            "id": "plant_pot_terra",
            "name": "Terra Cotta Pot",
            "icon": "🪴",
            "price": 50,
            "desc": "Classic clay pot for your virtual plant",
            "effect": "cosmetic"
        },
        {
            "id": "plant_pot_ceramic",
            "name": "Ceramic Pot",
            "icon": "🏺",
            "price": 100,
            "desc": "Decorative ceramic planter",
            "effect": "cosmetic"
        },
        {
            "id": "background_garden",
            "name": "Garden Background",
            "icon": "🏡",
            "price": 150,
            "desc": "Beautiful garden scenery",
            "effect": "cosmetic"
        },
    ],
    "boosters": [
        {
            "id": "xp_boost_2x",
            "name": "2x XP Boost",
            "icon": "⚡",
            "price": 75,
            "desc": "Double XP for next 5 tasks",
            "effect": "boost_xp",
            "duration": 5
        },
        {
            "id": "streak_freeze",
            "name": "Streak Freeze",
            "icon": "🧊",
            "price": 100,
            "desc": "Protect your streak for 1 day",
            "effect": "streak_protect",
            "duration": 1
        },
        {
            "id": "auto_water",
            "name": "Auto Water",
            "icon": "💧",
            "price": 125,
            "desc": "Automatically complete 1 task",
            "effect": "auto_water",
            "duration": 1
        },
        {
            "id": "coin_doubler",
            "name": "Coin Doubler",
            "icon": "💰",
            "price": 150,
            "desc": "Double coins for next 3 tasks",
            "effect": "coin_boost",
            "duration": 3
        },
    ],
    "plant_buddies": [
        {
            "id": "buddy_cat",
            "name": "Garden Cat Companion",
            "icon": "🐱",
            "price": 200,
            "desc": "A friendly cat to keep your plants company",
            "effect": "companion"
        },
        {
            "id": "buddy_butterfly",
            "name": "Butterfly Friend",
            "icon": "🦋",
            "price": 150,
            "desc": "Colorful butterfly visitor",
            "effect": "companion"
        },
    ]
}

def display_badges(earned_badges, show_all=False):
    theme = DARK_THEME if st.session_state.get("dark_mode", False) else THEME
    st.markdown("### 🎖️ Your Badges")
    cols = st.columns(4)
    all_badges = list(BADGES.items())

    for i, (badge_id, badge_info) in enumerate(all_badges):
        with cols[i % 4]:
            if badge_id in earned_badges:
                # Earned badge - use golden background
                bg_color = "#3D3D00" if st.session_state.get("dark_mode", False) else "#FFFDE7"
                border_color = theme['gold']
                st.markdown(f"""
                <div style="text-align: center; padding: 12px; background: {bg_color}; border-radius: 12px; margin: 5px; border: 2px solid {border_color}; height: 130px; display: flex; flex-direction: column; justify-content: center;">
                    <div style="font-size: 32px;">{badge_info['icon']}</div>
                    <div style="font-size: 13px; font-weight: bold; margin-top: 5px; color: {theme['text']};">{badge_info['name']}</div>
                    <div style="font-size: 11px; color: {theme['subtext']}; margin-top: 3px; line-height: 1.2;">{badge_info['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Locked badge
                st.markdown(f"""
                <div style="text-align: center; padding: 12px; background: {theme['card_bg']}; border-radius: 12px; margin: 5px; opacity: 0.5; height: 130px; display: flex; flex-direction: column; justify-content: center; border: 1px solid {theme['border']};">
                    <div style="font-size: 32px; filter: grayscale(100%);">🔒</div>
                    <div style="font-size: 13px; font-weight: bold; margin-top: 5px; color: {theme['subtext']};">{badge_info['name']}</div>
                </div>
                """, unsafe_allow_html=True)

def display_all_possible_badges(active_categories):
    theme = DARK_THEME if st.session_state.get("dark_mode", False) else THEME
    st.markdown("### 🎖️ Available Badges")

    st.markdown("**⭐ General Badges**")
    cols = st.columns(4)
    for i, (badge_id, badge_info) in enumerate(BADGES.items()):
        with cols[i % 4]:
             st.markdown(f"""
            <div style="text-align: center; padding: 10px; background: {theme['card_bg']}; border-radius: 10px; margin: 3px; border: 1px dashed {theme['earth']}; height: 100px; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 25px;">{badge_info['icon']}</div>
                <div style="font-size: 11px; font-weight: bold; color: {theme['text']}">{badge_info['name']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height: 25px'></div>", unsafe_allow_html=True)

    if isinstance(active_categories, str):
        active_categories = [active_categories]
    unique_cats = set(active_categories)

    first_special_cat = True
    for cat in unique_cats:
        if cat in USAGE_BADGES:
            if not first_special_cat:
                st.markdown("<div style='height: 25px'></div>", unsafe_allow_html=True)

            st.markdown(f"**🌿 Special Badges for {cat}**")
            first_special_cat = False

            specific_badges = USAGE_BADGES[cat]
            cols = st.columns(3)
            for i, (badge_id, badge_info) in enumerate(specific_badges.items()):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 10px; background: {theme['card_bg']}; border-radius: 10px; margin: 3px; border: 1px dashed {theme['primary']}; height: 100px; display: flex; flex-direction: column; justify-content: center;">
                        <div style="font-size: 25px;">{badge_info['icon']}</div>
                        <div style="font-size: 12px; font-weight: bold; color: {theme['text']}">{badge_info['name']}</div>
                    </div>
                    """, unsafe_allow_html=True)

# -------------------------------------
# XP Bar
# -------------------------------------
def display_xp_progress(current_points, level):
    if level >= len(LEVEL_THRESHOLDS) - 1:
        next_threshold = current_points * 1.5
        prev_threshold = LEVEL_THRESHOLDS[-1]
    else:
        next_threshold = LEVEL_THRESHOLDS[level]
        prev_threshold = LEVEL_THRESHOLDS[level-1] if level > 0 else 0
    
    level_range = next_threshold - prev_threshold
    points_in_level = current_points - prev_threshold
    
    if level_range <= 0: progress_percent = 100
    else: progress_percent = min(max((points_in_level / level_range) * 100, 0), 100)
    
    st.markdown(f"""
    <div style="margin: 15px 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 12px;">
            <span style="font-weight: bold; color: {THEME['text']}">🆙 Level {level}</span>
            <span style="color: {THEME['subtext']};">{current_points}/{next_threshold} XP</span>
        </div>
        <div style="background: #E0E0E0; border-radius: 10px; height: 8px; overflow: hidden;">
            <div style="background: {THEME['earth']}; height: 100%; width: {progress_percent}%; border-radius: 10px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------
# Powerups Inventory Display
# -------------------------------------
def display_powerups_inventory():
    """Display user's powerup inventory in Profile"""
    theme = DARK_THEME if st.session_state.get("dark_mode", False) else THEME
    st.markdown("### ⚡ Your Power-Ups")

    # Define all powerups that can be owned
    all_powerups = [
        {"id": "xp_boost_2x", "icon": "⚡", "name": "2x XP Boost", "qty_key": "powerup_xp_boost", "uses_left_key": "active_xp_boost_uses"},
        {"id": "streak_freeze", "icon": "🧊", "name": "Streak Freeze", "qty_key": "powerup_streak_freeze", "uses_left_key": "active_streak_freeze"},
        {"id": "auto_water", "icon": "💧", "name": "Auto Water", "qty_key": "powerup_auto_water", "uses_left_key": None},
        {"id": "coin_doubler", "icon": "💰", "name": "Coin Doubler", "qty_key": "powerup_coin_doubler", "uses_left_key": "active_coin_doubler_uses"}
    ]

    cols = st.columns(4)
    for i, powerup in enumerate(all_powerups):
        with cols[i]:
            quantity = st.session_state.get(powerup['qty_key'], 0)
            has_item = quantity > 0

            # Dark mode compatible colors
            if has_item:
                bg_color = "#3D3D00" if st.session_state.get("dark_mode", False) else "#FFF9E6"
                border_color = theme['gold']
                text_color = theme['text']
                quantity_color = theme['gold']
            else:
                bg_color = theme['card_bg']
                border_color = theme['border']
                text_color = theme['subtext']
                quantity_color = theme['subtext']

            st.markdown(f"""
            <div style="background: {bg_color}; padding: 15px; border-radius: 12px;
                 border: 2px solid {border_color}; text-align: center;
                 min-height: 120px; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 36px; margin-bottom: 8px; filter: {'none' if has_item else 'grayscale(100%) opacity(0.4)'};">
                    {powerup['icon']}
                </div>
                <div style="font-size: 12px; font-weight: bold; color: {text_color}; margin-bottom: 4px;">
                    {powerup['name']}
                </div>
                <div style="font-size: 16px; font-weight: bold; color: {quantity_color};">
                    {'x' + str(quantity) if has_item else 'None'}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Add "Use" button if powerup is available
            if has_item:
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                if st.button("Use", key=f"use_{powerup['id']}", use_container_width=True, type="primary"):
                    # Decrement quantity
                    st.session_state[powerup['qty_key']] = quantity - 1
                    
                    # Apply powerup effect
                    if powerup['id'] == 'xp_boost_2x':
                        # Activate 2x XP boost for next 5 tasks
                        st.session_state.active_xp_boost_uses = st.session_state.get("active_xp_boost_uses", 0) + 5
                        st.toast("⚡ 2x XP Boost activated! Next 5 tasks will give double XP!", icon="⚡")
                    elif powerup['id'] == 'streak_freeze':
                        # Activate streak freeze for 1 day
                        st.session_state.active_streak_freeze = True
                        st.toast("🧊 Streak Freeze activated! Your streak is protected for 1 day!", icon="🧊")
                    elif powerup['id'] == 'auto_water':
                        # Automatically complete one incomplete task
                        tasks = st.session_state.get("tasks", [])
                        task_completed = st.session_state.get("task_completed", {})
                        
                        # Find first incomplete task
                        auto_completed = False
                        for idx, task in enumerate(tasks):
                            if not task_completed.get(idx, False):
                                # Mark task as completed
                                st.session_state.task_completed[idx] = True
                                
                                # Record task completion in history
                                today = datetime.now().date()
                                completion_history = st.session_state.get("task_completion_history", [])
                                completion_history.append({"date": today, "task_index": idx})
                                st.session_state.task_completion_history = completion_history
                                
                                # Award XP and coins
                                points = task.get('points', 10)
                                difficulty = task.get('difficulty', 'Easy')
                                coins_earned = COINS_PER_TASK.get(difficulty, 5)
                                
                                # Apply active powerups
                                if st.session_state.get("active_xp_boost_uses", 0) > 0:
                                    points *= 2
                                    st.session_state.active_xp_boost_uses -= 1
                                
                                if st.session_state.get("active_coin_doubler_uses", 0) > 0:
                                    coins_earned *= 2
                                    st.session_state.active_coin_doubler_uses -= 1
                                
                                st.session_state.total_points += points
                                st.session_state.coins = st.session_state.get("coins", 0) + coins_earned
                                
                                # Check level up
                                next_lvl_points = get_next_level_threshold(st.session_state.level)
                                if st.session_state.total_points >= next_lvl_points:
                                    st.session_state.level += 1
                                    st.balloons()
                                    st.toast(f"Level Up! Level {st.session_state.level}!", icon="🆙")
                                
                                # Update streak
                                if st.session_state.streak == 0:
                                    st.session_state.streak = 1

                                # Check for daily champion badge
                                current_done_count = sum(1 for v in st.session_state.task_completed.values() if v)
                                if current_done_count == len(tasks):
                                    if "daily_champion" not in st.session_state.earned_badges:
                                        st.session_state.earned_badges.append("daily_champion")
                                        st.toast("🏆 Daily Champion!", icon="👑")
                                        st.balloons()
                                
                                auto_completed = True
                                plant_name = task.get('plant_name', 'Plant')
                                
                                # Show powerup indicators
                                powerup_indicator = ""
                                base_points = task.get('points', 10)
                                base_coins = COINS_PER_TASK.get(difficulty, 5)
                                if base_points * 2 == points:
                                    powerup_indicator += " ⚡2x"
                                if base_coins * 2 == coins_earned:
                                    powerup_indicator += " 💰2x"
                                
                                st.toast(f"💧 Auto Water used! {plant_name} task completed automatically (+{points} XP, +{coins_earned} 🪙{powerup_indicator})", icon="💧")
                                break
                        
                        if not auto_completed:
                            st.warning("No incomplete tasks to auto-complete!")
                    elif powerup['id'] == 'coin_doubler':
                        # Activate coin doubler for next 3 tasks
                        st.session_state.active_coin_doubler_uses = st.session_state.get("active_coin_doubler_uses", 0) + 3
                        st.toast("💰 Coin Doubler activated! Next 3 tasks will give double coins!", icon="💰")
                    
                    st.balloons()
                    st.rerun()

# -------------------------------------
# Active Powerups Display
# -------------------------------------
def display_active_powerups():
    """Display currently active powerups"""
    theme = DARK_THEME if st.session_state.get("dark_mode", False) else THEME
    active_powerups = []

    # Check for active XP boost
    xp_uses = st.session_state.get("active_xp_boost_uses", 0)
    if xp_uses > 0:
        active_powerups.append({"icon": "⚡", "name": "2x XP Boost", "remaining": f"{xp_uses} tasks left"})

    # Check for active coin doubler
    coin_uses = st.session_state.get("active_coin_doubler_uses", 0)
    if coin_uses > 0:
        active_powerups.append({"icon": "💰", "name": "Coin Doubler", "remaining": f"{coin_uses} tasks left"})

    # Check for active streak freeze
    if st.session_state.get("active_streak_freeze", False):
        active_powerups.append({"icon": "🧊", "name": "Streak Freeze", "remaining": "Active"})

    if active_powerups:
        st.markdown("### ✨ Active Power-Ups")
        cols = st.columns(len(active_powerups))

        # Dark mode compatible gradient
        if st.session_state.get("dark_mode", False):
            bg_gradient = "linear-gradient(135deg, #3D3D00 0%, #4A4A00 100%)"
        else:
            bg_gradient = "linear-gradient(135deg, #FFF9E6 0%, #FFE082 100%)"

        for i, powerup in enumerate(active_powerups):
            with cols[i]:
                st.markdown(f"""
                <div style="background: {bg_gradient}; padding: 12px; border-radius: 10px;
                     border: 2px solid {theme['gold']}; text-align: center;">
                    <div style="font-size: 28px; margin-bottom: 5px;">{powerup['icon']}</div>
                    <div style="font-size: 11px; font-weight: bold; color: {theme['text']}; margin-bottom: 3px;">
                        {powerup['name']}
                    </div>
                    <div style="font-size: 10px; color: {theme['text']}; opacity: 0.8;">
                        {powerup['remaining']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# -------------------------------------
# Timezone Helper
# -------------------------------------
def get_time_until_next_day(user_timezone):
    """Calculate time remaining until midnight in user's timezone"""
    try:
        user_tz = pytz.timezone(user_timezone)
        now = datetime.now(user_tz)
        midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        delta = midnight - now

        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        return hours, minutes
    except:
        # Fallback if timezone is invalid
        return 14, 30

# -------------------------------------
# New UI Component Helpers
# -------------------------------------
def display_breadcrumb(items):
    """Display breadcrumb navigation
    items: list of tuples [(label, callback), ...]
    """
    theme = DARK_THEME if st.session_state.get("dark_mode", False) else THEME
    breadcrumb_html = '<div class="breadcrumb">'
    for i, (label, callback) in enumerate(items):
        if i > 0:
            breadcrumb_html += f'<span class="breadcrumb-separator">›</span>'
        breadcrumb_html += f'<span class="breadcrumb-item">{label}</span>'
    breadcrumb_html += '</div>'
    st.markdown(breadcrumb_html, unsafe_allow_html=True)

def display_accordion(title, content, key, default_expanded=False):
    """Display an accordion/collapsible section"""
    theme = DARK_THEME if st.session_state.get("dark_mode", False) else THEME

    # Initialize state
    if f"accordion_{key}" not in st.session_state:
        st.session_state[f"accordion_{key}"] = default_expanded

    # Toggle button
    if st.button(f"{'▼' if st.session_state[f'accordion_{key}'] else '▶'} {title}", key=f"btn_{key}", use_container_width=True):
        st.session_state[f"accordion_{key}"] = not st.session_state[f"accordion_{key}"]
        st.rerun()

    # Content
    if st.session_state[f"accordion_{key}"]:
        st.markdown(f'<div style="padding: {SPACING["md"]}; background: {theme["card_bg"]}; border-radius: {SPACING["sm"]}; margin-top: {SPACING["xs"]};">', unsafe_allow_html=True)
        content()
        st.markdown('</div>', unsafe_allow_html=True)

def display_empty_state(icon, title, description, cta_text=None, cta_callback=None):
    """Display an engaging empty state"""
    theme = DARK_THEME if st.session_state.get("dark_mode", False) else THEME
    st.markdown(f"""
    <div class="empty-state">
        <div class="empty-state-icon">{icon}</div>
        <div class="empty-state-title">{title}</div>
        <div class="empty-state-description">{description}</div>
    </div>
    """, unsafe_allow_html=True)

    if cta_text and cta_callback:
        if st.button(cta_text, type="primary", use_container_width=True):
            cta_callback()

def display_achievement_animation(badge_name, badge_icon):
    """Display achievement unlock animation"""
    st.markdown(f"""
    <div class="achievement-popup">
        <div style="font-size: 64px; margin-bottom: 16px;">{badge_icon}</div>
        <h2 style="color: white; margin: 0;">Achievement Unlocked!</h2>
        <h3 style="color: white; margin-top: 8px;">{badge_name}</h3>
    </div>
    """, unsafe_allow_html=True)

def filter_tasks(tasks, search_query="", difficulty_filter=None, sort_by="default"):
    """Filter and sort tasks based on criteria"""
    filtered = tasks.copy()

    # Search filter
    if search_query:
        filtered = [t for t in filtered if
                   search_query.lower() in t.get("task_title", "").lower() or
                   search_query.lower() in t.get("plant_name", "").lower() or
                   search_query.lower() in t.get("description", "").lower()]

    # Difficulty filter
    if difficulty_filter and difficulty_filter != "All":
        filtered = [t for t in filtered if t.get("difficulty") == difficulty_filter]

    # Sort
    if sort_by == "points_high":
        filtered.sort(key=lambda x: x.get("points", 0), reverse=True)
    elif sort_by == "points_low":
        filtered.sort(key=lambda x: x.get("points", 0))
    elif sort_by == "alphabetical":
        filtered.sort(key=lambda x: x.get("task_title", ""))
    elif sort_by == "difficulty":
        difficulty_order = {"Easy": 1, "Medium": 2, "Hard": 3}
        filtered.sort(key=lambda x: difficulty_order.get(x.get("difficulty", "Easy"), 1))

    return filtered

def group_tasks_by(tasks, group_by="difficulty"):
    """Group tasks by a specific field"""
    from collections import defaultdict
    grouped = defaultdict(list)

    for task in tasks:
        if group_by == "difficulty":
            key = task.get("difficulty", "Easy")
        elif group_by == "plant":
            key = task.get("plant_name", "Unknown")
        elif group_by == "points":
            points = task.get("points", 0)
            if points < 10:
                key = "Low Points (< 10)"
            elif points < 20:
                key = "Medium Points (10-19)"
            else:
                key = "High Points (20+)"
        else:
            key = "All Tasks"

        grouped[key].append(task)

    return dict(grouped)

def display_daily_challenge():
    """Display a daily challenge for extra engagement"""
    theme = DARK_THEME if st.session_state.get("dark_mode", False) else THEME

    # Initialize daily challenge if not exists
    if "daily_challenge" not in st.session_state:
        challenges = [
            {"title": "Early Bird", "desc": "Complete 3 tasks before 10 AM", "reward": 50, "icon": "🌅", "target": 3},
            {"title": "Perfect Day", "desc": "Complete all tasks today", "reward": 100, "icon": "⭐", "target": "all"},
            {"title": "Consistency King", "desc": "Complete at least 1 task", "reward": 20, "icon": "👑", "target": 1},
            {"title": "Point Hunter", "desc": "Earn 50+ points today", "reward": 75, "icon": "🎯", "target": 50},
            {"title": "Quick Hands", "desc": "Complete 5 tasks in one session", "reward": 80, "icon": "⚡", "target": 5},
        ]
        st.session_state.daily_challenge = random.choice(challenges)
        st.session_state.daily_challenge_progress = 0
        st.session_state.daily_challenge_completed = False

    challenge = st.session_state.daily_challenge
    progress = st.session_state.daily_challenge_progress
    completed = st.session_state.daily_challenge_completed

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {theme['primary']} 0%, {theme['forest']} 100%);
                padding: {SPACING['lg']}; border-radius: {SPACING['md']}; color: white; margin-bottom: {SPACING['md']};">
        <div style="display: flex; align-items: center; gap: {SPACING['md']};">
            <div style="font-size: 48px;">{challenge['icon']}</div>
            <div style="flex: 1;">
                <div style="font-size: {TYPOGRAPHY['h4']}; font-weight: 600; margin-bottom: {SPACING['xs']};">
                    Daily Challenge: {challenge['title']}
                </div>
                <div style="font-size: {TYPOGRAPHY['body']}; opacity: 0.9;">
                    {challenge['desc']}
                </div>
                <div style="margin-top: {SPACING['sm']}; font-size: {TYPOGRAPHY['small']}; opacity: 0.8;">
                    Reward: {challenge['reward']} 🪙 coins
                </div>
            </div>
            <div style="text-align: center;">
                {'✅' if completed else '⏳'}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def _handle_task_completion(task_index, is_done, task, all_tasks, plant_name, points):
    """Helper function to handle task completion/undo"""
    new_state = not is_done
    st.session_state.task_completed[task_index] = new_state

    # Get completion history
    completion_history = st.session_state.get("task_completion_history", [])
    today = datetime.now().date()

    if new_state:  # Just completed
        if st.session_state.streak == 0:
            st.session_state.streak = 1

        # Record task completion in history
        completion_history.append({"date": today, "task_index": task_index})
        st.session_state.task_completion_history = completion_history

        # Apply active powerups
        base_points = points
        base_coins = COINS_PER_TASK.get(task.get('difficulty', 'Easy'), 5)

        # Check for active XP boost
        if st.session_state.get("active_xp_boost_uses", 0) > 0:
            points = points * 2
            st.session_state.active_xp_boost_uses -= 1

        # Check for active coin doubler
        if st.session_state.get("active_coin_doubler_uses", 0) > 0:
            base_coins = base_coins * 2
            st.session_state.active_coin_doubler_uses -= 1

        coins_earned = base_coins

        # Award XP points
        st.session_state.total_points += points

        # Award coins based on difficulty
        st.session_state.coins = st.session_state.get("coins", 0) + coins_earned

        # Show toast with powerup indicators
        powerup_indicator = ""
        if base_points != points:
            powerup_indicator += " ⚡2x"
        if base_coins != coins_earned:
            powerup_indicator += " 💰2x"

        st.toast(f"Nice! {plant_name} watered (+{points} XP, +{coins_earned} 🪙{powerup_indicator})", icon="💧")

        next_lvl_points = get_next_level_threshold(st.session_state.level)
        if st.session_state.total_points >= next_lvl_points:
            st.session_state.level += 1
            st.balloons()
            st.toast(f"Level Up! Level {st.session_state.level}!", icon="🆙")

        current_done_count = sum(1 for v in st.session_state.task_completed.values() if v)
        if current_done_count == len(all_tasks):
            if "daily_champion" not in st.session_state.earned_badges:
                st.session_state.earned_badges.append("daily_champion")
                st.toast("🏆 Daily Champion!", icon="👑")
                st.balloons()
    else:  # Undone
        # Remove task completion from history
        for i, entry in enumerate(completion_history):
            if entry.get("task_index") == task_index:
                completion_history.pop(i)
                break
        st.session_state.task_completion_history = completion_history

    st.rerun()

# -------------------------------------
# Bottom Navigation
# -------------------------------------
def display_bottom_nav(current_tab):
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    cols = st.columns(4)
    tabs_config = [
        {"id": "home", "icon": "🏠", "label": "Home"},
        {"id": "shop", "icon": "🏪", "label": "Shop"},
        {"id": "leaderboard", "icon": "🏆", "label": "Leaderboard"},
        {"id": "profile", "icon": "👤", "label": "Profile"}
    ]
    for i, tab in enumerate(tabs_config):
        with cols[i]:
            is_active = current_tab == tab["id"]
            if st.button(
                f"{tab['icon']} {tab['label']}",
                key=f"nav_{tab['id']}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.current_tab = tab["id"]
                st.rerun()

# -------------------------------------
# Leaderboard Display
# -------------------------------------
def display_leaderboard():
    theme = DARK_THEME if st.session_state.get("dark_mode", False) else THEME

    st.markdown(f"""
    <div style="text-align: center; padding: 20px; background: linear-gradient(90deg, {theme['primary']} 0%, {theme['forest']} 100%); border-radius: 15px; margin-bottom: 20px; color: white;">
        <h2 style="color: white; margin: 0;">🏆 Leaderboard</h2>
        <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0;">Community Gardeners</p>
    </div>
    """, unsafe_allow_html=True)

    friends = get_mock_leaderboard()
    user_points = st.session_state.get("total_points", 0)
    user_streak = st.session_state.get("streak", 0)
    user_level = st.session_state.get("level", 1)
    pet_name = st.session_state.get("pet_name", "Sprout")

    all_players = friends + [{"name": "🌱 You", "points": user_points, "streak": user_streak, "level": user_level, "pet_name": pet_name, "is_user": True}]
    all_players.sort(key=lambda x: x["points"], reverse=True)

    for rank, player in enumerate(all_players, 1):
        is_user = player.get("is_user", False)

        if rank == 1: medal = "🥇"
        elif rank == 2: medal = "🥈"
        elif rank == 3: medal = "🥉"
        else: medal = f"#{rank}"

        # Dark mode compatible colors
        if is_user:
            row_bg = "#1A3A1A" if st.session_state.get("dark_mode", False) else "#E8F5E9"
        else:
            row_bg = "transparent"

        row_border = f"2px solid {theme['primary']}" if is_user else f"1px solid {theme['border']}"
        name_color = theme['primary'] if is_user else theme['text']

        st.markdown(f"""
        <div style="background-color: {row_bg}; border: {row_border}; border-radius: 12px; padding: 15px; display: flex; align-items: center; margin-bottom: 8px;">
            <div style="width: 15%; font-size: 24px; text-align: center;">{medal}</div>
            <div style="width: 60%;">
                <div style="font-weight: bold; color: {name_color}; font-size: 16px;">
                    {player['name']}
                </div>
                <div style="font-size: 12px; color: {theme['subtext']};">
                    {player.get('pet_name', '?')} • Lvl {player['level']} • 🔥 {player['streak']}
                </div>
            </div>
            <div style="width: 25%; text-align: right;">
                <span style="font-weight: bold; color: {theme['text']}; font-size: 18px;">{player['points']}</span>
                <br><small style="color: {theme['subtext']};">pts</small>
            </div>
        </div>
        """, unsafe_allow_html=True)

# -------------------------------------
# Tutorial Display
# -------------------------------------
def display_tutorial():
    """Interactive tutorial overlay for first-time users"""
    st.markdown(f"""
    <div style="text-align: center; padding: 40px 20px; background: linear-gradient(135deg, {THEME['primary']} 0%, {THEME['forest']} 100%); border-radius: 20px; margin-bottom: 20px; box-shadow: 0 6px 20px rgba(0,0,0,0.15);">
        <div style="font-size: 60px; margin-bottom: 15px;">🌱</div>
        <h1 style="color: white; margin: 10px 0;">Welcome to PlantCare!</h1>
        <p style="color: rgba(255,255,255,0.9); font-size: 16px; line-height: 1.6; max-width: 500px; margin: 0 auto;">
            Your gamified plant companion that helps you keep your plants thriving while earning rewards!
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎮 How It Works")

    steps = [
        {
            "icon": "🪴",
            "title": "Add Your Plants",
            "desc": "Tell us about the plants you're growing - herbs, ornamentals, or seedlings!",
            "color": THEME['primary']
        },
        {
            "icon": "🤖",
            "title": "Get AI Recommendations",
            "desc": "Our AI creates personalized watering schedules based on your environment.",
            "color": THEME['secondary']
        },
        {
            "icon": "✅",
            "title": "Complete Daily Tasks",
            "desc": "Water your plants, earn points, level up, and unlock badges!",
            "color": THEME['earth']
        },
        {
            "icon": "🏆",
            "title": "Compete & Grow",
            "desc": "Build streaks, climb the leaderboard, and watch your virtual plant buddy thrive!",
            "color": THEME['success']
        }
    ]

    for i, step in enumerate(steps, 1):
        st.markdown(f"""
        <div style="background: white; padding: 20px; border-radius: 12px; margin: 15px 0; border-left: 4px solid {step['color']}; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            <div style="display: flex; align-items: center; gap: 15px;">
                <div style="font-size: 40px; min-width: 50px;">{step['icon']}</div>
                <div>
                    <div style="font-size: 18px; font-weight: bold; color: {THEME['text']}; margin-bottom: 5px;">
                        {i}. {step['title']}
                    </div>
                    <div style="font-size: 14px; color: {THEME['subtext']}; line-height: 1.4;">
                        {step['desc']}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Skip Tutorial ⏭️", use_container_width=True, type="secondary"):
            st.session_state.show_tutorial = False
            st.session_state.tutorial_completed = True
            st.rerun()

    with col2:
        if st.button("Let's Get Started! 🚀", use_container_width=True, type="primary"):
            st.session_state.show_tutorial = False
            st.session_state.tutorial_completed = True
            st.rerun()

    # Option to disable forever
    if st.checkbox("Don't show this again"):
        st.session_state.tutorial_completed = True

# -------------------------------------
# Profile Display
# -------------------------------------
def display_profile():
    pet_name = st.session_state.get("pet_name", "Sprout")
    total_points = st.session_state.get("total_points", 0)
    level = st.session_state.get("level", 1)
    streak = st.session_state.get("streak", 0)
    earned_badges = st.session_state.get("earned_badges", ["first_drop"])
    plant_list = st.session_state.get("plant_list", [])
    
    st.markdown(f"""
    <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, {THEME['primary']} 0%, {THEME['forest']} 100%); border-radius: 20px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
        <div style="font-size: 60px; margin-bottom: 10px; background: rgba(255,255,255,0.2); width: 100px; height: 100px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px auto; border: 3px solid rgba(255,255,255,0.3);">👤</div>
        <h2 style="color: white; margin: 0;">Your Profile</h2>
        <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0;">Plant Parent & Nature Lover</p>
    </div>
    """, unsafe_allow_html=True)
    
    theme = DARK_THEME if st.session_state.get("dark_mode", False) else THEME

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style="background: {theme['card_bg']}; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid {theme['border']};">
            <div style="font-size: 24px; font-weight: bold; color: {theme['primary']}">⭐ {total_points}</div>
            <div style="font-size: 12px; color: {theme['subtext']}">Points</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background: {theme['card_bg']}; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid {theme['border']};">
            <div style="font-size: 24px; font-weight: bold; color: {theme['secondary']}">📊 {level}</div>
            <div style="font-size: 12px; color: {theme['subtext']}">Level</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="background: {theme['card_bg']}; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid {theme['border']};">
            <div style="font-size: 24px; font-weight: bold; color: {theme['earth']}">🔥 {streak}</div>
            <div style="font-size: 12px; color: {theme['subtext']}">Streak</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    display_powerups_inventory()
    display_active_powerups()

    st.markdown("---")
    st.markdown("### 🌿 Your Garden")
    
    st.info("💡 **AI Insight:** Our system can help you target the timing of important tasks like repotting and pruning for specific plants.")

    if plant_list:
        for p in plant_list:
            p_name = p.get('name', 'Unknown').title()
            p_date_str = p.get('date_added', '2025-01-01')
            p_icon = p.get('icon', '🌱')
            p_type = p.get('type', '')
            
            insights = get_plant_insight(p_name, p_type)

            # Dark mode compatible insight background
            if st.session_state.get("dark_mode", False):
                insight_bg = "#1A3A1A"
                insight_text_color = theme['text']
            else:
                insight_bg = "#E8F5E9"
                insight_text_color = THEME['text']

            with st.expander(f"{p_icon} {p_name}"):
                st.markdown(f"""
                <div style="background: {insight_bg}; padding: 15px; border-radius: 8px; border-left: 4px solid {theme['primary']}; margin-bottom: 10px; color: {insight_text_color};">
                    <strong>🧹 Cleaning:</strong> {insights['clean']}<br>
                    <strong>🪴 Repotting:</strong> {insights['repot']}<br>
                    <strong>✂️ Pruning:</strong> {insights['prune']}<br>
                    <strong>🧺 Harvest:</strong> {insights['harvest']}<br>
                    <strong>🧪 Fertilizing:</strong> {insights['fertilize']}
                </div>
                """, unsafe_allow_html=True)
                st.caption(f"Added to garden: {p_date_str}")
    else:
        st.info("No plants added yet.")

    st.markdown("---")
    display_badges(earned_badges)
    
    st.markdown("---")
    display_progress_history()

    st.markdown("---")

    st.markdown("### ⚙️ Settings")

    # Pet Name
    new_pet_name = st.text_input("🌱 Rename your plant buddy:", value=pet_name)
    if new_pet_name != pet_name:
        st.session_state.pet_name = new_pet_name
        st.success("Name updated!")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Dark Mode Toggle
    st.markdown("**🌓 Appearance**")
    dark_mode = st.checkbox(
        "Dark Mode",
        value=st.session_state.get("dark_mode", False),
        help="Switch between light and dark themes"
    )

    if dark_mode != st.session_state.get("dark_mode", False):
        st.session_state.dark_mode = dark_mode
        st.success("🌓 Theme updated! " + ("Dark mode enabled" if dark_mode else "Light mode enabled"))
        st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Timezone Settings
    st.markdown("**🌍 Timezone Settings**")
    common_timezones = [
        "UTC", "US/Eastern", "US/Central", "US/Pacific",
        "Europe/London", "Europe/Paris", "Asia/Tokyo",
        "Asia/Jerusalem", "Australia/Sydney"
    ]

    selected_tz = st.selectbox(
        "Your Timezone:",
        options=common_timezones,
        index=common_timezones.index(st.session_state.get("user_timezone", "UTC"))
              if st.session_state.get("user_timezone", "UTC") in common_timezones else 0
    )

    if selected_tz != st.session_state.get("user_timezone", "UTC"):
        st.session_state.user_timezone = selected_tz
        st.success(f"✓ Timezone updated to {selected_tz}")

    # Show current time in user's timezone
    try:
        user_tz = pytz.timezone(st.session_state.get("user_timezone", "UTC"))
        current_time = datetime.now(user_tz)
        st.caption(f"🕐 Current time in your zone: {current_time.strftime('%I:%M %p, %B %d')}")
    except:
        pass

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # Reminders Section
    st.markdown("**🔔 Notification Preferences**")

    reminders_enabled = st.checkbox(
        "Enable reminders",
        value=st.session_state.get("reminders_enabled", True),
        help="Receive notifications for watering tasks"
    )

    if reminders_enabled != st.session_state.get("reminders_enabled", True):
        st.session_state.reminders_enabled = reminders_enabled
        st.success("✓ Reminder settings updated!" if reminders_enabled else "🔕 Reminders disabled")

    if reminders_enabled:
        reminder_time = st.select_slider(
            "Remind me before task:",
            options=[5, 10, 15, 30, 60, 120],
            value=st.session_state.get("reminder_minutes_before", 15),
            format_func=lambda x: f"{x} minutes" if x < 60 else f"{x//60} hour{'s' if x > 60 else ''}"
        )

        if reminder_time != st.session_state.get("reminder_minutes_before", 15):
            st.session_state.reminder_minutes_before = reminder_time
            st.success(f"✓ Will remind you {reminder_time} min before tasks")

        st.caption("💡 Reminders will notify you based on your preferences")

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # Data Management
    st.markdown("**📊 Data & Privacy**")
    col_export, col_clear = st.columns(2)

    with col_export:
        if st.button("📥 Export Data", use_container_width=True):
            # Create JSON export of user data
            export_data = {
                "pet_name": st.session_state.get("pet_name", "Sprout"),
                "total_points": st.session_state.get("total_points", 0),
                "level": st.session_state.get("level", 1),
                "streak": st.session_state.get("streak", 0),
                "coins": st.session_state.get("coins", 0),
                "earned_badges": st.session_state.get("earned_badges", []),
                "plant_list": st.session_state.get("plant_list", []),
                "purchased_items": st.session_state.get("purchased_items", []),
            }
            st.download_button(
                "⬇️ Download",
                data=json.dumps(export_data, indent=2),
                file_name=f"plantcare_backup_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )

    with col_clear:
        if st.button("🗑️ Clear All Data", use_container_width=True, type="secondary"):
            st.warning("⚠️ This will delete all your progress!")

# -------------------------------------
# Shop Display
# -------------------------------------
def display_shop():
    """Display the shop interface"""
    theme = DARK_THEME if st.session_state.get("dark_mode", False) else THEME

    st.markdown(f"""
    <div style="text-align: center; padding: 20px; background: linear-gradient(90deg, {theme['gold']} 0%, {theme['earth']} 100%); border-radius: 15px; margin-bottom: 20px; color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
        <h2 style="color: white; margin: 0;">🏪 Plant Shop</h2>
        <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0;">Spend your coins wisely!</p>
    </div>
    """, unsafe_allow_html=True)

    # Display coin balance
    col1, col2 = st.columns([2.5, 1.5])
    with col1:
        st.markdown(f"""
        <div style="background: {theme['card_bg']}; padding: 15px; border-radius: 12px; text-align: center; border: 2px solid {theme['gold']}; display: flex; flex-direction: column; justify-content: center; height: 100px;">
            <div style="font-size: 32px; font-weight: bold; color: {theme['gold']}">🪙 {st.session_state.get('coins', 0)}</div>
            <div style="font-size: 12px; color: {theme['subtext']}">Your Coins</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background: {theme['card_bg']}; padding: 15px; border-radius: 12px; text-align: center; border: 2px solid {theme['primary']}; display: flex; flex-direction: column; justify-content: center; height: 100px; cursor: pointer;">
            <div style="font-size: 24px; margin-bottom: 2px;">💰</div>
            <div style="font-size: 12px; font-weight: bold; color: {theme['primary']};">Earn More</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Shop categories
    for category, items in SHOP_ITEMS.items():
        category_titles = {
            "cosmetic": "🎨 Cosmetics & Decorations",
            "boosters": "⚡ Power-Ups & Boosters",
            "plant_buddies": "🐾 Plant Companions"
        }

        st.markdown(f"### {category_titles.get(category, category.title())}")

        cols = st.columns(2)
        for i, item in enumerate(items):
            with cols[i % 2]:
                is_owned = item['id'] in st.session_state.get("purchased_items", [])

                # Dark mode compatible backgrounds
                if is_owned:
                    item_bg = "#1A3A1A" if st.session_state.get("dark_mode", False) else "#E8F5E9"
                else:
                    item_bg = theme['card_bg']

                st.markdown(f"""
                <div style="background: {item_bg};
                     padding: 15px; border-radius: 12px;
                     border: 1px solid {theme['success'] if is_owned else theme['border']};
                     margin-bottom: 10px; height: 140px;">
                    <div style="display: flex; align-items: start; gap: 10px;">
                        <div style="font-size: 40px;">{item['icon']}</div>
                        <div style="flex: 1;">
                            <div style="font-weight: bold; color: {theme['text']}; margin-bottom: 3px;">
                                {item['name']}
                            </div>
                            <div style="font-size: 11px; color: {theme['subtext']}; margin-bottom: 8px; line-height: 1.3;">
                                {item['desc']}
                            </div>
                            <div style="font-size: 14px; font-weight: bold; color: {theme['gold']};">
                                {'OWNED ✓' if is_owned else f"🪙 {item['price']}"}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # For boosters, show "Buy" instead of "Owned" (can buy multiple)
                is_booster = item.get('effect') in ['boost_xp', 'streak_protect', 'auto_water', 'coin_boost']
                show_buy_button = not is_owned or is_booster

                if show_buy_button:
                    can_afford = st.session_state.get("coins", 0) >= item['price']
                    if st.button(
                        f"Buy for {item['price']} 🪙",
                        key=f"buy_{item['id']}",
                        disabled=not can_afford,
                        use_container_width=True
                    ):
                        st.session_state.coins = st.session_state.get("coins", 0) - item['price']

                        # Add to purchased items list (for cosmetics)
                        if not is_booster:
                            purchased = st.session_state.get("purchased_items", [])
                            purchased.append(item['id'])
                            st.session_state.purchased_items = purchased

                        # For boosters, increment powerup quantity
                        if item['id'] == 'xp_boost_2x':
                            st.session_state.powerup_xp_boost = st.session_state.get("powerup_xp_boost", 0) + 1
                        elif item['id'] == 'streak_freeze':
                            st.session_state.powerup_streak_freeze = st.session_state.get("powerup_streak_freeze", 0) + 1
                        elif item['id'] == 'auto_water':
                            st.session_state.powerup_auto_water = st.session_state.get("powerup_auto_water", 0) + 1
                        elif item['id'] == 'coin_doubler':
                            st.session_state.powerup_coin_doubler = st.session_state.get("powerup_coin_doubler", 0) + 1

                        st.balloons()
                        st.toast(f"Purchased {item['name']}!", icon="🎉")
                        st.rerun()
                else:
                    st.button("Equipped ✓", key=f"equipped_{item['id']}", disabled=True, use_container_width=True)

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# -------------------------------------
# Streamlit Setup
# -------------------------------------
st.set_page_config(page_title="PlantCare - Nature Edition", page_icon="🌿", layout="centered")
inject_custom_css()

# Session State
if "page" not in st.session_state: st.session_state.page = "form"
if "tasks" not in st.session_state: st.session_state.tasks = []
if "total_points" not in st.session_state: st.session_state.total_points = 0
if "earned_badges" not in st.session_state: st.session_state.earned_badges = ["first_drop"]
if "level" not in st.session_state: st.session_state.level = 1
if "streak" not in st.session_state: st.session_state.streak = 0
if "pet_name" not in st.session_state: st.session_state.pet_name = "Sprout"
if "current_tab" not in st.session_state: st.session_state.current_tab = "home"
if "plant_list" not in st.session_state: st.session_state.plant_list = []
if "temp_plant_input" not in st.session_state: st.session_state.temp_plant_input = ""
if "task_completed" not in st.session_state: st.session_state.task_completed = {}
if "pet_name_input" not in st.session_state: st.session_state.pet_name_input = st.session_state.pet_name
if "day_view_offset" not in st.session_state: st.session_state.day_view_offset = 0

# NEW: Rewards System
if "coins" not in st.session_state: st.session_state.coins = 50  # Start with 50 coins
if "purchased_items" not in st.session_state: st.session_state.purchased_items = []

# NEW: Powerups Inventory
if "powerup_xp_boost" not in st.session_state: st.session_state.powerup_xp_boost = 1  # Start with 1 XP boost
if "powerup_streak_freeze" not in st.session_state: st.session_state.powerup_streak_freeze = 0
if "powerup_auto_water" not in st.session_state: st.session_state.powerup_auto_water = 0
if "powerup_coin_doubler" not in st.session_state: st.session_state.powerup_coin_doubler = 0

# NEW: Active Powerups (tracking active effects)
if "active_xp_boost_uses" not in st.session_state: st.session_state.active_xp_boost_uses = 0
if "active_coin_doubler_uses" not in st.session_state: st.session_state.active_coin_doubler_uses = 0
if "active_streak_freeze" not in st.session_state: st.session_state.active_streak_freeze = False

# NEW: Progress History Tracking
if "daily_progress" not in st.session_state: st.session_state.daily_progress = 0
if "weekly_progress" not in st.session_state: st.session_state.weekly_progress = 0
if "monthly_progress" not in st.session_state: st.session_state.monthly_progress = 0
if "task_completion_history" not in st.session_state: st.session_state.task_completion_history = []  # List of {"date": date, "task_index": int}

# NEW: Tutorial System
if "show_tutorial" not in st.session_state: st.session_state.show_tutorial = True
if "tutorial_completed" not in st.session_state: st.session_state.tutorial_completed = False

# NEW: Timezone Support
if "user_timezone" not in st.session_state: st.session_state.user_timezone = "UTC"
if "last_task_date" not in st.session_state: st.session_state.last_task_date = datetime.now(pytz.UTC).date()

# NEW: Reminder Settings
if "reminders_enabled" not in st.session_state: st.session_state.reminders_enabled = True
if "reminder_minutes_before" not in st.session_state: st.session_state.reminder_minutes_before = 15

# =====================================
#  PAGE 1: FORM
# =====================================
if st.session_state.page == "form":
    # Show tutorial if first time
    if st.session_state.show_tutorial and not st.session_state.tutorial_completed:
        display_tutorial()
        st.stop()

    st.markdown(f"""
    <div style="text-align: center; padding: 25px; background: {THEME['primary']}; border-radius: 20px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <h1 style="color: white; margin: 0; font-size: 2.2em;">🌱 PlantCare</h1>
        <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0 0; font-size: 1.1em;">Your Gamified Plant Watering Assistant</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("Tell us about your plants to get personalized watering tasks!")

    col_name, col_suggest = st.columns([3, 1])
    with col_name:
        pet_name_val = st.text_input("Plant Buddy Name:", value=st.session_state.get("pet_name", ""), key="pet_name_input")
        if pet_name_val and pet_name_val != st.session_state.pet_name:
            st.session_state.pet_name = pet_name_val

    with col_suggest:
        st.markdown('<div style="margin-top: 28px;"></div>', unsafe_allow_html=True)
        if st.button("🎲 Random", key="random_name", use_container_width=True):
            new_name = random.choice(PLANT_PET_NAMES)
            st.session_state.pet_name = new_name
            st.rerun()

    st.markdown("---")

    usage_type = st.radio("What type of plants do you grow?", options=USAGE_OPTIONS, index=0, key="usage_type_radio")

    st.markdown("### 🌿 Your Plants")
    is_mixed = "Mixed" in usage_type
    
    if is_mixed:
        col_type, col_inp, col_btn = st.columns([2, 2, 1])
        with col_type:
            plant_category = st.selectbox("Type", options=BASE_OPTIONS, key="current_plant_type", format_func=lambda x: CATEGORY_ICONS.get(x, x))
    else:
        col_inp, col_btn = st.columns([4, 1])
        plant_category = usage_type

    def add_plant():
        p_name = st.session_state.temp_plant_input
        if p_name.strip():
            cat = st.session_state.current_plant_type if is_mixed else usage_type
            icon = CATEGORY_ICONS.get(cat, "🌱")
            st.session_state.plant_list.append({
                "name": p_name.strip(),
                "date_added": datetime.now().strftime("%Y-%m-%d"),
                "type": cat,
                "icon": icon
            })
            st.session_state.temp_plant_input = "" 

    with col_inp:
        st.text_input("Plant Name (e.g. Basil) & Enter:", key="temp_plant_input", on_change=add_plant)
    with col_btn:
        st.markdown('<div style="margin-top: 28px;"></div>', unsafe_allow_html=True)
        st.button("Add", on_click=add_plant, use_container_width=True)

    if st.session_state.plant_list:
        st.write("Current Garden:")
        for idx, p in enumerate(st.session_state.plant_list):
            c1, c2 = st.columns([5, 1])
            with c1: st.markdown(f"{p['icon']} **{p['name']}**", unsafe_allow_html=True)
            with c2:
                if st.button("❌", key=f"del_{idx}"):
                    st.session_state.plant_list.pop(idx)
                    st.rerun()
    else:
        st.info("Your garden is empty. Add some plants above!")

    st.markdown("---")
    st.subheader("🌡️ Your Growing Conditions")
    col1, col2 = st.columns(2)
    with col1: temperature = st.slider("Average temperature (°C)", 5, 45, 25)
    with col2: humidity = st.slider("Average humidity (%)", 10, 100, 50)
    sunlight_hours = st.slider("Hours of sunlight per day", 1, 14, 6)

    if st.button("✨ Generate Watering Tasks with AI", use_container_width=True, type="primary"):
        if not st.session_state.plant_list:
            st.error("Please add at least one plant!")
            st.stop()
        
        st.session_state.usage_type = usage_type
        st.session_state.temperature = temperature
        st.session_state.humidity = humidity
        st.session_state.sunlight_hours = sunlight_hours

        plants_desc = []
        for p in st.session_state.plant_list:
            type_short = p['type'].split(',')[0]
            plants_desc.append(f"{p['name']} [{type_short}]")
        plants_str = ", ".join(plants_desc)

        prompt = f"""
        Return ONLY a JSON list of dictionaries.
        Each dictionary must contain:
        plant_name, task_title, description, frequency, best_time, water_amount, points, difficulty, tip

        IMPORTANT RULES FOR POINTS:
        - Points are determined by task difficulty.
        - Easy tasks: 10-15 points
        - Medium tasks: 20-30 points
        - Hard tasks: 35-50 points

        Difficulty must be: "Easy", "Medium", or "Hard"
        
        User's plant type: {usage_type}
        Specific plants: {plants_str}
        Temperature: {temperature}°C
        Humidity: {humidity}%
        Sunlight hours: {sunlight_hours} hours

        Generate personalized watering tasks for each plant.
        Example JSON:
        [{{"plant_name":"Basil","task_title":"Morning watering","description":"Water at soil level","frequency":"Daily","best_time":"7:00 AM","water_amount":"200ml","points":15,"difficulty":"Easy","tip":"Basil loves warm weather"}}]
        """

        with st.spinner(f"🌿 AI is creating personalized tasks for {st.session_state.pet_name}..."):
            response = generate(prompt)

        # --- FIX: ROBUST PARSING LOGIC ---
        try:
            # 1. Try regex extraction first
            match = re.search(r"\[.*\]", response, re.DOTALL)
            if match:
                json_str = match.group(0)
                st.session_state.tasks = json.loads(json_str)
            else:
                # 2. Fallback to basic clean
                cleaned = response.replace("```json", "").replace("```", "").strip()
                st.session_state.tasks = json.loads(cleaned)
        except Exception as e:
            st.warning("Could not parse AI response. Using default tasks.")
            # Fallback: create default tasks for each plant
            default_tasks = []
            for p in st.session_state.plant_list:
                default_tasks.append({
                    "plant_name": p['name'],
                    "task_title": "Daily watering",
                    "description": f"Water {p['name']} at soil level",
                    "frequency": "Daily",
                    "best_time": "8:00 AM",
                    "water_amount": "200ml",
                    "points": 10,
                    "difficulty": "Easy",
                    "tip": "Check soil moisture before watering"
                })
            st.session_state.tasks = default_tasks
            with st.expander("See raw AI response for debugging"):
                st.text(f"Error: {e}")
                st.text(response)

        st.session_state.page = "editor"
        st.rerun()

# =====================================
#  PAGE 2: EDITOR
# =====================================
elif st.session_state.page == "editor":
    st.title("✨ Your Personalized Watering Tasks")
    st.caption("AI-generated tasks. Review below.")

    tasks = st.session_state.tasks
    pet_name = st.session_state.get("pet_name", "Sprout")

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {THEME['primary']} 0%, {THEME['forest']} 100%); padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: center; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <span style="font-size: 30px;">🌱😄</span>
        <div style="font-weight: bold; margin-top: 5px;">{pet_name} says: "I can't wait to grow with you!"</div>
    </div>
    """, unsafe_allow_html=True)

    for i, task in enumerate(tasks):
        with st.container():
            col_title, col_trash = st.columns([8, 1], vertical_alignment="center")
            
            with col_title:
                st.markdown(f"#### Task {i+1}: {task.get('plant_name')}")
            
            with col_trash:
                if st.button("🗑️", key=f"remove_{i}"):
                    tasks.pop(i)
                    st.session_state.tasks = tasks
                    st.rerun()

            task["task_title"] = st.text_input("Task", value=task.get("task_title", ""), key=f"title_{i}")
            task["description"] = st.text_area("Description", value=task.get("description", ""), key=f"desc_{i}", height=60)

            if task.get("tip"):
                st.info(f"💡 **Tip:** {task['tip']}")

            col_freq, col_time, col_water = st.columns(3)
            with col_freq: task["frequency"] = st.text_input("Frequency", value=task.get("frequency", "Daily"), key=f"freq_{i}")
            with col_time: task["best_time"] = st.text_input("Time", value=task.get("best_time", "7:00 AM"), key=f"time_{i}")
            with col_water: task["water_amount"] = st.text_input("Amount", value=task.get("water_amount", "200ml"), key=f"amt_{i}")
            
            st.markdown("---")

    active_cats = []
    if st.session_state.plant_list:
        active_cats = list(set([p.get('type') for p in st.session_state.plant_list if p.get('type')]))
    
    display_all_possible_badges(active_cats if active_cats else [st.session_state.get("usage_type", "")])
    st.divider()

    if st.button("💾 Save & Start Tracking", type="primary", use_container_width=True):
        st.session_state.page = "dashboard"
        st.session_state.current_tab = "home"
        st.rerun()

    if st.button("🔄 Start Over"):
        for k in ["tasks", "plants", "usage_type", "temperature", "humidity", "sunlight_hours", "plant_list"]:
            if k in st.session_state: st.session_state.pop(k)
        st.session_state.plant_list = []
        st.session_state.page = "form"
        st.rerun()

# =====================================
#  PAGE 3: DASHBOARD
# =====================================
elif st.session_state.page == "dashboard":
    tasks = st.session_state.tasks
    pet_name = st.session_state.get("pet_name", "Sprout")
    current_tab = st.session_state.get("current_tab", "home")
    
    plant_icon_map = {p['name']: p['icon'] for p in st.session_state.plant_list}

    # Preserve completed tasks when task count changes
    if len(st.session_state.task_completed) != len(tasks):
        old_completed = st.session_state.task_completed.copy()
        st.session_state.task_completed = {i: old_completed.get(i, False) for i in range(len(tasks))}

    completed_tasks_count = sum(1 for k, v in st.session_state.task_completed.items() if v)
    total_tasks_count = len(tasks) if len(tasks) > 0 else 1
    daily_completion_percentage = (completed_tasks_count / total_tasks_count) * 100

    st.markdown(f"""
    <div style="text-align: center; padding: 20px; background: linear-gradient(90deg, {THEME['primary']} 0%, {THEME['forest']} 100%); border-radius: 15px; margin-bottom: 20px; color: white;">
        <h1 style="margin: 0; font-size: 24px;">🌱 PlantCare Dashboard</h1>
        <p style="opacity: 0.9; margin: 5px 0 0 0;">Taking care of {pet_name} together</p>
    </div>
    """, unsafe_allow_html=True)

    if current_tab == "home":
        # Custom metric cards with dark mode support
        theme = DARK_THEME if st.session_state.get("dark_mode", False) else THEME

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div style="background: {theme['card_bg']}; padding: {SPACING['md']}; border-radius: 10px; border: 1px solid {theme['border']}; text-align: center;">
                <div style="font-size: 24px; margin-bottom: 4px;">⭐</div>
                <div style="font-size: 12px; color: {theme['subtext']}; margin-bottom: 4px;">Points</div>
                <div style="font-size: 24px; font-weight: 700; color: {theme['text']};">{st.session_state.total_points}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div style="background: {theme['card_bg']}; padding: {SPACING['md']}; border-radius: 10px; border: 1px solid {theme['border']}; text-align: center;">
                <div style="font-size: 24px; margin-bottom: 4px;">🪙</div>
                <div style="font-size: 12px; color: {theme['subtext']}; margin-bottom: 4px;">Coins</div>
                <div style="font-size: 24px; font-weight: 700; color: {theme['text']};">{st.session_state.get("coins", 0)}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div style="background: {theme['card_bg']}; padding: {SPACING['md']}; border-radius: 10px; border: 1px solid {theme['border']}; text-align: center;">
                <div style="font-size: 24px; margin-bottom: 4px;">✅</div>
                <div style="font-size: 12px; color: {theme['subtext']}; margin-bottom: 4px;">Tasks</div>
                <div style="font-size: 24px; font-weight: 700; color: {theme['text']};">{completed_tasks_count}/{total_tasks_count}</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div style="background: {theme['card_bg']}; padding: {SPACING['md']}; border-radius: 10px; border: 1px solid {theme['border']}; text-align: center;">
                <div style="font-size: 24px; margin-bottom: 4px;">🔥</div>
                <div style="font-size: 12px; color: {theme['subtext']}; margin-bottom: 4px;">Streak</div>
                <div style="font-size: 24px; font-weight: 700; color: {theme['text']};">{st.session_state.streak} day</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### 📊 Daily Goal")
        display_daily_progress(daily_completion_percentage)
        display_virtual_plant(daily_completion_percentage, pet_name)
        display_xp_progress(st.session_state.total_points, st.session_state.level)

        # Display Daily Challenge
        display_daily_challenge()

        # Task Filtering and Sorting UI
        with st.expander("🔍 Filter & Sort Tasks", expanded=False):
            col_search, col_filter, col_sort, col_group = st.columns(4)

            with col_search:
                search_query = st.text_input("🔎 Search", key="task_search", placeholder="Search tasks...")

            with col_filter:
                difficulty_filter = st.selectbox("Difficulty", ["All", "Easy", "Medium", "Hard"], key="task_difficulty_filter")

            with col_sort:
                sort_by = st.selectbox("Sort by", ["default", "points_high", "points_low", "alphabetical", "difficulty"], key="task_sort",
                                      format_func=lambda x: {
                                          "default": "Default",
                                          "points_high": "Points (High to Low)",
                                          "points_low": "Points (Low to High)",
                                          "alphabetical": "Alphabetical",
                                          "difficulty": "Difficulty"
                                      }[x])

            with col_group:
                group_by = st.selectbox("Group by", ["none", "difficulty", "plant", "points"], key="task_group",
                                       format_func=lambda x: {
                                           "none": "No Grouping",
                                           "difficulty": "Difficulty",
                                           "plant": "Plant",
                                           "points": "Points"
                                       }[x])

            # Bulk Actions
            st.markdown("#### Bulk Actions")
            col_bulk1, col_bulk2, col_bulk3, col_bulk4 = st.columns(4)

            with col_bulk1:
                if st.button("✅ Complete All", use_container_width=True):
                    for i in range(len(tasks)):
                        if not st.session_state.task_completed.get(i, False):
                            st.session_state.task_completed[i] = True
                    st.rerun()

            with col_bulk2:
                if st.button("↩️ Undo All", use_container_width=True):
                    for i in range(len(tasks)):
                        st.session_state.task_completed[i] = False
                    st.rerun()

            with col_bulk3:
                if st.button("⭐ Complete Easy", use_container_width=True):
                    for i, task in enumerate(tasks):
                        if task.get("difficulty") == "Easy":
                            st.session_state.task_completed[i] = True
                    st.rerun()

            with col_bulk4:
                if st.button("🎯 Complete Hard", use_container_width=True):
                    for i, task in enumerate(tasks):
                        if task.get("difficulty") == "Hard":
                            st.session_state.task_completed[i] = True
                    st.rerun()

        # Apply filters and sorting
        filtered_tasks = filter_tasks(tasks, search_query, difficulty_filter if difficulty_filter != "All" else None, sort_by)

        c_header, c_space, c_next = st.columns([6, 3, 3])
        
        is_next_day = st.session_state.day_view_offset == 1
        header_text = "📋 Next Day Tasks" if is_next_day else "📋 Today's Tasks"
        
        with c_header:
            st.markdown(f"### {header_text}")
        
        with c_next:
            if not is_next_day:
                if st.button("Next Day ➡️", use_container_width=True):
                    st.session_state.day_view_offset = 1
                    st.rerun()
            else:
                if st.button("⬅️ Back to Today", use_container_width=True):
                    st.session_state.day_view_offset = 0
                    st.rerun()

        if is_next_day:
            hours, minutes = get_time_until_next_day(st.session_state.user_timezone)
            st.info(f"🔒 **Tasks unlock in:** {hours}h {minutes}m (based on {st.session_state.user_timezone})")
            
            for task in tasks:
                p_name = task.get('plant_name', 'Plant')
                p_icon = plant_icon_map.get(p_name, '🪴')
                st.markdown(f"""
                <div style="background-color: #F8F9FA; padding: 15px; border-radius: 12px; border: 1px dashed #B0BEC5; margin-bottom: 10px; opacity: 0.8; height: 100%;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <div style="font-size:14px; font-weight:bold; color:#90A4AE;">🔒 {p_icon} {p_name}</div>
                            <div style="font-size:13px; color:#CFD8DC;">{task.get('task_title')}</div>
                            <div style="font-size:11px; color:#CFD8DC;">{task.get('water_amount')} • {task.get('best_time')}</div>
                        </div>
                        <div style="text-align:right;">
                             <div style="font-size: 20px;">🔒</div>
                             <div style="font-size: 10px; color: {THEME['gold']}; font-weight: bold;">LOCKED</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

        else:
            # Check if there are any tasks after filtering
            if len(filtered_tasks) == 0:
                display_empty_state(
                    "🔍",
                    "No Tasks Found",
                    "Try adjusting your filters or search terms to find tasks.",
                    "Clear Filters",
                    lambda: st.rerun()
                )
            elif group_by != "none":
                # Display tasks grouped
                grouped = group_tasks_by(filtered_tasks, group_by)
                for group_name, group_tasks in grouped.items():
                    st.markdown(f"#### {group_name}")
                    for task in group_tasks:
                        # Find original index
                        original_index = tasks.index(task)
                        is_done = st.session_state.task_completed.get(original_index, False)
                        p_name = task.get('plant_name', 'Plant')
                        p_icon = plant_icon_map.get(p_name, '🪴')
                        points = task.get('points', 10)

                        border_color = THEME['success'] if is_done else "#eee"
                        opacity = "0.6" if is_done else "1"
                        bg_color = "#F1F8E9" if is_done else "white"

                        with st.container():
                            theme = DARK_THEME if st.session_state.get("dark_mode", False) else THEME
                            st.markdown(f"""
                            <div class="task-card {'completed' if is_done else ''}">
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <div>
                                        <div style="font-size:14px; font-weight:bold; color:{theme['text']};">{p_icon} {p_name}</div>
                                        <div style="font-size:13px; color:{theme['text']}; opacity: 0.9;">{task.get('task_title')}</div>
                                        <div style="font-size:11px; color:{theme['text']}; opacity: 0.7;">{task.get('water_amount')} • {task.get('best_time')}</div>
                                    </div>
                                    <div style="font-weight:bold; color:{theme['primary']};">+{points} pts</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            col_spacer, col_camera, col_btn = st.columns([3, 0.6, 1])
                            with col_camera:
                                st.button("📷", key=f"btn_camera_g_{original_index}", disabled=True, use_container_width=True, help="AI Visual Verification (Coming Soon)")
                            with col_btn:
                                btn_label = "Undo" if is_done else "Done ✅"
                                btn_type = "secondary" if is_done else "primary"

                                if st.button(btn_label, key=f"btn_action_g_{original_index}", type=btn_type, use_container_width=True):
                                    _handle_task_completion(original_index, is_done, task, tasks, p_name, points)
            else:
                # Display tasks without grouping
                for task in filtered_tasks:
                    # Find original index
                    original_index = tasks.index(task)
                    is_done = st.session_state.task_completed.get(original_index, False)
                    p_name = task.get('plant_name', 'Plant')
                    p_icon = plant_icon_map.get(p_name, '🪴')
                    points = task.get('points', 10)

                    with st.container():
                        theme = DARK_THEME if st.session_state.get("dark_mode", False) else THEME
                        st.markdown(f"""
                        <div class="task-card {'completed' if is_done else ''}">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <div>
                                    <div style="font-size:14px; font-weight:bold; color:{theme['text']};">{p_icon} {p_name}</div>
                                    <div style="font-size:13px; color:{theme['text']}; opacity: 0.9;">{task.get('task_title')}</div>
                                    <div style="font-size:11px; color:{theme['text']}; opacity: 0.7;">{task.get('water_amount')} • {task.get('best_time')}</div>
                                </div>
                                <div style="font-weight:bold; color:{theme['primary']};">+{points} pts</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        col_spacer, col_camera, col_btn = st.columns([3, 0.6, 1])
                        with col_camera:
                            st.button("📷", key=f"btn_camera_{original_index}", disabled=True, use_container_width=True, help="AI Visual Verification (Coming Soon)")
                        with col_btn:
                            btn_label = "Undo" if is_done else "Done ✅"
                            btn_type = "secondary" if is_done else "primary"

                            if st.button(btn_label, key=f"btn_action_{original_index}", type=btn_type, use_container_width=True):
                                _handle_task_completion(original_index, is_done, task, tasks, p_name, points)

        st.divider()
        display_badges(st.session_state.earned_badges)
        st.divider()
        
        if st.button("✏️ Edit Tasks", use_container_width=True):
            st.session_state.page = "editor"
            st.rerun()

    elif current_tab == "shop":
        display_shop()

    elif current_tab == "leaderboard":
        display_leaderboard()

    elif current_tab == "profile":
        display_profile()

    st.markdown("---")
    display_bottom_nav(current_tab)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Reset Everything", use_container_width=True, type="secondary"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()