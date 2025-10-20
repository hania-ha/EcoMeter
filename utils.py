import json
import os
from datetime import datetime, timedelta
import random
import shutil

DATA_FILE = "user_data.json"
BILLS_FOLDER = "uploaded_bills"

def load_user_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return initialize_default_data()

def save_user_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def initialize_default_data():
    return {
        "user": {
            "name": "Hania",
            "household_size": 4,
            "location": "Lahore",
            "joined_date": datetime.now().strftime("%Y-%m-%d")
        },
        "usage_history": [
            {"month": "Aug 2024", "units": 280, "bill": 6580},
            {"month": "Sep 2024", "units": 295, "bill": 6932},
            {"month": "Oct 2024", "units": 290, "bill": 6815}
        ],
        "current_month": {
            "units": 0,
            "bill": 0,
            "date_uploaded": None
        },
        "eco_score": 0,
        "achievements": [],
        "challenges_completed": 0
    }

def calculate_eco_score(units_used, household_size=4):
    avg_per_person = 75
    expected_usage = avg_per_person * household_size
    if units_used <= expected_usage * 0.7:  
        score = 95 + random.randint(0, 5)
    elif units_used <= expected_usage:  
        score = 80 + int((expected_usage - units_used) / expected_usage * 15)
    elif units_used <= expected_usage * 1.3:  
        score = 60 + int((1 - (units_used - expected_usage) / (expected_usage * 0.3)) * 20)
    else:  
        score = max(30, 60 - int((units_used - expected_usage * 1.3) / expected_usage * 30))
    return min(100, max(0, score))

def get_ai_suggestion(eco_score, units_used, avg_usage=300):
    suggestions = []
    if eco_score >= 85:
        suggestions = [
            " Excellent work! You're in the top 10% of efficient users.",
            " Consider installing smart plugs to monitor standby power consumption.",
            " Share your energy-saving tips with the community to earn bonus points!"
        ]
    elif eco_score >= 70:
        suggestions = [
            " Good job! You're doing better than average.",
            " Reduce AC runtime by 30 minutes daily to save ~8% energy.",
            " Switch to LED bulbs if you haven't already - save up to 75% on lighting costs.",
            " Use heavy appliances during off-peak hours (11 PM - 7 AM) for lower rates."
        ]
    elif eco_score >= 50:
        suggestions = [
            " Your usage is above average. Let's work on improving it!",
            " Set your AC to 24°C instead of 18°C - save up to 20% energy.",
            " Unplug devices when not in use - they consume power even on standby.",
            " Use washing machine and dishwasher only with full loads.",
            " Replace old appliances with energy-efficient models (look for 5-star ratings)."
        ]
    else:
        suggestions = [
            " High energy consumption detected! Immediate action recommended.",
            " Check for faulty appliances or wiring - they may be consuming excess power.",
            " Your AC might be the biggest culprit - service it and use it wisely.",
            " Switch off lights and fans when leaving rooms.",
            " Track your daily usage to identify peak consumption times.",
            " Consider a home energy audit to find hidden energy drains."
        ]
    if units_used > avg_usage * 1.5:
        suggestions.insert(0, f" You're using {int((units_used/avg_usage - 1) * 100)}% more than the community average!")
    return suggestions

def get_community_leaderboard():
    users = [
        {"name": "Ali Khan", "eco_score": 94, "savings": "25%", "location": "Lahore"},
        {"name": "Sara Ahmed", "eco_score": 89, "savings": "18%", "location": "Lahore"},
        {"name": "Usman Tariq", "eco_score": 85, "savings": "15%", "location": "Islamabad"},
        {"name": "Fatima Malik", "eco_score": 82, "savings": "12%", "location": "Lahore"},
        {"name": "Ahmed Raza", "eco_score": 78, "savings": "10%", "location": "Karachi"},
        {"name": "Ayesha Siddiqui", "eco_score": 75, "savings": "8%", "location": "Lahore"},
        {"name": "Hassan Ali", "eco_score": 71, "savings": "5%", "location": "Islamabad"},
        {"name": "Zainab Hussain", "eco_score": 68, "savings": "3%", "location": "Karachi"},
    ]
    return users

def get_comparison_stats(user_units, household_size=4):
    avg_usage = 300
    percentile = max(0, min(100, int((1 - (user_units - avg_usage) / avg_usage) * 50 + 50)))
    comparison = {
        "your_usage": user_units,
        "community_avg": avg_usage,
        "difference": user_units - avg_usage,
        "difference_percent": round((user_units - avg_usage) / avg_usage * 100, 1),
        "percentile": percentile,
        "similar_households_avg": avg_usage + random.randint(-20, 20),
        "efficient_households_avg": int(avg_usage * 0.7),
        "potential_savings": max(0, user_units - int(avg_usage * 0.7))
    }
    return comparison

def get_monthly_challenge():
    challenges = [
        {
            "title": "AC Efficiency Challenge",
            "description": "Keep your AC at 24°C or higher for the entire month",
            "reward": "+10 EcoScore points",
            "participants": 156
        },
        {
            "title": "Peak Hour Saver",
            "description": "Reduce usage during peak hours (6 PM - 11 PM) by 20%",
            "reward": "+15 EcoScore points",
            "participants": 203
        },
        {
            "title": "Zero Standby Week",
            "description": "Unplug all devices when not in use for 7 days",
            "reward": "+8 EcoScore points",
            "participants": 89
        }
    ]
    return random.choice(challenges)

def save_bill_image(uploaded_file):
    if not os.path.exists(BILLS_FOLDER):
        os.makedirs(BILLS_FOLDER)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = uploaded_file.name.split('.')[-1]
    filename = f"bill_{timestamp}.{file_extension}"
    filepath = os.path.join(BILLS_FOLDER, filename)
    
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return filename

def add_usage_entry(units, bill, bill_image_filename=None):
    data = load_user_data()
    
    data["current_month"] = {
        "units": units,
        "bill": bill,
        "date_uploaded": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "bill_image": bill_image_filename
    }
    
    data["eco_score"] = calculate_eco_score(units, data["user"]["household_size"])
    
    current_month = datetime.now().strftime("%b %Y")
    if not any(entry["month"] == current_month for entry in data["usage_history"]):
        data["usage_history"].append({
            "month": current_month,
            "units": units,
            "bill": bill,
            "bill_image": bill_image_filename
        })
    else:
        for entry in data["usage_history"]:
            if entry["month"] == current_month:
                entry["units"] = units
                entry["bill"] = bill
                entry["bill_image"] = bill_image_filename
                break
    
    save_user_data(data)
    return data

def get_bill_image_path(filename):
    if filename:
        return os.path.join(BILLS_FOLDER, filename)
    return None

def get_achievements(eco_score, total_months):
    achievements = []
    
    if eco_score >= 90:
        achievements.append({"icon": "🏆", "title": "Eco Champion", "desc": "EcoScore above 90"})
    if eco_score >= 80:
        achievements.append({"icon": "🌟", "title": "Energy Star", "desc": "EcoScore above 80"})
    if total_months >= 3:
        achievements.append({"icon": "📅", "title": "Consistent Tracker", "desc": "3+ months of data"})
    if total_months >= 6:
        achievements.append({"icon": "🎯", "title": "Long-term Saver", "desc": "6+ months of tracking"})
    
    return achievements
