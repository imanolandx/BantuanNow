import mysql.connector
import pandas as pd
from datetime import datetime
import os
import qrcode

class Database:
    def __init__(self):
        # Get database credentials from environment variables
        mysql_user = os.getenv("MYSQL_USER")
        mysql_password = os.getenv("MYSQL_PASSWORD")

        # Database connection using mysql.connector
        try:
            self.conn = mysql.connector.connect(
                host="localhost",  # Change if different in DBeaver
                user=mysql_user,
                password=mysql_password,
                database="bantuannow",
                port="3306"  # MySQL default port
            )
            self.cursor = self.conn.cursor()
        except Exception as e:
            raise Exception(f"Database connection error: {e}")

    def initialize_database(self):
        # Execute SQL scripts to create tables if they don't exist
        with open('schema.sql', 'r') as f:
            self.cursor.execute(f.read(), multi=True)
            self.conn.commit()
    def insert_ngoinventory(self, ngo_id,item_id,quantity, expiry_date, batch_id, source, notes):
        query = """
        INSERT INTO ngo_inventory (ngo_id, item_id, quantity, expiry_date, batch_id, last_updated, source, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (ngo_id, item_id, quantity, expiry_date, batch_id, datetime.now(), source, notes)
        self.cursor.execute(query, values)
        self.conn.commit()
        return self.cursor.lastrowid
    # Flood Center Functions
    def get_all_centers(self):
        query = "SELECT * FROM flood_centers2"
        self.cursor.execute(query)
        df = pd.DataFrame(self.cursor.fetchall(), columns=[desc[0] for desc in self.cursor.description])
        return df

    def get_center_demands(self, center_id):
        query = """
        SELECT sd.demand_id, si.name, sd.quantity, sd.priority, sd.status, sd.request_date
        FROM supply_demands sd
        JOIN supply_items si ON sd.item_id = si.item_id
        WHERE sd.center_id = %s
        ORDER BY sd.request_date DESC
        """
        self.cursor.execute(query, (center_id,))
        df = pd.DataFrame(self.cursor.fetchall(), columns=[desc[0] for desc in self.cursor.description])
        return df

    # Supply Demand Functions
    def create_demand(self, center_id, item_id, quantity, priority):
        query = """
        INSERT INTO supply_demands (center_id, item_id, quantity, priority, request_date, status)
        VALUES (%s, %s, %s, %s, %s, 'Pending')
        """
        self.cursor.execute(query, (center_id, item_id, quantity, priority, datetime.now()))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_demand_status(self, demand_id, status):
        self.cursor.execute(
            "UPDATE supply_demands SET status = %s WHERE demand_id = %s", 
            (status, demand_id)
        )
        self.conn.commit()

    # NGO and Donation Functions
    def get_all_ngos(self):
        query = "SELECT * FROM ngos2 WHERE verification_status = 'Verified'"
        self.cursor.execute(query)
        df = pd.DataFrame(self.cursor.fetchall(), columns=[desc[0] for desc in self.cursor.description])
        return df

    def create_donation(self, ngo_id, donor_name, donor_email, amount, payment_method):
            query = """
            INSERT INTO donations (ngo_id, donor_name, donor_email, amount, donation_date, payment_method)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (ngo_id, donor_name, donor_email, amount, datetime.now(), payment_method)
            self.cursor.execute(query, values)
            self.conn.commit()
            return self.cursor.lastrowid

    def track_donation(self, donor_email):
        query = """
        SELECT d.donation_id, n.name as ngo_name, d.amount, d.donation_date, 
               da.purpose, da.amount as allocated_amount, da.allocation_date
        FROM donations d
        JOIN ngos2 n ON d.ngo_id = n.ngo_id
        LEFT JOIN donation_allocations da ON d.donation_id = da.donation_id
        WHERE d.donor_email = %s
        ORDER BY d.donation_date DESC
        """
        self.cursor.execute(query, (donor_email,))
        df = pd.DataFrame(self.cursor.fetchall(), columns=[desc[0] for desc in self.cursor.description])
        return df

   # QR Code Functions
    def generate_qr_code(self):
        import uuid
        qr_code = str(uuid.uuid4())
        self.cursor.execute(
            "INSERT INTO supply_boxes (qr_code, created_date) VALUES (?, ?)",
            (qr_code, datetime.now())
        )
        self.conn.commit()
        return qr_code, self.cursor.lastrowid
    def get_next_box_id(self):
        query = "SELECT MAX(box_id) FROM supply_boxes"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return result[0] + 1 if result[0] else 1
    def get_next_content_id(self):
        query = "SELECT MAX(content_id) FROM box_contents"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return result[0] + 1 if result[0] else 1
    
    def add_item_to_box(self, content_id, box_id, item_id, quantity):
        query = """INSERT INTO box_contents (content_id, box_id, item_id, quantity)
                VALUES (%s, %s, %s, %s)"""
        self.cursor.execute(query, (content_id, box_id, item_id, quantity))
        self.conn.commit()
    def insert_box_ngo_info(self, box_id, destination_center_id, priority):
        query = """
        INSERT INTO box_ngo_info (box_id, destination_center_id, priority)
        VALUES (%s, %s, %s)
        """
        self.cursor.execute(query, (box_id, destination_center_id, priority))
        self.conn.commit()
    def scan_qr_code(self, qr_code, center_id, received_by):
        # Get box details
        box_query = "SELECT box_id FROM supply_boxes WHERE qr_code = ?"
        self.cursor.execute(box_query, (qr_code,))
        box_result = self.cursor.fetchone()
        
        if not box_result:
            return False, "Invalid QR code"
        
        box_id = box_result[0]
        
        # Get box contents
        contents_query = """
        SELECT bc.item_id, si.name, bc.quantity
        FROM box_contents bc
        JOIN supply_items si ON bc.item_id = si.item_id
        WHERE bc.box_id = ?
        """
        self.cursor.execute(contents_query, (box_id,))
        contents = self.cursor.fetchall()
        
        # Update demands that match the contents
        for item_id, _, quantity in contents:
            # Find matching demand
            demand_query = """
            SELECT demand_id FROM supply_demands 
            WHERE center_id = ? AND item_id = ? AND status = 'Pending'
            ORDER BY request_date ASC LIMIT 1
            """
            self.cursor.execute(demand_query, (center_id, item_id))
            demand_result = self.cursor.fetchone()
            
            if demand_result:
                demand_id = demand_result[0]
                # Record delivery
                self.cursor.execute(
                    """INSERT INTO supply_deliveries 
                       (box_id, demand_id, center_id, delivery_date, received_by)
                       VALUES (?, ?, ?, ?, ?)""",
                    (box_id, demand_id, center_id, datetime.now(), received_by)
                )
                # Update demand status
                self.update_demand_status(demand_id, 'Fulfilled')
        
        self.conn.commit()
        return True, contents

    # Alert System Functions
    def get_pending_demands(self):
        query = """
        SELECT sd.demand_id, fc.name as center_name, si.name as item_name, 
               sd.quantity, sd.priority, sd.request_date
        FROM supply_demands sd
        JOIN flood_centers2 fc ON sd.center_id = fc.center_id
        JOIN supply_items si ON sd.item_id = si.item_id
        WHERE sd.status = 'Pending'
        ORDER BY 
            CASE sd.priority
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                WHEN 'Low' THEN 4
                ELSE 5
            END,
            sd.request_date ASC
        """
        self.cursor.execute(query)
        df = pd.DataFrame(self.cursor.fetchall(), columns=[desc[0] for desc in self.cursor.description])
        return df

    def get_supplies_for_center(self, center_id):
        query = """
        SELECT si.name as supply_type, sc.quantity, sc.date
        FROM supply_centers sc
        JOIN supply_items si ON sc.item_id = si.item_id
        WHERE sc.center_id = %s
        """
        self.cursor.execute(query, (center_id,))
        df = pd.DataFrame(self.cursor.fetchall(), columns=[desc[0] for desc in self.cursor.description])
        return df
    def get_new_demands(self, selected_centers, selected_priorities):
        query = """
        SELECT sd.demand_id, fc.name as center_name, si.name as item_name, 
               sd.quantity, sd.priority, sd.request_date
        FROM supply_demands sd
        JOIN flood_centers2 fc ON sd.center_id = fc.center_id
        JOIN supply_items si ON sd.item_id = si.item_id
        WHERE sd.status = 'Pending' AND sd.center_id IN (%s) AND sd.priority IN (%s)
        ORDER BY sd.request_date DESC
        """ % (','.join(['%s'] * len(selected_centers)), ','.join(['%s'] * len(selected_priorities)))
        self.cursor.execute(query, selected_centers + selected_priorities)
        df = pd.DataFrame(self.cursor.fetchall(), columns=[desc[0] for desc in self.cursor.description])
        return df

    def close(self):
        self.conn.close()