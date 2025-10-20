import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os
from utils import load_user_data, get_ai_suggestion, get_comparison_stats, get_bill_image_path

st.markdown("<div class='app-header'>⚡ EcoMeter - Community Energy Insights</div>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>📈 My Energy Statistics</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Detailed insights into your electricity consumption and efficiency trends</p>", unsafe_allow_html=True)

st.markdown("---")

user_data = load_user_data()
usage_history = user_data["usage_history"]
current_usage = user_data["current_month"]["units"]
eco_score = user_data["eco_score"]
household_size = user_data["user"]["household_size"]

if len(usage_history) == 0 and current_usage == 0:
    st.warning("⚠️ No usage data found! Please upload your electricity bill first.")
    if st.button("📤 Upload Bill Now", type="primary"):
        st.session_state.page = 'Upload'
        st.rerun()
else:
    st.markdown("### 📊 Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current EcoScore", eco_score)
    
    with col2:
        if current_usage > 0:
            st.metric("Current Usage", f"{current_usage} kWh")
        else:
            st.metric("Latest Usage", f"{usage_history[-1]['units']} kWh" if usage_history else "N/A")
    
    with col3:
        if len(usage_history) >= 2:
            trend = usage_history[-1]['units'] - usage_history[-2]['units']
            st.metric("Monthly Trend", f"{trend:+d} kWh")
        else:
            st.metric("Monthly Trend", "N/A")
    
    with col4:
        total_months = len(usage_history)
        st.metric("Months Tracked", total_months)
    
    st.markdown("---")
    
    # Usage History Chart
    if len(usage_history) > 0:
        st.markdown("### 📉 Usage History")
        
        # Prepare data for chart
        df_history = pd.DataFrame(usage_history)
        
        # Create line chart with Plotly
        fig = go.Figure()
        
        # Add usage line
        fig.add_trace(go.Scatter(
            x=df_history['month'],
            y=df_history['units'],
            mode='lines+markers',
            name='Your Usage',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=10, color='#3b82f6'),
            hovertemplate='<b>%{x}</b><br>Usage: %{y} kWh<extra></extra>'
        ))
        
        # Add community average line
        avg_line = [300] * len(df_history)
        fig.add_trace(go.Scatter(
            x=df_history['month'],
            y=avg_line,
            mode='lines',
            name='Community Average',
            line=dict(color='#10b981', width=2, dash='dash'),
            hovertemplate='<b>%{x}</b><br>Average: %{y} kWh<extra></extra>'
        ))
        
        fig.update_layout(
            title="Monthly Electricity Usage Trend",
            xaxis_title="Month",
            yaxis_title="Usage (kWh)",
            hovermode='x unified',
            template='plotly_dark',
            height=400,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Bill Amount Chart
        st.markdown("### 💰 Bill Amount History")
        
        fig_bill = go.Figure()
        
        fig_bill.add_trace(go.Bar(
            x=df_history['month'],
            y=df_history['bill'],
            name='Bill Amount',
            marker_color='#f59e0b',
            hovertemplate='<b>%{x}</b><br>Bill: PKR %{y:,.0f}<extra></extra>'
        ))
        
        fig_bill.update_layout(
            title="Monthly Bill Amount",
            xaxis_title="Month",
            yaxis_title="Amount (PKR)",
            template='plotly_dark',
            height=350
        )
        
        st.plotly_chart(fig_bill, use_container_width=True)
        
        st.markdown("---")
        
        # Comparison with Community
        st.markdown("### 🏘️ Community Comparison")
        
        if current_usage > 0:
            comparison = get_comparison_stats(current_usage, household_size)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Gauge chart for percentile
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=comparison['percentile'],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Efficiency Percentile", 'font': {'size': 20}},
                    delta={'reference': 50, 'increasing': {'color': "#10b981"}},
                    gauge={
                        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
                        'bar': {'color': "#3b82f6"},
                        'bgcolor': "rgba(255,255,255,0.1)",
                        'borderwidth': 2,
                        'bordercolor': "white",
                        'steps': [
                            {'range': [0, 25], 'color': 'rgba(239, 68, 68, 0.3)'},
                            {'range': [25, 50], 'color': 'rgba(251, 191, 36, 0.3)'},
                            {'range': [50, 75], 'color': 'rgba(34, 197, 94, 0.3)'},
                            {'range': [75, 100], 'color': 'rgba(16, 185, 129, 0.3)'}
                        ],
                        'threshold': {
                            'line': {'color': "white", 'width': 4},
                            'thickness': 0.75,
                            'value': comparison['percentile']
                        }
                    }
                ))
                
                fig_gauge.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': "white", 'family': "Inter"},
                    height=300
                )
                
                st.plotly_chart(fig_gauge, use_container_width=True)
                
                st.info(f"🎯 You're more efficient than **{comparison['percentile']}%** of households in your area!")
            
            with col2:
                # Comparison bar chart
                comparison_data = {
                    'Category': ['Your Usage', 'Community Avg', 'Efficient Users'],
                    'Usage (kWh)': [
                        comparison['your_usage'],
                        comparison['community_avg'],
                        comparison['efficient_households_avg']
                    ]
                }
                
                df_comp = pd.DataFrame(comparison_data)
                
                fig_comp = px.bar(
                    df_comp,
                    x='Category',
                    y='Usage (kWh)',
                    color='Category',
                    color_discrete_map={
                        'Your Usage': '#3b82f6',
                        'Community Avg': '#10b981',
                        'Efficient Users': '#8b5cf6'
                    },
                    title="Usage Comparison"
                )
                
                fig_comp.update_layout(
                    template='plotly_dark',
                    height=300,
                    showlegend=False
                )
                
                st.plotly_chart(fig_comp, use_container_width=True)
                
                if comparison['potential_savings'] > 0:
                    savings_pkr = comparison['potential_savings'] * 23.5
                    st.warning(f"💡 Potential savings: **{comparison['potential_savings']} kWh** (≈ PKR {savings_pkr:,.0f}/month)")
                else:
                    st.success("🌟 You're already among the most efficient users!")
        
        st.markdown("---")
        
        # Show uploaded bill images
        st.markdown("### 📸 Uploaded Bill Images")
        
        # Check if there are any bill images
        bill_images = []
        if current_usage > 0 and user_data["current_month"].get("bill_image"):
            bill_images.append({
                "month": "Current Month",
                "filename": user_data["current_month"]["bill_image"]
            })
        
        for entry in reversed(usage_history):
            if entry.get("bill_image"):
                bill_images.append({
                    "month": entry["month"],
                    "filename": entry["bill_image"]
                })
        
        if bill_images:
            # Show bills in columns
            cols_per_row = 3
            for i in range(0, len(bill_images), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(bill_images):
                        bill = bill_images[i + j]
                        image_path = get_bill_image_path(bill["filename"])
                        
                        with col:
                            if image_path and os.path.exists(image_path):
                                st.image(image_path, caption=f"📄 {bill['month']}", use_column_width=True)
                            else:
                                st.info(f"📄 {bill['month']}\n\n(Image not found)")
        else:
            st.info("📷 No bill images uploaded yet. Upload a bill image to see it here!")
        
        st.markdown("---")
        
        # Detailed Statistics Table
        st.markdown("### 📋 Detailed History")
        
        # Add calculated columns
        df_display = df_history.copy()
        df_display['Rate (PKR/kWh)'] = (df_display['bill'] / df_display['units']).round(2)
        df_display['vs Avg'] = ((df_display['units'] - 300) / 300 * 100).round(1).astype(str) + '%'
        
        # Rename columns for display
        df_display = df_display.rename(columns={
            'month': 'Month',
            'units': 'Usage (kWh)',
            'bill': 'Bill (PKR)'
        })
        
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )
        
        # Download data option
        csv = df_display.to_csv(index=False)
        st.download_button(
            label="📥 Download Usage History (CSV)",
            data=csv,
            file_name=f"ecometer_usage_history_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        st.markdown("---")
        
        # AI Insights
        st.markdown("### 🤖 AI-Powered Insights")
        
        suggestions = get_ai_suggestion(eco_score, current_usage if current_usage > 0 else usage_history[-1]['units'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💡 Recommendations")
            for i, suggestion in enumerate(suggestions[:3]):
                st.info(suggestion)
        
        with col2:
            st.markdown("#### 📊 Key Insights")
            
            # Calculate insights
            if len(usage_history) >= 3:
                recent_avg = sum([h['units'] for h in usage_history[-3:]]) / 3
                overall_avg = sum([h['units'] for h in usage_history]) / len(usage_history)
                trend_direction = "increasing" if recent_avg > overall_avg else "decreasing"
                
                st.success(f"📈 Your 3-month average: **{recent_avg:.0f} kWh**")
                st.info(f"📊 Overall average: **{overall_avg:.0f} kWh**")
                
                if trend_direction == "decreasing":
                    st.success(f"✅ Your usage is **{trend_direction}** - great job!")
                else:
                    st.warning(f"⚠️ Your usage is **{trend_direction}** - consider our recommendations")
            
            # Best and worst months
            if len(usage_history) >= 2:
                best_month = min(usage_history, key=lambda x: x['units'])
                worst_month = max(usage_history, key=lambda x: x['units'])
                
                st.success(f"🌟 Best month: **{best_month['month']}** ({best_month['units']} kWh)")
                st.error(f"⚡ Highest usage: **{worst_month['month']}** ({worst_month['units']} kWh)")
        
        st.markdown("---")
        
        # Usage breakdown (simulated)
        st.markdown("### 🏠 Estimated Usage Breakdown")
        st.caption("Based on typical household consumption patterns")
        
        # Simulate appliance breakdown
        total = current_usage if current_usage > 0 else usage_history[-1]['units']
        
        breakdown = {
            'Air Conditioning': total * 0.40,
            'Refrigerator': total * 0.15,
            'Lighting': total * 0.12,
            'Water Heater': total * 0.10,
            'Washing Machine': total * 0.08,
            'TV & Entertainment': total * 0.07,
            'Other Appliances': total * 0.08
        }
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=list(breakdown.keys()),
            values=list(breakdown.values()),
            hole=.4,
            marker=dict(colors=['#ef4444', '#f59e0b', '#fbbf24', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899'])
        )])
        
        fig_pie.update_layout(
            title="Appliance-wise Usage Distribution",
            template='plotly_dark',
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
        
        st.info("💡 **Tip:** Air conditioning typically accounts for 40% of household electricity usage. Optimizing AC usage can lead to significant savings!")

# Footer actions
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.session_state.page = 'Home'
        st.rerun()

with col2:
    if st.button("📤 Upload New Bill", use_container_width=True):
        st.session_state.page = 'Upload'
        st.rerun()

with col3:
    if st.button("🏆 View Leaderboard", use_container_width=True):
        st.session_state.page = 'Leaderboard'
        st.rerun()
