import streamlit as st
import pandas as pd
import time
from datetime import datetime

from modules.database import init_db, save_receipt, get_all_receipts
from modules.ai_service import analyze_receipt
from modules.utils import (
    load_css,
    render_app_header,
    render_receipt_card,
    render_metrics_dashboard,
    render_empty_state,
)


st.set_page_config(
    page_title="TicketScan",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def main():
    load_css()
    init_db()

    if "page" not in st.session_state:
        st.session_state.page = "scan"

    
    render_app_header()

    nav1, nav2, nav3 = st.columns(3)
    with nav1:
        if st.button("SCAN", key="btn_scan", use_container_width=True,
                      type="primary" if st.session_state.page == "scan" else "secondary"):
            st.session_state.page = "scan"
            st.rerun()
    with nav2:
        if st.button("HISTORY", key="btn_history", use_container_width=True,
                      type="primary" if st.session_state.page == "history" else "secondary"):
            st.session_state.page = "history"
            st.rerun()
    with nav3:
        if st.button("STATS", key="btn_stats", use_container_width=True,
                      type="primary" if st.session_state.page == "stats" else "secondary"):
            st.session_state.page = "stats"
            st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)


    if st.session_state.page == "scan":
        page_scan()
    elif st.session_state.page == "history":
        page_history()
    elif st.session_state.page == "stats":
        page_stats()


# ──────────────────────────────────────────────
#  PAGE: Scan
# ──────────────────────────────────────────────
def page_scan():
    st.markdown('<div class="section-title">Upload Receipt</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload receipt image",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
        key="receipt_uploader",
    )

    if uploaded_file:
        st.image(uploaded_file, caption="Preview", width="stretch")

        if st.button("Analyze Receipt", type="primary", use_container_width=True):
            with st.status("Processing...", expanded=True) as status:
                st.write("Reading image...")
                image_bytes = uploaded_file.getvalue()
                
                from modules.file_manager import save_uploaded_image
                db_image_path = save_uploaded_image(image_bytes, uploaded_file.name)

                result = analyze_receipt(image_bytes, mime_type=uploaded_file.type)

                if result:
                    st.write("Saving data...")
                    # Override date with current upload date as requested
                    result['date'] = datetime.now().strftime("%Y-%m-%d")
                    result['image_path'] = db_image_path
                    save_receipt(result)
                    status.update(label="Complete", state="complete", expanded=False)
                    st.toast("Success")
                    time.sleep(1)
                    st.session_state.page = "history"
                    st.rerun()
                else:
                    status.update(label="Failed", state="error")
    else:
        render_empty_state("Upload an image to start")


# ──────────────────────────────────────────────
#  PAGE: History
# ──────────────────────────────────────────────
def page_history():
    st.markdown('<div class="section-title">Log</div>', unsafe_allow_html=True)

    df = get_all_receipts()

    if df.empty:
        render_empty_state("No history available")
        return

    # --- Preprocess Dates ---
    df["date_dt"] = pd.to_datetime(df["date"], errors="coerce")

    # --- Filters ---
    with st.expander("Filter Options", expanded=False):
        # 1. Merchant Filter
        merchants = sorted(list(df["merchant"].dropna().unique()))
        sel_merchant = st.multiselect("Merchant", merchants, placeholder="Select merchants...")
        
        st.markdown("---")
        
        # 2. Date Filter
        st.markdown('<div style="font-size:12px; font-weight:700; color:#95A5A6; margin-bottom:8px; text-transform:uppercase; letter-spacing:1px;">Date Range</div>', unsafe_allow_html=True)
        date_mode = st.radio("Date Mode", ["All Time", "By Month", "Custom Range"], horizontal=True, label_visibility="collapsed")
        
        sel_year = None
        sel_month_idx = None
        date_range = None

        if date_mode == "By Month":
            # Get available years
            years = sorted(df["date_dt"].dt.year.dropna().unique().astype(int), reverse=True)
            if not years:
                years = [datetime.now().year]
            
            c1, c2 = st.columns(2)
            sel_year = c1.selectbox("Year", years)
            
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            sel_month = c2.selectbox("Month", months)
            sel_month_idx = months.index(sel_month) + 1
            
        elif date_mode == "Custom Range":
            c1, c2 = st.columns(2)
            start_date = c1.date_input("From", value=None)
            end_date = c2.date_input("To", value=None)


    # --- Apply Filters ---
    filtered = df.copy()
    
    # Merchant
    if sel_merchant:
        filtered = filtered[filtered["merchant"].isin(sel_merchant)]
        
    # Date
    if date_mode == "By Month" and sel_year and sel_month_idx:
        filtered = filtered[
            (filtered["date_dt"].dt.year == sel_year) & 
            (filtered["date_dt"].dt.month == sel_month_idx)
        ]
    elif date_mode == "Custom Range" and start_date and end_date:
        # Filter by date range (inclusive)
        filtered = filtered[
            (filtered["date_dt"].dt.date >= start_date) & 
            (filtered["date_dt"].dt.date <= end_date)
        ]

    # --- Render Cards ---
    from modules.database import delete_receipt
    
    for _, row in filtered.iterrows():
        # render_receipt_card handles the layout and delete button
        if render_receipt_card(
            merchant=row.get("merchant", "Unknown"),
            date=row.get("date", "--"),
            total=float(row.get("total", 0)),
            currency=row.get("currency", "USD"),
            category=row.get("category", "OTHER"),
            summary=row.get("narrative_summary", ""),
            image_path=row.get("image_path", None),
            key=f"card_{row['id']}"
        ):
            delete_receipt(row['id'])
            st.rerun()


# ──────────────────────────────────────────────
#  PAGE: Insights / Stats
# ──────────────────────────────────────────────
def page_stats():
    st.markdown('<div class="section-title">Analytics</div>', unsafe_allow_html=True)

    df = get_all_receipts()
    render_metrics_dashboard(df)

    if df.empty:
        return

    df["total"] = pd.to_numeric(df["total"], errors="coerce").fillna(0)

    # --- Spending by Category ---
    if "category" in df.columns:
        cat_spend = df.groupby("category")["total"].sum().sort_values(ascending=False)
        # Filter out 0 or negative values to avoid Vega-Lite "Infinite extent" warnings
        cat_spend = cat_spend[cat_spend > 0]
        
        if not cat_spend.empty:
            st.markdown('<div class="section-title">Category Breakdown</div>', unsafe_allow_html=True)
            st.bar_chart(cat_spend, color="#5C8BB5")

    # --- Spending by Merchant ---
    if "merchant" in df.columns:
        merch_spend = df.groupby("merchant")["total"].sum().sort_values(ascending=False).head(10)
        merch_spend = merch_spend[merch_spend > 0]
        
        if not merch_spend.empty:
            st.markdown('<div class="section-title">Merchant Breakdown</div>', unsafe_allow_html=True)
            st.bar_chart(merch_spend, color="#2C3E50")
        
if __name__ == "__main__":
    main()
