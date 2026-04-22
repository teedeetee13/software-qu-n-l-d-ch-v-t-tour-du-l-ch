import sqlite3

class DBManager:
    def __init__(self, db_name="tour_management.db"):
        self.db_name = db_name

    def connect(self):
        return sqlite3.connect(self.db_name)

    # --- Xác thực ---
    def check_login(self, username, password):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM Users WHERE username=? AND password=?", (username, password))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    # --- Quản lý Tour ---
    def get_all_tours(self, search_text="", status_filter="Tất cả"):
        conn = self.connect()
        query = "SELECT * FROM Tours WHERE (name LIKE ? OR destination LIKE ?)"
        params = [f"%{search_text}%", f"%{search_text}%"]
        
        if status_filter != "Tất cả":
            query += " AND status = ?"
            params.append(status_filter)
            
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_tour(self, t_id, name, dest, duration, price, status):
        conn = self.connect()
        try:
            conn.execute("INSERT INTO Tours VALUES (?, ?, ?, ?, ?, ?)", (t_id, name, dest, duration, price, status))
            conn.commit()
            return True, "Thêm thành công!"
        except sqlite3.IntegrityError:
            return False, "Mã Tour đã tồn tại!"
        finally:
            conn.close()

    def update_tour(self, t_id, name, dest, duration, price, status):
        conn = self.connect()
        conn.execute("UPDATE Tours SET name=?, destination=?, duration=?, price=?, status=? WHERE id=?", 
                     (name, dest, duration, price, status, t_id))
        conn.commit()
        conn.close()

    def delete_tour(self, t_id):
        conn = self.connect()
        conn.execute("DELETE FROM Tours WHERE id=?", (t_id,))
        conn.commit()
        conn.close()

    # --- Quản lý Khách hàng ---
    def get_all_customers(self, search_text=""):
        conn = self.connect()
        query = "SELECT * FROM Customers WHERE (full_name LIKE ? OR phone LIKE ?)"
        params = [f"%{search_text}%", f"%{search_text}%"]
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_customer(self, c_id, full_name, email, phone):
        conn = self.connect()
        try:
            conn.execute("INSERT INTO Customers VALUES (?, ?, ?, ?)", (c_id, full_name, email, phone))
            conn.commit()
            return True, "Thêm thành công!"
        except sqlite3.IntegrityError:
            return False, "Mã Khách hàng đã tồn tại!"
        finally:
            conn.close()

    def update_customer(self, c_id, full_name, email, phone):
        conn = self.connect()
        conn.execute("UPDATE Customers SET full_name=?, email=?, phone=? WHERE id=?", 
                     (full_name, email, phone, c_id))
        conn.commit()
        conn.close()

    def delete_customer(self, c_id):
        conn = self.connect()
        conn.execute("DELETE FROM Customers WHERE id=?", (c_id,))
        conn.commit()
        conn.close()

    # --- Quản lý Đặt chỗ (Bookings) ---
    def get_all_bookings(self, search_text="", status_filter="Tất cả"):
        conn = self.connect()
        query = "SELECT * FROM Bookings WHERE (customer_name LIKE ? OR tour_name LIKE ?)"
        params = [f"%{search_text}%", f"%{search_text}%"]
        
        if status_filter != "Tất cả":
            query += " AND status = ?"
            params.append(status_filter)
            
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_booking(self, b_id, customer_name, tour_name, booking_date, guest_count, total_price, status):
        conn = self.connect()
        try:
            conn.execute("INSERT INTO Bookings VALUES (?, ?, ?, ?, ?, ?, ?)", 
                         (b_id, customer_name, tour_name, booking_date, guest_count, total_price, status))
            conn.commit()
            return True, "Thêm thành công!"
        except sqlite3.IntegrityError:
            return False, "Mã Booking đã tồn tại!"
        finally:
            conn.close()

    def update_booking(self, b_id, customer_name, tour_name, booking_date, guest_count, total_price, status):
        conn = self.connect()
        conn.execute("UPDATE Bookings SET customer_name=?, tour_name=?, booking_date=?, guest_count=?, total_price=?, status=? WHERE id=?", 
                     (customer_name, tour_name, booking_date, guest_count, total_price, status, b_id))
        conn.commit()
        conn.close()

    def delete_booking(self, b_id):
        conn = self.connect()
        conn.execute("DELETE FROM Bookings WHERE id=?", (b_id,))
        conn.commit()
        conn.close()

    # --- Thống kê Dashboard ---
    def get_dashboard_stats(self):
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT SUM(total_price) FROM Bookings WHERE status='Đã xác nhận'")
        rev = cursor.fetchone()[0]
        revenue = rev if rev else 0
        
        cursor.execute("SELECT COUNT(*) FROM Bookings")
        bookings = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Customers")
        customers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Tours WHERE status='Hoạt động'")
        tours = cursor.fetchone()[0]
        
        conn.close()
        return revenue, bookings, customers, tours

    def get_recent_bookings(self, limit=5):
        conn = self.connect()
        cursor = conn.execute("SELECT * FROM Bookings ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return rows