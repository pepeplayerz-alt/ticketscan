import streamlit as st
import pandas as pd
import time
from datetime import datetime

from modules.supabase_client import (
    sign_in,
    sign_up,
    upload_file,
    save_receipt,
    get_user_receipts,
    delete_receipt,
)
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


def auth_page():
    load_css()
    render_app_header()

    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Sign In", type="primary", use_container_width=True, key="btn_login"):
            if not email or not password:
                st.warning("Enter email and password.")
                return
            try:
                response = sign_in(email, password)
                st.session_state.user = {
                    "id": response.user.id,
                    "email": response.user.email,
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                }
                st.rerun()
            except Exception as e:
                st.error(f"Authentication failed: {e}")

    with tab_register:
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        if st.button("Create Account", type="primary", use_container_width=True, key="btn_register"):
            if not reg_email or not reg_password:
                st.warning("Enter email and password.")
                return
            try:
                response = sign_up(reg_email, reg_password)
                if response.user and response.user.identities is not None and len(response.user.identities) == 0:
                    st.warning("An account with this email already exists.")
                    return
                login = sign_in(reg_email, reg_password)
                st.session_state.user = {
                    "id": login.user.id,
                    "email": login.user.email,
                    "access_token": login.session.access_token,
                    "refresh_token": login.session.refresh_token,
                }
                st.rerun()
            except Exception as e:
                error_msg = str(e)
                if "already registered" in error_msg.lower() or "duplicate" in error_msg.lower():
                    st.warning("An account with this email already exists.")
                else:
                    st.error(f"Registration failed: {error_msg}")


def main():
    if "user" not in st.session_state:
        auth_page()
        st.stop()

    user = st.session_state.user
    load_css()

    render_app_header()

    if "page" not in st.session_state:
        st.session_state.page = "scan"

    nav1, nav2, nav3 = st.columns(3)
    with nav1:
        if st.button(
            "SCAN",
            key="btn_scan",
            use_container_width=True,
            type="primary" if st.session_state.page == "scan" else "secondary",
        ):
            st.session_state.page = "scan"
            st.rerun()
    with nav2:
        if st.button(
            "HISTORY",
            key="btn_history",
            use_container_width=True,
            type="primary" if st.session_state.page == "history" else "secondary",
        ):
            st.session_state.page = "history"
            st.rerun()
    with nav3:
        if st.button(
            "STATS",
            key="btn_stats",
            use_container_width=True,
            type="primary" if st.session_state.page == "stats" else "secondary",
        ):
            st.session_state.page = "stats"
            st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    if st.session_state.page == "scan":
        page_scan(user)
    elif st.session_state.page == "history":
        page_history(user)
    elif st.session_state.page == "stats":
        page_stats(user)

    st.markdown(
        f"""<div class="bottom-bar">
            <span class="bottom-bar-email">{user['email']}</span>
        </div>""",
        unsafe_allow_html=True,
    )
    if st.button("Logout", key="btn_logout", use_container_width=True):
        del st.session_state.user
        st.rerun()


def page_scan(user):
    st.markdown('<div class="section-title">Upload Receipt</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload receipt",
        type=["jpg", "jpeg", "png", "pdf"],
        label_visibility="collapsed",
        key="receipt_uploader",
    )

    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            st.info(f"PDF loaded: {uploaded_file.name}")
        else:
            st.image(uploaded_file, caption="Preview", use_container_width=True)

        if st.button("Analyze Receipt", type="primary", use_container_width=True):
            with st.status("Processing...", expanded=True) as status:
                st.write("Reading file...")
                file_bytes = uploaded_file.getvalue()

                st.write("Uploading to storage...")
                file_url = upload_file(file_bytes, uploaded_file.name, uploaded_file.type)

                st.write("Analyzing with AI...")
                result = analyze_receipt(file_bytes, mime_type=uploaded_file.type)

                if result:
                    st.write("Saving data...")
                    result["file_url"] = file_url
                    save_receipt(result, user["id"])
                    status.update(label="Complete", state="complete", expanded=False)
                    st.toast("Receipt saved successfully.")
                    time.sleep(1)
                    st.session_state.page = "history"
                    st.rerun()
                else:
                    status.update(label="Failed", state="error")
    else:
        render_empty_state("Upload an image or PDF to start")


