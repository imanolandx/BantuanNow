import mysql.connector
import pandas as pd
import streamlit as st
import plotly.express as px
import os
from datetime import datetime

# Get database credentials from environment variables
mysql_user = os.getenv("MYSQL_USER")
mysql_password = os.getenv("MYSQL_PASSWORD")

# Database connection using mysql.connector
try:
    conn = mysql.connector.connect(
        host="localhost",  # Change if different in DBeaver
        user=mysql_user,
        password=mysql_password,
        database="bantuannow",
        port="3306"  # MySQL default port
    )
    cursor = conn.cursor()
    query = "SELECT * FROM flood_centres"
    cursor.execute(query)
    df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
    cursor.close()
    conn.close()
except Exception as e:
    st.error(f"Database connection error: {e}")

# Standardize column names
df.columns = df.columns.str.lower()

# Basic data validation
required_columns = ['centre_name', 'state', 'clothes', 'food', 'medicine_kit', 'mineral_water']
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.warning(f"Missing columns: {missing_columns}")

st.set_page_config(layout="wide")  # Make the dashboard full-width
st.title("Flood Centres Supply Management Dashboard")

if df is None:
    st.error("Unable to load flood centres data.")

# Sidebar for filters
with st.sidebar:
    st.header("Dashboard Filters")
    
    states = ["All States"] + sorted(list(df["state"].unique()))
    selected_state = st.selectbox("Filter by State", states)
    
    supply_types = ['clothes', 'food', 'medicine_kit', 'mineral_water']
    selected_supplies = st.multiselect(
        "Select Supply Types to Analyze", 
        supply_types, 
        default=['food', 'clothes', 'medicine_kit', 'mineral_water']
    )

# Apply state filter
filtered_df = df if selected_state == "All States" else df[df["state"] == selected_state]

# Quick insights at the top
st.subheader("Quick Insights")
metrics_col1, metrics_col2, metrics_col3 = st.columns(3)

with metrics_col1:
    st.metric(
        "Total Centres", 
        filtered_df.shape[0], 
        help="Number of flood centres in selected state/all states"
    )

with metrics_col2:
    st.metric(
        "Total Supplies", 
        filtered_df[selected_supplies].sum().sum(), 
        help="Total quantity of selected supply types"
    )

with metrics_col3:
    st.metric(
        "Average Supplies per Centre",
        round(filtered_df[selected_supplies].sum().sum() / filtered_df.shape[0], 2),
        help="Average quantity of supplies per centre"
    )

# Create tabs for different visualizations
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Supply Overview", "📈 Detailed Analysis", "➕ Add New Centre", "🗑️ Manage Centres", "Add Supply Items", "Add New Items"])

