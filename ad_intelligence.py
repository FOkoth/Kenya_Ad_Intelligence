"""
Kenya Omni-Channel Ad Intelligence Platform
Complete working dashboard for Kenyan advertisers
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Kenya Ad Intelligence",
    page_icon="🇰🇪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #006B3F;
        text-align: center;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="main-header">🇰🇪 Kenya Omni-Channel Ad Intelligence Platform</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Data-driven recommendations for TV, Radio & Digital Advertising</p>', unsafe_allow_html=True)

# Sidebar
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/Flag_of_Kenya.svg/1200px-Flag_of_Kenya.svg.png", width=100)
st.sidebar.markdown("## Dashboard Controls")
st.sidebar.markdown("---")

# Data generation function
@st.cache_data
def generate_kenya_ad_data():
    """Generate realistic Kenyan advertising data"""
    
    campaigns = [
        "Tourism Kenya - Magical Kenya",
        "Safaricom Bonga Points", 
        "KCB Bank - M-Benki",
        "Mombasa Hotel Bookings",
        "Nairobi Real Estate",
        "Kisumu Agriculture Expo",
        "Eldoret Retail Week",
        "Coast Beach Resorts"
    ]
    
    records = []
    for day in range(90):
        date = datetime.now() - timedelta(days=day)
        for campaign in campaigns:
            spend = np.random.uniform(2000, 20000)
            if "Tourism" in campaign or "Resorts" in campaign:
                roas_multiplier = np.random.uniform(2.5, 5.0)
            elif "KCB" in campaign or "Real Estate" in campaign:
                roas_multiplier = np.random.uniform(1.5, 3.0)
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

# Kenyan media directory
@st.cache_data
def get_kenyan_media():
    """Kenyan TV and Radio stations by region"""
    
    return {
        "Nairobi / National": {
            "TV": [
                {"name": "Citizen TV", "reach": "5,000,000", "format": "General", "language": "English/Swahili"},
                {"name": "KTN", "reach": "3,000,000", "format": "News", "language": "English"},
                {"name": "NTV", "reach": "2,800,000", "format": "News/Entertainment", "language": "English"},
                {"name": "KBC", "reach": "2,000,000", "format": "Public", "language": "Swahili/English"}
            ],
            "Radio": [
                {"name": "Citizen Radio", "reach": "2,500,000", "format": "News/Talk", "language": "English/Swahili"},
                {"name": "Radio Jambo", "reach": "2,000,000", "format": "Entertainment", "language": "Swahili"},
                {"name": "Classic 105", "reach": "1,500,000", "format": "Adult Contemporary", "language": "English"}
            ]
        },
        "Mombasa / Coast": {
            "Radio": [
                {"name": "Baraka FM", "reach": "600,000", "format": "Religious/Talk", "language": "Swahili"},
                {"name": "Milele FM", "reach": "450,000", "format": "Entertainment", "language": "Swahili"}
            ]
        },
        "Kisumu / Western": {
            "Radio": [
                {"name": "Lake Victoria FM", "reach": "700,000", "format": "Vernacular", "language": "Luo"},
                {"name": "Ramogi FM", "reach": "850,000", "format": "Vernacular", "language": "Luo"}
            ]
        },
        "Central": {
            "Radio": [
                {"name": "Inooro FM", "reach": "1,200,000", "format": "Vernacular", "language": "Kikuyu"},
                {"name": "Kameme FM", "reach": "1,000,000", "format": "Vernacular", "language": "Kikuyu"}
            ]
        }
    }

# Load data
df = generate_kenya_ad_data()
media = get_kenyan_media()

# Sidebar filters
st.sidebar.markdown("### Filters")
all_campaigns = df['campaign'].unique().tolist()
selected_campaigns = st.sidebar.multiselect(
    "Select Campaigns",
    all_campaigns,
    default=all_campaigns[:4]
)

all_platforms = df['platform'].unique().tolist()
selected_platforms = st.sidebar.multiselect(
    "Select Platforms",
    all_platforms,
    default=all_platforms
)

# Filter data
filtered_df = df[df['campaign'].isin(selected_campaigns)]
filtered_df = filtered_df[filtered_df['platform'].isin(selected_platforms)]

# Key Metrics Row
st.markdown("## 📊 Performance Dashboard")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_spend = filtered_df['spend_kes'].sum()
    st.metric("💰 Total Ad Spend", f"KES {total_spend:,.0f}")

with col2:
    total_revenue = filtered_df['revenue_kes'].sum()
    st.metric("💵 Total Revenue", f"KES {total_revenue:,.0f}")

with col3:
    avg_roas = total_revenue / total_spend if total_spend > 0 else 0
    delta_color = "normal" if avg_roas >= 2 else "inverse"
    st.metric("📈 Average ROAS", f"{avg_roas:.2f}x")

with col4:
    num_campaigns = len(filtered_df['campaign'].unique())
    st.metric("🎯 Active Campaigns", num_campaigns)

st.markdown("---")

# Charts Row 1
col1, col2 = st.columns(2)

with col1:
    st.markdown("### ROAS by Campaign")
    campaign_roas = filtered_df.groupby('campaign')['roas'].mean().reset_index()
    campaign_roas = campaign_roas.sort_values('roas', ascending=True)
    
    fig = px.bar(campaign_roas, 
                 x='roas', 
                 y='campaign',
                 orientation='h',
                 color='roas',
                 color_continuous_scale='RdYlGn',
                 title="Return on Ad Spend by Campaign",
                 labels={'roas': 'ROAS (x)', 'campaign': ''})
    fig.add_vline(x=2.0, line_dash="dash", line_color="red", annotation_text="Target (2x)")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### Spend vs Revenue Trend")
    daily = filtered_df.groupby('date').agg({
        'spend_kes': 'sum',
        'revenue_kes': 'sum'
    }).reset_index()
    daily['date'] = pd.to_datetime(daily['date'])
    daily = daily.sort_values('date')
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily['date'], y=daily['spend_kes'], 
                            name='Ad Spend', line=dict(color='red', width=2)))
    fig.add_trace(go.Scatter(x=daily['date'], y=daily['revenue_kes'], 
                            name='Revenue', line=dict(color='green', width=2)))
    fig.update_layout(title="Daily Performance", xaxis_title="Date", yaxis_title="Amount (KES)")
    st.plotly_chart(fig, use_container_width=True)

# Charts Row 2
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Platform Performance")
    platform_roas = filtered_df.groupby('platform')['roas'].mean().reset_index()
    fig = px.pie(platform_roas, values='roas', names='platform', 
                 title="ROAS by Platform", hole=0.3)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### Weekly ROAS Trend")
    filtered_df['week'] = pd.to_datetime(filtered_df['date']).dt.isocalendar().week
    weekly = filtered_df.groupby('week').agg({
        'spend_kes': 'sum',
        'revenue_kes': 'sum'
    }).reset_index()
    weekly['roas'] = weekly['revenue_kes'] / weekly['spend_kes']
    
    fig = px.line(weekly, x='week', y='roas', 
                  title="ROAS by Week",
                  markers=True,
                  labels={'week': 'Week Number', 'roas': 'ROAS (x)'})
    fig.add_hline(y=2.0, line_dash="dash", line_color="red")
    st.plotly_chart(fig, use_container_width=True)

# Kenyan Media Section
st.markdown("---")
st.markdown("## 📺 📻 Kenyan Media Directory")
st.markdown("*Find the right TV and radio stations for your campaign*")

col1, col2 = st.columns(2)

with col1:
    selected_region = st.selectbox("Select Region", list(media.keys()))
    
with col2:
    selected_media_type = st.selectbox("Select Media Type", ["Both", "TV", "Radio"])

if selected_region:
    region_media = media[selected_region]
    
    if selected_media_type in ["Both", "TV"] and "TV" in region_media:
        st.markdown(f"### 📺 TV Stations in {selected_region}")
        for tv in region_media["TV"]:
            with st.expander(f"{tv['name']}"):
                st.write(f"**Reach:** {tv['reach']} viewers")
                st.write(f"**Format:** {tv['format']}")
                st.write(f"**Language:** {tv['language']}")
    
    if selected_media_type in ["Both", "Radio"] and "Radio" in region_media:
        st.markdown(f"### 📻 Radio Stations in {selected_region}")
        for radio in region_media["Radio"]:
            with st.expander(f"{radio['name']}"):
                st.write(f"**Reach:** {radio['reach']} listeners")
                st.write(f"**Format:** {radio['format']}")
                st.write(f"**Language:** {radio['language']}")

# Recommendation Engine
st.markdown("---")
st.markdown("## 🎯 Campaign Recommendation Engine")
st.markdown("*Get data-driven recommendations for your advertising campaign*")

col1, col2, col3 = st.columns(3)

with col1:
    product_type = st.selectbox("Product/Service Type", 
                                 ["Tourism", "Banking/Finance", "Agriculture", 
                                  "Retail", "Real Estate", "Telecom", "Healthcare"])

with col2:
    estimated_budget = st.number_input("Estimated Budget (KES)", min_value=50000, value=200000, step=50000)

with col3:
    target_audience = st.selectbox("Target Audience", 
                                    ["Mass Market", "Youth (18-35)", "Professionals", "Rural", "Urban"])

if st.button("Generate Recommendations", type="primary"):
    st.markdown("### 📋 Your Custom Recommendations")
    
    # Recommendation logic
    recommendations = []
    
    if product_type == "Tourism":
        recommendations.append("📍 **Primary Region:** Mombasa/Coast")
        recommendations.append("📺 **Top TV Pick:** Citizen TV (National reach for brand awareness)")
        recommendations.append("📻 **Top Radio Pick:** Baraka FM (Coastal audience)")
        recommendations.append(f"💰 **Suggested Budget Allocation:** KES {estimated_budget:,.0f} (70% TV, 30% Radio)")
        recommendations.append("📈 **Expected ROAS:** 3.5x - 5.0x")
        
    elif product_type == "Banking/Finance":
        recommendations.append("📍 **Primary Region:** Nairobi/National")
        recommendations.append("📺 **Top TV Pick:** KTN (Professional audience)")
        recommendations.append("📻 **Top Radio Pick:** Classic 105 (Urban professionals)")
        recommendations.append(f"💰 **Suggested Budget Allocation:** KES {estimated_budget:,.0f} (80% TV, 20% Radio)")
        recommendations.append("📈 **Expected ROAS:** 2.0x - 3.5x")
        
    elif product_type == "Agriculture":
        recommendations.append("📍 **Primary Region:** Kisumu/Western, Central")
        recommendations.append("📻 **Top Radio Picks:** Ramogi FM (Luo), Inooro FM (Kikuyu)")
        recommendations.append(f"💰 **Suggested Budget Allocation:** KES {estimated_budget:,.0f} (100% Radio)")
        recommendations.append("📈 **Expected ROAS:** 2.5x - 4.0x")
        
    elif product_type == "Retail":
        recommendations.append("📍 **Primary Region:** Nairobi, Mombasa, Kisumu")
        recommendations.append("📺 **Top TV Pick:** NTV")
        recommendations.append("📻 **Top Radio Pick:** Radio Jambo")
        recommendations.append(f"💰 **Suggested Budget Allocation:** KES {estimated_budget:,.0f} (50% TV, 50% Radio)")
        recommendations.append("📈 **Expected ROAS:** 1.8x - 2.8x")
    
    for rec in recommendations:
        st.markdown(rec)
    
    # Generate outreach template
    st.markdown("---")
    st.markdown("### 📧 Outreach Email Template")
    
    email_template = f"""
**Subject:** Advertising Opportunity - {product_type} Campaign in Kenya

Dear Station Sales Team,

I am reaching out regarding a {product_type} advertising campaign with an estimated budget of KES {estimated_budget:,.0f}.

Based on our media intelligence analysis, your station has been identified as an ideal partner for reaching our target audience ({target_audience} demographic).

**Request for Information:**
1. Current rate card (30-second spots)
2. Available inventory for upcoming month
3. Audience demographic breakdown

We look forward to discussing this opportunity.

Best regards,
[Your Name]
Media Intelligence Consultant
"""
    st.code(email_template, language="markdown")
    st.info("💡 **Pro Tip:** Copy this email, add your contact details, and send it to station sales managers")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🇰🇪 Kenya Omni-Channel Ad Intelligence Platform | Built with Streamlit</p>
    <p style="font-size: 0.8rem;">Data sources: Media Council of Kenya, Industry Research</p>
</div>
""", unsafe_allow_html=True)