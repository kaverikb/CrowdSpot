import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="CrowdSpot", layout="wide")
st.title("CrowdSpot - Crowd Intelligence Dashboard")

# Load alerts data
alerts_file = Path("results/alerts_timeline.json")
if not alerts_file.exists():
    st.error("alerts_timeline.json not found. Run video processing first.")
    st.stop()

with open(alerts_file) as f:
    data = json.load(f)

baseline = data.get("baseline", 0)
peak = data.get("peak", 0)
alerts = data.get("alerts", [])

# Convert to DataFrame for easier manipulation
alerts_df = pd.DataFrame(alerts)
if len(alerts_df) > 0:
    alerts_df["count"] = alerts_df["count"].astype(int)
    alerts_df["deviation"] = ((alerts_df["count"] - baseline) / baseline * 100).round(2)
else:
    alerts_df = pd.DataFrame()

#Metrics
st.subheader("Operational Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Baseline", f"{baseline:.0f} people")

with col2:
    st.metric("Peak", f"{peak:.0f} people")

with col3:
    st.metric("Total Alerts", len(alerts))

with col4:
    avg_count = alerts_df["count"].mean() if len(alerts_df) > 0 else baseline
    st.metric("Avg Count", f"{avg_count:.0f} people")

st.divider()

#Charts
st.subheader("Analysis Charts")

chart_col1, chart_col2 = st.columns(2)

# Chart 1: Count over time
with chart_col1:
    if len(alerts_df) > 0:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=alerts_df["timestamp"],
            y=alerts_df["count"],
            mode="lines+markers",
            name="Count",
            line=dict(color="blue", width=2),
            marker=dict(size=6)
        ))
        fig1.add_hline(y=baseline, line_dash="dash", line_color="green", annotation_text="Baseline")
        fig1.add_hline(y=peak, line_dash="dash", line_color="red", annotation_text="Peak")
        fig1.update_layout(
            title="Crowd Count Over Time",
            xaxis_title="Time (seconds)",
            yaxis_title="Count",
            hovermode="x unified"
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("No alert data to chart")

# Chart 2: Deviation trend
with chart_col2:
    if len(alerts_df) > 0:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=alerts_df["timestamp"],
            y=alerts_df["deviation"],
            fill="tozeroy",
            name="Deviation %",
            line=dict(color="orange"),
            fillcolor="rgba(255, 165, 0, 0.3)"
        ))
        fig2.add_hline(y=0, line_dash="dash", line_color="gray")
        fig2.update_layout(
            title="Deviation from Baseline (%)",
            xaxis_title="Time (seconds)",
            yaxis_title="Deviation %",
            hovermode="x unified"
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No alert data to chart")

st.divider()

#Alert Notif
st.subheader("Alert Notifications")

if len(alerts) > 0:
    latest_alert = alerts[0]
    
    col1, col2 = st.columns(2)
    
    # Control Room Notification
    with col1:
        st.write("**Control Room Notification**")
        with st.container(border=True):
            st.write(f"🚨 **ALERT**")
            st.write(f"Timestamp: {latest_alert['timestamp']:.2f}s")
            st.write(f"Location: Shibuya Crossing")
            st.write(f"Count: {latest_alert['count']} people")
            st.write(f"Deviation: {((latest_alert['count'] - baseline) / baseline * 100):.2f}%")
            st.write(f"Status: ⚠️ Monitor")
    
    # Patrol Unit Notification
    with col2:
        st.write("**Nearest Patrol Unit Alert**")
        with st.container(border=True):
            st.write(f"📡 **DISPATCH**")
            st.write(f"Unit ID: PATROL_001")
            st.write(f"Location: Shibuya Crossing")
            st.write(f"Priority: MEDIUM")
            st.write(f"Action: Investigate crowd surge")
            st.write(f"ETA: 5 minutes")
else:
    st.info("No active alerts")

#Alert Timeline
st.subheader("Alert Timeline")

if len(alerts_df) > 0:
    # Display as table
    display_df = alerts_df[["timestamp", "count", "deviation"]].copy()
    display_df["timestamp"] = display_df["timestamp"].round(2)
    display_df.columns = ["Time (s)", "Count", "Deviation (%)"]
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.write("**Alert Details:**")
    
    # Pagination
    if "alerts_shown" not in st.session_state:
        st.session_state.alerts_shown = 10
    
    # Display alerts in batches
    for idx in range(min(st.session_state.alerts_shown, len(alerts))):
        alert = alerts[idx]
        with st.expander(f"Alert {idx + 1} - {alert['timestamp']:.2f}s"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Frame:** {alert['frame']}")
                st.write(f"**Count:** {alert['count']} people")
                st.write(f"**Deviation:** {((alert['count'] - baseline) / baseline * 100):.2f}%")
            
            with col2:
                pattern = alert.get("pattern", {})
                st.write(f"**Baseline:** {pattern.get('avg_people', 'N/A')}")
                st.write(f"**Peak:** {pattern.get('peak_people', 'N/A')}")
                st.write(f"**Source:** {pattern.get('baseline_source', 'N/A')}")
            
            st.write(f"**LLM Summary:**")
            st.write(alert.get("llm", "N/A"))
    
    # See more button
    if st.session_state.alerts_shown < len(alerts):
        if st.button("See More Alerts"):
            st.session_state.alerts_shown += 10
            st.rerun()
    
    if st.session_state.alerts_shown >= len(alerts):
        st.caption(f"Showing all {len(alerts)} alerts")
else:
    st.info("No alerts detected. Crowd remained within normal parameters.")