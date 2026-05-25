# -*- coding: utf-8 -*-
"""
Created on Sat May 23 18:50:36 2026

@author: dvlpt
"""

#Installation
#pip install streamlit



# =============================================================================
# import streamlit as st
# Title of the app
# st.title("My First Streamlit App")
# 
# # Text input
# name = st.text_input("Enter your name:")
# 
# # Number input
# age = st.number_input("Enter your age:", min_value=1, max_value=120)
# 
# # Button
# if st.button("Submit"):
#     st.write(f"Hello {name}, you are {age} years old!")
# 
# =============================================================================

# =============================================================================
# 
# import streamlit as st
# import pandas as pd
# import numpy as np
# 
# # Title and description
# st.title("My Enhanced Streamlit App")
# st.write("This app shows how to make a nicer UI.")
# 
# # Sidebar
# st.sidebar.header("User Input")
# name = st.sidebar.text_input("Enter your name:")
# age = st.sidebar.slider("Select your age:", 1, 100, 25)
# 
# # Main content
# st.header("Greetings")
# if name:
#     st.success(f"Hello {name}, you are {age} years old!")
# 
# # Columns layout
# col1, col2 = st.columns(2)
# col1.write("Left side content")
# col2.write("Right side content")
# 
# # Chart
# st.header("Random Data Chart")
# data = pd.DataFrame(np.random.randn(20, 3), columns=['A', 'B', 'C'])
# st.line_chart(data)
# 
# =============================================================================


# =============================================================================
# 
# import streamlit as st
# import pandas as pd
# import win32evtlog
# from datetime import datetime, timedelta
# 
# # --- Cache data to avoid re-reading logs ---
# @st.cache_data
# def get_wake_events(days=30):
#     server = 'localhost'
#     log_type = 'System'
#     hand = win32evtlog.OpenEventLog(server, log_type)
# 
#     start_time = datetime.now() - timedelta(days=days)
#     flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
# 
#     events_per_day = {}
# 
#     while True:
#         events = win32evtlog.ReadEventLog(hand, flags, 0)
#         if not events:
#             break
#         for ev in events:
#             if ev.EventID == 1 and ev.TimeGenerated >= start_time:
#                 day = ev.TimeGenerated.strftime("%Y-%m-%d")
#                 events_per_day[day] = events_per_day.get(day, 0) + 1
# 
#     df = pd.DataFrame(list(events_per_day.items()), columns=["Date", "Opens"])
#     df["Date"] = pd.to_datetime(df["Date"])
#     df = df.sort_values("Date")
#     return df
# 
# # --- Weekly aggregation (weeks start Sunday) ---
# def aggregate_weekly(df):
#     df["WeekStart"] = df["Date"] - pd.to_timedelta(df["Date"].dt.weekday + 1, unit="D")
#     weekly = df.groupby("WeekStart")["Opens"].sum().reset_index()
#     weekly = weekly.sort_values("WeekStart").tail(4)
#     return weekly
# 
# # --- Streamlit UI ---
# st.set_page_config(page_title="Laptop Wake Events Dashboard", layout="wide")
# 
# st.title("💻 Laptop Wake Events Dashboard")
# st.write("This dashboard shows how many times your laptop was opened (wake events).")
# 
# data = get_wake_events(30)
# weekly_data = aggregate_weekly(data)
# 
# # --- Charts ---
# col1, col2 = st.columns(2)
# 
# with col1:
#     st.subheader("Daily Wake Events (Last 30 Days)")
#     st.bar_chart(data.set_index("Date"))  # vertical bars
# 
# with col2:
#     st.subheader("Weekly Aggregated Wake Events (Last 4 Weeks)")
#     st.bar_chart(weekly_data.set_index("WeekStart"))  # vertical bars
# 
# # --- Notes section ---
# st.markdown("### 📊 Notes")
# st.markdown("""
# - **X-axis** shows dates or weeks starting Sunday.  
# - **Y-axis** shows the number of times the laptop woke up.  
# - Daily chart shows raw counts; weekly chart shows totals per week.  
# """)
# 
# # --- Styling tweaks ---
# st.markdown("""
# <style>
# h1, h2, h3, h4, h5, h6 { color: #2E86C1; }
# body { background-color: #F8F9F9; }
# </style>
# """, unsafe_allow_html=True)
# 
# =============================================================================




