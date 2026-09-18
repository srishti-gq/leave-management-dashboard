import streamlit as st

st.title("Leave Management Dashboard - Test")

name = st.text_input("Enter your name")

if st.button("Say Hello"):
    st.write(f"Hello, {name}! 👋")