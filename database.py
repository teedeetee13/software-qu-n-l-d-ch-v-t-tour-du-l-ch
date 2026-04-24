import sqlite3
import os

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
            ("T003", "Chinh phục Sapa", "Lào Cai", "2N1Đ", 1800000, "Hoạt động"),
            ("T004", "Nghỉ dưỡng Phú Quốc", "Kiên Giang", "3N2Đ", 4500000, "Hoạt động"),
            ("T005", "Khám phá Đà Lạt", "Lâm Đồng", "3N2Đ", 2800000, "Hoạt động"),
            ("T006", "Tour miền Tây sông nước", "Cần Thơ", "2N1Đ", 1500000, "Hoạt động"),
            ("T007", "Kỳ nghỉ Nha Trang", "Khánh Hòa", "4N3Đ", 4200000, "Tạm dừng")
        ]
        cursor.executemany("INSERT INTO Tours VALUES (?, ?, ?, ?, ?, ?)", sample_tours)

        sample_customers = [
            ("KH001", "Nguyễn Văn A", "nva@email.com", "0901234567"),
            ("KH002", "Trần Thị B", "ttb@email.com", "0918765432"),
            ("KH003", "Lê Văn C", "lvc@email.com", "0987654321"),
            ("KH004", "Phạm Thị D", "ptd@email.com", "0933445566"),
            ("KH005", "Hoàng Văn E", "hve@email.com", "0977889900"),
            ("KH006", "Vũ Thị F", "vtf@email.com", "0909112233"),
            ("KH007", "Đặng Văn G", "dvg@email.com", "0944556677"),
            ("KH008", "Bùi Thị H", "bth@email.com", "0912345678"),
            ("KH009", "Đỗ Văn I", "dvi@email.com", "0988776655"),
            ("KH010", "Ngô Thị K", "ntk@email.com", "0966554433")
        ]
        cursor.executemany("INSERT INTO Customers VALUES (?, ?, ?, ?)", sample_customers)

        sample_bookings = [
            # 2023 Bookings
            ("BK001", "Nguyễn Văn A", "Khám phá Vịnh Hạ Long", "15/01/2023", 2, 7000000, "Đã xác nhận"),
            ("BK002", "Trần Thị B", "Chinh phục Sapa", "20/02/2023", 3, 5400000, "Đã xác nhận"),
            ("BK003", "Lê Văn C", "Nghỉ dưỡng Phú Quốc", "10/03/2023", 2, 9000000, "Đã xác nhận"),
            ("BK004", "Phạm Thị D", "Hành trình Di sản Miền Trung", "05/04/2023", 4, 20800000, "Hủy bỏ"),
            ("BK005", "Hoàng Văn E", "Khám phá Đà Lạt", "22/05/2023", 2, 5600000, "Đã xác nhận"),
            ("BK006", "Vũ Thị F", "Tour miền Tây sông nước", "18/06/2023", 5, 7500000, "Đã xác nhận"),
            ("BK007", "Đặng Văn G", "Khám phá Vịnh Hạ Long", "12/07/2023", 2, 7000000, "Đã xác nhận"),
            ("BK008", "Bùi Thị H", "Nghỉ dưỡng Phú Quốc", "25/08/2023", 4, 18000000, "Đã xác nhận"),
            ("BK009", "Đỗ Văn I", "Chinh phục Sapa", "10/09/2023", 2, 3600000, "Đã xác nhận"),
            ("BK010", "Ngô Thị K", "Hành trình Di sản Miền Trung", "05/10/2023", 3, 15600000, "Đã xác nhận"),
            ("BK011", "Nguyễn Văn A", "Khám phá Đà Lạt", "20/11/2023", 2, 5600000, "Đã xác nhận"),
            ("BK012", "Trần Thị B", "Khám phá Vịnh Hạ Long", "15/12/2023", 4, 14000000, "Đã xác nhận"),
            # 2024 Bookings
            ("BK013", "Lê Văn C", "Nghỉ dưỡng Phú Quốc", "05/01/2024", 2, 9000000, "Đã xác nhận"),
            ("BK014", "Phạm Thị D", "Tour miền Tây sông nước", "12/02/2024", 3, 4500000, "Đã xác nhận"),
            ("BK015", "Hoàng Văn E", "Chinh phục Sapa", "20/03/2024", 2, 3600000, "Đã xác nhận"),
            ("BK016", "Vũ Thị F", "Khám phá Vịnh Hạ Long", "15/04/2024", 5, 17500000, "Đã xác nhận"),
            ("BK017", "Đặng Văn G", "Khám phá Đà Lạt", "25/05/2024", 2, 5600000, "Đã xác nhận"),
            ("BK018", "Bùi Thị H", "Hành trình Di sản Miền Trung", "10/06/2024", 4, 20800000, "Đã xác nhận"),
            ("BK019", "Đỗ Văn I", "Nghỉ dưỡng Phú Quốc", "22/07/2024", 2, 9000000, "Chờ xử lý"),
            ("BK020", "Ngô Thị K", "Khám phá Vịnh Hạ Long", "18/08/2024", 3, 10500000, "Đã xác nhận"),
            ("BK021", "Nguyễn Văn A", "Tour miền Tây sông nước", "05/09/2024", 4, 6000000, "Đã xác nhận"),
            ("BK022", "Trần Thị B", "Chinh phục Sapa", "15/10/2024", 2, 3600000, "Đã xác nhận"),
            ("BK023", "Lê Văn C", "Khám phá Đà Lạt", "20/11/2024", 3, 8400000, "Đã xác nhận"),
            ("BK024", "Phạm Thị D", "Nghỉ dưỡng Phú Quốc", "10/12/2024", 5, 22500000, "Chờ xử lý")
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

def reset_and_seed_db():
    db_file = "tour_management.db"
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"Đã xóa file database cũ: {db_file}")
    
    init_db()

if __name__ == "__main__":
    # Chạy hàm này sẽ luôn tạo lại DB từ đầu với dữ liệu mẫu mới nhất
    reset_and_seed_db()