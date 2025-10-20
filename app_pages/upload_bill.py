import streamlit as st
import time
from datetime import datetime
from utils import add_usage_entry, calculate_eco_score, save_bill_image

st.markdown("<div class='app-header'>⚡ EcoMeter - Community Energy Insights</div>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>📤 Upload Electricity Bill</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Upload your electricity bill or enter your usage data manually to track your energy consumption 🌱</p>", unsafe_allow_html=True)

st.markdown("---")

tab1, tab2 = st.tabs(["📄 Upload Bill Image", "⌨️ Manual Entry"])

with tab1:
    st.markdown("<h3 style='color: #03A9F4; text-align: center;'>Upload Your Bill</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #263238; text-align: center;'>Take a photo or scan your electricity bill and upload it here.</p>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose your bill file", 
        type=["jpg", "jpeg", "png", "pdf"],
        help="Supported formats: JPG, PNG, PDF"
    )
    
    if uploaded_file:
        st.success("✅ Bill uploaded successfully!")
        
        if uploaded_file.type.startswith('image'):
            st.image(uploaded_file, caption="Uploaded Bill Preview", use_column_width=True)
        else:
            st.info("📄 PDF file uploaded. Preview not available.")
        
        st.markdown("---")
        st.info("💡 **Coming Soon:** OCR (Optical Character Recognition) will automatically extract usage data from your bill!")
        
        st.markdown("### Enter Details from Bill")
        col1, col2 = st.columns(2)
        
        with col1:
            units_from_image = st.number_input(
                "Electricity Usage (kWh)", 
                min_value=0, 
                step=1,
                key="units_image",
                help="Enter the total units consumed as shown on your bill"
            )
        
        with col2:
            bill_from_image = st.number_input(
                "Total Bill Amount (PKR)", 
                min_value=0.0, 
                step=10.0,
                key="bill_image",
                help="Enter the total amount to be paid"
            )
        
        if st.button("🔍 Analyze This Bill", type="primary", key="analyze_image"):
            if units_from_image == 0 or bill_from_image == 0:
                st.warning("⚠️ Please enter both usage and bill amount!")
            else:
                with st.spinner("Calculating your EcoScore..."):
                    time.sleep(1.5)
                    
                    bill_image_filename = save_bill_image(uploaded_file)
                    
                    updated_data = add_usage_entry(units_from_image, bill_from_image, bill_image_filename)
                    eco_score = updated_data["eco_score"]
                    
                    st.success(f"✅ Bill data and image saved successfully!")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Usage", f"{units_from_image} kWh")
                    
                    with col2:
                        st.metric("Bill Amount", f"PKR {bill_from_image:,.0f}")
                    
                    with col3:
                        st.metric("Your EcoScore", eco_score)
                    
                    if eco_score >= 85:
                        st.balloons()
                        st.success("🌟 Excellent! You're among the most efficient users! Keep up the great work! 👏")
                    elif eco_score >= 70:
                        st.info("👍 Good effort! You're doing better than average. Check out AI suggestions to improve further.")
                    elif eco_score >= 50:
                        st.warning("⚠️ Your usage is above average. Try our AI recommendations to reduce consumption.")
                    else:
                        st.error("🚨 High usage detected. Let's work together to improve your energy efficiency! ⚡")
                    
                    if st.button("📈 View My Stats", key="view_stats_image"):
                        st.session_state.page = 'Stats'
                        st.rerun()

