import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from utils import (
    load_user_data, 
    get_ai_suggestion, 
    get_comparison_stats,
    get_monthly_challenge,
    get_achievements
)

st.set_page_config(
    page_title="EcoMeter - Community Energy Insights",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'page' not in st.session_state:
    st.session_state.page = 'Home'

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    .main {
        background: #FFFFFF;
        font-family: 'Inter', sans-serif;
        color: #4b5248;
    }
    
    .stMetricLabel {
        color: #4b5248 !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }
    
    .stMetricValue {
        color: #A8E6A3 !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }
    
    .eco-score-card {
        background: linear-gradient(135deg, #A8E6A3 0%, #8FD48A 100%);
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(168, 230, 163, 0.4);
    }
    
    .eco-score-value {
        font-size: 72px;
        font-weight: 800;
        color: #4b5248;
        text-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .eco-score-label {
        font-size: 16px;
        color: #4b5248;
        margin-top: -10px;
        font-weight: 600;
    }
    
    .section-header {
        font-size: 24px;
        font-weight: 700;
        color: #A8E6A3;
        margin-bottom: 20px;
        margin-top: 20px;
        text-align: center;
    }
    
    .stat-card {
        background: rgba(168, 230, 163, 0.15);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(168, 230, 163, 0.4);
        backdrop-filter: blur(10px);
    }
    
    .achievement-badge {
        background: linear-gradient(135deg, #f3fc9a 0%, #e8f285 100%);
        padding: 10px 20px;
        border-radius: 25px;
        display: inline-block;
        margin: 5px;
        font-weight: 600;
        color: #4b5248;
        box-shadow: 0 4px 15px rgba(243, 252, 154, 0.4);
    }
    
    .challenge-card {
        background: linear-gradient(135deg, #C8F7C5 0%, #B3E8AF 100%);
        padding: 20px;
        border-radius: 15px;
        color: #4b5248;
        margin: 10px 0;
        box-shadow: 0 8px 25px rgba(200, 247, 197, 0.4);
    }
    
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f5f9f5 0%, #e8f3e8 100%);
    }
    
    .app-header {
        background: linear-gradient(135deg, #A8E6A3 0%, #8FD48A 100%);
        padding: 20px;
        text-align: center;
        color: #4b5248;
        font-size: 28px;
        font-weight: 700;
        margin: -70px -70px 30px -70px;
        box-shadow: 0 4px 15px rgba(168, 230, 163, 0.3);
    }
    
    .sidebar-header {
        text-align: center;
        color: #A8E6A3;
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 20px;
        padding: 15px;
        background: rgba(168, 230, 163, 0.2);
        border-radius: 10px;
    }
    
    .quick-stats {
        text-align: right;
        background: rgba(168, 230, 163, 0.15);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(168, 230, 163, 0.4);
    }
    
    h1, h2, h3 {
        color: #4b5248 !important;
        text-align: center;
    }
    
    p {
        color: #4b5248;
        text-align: center;
    }
    
    .stMarkdown p {
        color: #4b5248;
    }
    
    div[data-testid="stMarkdownContainer"] p {
        color: #4b5248;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #A8E6A3 0%, #8FD48A 100%);
        color: #4b5248;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #8FD48A 0%, #7BC271 100%);
        box-shadow: 0 4px 15px rgba(168, 230, 163, 0.4);
    }
    
    .stAlert p {
        color: #4b5248 !important;
    }
    
    div[data-testid="stSidebar"] p {
        color: #4b5248 !important;
    }
    
    div[data-testid="stSidebar"] h3 {
        color: #A8E6A3 !important;
    }
    
    .main .block-container p {
        color: #4b5248;
    }
    
    .eco-score-card p,
    .challenge-card p,
    .achievement-badge p {
        color: #4b5248 !important;
    }
    </style>
""", unsafe_allow_html=True)

user_data = load_user_data()
user_name = user_data["user"]["name"]
eco_score = user_data["eco_score"]
current_usage = user_data["current_month"]["units"]
usage_history = user_data["usage_history"]

if len(usage_history) > 0:
    last_month_usage = usage_history[-1]["units"]
    usage_change = current_usage - last_month_usage if current_usage > 0 else 0
    percentage_change = (usage_change / last_month_usage * 100) if last_month_usage > 0 else 0
else:
    last_month_usage = 0
    usage_change = 0
    percentage_change = 0

with st.sidebar:
    st.markdown("<div class='sidebar-header'>⚡ EcoMeter</div>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("<h3 style='color: #03A9F4; text-align: center;'>🧭 Navigation</h3>", unsafe_allow_html=True)
    
    if st.button("🏠 Home", key="nav_home", use_container_width=True):
        st.session_state.page = 'Home'
        st.rerun()
    
    if st.button("📤 Upload Bill", key="nav_upload", use_container_width=True):
        st.session_state.page = 'Upload'
        st.rerun()
    
    if st.button("📈 My Stats", key="nav_stats", use_container_width=True):
        st.session_state.page = 'Stats'
        st.rerun()
    
    if st.button("🏆 Leaderboard", key="nav_leaderboard", use_container_width=True):
        st.session_state.page = 'Leaderboard'
        st.rerun()
    
    st.markdown("---")
    
    st.markdown("<div class='quick-stats'>", unsafe_allow_html=True)
    st.markdown("### 📊 Quick Stats")
    st.metric("Your EcoScore", eco_score)
    st.metric("Current Usage", f"{current_usage} kWh" if current_usage > 0 else "No data")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"<p style='text-align: center; color: #4b5248;'>👤 {user_name}</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #4b5248;'>EcoMeter © 2025</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #4b5248;'>Built with ❤️ by Hania Haroon</p>", unsafe_allow_html=True)

if st.session_state.page == 'Home':
    st.markdown("<div class='app-header'>⚡ EcoMeter - Community Energy Insights</div>", unsafe_allow_html=True)
    
    st.markdown(f"<h2 style='text-align: center; color: #4b5248;'>Welcome back, {user_name} 👋</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #4b5248;'>Track your electricity usage, compare with your community, and boost your EcoScore 🌿</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    if current_usage == 0:
        st.warning("⚠️ No usage data found! Please upload your electricity bill to get started.")
        if st.button("📤 Upload Bill Now", type="primary"):
            st.session_state.page = 'Upload'
            st.rerun()
    else:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("<div class='section-header'>Your EcoScore</div>", unsafe_allow_html=True)
            st.markdown(f"""
                <div class='eco-score-card'>
                    <div class='eco-score-value'>{eco_score}</div>
                    <div class='eco-score-label'>out of 100</div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if eco_score >= 85:
                st.success("🌟 Excellent! You're among the most energy-efficient users!")
            elif eco_score >= 70:
                st.info("👍 Good! You're doing better than average.")
            elif eco_score >= 50:
                st.warning("⚠️ Room for improvement. Check our AI suggestions below.")
            else:
                st.error("🚨 High usage detected. Immediate action recommended!")
        
        with col2:
            st.markdown("<div class='section-header'>Usage Summary</div>", unsafe_allow_html=True)
            
            col2a, col2b, col2c = st.columns(3)
            
            with col2a:
                st.metric(
                    "This Month's Usage", 
                    f"{current_usage} kWh",
                    f"{percentage_change:+.1f}%" if percentage_change != 0 else "No change"
                )
            
            with col2b:
                bill_estimate = current_usage * 23.5
                st.metric("Bill Estimate", f"PKR {bill_estimate:,.0f}")
            
            with col2c:
                st.metric("Community Average", "300 kWh")
            
            # Comparison stats
            if current_usage > 0:
                comparison = get_comparison_stats(current_usage, user_data["user"]["household_size"])
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                if comparison["difference"] > 0:
                    st.error(f"📊 You're using **{comparison['difference_percent']:+.1f}%** more energy than the community average")
                elif comparison["difference"] < 0:
                    st.success(f"📊 You're using **{abs(comparison['difference_percent']):.1f}%** less energy than the community average! 🎉")
                else:
                    st.info("📊 You're using exactly the community average amount of energy")
                
                # Percentile ranking
                st.info(f"🎯 You're in the **{comparison['percentile']}th percentile** of energy efficiency in your area")
        
        st.markdown("---")
        
        # AI Suggestions
        st.markdown("<div class='section-header'>💡 AI-Powered Suggestions</div>", unsafe_allow_html=True)
        
        suggestions = get_ai_suggestion(eco_score, current_usage)
        
        for i, suggestion in enumerate(suggestions[:3]):  # Show top 3 suggestions
            st.info(suggestion)
        
        st.markdown("---")
        
        # Monthly Challenge
        st.markdown("<div class='section-header'>🎯 Monthly Challenge</div>", unsafe_allow_html=True)
        
        challenge = get_monthly_challenge()
        st.markdown(f"""
            <div class='challenge-card'>
                <h3>🏅 {challenge['title']}</h3>
                <p>{challenge['description']}</p>
                <p><strong>Reward:</strong> {challenge['reward']}</p>
                <p>👥 {challenge['participants']} participants</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Join Challenge", type="primary"):
            st.balloons()
            st.success("🎉 You've joined the challenge! Good luck!")
        
        st.markdown("---")
        
        # Achievements
        achievements = get_achievements(eco_score, len(usage_history))
        
        if achievements:
            st.markdown("<div class='section-header'>🏆 Your Achievements</div>", unsafe_allow_html=True)
            
            achievement_html = ""
            for achievement in achievements:
                achievement_html += f"""
                    <span class='achievement-badge'>
                        {achievement['icon']} {achievement['title']}
                    </span>
                """
            
            st.markdown(achievement_html, unsafe_allow_html=True)

elif st.session_state.page == 'Upload':
    with open('app_pages/upload_bill.py', 'r', encoding='utf-8') as f:
        exec(f.read())

elif st.session_state.page == 'Stats':
    with open('app_pages/my_stats.py', 'r', encoding='utf-8') as f:
        exec(f.read())

elif st.session_state.page == 'Leaderboard':
    with open('app_pages/leaderboard.py', 'r', encoding='utf-8') as f:
        exec(f.read())
