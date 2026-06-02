"""
Ad Intelligence Kenya - Complete Platform with Smart Recommendations
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from datetime import datetime, timedelta
import random

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Ad Intelligence Kenya",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# DATABASE SETUP (Auto-runs on first load)
# ============================================================================
def init_database():
    """Initialize database with all tables"""
    
    conn = sqlite3.connect('ad_intelligence.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'client',
        company_id INTEGER,
        created_date TEXT
    )
    ''')
    
    # Companies table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS companies (
        company_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT UNIQUE NOT NULL,
        industry TEXT,
        email TEXT,
        phone TEXT,
        created_date TEXT,
        status TEXT DEFAULT 'active'
    )
    ''')
    
    # Campaigns table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS campaigns (
        campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        campaign_name TEXT,
        platform TEXT,
        spend_kes REAL,
        revenue_kes REAL,
        roas REAL,
        date TEXT,
        FOREIGN KEY (company_id) REFERENCES companies (company_id)
    )
    ''')
    
    # Media logs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS media_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        campaign_id INTEGER,
        station_name TEXT,
        media_type TEXT,
        spot_time TEXT,
        duration_seconds INTEGER,
        cost_kes REAL,
        estimated_reach INTEGER,
        log_date TEXT,
        FOREIGN KEY (company_id) REFERENCES companies (company_id)
    )
    ''')
    
    # Products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        product_name TEXT,
        category TEXT,
        target_audience TEXT,
        created_date TEXT,
        FOREIGN KEY (company_id) REFERENCES companies (company_id)
    )
    ''')
    
    # Recommendations history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recommendations (
        rec_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        campaign_goal TEXT,
        budget_kes REAL,
        duration_days INTEGER,
        target_audience TEXT,
        recommended_stations TEXT,
        estimated_roas REAL,
        created_date TEXT,
        FOREIGN KEY (company_id) REFERENCES companies (company_id)
    )
    ''')
    
    # Check if default users exist
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Admin user
        cursor.execute('''
        INSERT INTO users (username, password, role, company_id, created_date)
        VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin123', 'admin', None, datetime.now().isoformat()))
        
        # Sample companies
        companies = [
            ('Safaricom', 'Telecommunications', 'advertising@safaricom.com', '+254700000000'),
            ('KCB Bank', 'Financial Services', 'marketing@kcb.co.ke', '+254711000000'),
            ('Tourism Kenya', 'Tourism', 'info@tourism.go.ke', '+254730000000'),
            ('Toyota Kenya', 'Automotive', 'marketing@toyota.co.ke', '+254721000000'),
        ]
        
        for company in companies:
            cursor.execute('''
            INSERT INTO companies (company_name, industry, email, phone, created_date, status)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (company[0], company[1], company[2], company[3], datetime.now().isoformat(), 'active'))
            
            company_id = cursor.lastrowid
            username = company[0].lower().replace(' ', '')
            
            cursor.execute('''
            INSERT INTO users (username, password, role, company_id, created_date)
            VALUES (?, ?, ?, ?, ?)
            ''', (username, 'client123', 'client', company_id, datetime.now().isoformat()))
            
            # Generate sample campaign data
            for day in range(30):
                date = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d')
                spend = random.uniform(5000, 50000)
                revenue = spend * random.uniform(0.5, 4.0)
                cursor.execute('''
                INSERT INTO campaigns (company_id, campaign_name, platform, spend_kes, revenue_kes, roas, date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (company_id, f"{company[0]} Campaign", random.choice(['Meta', 'Google', 'TikTok']), 
                      spend, revenue, revenue/spend, date))
    
    conn.commit()
    conn.close()
    return True

# Run database initialization
init_database()

# ============================================================================
# CUSTOM CSS
# ============================================================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #004953 0%, #006B7A 100%);
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .main-header h1 { color: white; margin: 0; font-size: 1.75rem; }
    .main-header p { color: rgba(255,255,255,0.85); margin: 0.25rem 0 0 0; }
    
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border-left: 3px solid #C6A43F;
        text-align: center;
    }
    .metric-value { font-size: 1.5rem; font-weight: 700; color: #004953; }
    .metric-label { font-size: 0.7rem; color: #64748B; text-transform: uppercase; }
    
    .section-card {
        background: white;
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1.25rem;
        border: 1px solid #E2E8F0;
    }
    .section-title {
        font-size: 1rem;
        font-weight: 600;
        color: #1E293B;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #C6A43F;
        display: inline-block;
    }
    
    .rec-card {
        background: linear-gradient(135deg, #004953 0%, #003540 100%);
        border-radius: 12px;
        padding: 1rem;
        color: white;
        margin-bottom: 0.5rem;
    }
    .rec-card h4 { color: #C6A43F; margin: 0 0 0.5rem 0; font-size: 0.9rem; }
    .rec-card p { margin: 0.25rem 0; font-size: 0.8rem; }
    
    .success-card {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        border-radius: 12px;
        padding: 1rem;
        color: white;
    }
    
    .footer {
        text-align: center;
        padding: 1rem;
        margin-top: 1.5rem;
        background: #F8FAFC;
        border-radius: 12px;
        font-size: 0.7rem;
        color: #64748B;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
        background: #F1F5F9;
        padding: 0.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1.25rem;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        background: #004953;
        color: white;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .recommendation-badge {
        background: #C6A43F;
        color: #004953;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATABASE HELPER FUNCTIONS
# ============================================================================
def get_company_data(company_id):
    """Get campaign data for a specific company"""
    conn = sqlite3.connect('ad_intelligence.db')
    df = pd.read_sql_query('''
        SELECT * FROM campaigns 
        WHERE company_id = ? 
        ORDER BY date DESC
    ''', conn, params=(company_id,))
    conn.close()
    return df

def get_all_companies():
    """Get all active companies"""
    conn = sqlite3.connect('ad_intelligence.db')
    df = pd.read_sql_query("SELECT company_id, company_name, industry FROM companies WHERE status = 'active'", conn)
    conn.close()
    return df

def get_company_logs(company_id):
    """Get media logs for a specific company"""
    conn = sqlite3.connect('ad_intelligence.db')
    df = pd.read_sql_query('''
        SELECT * FROM media_logs 
        WHERE company_id = ? 
        ORDER BY log_date DESC
    ''', conn, params=(company_id,))
    conn.close()
    return df

def add_media_log(company_id, station_name, media_type, spot_time, duration, cost, reach):
    """Add a new media log entry"""
    conn = sqlite3.connect('ad_intelligence.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO media_logs (company_id, station_name, media_type, spot_time, duration_seconds, cost_kes, estimated_reach, log_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (company_id, station_name, media_type, spot_time, duration, cost, reach, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return True

def save_recommendation(company_id, campaign_goal, budget, duration, audience, stations, estimated_roas):
    """Save recommendation for future reference"""
    conn = sqlite3.connect('ad_intelligence.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO recommendations (company_id, campaign_goal, budget_kes, duration_days, target_audience, recommended_stations, estimated_roas, created_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (company_id, campaign_goal, budget, duration, audience, stations, estimated_roas, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return True

# ============================================================================
# SMART RECOMMENDATION ENGINE
# ============================================================================
class MediaRecommendationEngine:
    """Intelligent station recommendation engine"""
    
    def __init__(self):
        # Station database with detailed profiles
        self.stations = {
            "TV": {
                "Citizen TV": {
                    "region": "National",
                    "reach": 5000000,
                    "cost_per_spot": 250000,
                    "primary_audience": ["Mass Market", "Families", "General"],
                    "age_group": "25-55",
                    "income_level": "Middle to High",
                    "best_for": ["Brand Awareness", "Mass Market Products", "Telecom", "Banking"],
                    "language": ["English", "Swahili"],
                    "price_tier": "Premium",
                    "peak_times": ["19:30-21:00", "20:00-20:30"]
                },
                "KTN": {
                    "region": "National",
                    "reach": 3000000,
                    "cost_per_spot": 200000,
                    "primary_audience": ["Professionals", "News Viewers", "Urban"],
                    "age_group": "30-50",
                    "income_level": "High",
                    "best_for": ["News", "Corporate", "Financial Services", "Luxury Goods"],
                    "language": ["English"],
                    "price_tier": "Premium",
                    "peak_times": ["19:00-20:00", "21:00-22:00"]
                },
                "NTV": {
                    "region": "National",
                    "reach": 2800000,
                    "cost_per_spot": 220000,
                    "primary_audience": ["General", "Young Adults", "Urban"],
                    "age_group": "20-45",
                    "income_level": "Middle",
                    "best_for": ["Entertainment", "Retail", "Youth Products"],
                    "language": ["English"],
                    "price_tier": "Premium",
                    "peak_times": ["19:00-20:00", "20:00-21:00"]
                },
                "KBC": {
                    "region": "National",
                    "reach": 2000000,
                    "cost_per_spot": 150000,
                    "primary_audience": ["Mass Market", "Rural", "Older Adults"],
                    "age_group": "35-65",
                    "income_level": "Low to Middle",
                    "best_for": ["Government", "Public Service", "Agriculture", "Mass Market"],
                    "language": ["Swahili", "English"],
                    "price_tier": "Standard",
                    "peak_times": ["19:00-20:00", "20:00-21:00"]
                }
            },
            "Radio": {
                "Citizen Radio": {
                    "region": "National",
                    "reach": 2500000,
                    "cost_per_spot": 90000,
                    "primary_audience": ["General", "Talk Radio Listeners", "Urban"],
                    "age_group": "25-50",
                    "income_level": "Middle",
                    "best_for": ["Talk Shows", "News", "Consumer Goods"],
                    "language": ["English", "Swahili"],
                    "price_tier": "Premium",
                    "peak_times": ["06:00-09:00", "16:00-19:00"]
                },
                "Radio Jambo": {
                    "region": "National",
                    "reach": 2000000,
                    "cost_per_spot": 75000,
                    "primary_audience": ["Youth", "Entertainment Seekers", "Urban"],
                    "age_group": "18-35",
                    "income_level": "Low to Middle",
                    "best_for": ["Youth Products", "Music", "Entertainment", "Retail"],
                    "language": ["Swahili"],
                    "price_tier": "Standard",
                    "peak_times": ["07:00-10:00", "16:00-19:00"]
                },
                "Classic 105": {
                    "region": "National",
                    "reach": 1500000,
                    "cost_per_spot": 80000,
                    "primary_audience": ["Professionals", "Adults", "Urban Elite"],
                    "age_group": "30-50",
                    "income_level": "High",
                    "best_for": ["Corporate", "Luxury", "Financial Services", "Automotive"],
                    "language": ["English"],
                    "price_tier": "Premium",
                    "peak_times": ["07:00-09:00", "17:00-19:00"]
                },
                "Baraka FM": {
                    "region": "Coast",
                    "reach": 600000,
                    "cost_per_spot": 40000,
                    "primary_audience": ["Religious", "Coastal Residents"],
                    "age_group": "25-60",
                    "income_level": "Low to Middle",
                    "best_for": ["Religious Products", "Local Services", "Tourism"],
                    "language": ["Swahili"],
                    "price_tier": "Economy",
                    "peak_times": ["05:00-08:00", "18:00-20:00"]
                },
                "Ramogi FM": {
                    "region": "Western",
                    "reach": 850000,
                    "cost_per_spot": 35000,
                    "primary_audience": ["Luo Community", "Vernacular Listeners"],
                    "age_group": "25-55",
                    "income_level": "Low to Middle",
                    "best_for": ["Agriculture", "Local Products", "Community News"],
                    "language": ["Luo"],
                    "price_tier": "Economy",
                    "peak_times": ["06:00-09:00", "18:00-20:00"]
                },
                "Inooro FM": {
                    "region": "Central",
                    "reach": 1200000,
                    "cost_per_spot": 45000,
                    "primary_audience": ["Kikuyu Community", "Vernacular Listeners"],
                    "age_group": "25-55",
                    "income_level": "Middle",
                    "best_for": ["Agriculture", "Real Estate", "Local Business"],
                    "language": ["Kikuyu"],
                    "price_tier": "Standard",
                    "peak_times": ["06:00-09:00", "17:00-20:00"]
                }
            }
        }
        
        # Audience-to-station matching weights
        self.audience_weights = {
            "Mass Market": {"Citizen TV": 0.9, "KBC": 0.8, "Citizen Radio": 0.7},
            "Youth (18-35)": {"Radio Jambo": 0.9, "NTV": 0.7, "Citizen TV": 0.6},
            "Professionals (25-45)": {"KTN": 0.9, "Classic 105": 0.9, "Citizen TV": 0.7},
            "Rural Population": {"KBC": 0.8, "Ramogi FM": 0.7, "Inooro FM": 0.7},
            "Urban Consumers": {"Citizen TV": 0.8, "NTV": 0.8, "Classic 105": 0.7},
            "Affluent Segment": {"KTN": 0.9, "Classic 105": 0.9, "Citizen TV": 0.7}
        }
    
    def recommend_stations(self, campaign_goal, budget, duration_days, target_audience, region="National"):
        """Generate station recommendations based on all inputs"""
        
        recommendations = []
        available_budget = budget
        
        # Calculate total available spots based on budget
        for media_type in ["TV", "Radio"]:
            for station_name, station in self.stations[media_type].items():
                # Skip if region doesn't match
                if region != "National" and station["region"] != region and station["region"] != "National":
                    continue
                
                # Calculate match score
                score = 0
                
                # Goal matching
                if campaign_goal in station["best_for"]:
                    score += 30
                elif any(goal in station["best_for"] for goal in ["Brand Awareness", "Mass Market"]):
                    score += 15
                
                # Audience matching
                if target_audience in station["primary_audience"]:
                    score += 30
                elif target_audience in self.audience_weights and station_name in self.audience_weights[target_audience]:
                    score += self.audience_weights[target_audience][station_name] * 30
                
                # Budget matching
                if station["price_tier"] == "Economy" and available_budget < 300000:
                    score += 20
                elif station["price_tier"] == "Standard" and 200000 <= available_budget <= 600000:
                    score += 20
                elif station["price_tier"] == "Premium" and available_budget > 500000:
                    score += 20
                
                # Duration bonus - longer campaigns get better recommendations
                if duration_days > 14:
                    score += 10
                
                if score > 20:  # Only include relevant stations
                    # Calculate how many spots the budget allows
                    cost_per_spot = station["cost_per_spot"]
                    max_spots = int(available_budget / cost_per_spot) if cost_per_spot > 0 else 0
                    
                    recommendations.append({
                        "station_name": station_name,
                        "media_type": media_type,
                        "reach": station["reach"],
                        "cost_per_spot": cost_per_spot,
                        "recommended_spots": min(max_spots, 7 if duration_days <= 7 else 14),
                        "primary_audience": station["primary_audience"],
                        "best_for": station["best_for"],
                        "score": score,
                        "peak_times": station["peak_times"],
                        "price_tier": station["price_tier"]
                    })
        
        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:5]
    
    def calculate_estimated_roas(self, recommendations, budget, industry):
        """Estimate potential ROAS based on recommendations"""
        
        base_roas = 1.5  # Conservative baseline
        
        # Industry multipliers
        industry_multipliers = {
            "Telecommunications": 1.3,
            "Financial Services": 1.2,
            "Tourism": 1.4,
            "Automotive": 1.1,
            "Retail": 1.0,
            "Agriculture": 1.2
        }
        
        industry_mult = industry_multipliers.get(industry, 1.0)
        
        # Recommendation quality multiplier
        avg_score = sum(r["score"] for r in recommendations) / len(recommendations) if recommendations else 50
        quality_mult = 0.5 + (avg_score / 100)
        
        estimated_roas = base_roas * industry_mult * quality_mult
        
        # Budget efficiency
        if budget > 1000000:
            estimated_roas *= 1.1
        elif budget < 200000:
            estimated_roas *= 0.9
        
        return round(estimated_roas, 2)

# ============================================================================
# KENYAN MEDIA DIRECTORY
# ============================================================================
def get_kenyan_media():
    return {
        "Nairobi Metropolitan": {
            "TV": [
                {"name": "Citizen TV", "reach": "5,000,000", "format": "General", "price_tier": "Premium"},
                {"name": "KTN", "reach": "3,000,000", "format": "News", "price_tier": "Premium"},
                {"name": "NTV", "reach": "2,800,000", "format": "News/Entertainment", "price_tier": "Premium"},
                {"name": "KBC", "reach": "2,000,000", "format": "Public", "price_tier": "Standard"},
            ],
            "Radio": [
                {"name": "Citizen Radio", "reach": "2,500,000", "format": "News/Talk", "price_tier": "Premium"},
                {"name": "Radio Jambo", "reach": "2,000,000", "format": "Entertainment", "price_tier": "Standard"},
                {"name": "Classic 105", "reach": "1,500,000", "format": "Adult Contemporary", "price_tier": "Premium"},
            ]
        },
        "Coast Region": {
            "Radio": [
                {"name": "Baraka FM", "reach": "600,000", "format": "Religious/Talk", "price_tier": "Economy"},
                {"name": "Milele FM", "reach": "450,000", "format": "Entertainment", "price_tier": "Economy"},
            ]
        },
        "Western Region": {
            "Radio": [
                {"name": "Ramogi FM", "reach": "850,000", "format": "Vernacular", "price_tier": "Economy"},
                {"name": "Lake Victoria FM", "reach": "700,000", "format": "Vernacular", "price_tier": "Economy"},
            ]
        },
        "Central Region": {
            "Radio": [
                {"name": "Inooro FM", "reach": "1,200,000", "format": "Vernacular", "price_tier": "Standard"},
                {"name": "Kameme FM", "reach": "1,000,000", "format": "Vernacular", "price_tier": "Standard"},
            ]
        }
    }

# ============================================================================
# LOGIN SYSTEM
# ============================================================================
def check_login(username, password):
    conn = sqlite3.connect('ad_intelligence.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, role, company_id FROM users WHERE username = ? AND password = ?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result

def show_login():
    st.markdown("""
    <div class="main-header">
        <h1>Ad Intelligence Kenya</h1>
        <p>Data-driven advertising analytics platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", use_container_width=True):
            user = check_login(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.session_state.username = user[1]
                st.session_state.role = user[2]
                st.session_state.company_id = user[3]
                st.rerun()
            else:
                st.error("Invalid username or password")
        
        st.markdown("---")
        st.caption("Demo Accounts:")
        st.caption("Admin: username='admin', password='admin123'")
        st.caption("Client: username='safaricom', password='client123'")

# ============================================================================
# ADMIN DASHBOARD
# ============================================================================
def show_admin_dashboard():
    st.markdown("""
    <div class="main-header">
        <h1>Admin Dashboard</h1>
        <p>System-wide advertising intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    
    companies = get_all_companies()
    
    selected_company = st.selectbox("Select Company", ["All Companies"] + companies['company_name'].tolist())
    
    if selected_company != "All Companies":
        company_id = companies[companies['company_name'] == selected_company]['company_id'].values[0]
        df = get_company_data(company_id)
        company_name = selected_company
    else:
        all_data = []
        for _, company in companies.iterrows():
            company_df = get_company_data(company['company_id'])
            company_df['company_name'] = company['company_name']
            all_data.append(company_df)
        df = pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
        company_name = "All Companies"
    
    if not df.empty:
        total_spend = df['spend_kes'].sum()
        total_revenue = df['revenue_kes'].sum()
        avg_roas = total_revenue / total_spend if total_spend > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">💰 Total Spend</div><div class="metric-value">KES {total_spend:,.0f}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><div class="metric-label">💵 Total Revenue</div><div class="metric-value">KES {total_revenue:,.0f}</div></div>', unsafe_allow_html=True)
        with col3:
            roas_color = "#EF4444" if avg_roas < 2 else "#10B981"
            st.markdown(f'<div class="metric-card"><div class="metric-label">📈 Avg ROAS</div><div class="metric-value" style="color:{roas_color};">{avg_roas:.2f}x</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card"><div class="metric-label">🏢 Company</div><div class="metric-value">{company_name}</div></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            campaign_roas = df.groupby('campaign_name')['roas'].mean().reset_index()
            campaign_roas = campaign_roas.sort_values('roas', ascending=True)
            fig = px.bar(campaign_roas, x='roas', y='campaign_name', orientation='h',
                        color='roas', color_continuous_scale='RdYlGn',
                        labels={'roas': 'ROAS (x)', 'campaign_name': ''})
            fig.add_vline(x=2.0, line_dash="dash", line_color="#EF4444")
            fig.update_layout(height=400, plot_bgcolor='white', showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            daily = df.groupby('date').agg({'spend_kes': 'sum', 'revenue_kes': 'sum'}).reset_index()
            daily['date'] = pd.to_datetime(daily['date'])
            daily = daily.sort_values('date')
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=daily['date'], y=daily['spend_kes'], name='Spend', line=dict(color='#004953', width=2)))
            fig.add_trace(go.Scatter(x=daily['date'], y=daily['revenue_kes'], name='Revenue', line=dict(color='#C6A43F', width=2)))
            fig.update_layout(height=400, plot_bgcolor='white')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No campaign data available")

# ============================================================================
# CLIENT PORTAL WITH SMART RECOMMENDATIONS
# ============================================================================
def show_client_portal():
    company_id = st.session_state.company_id
    
    conn = sqlite3.connect('ad_intelligence.db')
    cursor = conn.cursor()
    cursor.execute("SELECT company_name, industry FROM companies WHERE company_id = ?", (company_id,))
    result = cursor.fetchone()
    company_name = result[0]
    company_industry = result[1] if result[1] else "General"
    conn.close()
    
    st.markdown(f"""
    <div class="main-header">
        <h1>Welcome, {company_name}</h1>
        <p>Your personalized advertising intelligence dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    df = get_company_data(company_id)
    logs_df = get_company_logs(company_id)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Performance", "🎯 Smart Recommendations", "📺 TV/Radio Logs", "📈 Media Directory", "⚙️ Settings"])
    
    # ========================================================================
    # TAB 1: Performance Dashboard
    # ========================================================================
    with tab1:
        if not df.empty:
            total_spend = df['spend_kes'].sum()
            total_revenue = df['revenue_kes'].sum()
            avg_roas = total_revenue / total_spend if total_spend > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'<div class="metric-card"><div class="metric-label">💰 Total Spend</div><div class="metric-value">KES {total_spend:,.0f}</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="metric-card"><div class="metric-label">💵 Total Revenue</div><div class="metric-value">KES {total_revenue:,.0f}</div></div>', unsafe_allow_html=True)
            with col3:
                roas_color = "#EF4444" if avg_roas < 2 else "#10B981"
                st.markdown(f'<div class="metric-card"><div class="metric-label">📈 Your ROAS</div><div class="metric-value" style="color:{roas_color};">{avg_roas:.2f}x</div></div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                campaign_roas = df.groupby('campaign_name')['roas'].mean().reset_index()
                fig = px.bar(campaign_roas, x='roas', y='campaign_name', orientation='h',
                            color='roas', color_continuous_scale='RdYlGn')
                fig.add_vline(x=2.0, line_dash="dash", line_color="#EF4444")
                fig.update_layout(height=350, plot_bgcolor='white', showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                platform_roas = df.groupby('platform')['roas'].mean().reset_index()
                fig = px.pie(platform_roas, values='roas', names='platform', hole=0.4,
                            color_discrete_sequence=['#004953', '#006B7A', '#C6A43F'])
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No campaign data available")
    
    # ========================================================================
    # TAB 2: SMART RECOMMENDATIONS (Enhanced)
    # ========================================================================
    with tab2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### 🎯 AI-Powered Media Recommendation Engine")
        st.markdown("Get intelligent station recommendations based on your campaign parameters")
        
        # Recommendation Input Form
        st.markdown("##### 📋 Campaign Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            campaign_goal = st.selectbox(
                "Campaign Goal",
                ["Brand Awareness", "Lead Generation", "Sales", "Customer Retention", "Product Launch"],
                help="What is the primary objective of this campaign?"
            )
            
            budget = st.number_input(
                "Total Budget (KES)", 
                min_value=100000, 
                max_value=10000000, 
                value=500000, 
                step=50000,
                help="Your total campaign budget"
            )
            
            duration = st.select_slider(
                "Campaign Duration (Days)",
                options=[7, 14, 21, 30, 45, 60],
                value=14,
                help="How long will the campaign run?"
            )
        
        with col2:
            target_audience = st.selectbox(
                "Target Audience",
                ["Mass Market", "Youth (18-35)", "Professionals (25-45)", 
                 "Rural Population", "Urban Consumers", "Affluent Segment"],
                help="Who are you trying to reach?"
            )
            
            target_region = st.selectbox(
                "Target Region",
                ["National", "Nairobi Metropolitan", "Coast Region", "Western Region", "Central Region"],
                help="Which geographic area are you targeting?"
            )
            
            seasonality = st.selectbox(
                "Campaign Season",
                ["Regular", "Peak Season (Dec-Jan)", "Low Season", "Holiday Period"],
                help="Consider seasonal factors that affect advertising effectiveness"
            )
        
        # Industry-specific insights
        st.markdown("##### 💡 Industry Insights")
        
        industry_insights = {
            "Telecommunications": "📱 Telco ads perform best on Citizen TV and Radio Jambo. Peak viewership is 7-9 PM weekdays.",
            "Financial Services": "🏦 Banking ads see highest engagement on KTN and Classic 105. Professional audiences respond best.",
            "Tourism": "🏖️ Tourism campaigns work well on Citizen TV and Baraka FM. Coast region stations are ideal for local targeting.",
            "Automotive": "🚗 Auto ads perform well on Classic 105 and NTV. Weekend slots have higher conversion rates.",
            "Retail": "🛍️ Retail campaigns get best ROI on Radio Jambo and NTV. Evening slots drive immediate action.",
            "General": "📺 Mass market campaigns perform consistently across major stations. Consider frequency over reach."
        }
        
        insight = industry_insights.get(company_industry, industry_insights["General"])
        st.info(insight)
        
        if st.button("🔍 Generate Smart Recommendations", use_container_width=True):
            # Initialize recommendation engine
            engine = MediaRecommendationEngine()
            
            # Get recommendations
            recommendations = engine.recommend_stations(
                campaign_goal=campaign_goal,
                budget=budget,
                duration_days=duration,
                target_audience=target_audience,
                region=target_region
            )
            
            estimated_roas = engine.calculate_estimated_roas(recommendations, budget, company_industry)
            
            # Save recommendation
            station_names = ", ".join([r["station_name"] for r in recommendations[:3]])
            save_recommendation(company_id, campaign_goal, budget, duration, target_audience, station_names, estimated_roas)
            
            st.markdown("---")
            st.markdown("### 📊 Your Personalized Media Plan")
            
            # ROAS Prediction Card
            st.markdown(f"""
            <div class="success-card">
                <h4 style="margin:0 0 0.5rem 0;">📈 Predicted Campaign Performance</h4>
                <p style="font-size:1.5rem; margin:0;"><strong>Estimated ROAS: {estimated_roas}x</strong></p>
                <p style="margin:0; opacity:0.9;">Based on your {campaign_goal} campaign targeting {target_audience}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Display top 3 recommendations prominently
            st.markdown("### 🏆 Top Recommended Stations")
            
            for idx, rec in enumerate(recommendations[:3]):
                price_icon = "🟢" if rec["price_tier"] == "Economy" else "🟡" if rec["price_tier"] == "Standard" else "🔴"
                
                with st.container():
                    st.markdown(f"""
                    <div class="rec-card">
                        <h4>#{idx+1} {rec['station_name']} ({rec['media_type']}) {price_icon} {rec['price_tier']}</h4>
                        <p><strong>📊 Reach:</strong> {rec['reach']:,} | <strong>💰 Cost per spot:</strong> KES {rec['cost_per_spot']:,}</p>
                        <p><strong>🎯 Best For:</strong> {', '.join(rec['best_for'][:3])}</p>
                        <p><strong>👥 Primary Audience:</strong> {', '.join(rec['primary_audience'][:2])}</p>
                        <p><strong>⏰ Recommended Times:</strong> {', '.join(rec['peak_times'][:2])}</p>
                        <p><strong>📺 Recommended Spots:</strong> {rec['recommended_spots']} per day</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Budget calculation
                    total_cost = rec["cost_per_spot"] * rec["recommended_spots"] * duration
                    st.caption(f"💰 Estimated campaign cost on {rec['station_name']}: KES {total_cost:,.0f} for {duration} days")
            
            # Budget allocation recommendation
            st.markdown("---")
            st.markdown("### 💰 Recommended Budget Allocation")
            
            total_recommended_cost = sum(r["cost_per_spot"] * r["recommended_spots"] * duration for r in recommendations[:3])
            
            if total_recommended_cost > budget:
                st.warning(f"⚠️ Your budget (KES {budget:,.0f}) is lower than the recommended plan (KES {total_recommended_cost:,.0f}). Consider focusing on 1-2 stations.")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Option 1: Focus on Top Station**")
                    st.markdown(f"Run campaign on {recommendations[0]['station_name']} only")
                    st.markdown(f"Estimated cost: KES {recommendations[0]['cost_per_spot'] * recommendations[0]['recommended_spots'] * duration:,.0f}")
                with col2:
                    st.markdown("**Option 2: Reduce Frequency**")
                    st.markdown(f"Reduce spots from {recommendations[0]['recommended_spots']} to {max(2, recommendations[0]['recommended_spots']//2)} per day")
                    reduced_cost = recommendations[0]['cost_per_spot'] * max(2, recommendations[0]['recommended_spots']//2) * duration
                    st.markdown(f"Estimated cost: KES {reduced_cost:,.0f}")
            else:
                st.success(f"✅ Your budget of KES {budget:,.0f} is sufficient for the recommended {len(recommendations[:3])} stations")
                
                # Budget breakdown
                st.markdown("#### Budget Breakdown")
                breakdown_data = []
                for rec in recommendations[:3]:
                    rec_cost = rec["cost_per_spot"] * rec["recommended_spots"] * duration
                    breakdown_data.append({
                        "Station": rec["station_name"],
                        "Spots/Day": rec["recommended_spots"],
                        "Cost/Spot": f"KES {rec['cost_per_spot']:,}",
                        "Total Cost": f"KES {rec_cost:,.0f}",
                        "Percentage": f"{(rec_cost/budget)*100:.0f}%"
                    })
                
                st.dataframe(pd.DataFrame(breakdown_data), use_container_width=True, hide_index=True)
            
            # Implementation button
            st.markdown("---")
            if st.button("📺 Generate Media Logs from This Plan", use_container_width=True):
                for rec in recommendations[:2]:  # Generate for top 2 stations
                    for day in range(min(duration, 7)):  # Generate for first week
                        spot_time = (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d") + " 19:30:00"
                        add_media_log(
                            company_id, 
                            rec["station_name"], 
                            rec["media_type"], 
                            spot_time, 
                            30, 
                            rec["cost_per_spot"], 
                            rec["reach"]
                        )
                st.success(f"✅ Media logs generated for {len(recommendations[:2])} stations. Check the TV/Radio Logs tab.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # TAB 3: TV/Radio Logs
    # ========================================================================
    with tab3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### 📺 📻 Airtime Logs")
        
        if not logs_df.empty:
            total_spots = len(logs_df)
            total_cost = logs_df['cost_kes'].sum()
            total_reach = logs_df['estimated_reach'].sum()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Spots Aired", total_spots)
            with col2:
                st.metric("Total Cost", f"KES {total_cost:,.0f}")
            with col3:
                st.metric("Total Reach", f"{total_reach:,.0f}")
            
            station_summary = logs_df.groupby('station_name').agg({
                'cost_kes': 'sum', 'estimated_reach': 'sum', 'duration_seconds': 'count'
            }).reset_index()
            station_summary.columns = ['Station', 'Total Cost', 'Total Reach', 'Spots']
            st.dataframe(station_summary, use_container_width=True)
            
            # Display recent logs
            st.markdown("#### Recent Airtime Logs")
            display_df = logs_df[['station_name', 'media_type', 'spot_time', 'duration_seconds', 'cost_kes', 'estimated_reach']].head(10)
            display_df.columns = ['Station', 'Type', 'Time', 'Duration', 'Cost (KES)', 'Est. Reach']
            st.dataframe(display_df, use_container_width=True)
            
            csv = logs_df.to_csv(index=False)
            st.download_button("📥 Export All Logs", csv, f"media_logs_{datetime.now().strftime('%Y%m%d')}.csv")
        else:
            st.info("No airtime logs yet. Use the Smart Recommendations tab to generate your first media plan.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.expander("➕ Manually Add Airtime Log"):
            col1, col2 = st.columns(2)
            with col1:
                media = get_kenyan_media()
                all_stations = []
                for region in media.values():
                    if "TV" in region:
                        all_stations.extend([(s['name'], 'TV') for s in region["TV"]])
                    if "Radio" in region:
                        all_stations.extend([(s['name'], 'Radio') for s in region["Radio"]])
                
                station_names = [s[0] for s in all_stations]
                station = st.selectbox("Station", station_names)
                media_type = next((s[1] for s in all_stations if s[0] == station), "TV")
                spot_time = st.text_input("Time (YYYY-MM-DD HH:MM:SS)", datetime.now().strftime("%Y-%m-%d 19:30:00"))
            with col2:
                duration = st.number_input("Duration (sec)", 15, 60, 30)
                
                # Auto-populate cost based on station
                station_costs = {
                    'Citizen TV': 250000, 'KTN': 200000, 'NTV': 220000, 'KBC': 150000,
                    'Citizen Radio': 90000, 'Radio Jambo': 75000, 'Classic 105': 80000,
                    'Baraka FM': 40000, 'Milele FM': 35000, 'Ramogi FM': 35000,
                    'Inooro FM': 45000, 'Kameme FM': 40000
                }
                cost = st.number_input("Cost (KES)", 10000, 500000, station_costs.get(station, 50000))
                reach = st.number_input("Est. Reach", 10000, 5000000, 500000)
            
            if st.button("Add Log"):
                add_media_log(company_id, station, media_type, spot_time, duration, cost, reach)
                st.success("Log added!")
                st.rerun()
    
    # ========================================================================
    # TAB 4: Media Directory
    # ========================================================================
    with tab4:
        media = get_kenyan_media()
        selected_region = st.selectbox("Select Region", list(media.keys()))
        
        if selected_region:
            region_media = media[selected_region]
            if "TV" in region_media:
                st.markdown(f"#### 📺 TV Stations in {selected_region}")
                for tv in region_media["TV"]:
                    with st.expander(tv['name']):
                        st.write(f"**Reach:** {tv['reach']}")
                        st.write(f"**Format:** {tv['format']}")
                        tier_icon = "🔴" if tv['price_tier'] == "Premium" else "🟡" if tv['price_tier'] == "Standard" else "🟢"
                        st.write(f"**Price Tier:** {tier_icon} {tv['price_tier']}")
            
            if "Radio" in region_media:
                st.markdown(f"#### 📻 Radio Stations in {selected_region}")
                for radio in region_media["Radio"]:
                    with st.expander(radio['name']):
                        st.write(f"**Reach:** {radio['reach']}")
                        st.write(f"**Format:** {radio['format']}")
                        tier_icon = "🔴" if radio['price_tier'] == "Premium" else "🟡" if radio['price_tier'] == "Standard" else "🟢"
                        st.write(f"**Price Tier:** {tier_icon} {radio['price_tier']}")
    
    # ========================================================================
    # TAB 5: Settings
    # ========================================================================
    with tab5:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### ⚙️ Account Settings")
        
        st.markdown(f"**Company:** {company_name}")
        st.markdown(f"**Industry:** {company_industry}")
        
        st.markdown("---")
        st.markdown("#### 📊 Past Recommendations")
        
        conn = sqlite3.connect('ad_intelligence.db')
        past_recs = pd.read_sql_query('''
            SELECT created_date, campaign_goal, budget_kes, duration_days, target_audience, recommended_stations, estimated_roas
            FROM recommendations 
            WHERE company_id = ?
            ORDER BY created_date DESC
            LIMIT 5
        ''', conn, params=(company_id,))
        conn.close()
        
        if not past_recs.empty:
            past_recs.columns = ['Date', 'Goal', 'Budget', 'Duration', 'Audience', 'Stations', 'Est. ROAS']
            st.dataframe(past_recs, use_container_width=True, hide_index=True)
        else:
            st.info("No past recommendations. Generate your first media plan in the Smart Recommendations tab.")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# MAIN APP ROUTING
# ============================================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    if st.session_state.role == 'admin':
        show_admin_dashboard()
    else:
        show_client_portal()
    
    # Logout button in sidebar
    with st.sidebar:
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
else:
    show_login()

# Footer
st.markdown("""
<div class="footer">
    <p>Ad Intelligence Kenya | AI-Powered Media Recommendations</p>
</div>
""", unsafe_allow_html=True)
