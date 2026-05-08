import sqlite3
import os
from faker import Faker
import random
from datetime import datetime, timedelta

def init_db():
    conn = sqlite3.connect("tour_management.db")
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # 1. Bảng Users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            address TEXT,
            role TEXT NOT NULL CHECK(role IN ('Admin', 'Staff', 'Customer'))
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Destinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            country TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Tour_Categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # 2. Bảng Tours
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Tours (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            destination_id INTEGER,
            category_id INTEGER,
            duration TEXT,
            description TEXT,
            FOREIGN KEY (destination_id) REFERENCES Destinations(id) ON DELETE SET NULL,
            FOREIGN KEY (category_id) REFERENCES Tour_Categories(id) ON DELETE SET NULL
        )
    ''')

    # 3. Bảng Schedules
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Schedules (
            id TEXT PRIMARY KEY,
            tour_id TEXT NOT NULL,
            departure_date TEXT NOT NULL,
            return_date TEXT,
            max_slots INTEGER NOT NULL,
            booked_slots INTEGER DEFAULT 0,
            status TEXT,
            FOREIGN KEY (tour_id) REFERENCES Tours(id) ON DELETE CASCADE ON UPDATE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Price_Policies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            schedule_id TEXT NOT NULL,
            passenger_type TEXT NOT NULL,
            price INTEGER NOT NULL,
            FOREIGN KEY (schedule_id) REFERENCES Schedules(id) ON DELETE CASCADE,
            UNIQUE(schedule_id, passenger_type)
        )
    ''')

    # 4. Bảng Bookings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Bookings (
            id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            schedule_id TEXT NOT NULL,
            booking_date TEXT NOT NULL,
            guest_count INTEGER NOT NULL,
            total_price INTEGER NOT NULL,
            status TEXT,
            FOREIGN KEY (customer_id) REFERENCES Users(id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (schedule_id) REFERENCES Schedules(id) ON DELETE CASCADE ON UPDATE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Passengers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id TEXT NOT NULL,
            full_name TEXT NOT NULL,
            date_of_birth TEXT,
            gender TEXT,
            passport_number TEXT,
            FOREIGN KEY (booking_id) REFERENCES Bookings(id) ON DELETE CASCADE
        )
    ''')

    # 6. Bảng Payments
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Payments (
            id TEXT PRIMARY KEY,
            booking_id TEXT NOT NULL,
            amount INTEGER NOT NULL,
            payment_method TEXT,
            payment_date TEXT NOT NULL,
            transaction_id TEXT,
            status TEXT,
            FOREIGN KEY (booking_id) REFERENCES Bookings(id) ON DELETE CASCADE ON UPDATE CASCADE
        )
    ''')

    # --- BƠM DỮ LIỆU MẪU ---
    cursor.execute("SELECT COUNT(*) FROM Users")
    if cursor.fetchone()[0] == 0:
        fake = Faker('vi_VN')
        NUM_CUSTOMERS  = 28
        NUM_TOURS      = 30
        NUM_SCHEDULES  = 60
        NUM_BOOKINGS   = 80
        NUM_PAYMENTS   = 70

        print("Bắt đầu tạo dữ liệu mẫu...")

        # 1. Users
        sample_users = [
            ('U001', 'admin', '123456', 'Trần Đức Trường', 'admin@tour.com', '0987654321', 'Hanoi', 'Admin'),
            ('U002', 'staff', '123456', 'Nguyễn Việt Thành', 'staff@tour.com', '0987123456', 'Hanoi', 'Staff'),
        ]
        for i in range(NUM_CUSTOMERS):
            full_name = fake.name()
            username  = fake.unique.user_name()
            sample_users.append(
                (f'C{i+1:03}', username, '123456', full_name,
                 fake.unique.email(), fake.phone_number(), fake.address(), 'Customer')
            )
        cursor.executemany("INSERT INTO Users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", sample_users)
        customer_ids = [u[0] for u in sample_users if u[7] == 'Customer']
        print(f"Đã tạo {len(sample_users)} Users.")

        # 2. Destinations
        destinations = [
            'Hà Giang', 'Cao Bằng', 'Sapa (Lào Cai)', 'Mộc Châu (Sơn La)', 'Mai Châu (Hòa Bình)',
            'Vịnh Hạ Long (Quảng Ninh)', 'Cát Bà (Hải Phòng)', 'Ninh Bình', 'Hà Nội', 'Huế',
            'Đà Nẵng', 'Hội An (Quảng Nam)', 'Quy Nhơn (Bình Định)', 'Nha Trang (Khánh Hòa)', 'Đà Lạt (Lâm Đồng)',
            'Mũi Né (Bình Thuận)', 'Vũng Tàu', 'TP. Hồ Chí Minh', 'Cần Thơ', 'Phú Quốc (Kiên Giang)',
            'Côn Đảo', 'Bangkok (Thái Lan)', 'Chiang Mai (Thái Lan)', 'Singapore', 'Kuala Lumpur (Malaysia)',
            'Bali (Indonesia)', 'Seoul (Hàn Quốc)', 'Tokyo (Nhật Bản)', 'Paris (Pháp)', 'Rome (Ý)'
        ]
        sample_destinations = []
        for dest in destinations:
            country = 'Việt Nam'
            if '(' in dest:
                parts   = dest.split('(')
                name    = parts[0].strip()
                country = parts[1].replace(')', '').strip()
            else:
                name = dest
            sample_destinations.append((name, country))
        cursor.executemany("INSERT INTO Destinations (name, country) VALUES (?, ?)", sample_destinations)
        cursor.execute("SELECT id, name FROM Destinations")
        destinations_data = cursor.fetchall()
        destination_ids   = [row[0] for row in destinations_data]
        destination_map   = {row[0]: row[1] for row in destinations_data}
        print(f"Đã tạo {len(destinations)} Destinations.")

        # 3. Tour Categories
        categories = [
            'Du lịch biển', 'Du lịch văn hóa', 'Du lịch khám phá', 'Trekking & Leo núi', 'Nghỉ dưỡng cao cấp',
            'Du lịch mạo hiểm', 'Tour ẩm thực', 'Tour gia đình', 'Tour Free & Easy', 'Du lịch nước ngoài'
        ]
        cursor.executemany("INSERT INTO Tour_Categories (name) VALUES (?)", [(c,) for c in categories])
        cursor.execute("SELECT id, name FROM Tour_Categories")
        categories_data = cursor.fetchall()
        category_ids    = [row[0] for row in categories_data]
        category_map    = {row[0]: row[1] for row in categories_data}
        print(f"Đã tạo {len(categories)} Tour Categories.")

        # 4. Tours
        sample_tours = []
        for i in range(NUM_TOURS):
            dest_id       = random.choice(destination_ids)
            cat_id        = random.choice(category_ids)
            duration      = f"{random.randint(2,7)}N{random.randint(1,6)}Đ"
            dest_name     = destination_map[dest_id]
            cat_name_full = category_map[cat_id]
            name_templates = [
                f"Khám phá {dest_name} {duration}",
                f"Hành trình {dest_name} kỳ thú",
                f"Tour {cat_name_full}: Trải nghiệm {dest_name}",
                f"Du lịch {dest_name} - Vẻ đẹp bất tận",
                f"Chinh phục {dest_name}",
            ]
            sample_tours.append(
                (f'T{i+1:03}', random.choice(name_templates), dest_id, cat_id,
                 duration, fake.sentence(nb_words=15))
            )
        cursor.executemany("INSERT INTO Tours VALUES (?, ?, ?, ?, ?, ?)", sample_tours)
        tour_ids = [t[0] for t in sample_tours]
        print(f"Đã tạo {len(sample_tours)} Tours.")

        # 5. Schedules & Price Policies
        sample_schedules      = []
        sample_price_policies = []
        today      = datetime.now()
        # Dữ liệu trải từ 3 năm trước đến cuối năm hiện tại (không tạo dữ liệu tương lai)
        start_date = today - timedelta(days=365 * 3)
        end_date   = today  # Không seed quá ngày hôm nay

        for i in range(NUM_SCHEDULES):
            schedule_id  = f'SCH{i+1:03}'
            tour_id      = random.choice(tour_ids)
            departure_dt = fake.date_time_between(start_date=start_date, end_date=end_date)
            duration_days = random.randint(2, 7)
            return_dt    = departure_dt + timedelta(days=duration_days - 1)

            max_slots    = random.choice([20, 25, 30, 35, 40])
            status       = 'Đã kết thúc' if departure_dt < today else 'Còn chỗ'

            sample_schedules.append(
                (schedule_id, tour_id,
                 departure_dt.strftime('%Y-%m-%d'),
                 return_dt.strftime('%Y-%m-%d'),
                 max_slots, 0, status)
            )

            price_adult = random.randint(20, 200) * 100_000
            sample_price_policies.append((schedule_id, 'Người lớn', price_adult))
            if random.random() > 0.3:
                sample_price_policies.append(
                    (schedule_id, 'Trẻ em', int(price_adult * random.uniform(0.6, 0.8)))
                )
            if random.random() > 0.8:
                sample_price_policies.append(
                    (schedule_id, 'Em bé', int(price_adult * random.uniform(0.1, 0.3)))
                )

        cursor.executemany("INSERT INTO Schedules VALUES (?, ?, ?, ?, ?, ?, ?)", sample_schedules)
        cursor.executemany(
            "INSERT INTO Price_Policies (schedule_id, passenger_type, price) VALUES (?, ?, ?)",
            sample_price_policies
        )
        schedule_ids = [s[0] for s in sample_schedules]
        print(f"Đã tạo {len(sample_schedules)} Schedules và {len(sample_price_policies)} Price Policies.")

        # 7. Bookings & Passengers
        sample_bookings          = []
        sample_passengers        = []
        bookings_to_update_slots = {}

        for i in range(NUM_BOOKINGS):
            booking_id   = f'BK{i+1:03}'
            customer_id  = random.choice(customer_ids)
            schedule_id  = random.choice(schedule_ids)

            cursor.execute(
                "SELECT departure_date, max_slots FROM Schedules WHERE id=?",
                (schedule_id,)
            )
            schedule_info = cursor.fetchone()
            if not schedule_info:
                continue

            departure_date = datetime.strptime(schedule_info[0], '%Y-%m-%d')
            max_slots      = schedule_info[1]

            # booking_date phải trước ngày khởi hành
            earliest_booking = departure_date - timedelta(days=90)
            if earliest_booking >= departure_date - timedelta(days=1):
                continue
            booking_date = fake.date_time_between(
                start_date=earliest_booking,
                end_date=departure_date - timedelta(days=1)
            )

            current_booked  = bookings_to_update_slots.get(schedule_id, 0)
            available_slots = max_slots - current_booked
            if available_slots <= 0:
                continue
            guest_count = random.randint(1, min(5, available_slots))

            cursor.execute(
                "SELECT price FROM Price_Policies WHERE schedule_id=? AND passenger_type='Người lớn'",
                (schedule_id,)
            )
            adult_price = (cursor.fetchone() or [3_000_000])[0]
            total_price = adult_price * guest_count
            status      = random.choice(['Đã xác nhận', 'Chờ xử lý', 'Đã hủy'])

            sample_bookings.append((
                booking_id, customer_id, schedule_id,
                booking_date.strftime('%Y-%m-%d'),
                guest_count, total_price, status
            ))

            if status == 'Đã xác nhận':
                bookings_to_update_slots[schedule_id] = (
                    bookings_to_update_slots.get(schedule_id, 0) + guest_count
                )

            for _ in range(guest_count):
                sample_passengers.append((
                    booking_id, fake.name(),
                    fake.date_of_birth(minimum_age=1, maximum_age=80).strftime('%Y-%m-%d'),
                    random.choice(['Nam', 'Nữ']), None
                ))

        cursor.executemany("INSERT INTO Bookings VALUES (?, ?, ?, ?, ?, ?, ?)", sample_bookings)
        cursor.executemany(
            "INSERT INTO Passengers (booking_id, full_name, date_of_birth, gender, passport_number) VALUES (?, ?, ?, ?, ?)",
            sample_passengers
        )
        print(f"Đã tạo {len(sample_bookings)} Bookings và {len(sample_passengers)} Passengers.")

        for schedule_id, total_booked in bookings_to_update_slots.items():
            cursor.execute("UPDATE Schedules SET booked_slots = ? WHERE id = ?", (total_booked, schedule_id))
            cursor.execute(
                "UPDATE Schedules SET status = 'Hết chỗ' WHERE id = ? AND max_slots <= booked_slots",
                (schedule_id,)
            )

        # 9. Payments
        cursor.execute("SELECT id, total_price, booking_date FROM Bookings WHERE status != 'Đã hủy'")
        payable_bookings = cursor.fetchall()
        sample_payments  = []
        for i in range(NUM_PAYMENTS):
            if not payable_bookings:
                break
            booking_id, total_price, booking_date_str = random.choice(payable_bookings)
            booking_date   = datetime.strptime(booking_date_str, '%Y-%m-%d')
            payment_date   = fake.date_time_between(
                start_date=booking_date,
                end_date=min(booking_date + timedelta(days=7), today)
            )
            payment_status = random.choice(['Thành công', 'Đang chờ', 'Thất bại', 'Hoàn tiền'])
            amount = total_price if random.random() > 0.3 else int(total_price * random.uniform(0.3, 0.5))
            sample_payments.append((
                f'PAY{i+1:03}', booking_id, amount,
                random.choice(['Chuyển khoản', 'Tiền mặt', 'Thẻ tín dụng']),
                payment_date.strftime('%Y-%m-%d'),
                fake.bothify(text='TRN-?#?#?#?#').upper(),
                payment_status
            ))
        cursor.executemany("INSERT INTO Payments VALUES (?, ?, ?, ?, ?, ?, ?)", sample_payments)
        print(f"Đã tạo {len(sample_payments)} Payments.")

    conn.commit()
    conn.close()
    print("Cơ sở dữ liệu đã được khởi tạo thành công!")


def reset_and_seed_db():
    db_file = "tour_management.db"
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"Đã xóa file database cũ: {db_file}")
    init_db()


if __name__ == "__main__":
    reset_and_seed_db()