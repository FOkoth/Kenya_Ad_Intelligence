"""
CSS styles for the application - Professional Responsive Design
"""
import streamlit as st

def apply_styles():
    """Apply custom CSS styles"""
    st.markdown("""
    <style>
        /* ============================================ */
        /* MAIN CONTAINER - FULL WIDTH FIX */
        /* ============================================ */
        .main .block-container {
            padding: 1rem 2rem 2rem 2rem;
            max-width: 100% !important;
            width: 100% !important;
        }
        
        /* Remove default padding restrictions */
        section.main > div {
            max-width: 100% !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        /* ============================================ */
        /* HEADER STYLING - GRADIENT BACKGROUND */
        /* ============================================ */
        .app-header {
            background: linear-gradient(135deg, #004953 0%, #006B7A 100%);
            padding: 1.2rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            box-shadow: 0 8px 32px rgba(0,73,83,0.15);
        }
        
        .header-title h1 {
            color: white;
            margin: 0;
            font-size: 1.5rem;
            font-weight: 600;
            letter-spacing: -0.3px;
        }
        
        .header-title p {
            color: rgba(255,255,255,0.85);
            margin: 0.2rem 0 0 0;
            font-size: 0.8rem;
        }
        
        /* Logout button styling */
        .logout-btn-custom {
            background: rgba(255,255,255,0.15);
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 12px;
            padding: 0.5rem 1.2rem;
            color: white;
            font-weight: 500;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s ease;
            text-align: center;
        }
        
        .logout-btn-custom:hover {
            background: rgba(255,255,255,0.25);
            transform: translateY(-2px);
        }
        
        /* ============================================ */
        /* LOGIN PAGE STYLING */
        /* ============================================ */
        .login-container {
            max-width: 450px;
            margin: 0 auto;
            padding: 2rem;
            background: white;
            border-radius: 24px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.08);
            border: 1px solid #E2E8F0;
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 1.5rem;
        }
        
        .login-header h2 {
            color: #004953;
            margin-bottom: 0.5rem;
            font-size: 1.5rem;
        }
        
        .login-header p {
            color: #64748B;
            font-size: 0.85rem;
        }
        
        /* ============================================ */
        /* METRIC CARDS - MODERN & INTERACTIVE */
        /* ============================================ */
        .metric-card {
            background: white;
            border-radius: 20px;
            padding: 1rem 0.8rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            border: 1px solid #E2E8F0;
            text-align: center;
            transition: all 0.2s ease;
            height: 100%;
        }
        
        .metric-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 24px rgba(0,0,0,0.08);
            border-color: #C6A43F;
        }
        
        .metric-value {
            font-size: 1.6rem;
            font-weight: 700;
            color: #004953;
            line-height: 1.2;
        }
        
        .metric-label {
            font-size: 0.7rem;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            font-weight: 600;
            margin-top: 0.3rem;
        }
        
        /* ============================================ */
        /* SECTION CARDS */
        /* ============================================ */
        .section-card {
            background: white;
            border-radius: 20px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid #E2E8F0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        }
        
        .section-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #1E293B;
            margin-bottom: 1.2rem;
            padding-bottom: 0.6rem;
            border-bottom: 2px solid #C6A43F;
            display: inline-block;
        }
        
        /* ============================================ */
        /* RECOMMENDATION CARDS */
        /* ============================================ */
        .rec-card {
            background: linear-gradient(135deg, #004953 0%, #003540 100%);
            border-radius: 16px;
            padding: 1rem;
            color: white;
            margin-bottom: 0.8rem;
            transition: transform 0.2s ease;
        }
        
        .rec-card:hover {
            transform: translateX(5px);
        }
        
        .rec-card h4 {
            color: #C6A43F;
            margin: 0 0 0.5rem 0;
            font-size: 1rem;
        }
        
        .rec-card p {
            margin: 0.25rem 0;
            font-size: 0.8rem;
            opacity: 0.9;
        }
        
        /* ============================================ */
        /* BOOKING CARDS */
        /* ============================================ */
        .booking-card {
            border-radius: 16px;
            padding: 1rem;
            margin-bottom: 1rem;
            transition: all 0.2s ease;
        }
        
        .booking-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        }
        
        .booking-card-pending { 
            background: #FFFBEB; 
            border: 1px solid #FDE68A; 
            border-left: 4px solid #F59E0B; 
        }
        
        .booking-card-approved { 
            background: #F5F3FF; 
            border: 1px solid #C4B5FD; 
            border-left: 4px solid #8B5CF6; 
        }
        
        .booking-card-confirmed { 
            background: #ECFDF5; 
            border: 1px solid #A7F3D0; 
            border-left: 4px solid #10B981; 
        }
        
        .booking-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            margin-bottom: 0.75rem;
        }
        
        .booking-id {
            font-weight: 700;
            font-size: 0.95rem;
            color: #1E293B;
        }
        
        .booking-date {
            font-size: 0.7rem;
            color: #64748B;
        }
        
        .booking-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 0.5rem;
            margin: 0.6rem 0;
        }
        
        .booking-detail-item {
            font-size: 0.8rem;
        }
        
        .booking-detail-label {
            font-weight: 600;
            color: #475569;
        }
        
        /* ============================================ */
        /* LEAD CARDS */
        /* ============================================ */
        .lead-card {
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 1rem;
            margin-bottom: 0.8rem;
            transition: all 0.2s ease;
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
            margin-bottom: 0.6rem;
        }
        
        .lead-name {
            font-weight: 700;
            font-size: 0.95rem;
            color: #1E293B;
        }
        
        .lead-contact {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 0.4rem;
            margin: 0.4rem 0;
            font-size: 0.75rem;
            color: #475569;
        }
        
        .lead-message {
            background: white;
            padding: 0.6rem;
            border-radius: 12px;
            margin-top: 0.5rem;
            font-size: 0.8rem;
            color: #334155;
            border-left: 3px solid #C6A43F;
        }
        
        /* ============================================ */
        /* STATUS BADGES */
        /* ============================================ */
        .badge {
            display: inline-block;
            padding: 0.2rem 0.8rem;
            border-radius: 20px;
            font-size: 0.65rem;
            font-weight: 600;
        }
        
        .badge-pending { background: #F59E0B; color: white; }
        .badge-approved { background: #8B5CF6; color: white; }
        .badge-confirmed { background: #10B981; color: white; }
        .badge-new { background: #10B981; color: white; }
        .badge-contacted { background: #F59E0B; color: white; }
        .badge-converted { background: #8B5CF6; color: white; }
        
        /* ============================================ */
        /* BUTTON STYLING */
        /* ============================================ */
        .stButton > button {
            background: #004953;
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.5rem 1.2rem;
            font-weight: 500;
            transition: all 0.2s ease;
            width: 100%;
        }
        
        .stButton > button:hover {
            background: #006B7A;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,73,83,0.2);
        }
        
        /* ============================================ */
        /* TIME FILTER BAR */
        /* ============================================ */
        .time-filter-bar {
            background: #F8FAFC;
            padding: 1rem 1.2rem;
            border-radius: 16px;
            margin-bottom: 1.5rem;
            display: flex;
            gap: 1rem;
            align-items: center;
            flex-wrap: wrap;
        }
        
        /* ============================================ */
        /* TAB STYLING */
        /* ============================================ */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            background: #F1F5F9;
            padding: 0.5rem;
            border-radius: 14px;
            margin-bottom: 1.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px;
            padding: 0.5rem 1.2rem;
            font-size: 0.8rem;
            font-weight: 500;
            white-space: nowrap;
        }
        
        .stTabs [aria-selected="true"] {
            background: #004953;
            color: white;
        }
        
        /* ============================================ */
        /* EXPANDER STYLING */
        /* ============================================ */
        .streamlit-expanderHeader {
            background: #F8FAFC;
            border-radius: 12px;
            font-weight: 500;
            font-size: 0.85rem;
        }
        
        /* ============================================ */
        /* FOOTER */
        /* ============================================ */
        .footer {
            text-align: center;
            padding: 1.2rem;
            margin-top: 2rem;
            background: #F8FAFC;
            border-radius: 16px;
            font-size: 0.7rem;
            color: #64748B;
        }
        
        /* ============================================ */
        /* RESPONSIVE DESIGN */
        /* ============================================ */
        @media (max-width: 768px) {
            .main .block-container {
                padding: 0.5rem 1rem 1rem 1rem;
            }
            
            .app-header {
                flex-direction: column;
                text-align: center;
                gap: 0.8rem;
                padding: 1rem;
            }
            
            .header-title h1 {
                font-size: 1.2rem;
            }
            
            .metric-value {
                font-size: 1.2rem;
            }
            
            .booking-details {
                grid-template-columns: 1fr;
            }
            
            .stTabs [data-baseweb="tab"] {
                padding: 0.4rem 0.8rem;
                font-size: 0.7rem;
            }
        }
        
        /* Large screens - better spacing */
        @media (min-width: 1200px) {
            .main .block-container {
                padding: 1rem 3rem 2rem 3rem;
            }
        }
        
        /* ============================================ */
        /* HIDE DEFAULT STREAMLIT BRANDING */
        /* ============================================ */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* ============================================ */
        /* DATA FRAME STYLING */
        /* ============================================ */
        .dataframe {
            font-size: 0.8rem;
            border-radius: 12px;
            overflow: hidden;
        }
        
        /* ============================================ */
        /* SELECT BOX STYLING */
        /* ============================================ */
        .stSelectbox > div > div {
            border-radius: 10px;
        }
        
        /* ============================================ */
        /* NUMBER INPUT STYLING */
        /* ============================================ */
        .stNumberInput > div > div > input {
            border-radius: 10px;
        }
        
        /* ============================================ */
        /* TEXT INPUT STYLING */
        /* ============================================ */
        .stTextInput > div > div > input {
            border-radius: 10px;
        }
        
        /* ============================================ */
        /* TEXT AREA STYLING */
        /* ============================================ */
        .stTextArea > div > div > textarea {
            border-radius: 10px;
        }
        
        /* ============================================ */
        /* DATE INPUT STYLING */
        /* ============================================ */
        .stDateInput > div > div > input {
            border-radius: 10px;
        }
        
        /* ============================================ */
        /* MULTISELECT STYLING */
        /* ============================================ */
        .stMultiSelect > div > div {
            border-radius: 10px;
        }
    </style>
    """, unsafe_allow_html=True)