with tab2:
    st.markdown("<h3 style='color: #03A9F4; text-align: center;'>Manual Data Entry</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #263238; text-align: center;'>Don't have a bill image? Enter your usage details manually below.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        units_manual = st.number_input(
            "Electricity Usage (kWh)", 
            min_value=0, 
            step=1,
            key="units_manual",
            help="Enter the total units consumed this month"
        )
        
        billing_month = st.selectbox(
            "Billing Month",
            ["Current Month", "Last Month", "Custom"],
            help="Select the billing period"
        )
    
    with col2:
        bill_manual = st.number_input(
            "Total Bill Amount (PKR)", 
            min_value=0.0, 
            step=10.0,
            key="bill_manual",
            help="Enter the total amount to be paid"
        )
        
        household_size = st.number_input(
            "Household Size",
            min_value=1,
            max_value=20,
            value=4,
            help="Number of people in your household"
        )
    
    st.markdown("---")
    
    # Calculate estimated rate
    if units_manual > 0 and bill_manual > 0:
        rate = bill_manual / units_manual
        st.info(f"💰 Your average rate: **PKR {rate:.2f} per kWh**")
    
    if st.button("🔍 Calculate My EcoScore", type="primary", key="analyze_manual"):
        if units_manual == 0 or bill_manual == 0:
            st.warning("⚠️ Please enter both usage and bill amount!")
        else:
            with st.spinner("Calculating your EcoScore..."):
                time.sleep(1.5)
                
                # Save data and calculate eco score
                updated_data = add_usage_entry(units_manual, bill_manual)
                eco_score = updated_data["eco_score"]
                
                st.success(f"✅ Data saved successfully!")
                
                # Display results in a nice card
                st.markdown("---")
                st.markdown("### 📊 Your Results")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Usage", f"{units_manual} kWh")
                
                with col2:
                    st.metric("Bill Amount", f"PKR {bill_manual:,.0f}")
                
                with col3:
                    st.metric("Your EcoScore", eco_score)
                
                with col4:
                    avg_usage = 300
                    diff = ((units_manual - avg_usage) / avg_usage) * 100
                    st.metric("vs Average", f"{diff:+.1f}%")
                
                st.markdown("---")
                
                # Show feedback based on score
                if eco_score >= 85:
                    st.balloons()
                    st.success("🌟 Excellent! You're among the most efficient users! Keep up the great work! 👏")
                    st.info("💡 **Tip:** Share your energy-saving strategies with the community to inspire others!")
                elif eco_score >= 70:
                    st.info("👍 Good effort! You're doing better than average.")
                    st.info("💡 **Tip:** Try reducing AC usage by 30 minutes daily to boost your score by ~8 points.")
                elif eco_score >= 50:
                    st.warning("⚠️ Your usage is above average. Let's work on improving it!")
                    st.info("💡 **Tip:** Unplug devices when not in use and switch to energy-efficient appliances.")
                else:
                    st.error("🚨 High usage detected. Immediate action recommended! ⚡")
                    st.info("💡 **Tip:** Check for faulty appliances and consider a home energy audit.")
                
                # Navigation buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🏠 Back to Home", key="home_manual", use_container_width=True):
                        st.session_state.page = 'Home'
                        st.rerun()
                
                with col2:
                    if st.button("📈 View Detailed Stats", key="stats_manual", use_container_width=True):
                        st.session_state.page = 'Stats'
                        st.rerun()

# Information section
st.markdown("---")
st.markdown("### 📚 How EcoScore Works")

with st.expander("ℹ️ Click to learn more"):
    st.markdown("""
    **EcoScore** is your energy efficiency rating on a scale of 0-100:
    
    - **90-100:** 🌟 Exceptional - You're in the top 10% of efficient users
    - **80-89:** ⭐ Excellent - Better than 80% of households
    - **70-79:** 👍 Good - Above average efficiency
    - **50-69:** ⚠️ Fair - Room for improvement
    - **Below 50:** 🚨 Needs attention - High consumption detected
    
    **How it's calculated:**
    - Compares your usage to similar households in your area
    - Factors in household size and location
    - Adjusts for seasonal variations
    - Uses AI to identify optimization opportunities
    
    **Benefits of a high EcoScore:**
    - Lower electricity bills 💰
    - Reduced carbon footprint 🌍
    - Community recognition 🏆
    - Exclusive energy-saving tips 💡
    """)

st.markdown("---")
st.caption("💡 **Tip:** Upload your bill every month to track your progress and compete on the leaderboard!")
