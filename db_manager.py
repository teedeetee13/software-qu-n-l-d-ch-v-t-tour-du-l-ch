import sqlite3

class DBManager:
    def __init__(self, db_name="tour_management.db"):
        self.db_name = db_name

    def connect(self):
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def next_id(self, table_name, id_column, prefix):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f"SELECT {id_column} FROM {table_name} WHERE {id_column} LIKE ?", (f"{prefix}%",))
        rows = cursor.fetchall()
        conn.close()
        
        max_num = 0
        for row in rows:
            try:
                num_part = int(row[0].replace(prefix, ""))
                if num_part > max_num:
                    max_num = num_part
            except ValueError:
                pass
        return f"{prefix}{max_num + 1:03d}"

    # --- Xác thực ---
    def check_login(self, username, password):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM Users WHERE username=? AND password=?", (username, password)) # Schema không đổi nhiều
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    # --- Quản lý Tour ---
    def get_all_tours(self, search_text=""):
        conn = self.connect()
        query = """
            SELECT t.id, t.name, d.name, c.name, t.duration, t.description, t.destination_id, t.category_id
            FROM Tours t
            LEFT JOIN Destinations d ON t.destination_id = d.id
            LEFT JOIN Tour_Categories c ON t.category_id = c.id
            WHERE (t.name LIKE ? OR d.name LIKE ?)
        """
        params = [f"%{search_text}%", f"%{search_text}%"]
            
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_tour(self, t_id, name, dest_id, cat_id, duration, description):
        conn = self.connect()
        try:
            conn.execute("INSERT INTO Tours (id, name, destination_id, category_id, duration, description) VALUES (?, ?, ?, ?, ?, ?)", 
                         (t_id, name, dest_id, cat_id, duration, description))
            conn.commit()
            return True, "Thêm thành công!"
        except sqlite3.IntegrityError:
            return False, "Mã Tour đã tồn tại!"
        finally:
            conn.close()

    def update_tour(self, t_id, name, dest_id, cat_id, duration, description):
        conn = self.connect()
        conn.execute("UPDATE Tours SET name=?, destination_id=?, category_id=?, duration=?, description=? WHERE id=?", 
                     (name, dest_id, cat_id, duration, description, t_id))
        conn.commit()
        conn.close()

    def delete_tour(self, t_id):
        conn = self.connect()
        conn.execute("DELETE FROM Tours WHERE id=?", (t_id,))
        conn.commit()
        conn.close()

    # --- Helpers for Forms ---
    def get_all_destinations(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM Destinations ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_all_categories(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM Tour_Categories ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        return rows

    # --- Quản lý Khách hàng (Customers) ---
    def get_all_customers(self, search_text=""):
        conn = self.connect()
        query = "SELECT id, full_name, email, phone, address FROM Customers WHERE (full_name LIKE ? OR phone LIKE ? OR email LIKE ?)"
        params = [f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"]
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_customer(self, c_id, full_name, email, phone, address):
        conn = self.connect()
        try:
            conn.execute("INSERT INTO Customers VALUES (?, ?, ?, ?, ?)", 
                         (c_id, full_name, email, phone, address))
            conn.commit()
            return True, "Thêm thành công!"
        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed: Customers.email' in str(e):
                return False, "Email đã tồn tại!"
            return False, "Mã khách hàng đã tồn tại!"
        finally:
            conn.close()

    def update_customer(self, c_id, full_name, email, phone, address):
        conn = self.connect()
        conn.execute("UPDATE Customers SET full_name=?, email=?, phone=?, address=? WHERE id=?", 
                     (full_name, email, phone, address, c_id))
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
        query = """
            SELECT b.id, c.full_name, t.name, b.booking_date, b.guest_count, b.total_price, b.status, b.customer_id, b.schedule_id 
            FROM Bookings b
            JOIN Customers c ON b.customer_id = c.id
            JOIN Schedules s ON b.schedule_id = s.id
            JOIN Tours t ON s.tour_id = t.id
            WHERE (c.full_name LIKE ? OR t.name LIKE ? OR b.id LIKE ?)
        """
        params = [f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"]
        
        if status_filter != "Tất cả":
            query += " AND b.status = ?"
            params.append(status_filter)
            
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_booking(self, b_id, customer_id, schedule_id, booking_date, guest_count, total_price, status):
        conn = self.connect()
        try:
            conn.execute("INSERT INTO Bookings VALUES (?, ?, ?, ?, ?, ?, ?)", 
                         (b_id, customer_id, schedule_id, booking_date, guest_count, total_price, status))
            conn.commit()
            return True, "Thêm thành công!"
        except sqlite3.IntegrityError:
            return False, "Mã Booking đã tồn tại!"
        finally:
            conn.close()

    def update_booking(self, b_id, customer_id, schedule_id, booking_date, guest_count, total_price, status):
        conn = self.connect()
        conn.execute("UPDATE Bookings SET customer_id=?, schedule_id=?, booking_date=?, guest_count=?, total_price=?, status=? WHERE id=?", 
                     (customer_id, schedule_id, booking_date, guest_count, total_price, status, b_id))
        conn.commit()
        conn.close()

    def delete_booking(self, b_id):
        conn = self.connect()
        conn.execute("DELETE FROM Bookings WHERE id=?", (b_id,))
        conn.commit()
        conn.close()

    # --- Quản lý Lịch Khởi Hành (Schedules) ---
    def get_all_schedules(self, search_text=""):
        conn = self.connect()
        query = """
            SELECT
                s.id, s.tour_id, t.name, s.departure_date, s.return_date,
                p.price,
                s.max_slots, s.booked_slots, s.status, s.guide_name
            FROM Schedules s
            JOIN Tours t ON s.tour_id = t.id
            LEFT JOIN Price_Policies p ON s.id = p.schedule_id AND p.passenger_type = 'Người lớn'
            WHERE (t.name LIKE ? OR s.id LIKE ?)
            ORDER BY s.departure_date DESC
        """
        params = [f"%{search_text}%", f"%{search_text}%"]
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_prices_for_schedule(self, schedule_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT passenger_type, price FROM Price_Policies WHERE schedule_id=?", (schedule_id,))
        rows = cursor.fetchall()
        conn.close()
        return {row[0]: row[1] for row in rows}

    @staticmethod
    def _calc_status(dep_date_str, booked_slots, max_slots=None):
        """Tự động tính trạng thái dựa vào ngày và số chỗ."""
        from datetime import date, timedelta
        try:
            dep = date.fromisoformat(str(dep_date_str))
        except (ValueError, TypeError):
            return "Còn chỗ"
        today = date.today()
        if dep < today:
            return "Đã kết thúc"
        if max_slots is not None and int(booked_slots) >= int(max_slots):
            return "Hết chỗ"
        if dep <= today + timedelta(days=3):
            return "Sắp khởi hành"
        return "Còn chỗ"

    def add_schedule(self, s_id, tour_id, dep_date, ret_date, booked_slots, prices, guide_name=""):
        """Thêm lịch khởi hành mới. max_slots mặc định 999 (không giới hạn)."""
        status = self._calc_status(dep_date, booked_slots)
        conn = self.connect()
        try:
            cursor = conn.cursor()
            cursor.execute("BEGIN TRANSACTION")
            cursor.execute(
                "INSERT INTO Schedules (id, tour_id, departure_date, return_date, max_slots, booked_slots, status, guide_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (s_id, tour_id, dep_date, ret_date, 999, booked_slots, status, guide_name)
            )
            for p_type, price in prices.items():
                cursor.execute(
                    "INSERT INTO Price_Policies (schedule_id, passenger_type, price) VALUES (?, ?, ?)",
                    (s_id, p_type, price)
                )
            conn.commit()
            return True, "Thêm thành công!"
        except Exception as e:
            conn.rollback()
            return False, f"Lỗi: {e}"
        finally:
            conn.close()

    def update_schedule(self, s_id, tour_id, dep_date, ret_date, booked_slots, prices, guide_name=""):
        """Cập nhật lịch khởi hành. Trạng thái được tính tự động."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT max_slots FROM Schedules WHERE id=?", (s_id,))
        row = cursor.fetchone()
        max_slots = row[0] if row else 999
        status = self._calc_status(dep_date, booked_slots, max_slots)
        try:
            cursor.execute("BEGIN TRANSACTION")
            cursor.execute(
                "UPDATE Schedules SET tour_id=?, departure_date=?, return_date=?, booked_slots=?, status=?, guide_name=? WHERE id=?",
                (tour_id, dep_date, ret_date, booked_slots, status, guide_name, s_id)
            )
            cursor.execute("DELETE FROM Price_Policies WHERE schedule_id=?", (s_id,))
            for p_type, price in prices.items():
                cursor.execute(
                    "INSERT INTO Price_Policies (schedule_id, passenger_type, price) VALUES (?, ?, ?)",
                    (s_id, p_type, price)
                )
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def delete_schedule(self, s_id):
        conn = self.connect()
        conn.execute("DELETE FROM Schedules WHERE id=?", (s_id,))
        conn.commit()
        conn.close()

    # --- Quản lý User ---
    def get_all_users(self, search_text=""):
        conn = self.connect()
        query = "SELECT id, username, full_name, email, phone, role FROM Users WHERE (username LIKE ? OR full_name LIKE ? OR email LIKE ?)"
        params = [f"%{search_text}%"] * 3
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_user(self, u_id, username, password, full_name, email, phone, address, role):
        conn = self.connect()
        try:
            conn.execute("INSERT INTO Users VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                         (u_id, username, password, full_name, email, phone, address, role))
            conn.commit()
            return True, "Thêm thành công!"
        except sqlite3.IntegrityError as e:
            if 'username' in str(e):
                return False, "Tên đăng nhập đã tồn tại!"
            if 'email' in str(e):
                return False, "Email đã tồn tại!"
            return False, "Mã User đã tồn tại!"
        finally:
            conn.close()

    def update_user(self, u_id, username, password, full_name, email, phone, address, role):
        conn = self.connect()
        try:
            conn.execute(
                "UPDATE Users SET username=?, password=?, full_name=?, email=?, phone=?, address=?, role=? WHERE id=?",
                (username, password, full_name, email, phone, address, role, u_id))
            conn.commit()
            return True, "Cập nhật thành công!"
        except sqlite3.IntegrityError as e:
            if 'username' in str(e):
                return False, "Tên đăng nhập đã tồn tại!"
            if 'email' in str(e):
                return False, "Email đã tồn tại!"
            return False, "Lỗi cập nhật!"
        finally:
            conn.close()

    def delete_user(self, u_id):
        conn = self.connect()
        conn.execute("DELETE FROM Users WHERE id=?", (u_id,))
        conn.commit()
        conn.close()

    # --- Quản lý Hướng dẫn viên ---
    def get_all_guides(self, search_text=""):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, full_name, phone, email, specialty, experience_years FROM Guides "
            "WHERE (full_name LIKE ? OR specialty LIKE ? OR phone LIKE ?) ORDER BY full_name",
            [f"%{search_text}%"] * 3)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_all_guides_for_form(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT full_name FROM Guides ORDER BY full_name")
        rows = cursor.fetchall()
        conn.close()
        return [r[0] for r in rows]

    def add_guide(self, g_id, full_name, phone, email, specialty, experience):
        conn = self.connect()
        try:
            conn.execute("INSERT INTO Guides VALUES (?, ?, ?, ?, ?, ?)",
                         (g_id, full_name, phone, email, specialty, experience))
            conn.commit()
            return True, "Thêm thành công!"
        except sqlite3.IntegrityError as e:
            if 'email' in str(e):
                return False, "Email đã tồn tại!"
            return False, "Mã HDV đã tồn tại!"
        finally:
            conn.close()

    def update_guide(self, g_id, full_name, phone, email, specialty, experience):
        conn = self.connect()
        try:
            conn.execute(
                "UPDATE Guides SET full_name=?, phone=?, email=?, specialty=?, experience_years=? WHERE id=?",
                (full_name, phone, email, specialty, experience, g_id))
            conn.commit()
            return True, "Cập nhật thành công!"
        except sqlite3.IntegrityError:
            return False, "Email đã tồn tại!"
        finally:
            conn.close()

    def delete_guide(self, g_id):
        conn = self.connect()
        conn.execute("DELETE FROM Guides WHERE id=?", (g_id,))
        conn.commit()
        conn.close()

    # --- Helpers cho Form Đặt chỗ ---
    def get_schedules_by_tour_for_form(self, tour_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id, s.departure_date || ' [' || s.status || ']' as display
            FROM Schedules s
            WHERE s.tour_id = ? AND s.status IN ('Còn chỗ', 'Sắp khởi hành')
            ORDER BY s.departure_date
        """, (tour_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def search_customers(self, search_text):
        conn = self.connect()
        query = """SELECT id, full_name, phone, email FROM Customers
                   WHERE (full_name LIKE ? OR phone LIKE ? OR email LIKE ?)
                   ORDER BY full_name LIMIT 50"""
        params = [f"%{search_text}%"] * 3
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    # --- Quản lý Thanh toán (Payments) ---
    def get_all_payments(self, search_text=""):
        conn = self.connect()
        query = "SELECT id, booking_id, amount, payment_method, payment_date, transaction_id, status FROM Payments WHERE (id LIKE ? OR booking_id LIKE ?)"
        params = [f"%{search_text}%", f"%{search_text}%"]
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_payment(self, p_id, b_id, amount, method, p_date, trans_id, status):
        conn = self.connect()
        try:
            conn.execute("INSERT INTO Payments VALUES (?, ?, ?, ?, ?, ?, ?)", (p_id, b_id, amount, method, p_date, trans_id, status))
            conn.commit()
            return True, "Thêm thành công!"
        except sqlite3.IntegrityError:
            return False, "Mã Thanh toán đã tồn tại!"
        finally:
            conn.close()
    
    def update_payment(self, p_id, b_id, amount, method, p_date, trans_id, status):
        conn = self.connect()
        conn.execute("UPDATE Payments SET booking_id=?, amount=?, payment_method=?, payment_date=?, transaction_id=?, status=? WHERE id=?", (b_id, amount, method, p_date, trans_id, status, p_id))
        conn.commit()
        conn.close()
    
    def delete_payment(self, p_id):
        conn = self.connect()
        conn.execute("DELETE FROM Payments WHERE id=?", (p_id,))
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
        bookings = cursor.fetchone()[0] # This is fine
        
        cursor.execute("SELECT COUNT(*) FROM Customers")
        customers = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM Schedules
            WHERE departure_date >= date('now') AND booked_slots < max_slots
        """)
        active_schedules = cursor.fetchone()[0]
        
        conn.close()
        return revenue, bookings, customers, active_schedules

    # --- Thống kê nâng cao (Dashboard & Report) ---
    def get_monthly_revenue(self, year=None):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT booking_date, total_price FROM Bookings WHERE status='Đã xác nhận'")
        rows = cursor.fetchall()
        conn.close()
        
        from collections import defaultdict
        from datetime import datetime
        
        revenue_by_month = defaultdict(int)
        for date_str, price in rows:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                if year is None or dt.year == year:
                    revenue_by_month[dt.month] += price
            except ValueError:
                continue
        return revenue_by_month

    def get_tour_booking_ratio(self):
        conn = self.connect()
        query = """
            SELECT t.name, COUNT(b.id) 
            FROM Bookings b
            JOIN Schedules s ON b.schedule_id = s.id
            JOIN Tours t ON s.tour_id = t.id
            WHERE b.status != 'Hủy bỏ'
            GROUP BY t.id
            ORDER BY COUNT(b.id) DESC
        """
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_report_summary(self, year=None):
        conn = self.connect()
        query = """
            SELECT b.booking_date, b.total_price, t.name 
            FROM Bookings b
            JOIN Schedules s ON b.schedule_id = s.id
            JOIN Tours t ON s.tour_id = t.id
            WHERE b.status='Đã xác nhận'
        """
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        from collections import defaultdict
        from datetime import datetime

        summary = defaultdict(lambda: {'revenue': 0, 'bookings': 0, 'tours': defaultdict(int)})

        for date_str, price, tour_name in rows:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                if year is None or dt.year == year:
                    m = dt.month
                    summary[m]['revenue'] += price
                    summary[m]['bookings'] += 1
                    summary[m]['tours'][tour_name] += 1
            except ValueError:
                continue
        return summary

    def get_yearly_revenue_report(self):
        conn = self.connect()
        query = """
            SELECT b.booking_date, b.total_price 
            FROM Bookings b
            WHERE b.status='Đã xác nhận'
        """
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        from collections import defaultdict
        from datetime import datetime

        summary = defaultdict(lambda: {'revenue': 0, 'bookings': 0})

        for date_str, price in rows:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                y = dt.year
                summary[y]['revenue'] += price
                summary[y]['bookings'] += 1
            except ValueError:
                continue
        return summary

    def get_revenue_by_tour_report(self, year=None, month=None):
        conn = self.connect()
        query = """
            SELECT b.booking_date, t.name, b.total_price, b.guest_count 
            FROM Bookings b
            JOIN Schedules s ON b.schedule_id = s.id
            JOIN Tours t ON s.tour_id = t.id
            WHERE b.status='Đã xác nhận'
        """
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        from collections import defaultdict
        from datetime import datetime

        summary = defaultdict(lambda: {'revenue': 0, 'bookings': 0, 'guests': 0})

        for date_str, tour_name, price, guests in rows:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                if (year is None or dt.year == year) and (month is None or dt.month == month):
                    summary[tour_name]['revenue'] += price
                    summary[tour_name]['bookings'] += 1
                    summary[tour_name]['guests'] += guests
            except ValueError:
                continue
        return summary

    def get_all_customers_for_form(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name FROM Customers ORDER BY full_name")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_all_schedules_for_form(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id, t.name || ' - ' || s.departure_date as display_name
            FROM Schedules s JOIN Tours t ON s.tour_id = t.id
            WHERE s.status = 'Còn chỗ'
            ORDER BY t.name, s.departure_date
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_daily_revenue_report(self, year: int, month: int) -> dict:
        import calendar
        num_days = calendar.monthrange(year, month)[1]
        result = {d: {'revenue': 0, 'bookings': 0, 'tours': {}}
                  for d in range(1, num_days + 1)}
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                CAST(strftime('%d', b.booking_date) AS INTEGER) AS day,
                b.total_price,
                b.guest_count,
                t.name AS tour_name
            FROM Bookings b
            JOIN Schedules s ON b.schedule_id = s.id
            JOIN Tours t     ON s.tour_id     = t.id
            WHERE b.status = 'Đã xác nhận'
              AND strftime('%Y', b.booking_date) = ?
              AND strftime('%m', b.booking_date) = ?
        """, (str(year), f"{month:02d}"))
        for day, price, guests, tour_name in cursor.fetchall():
            if day not in result:
                continue
            result[day]['revenue']  += price
            result[day]['bookings'] += 1
            result[day]['tours'][tour_name] = result[day]['tours'].get(tour_name, 0) + guests
        conn.close()
        return result