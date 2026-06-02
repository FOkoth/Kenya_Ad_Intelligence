"""
Kenya Omni-Channel Ad Intelligence Platform
Professional Dashboard with Midnight Green Theme
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from streamlit_option_menu import option_menu

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
# CUSTOM CSS FOR MIDNIGHT GREEN THEME
# ============================================================================
st.markdown("""
<style>
    /* Midnight Green Color Palette */
    :root {
        --midnight-green: #004953;
        --midnight-light: #006B7A;
        --midnight-dark: #003540;
        --midnight-gold: #C6A43F;
        --midnight-gray: #F5F6F5;
        --midnight-white: #FFFFFF;
        --midnight-soft: #E8EDEE;
        --accent-success: #2E7D32;
        --accent-warning: #F57C00;
        --accent-danger: #C62828;
    }
    
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #004953 0%, #006B7A 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,73,83,0.15);
        border-bottom: 3px solid #C6A43F;
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.2rem;
        margin: 0;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.85);
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    
    /* Card styling */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border-top: 3px solid #004953;
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,73,83,0.12);
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 600;
        color: #004953;
        margin: 0.5rem 0;
        letter-spacing: -0.5px;
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 500;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1E293B;
        margin: 1.5rem 0 1rem 0;
        padding-left: 1rem;
        border-left: 3px solid #C6A43F;
    }
    
    /* Recommendation cards */
    .rec-card {
        background: linear-gradient(135deg, #004953 0%, #003540 100%);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.5rem 0;
        color: white;
        border-left: 3px solid #C6A43F;
    }
    
    .rec-card h4 {
        color: #C6A43F;
        margin: 0 0 0.5rem 0;
        font-size: 1rem;
        font-weight: 600;
    }
    
    .rec-card p {
        margin: 0.25rem 0;
        font-size: 0.85rem;
        opacity: 0.9;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 1.5rem;
        margin-top: 2rem;
        background: #F8FAFC;
        border-radius: 12px;
        font-size: 0.75rem;
        color: #64748B;
        border-top: 1px solid #E2E8F0;
    }
    
    /* Button styling */
    .stButton > button {
        background: #004953;
        color: white;
        border: none;
        padding: 0.6rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background: #006B7A;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,73,83,0.2);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F8FAFC 0%, #FFFFFF 100%);
        border-right: 1px solid #E2E8F0;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #1E293B;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: #F8FAFC;
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        color: #64748B;
    }
    
    .stTabs [aria-selected="true"] {
        background: #004953;
        color: white;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        background: white;
        border-color: #E2E8F0;
    }
    
    /* Number input */
    .stNumberInput > div > div > input {
        border-color: #E2E8F0;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #F8FAFC;
        border-radius: 8px;
        font-weight: 500;
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
        "🏖️ Tourism Kenya Campaign",
        "📱 Safaricom Digital", 
        "🏦 KCB Banking Solutions",
        "🏨 Mombasa Hospitality",
        "🏠 Nairobi Property Market",
        "🌾 Kisumu Agribusiness",
        "🛍️ Eldoret Retail Network",
        "🌊 Coast Beach Resorts",
        "🚗 Toyota Kenya Motors",
        "📚 Strathmore University"
    ]
    
    records = []
    for day in range(90):
        date = datetime.now() - timedelta(days=day)
        for campaign in campaigns:
            spend = np.random.uniform(2000, 20000)
            if "Tourism" in campaign or "Resorts" in campaign:
                roas_multiplier = np.random.uniform(2.5, 5.0)
            elif "Banking" in campaign or "Property" in campaign:
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
# SIDEBAR NAVIGATION
# ============================================================================
# Load data
df = generate_kenya_ad_data()

with st.sidebar:
    st.markdown("### 🎯 AdIntel Kenya")
    st.markdown("---")
    
    selected = option_menu(
        menu_title="Navigation",
        options=["Dashboard", "Media Directory", "Recommendations", "Analytics"],
        icons=["speedometer2", "tv", "robot", "graph-up"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#004953", "font-size": "18px"},
            "nav-link": {"font-size": "14px", "text-align": "left", "margin": "4px 0", "color": "#1E293B"},
            "nav-link-selected": {"background-color": "#004953", "color": "white"},
        }
    )
    
    st.markdown("---")
    st.markdown("### 📊 Filters")
    
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
        "Analysis Period (Days)",
        min_value=7,
        max_value=90,
        value=30,
        step=7
    )