with tab1:
    # Main content area with supply overview
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("Flood Centres Supply Overview")
        # Style the dataframe
        table_height = min(400, 35 + len(filtered_df) * 35)
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=table_height,
            hide_index=True,
        )
    
    with col2:
        st.subheader("Supply Distribution")
        supply_totals = filtered_df[selected_supplies].sum()
        fig_pie = px.pie(
            names=supply_totals.index,
            values=supply_totals.values,
            hole=0.4,  # Make it a donut chart
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_layout(
            height=400,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Add line graph under the pie chart and table
    st.subheader("Supply Trends Over Time")
    # Assuming you have a 'date' column in your dataframe for the line graph
    if 'date' in df.columns:
        fig_line = px.line(
            df,
            x='date',
            y=selected_supplies,
            title='Supply Trends Over Time',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_line.update_layout(
            xaxis_title="Date",
            yaxis_title="Quantity",
            legend_title="Supply Type",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.warning("No 'date' column found in the data for the line graph.")

with tab2:
    st.subheader("Detailed Supply Breakdown by Centre")
    # Create a more detailed bar chart
    fig_bar = px.bar(
        filtered_df,
        x='centre_name',
        y=selected_supplies,
        title='Supply Quantities by Flood Centre',
        barmode='group',
        color_discrete_sequence=px.colors.qualitative.Set3,
        height=500
    )
    
    # Customize the bar chart
    fig_bar.update_layout(
        xaxis_title="Centre Name",
        yaxis_title="Quantity",
        legend_title="Supply Type",
        xaxis={'categoryorder':'total descending'},  # Sort by total supplies
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Rotate x-axis labels for better readability
    fig_bar.update_xaxes(tickangle=45)
    
    st.plotly_chart(fig_bar, use_container_width=True)

with tab3:
    st.subheader("Add New Flood Centre")
    with st.form("add_centre_form"):
        
        centre_name = st.text_input("Centre Name")
        location = st.text_input("Location")
        contact_person = st.text_input("Person in Charge")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email")
        
        submit = st.form_submit_button("Add Centre")
        
        if submit:
            try:
                conn = mysql.connector.connect(
                    host="localhost",  # Change if different in DBeaver
                    user=mysql_user,
                    password=mysql_password,
                    database="bantuannow",
                    port="3306"  # MySQL default port
                )
                cursor = conn.cursor()
                query = """
                INSERT INTO flood_centers2 (name, location, contact_person, phone, email)
                VALUES (%s, %s, %s, %s, %s)
                """
                values = (centre_name, location, contact_person, phone, email)
                cursor.execute(query, values)
                conn.commit()
                cursor.close()
                conn.close()
                st.success("New flood centre added successfully!")
            except Exception as e:
                st.error(f"Failed to add new flood centre: {e}")

with tab4:
    st.subheader("Manage Flood Centres")
    st.write("Select a row to delete from the table below:")
    try:
        conn = mysql.connector.connect(
            host="localhost",  # Change if different in DBeaver
            user=mysql_user,
            password=mysql_password,
            database="bantuannow",
            port="3306"  # MySQL default port
        )
        cursor = conn.cursor()
        query = "SELECT * FROM flood_centers2"
        cursor.execute(query)
        df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
        cursor.close()
        conn.close()
    except Exception as e:
        st.error(f"Database connection error: {e}")
        st.subheader("Manage Flood Centres")
    st.dataframe(df)
    # Display the table with an option to delete rows
    if not df.empty:
        selected_rows = st.multiselect("Select rows to delete", df.index, format_func=lambda x: df.loc[x, 'name'])
        
        if selected_rows:
            if st.button("Delete Selected Rows"):
                try:
                    conn = mysql.connector.connect(
                        host="localhost",  # Change if different in DBeaver
                        user=mysql_user,
                        password=mysql_password,
                        database="bantuannow",
                        port="3306"  # MySQL default port
                    )
                    cursor = conn.cursor()
                    for row in selected_rows:
                        centre_id = int(df.loc[row, 'center_id'])
                        query = "DELETE FROM flood_centers2 WHERE center_id = %s"
                        cursor.execute(query, (centre_id,))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success("Selected rows deleted successfully!")
                except Exception as e:
                    st.error(f"Failed to delete selected rows: {e}")
    else:
        st.warning("No data available to display.")

with tab5:
    st.subheader("Add Supply Items")
    with st.form("add_supply_item_form"):
        
        item_name = st.text_input("Item Name")
        category = st.selectbox(
            "Select a category",
            ["Food & water", "Hygiene & sanitation", "Medical supplies", "Clothing & Blankets", "Shelter & Emergency Items", "Children & Elderly Needs","Rescue & safety gear", "Other"]
        )
        unit = st.text_input("Unit")
        
        submit = st.form_submit_button("Add Supply Item")
        
        if submit:
            try:
                conn = mysql.connector.connect(
                    host="localhost",  # Change if different in DBeaver
                    user=mysql_user,
                    password=mysql_password,
                    database="bantuannow",
                    port="3306"  # MySQL default port
                )
                cursor = conn.cursor()
                query = """
                INSERT INTO supply_items (name, category, unit)
                VALUES (%s, %s, %s)
                """
                values = (item_name, category, unit)
                cursor.execute(query, values)
                conn.commit()
                cursor.close()
                conn.close()
                st.success("New supply item added successfully!")
            except Exception as e:
                st.error(f"Failed to add new supply item: {e}")

with tab6:
    st.subheader("Add New Items")
    with st.form("add_supplies_form"):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user=mysql_user,
                password=mysql_password,
                database="bantuannow",
                port="3306"
            )
            items = pd.read_sql_query("SELECT * FROM supply_items", conn)
            conn.close()
        except Exception as e:
            st.error(f"Database connection error: {e}")
            items = pd.DataFrame(columns=['item_id', 'name'])

        ngo_id = st.number_input("NGO ID", min_value=1, value=1)
        item_id = st.selectbox(
            "Item Type",
            options=items['item_id'].tolist(),
            format_func=lambda x: items[items['item_id'] == x]['name'].iloc[0]
        )
        quantity = st.number_input("Quantity", min_value=1, value=10)
        batch_id = st.text_input("Batch ID")
        expiry_date = st.date_input("Expiry Date")
        source = st.text_input("Source/Supplier")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Add to Inventory")

    if submitted:
        if all([item_id, quantity, expiry_date]):
            try:
                conn = mysql.connector.connect(
                    host="localhost",
                    user=mysql_user,
                    password=mysql_password,
                    database="bantuannow",
                    port="3306"
                )
                cursor = conn.cursor()

                # Insert query
                query = """
                INSERT INTO ngo_inventory (ngo_id, item_id, quantity, expiry_date, batch_id, source, notes, last_updated)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (ngo_id, item_id, quantity, expiry_date, batch_id, source, notes, datetime.now())
                
                cursor.execute(query, values)
                conn.commit()
                cursor.close()
                conn.close()

                st.success("✅ Items added successfully!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        else:
            st.error("Please fill in all required fields")