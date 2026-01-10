import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)
api_key = os.getenv("OPENROUTER_API_KEY")


st.set_page_config(page_title="CrowdSpot", layout="wide")
st.title("CrowdSpot - Crowd Intelligence Dashboard")


frames_df = pd.read_csv("results/frames.csv")
anomalies_df = pd.read_csv("results/anomalies.csv")

alerts_df = None
alerts_path = Path("results/alerts.csv")
if alerts_path.exists() and alerts_path.stat().st_size > 0:
    alerts_df = pd.read_csv(alerts_path)

baselines = pd.read_csv("data/baselines.csv")
baseline_mean = baselines.loc[
    baselines["metric"] == "baseline_mean", "value"
].values[0]
baseline_std = baselines.loc[
    baselines["metric"] == "baseline_std", "value"
].values[0]


# Store full path internally, but expose clean ID to UI
frames_df["image_id_clean"] = frames_df["image_id"].apply(
    lambda x: os.path.basename(x)
)

all_image_ids = sorted(frames_df["image_id_clean"].unique())


st.subheader("Zone Overview")

zone_stats = []
for img_id in all_image_ids[:10]:  # show first 10 only
    zone_data = frames_df[frames_df["image_id_clean"] == img_id]

    density_level = zone_data["density_level"].iloc[0]

    alert_count = 0
    if alerts_df is not None:
        alert_count = len(
            alerts_df[alerts_df["zone"].str.contains(img_id, na=False)]
        )

    zone_stats.append({
        "Zone": img_id,
        "Density": density_level,
        "Trend": "→",  # static images, no temporal trend
        "Alerts": alert_count
    })

st.dataframe(pd.DataFrame(zone_stats), use_container_width=True)


st.subheader("Density Distribution")

fig = go.Figure()
fig.add_trace(go.Histogram(
    x=frames_df["global_density"],
    nbinsx=50,
    marker_color="rgba(0, 150, 255, 0.7)"
))

fig.add_vline(
    x=baseline_mean,
    line_dash="dash",
    line_color="green",
    annotation_text="Baseline"
)
fig.add_vline(
    x=baseline_mean + baseline_std,
    line_dash="dash",
    line_color="orange"
)
fig.add_vline(
    x=baseline_mean - baseline_std,
    line_dash="dash",
    line_color="orange"
)

fig.update_layout(
    title="Global Density Distribution vs Baseline",
    xaxis_title="Global Density",
    yaxis_title="Frame Count"
)

st.plotly_chart(fig, use_container_width=True)


st.subheader("Active Alerts")

if alerts_df is not None and len(alerts_df) > 0:
    for _, alert in alerts_df.head(10).iterrows():
        col1, col2, col3 = st.columns(3)

        with col1:
            icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(
                alert["severity"], "⚪"
            )
            st.write(f"{icon} **{alert['severity']}**")

        with col2:
            st.write(alert["zone"])

        with col3:
            st.write(f"{int(alert['person_count'])} people")

        st.caption(alert.get("operator_note", ""))
        st.divider()
else:
    st.info("No active alerts")

#summary
st.subheader("Generate Summary")

selected_image = st.selectbox(
    "Select Image ID (type to search)",
    all_image_ids
)

if st.button("Generate Summary"):
    if not api_key:
        st.error("OPENROUTER_API_KEY not found in .env")
    else:
        try:
            from src.rag import RAGSummary

            zone_data = frames_df[
                frames_df["image_id_clean"] == selected_image
            ]

            current_density = zone_data["person_count"].iloc[0]
            density_level = zone_data["density_level"].iloc[0]

            z_score = (
                (current_density - baseline_mean) / baseline_std
                if baseline_std > 0 else 0
            )

            rag = RAGSummary(api_key=api_key)
            summary = rag.generate_summary(
    selected_image,
    person_count=zone_data["person_count"].iloc[0],
    density_level=zone_data["density_level"].iloc[0],
    baseline_mean=baseline_mean,
    baseline_std=baseline_std,
    z_score=z_score
)



            st.success(summary)

        except Exception as e:
            st.error(f"Error generating summary: {str(e)}")