# Filter data
filtered_df = df[df['campaign'].isin(selected_campaigns)]
filtered_df = filtered_df[filtered_df['platform'].isin(selected_platforms)]
recent_date = datetime.now() - timedelta(days=date_range)
filtered_df['date_dt'] = pd.to_datetime(filtered_df['date'])
filtered_df = filtered_df[filtered_df['date_dt'] >= recent_date]

# ============================================================================
# DASHBOARD PAGE
# ============================================================================
if selected == "Dashboard":
    # Hero Section
    st.markdown("""
    <div class="main-header">
        <h1>Ad Intelligence Kenya</h1>
        <p>Data-driven advertising analytics for TV, Radio & Digital Media</p>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    total_spend = filtered_df['spend_kes'].sum()
    total_revenue = filtered_df['revenue_kes'].sum()
    avg_roas = total_revenue / total_spend if total_spend > 0 else 0
    total_campaigns = len(filtered_df['campaign'].unique())
    
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
        roas_color = "#C62828" if avg_roas < 2 else "#2E7D32"
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
            <div class="metric-value">{total_campaigns}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts Section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">ROAS by Campaign</div>', unsafe_allow_html=True)
        campaign_roas = filtered_df.groupby('campaign')['roas'].mean().reset_index()
        campaign_roas = campaign_roas.sort_values('roas', ascending=True)
        
        fig = px.bar(campaign_roas, 
                     x='roas', 
                     y='campaign',
                     orientation='h',
                     color='roas',
                     color_continuous_scale='RdYlGn',
                     title="Return on Ad Spend by Campaign",
                     labels={'roas': 'ROAS (x)', 'campaign': ''},
                     text='roas')
        fig.add_vline(x=2.0, line_dash="dash", line_color="#C62828", 
                     annotation_text=" Target (2x)", annotation_position="top right")
        fig.update_layout(height=400, showlegend=False, plot_bgcolor='white')
        fig.update_traces(texttemplate='%{text:.2f}x', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<div class="section-header">Performance Trends</div>', unsafe_allow_html=True)
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
                                fillcolor='rgba(0,73,83,0.08)'))
        fig.add_trace(go.Scatter(x=daily['date'], y=daily['revenue_kes'], 
                                name='Revenue', 
                                line=dict(color='#C6A43F', width=2),
                                fill='tozeroy',
                                fillcolor='rgba(198,164,63,0.08)'))
        fig.update_layout(title="Daily Spend vs Revenue", 
                         xaxis_title="Date", 
                         yaxis_title="Amount (KES)",
                         height=400,
                         hovermode='x unified',
                         plot_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)
    
    # Second Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">Platform Performance</div>', unsafe_allow_html=True)
        platform_roas = filtered_df.groupby('platform')['roas'].mean().reset_index()
        
        fig = px.pie(platform_roas, 
                    values='roas', 
                    names='platform', 
                    title="ROAS by Platform",
                    hole=0.4,
                    color_discrete_sequence=['#004953', '#006B7A', '#C6A43F'])
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<div class="section-header">Weekly Performance</div>', unsafe_allow_html=True)
        filtered_df['week'] = pd.to_datetime(filtered_df['date']).dt.isocalendar().week
        weekly = filtered_df.groupby('week').agg({
            'spend_kes': 'sum',
            'revenue_kes': 'sum'
        }).reset_index()
        weekly['roas'] = weekly['revenue_kes'] / weekly['spend_kes']
        
        fig = px.line(weekly, x='week', y='roas', 
                     title="ROAS Trend by Week",
                     markers=True,
                     labels={'week': 'Week', 'roas': 'ROAS (x)'})
        fig.add_hline(y=2.0, line_dash="dash", line_color="#C62828", 
                     annotation_text="Target (2x)")
        fig.update_layout(height=400, plot_bgcolor='white')
        fig.update_traces(line=dict(color='#004953', width=2), marker=dict(color='#C6A43F', size=8))
        st.plotly_chart(fig, use_container_width=True)
    
    # AI Recommendations
    st.markdown('<div class="section-header">Intelligence Insights</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    if not campaign_roas.empty:
        best_campaign = campaign_roas.loc[campaign_roas['roas'].idxmax()]
        worst_campaign = campaign_roas.loc[campaign_roas['roas'].idxmin()]
    else:
        best_campaign = {'campaign': 'N/A', 'roas': 0}
        worst_campaign = {'campaign': 'N/A', 'roas': 0}
    
    if not platform_roas.empty:
        best_platform = platform_roas.loc[platform_roas['roas'].idxmax()]
    else:
        best_platform = {'platform': 'N/A', 'roas': 0}
    
    with col1:
        st.markdown(f"""
        <div class="rec-card">
            <h4>🚀 High-Performance Campaign</h4>
            <p><strong>{best_campaign['campaign'][:35] if best_campaign['campaign'] != 'N/A' else 'No data'}</strong></p>
            <p>ROAS: {best_campaign['roas']:.2f}x</p>
            <p style="font-size:0.8rem; margin-top:0.5rem;">✓ Increase budget allocation</p>
            <p style="font-size:0.8rem;">✓ Expand to similar audience segments</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="rec-card">
            <h4>⚠️ Underperforming Asset</h4>
            <p><strong>{worst_campaign['campaign'][:35] if worst_campaign['campaign'] != 'N/A' else 'No data'}</strong></p>
            <p>ROAS: {worst_campaign['roas']:.2f}x</p>
            <p style="font-size:0.8rem; margin-top:0.5rem;">✓ Reduce spend or pause</p>
            <p style="font-size:0.8rem;">✓ Review creative & targeting</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="rec-card">
            <h4>📱 Platform Optimization</h4>
            <p><strong>{best_platform['platform'] if best_platform['platform'] != 'N/A' else 'No data'}</strong></p>
            <p>ROAS: {best_platform['roas']:.2f}x</p>
            <p style="font-size:0.8rem; margin-top:0.5rem;">✓ Shift budget to top platform</p>
            <p style="font-size:0.8rem;">✓ Test new creative formats</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# MEDIA DIRECTORY PAGE
# ============================================================================
elif selected == "Media Directory":
    st.markdown("""
    <div class="main-header">
        <h1>Media Directory</h1>
        <p>Complete guide to TV and Radio stations across Kenya</p>
    </div>
    """, unsafe_allow_html=True)
    
    media = get_kenyan_media()
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_region = st.selectbox("Select Region", list(media.keys()))
    
    with col2:
        selected_media_type = st.selectbox("Media Type", ["Both", "TV", "Radio"])
    
    if selected_region:
        region_media = media[selected_region]
        
        if selected_media_type in ["Both", "TV"] and "TV" in region_media:
            st.markdown(f"#### 📺 Television Stations in {selected_region}")
            
            for tv in region_media["TV"]:
                with st.expander(f"{tv['name']}"):
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Audience Reach", tv['reach'])
                    with col_b:
                        st.metric("Format", tv['format'])
                    with col_c:
                        tier_icon = "🔴" if tv['price_tier'] == "Premium" else "🟡" if tv['price_tier'] == "Standard" else "🟢"
                        st.metric("Price Tier", f"{tier_icon} {tv['price_tier']}")
                    st.write(f"**Language:** {tv['language']}")
        
        if selected_media_type in ["Both", "Radio"] and "Radio" in region_media:
            st.markdown(f"#### 📻 Radio Stations in {selected_region}")
            
            for radio in region_media["Radio"]:
                with st.expander(f"{radio['name']}"):
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Audience Reach", radio['reach'])
                    with col_b:
                        st.metric("Format", radio['format'])
                    with col_c:
                        tier_icon = "🔴" if radio['price_tier'] == "Premium" else "🟡" if radio['price_tier'] == "Standard" else "🟢"
                        st.metric("Price Tier", f"{tier_icon} {radio['price_tier']}")
                    st.write(f"**Language:** {radio['language']}")

# ============================================================================
# RECOMMENDATIONS PAGE
# ============================================================================
elif selected == "Recommendations":
    st.markdown("""
    <div class="main-header">
        <h1>Campaign Intelligence</h1>
        <p>AI-powered media recommendations for your campaign</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        product_type = st.selectbox("Industry Sector", 
                                   ["Tourism & Hospitality", "Financial Services", "Agriculture", 
                                    "Retail & E-commerce", "Real Estate", "Telecommunications", 
                                    "Healthcare", "Education", "Automotive"])
    
    with col2:
        budget = st.number_input("Campaign Budget (KES)", min_value=50000, value=500000, step=50000)
    
    with col3:
        target_audience = st.selectbox("Target Demographic",
                                      ["Mass Market", "Youth (18-35)", "Professionals (25-45)",
                                       "Rural Population", "Urban Consumers", "Affluent Segment"])
    
    if st.button("Generate Intelligence Report", use_container_width=True):
        st.markdown("---")
        st.markdown("### 📋 Media Strategy Report")
        
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
            st.markdown("#### 🎯 Target Markets")
            for r in regions:
                st.markdown(f"📍 **{r}**")
            
            st.markdown("#### 📺 Primary TV Partner")
            st.markdown(f"**{primary_tv}**")
            st.markdown(f"**Media Mix:** 60% TV, 40% Radio")
        
        with col2:
            st.markdown("#### 📻 Primary Radio Partner")
            st.markdown(f"**{primary_radio}**")
            st.markdown(f"**Expected ROAS:** {expected_roas}")
        
        st.markdown("---")
        st.markdown("### 📧 Station Outreach Template")
        
        email = f"""
**Subject:** Media Partnership Request - {product_type} Campaign

Dear Station Sales Team,

We are developing a {product_type} advertising campaign with a budget of KES {budget:,.0f}.

**Campaign Parameters:**
- Target Markets: {', '.join(regions)}
- Target Audience: {target_audience}
- Campaign Duration: 4 weeks (initial)

Based on our media intelligence analysis, your station aligns with our targeting requirements.

**Information Request:**
1. Current rate card (30-second spots)
2. Inventory availability
3. Audience demographic profile

We look forward to discussing this opportunity.

Best regards,
Ad Intelligence Kenya
"""
        st.code(email, language="markdown")

# ============================================================================
# ANALYTICS PAGE
# ============================================================================
elif selected == "Analytics":
    st.markdown("""
    <div class="main-header">
        <h1>Analytics Hub</h1>
        <p>Deep dive into campaign performance metrics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Export Data (CSV)",
        data=csv,
        file_name=f"campaign_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ROAS Distribution")
        if not filtered_df.empty:
            fig = px.histogram(filtered_df, x='roas', nbins=30,
                              title="Campaign ROAS Distribution",
                              labels={'roas': 'ROAS (x)'},
                              color_discrete_sequence=['#004953'])
            fig.add_vline(x=2.0, line_dash="dash", line_color="#C62828")
            fig.update_layout(height=350, plot_bgcolor='white')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected filters.")
    
    with col2:
        st.markdown("#### Top Performers")
        if not filtered_df.empty:
            top5 = filtered_df.groupby('campaign')['roas'].mean().nlargest(5).reset_index()
            fig = px.bar(top5, x='roas', y='campaign', orientation='h',
                        title="Top 5 Campaigns by ROAS",
                        labels={'roas': 'ROAS (x)', 'campaign': ''},
                        color='roas',
                        color_continuous_scale='Greens')
            fig.update_layout(height=350, plot_bgcolor='white')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected filters.")
    
    st.markdown("#### Platform Summary")
    if not filtered_df.empty:
        platform_stats = filtered_df.groupby('platform').agg({
            'spend_kes': ['sum', 'mean'],
            'revenue_kes': ['sum', 'mean'],
            'roas': ['mean', 'min', 'max']
        }).round(2)
        
        st.dataframe(platform_stats, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("""
<div class="footer">
    <p>Ad Intelligence Kenya | Data-driven advertising analytics</p>
    <p style="font-size: 0.7rem;">© 2024 All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)
