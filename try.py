import streamlit as st
import pandas as pd
import numpy as np
import time
import altair as alt
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Guardian FinTech | Live Monitor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- STYLING (HACKATHON DARK MODE) ---
st.markdown("""
<style>
    [data-testid="stMetricValue"] { font-size: 2rem; color: #4ade80; }
    .fraud-alert { color: #ff4b4b; font-weight: bold; font-size: 1.2rem; border: 2px solid #ff4b4b; padding: 10px; border-radius: 5px; animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
</style>
""", unsafe_allow_html=True)

# --- MOCK DATA GENERATOR ---
MERCHANTS = ["Starbucks", "Uber", "Amazon AWS", "Target", "Shell Station", "Netflix"]
LOCATIONS = ["New York, US", "San Francisco, US", "Austin, US", "London, UK", "Moscow, RU"]
CATEGORIES = ["Food", "Transport", "Tech", "Shopping", "Utility"]

def generate_transaction():
    """Simulates receiving a JSON payload from a card terminal."""
    is_anomaly = np.random.random() < 0.15 # 15% chance of weird behavior
    
    if is_anomaly:
        merchant = "Unknown Crypto Exchange"
        amount = np.random.uniform(500, 2000)
        location = "Moscow, RU" # Suspicious location
        risk_score = np.random.uniform(0.8, 0.99)
    else:
        merchant = np.random.choice(MERCHANTS)
        amount = np.random.uniform(5, 150)
        location = "New York, US"
        risk_score = np.random.uniform(0.01, 0.2)
        
    return {
        "timestamp": datetime.now(),
        "merchant": merchant,
        "amount": round(amount, 2),
        "location": location,
        "category": np.random.choice(CATEGORIES),
        "risk_score": round(risk_score, 2),
        "status": "BLOCKED" if risk_score > 0.75 else "APPROVED"
    }

# --- SESSION STATE ---
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["timestamp", "merchant", "amount", "location", "category", "risk_score", "status"])

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Simulation Control")
    simulation_speed = st.slider("Transaction Speed (sec)", 0.1, 2.0, 1.0)
    st.divider()
    
    # Manual Override (The "Kill Switch" Feature)
    st.subheader("Manual Override")
    if st.button("🚨 TRIGGER ATTACK (DEMO)", type="primary"):
        # Force insert a fraud case immediately
        fraud_tx = {
            "timestamp": datetime.now(),
            "merchant": "EVIL CORP HACKER",
            "amount": 9999.99,
            "location": "Dark Web Proxy",
            "category": "High Risk",
            "risk_score": 0.99,
            "status": "BLOCKED"
        }
        st.session_state.data = pd.concat([pd.DataFrame([fraud_tx]), st.session_state.data], ignore_index=True)
    
    if st.button("🛑 FREEZE ALL CARDS"):
        st.error("SYSTEM LOCKDOWN INITIATED. ALL CARDS DECLINED.")
        st.stop()

# --- MAIN DASHBOARD LAYOUT ---
st.title("🛡️ Guardian AI: Real-Time Fraud Monitor")
st.markdown("Processing live transaction stream via **FastAPI** + **Isolation Forest**...")

# Layout: 3 Columns for KPIs
kpi1, kpi2, kpi3 = st.columns(3)

# Placeholders for live updates
chart_placeholder = st.empty()
alert_placeholder = st.empty()
table_placeholder = st.empty()

# --- REAL-TIME LOOP ---
while True:
    # 1. Generate Data
    new_tx = generate_transaction()
    new_df = pd.DataFrame([new_tx])
    
    # 2. Update State (Keep last 50 records)
    st.session_state.data = pd.concat([new_df, st.session_state.data], ignore_index=True).head(50)
    
    # 3. Calculate Metrics
    df = st.session_state.data
    total_spend = df[df['status'] == 'APPROVED']['amount'].sum()
    fraud_attempts = len(df[df['status'] == 'BLOCKED'])
    last_risk = df.iloc[0]['risk_score']
    
    # 4. Render KPIs
    with kpi1:
        st.metric("Total Approved Volume", f"${total_spend:,.2f}")
    with kpi2:
        st.metric("Fraud Attempts Blocked", f"{fraud_attempts}", delta_color="inverse")
    with kpi3:
        st.metric("Live Risk Score", f"{last_risk:.2f}", delta=f"{'CRITICAL' if last_risk > 0.75 else 'SAFE'}", delta_color="inverse")

    # 5. Render Alert Box (If Fraud)
    with alert_placeholder:
        if new_tx['status'] == 'BLOCKED':
            st.markdown(f"""
            <div class="fraud-alert">
                ⚠️ FRAUD DETECTED: {new_tx['merchant']} (${new_tx['amount']}) in {new_tx['location']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.write("") # Clear alert

    # 6. Render Chart (Spending vs Time)
    with chart_placeholder:
        chart = alt.Chart(df).mark_circle(size=60).encode(
            x='timestamp',
            y='amount',
            color=alt.Color('status', scale=alt.Scale(domain=['APPROVED', 'BLOCKED'], range=['#4ade80', '#ff4b4b'])),
            tooltip=['merchant', 'amount', 'location']
        ).properties(height=350).interactive()
        st.altair_chart(chart, use_container_width=True)

    # 7. Render Data Table (Styled)
    with table_placeholder:
        st.subheader("Live Transaction Ledger")
        
        # Color the rows based on status
        def highlight_fraud(row):
            return ['background-color: #ff4b4b; color: white' if row['status'] == 'BLOCKED' else '' for _ in row]

        st.dataframe(
            df.style.apply(highlight_fraud, axis=1),
            use_container_width=True,
            column_config={
                "timestamp": st.column_config.DatetimeColumn("Time", format="h:mm:ss a"),
                "amount": st.column_config.NumberColumn("Amount", format="$%.2f"),
                "risk_score": st.column_config.ProgressColumn("AI Confidence", min_value=0, max_value=1, format="%.2f"),
            }
        )

    # Loop delay
    time.sleep(simulation_speed)