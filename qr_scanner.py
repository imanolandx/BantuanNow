import cv2
from pyzbar.pyzbar import decode
from sqlalchemy import create_engine
import pandas as pd
import streamlit as st
import os

# Get database credentials from environment variables
mysql_user = os.getenv("MYSQL_USER")
mysql_password = os.getenv("MYSQL_PASSWORD")

# Initialize camera
cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set frame width
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Set frame height

# Streamlit app
st.title("QR Code Scanner")

# Database connection
try:
    connection_string = f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@db4free.net/imankamil"
    engine = create_engine(connection_string)
except Exception as e:
    st.error(f"Database connection error: {e}")

# Function to capture and process frames
def capture_and_process_frame():
    success, frame = cam.read()  # Capture the frame
    if not success:
        st.error("Failed to open camera.")
        return None, None

    # Decode QR codes in the frame
    qr_codes = decode(frame)
    return frame, qr_codes

# Streamlit button to start scanning
if st.button("Start Scanning", key="start_scanning"):
    placeholder = st.empty()  # Placeholder for the camera feed
    scanned_data = []  # List to store scanned QR code data

    stop_scanning = False

    while not stop_scanning:
        frame, qr_codes = capture_and_process_frame()
        if frame is None:
            break

        # Display the frame
        placeholder.image(frame, channels="BGR")

        # Process QR codes
        for qr_code in qr_codes:
            qr_data = qr_code.data.decode('utf-8')  # Get the decoded data
            qr_type = qr_code.type  # Get the type of the QR code

            st.write(f"QR Code Type: {qr_type}")
            st.write(f"QR Code Data: {qr_data}")

            # Insert the QR code data into the database
            try:
                query = f"INSERT INTO qr_codes (qr_type, qr_data) VALUES ('{qr_type}', '{qr_data}')"
                with engine.connect() as conn:
                    conn.execute(query)
                st.write("QR Code data inserted into database.")
            except Exception as e:
                st.error(f"Failed to insert data into the database: {e}")

            # Add the scanned data to the list
            scanned_data.append({"Type": qr_type, "Data": qr_data})

            # Check if the QR code contains a URL and display it
            if qr_data.startswith('http://') or qr_data.startswith('https://'):
                st.write(f"Detected URL: {qr_data}")
                st.markdown(f"[Open Link]({qr_data})")
            else:
                st.write("No valid URL detected in QR code.")

        # Display the scanned data in a table
        if scanned_data:
            df = pd.DataFrame(scanned_data)
            st.table(df)

        # Check if the user wants to stop scanning
        if st.button("Stop Scanning", key="stop_scanning"):
            stop_scanning = True

# Release the camera
cam.release()