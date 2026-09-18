import streamlit as st
import pandas as pd

st.set_page_config(page_title="Leave Management Dashboard", layout="wide")

# --- Sidebar navigation (not clickable/functional yet — that comes later) ---
st.sidebar.title("📋 Leave Management")
st.sidebar.radio("Navigate", ["Dashboard", "Apply for Leave", "My Leave Requests", "Profile"])

# --- Page header ---
st.title("Good Morning, Srishti! 👋")
st.write("Here's a quick overview of your leave requests and status.")

# --- Stat cards ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Pending", 1)
col2.metric("Approved", 3)
col3.metric("Rejected", 0)
col4.metric("Total Requests", 4)

# --- Leave requests table (fake placeholder data for now) ---
st.subheader("My Leave Requests")

leave_requests = [
    {"Request ID": "LR004", "Leave Type": "Personal", "From": "20 Sep 2025", "To": "22 Sep 2025", "Reason": "Personal work", "Status": "Pending", "Applied On": "16 Sep 2025"},
    {"Request ID": "LR003", "Leave Type": "Personal", "From": "10 Sep 2025", "To": "12 Sep 2025", "Reason": "Family function", "Status": "Approved", "Applied On": "08 Sep 2025"},
    {"Request ID": "LR002", "Leave Type": "Sick", "From": "02 Sep 2025", "To": "03 Sep 2025", "Reason": "Health issue", "Status": "Approved", "Applied On": "01 Sep 2025"},
    {"Request ID": "LR001", "Leave Type": "Personal", "From": "25 Aug 2025", "To": "26 Aug 2025", "Reason": "Personal work", "Status": "Approved", "Applied On": "24 Aug 2025"},
]

df = pd.DataFrame(leave_requests)
st.dataframe(df, use_container_width=True)