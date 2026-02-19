import streamlit as st
import pandas as pd


def load_css():
    """Inject industrial mobile-app CSS."""
    st.markdown("""
        <style>
        /* ===== HIDE STREAMLIT DEFAULTS ===== */
        #MainMenu, footer, header, .stDeployButton {display: none !important;}

        /* ===== GLOBAL ===== */
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Roboto', sans-serif !important;
            color: #2C3E50;
        }

        .block-container {
            padding: 1.5rem 1rem 4rem 1rem !important;
            max-width: 480px !important;
            margin: 0 auto;
            background-color: #F8F9FA;
        }

        /* ===== TOP APP BAR (Industrial Style) ===== */
        .app-header {
            background: transparent;
            color: #2C3E50;
            padding: 10px 0 20px 0;
            text-align: center;
            border-bottom: 2px solid #E9ECEF;
            margin-bottom: 1.5rem;
        }
        .app-header h1 {
            color: #2C3E50 !important;
            font-size: 24px !important;
            font-weight: 800 !important;
            margin: 0 !important;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        .app-header p {
            color: #7F8C8D;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin: 4px 0 0 0;
            font-weight: 500;
        }

        /* ===== CARD COMPONENT (Industrial) ===== */
        /* Target the container wrapping the card content and button */
        div[data-testid="stVerticalBlock"]:has(div.receipt-card-marker) {
            background: white;
            border: 1px solid #DCE1E5;
            border-radius: 4px;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.03);
            gap: 0 !important; /* Remove gap between columns if possible */
        }
        
        .card-content {
            /* Inner content style */
        }

        .card-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .card-merchant {
            font-weight: 700;
            font-size: 15px;
            color: #2C3E50;
            text-transform: uppercase;
        }
        .card-amount {
            font-weight: 700;
            font-size: 16px;
            color: #2C3E50;
        }
        .card-meta {
            font-size: 12px;
            color: #95A5A6;
            margin-top: 6px;
        }
        .card-category {
            display: inline-block;
            background: #E9ECEF;
            color: #5C8BB5;
            padding: 2px 8px;
            border-radius: 2px;
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            margin-top: 8px;
        }

        /* ===== METRIC CARDS (Industrial) ===== */
        .metric-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 1.5rem;
        }
        .metric-card {
            background: white;
            border: 1px solid #DCE1E5;
            border-radius: 4px;
            padding: 20px 10px;
            text-align: center;
            box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        }
        .metric-card.featured {
            grid-column: 1 / -1;
            background: #2C3E50;
            color: white;
            border: none;
        }
        .metric-card.featured .metric-value { color: white !important; }
        .metric-card.featured .metric-label { color: #BDC3C7 !important; }
        
        .metric-value {
            font-size: 24px;
            font-weight: 700;
            color: #2C3E50;
            line-height: 1.1;
        }
        .metric-label {
            font-size: 11px;
            color: #95A5A6;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 6px;
        }

        /* ===== SECTION TITLES ===== */
        .section-title {
            font-size: 14px;
            font-weight: 800;
            color: #7F8C8D;
            margin: 20px 0 12px 0;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-bottom: 1px solid #E9ECEF;
            padding-bottom: 4px;
        }

        /* ===== BUTTONS ===== */
        .stButton > button {
            border-radius: 4px !important; /* Square */
            height: 48px !important;
            font-weight: 700 !important;
            font-size: 14px !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            box-shadow: none !important;
            border: 1px solid transparent;
            transition: all 0.2s ease !important;
        }
        
        /* Primary Button (Blue) */
        .stButton > button[kind="primary"] {
            background-color: #5C8BB5 !important;
            color: white !important;
        }
        
        /* Secondary Button (Outline) */
        .stButton > button[kind="secondary"] {
            background-color: white !important;
            border: 1px solid #5C8BB5 !important;
            color: #5C8BB5 !important;
        }
        .stButton > button:hover {
            transform: translateY(-1px);
            border-color: #5C8BB5;
        }

        /* ===== FILE UPLOADER ===== */
        [data-testid="stFileUploader"] {
            background: white;
            border: 1px solid #DCE1E5;
            border-radius: 4px;
            padding: 10px;
        }
        [data-testid="stFileUploader"] section {
            border: 2px dashed #DCE1E5 !important;
            background: #FAFBFC;
            border-radius: 4px;
        }

        /* ===== EMPTY STATE ===== */
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: #95A5A6;
            background: #F8F9FA;
            border: 2px dashed #E9ECEF;
            border-radius: 4px;
        }
        .empty-state .icon {
            font-size: 32px;
            margin-bottom: 12px;
            opacity: 0.5;
            font-family: monospace;
        }

        /* ===== CHART ===== */
        [data-testid="stArrowVegaLiteChart"],
        [data-testid="stBarChart"] {
            background: white;
            border: 1px solid #DCE1E5;
            padding: 10px;
            border-radius: 4px;
        }
        
        /* Clean up standard Streamlit spacing */
        .st-emotion-cache-1y4p8pa { padding: 0 !important; }
        div[data-testid="stVerticalBlock"] { gap: 0.5rem; }
        
        /* ===== RADIO BUTTONS (Industrial Pills) ===== */
        div[role="radiogroup"] {
            background-color: white;
            padding: 4px;
            border-radius: 4px;
            border: 1px solid #DCE1E5;
            display: flex;
            gap: 4px;
        }
        div[role="radiogroup"] label {
            background-color: transparent;
            border: none;
            border-radius: 2px;
            padding: 4px 12px;
            margin: 0 !important;
            transition: all 0.2s;
            font-size: 12px;
            font-weight: 600;
            color: #7F8C8D;
            flex: 1;
            text-align: center;
            justify-content: center;
        }
        div[role="radiogroup"] label[data-checked="true"] {
            background-color: #5C8BB5 !important;
            color: white !important;
        }

        /* ===== AUTH TABS ===== */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
            background: white;
            border: 1px solid #DCE1E5;
            border-radius: 4px;
            padding: 4px;
        }
        .stTabs [data-baseweb="tab"] {
            flex: 1;
            justify-content: center;
            font-weight: 700;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #7F8C8D;
            border-radius: 2px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #5C8BB5 !important;
            color: white !important;
        }
        .stTabs [data-baseweb="tab-highlight"] { display: none; }
        .stTabs [data-baseweb="tab-border"] { display: none; }
        
        </style>
    """, unsafe_allow_html=True)


