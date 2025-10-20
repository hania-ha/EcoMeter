import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils import load_user_data, get_community_leaderboard, get_monthly_challenge

st.markdown("<div class='app-header'>⚡ EcoMeter - Community Energy Insights</div>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🏆 Community Leaderboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>See how you rank against other energy-conscious households in your area!</p>", unsafe_allow_html=True)

st.markdown("---")

user_data = load_user_data()
user_name = user_data["user"]["name"]
user_eco_score = user_data["eco_score"]
user_location = user_data["user"]["location"]

leaderboard = get_community_leaderboard()

if user_eco_score > 0:
    user_entry = {
        "name": f"{user_name} (You)",
        "eco_score": user_eco_score,
        "savings": "N/A",
        "location": user_location
    }
    
    leaderboard_with_user = leaderboard.copy()
    inserted = False
    for i, entry in enumerate(leaderboard_with_user):
        if user_eco_score > entry["eco_score"]:
            leaderboard_with_user.insert(i, user_entry)
            inserted = True
            break
    
    if not inserted:
        leaderboard_with_user.append(user_entry)
else:
    leaderboard_with_user = leaderboard

# Create DataFrame
df_leaderboard = pd.DataFrame(leaderboard_with_user)
df_leaderboard['Rank'] = range(1, len(df_leaderboard) + 1)

# Reorder columns
df_leaderboard = df_leaderboard[['Rank', 'name', 'eco_score', 'savings', 'location']]
df_leaderboard.columns = ['Rank', 'User', 'EcoScore', 'Savings', 'Location']

# Display user's rank prominently
if user_eco_score > 0:
    user_rank = df_leaderboard[df_leaderboard['User'].str.contains('You')]['Rank'].values[0]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Your Rank", f"#{user_rank}")
    
    with col2:
        st.metric("Your EcoScore", user_eco_score)
    
    with col3:
        total_users = len(df_leaderboard)
        percentile = int((1 - (user_rank / total_users)) * 100)
        st.metric("Percentile", f"Top {100-percentile}%")
    
    with col4:
        if user_rank == 1:
            st.metric("Status", "🥇 Leader!")
        elif user_rank <= 3:
            st.metric("Status", "🥈 Top 3!")
        elif user_rank <= 10:
            st.metric("Status", "⭐ Top 10!")
        else:
            st.metric("Status", "🌱 Growing")
    
    st.markdown("---")

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["🏆 Overall Rankings", "📍 Local Rankings", "🎯 Challenges"])

