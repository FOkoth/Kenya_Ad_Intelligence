"""
CSS styles for the application
"""
import streamlit as st

def apply_styles():
    """Apply custom CSS styles"""
    st.markdown("""
    <style>
        /* Main container */
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        /* Header styling */
        .app-header {
            background: linear-gradient(135deg, #004953 0%, #006B7A 100%);
            padding: 1.5rem 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            box-shadow: 0 4px 20px rgba(0,73,83,0.15);
        }
        .header-title h1 {
            color: white;
            margin: 0;
            font-size: 1.6rem;
            font-weight: 600;
        }
        .header-title p {
            color: rgba(255,255,255,0.85);
            margin: 0.25rem 0 0 0;
            font-size: 0.85rem;
        }
        .logout-btn {
            background: rgba(255,255,255,0.15);
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 10px;
            padding: 0.5rem 1.2rem;
            color: white;
            cursor: pointer;
            transition: all 0.2s;
            font-weight: 500;
        }
        .logout-btn:hover {
            background: rgba(255,255,255,0.25);
            transform: translateY(-1px);
        }
        
        /* Login page */
        .login-container {
            max-width: 450px;
            margin: 0 auto;
            padding: 2rem;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.08);
            border: 1px solid #E2E8F0;
        }
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .login-header h2 {
            color: #004953;
            margin-bottom: 0.5rem;
        }
        .login-header p {
            color: #64748B;
            font-size: 0.85rem;
        }
        
        /* Metric cards */
        .metric-card {
            background: white;
            border-radius: 16px;
            padding: 1.2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            border-left: 4px solid #C6A43F;
            text-align: center;
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #004953;
        }
        .metric-label {
            font-size: 0.75rem;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
        }
        
        /* Section cards */
        .section-card {
            background: white;
            border-radius: 20px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid #E2E8F0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        }
        .section-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #1E293B;
            margin-bottom: 1.2rem;
            padding-bottom: 0.75rem;
            border-bottom: 2px solid #C6A43F;
            display: inline-block;
        }
        
        /* Recommendation cards */
        .rec-card {
            background: linear-gradient(135deg, #004953 0%, #003540 100%);
            border-radius: 16px;
            padding: 1.2rem;
            color: white;
            margin-bottom: 1rem;
            transition: transform 0.2s;
        }
        .rec-card:hover {
            transform: translateX(5px);
        }
        .rec-card h4 {
            color: #C6A43F;
            margin: 0 0 0.6rem 0;
            font-size: 1.1rem;
        }
        .rec-card p {
            margin: 0.3rem 0;
            font-size: 0.85rem;
            opacity: 0.9;
        }
        
        /* Booking cards */
        .booking-card {
            background: #FFFBEB;
            border: 1px solid #FDE68A;
            border-radius: 16px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            transition: all 0.2s;
        }
        .booking-card-pending { border-left: 5px solid #F59E0B; background: #FFFBEB; }
        .booking-card-approved { border-left: 5px solid #8B5CF6; background: #F5F3FF; }
        .booking-card-confirmed { border-left: 5px solid #10B981; background: #ECFDF5; }
        .booking-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            margin-bottom: 0.75rem;
        }
        .booking-id { font-weight: 700; font-size: 1rem; color: #1E293B; }
        .booking-date { font-size: 0.75rem; color: #64748B; }
        .booking-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 0.5rem;
            margin: 0.75rem 0;
        }
        .booking-detail-item { font-size: 0.85rem; }
        .booking-detail-label { font-weight: 600; color: #475569; }
        
        /* Lead cards */
        .lead-card {
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            transition: all 0.2s;
        }
        .lead-card:hover {
            border-color: #C6A43F;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        .lead-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            margin-bottom: 0.75rem;
        }
        .lead-name { font-weight: 700; font-size: 1rem; color: #1E293B; }
        .lead-contact {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 0.5rem;
            margin: 0.5rem 0;
            font-size: 0.8rem;
            color: #475569;
        }
        .lead-message {
            background: white;
            padding: 0.75rem;
            border-radius: 12px;
            margin-top: 0.5rem;
            font-size: 0.85rem;
            color: #334155;
            border-left: 3px solid #C6A43F;
        }
        
        /* Status badges */
        .badge-pending { background: #F59E0B; color: white; padding: 0.25rem 0.9rem; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
        .badge-approved { background: #8B5CF6; color: white; padding: 0.25rem 0.9rem; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
        .badge-confirmed { background: #10B981; color: white; padding: 0.25rem 0.9rem; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
        .badge-new { background: #10B981; color: white; padding: 0.25rem 0.9rem; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
        .badge-contacted { background: #F59E0B; color: white; padding: 0.25rem 0.9rem; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
        .badge-converted { background: #8B5CF6; color: white; padding: 0.25rem 0.9rem; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
        
        /* Time filter bar */
        .time-filter-bar {
            background: #F8FAFC;
            padding: 1rem;
            border-radius: 16px;
            margin-bottom: 1.5rem;
            display: flex;
            gap: 1rem;
            align-items: center;
            flex-wrap: wrap;
        }
        
        /* Button styling */
        .stButton > button {
            background: #004953;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.6rem 1.5rem;
            font-weight: 500;
            transition: all 0.2s;
            width: 100%;
        }
        .stButton > button:hover {
            background: #006B7A;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,73,83,0.2);
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 1.5rem;
            margin-top: 2rem;
            background: #F8FAFC;
            border-radius: 16px;
            font-size: 0.75rem;
            color: #64748B;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            background: #F1F5F9;
            padding: 0.5rem;
            border-radius: 14px;
            margin-bottom: 1.5rem;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px;
            padding: 0.6rem 1.5rem;
            font-size: 0.85rem;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            background: #004953;
            color: white;
        }
        
        /* Hide default Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
