"""
Kenya Omni-Channel Ad Intelligence Platform
Professional Dashboard with Tab Navigation - Midnight Green Theme
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

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
# CUSTOM CSS FOR PROFESSIONAL THEME
# ============================================================================
st.markdown("""
<style>
    /* Professional Color Palette */
    :root {
        --primary: #004953;
        --primary-light: #006B7A;
        --primary-dark: #003540;
        --accent: #C6A43F;
        --accent-light: #D4B85E;
        --text-dark: #1E293B;
        --text-medium: #475569;
        --text-light: #94A3B8;
        --bg-white: #FFFFFF;
        --bg-light: #F8FAFC;
        --bg-gray: #F1F5F9;
        --border: #E2E8F0;
        --success: #10B981;
        --warning: #F59E0B;
        --danger: #EF4444;
    }
    
    /* Reset and Base */
    .stApp {
        background-color: var(--bg-light);
    }
    
    /* Main container padding */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1400px;
    }
    
    /* Header styling */
    .app-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,73,83,0.1);
    }
    
    .app-header h1 {
        color: white;
        font-size: 1.75rem;
        margin: 0;
        font-weight: 600;
        letter-spacing: -0.3px;
    }
    
    .app-header p {
        color: rgba(255,255,255,0.85);
        font-size: 0.85rem;
        margin: 0.25rem 0 0 0;
    }
    
    /* Metric Cards */
    .metric-card {
        background: var(--bg-white);
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid var(--border);
        transition: all 0.2s;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--primary);
        margin: 0.25rem 0;
    }
    
    .metric-label {
        font-size: 0.7rem;
        color: var(--text-medium);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    
    /* Section Cards */
    .section-card {
        background: var(--bg-white);
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1.25rem;
        border: 1px solid var(--border);
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    
    .section-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-dark);
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--accent);
        display: inline-block;
    }
    
    /* Recommendation Cards */
    .rec-card {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        border-radius: 12px;
        padding: 1rem;
        color: white;
        height: 100%;
    }
    
    .rec-card h4 {
        color: var(--accent);
        margin: 0 0 0.5rem 0;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    .rec-card p {
        margin: 0.25rem 0;
        font-size: 0.8rem;
        opacity: 0.9;
    }
    
    /* Button styling */
    .stButton > button {
        background: var(--primary);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.25rem;
        font-weight: 500;
        font-size: 0.85rem;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background: var(--primary-light);
        transform: translateY(-1px);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: var(--bg-white);
        border-right: 1px solid var(--border);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: var(--text-dark);
    }
    
    /* Sidebar headers */
    .sidebar-header {
        font-size: 1rem;
        font-weight: 600;
        color: var(--primary);
        margin-bottom: 0.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--accent);
    }
    
    /* Tab styling - Clean and modern */
    .stTabs {
        gap: 0rem;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
        background: var(--bg-gray);
        padding: 0.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 0.5rem 1.25rem;
        font-weight: 500;
        font-size: 0.85rem;
        color: var(--text-medium);
        white-space: nowrap;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary);
        color: white;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: var(--bg-light);
        border-radius: 8px;
        font-weight: 500;
        font-size: 0.85rem;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 1rem;
        margin-top: 1.5rem;
        background: var(--bg-white);
        border-radius: 12px;
        font-size: 0.7rem;
        color: var(--text-light);
        border: 1px solid var(--border);
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .app-header h1 {
            font-size: 1.25rem;
        }
        .metric-value {
            font-size: 1.1rem;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 0.35rem 0.75rem;
            font-size: 0.75rem;
        }
    }
    
    /* Metric row responsive */
    @media (max-width: 640px) {
        .row-widget.stHorizontal {
            flex-wrap: wrap;
        }
    }
    
    /* Dataframe styling */
    .dataframe {
        font-size: 0.8rem;
    }
    
    /* Hide default streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: var(--bg-gray);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: var(--primary-light);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA GENERATION FUNCTIONS
# ============================================================================
@st.cache_data
def generate_kenya_ad_data():
    """Generate realistic Kenyan advertising data"""
    
    campaigns = [
        "🏖️ Tourism Kenya",
        "📱 Safaricom Digital", 
        "🏦 KCB Banking",
        "🏨 Mombasa Hotels",
        "🏠 Nairobi Real Estate",
        "🌾 Kisumu Agriculture",
        "🛍️ Eldoret Retail",
        "🌊 Coast Resorts",
        "🚗 Toyota Kenya",
        "📚 Strathmore"
    ]
    
    records = []
    for day in range(90):
        date = datetime.now() - timedelta(days=day)
        for campaign in campaigns:
            spend = np.random.uniform(2000, 20000)
            if "Tourism" in campaign or "Resorts" in campaign:
                roas_multiplier = np.random.uniform(2.5, 5.0)
            elif "Banking" in campaign or "Real Estate" in campaign:
                roas_multiplier = np.random.uniform(1.5, 3.0)
            elif "Safaricom" in campaign:
                roas_multiplier = np.random.uniform(2.0, 4.0)
            else:
                roas_multiplier = np.random.uniform(0.8, 2.5)
            
            revenue = spend * roas_multiplier
            records.append({
                'date': date.strftime('%Y-%m-%d'),
                'campaign': campaign,
                'platform': np.random.choice(['Meta', 'Google', 'TikTok']),
                'spend_kes': round(spend, 2),
                'revenue_kes': round(revenue, 2),
                'roas': round(revenue / spend, 2)
            })
    
    return pd.DataFrame(records)

@st.cache_data
def get_kenyan_media():
    """Kenyan TV and Radio stations by region"""
    
    return {
        "Nairobi Metropolitan": {
            "TV": [
                {"name": "Citizen TV", "reach": "5,000,000", "format": "General", "language": "English/Swahili", "price_tier": "Premium"},
                {"name": "KTN", "reach": "3,000,000", "format": "News", "language": "English", "price_tier": "Premium"},
                {"name": "NTV", "reach": "2,800,000", "format": "News/Entertainment", "language": "English", "price_tier": "Premium"},
                {"name": "KBC", "reach": "2,000,000", "format": "Public", "language": "Swahili/English", "price_tier": "Standard"},
                {"name": "TV47", "reach": "500,000", "format": "News", "language": "English", "price_tier": "Economy"}
            ],
            "Radio": [
                {"name": "Citizen Radio", "reach": "2,500,000", "format": "News/Talk", "language": "English/Swahili", "price_tier": "Premium"},
                {"name": "Radio Jambo", "reach": "2,000,000", "format": "Entertainment", "language": "Swahili", "price_tier": "Standard"},
                {"name": "Classic 105", "reach": "1,500,000", "format": "Adult Contemporary", "language": "English", "price_tier": "Premium"},
                {"name": "Kiss FM", "reach": "1,200,000", "format": "Top 40", "language": "English", "price_tier": "Standard"},
                {"name": "X FM", "reach": "800,000", "format": "Urban", "language": "English", "price_tier": "Standard"}
            ]
        },
        "Coast Region": {
            "Radio": [
                {"name": "Baraka FM", "reach": "600,000", "format": "Religious/Talk", "language": "Swahili", "price_tier": "Economy"},
                {"name": "Milele FM", "reach": "450,000", "format": "Entertainment", "language": "Swahili", "price_tier": "Economy"},
                {"name": "Pwani FM", "reach": "350,000", "format": "Regional", "language": "Swahili", "price_tier": "Economy"}
            ]
        },
        "Western Region": {
            "Radio": [
                {"name": "Lake Victoria FM", "reach": "700,000", "format": "Vernacular", "language": "Luo", "price_tier": "Economy"},
                {"name": "Ramogi FM", "reach": "850,000", "format": "Vernacular", "language": "Luo", "price_tier": "Economy"},
                {"name": "Pamoja FM", "reach": "400,000", "format": "Community", "language": "Luo/Swahili", "price_tier": "Economy"}
            ]
        },
        "Central Region": {
            "Radio": [
                {"name": "Inooro FM", "reach": "1,200,000", "format": "Vernacular", "language": "Kikuyu", "price_tier": "Standard"},
                {"name": "Kameme FM", "reach": "1,000,000", "format": "Vernacular", "language": "Kikuyu", "price_tier": "Standard"},
                {"name": "Coroo FM", "reach": "600,000", "format": "Vernacular", "language": "Kikuyu", "price_tier": "Economy"}
            ]
        }
    }

# ============================================================================
# SIDEBAR
# ============================================================================
# Load data
df = generate_kenya_ad_data()

with st.sidebar:
    st.markdown("### 🎯 AdIntel")
    st.markdown("#### Kenya")
    st.markdown("---")
    
    # Filters Section
    st.markdown('<p class="sidebar-header">📊 Filters</p>', unsafe_allow_html=True)
    
    all_campaigns = df['campaign'].unique().tolist()
    selected_campaigns = st.multiselect(
        "Campaigns",
        all_campaigns,
        default=all_campaigns[:4]
    )
    
    all_platforms = df['platform'].unique().tolist()
    selected_platforms = st.multiselect(
        "Platforms",
        all_platforms,
        default=all_platforms
    )
    
    date_range = st.slider(
        "Analysis Period",
        min_value=7,
        max_value=90,
        value=30,
        step=7,
        help="Number of days to analyze"
    )
    
    st.markdown("---")
    
    # Quick Stats
    st.markdown('<p class="sidebar-header">ℹ️ Quick Stats</p>', unsafe_allow_html=True)
    
    total_campaigns = len(df['campaign'].unique())
    total_platforms = len(df['platform'].unique())
    total_spend = df['spend_kes'].sum()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Campaigns", total_campaigns)
    with col2:
        st.metric("Platforms", total_platforms)
    
    st.caption(f"Total Ad Spend: KES {total_spend:,.0f}")
    
    st.markdown("---")
    st.caption("v1.0 | Data-driven insights")

# Filter data
filtered_df = df[df['campaign'].isin(selected_campaigns)]
filtered_df = filtered_df[filtered_df['platform'].isin(selected_platforms)]
recent_date = datetime.now() - timedelta(days=date_range)
filtered_df['date_dt'] = pd.to_datetime(filtered_df['date'])
filtered_df = filtered_df[filtered_df['date_dt'] >= recent_date]

# ============================================================================
# MAIN HEADER
# ============================================================================
st.markdown("""
<div class="app-header">
    <h1>Ad Intelligence Kenya</h1>
    <p>Data-driven advertising analytics for TV, Radio & Digital Media</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# KPI METRICS ROW (Visible on all tabs)
# ============================================================================
total_spend = filtered_df['spend_kes'].sum()
total_revenue = filtered_df['revenue_kes'].sum()
avg_roas = total_revenue / total_spend if total_spend > 0 else 0
total_campaigns_active = len(filtered_df['campaign'].unique())
avg_ctr = np.random.uniform(1.5, 3.5)  # Mock CTR for demonstration

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">💰 Total Ad Spend</div>
        <div class="metric-value">KES {total_spend:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">💵 Total Revenue</div>
        <div class="metric-value">KES {total_revenue:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    roas_color = "#EF4444" if avg_roas < 2 else "#10B981"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">📈 Average ROAS</div>
        <div class="metric-value" style="color:{roas_color};">{avg_roas:.2f}x</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🎯 Active Campaigns</div>
        <div class="metric-value">{total_campaigns_active}</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# TAB NAVIGATION
# ============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Performance Dashboard",
    "📺 Media Directory",
    "🎯 Campaign Intelligence",
    "📈 Analytics Hub"
])

# ============================================================================
# TAB 1: PERFORMANCE DASHBOARD
# ============================================================================
with tab1:
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">ROAS by Campaign</p>', unsafe_allow_html=True)
        
        if not filtered_df.empty:
            campaign_roas = filtered_df.groupby('campaign')['roas'].mean().reset_index()
            campaign_roas = campaign_roas.sort_values('roas', ascending=True)
            
            fig = px.bar(campaign_roas, 
                         x='roas', 
                         y='campaign',
                         orientation='h',
                         color='roas',
                         color_continuous_scale='RdYlGn',
                         labels={'roas': 'ROAS (x)', 'campaign': ''},
                         text='roas')
            fig.add_vline(x=2.0, line_dash="dash", line_color="#EF4444", 
                         annotation_text="Target (2x)", annotation_position="top right")
            fig.update_layout(height=350, showlegend=False, plot_bgcolor='white', margin=dict(l=0, r=0, t=30, b=0))
            fig.update_traces(texttemplate='%{text:.2f}x', textposition='outside')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No data available. Adjust your filters.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Performance Trends</p>', unsafe_allow_html=True)
        
        if not filtered_df.empty:
            daily = filtered_df.groupby('date').agg({
                'spend_kes': 'sum',
                'revenue_kes': 'sum'
            }).reset_index()
            daily['date'] = pd.to_datetime(daily['date'])
            daily = daily.sort_values('date')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=daily['date'], y=daily['spend_kes'], 
                                    name='Ad Spend', 
                                    line=dict(color='#004953', width=2),
                                    fill='tozeroy',
                                    fillcolor='rgba(0,73,83,0.05)'))
            fig.add_trace(go.Scatter(x=daily['date'], y=daily['revenue_kes'], 
                                    name='Revenue', 
                                    line=dict(color='#C6A43F', width=2),
                                    fill='tozeroy',
                                    fillcolor='rgba(198,164,63,0.05)'))
            fig.update_layout(height=350, 
                             xaxis_title="Date", 
                             yaxis_title="Amount (KES)",
                             hovermode='x unified',
                             plot_bgcolor='white',
                             margin=dict(l=0, r=0, t=30, b=0),
                             showlegend=True)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No data available. Adjust your filters.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Second Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Platform Performance</p>', unsafe_allow_html=True)
        
        if not filtered_df.empty:
            platform_roas = filtered_df.groupby('platform')['roas'].mean().reset_index()
            
            fig = px.pie(platform_roas, 
                        values='roas', 
                        names='platform', 
                        hole=0.4,
                        color_discrete_sequence=['#004953', '#006B7A', '#C6A43F'])
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=320, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No data available.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Weekly ROAS Trend</p>', unsafe_allow_html=True)
        
        if not filtered_df.empty:
            filtered_df['week'] = pd.to_datetime(filtered_df['date']).dt.isocalendar().week
            weekly = filtered_df.groupby('week').agg({
                'spend_kes': 'sum',
                'revenue_kes': 'sum'
            }).reset_index()
            weekly['roas'] = weekly['revenue_kes'] / weekly['spend_kes']
            
            fig = px.line(weekly, x='week', y='roas', 
                         markers=True,
                         labels={'week': 'Week', 'roas': 'ROAS (x)'})
            fig.add_hline(y=2.0, line_dash="dash", line_color="#EF4444", 
                         annotation_text="Target (2x)")
            fig.update_layout(height=320, plot_bgcolor='white', margin=dict(l=0, r=0, t=30, b=0))
            fig.update_traces(line=dict(color='#004953', width=2), marker=dict(color='#C6A43F', size=6))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No data available.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Intelligence Insights
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">💡 Intelligence Insights</p>', unsafe_allow_html=True)
    
    if not filtered_df.empty and not campaign_roas.empty:
        col1, col2, col3 = st.columns(3)
        
        best_campaign = campaign_roas.loc[campaign_roas['roas'].idxmax()]
        worst_campaign = campaign_roas.loc[campaign_roas['roas'].idxmin()]
        
        with col1:
            st.markdown(f"""
            <div class="rec-card">
                <h4>🚀 Top Performer</h4>
                <p><strong>{best_campaign['campaign'][:25]}</strong></p>
                <p>ROAS: {best_campaign['roas']:.2f}x</p>
                <p style="font-size:0.75rem; margin-top:0.5rem;">→ Increase budget allocation</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="rec-card">
                <h4>⚠️ Needs Attention</h4>
                <p><strong>{worst_campaign['campaign'][:25]}</strong></p>
                <p>ROAS: {worst_campaign['roas']:.2f}x</p>
                <p style="font-size:0.75rem; margin-top:0.5rem;">→ Review targeting & creative</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="rec-card">
                <h4>📱 Platform Insight</h4>
                <p><strong>{platform_roas.loc[platform_roas['roas'].idxmax(), 'platform']}</strong></p>
                <p>Best performing platform</p>
                <p style="font-size:0.75rem; margin-top:0.5rem;">→ Consider budget reallocation</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Run campaigns to see intelligence insights.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# TAB 2: MEDIA DIRECTORY
# ============================================================================
with tab2:
    media = get_kenyan_media()
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_region = st.selectbox("📍 Select Region", list(media.keys()), key="region_select")
    
    with col2:
        selected_media_type = st.selectbox("📡 Media Type", ["Both", "TV", "Radio"], key="media_select")
    
    if selected_region:
        region_media = media[selected_region]
        
        if selected_media_type in ["Both", "TV"] and "TV" in region_media:
            st.markdown(f"#### 📺 Television Stations in {selected_region}")
            
            cols = st.columns(2)
            for idx, tv in enumerate(region_media["TV"]):
                with cols[idx % 2]:
                    with st.expander(f"{tv['name']}"):
                        st.markdown(f"**Reach:** {tv['reach']} viewers")
                        st.markdown(f"**Format:** {tv['format']}")
                        st.markdown(f"**Language:** {tv['language']}")
                        tier_icon = "🔴" if tv['price_tier'] == "Premium" else "🟡" if tv['price_tier'] == "Standard" else "🟢"
                        st.markdown(f"**Price:** {tier_icon} {tv['price_tier']}")
        
        if selected_media_type in ["Both", "Radio"] and "Radio" in region_media:
            st.markdown(f"#### 📻 Radio Stations in {selected_region}")
            
            cols = st.columns(2)
            for idx, radio in enumerate(region_media["Radio"]):
                with cols[idx % 2]:
                    with st.expander(f"{radio['name']}"):
                        st.markdown(f"**Reach:** {radio['reach']} listeners")
                        st.markdown(f"**Format:** {radio['format']}")
                        st.markdown(f"**Language:** {radio['language']}")
                        tier_icon = "🔴" if radio['price_tier'] == "Premium" else "🟡" if radio['price_tier'] == "Standard" else "🟢"
                        st.markdown(f"**Price:** {tier_icon} {radio['price_tier']}")

# ============================================================================
# TAB 3: CAMPAIGN INTELLIGENCE
# ============================================================================
with tab3:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        product_type = st.selectbox("🏷️ Industry Sector", 
                                   ["Tourism & Hospitality", "Financial Services", "Agriculture", 
                                    "Retail & E-commerce", "Real Estate", "Telecommunications", 
                                    "Healthcare", "Education", "Automotive"])
    
    with col2:
        campaign_budget = st.number_input("💰 Campaign Budget (KES)", min_value=50000, value=500000, step=50000)
    
    with col3:
        target_audience = st.selectbox("👥 Target Demographic",
                                      ["Mass Market", "Youth (18-35)", "Professionals (25-45)",
                                       "Rural Population", "Urban Consumers", "Affluent Segment"])
    
    if st.button("Generate Intelligence Report", use_container_width=True):
        st.markdown("---")
        
        # Recommendation logic
        if "Tourism" in product_type:
            regions = ["Coast Region", "Nairobi Metropolitan"]
            primary_tv = "Citizen TV"
            primary_radio = "Baraka FM"
            expected_roas = "3.5x - 5.0x"
        elif "Financial" in product_type:
            regions = ["Nairobi Metropolitan"]
            primary_tv = "KTN"
            primary_radio = "Classic 105"
            expected_roas = "2.0x - 3.5x"
        elif "Agriculture" in product_type:
            regions = ["Western Region", "Central Region"]
            primary_tv = "Inooro TV"
            primary_radio = "Ramogi FM"
            expected_roas = "2.5x - 4.0x"
        else:
            regions = ["Nairobi Metropolitan", "Coast Region", "Western Region"]
            primary_tv = "NTV"
            primary_radio = "Radio Jambo"
            expected_roas = "1.8x - 2.8x"
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Recommended Markets")
            for r in regions:
                st.markdown(f"📍 **{r}**")
            
            st.markdown("#### 📺 Primary TV")
            st.markdown(f"**{primary_tv}**")
            st.markdown("**Media Mix:** 60% TV, 40% Radio")
        
        with col2:
            st.markdown("#### 📻 Primary Radio")
            st.markdown(f"**{primary_radio}**")
            st.markdown(f"**Expected ROAS:** {expected_roas}")
            st.markdown(f"**Budget Range:** KES {campaign_budget:,.0f}")
        
        st.markdown("---")
        st.markdown("#### 📧 Station Outreach Template")
        
        email = f"""Subject: Media Partnership - {product_type} Campaign (KES {campaign_budget:,.0f})

Dear Station Sales Team,

We are planning a {product_type} advertising campaign with a budget of KES {campaign_budget:,.0f}.

Campaign Details:
- Target Markets: {', '.join(regions)}
- Target Audience: {target_audience}
- Duration: 4 weeks initial

Please share:
1. Rate card (30-second spots)
2. Inventory availability
3. Audience demographics

Best regards,
Ad Intelligence Kenya"""
        
        st.code(email, language="markdown")

# ============================================================================
# TAB 4: ANALYTICS HUB
# ============================================================================
with tab4:
    # Download Section
    col1, col2 = st.columns([1, 3])
    with col1:
        if not filtered_df.empty:
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Export CSV",
                data=csv,
                file_name=f"ad_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">ROAS Distribution</p>', unsafe_allow_html=True)
        
        if not filtered_df.empty:
            fig = px.histogram(filtered_df, x='roas', nbins=30,
                              labels={'roas': 'ROAS (x)'},
                              color_discrete_sequence=['#004953'])
            fig.add_vline(x=2.0, line_dash="dash", line_color="#EF4444")
            fig.update_layout(height=300, plot_bgcolor='white', margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No data available.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Top Performers</p>', unsafe_allow_html=True)
        
        if not filtered_df.empty:
            top5 = filtered_df.groupby('campaign')['roas'].mean().nlargest(5).reset_index()
            fig = px.bar(top5, x='roas', y='campaign', orientation='h',
                        labels={'roas': 'ROAS (x)', 'campaign': ''},
                        color='roas',
                        color_continuous_scale='Greens')
            fig.update_layout(height=300, plot_bgcolor='white', margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No data available.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Platform Summary
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">Platform Performance Summary</p>', unsafe_allow_html=True)
    
    if not filtered_df.empty:
        platform