def render_app_header():
    """Render the top app bar."""
    st.markdown("""
        <div class="app-header">
            <h1>TicketScan</h1>
            <p>Receipt Intelligence</p>
        </div>
    """, unsafe_allow_html=True)


def render_receipt_card(merchant, date, total, currency, category, summary, file_url=None, key=None):
    view_btn = ""
    if file_url:
        view_btn = (
            f'<div style="margin-top: 10px; text-align: right;">'
            f'<a href="{file_url}" target="_blank" style="'
            f'text-decoration: none; color: white; background-color: #5C8BB5; '
            f'font-size: 11px; font-weight: 700; border: 1px solid white; '
            f'padding: 4px 8px; border-radius: 4px; text-transform: uppercase;">'
            f'View Ticket</a></div>'
        )

    with st.container():
        st.markdown('<div class="receipt-card-marker" style="display:none;"></div>', unsafe_allow_html=True)

        c1, c2 = st.columns([0.85, 0.15])

        with c1:
            st.markdown(f"""
                <div class="card-content">
                    <div class="card-row">
                        <span class="card-merchant">{merchant}</span>
                        <span class="card-amount">{total:.2f} {currency}</span>
                    </div>
                    <div class="card-meta">{date} // {summary}</div>
                    <div style="display: flex; justify-content: space-between; align-items: flex-end;">
                        <span class="card-category">{category}</span>
                        {view_btn}
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown("<div style='height: 5px'></div>", unsafe_allow_html=True)
            if st.button("X", key=key, type="secondary", use_container_width=True):
                return True

    return False


def render_metrics_dashboard(df):
    """Render dashboard metric cards."""
    if df.empty:
        st.markdown("""
            <div class="empty-state">
                <div class="icon">--</div>
                <p>No data analyzed.</p>
            </div>
        """, unsafe_allow_html=True)
        return

    df['total'] = pd.to_numeric(df['total'], errors='coerce').fillna(0)
    total_spent = df['total'].sum()
    receipt_count = len(df)
    unique_merchants = df['merchant'].nunique()

    st.markdown(f"""
        <div class="metric-grid">
            <div class="metric-card featured">
                <div class="metric-value">${total_spent:,.2f}</div>
                <div class="metric-label">Total Spend</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{receipt_count}</div>
                <div class="metric-label">Tickets</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{unique_merchants}</div>
                <div class="metric-label">Merchants</div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_empty_state(message="No receipts found."):
    """Render a clean empty state."""
    st.markdown(f"""
        <div class="empty-state">
            <div class="icon">[ ]</div>
            <p>{message}</p>
        </div>
    """, unsafe_allow_html=True)
