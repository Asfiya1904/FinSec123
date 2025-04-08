
import streamlit as st
import pandas as pd
import numpy as np
import requests
import os

st.set_page_config(page_title="FinSec Full Suite", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
    body, .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .st-c1, .st-c2, .css-1aumxhk {
        background-color: #1c1f26;
    }
    </style>
    """, unsafe_allow_html=True
)

st.title("🛡️ FinSec Full Dashboard")

if "auth" not in st.session_state:
    st.session_state.auth = {"logged_in": False, "role": None, "email": ""}

if not st.session_state.auth["logged_in"]:
    st.subheader("🔐 Login")
    with st.form("login_form"):
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["Admin", "Financial Client"])
        email = st.text_input("Email (for alerts)")
        submitted = st.form_submit_button("Login")
        if submitted:
            if user and pw:
                st.session_state.auth = {"logged_in": True, "role": role, "email": email}
                st.success("Login successful.")
                st.experimental_rerun()
            else:
                st.error("Please fill in all fields.")
    st.stop()

# Navigation
st.sidebar.title("Navigation")
nav = st.sidebar.radio("Go to", ["📊 Dashboard", "📥 Upload", "📁 Reports", "⚙️ Settings", "🚪 Logout"])
st.sidebar.write(f"Logged in as: {st.session_state.auth['role']}")

# Handle logout
if nav == "🚪 Logout":
    st.session_state.auth = {"logged_in": False, "role": None}
    st.experimental_rerun()

# Dashboard Page
elif nav == "📊 Dashboard":
    st.subheader("📊 Overview")
    st.metric("Transactions Today", "1342")
    st.metric("Threats Detected", "22")
    st.metric("API Status", "✅ Online")

# Upload Page
elif nav == "📥 Upload":
    st.subheader("📥 Upload Data for Analysis")
    use_api = st.toggle("Use FinSec API", value=True)
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        st.dataframe(df.head())
        if st.button("🚨 Analyze"):
            results = []
            for i, row in df.iterrows():
                row_data = row.to_dict()
                if use_api:
                    try:
                        r = requests.post(
                            os.getenv("FINSEC_API_URL", "https://finsec1.onrender.com/detect"),
                            headers={"Authorization": f"Bearer {os.getenv('FINSEC_API_KEY', 'supersecret')}",
                                     "Content-Type": "application/json"},
                            json=row_data, timeout=10)
                        result = r.json() if r.status_code == 200 else {"status": "API Error"}
                        row_data.update(result)
                    except:
                        row_data.update({"status": "Failed"})
                else:
                    score = sum(abs(float(v)) for k, v in row.items() if isinstance(v, (int, float)))
                    row_data.update({
                        "risk_score": round(score, 2),
                        "status": "🟢 Normal" if score < 100 else "🔴 Suspicious",
                        "severity": "Low" if score < 100 else "High",
                        "recommendation": "Review" if score >= 100 else "Monitor"
                    })
                results.append(row_data)
            result_df = pd.DataFrame(results)
            st.session_state["last_result"] = result_df
            st.dataframe(result_df)
            st.download_button("📁 Download Results", result_df.to_csv(index=False), "results.csv", "text/csv")

# Reports Page
elif nav == "📁 Reports":
    st.subheader("📄 Reports")
    if "last_result" in st.session_state:
        st.dataframe(st.session_state["last_result"])
        st.download_button("📥 Download CSV", st.session_state["last_result"].to_csv(index=False),
                           "full_report.csv", "text/csv")
    else:
        st.info("No results available yet.")

# Settings Page
elif nav == "⚙️ Settings":
    st.subheader("⚙️ Application Settings")
    st.text_input("Webhook URL")
    st.selectbox("Risk Sensitivity", ["Low", "Medium", "High"])
    st.toggle("Enable Email Alerts", value=True)