def page_history(user):
    st.markdown('<div class="section-title">Log</div>', unsafe_allow_html=True)

    receipts = get_user_receipts(user["id"])

    if not receipts:
        render_empty_state("No history available")
        return

    df = pd.DataFrame(receipts)
    df["date_dt"] = pd.to_datetime(df["created_at"], errors="coerce")

    with st.expander("Filter Options", expanded=False):
        merchants = sorted(list(df["merchant"].dropna().unique()))
        sel_merchant = st.multiselect("Merchant", merchants, placeholder="Select merchants...")

        st.markdown("---")

        st.markdown(
            '<div style="font-size:12px; font-weight:700; color:#95A5A6; margin-bottom:8px; '
            'text-transform:uppercase; letter-spacing:1px;">Date Range</div>',
            unsafe_allow_html=True,
        )
        date_mode = st.radio(
            "Date Mode",
            ["All Time", "By Month", "Custom Range"],
            horizontal=True,
            label_visibility="collapsed",
        )

        sel_year = None
        sel_month_idx = None
        start_date = None
        end_date = None

        if date_mode == "By Month":
            years = sorted(
                df["date_dt"].dt.year.dropna().unique().astype(int), reverse=True
            )
            if not years:
                years = [datetime.now().year]

            c1, c2 = st.columns(2)
            sel_year = c1.selectbox("Year", years)

            months = [
                "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
            ]
            sel_month = c2.selectbox("Month", months)
            sel_month_idx = months.index(sel_month) + 1

        elif date_mode == "Custom Range":
            c1, c2 = st.columns(2)
            start_date = c1.date_input("From", value=None)
            end_date = c2.date_input("To", value=None)

    filtered = df.copy()

    if sel_merchant:
        filtered = filtered[filtered["merchant"].isin(sel_merchant)]

    if date_mode == "By Month" and sel_year and sel_month_idx:
        filtered = filtered[
            (filtered["date_dt"].dt.year == sel_year)
            & (filtered["date_dt"].dt.month == sel_month_idx)
        ]
    elif date_mode == "Custom Range" and start_date and end_date:
        filtered = filtered[
            (filtered["date_dt"].dt.date >= start_date)
            & (filtered["date_dt"].dt.date <= end_date)
        ]

    for _, row in filtered.iterrows():
        if render_receipt_card(
            merchant=row.get("merchant", "Unknown"),
            date=str(row.get("created_at", "--"))[:10],
            total=float(row.get("total", 0)),
            currency=row.get("currency", "USD"),
            category=row.get("category", "OTHER"),
            summary=row.get("summary", ""),
            file_url=row.get("file_url", None),
            key=f"card_{row['id']}",
        ):
            delete_receipt(row["id"], user["id"])
            st.rerun()


def page_stats(user):
    st.markdown('<div class="section-title">Analytics</div>', unsafe_allow_html=True)

    receipts = get_user_receipts(user["id"])
    df = pd.DataFrame(receipts) if receipts else pd.DataFrame()

    render_metrics_dashboard(df)

    if df.empty:
        return

    df["total"] = pd.to_numeric(df["total"], errors="coerce").fillna(0)

    if "category" in df.columns:
        cat_spend = df.groupby("category")["total"].sum().sort_values(ascending=False)
        cat_spend = cat_spend[cat_spend > 0]

        if not cat_spend.empty:
            st.markdown(
                '<div class="section-title">Category Breakdown</div>',
                unsafe_allow_html=True,
            )
            st.bar_chart(cat_spend, color="#5C8BB5")

    if "merchant" in df.columns:
        merch_spend = (
            df.groupby("merchant")["total"].sum().sort_values(ascending=False).head(10)
        )
        merch_spend = merch_spend[merch_spend > 0]

        if not merch_spend.empty:
            st.markdown(
                '<div class="section-title">Merchant Breakdown</div>',
                unsafe_allow_html=True,
            )
            st.bar_chart(merch_spend, color="#2C3E50")


if __name__ == "__main__":
    main()
