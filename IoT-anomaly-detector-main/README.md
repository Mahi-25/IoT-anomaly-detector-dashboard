IIoT Anomaly Detection & AI Optimization Dashboard
Author
Nazifa Tabassum

A fully interactive AI-driven Industrial IoT (IIoT) Monitoring System that detects anomalies in real-time, performs MILP-based task optimization, and visualizes system health through a modern Streamlit dashboard.

This project simulates an industrial environment where connected devices continuously send performance data (CPU usage, energy consumption, response time, etc.).
An embedded machine-learning model (KNN) identifies abnormal behavior, while a MILP optimizer reallocates device workloads dynamically to maintain efficiency.

 Features
 1. AI Anomaly Detection

K-Nearest Neighbors (KNN) model trained on synthetic IIoT sensor data.

Detects anomalies such as abnormal energy usage, CPU spikes, or response delays.

Real-time anomaly scoring and confidence metrics shown on the dashboard.

2. MILP Optimization Engine

Uses Mixed-Integer Linear Programming (PuLP) to schedule device tasks efficiently.

Balances CPU load, energy use, and deadlines.

Automatically re-optimizes when anomalies are detected.

 3. Real-Time Simulation

Simulates continuous data streams from virtual IIoT devices.

Integrates real-time scheduling threads and optimization cycles.

Optional emergency override button pauses the optimizer instantly.

 4. Modern Streamlit Dashboard

A rich interactive control center that provides:

 Device status visuals (CPU vs response plots, energy trends)

 Anomaly distribution pie chart

 AI Intelligence Panel (model confidence gauge, status indicator, trend chart)

 MILP allocation visualization via Sankey flow

 Sidebar controls for refresh rate, email alerts, Slack alerts, and optimizer pause

 5. AI Intelligence Panel

Displays live analytics of the ML model:

Model Confidence Gauge (70–99 %)

System Status Indicator (Stable 🟢 / Caution 🟡 / Critical 🔴)

Anomaly Trend Graph showing detection probabilities over time

 6. Alerts & Integrations

Email alerts for anomaly surges (SMTP configurable).

Slack notifications for live anomaly events.


 Tech Stack
Layer	Tools / Libraries
Language	Python 3.10 +
Frontend (UI)	Streamlit + Plotly + CSS custom themes
Machine Learning	scikit-learn (KNN Classifier)
Optimization	PuLP (MILP solver)
Data Handling	pandas, NumPy
Visualization	Plotly (Scatter, Pie, Line, Gauge, Sankey)
Alerts	smtplib (Email), slack_sdk (Slack)
 Installation & Setup
# 1. Clone the repository
git clone https://github.com/<your-username>/IoT-anomaly-detector-main.git
cd IoT-anomaly-detector-main

# 2. Create a virtual environment
python -m venv venv
.\venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run Streamlit dashboard
streamlit run app.py

How It Works

Dataset Generation
generate_dataset.py simulates multiple IIoT devices with randomized metrics.

Model Training
train_knn.py trains a KNN model to differentiate between normal and anomalous patterns.

Optimization Loop
milp_optimizer.py minimizes energy and time costs using MILP constraints.

Real-Time Monitoring
main_controller.py streams live data → AI detects anomalies → optimizer reassigns tasks.

Visualization & Alerts
app.py displays all data and sends alerts for anomaly surges.

 Example Dashboard Views

System Metrics Cards
Devices • Readings • Anomalies • Health %

AI Intelligence Panel
Model confidence gauge + status indicator + anomaly trend chart

Energy and Task Charts
Bar and scatter plots with real-time updates

Sankey Flow
Dynamic task reallocation based on optimizer outputs

 Future Improvements

Integration with real IoT devices (via MQTT / AWS IoT Core)

Deep learning models for advanced anomaly detection

Cloud deployment on Streamlit Cloud or AWS Lambda

Advanced analytics for predictive maintenance

