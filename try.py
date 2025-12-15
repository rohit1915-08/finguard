import streamlit as st
import pandas as pd
import numpy as np
import random
import time

# Page configuration
st.set_page_config(
    page_title="FinGuard AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header
st.markdown(
    """
    <h1 style="text-align:center;">FinGuard AI</h1>
    <h4 style="text-align:center; color:gray;">
    Real-Time Financial Protection Powered by Artificial Intelligence
    </h4>
    """,
    unsafe_allow_html=True
)

st.divider()

# Sidebar controls
st.sidebar.title("Simulation Controls")
simulate_fraud = st.sidebar.checkbox("Simulate high-risk transaction")
run_demo = st.sidebar.button("Run transaction analysis")

# Helper functions
def categorize_expense(merchant):
    categories = {
        "Amazon": "Shopping",
        "Flipkart": "Shopping",
        "Swiggy": "Food",
        "Uber": "Travel",
        "Netflix": "Subscription",
        "Unknown Merchant": "Others"
    }
    return categories.get(merchant, "Others")

def analyze_transaction(amount, merchant, location):
    risk_score = 0
    reasons = []

    if amount > 10000:
        risk_score += 40
        reasons.append("Transaction amount significantly higher than usual")

    if merchant == "Unknown Merchant":
        risk_score += 30
        reasons.append("Merchant not seen in user history")

    if location == "Foreign Location":
        risk_score += 30
        reasons.append("Transaction location differs from normal usage")

    return min(risk_score, 100), reasons

def generate_transaction(fraud=False):
    merchants = ["Amazon", "Flipkart", "Swiggy", "Uber", "Netflix", "Unknown Merchant"]
    locations = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Foreign Location"]

    amount = random.randint(100, 3000)
    merchant = random.choice(merchants)
    location = random.choice(locations)

    if fraud:
        amount = random.randint(15000, 50000)
        merchant = "Unknown Merchant"
        location = "Foreign Location"

    risk_score, reasons = analyze_transaction(amount, merchant, location)

    return {
        "Amount": amount,
        "Merchant": merchant,
        "Location": location,
        "Category": categorize_expense(merchant),
        "Risk Score": risk_score,
        "Reasons": reasons
    }

# Dashboard layout
left, right = st.columns(2)

with left:
    st.subheader("Live Transaction Feed")
    st.write("Transactions are analyzed instantly as they occur.")

with right:
    st.subheader("AI Risk Analysis")
    st.write("Each transaction is scored using behavioral analysis.")

st.divider()

# Run simulation
if run_demo:
    with st.spinner("Processing transaction..."):
        time.sleep(1.2)

    transaction = generate_transaction(simulate_fraud)

    st.subheader("Transaction Details")
    st.json({
        "Amount (INR)": transaction["Amount"],
        "Merchant": transaction["Merchant"],
        "Location": transaction["Location"],
        "Category": transaction["Category"]
    })

    st.subheader("Fraud Risk Score")
    st.progress(transaction["Risk Score"])

    if transaction["Risk Score"] < 30:
        st.success("Transaction approved")
    elif transaction["Risk Score"] < 70:
        st.warning("Suspicious transaction. User confirmation required")
    else:
        st.error("Transaction blocked due to high fraud risk")

    st.subheader("AI Explanation")
    if transaction["Reasons"]:
        for reason in transaction["Reasons"]:
            st.write("- " + reason)
    else:
        st.write("Transaction aligns with normal user behavior")

# Expense summary
st.divider()
st.subheader("Automated Expense Summary")

expense_data = pd.DataFrame({
    "Category": ["Food", "Travel", "Shopping", "Subscriptions", "Others"],
    "Monthly Spend (INR)": [4200, 3100, 6800, 999, 1200]
})

st.bar_chart(expense_data.set_index("Category"))

# Footer
st.divider()
st.caption(
    "FinGuard AI prototype demonstrating real-time transaction intelligence, "
    "fraud risk analysis, and automated expense categorization."
)
