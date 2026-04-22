import sqlite3

def init_db():
    conn = sqlite3.connect("tour_management.db")
    cursor = conn.cursor()

    # Bảng Tours
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Tours (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            destination TEXT,
            duration TEXT,
            price INTEGER,
            status TEXT
        )
    ''')

    # Bảng Customers
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Customers (
            id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT,
            phone TEXT
        )
    ''')

    # Bảng Bookings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Bookings (
            id TEXT PRIMARY KEY,
            customer_name TEXT,
            tour_name TEXT,
            booking_date TEXT,
            guest_count INTEGER,
            total_price INTEGER,
            status TEXT
        )
    ''')

    # Bảng Users (Đưa lên đây để tạo cùng lúc)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # --- BƠM DỮ LIỆU MẪU ---
    
    # Dữ liệu Tour, Khách hàng, Đặt chỗ
    cursor.execute("SELECT COUNT(*) FROM Tours")
    if cursor.fetchone()[0] == 0:
        sample_tours = [
            ("T001", "Khám phá Vịnh Hạ Long", "Quảng Ninh", "3N2Đ", 3500000, "Hoạt động"),
            ("T002", "Hành trình Di sản Miền Trung", "Đà Nẵng", "4N3Đ", 5200000, "Hoạt động"),
            ("T003", "Chinh phục Sapa", "Lào Cai", "2N1Đ", 1800000, "Tạm dừng")
        ]
        cursor.executemany("INSERT INTO Tours VALUES (?, ?, ?, ?, ?, ?)", sample_tours)

        sample_customers = [
            ("KH001", "Nguyễn Văn A", "nva@email.com", "0901234567"),
            ("KH002", "Trần Thị B", "ttb@email.com", "0918765432")
        ]
        cursor.executemany("INSERT INTO Customers VALUES (?, ?, ?, ?)", sample_customers)

        sample_bookings = [
            ("BK001", "Nguyễn Văn A", "Khám phá Vịnh Hạ Long", "10/12/2023", 2, 7000000, "Đã xác nhận"),
            ("BK002", "Trần Thị B", "Hành trình Di sản Miền Trung", "05/12/2023", 4, 20800000, "Chờ xử lý")
        ]
        cursor.executemany("INSERT INTO Bookings VALUES (?, ?, ?, ?, ?, ?, ?)", sample_bookings)

    # Dữ liệu Users
    cursor.execute("SELECT COUNT(*) FROM Users")
    if cursor.fetchone()[0] == 0:
        sample_users = [
            ("admin", "123456", "Admin"),    # Tài khoản Quản lý
            ("staff", "123456", "Staff")     # Tài khoản Nhân viên
        ]
        cursor.executemany("INSERT INTO Users VALUES (?, ?, ?)", sample_users)

    # LƯU VÀ ĐÓNG KẾT NỐI (Chỉ gọi 1 lần duy nhất ở cuối cùng)
    conn.commit()
    conn.close()
    print("Cập nhật Database thành công! Đã tạo đầy đủ các bảng.")

if __name__ == "__main__":
    init_db()