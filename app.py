import streamlit as st

# Set page config (must be the first Streamlit command)
st.set_page_config(
    page_title="BantuanNow",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Import necessary modules after setting page config
from database import Database
import pandas as pd
from pages import adminscanqr, addintoinventory, inventory_dashboard, dashboard, donations, donationtrack, alerts, qr_manager, ngo_supplies, center_demands

# Initialize database
db = Database()

# Title
st.title("BantuanNow: A Centralized Real-Time Monitoring and Aid Distribution Platform for Malaysian Flood Shelters")

# User Type Selection (Now inside the main page)
user_type = st.radio("Select User Type:", ["👤 General User", "🌐 NGO", "🛡️ Admin"], horizontal=True)

# Navigation inside homepage
if user_type == "👤 General User":
    page = st.radio(
        "Select a page:",
        ["📈 Dashboard", "💝 Donations", "⚠️ Alerts", "📌 Donation Tracking"],
        key="user_page_selectbox"
    )
    
    # Display the selected page
    if page == "📈 Dashboard":
        dashboard.show(db)
    elif page == "💝 Donations":
        donations.show(db)
    elif page == "⚠️ Alerts":
        alerts.show(db)
    elif page == "📌 Donation Tracking":
        donationtrack.show(db)

elif user_type == "🌐 NGO":
    page = st.radio(
        "Select a page:",
        ["📦 Inventory Management", "📥 Add Supplies", "𝄃𝄃𝄂𝄂𝄀𝄁𝄃𝄂𝄂𝄃 QR Management", "⚠️ Alerts"],
        key="page_selectbox"
    )
    if page == "📦 Inventory Management":
        ngo_supplies.show(db)
    elif page == "📥 Add Supplies":
        addintoinventory.show(db)
    elif page == "𝄃𝄃𝄂𝄂𝄀𝄁𝄃𝄂𝄂𝄃 QR Management":
        qr_manager.show(db)
    elif page == "⚠️ Alerts":
        alerts.show(db)

elif user_type == "🛡️ Admin":
    page = st.radio(
        "Select a page",
        ["📈 Dashboard", "🙇 Demand Request", "✒️ Register Supply Items", "⚠️ Alerts"],
        key="admin_page_selectbox"
    )
    
    if page == "📈 Dashboard":
        dashboard.show(db)
    elif page == "🙇 Demand Request":
        center_demands.show(db)
    elif page == "✒️ Register Supply Items":
        adminscanqr.show(db)
    elif page == "⚠️ Alerts":
        alerts.show(db)