import streamlit as st
import pandas as pd
import win32evtlog
from datetime import datetime, timedelta
import altair as alt

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Laptop Wake Insights", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- STREAMLIT CUSTOM THEME/STYLE OVERRIDES ---
st.markdown("""
    <style>
    div[data-testid="stMetricValue"] { font-size: 28px; font-weight: bold; color: #2C3E50; }
    .block-container { padding-top: 2rem; }
    .explanation-box { background-color: #F8F9FA; border-left: 4px solid #3498DB; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def get_wake_events(days=90): 
    server = 'localhost'
    log_type = 'System'
    hand = win32evtlog.OpenEventLog(server, log_type)
    start_time = datetime.now() - timedelta(days=days)
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    
    all_events = []

    while True:
        events = win32evtlog.ReadEventLog(hand, flags, 0)
        if not events:
            break
        for ev in events:
            if ev.EventID == 1 and ev.TimeGenerated >= start_time:
                wake_reason = "Unknown / System Request"

                if ev.StringInserts and len(ev.StringInserts) > 0:
                    try:
                        inserts = [str(s).strip() for s in ev.StringInserts if s]
                
                        # Look for human‑readable wake sources
                        readable = [s for s in inserts if any(
                            kw in s.lower() for kw in ["wake", "button", "lid", "keyboard", "mouse", "usb", "network", "timer"]
                        )]
                
                        if readable:
                            wake_reason = readable[0]
                        else:
                            # Fallback to executables or drivers
                            system_paths = [s for s in inserts if ".exe" in s.lower() or ".sys" in s.lower()]
                            if system_paths:
                                chosen = system_paths[0]
                                if "\\" in chosen:
                                    chosen = chosen.split("\\")[-1]
                                wake_reason = chosen
                            else:
                                wake_reason = inserts[-1]
                    except Exception:
                        pass
                    
                    reason_map = {
                        "svchost.exe": "Background Service (svchost.exe)",
                        "NgcIso.exe": "Windows Hello / Credential Service",
                        "wininit.exe": "System Initialization",
                    }
                    
                    if wake_reason in reason_map:
                        wake_reason = reason_map[wake_reason]



                all_events.append({
                    "Date": ev.TimeGenerated.strftime("%Y-%m-%d"),
                    "Wake Reason": wake_reason
                })

    if not all_events:
        return pd.DataFrame(columns=["Date", "Wake Events", "Day of Week", "Month", "Year", "Week Number", "Primary Wake Reason"])

    raw_df = pd.DataFrame(all_events)
    raw_df["Date"] = pd.to_datetime(raw_df["Date"])
    
    daily_counts = raw_df.groupby(["Date", "Wake Reason"]).size().reset_index(name="Event Count")
    top_reasons = daily_counts.sort_values("Event Count", ascending=False).groupby("Date").first().reset_index()
    
    final_daily = daily_counts.groupby("Date")["Event Count"].sum().reset_index(name="Wake Events")
    df = pd.merge(final_daily, top_reasons[["Date", "Wake Reason"]], on="Date", how="left")
    df = df.rename(columns={"Wake Reason": "Primary Wake Reason"})
    
    df = df.sort_values("Date", ascending=False)
    
    df["Day of Week"] = df["Date"].dt.day_name()
    df["Month"] = df["Date"].dt.month_name()
    df["Year"] = df["Date"].dt.year
    df["Week Number"] = df["Date"].dt.isocalendar().week
    
    df.attrs["raw_event_log"] = raw_df
    return df

def aggregate_weekly(df):
    if df.empty:
        return pd.DataFrame(columns=["Week Start (Sunday)", "Wake Events", "Display Week"])
    df["Week Start (Sunday)"] = df["Date"] - pd.to_timedelta((df["Date"].dt.weekday + 1) % 7, unit="D")
    weekly = df.groupby("Week Start (Sunday)")["Wake Events"].sum().reset_index()
    weekly = weekly.sort_values("Week Start (Sunday)", ascending=False).head(5)
    weekly["Display Week"] = weekly["Week Start (Sunday)"].dt.strftime("%b %d")
    return weekly

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("## ⚙️ Dashboard Controls")
    st.markdown("Configure your diagnostics window below.")
    days_to_fetch = st.slider("Historical Lookback (Days)", min_value=7, max_value=90, value=30, step=7)
    st.divider()
    st.markdown("**Status:** 🟢 Connected to local Windows Event Log")

# --- DATA PROCESSING ---
raw_data = get_wake_events(days_to_fetch)

if raw_data.empty:
    st.warning("⚠️ No wake events discovered in the specified Windows event log timeframe.")
else:
    # --- HEADER ---
    st.title("💻 Laptop Wake Insights Dashboard")
    
    # --- GLOSSARY & EXPLANATION BOX ---
    st.markdown("""
    <div class="explanation-box">
        <strong>🔍 What is a Wake Event?</strong><br>
        A wake event is recorded every single time your laptop transitions out of a low-power <strong>Sleep</strong> or <strong>Hibernate</strong> state back into an active operating state. 
        <br><br>
        <ul>
            <li><strong>Intentional Triggers:</strong> Opening your laptop lid, pressing the power button, clicking a connected mouse, or typing on an external keyboard.</li>
            <li><strong>Background Triggers:</strong> Automated Windows operating system tasks, scheduled software updates, anti-virus scans, or network card activity ("Wake-on-LAN").</li>
            <li><strong>Anomalies to Spot:</strong> High wake counts on days you did not use your machine often indicate background applications or buggy hardware drivers are keeping your machine awake in your bag.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # --- KPI METRIC CARDS ---
    total_wakes = int(raw_data["Wake Events"].sum())
    avg_wakes = round(raw_data["Wake Events"].mean(), 1)
    
    raw_history = raw_data.attrs.get("raw_event_log", pd.DataFrame(columns=["Wake Reason"]))
    if not raw_history.empty:
        top_overall_reason = raw_history["Wake Reason"].value_counts().idxmax()
        top_overall_reason = top_overall_reason.split('\\')[-1][:22]
    else:
        top_overall_reason = "None Detected"

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric(label="Total Logged Wakes", value=total_wakes)
    with m2:
        st.metric(label="Daily Average", value=avg_wakes)
    with m3:
        st.metric(label="Primary Wake Trigger", value=top_overall_reason)
        
    st.write(" ")

    # --- HISTORICAL CHARTS SIDE BY SIDE (RESTORED AS ORIGINAL) ---
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown("#### 📅 Daily Wake Distribution")
            viz_daily = raw_data.copy()
            viz_daily["Clean Date"] = viz_daily["Date"].dt.strftime("%b %d")
            
            chart1 = alt.Chart(viz_daily).mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4).encode(
                y=alt.Y('Clean Date:N', sort=None, title='Date'),
                x=alt.X('Wake Events:Q', title='Wake Count'),
                tooltip=['Clean Date', 'Wake Events', 'Day of Week', 'Primary Wake Reason'],
                color=alt.condition(
                    alt.datum['Wake Events'] >= 10, 
                    alt.value('#E74C3C'), 
                    alt.value('#3498DB')
                )
            ).properties(height=350)
            st.altair_chart(chart1, use_container_width=True)

    with col2:
        with st.container(border=True):
            st.markdown("#### 📊 Weekly Aggregated Views")
            weekly_data = aggregate_weekly(raw_data)
            
            chart2 = alt.Chart(weekly_data).mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4, color='#1ABC9C').encode(
                y=alt.Y('Display Week:N', sort=None, title='Week Starting (Sun)'),
                x=alt.X('Wake Events:Q', title='Total Wake Count'),
                tooltip=['Week Start (Sunday):T', 'Wake Events']
            ).properties(height=350)
            st.altair_chart(chart2, use_container_width=True)

    # --- NEW: DONUT CHART PLACED AS A FULL-WIDTH THIRD CHART BELOW ---
    with st.container(border=True):
        st.markdown("#### ⚙️ Global Root Cause Analysis")
        if not raw_history.empty:
            reason_counts = raw_history.groupby("Wake Reason").size().reset_index(name="Count")
            
            chart3 = alt.Chart(reason_counts).mark_arc(innerRadius=70, stroke='#fff').encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Wake Reason", type="nominal", 
                                scale=alt.Scale(scheme='tableau10'),
                                legend=alt.Legend(orient="right", columns=1, symbolType="circle")),
                tooltip=['Wake Reason', 'Count']
            ).properties(height=280)
            st.altair_chart(chart3, use_container_width=True)
        else:
            st.info("No source data available to compile a breakdown.")

    # --- ENHANCED DATA VIEW & DOWNLOAD ---
    with st.container(border=True):
        st.markdown("#### 📋 Diagnostic Event Ledger")
        
        st.dataframe(
            raw_data, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Date": st.column_config.DatetimeColumn(format="YYYY-MM-DD"),
                "Wake Events": st.column_config.NumberColumn(help="Number of tracked opening triggers"),
                "Primary Wake Reason": st.column_config.TextColumn(help="Most frequent trigger recorded on this specific calendar date")
            }
        )
        
        csv = raw_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Export Structural Ledger (CSV)",
            data=csv,
            file_name="laptop_wake_diagnostics.csv",
            mime="text/csv"
        )
