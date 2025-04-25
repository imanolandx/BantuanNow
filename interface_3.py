import streamlit as st
import pandas as pd
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import qrcode
from io import BytesIO
from PIL import Image

# Set up the page configuration for a cleaner, centered interface
st.set_page_config(page_title="Donation Form", page_icon="🛍️", layout="centered")

# Title and introduction section
st.markdown("# 🛍️ Donation Form")
st.markdown("### Please fill in the details below if you wish to donate something.")
st.markdown("---")

# Columns for donor information to make the form more structured
col1, col2 = st.columns(2)

with col1:
    donor_name = st.text_input("NGO's Name", placeholder="Enter names *")
    donor_email = st.text_input("Email Address", placeholder="Enter your email *")

with col2:
    donor_phone = st.text_input("Phone Number", placeholder="Enter your contact number")
    # Initialize as empty string, to avoid "list" issue if not selected
    donation_item = "" 

# Donation category section with predefined essential items
st.markdown("### What items would you like to donate?")

donation_category = st.selectbox(
    "Choose a category of items you wish to donate:",
    [
        "Food & Water", 
        "Clothing", 
        "Hygiene & Sanitation", 
        "Medical Supplies", 
        "Shelter & Sleeping Essentials", 
        "Baby & Elderly Care", 
        "Safety & Emergency Items"
    ]
)

# Based on the selected category, dynamically show options for the item
if donation_category == "Food & Water":
    donation_item = st.multiselect(
        "Select items for donation:",
        ["Non-perishable Food", "Clean Drinking Water", "Baby Formula", "Utensils"]
    )

elif donation_category == "Clothing":
    donation_item = st.multiselect(
        "Select items for donation:",
        ["Dry Clothes", "Blankets", "Towels", "Shoes"]
    )

elif donation_category == "Hygiene & Sanitation":
    donation_item = st.multiselect(
        "Select items for donation:",
        ["Soap", "Toothbrush", "Toothpaste", "Sanitary Pads", "Diapers", "Hand Sanitizer", "Face Masks"]
    )

elif donation_category == "Medical Supplies":
    donation_item = st.multiselect(
        "Select items for donation:",
        ["First Aid Kits", "Pain Relievers", "Prescribed Medication", "Mosquito Repellent", "Disinfectants"]
    )

elif donation_category == "Shelter & Sleeping Essentials":
    donation_item = st.multiselect(
        "Select items for donation:",
        ["Mats", "Sleeping Bags", "Pillows", "Blankets", "Tents"]
    )

elif donation_category == "Baby & Elderly Care":
    donation_item = st.multiselect(
        "Select items for donation:",
        ["Diapers", "Baby Food", "Adult Diapers", "Baby Wipes"]
    )

elif donation_category == "Safety & Emergency Items":
    donation_item = st.multiselect(
        "Select items for donation:",
        ["Flashlights", "Batteries", "Power Banks", "Whistles", "Raincoats", "Emergency Contact Cards"]
    )

# Join the list of selected items into a single string to store in the database
donation_item = ', '.join(donation_item)

# Additional input fields
quantity = st.number_input("Quantity", min_value=1, value=1, step=1)

# Columns for delivery date and additional notes
col3, col4 = st.columns(2)

with col3:
    preferred_delivery_date = st.date_input("Preferred delivery Date", min_value=datetime.today().date())

with col4:
    additional_notes = st.text_area("Additional Notes", placeholder="Any additional information or notes")

# Define function to connect to the MySQL database (db4free.net)
def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host='db4free.net',            
            database='your_database_name',  
            user='aafifjazimin04910',            
            password='Afifj_04',    
        )
        st.success("Connected to the database successfully!")
    except Error as e:
        st.error(f"Error: '{e}'")
    return connection

# Define function to insert donation data into the database
def insert_donation_data(connection, donor_name, donor_email, donor_phone, donation_item, quantity, preferred_delivery_date, additional_notes):
    cursor = connection.cursor()
    query = """
    INSERT INTO donations (donor_name, donor_email, donor_phone, donation_item, quantity, delivery_date, additional_notes)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    values = (donor_name, donor_email, donor_phone, donation_item, quantity, preferred_delivery_date, additional_notes)
    cursor.execute(query, values)
    connection.commit()
    cursor.close()

# Function to generate QR code
def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,  # Controls the size of the QR code
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")
    return img

# Submission button and data validation
if st.button("Submit Donation"):
    if not donor_name or not donor_email or not donation_item:
        st.error("Please fill in all the required fields marked with *.")
    else:
        # Create a DataFrame to store the submission data
        donation_data = pd.DataFrame({
            "Donor Name": [donor_name],
            "Email": [donor_email],
            "Phone": [donor_phone],
            "Donation Item": [donation_item],
            "Quantity": [quantity],
            "Delivery Date": [preferred_delivery_date],
            "Additional Notes": [additional_notes]
        })

        # Display the collected data
        st.markdown("## 🎉 Thank you for your donation!")
        st.markdown("### Here are the details you submitted:")
        st.dataframe(donation_data)

        # Connect to the database and insert the data
        connection = create_connection()
        if connection is not None:
            insert_donation_data(connection, donor_name, donor_email, donor_phone, donation_item, quantity, preferred_delivery_date, additional_notes)
            st.success("Your donation details have been saved to the database!")
            connection.close()

        # Generate the QR code containing the donor information
        qr_data = f"Donor Name: {donor_name}\nEmail: {donor_email}\nPhone: {donor_phone}\nDonation Item: {donation_item}\nQuantity: {quantity}\nDelivery Date: {preferred_delivery_date}\nAdditional Notes: {additional_notes}"
        qr_image = generate_qr_code(qr_data)

        # Convert the QR code to a format that can be displayed on Streamlit
        buffer = BytesIO()
        qr_image.save(buffer)
        buffer.seek(0)

        st.image(buffer, caption="Scan this QR Code to view donation details", use_column_width=True)
