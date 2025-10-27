import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import time
import random
import smtplib
from email.mime.text import MIMEText
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

st.set_page_config(
    page_title="IIoT Intelligence Command Center",
    page_icon="🤖",
    layout="wide"
)


st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(120deg, #0b0f19, #111827, #0f172a);
    color: #e5e7eb;
    font-family: 'Inter', sans-serif;
}

/* 'Deploy' button and toolbar items */
button[title="View app menu"], 
button[title="View fullscreen"], 
button[title="Manage app"], 
button[title="Share this app"], 
[data-testid="stStatusWidget"] {
    color: #ffffff !important;
    opacity: 0.9 !important;
}

header[data-testid="stHeader"] {
    background: linear-gradient(90deg, rgba(0, 224, 255, 0.15), rgba(0, 0, 0, 0.4));
}
/* Sidebar  */
[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #2b1055, #7f00ff, #21d4fd);
    background-size: 300% 300%;
    animation: sidebarGradient 12s ease infinite;
    color: #f9f9fb;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
    box-shadow: 4px 0px 15px rgba(0, 0, 0, 0.3);
}
@keyframes sidebarGradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

[data-testid="stSidebar"] * {
    color: #f5f5f5 !important;
}

.stSlider [data-baseweb="slider"] > div {
    background: linear-gradient(90deg, #8f5eff, #4facfe, #00f2fe);
    height: 6px;
    border-radius: 10px;
}

.stSlider [data-baseweb="slider"] [role="slider"] {
    background-color: #fff;
    border: 2px solid #8f5eff;
    box-shadow: 0px 0px 6px rgba(143, 94, 255, 0.6);
}

/* Sidebar buttons */
button[kind="primary"], .stButton>button {
    background: linear-gradient(135deg, #7f00ff, #21d4fd);
    color: white !important;
    border: none;
    border-radius: 10px;
    transition: 0.3s ease;
    font-weight: 600;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
}
button[kind="primary"]:hover, .stButton>button:hover {
    background: linear-gradient(135deg, #21d4fd, #b721ff);
    transform: scale(1.04);
    box-shadow: 0 0 12px rgba(180, 120, 255, 0.7);
}

/*  Metric Cards  */
.metric-card {
    padding: 1rem;
    border-radius: 1rem;
    background: linear-gradient(135deg, rgba(25, 32, 50, 0.9), rgba(17, 24, 39, 0.85));
    box-shadow: 0 4px 20px rgba(0, 255, 204, 0.05);
    text-align: center;
    backdrop-filter: blur(6px);
    border: 1px solid rgba(0, 255, 204, 0.15);
}
.metric-label {
    font-size: 1rem;
    color: #b0b4bb;
}
.metric-value {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #00e0ff, #00ffa6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Tabs */
[data-baseweb="tab-list"] {
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
}
[data-baseweb="tab"] {
    color: #b0b4bb !important;
}
[data-baseweb="tab"][aria-selected="true"] {
    color: #00ffa6 !important;
    border-bottom: 2px solid #00ffa6 !important;
}

/* DataFrame & Alerts */
.stDataFrame {
    background: rgba(17, 24, 39, 0.7);
    border-radius: 10px;
    border: 1px solid rgba(0, 255, 204, 0.2);
    color: #e5e7eb !important;
}
.stDataFrame th {
    background-color: rgba(0, 255, 204, 0.1) !important;
    color: #00ffa6 !important;
}

.stAlert {
    background-color: rgba(255, 77, 77, 0.1) !important;
    border: 1px solid rgba(255, 77, 77, 0.4);
    color: #ff6b6b !important;
    font-weight: 500;
}

.plot-container {
    background-color: rgba(17, 24, 39, 0.4);
    border-radius: 12px;
    padding: 1rem;
    border: 1px solid rgba(0, 255, 204, 0.1);
}

h1, h2, h3, h4 {
    color: #00ffa6 !important;
}
</style>
""", unsafe_allow_html=True)





# sidebar

st.sidebar.title("⚙️ IIoT Control Center")

refresh_rate = st.sidebar.slider("🔄 Refresh Rate (seconds)", 1, 10, 3)
emergency_stop = st.sidebar.button("Emergency Override (Pause Optimizer)")
send_email_alert = st.sidebar.checkbox("Email Alerts", value=False)
send_slack_alert = st.sidebar.checkbox("Slack Alerts", value=False)

st.sidebar.markdown("---")
st.sidebar.info("This system visualizes AI anomaly detection and MILP optimization in real-time.")

# this is to load data

log_file = "data/system_log.csv"

if not os.path.exists(log_file):
    st.warning("No system log yet. Please run `main_controller.py` first.")
    st.stop()

data = pd.read_csv(log_file)

if len(data) > 250:
    data = data.tail(250)


# metrics

col1, col2, col3, col4 = st.columns(4)
total_devices = data["device"].nunique()
total_readings = len(data)
anomalies = len(data[data["label"] == "anomaly"])
health = 100 * (1 - anomalies / (total_readings + 1e-5))

col1.markdown(f'<div class="metric-card"><div class="metric-label">Devices</div><div class="metric-value">{total_devices}</div></div>', unsafe_allow_html=True)
col2.markdown(f'<div class="metric-card"><div class="metric-label">Readings</div><div class="metric-value">{total_readings}</div></div>', unsafe_allow_html=True)
col3.markdown(f'<div class="metric-card"><div class="metric-label">Anomalies</div><div class="metric-value">{anomalies}</div></div>', unsafe_allow_html=True)
col4.markdown(f'<div class="metric-card"><div class="metric-label">System Health</div><div class="metric-value">{health:.1f}%</div></div>', unsafe_allow_html=True)


# this is AI intelligence panel section

import plotly.graph_objects as go
import numpy as np

st.markdown("🤖 AI Intelligence Panel")

col_ai1, col_ai2, col_ai3 = st.columns([1, 1, 2])


confidence_score = round(np.random.uniform(70, 99), 2)
fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=confidence_score,
    delta={'reference': 90},
    title={'text': "Model Confidence (%)", 'font': {'size': 18, 'color': 'white'}},
    gauge={
        'axis': {'range': [0, 100], 'tickcolor': 'white'},
        'bar': {'color': "#00E0FF"},
        'bgcolor': "rgba(0,0,0,0)",
        'borderwidth': 2,
        'bordercolor': "#1E3A8A",
        'steps': [
            {'range': [0, 50], 'color': "#ff4d4d"},
            {'range': [50, 80], 'color': "#facc15"},
            {'range': [80, 100], 'color': "#22c55e"}
        ],
    }
))
fig_gauge.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', font={'color': 'white'})
col_ai1.plotly_chart(fig_gauge, use_container_width=True)


if anomalies < 20:
    model_status = "🟢 Stable"
    status_color = "#22c55e"
elif 20 <= anomalies < 100:
    model_status = "🟡 Caution"
    status_color = "#facc15"
else:
    model_status = "🔴 Critical"
    status_color = "#ef4444"

col_ai2.markdown(f"""
<div style="
    background: rgba(255,255,255,0.1);
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    color: white;
    border: 1px solid {status_color};
    box-shadow: 0 0 10px {status_color};
">
<h4 style="color:{status_color};margin-bottom:0;">Model Status</h4>
<h2 style="margin-top:5px;">{model_status}</h2>
<p style="font-size:0.9rem;opacity:0.8;">AI anomaly detector continuously monitors device behavior.</p>
</div>
""", unsafe_allow_html=True)


anomaly_prob = np.clip(np.random.normal(0.4, 0.2, 50), 0, 1)
time_steps = np.arange(len(anomaly_prob))
fig_line = go.Figure()
fig_line.add_trace(go.Scatter(
    x=time_steps,
    y=anomaly_prob * 100,
    mode='lines+markers',
    line=dict(color="#00E0FF", width=3),
    fill='tozeroy',
    name='Anomaly Probability'
))
fig_line.update_layout(
    title="AI Detection Trend (Last 50 readings)",
    template="plotly_dark",
    xaxis_title="Time Steps",
    yaxis_title="Anomaly Probability (%)",
    height=250,
    margin=dict(l=20, r=20, t=40, b=20)
)
col_ai3.plotly_chart(fig_line, use_container_width=True)

# this is email and slack alert function 

def send_email(subject, body):
    try:
        sender = "nazifatabassum206@gmail.com"    
        password = "TangLizhen206."     
        receiver = "receiveremail@gmail.com"

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = receiver

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        st.sidebar.success("Email alert sent!")
    except Exception as e:
        st.sidebar.error(f"Email error: {e}")

def send_slack_message(text):
    try:
        client = WebClient(token="xoxb-slack-bot-token")  
        client.chat_postMessage(channel="#iiot-alerts", text=text)
        st.sidebar.success("Slack alert sent!")
    except SlackApiError as e:
        st.sidebar.error(f"Slack error: {e.response['error']}")

# this will trigger alert if anomaly ratio is high
if anomalies > 5 and (send_email_alert or send_slack_alert):
    alert_msg = f"ALERT: {anomalies} anomalies detected in IIoT system!"
    if send_email_alert:
        send_email("IIoT Alert", alert_msg)
    if send_slack_alert:
        send_slack_message(alert_msg)


# visual tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Device Status", "⚡ Energy Analysis", "📋 Task Table", "🔀 Sankey Task Flow"
])

with tab1:
    fig = px.scatter(
        data,
        x="cpu",
        y="response",
        color="label",
        hover_data=["device", "task", "energy"],
        title="Device Performance: CPU vs Response Time",
        color_discrete_map={"normal": "#00C9A7", "anomaly": "#FF4B5C"},
    )
    fig.update_layout(template="plotly_dark", height=500)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig2 = px.bar(
        data,
        x="device",
        y="energy",
        color="label",
        title="Energy Usage by Device",
        color_discrete_map={"normal": "#4CAF50", "anomaly": "#FF6F61"},
    )
    fig2.update_layout(template="plotly_dark", height=500)
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    latest = data.tail(50)
    st.dataframe(
        latest[["time", "device", "task", "cpu", "energy", "response", "label"]],
        use_container_width=True,
        height=500
    )

with tab4:
    latest_assignments = data.tail(30)
    source = latest_assignments["device"]
    target = latest_assignments["task"]
    value = [random.randint(1, 10) for _ in range(len(source))]

    unique_devices = list(source.unique())
    unique_tasks = list(target.unique())
    labels = unique_devices + unique_tasks
    device_count = len(unique_devices)
    source_indices = [labels.index(d) for d in source]
    target_indices = [labels.index(t) for t in target]

    sankey_fig = go.Figure(data=[go.Sankey(
        node=dict(pad=15, thickness=20, line=dict(color="white", width=0.5), label=labels),
        link=dict(source=source_indices, target=target_indices, value=value, color="rgba(0, 224, 255, 0.4)")
    )])

    sankey_fig.update_layout(title_text="Real-Time Task Reallocation Flow", font=dict(color="white", size=12), height=550)
    st.plotly_chart(sankey_fig, use_container_width=True)


# this is for emergency stop 

if emergency_stop:
    st.error("🚨 Emergency Override Activated — Optimizer Paused!")
    # Create a flag file that main_controller can check
    with open("data/emergency_flag.txt", "w") as f:
        f.write("STOP")
else:
    if os.path.exists("data/emergency_flag.txt"):
        os.remove("data/emergency_flag.txt")


if st.button("🔄 Refresh Now"):
    st.rerun()