with tab1:
    st.markdown("### 🌍 Overall Community Rankings")
    
    # Top 3 podium
    if len(df_leaderboard) >= 3:
        st.markdown("#### 🥇 Top 3 Leaders")
        
        col1, col2, col3 = st.columns(3)
        
        with col2:  # First place in middle
            first = df_leaderboard.iloc[0]
            st.markdown(f"""
                <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #f3fc9a 0%, #e8f285 100%); border-radius: 15px; margin-bottom: 10px; box-shadow: 0 8px 25px rgba(243, 252, 154, 0.4);'>
                    <h1 style='margin: 0; color: #4b5248;'>🥇</h1>
                    <h3 style='margin: 5px 0; color: #4b5248;'>{first['User']}</h3>
                    <h2 style='margin: 5px 0; color: #4b5248;'>{first['EcoScore']}</h2>
                    <p style='margin: 0; color: #4b5248;'>{first['Savings']} savings</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col1:  # Second place on left
            second = df_leaderboard.iloc[1]
            st.markdown(f"""
                <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #A8E6A3 0%, #8FD48A 100%); border-radius: 15px; margin-top: 30px; box-shadow: 0 6px 20px rgba(168, 230, 163, 0.4);'>
                    <h2 style='margin: 0; color: #4b5248;'>🥈</h2>
                    <h4 style='margin: 5px 0; color: #4b5248;'>{second['User']}</h4>
                    <h3 style='margin: 5px 0; color: #4b5248;'>{second['EcoScore']}</h3>
                    <p style='margin: 0; color: #4b5248; font-size: 14px;'>{second['Savings']} savings</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:  # Third place on right
            third = df_leaderboard.iloc[2]
            st.markdown(f"""
                <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #C8F7C5 0%, #B3E8AF 100%); border-radius: 15px; margin-top: 30px; box-shadow: 0 6px 20px rgba(200, 247, 197, 0.4);'>
                    <h2 style='margin: 0; color: #4b5248;'>🥉</h2>
                    <h4 style='margin: 5px 0; color: #4b5248;'>{third['User']}</h4>
                    <h3 style='margin: 5px 0; color: #4b5248;'>{third['EcoScore']}</h3>
                    <p style='margin: 0; color: #4b5248; font-size: 14px;'>{third['Savings']} savings</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Full leaderboard table
    st.markdown("#### 📊 Complete Rankings")
    
    # Style the dataframe
    def highlight_user(row):
        if 'You' in str(row['User']):
            return ['background-color: rgba(59, 130, 246, 0.3)'] * len(row)
        return [''] * len(row)
    
    styled_df = df_leaderboard.style.apply(highlight_user, axis=1)
    
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        height=400
    )
    
    # EcoScore distribution chart
    st.markdown("#### 📈 EcoScore Distribution")
    
    fig_dist = go.Figure()
    
    fig_dist.add_trace(go.Histogram(
        x=df_leaderboard['EcoScore'],
        nbinsx=10,
        marker_color='#3b82f6',
        opacity=0.7,
        name='Users'
    ))
    
    if user_eco_score > 0:
        fig_dist.add_vline(
            x=user_eco_score,
            line_dash="dash",
            line_color="#10b981",
            annotation_text="You",
            annotation_position="top"
        )
    
    fig_dist.update_layout(
        title="Community EcoScore Distribution",
        xaxis_title="EcoScore",
        yaxis_title="Number of Users",
        template='plotly_dark',
        height=350,
        showlegend=False
    )
    
    st.plotly_chart(fig_dist, use_container_width=True)

with tab2:
    st.markdown(f"### 📍 Rankings in {user_location}")
    
    # Filter by location
    df_local = df_leaderboard[df_leaderboard['Location'] == user_location].copy()
    df_local['Local Rank'] = range(1, len(df_local) + 1)
    
    if len(df_local) > 0:
        st.info(f"👥 **{len(df_local)}** users from {user_location} are competing!")
        
        # Display local rankings
        st.dataframe(
            df_local[['Local Rank', 'User', 'EcoScore', 'Savings']],
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Local comparison chart
        fig_local = px.bar(
            df_local.head(10),
            x='User',
            y='EcoScore',
            color='EcoScore',
            color_continuous_scale='Viridis',
            title=f"Top 10 Users in {user_location}"
        )
        
        fig_local.update_layout(
            template='plotly_dark',
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig_local, use_container_width=True)
    else:
        st.warning(f"No other users found in {user_location}. Be the first to set a benchmark!")
    
    # Location statistics
    st.markdown("#### 📊 Location Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_score = df_local['EcoScore'].mean() if len(df_local) > 0 else 0
        st.metric(f"{user_location} Avg Score", f"{avg_score:.1f}")
    
    with col2:
        national_avg = df_leaderboard['EcoScore'].mean()
        st.metric("National Average", f"{national_avg:.1f}")
    
    with col3:
        diff = avg_score - national_avg if len(df_local) > 0 else 0
        st.metric("Difference", f"{diff:+.1f}")

with tab3:
    st.markdown("### 🎯 Energy-Saving Challenges")
    
    # Current challenge
    challenge = get_monthly_challenge()
    
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); padding: 30px; border-radius: 20px; margin: 20px 0;'>
            <h2 style='color: white; margin-top: 0;'>🏅 {challenge['title']}</h2>
            <p style='color: rgba(255,255,255,0.9); font-size: 18px;'>{challenge['description']}</p>
            <hr style='border-color: rgba(255,255,255,0.3);'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <p style='color: white; margin: 5px 0;'><strong>Reward:</strong> {challenge['reward']}</p>
                    <p style='color: white; margin: 5px 0;'><strong>Participants:</strong> 👥 {challenge['participants']}</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🎯 Join This Challenge", type="primary", use_container_width=True):
        st.balloons()
        st.success("🎉 You've joined the challenge! Track your progress in the My Stats page.")
    
    st.markdown("---")
    
    # Challenge leaderboard
    st.markdown("#### 🏆 Challenge Leaderboard")
    st.caption("Top performers in current challenge")
    
    challenge_leaders = [
        {"Rank": 1, "User": "Ali Khan", "Progress": "95%", "Status": "🌟 On track"},
        {"Rank": 2, "User": "Sara Ahmed", "Progress": "88%", "Status": "🌟 On track"},
        {"Rank": 3, "User": "Usman Tariq", "Progress": "82%", "Status": "🌟 On track"},
        {"Rank": 4, "User": "Fatima Malik", "Progress": "75%", "Status": "⚠️ Needs effort"},
        {"Rank": 5, "User": "Ahmed Raza", "Progress": "68%", "Status": "⚠️ Needs effort"},
    ]
    
    df_challenge = pd.DataFrame(challenge_leaders)
    st.dataframe(df_challenge, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Upcoming challenges
    st.markdown("#### 📅 Upcoming Challenges")
    
    upcoming = [
        {
            "title": "🌙 Night Owl Challenge",
            "description": "Use appliances during off-peak hours (11 PM - 7 AM)",
            "starts": "Next Week",
            "reward": "+12 points"
        },
        {
            "title": "☀️ Solar Sunday",
            "description": "Minimize electricity usage during peak solar hours",
            "starts": "In 2 Weeks",
            "reward": "+10 points"
        },
        {
            "title": "🏠 Smart Home Week",
            "description": "Optimize all smart devices for energy efficiency",
            "starts": "In 3 Weeks",
            "reward": "+15 points"
        }
    ]
    
    for challenge in upcoming:
        with st.expander(f"{challenge['title']} - {challenge['starts']}"):
            st.write(f"**Description:** {challenge['description']}")
            st.write(f"**Reward:** {challenge['reward']}")
            st.button(f"🔔 Remind Me", key=f"remind_{challenge['title']}")
    
    st.markdown("---")
    
    # Community achievements
    st.markdown("#### 🌍 Community Impact")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Energy Saved", "12,450 kWh", "+8% this month")
    
    with col2:
        st.metric("CO₂ Reduced", "8.7 tons", "+12% this month")
    
    with col3:
        st.metric("Money Saved", "PKR 292,575", "+8% this month")
    
    st.success("🌱 Together, we're making a real difference! Keep up the great work!")

# Footer
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.session_state.page = 'Home'
        st.rerun()

with col2:
    if st.button("📈 View My Stats", use_container_width=True):
        st.session_state.page = 'Stats'
        st.rerun()

st.markdown("---")
st.caption("💡 **Tip:** Compete with friends and neighbors to make energy saving fun and rewarding!")
