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
            role TEXT NOT NULL CHECK(role IN ('Admin', 'Staff'))
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Customers (
            id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            address TEXT
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

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Guides (
            id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            phone TEXT,
            email TEXT UNIQUE,
            specialty TEXT,
            experience_years INTEGER DEFAULT 0
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
            guide_name TEXT,
            FOREIGN KEY (tour_id) REFERENCES Tours(id) ON DELETE CASCADE ON UPDATE CASCADE
        )
    ''')
    # Migration: thêm cột guide_name nếu DB cũ chưa có
    try:
        cursor.execute("ALTER TABLE Schedules ADD COLUMN guide_name TEXT")
    except sqlite3.OperationalError:
        pass

    # Migration: cập nhật lại status theo ngày thực tế (sửa dữ liệu cũ bị stale)
    cursor.execute("""
        UPDATE Schedules SET status =
            CASE
                WHEN departure_date < date('now')                          THEN 'Đã kết thúc'
                WHEN booked_slots >= max_slots                             THEN 'Hết chỗ'
                WHEN departure_date <= date('now', '+3 days')              THEN 'Sắp khởi hành'
                ELSE 'Còn chỗ'
            END
    """)

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
            FOREIGN KEY (customer_id) REFERENCES Customers(id) ON DELETE CASCADE ON UPDATE CASCADE,
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
        cursor.executemany("INSERT INTO Users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", sample_users)
        print(f"Đã tạo {len(sample_users)} Users (Admin/Staff).")

        # 1b. Guides
        sample_guides = [
            ('GD001', 'Trần Minh Tuấn',   '0912 345 001', 'tuan.tran@guide.com',   'Miền Bắc',             8),
            ('GD002', 'Nguyễn Thị Hoa',   '0912 345 002', 'hoa.nguyen@guide.com',  'Quốc tế',              5),
            ('GD003', 'Lê Văn Bình',       '0912 345 003', 'binh.le@guide.com',     'Miền Trung',           6),
            ('GD004', 'Phạm Thu Thảo',     '0912 345 004', 'thao.pham@guide.com',   'Miền Nam',             4),
            ('GD005', 'Hoàng Đức Long',    '0912 345 005', 'long.hoang@guide.com',  'Sinh thái & Trekking', 10),
            ('GD006', 'Đặng Thị Mai',      '0912 345 006', 'mai.dang@guide.com',    'Văn hóa - Lịch sử',   7),
            ('GD007', 'Vũ Quang Huy',      '0912 345 007', 'huy.vu@guide.com',      'Quốc tế',              3),
            ('GD008', 'Bùi Thị Lan',       '0912 345 008', 'lan.bui@guide.com',     'Miền Nam',             9),
            ('GD009', 'Phan Văn Tùng',     '0912 345 009', 'tung.phan@guide.com',   'Tây Nguyên',           5),
            ('GD010', 'Đinh Thị Yến',      '0912 345 010', 'yen.dinh@guide.com',    'Miền Bắc',             6),
            ('GD011', 'Hà Minh Khoa',      '0912 345 011', 'khoa.ha@guide.com',     'Sinh thái & Trekking', 4),
            ('GD012', 'Trịnh Thu Hương',   '0912 345 012', 'huong.trinh@guide.com', 'Quốc tế',              8),
            ('GD013', 'Ngô Đức Thành',     '0912 345 013', 'thanh.ngo@guide.com',   'Miền Trung',           3),
            ('GD014', 'Cao Thị Phượng',    '0912 345 014', 'phuong.cao@guide.com',  'Miền Nam',             7),
            ('GD015', 'Lý Văn Nam',        '0912 345 015', 'nam.ly@guide.com',      'Văn hóa - Lịch sử',   5),
        ]
        cursor.executemany("INSERT INTO Guides VALUES (?, ?, ?, ?, ?, ?)", sample_guides)
        print(f"Đã tạo {len(sample_guides)} Hướng dẫn viên.")

        sample_customers = []
        for i in range(NUM_CUSTOMERS):
            full_name = fake.name()
            sample_customers.append(
                (f'C{i+1:03}', full_name, fake.unique.email(), fake.phone_number(), fake.address())
            )
        cursor.executemany("INSERT INTO Customers VALUES (?, ?, ?, ?, ?)", sample_customers)
        customer_ids = [c[0] for c in sample_customers]
        print(f"Đã tạo {len(sample_customers)} Customers.")

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
        _TOUR_DESCS = {
            'Du lịch biển': [
                "Tận hưởng kỳ nghỉ tuyệt vời bên bãi biển trong xanh, ngắm hoàng hôn lung linh và thưởng thức hải sản tươi ngon. Tour bao gồm lặn biển, chèo kayak và tham quan các đảo lân cận.",
                "Khám phá thiên đường biển đảo với làn nước xanh trong vắt và bãi cát trắng mịn. Trải nghiệm snorkeling, câu cá và thưởng thức ẩm thực biển đặc trưng của địa phương.",
                "Chuyến biển lý tưởng để thư giãn và tái tạo năng lượng. Nghỉ tại khách sạn ven biển, tiệc hải sản BBQ tối và ngắm bình minh trên sóng nước.",
            ],
            'Du lịch văn hóa': [
                "Hành trình khám phá chiều sâu văn hóa và lịch sử qua các di tích, đền đài, phố cổ và bảo tàng nổi tiếng. Cơ hội tìm hiểu phong tục tập quán và thưởng thức ẩm thực truyền thống đặc sắc.",
                "Trải nghiệm văn hóa địa phương phong phú qua các lễ hội truyền thống, làng nghề thủ công và kiến trúc cổ kính. Đặc biệt ấn tượng với ẩm thực đường phố đa dạng và độc đáo.",
                "Khám phá kho tàng văn hóa đặc sắc với những di sản được UNESCO công nhận, các công trình kiến trúc cổ xưa và câu chuyện lịch sử hào hùng qua từng địa danh.",
            ],
            'Du lịch khám phá': [
                "Cuộc hành trình khám phá những vùng đất còn hoang sơ và bí ẩn, nơi thiên nhiên hùng vĩ gặp gỡ văn hóa bản địa độc đáo. Phù hợp với những tâm hồn ưa phiêu lưu và yêu thích khám phá.",
                "Chuyến đi đưa bạn tới những địa danh ít người biết đến, trải nghiệm cuộc sống của người dân địa phương và khám phá những danh thắng thiên nhiên tuyệt đẹp chưa được khai phá.",
                "Hành trình khám phá vùng đất đầy cuốn hút với cảnh quan thiên nhiên ngoạn mục, hệ sinh thái đa dạng và những trải nghiệm văn hóa bản địa không thể quên.",
            ],
            'Trekking & Leo núi': [
                "Chinh phục những đỉnh núi hùng vĩ với cung đường trekking qua rừng già, thác nước và bản làng dân tộc thiểu số. Phù hợp với những người yêu thích mạo hiểm và muốn thử thách giới hạn bản thân.",
                "Hành trình trekking xuyên rừng nguyên sinh, ngắm nhìn toàn cảnh núi non hùng vĩ từ đỉnh cao. Cắm trại giữa thiên nhiên hoang dã, thưởng thức ẩm thực dân tộc và giao lưu cùng người bản địa.",
                "Trải nghiệm leo núi đầy hứng khởi qua các cung đường đẹp mê hồn, bắt gặp nhiều loài động thực vật quý hiếm. Thích hợp cho cả người mới bắt đầu lẫn dân trekking có kinh nghiệm.",
            ],
            'Nghỉ dưỡng cao cấp': [
                "Kỳ nghỉ sang trọng tại resort 5 sao với đầy đủ tiện nghi hiện đại, dịch vụ spa cao cấp và hồ bơi vô cực tuyệt đẹp. Thực đơn ẩm thực quốc tế tinh tế phục vụ suốt ngày.",
                "Trải nghiệm nghỉ dưỡng đẳng cấp với phòng Suite view biển hoặc núi, breakfast và dinner tại nhà hàng cao cấp, massage thư giãn và các tiện ích wellness trọn gói.",
                "Đắm chìm trong không gian nghỉ dưỡng xa hoa tại khu boutique resort riêng tư. Dịch vụ butler cá nhân, hồ bơi riêng và trải nghiệm ẩm thực fusion độc đáo của đầu bếp địa phương.",
            ],
            'Du lịch mạo hiểm': [
                "Thách thức giới hạn bản thân với các hoạt động mạo hiểm như zipline, vượt thác, leo vách đá và cắm trại trong rừng sâu. Tour được thiết kế cho những người ưa cảm giác mạnh.",
                "Khám phá thiên nhiên hoang dã qua các trải nghiệm phiêu lưu như chèo kayak vượt ghềnh thác, leo núi đá và đi bộ xuyên rừng già hùng vĩ cùng hướng dẫn viên chuyên nghiệp.",
                "Hành trình mạo hiểm đích thực với thám hiểm hang động, SUP trên sông và trekking qua địa hình hiểm trở. Tour dành cho những tâm hồn không ngại thử thách và luôn tìm kiếm cảm xúc mới.",
            ],
            'Tour ẩm thực': [
                "Hành trình ẩm thực khám phá tinh hoa ẩm thực địa phương qua các buổi tham quan chợ đêm, lớp học nấu ăn truyền thống và thưởng thức đặc sản vùng miền không thể bỏ lỡ.",
                "Chuyến du lịch dành riêng cho tín đồ ẩm thực, trải nghiệm các món ăn đặc trưng qua nhà hàng nổi tiếng, quán vỉa hè đậm chất địa phương và gia đình người dân bản xứ.",
                "Khám phá nền ẩm thực phong phú qua cooking class, food tour và tham quan cơ sở sản xuất thực phẩm truyền thống. Mang về những công thức và bí quyết nấu ăn độc đáo khó tìm ở đâu khác.",
            ],
            'Tour gia đình': [
                "Kỳ nghỉ lý tưởng cho cả gia đình với các hoạt động vui chơi phong phú, phù hợp mọi lứa tuổi. Trẻ em sẽ có những trải nghiệm học hỏi thú vị bên cạnh những giây phút vui vẻ cùng ba mẹ.",
                "Tạo nên kỷ niệm đáng nhớ cùng gia đình qua hành trình khám phá điểm đến an toàn, thú vị. Hướng dẫn viên chuyên nghiệp chăm sóc chu đáo cho cả người lớn lẫn trẻ nhỏ trong suốt chuyến đi.",
                "Chuyến đi gia đình trọn vẹn với xe đưa đón riêng, khách sạn tiêu chuẩn family room và lịch trình linh hoạt để mọi thành viên đều tận hưởng kỳ nghỉ theo cách riêng của mình.",
            ],
            'Tour Free & Easy': [
                "Tự do khám phá điểm đến theo cách riêng của bạn với gói vé máy bay khứ hồi và khách sạn đã được sắp xếp sẵn. Thời gian còn lại hoàn toàn thuộc về bạn để trải nghiệm địa phương tùy ý.",
                "Gói Free & Easy lý tưởng cho người thích tự do: vé bay và phòng khách sạn đã bao gồm, bạn tự lên kế hoạch từng ngày. Phù hợp với du khách độc lập muốn trải nghiệm theo phong cách riêng.",
                "Hành trình không có lịch trình cố định, chỉ cần vé máy bay và phòng khách sạn là đủ. Tự khám phá địa phương, ăn uống tùy chọn và tận hưởng chuyến đi theo nhịp sống của chính mình.",
            ],
            'Du lịch nước ngoài': [
                "Hành trình khám phá xứ sở xa xôi với văn hóa độc đáo, ẩm thực hấp dẫn và những kỳ quan thiên nhiên nổi tiếng thế giới. Tour trọn gói bao gồm visa, vé máy bay và hướng dẫn viên song ngữ.",
                "Chuyến du lịch nước ngoài trọn gói với lịch trình được thiết kế chi tiết, khách sạn tiêu chuẩn quốc tế và hướng dẫn viên thông thạo ngôn ngữ địa phương để đảm bảo trải nghiệm tốt nhất.",
                "Trải nghiệm đất nước và con người ở xứ sở mới lạ qua hành trình tham quan các địa danh nổi tiếng, thưởng thức ẩm thực bản địa và mua sắm đặc sản mang về làm quà.",
            ],
        }

        _NAME_TEMPLATES = [
            lambda d, c, dur: f"Khám phá {d} {dur}",
            lambda d, c, dur: f"Hành trình {d} kỳ thú",
            lambda d, c, dur: f"Du lịch {d} - Vẻ đẹp bất tận",
            lambda d, c, dur: f"Chinh phục {d}",
            lambda d, c, dur: f"Trải nghiệm {d} {dur}",
            lambda d, c, dur: f"{d} - Hành trình đáng nhớ",
            lambda d, c, dur: f"Tour {d} {dur}",
            lambda d, c, dur: f"Khám phá {d} cùng {c}",
        ]

        sample_tours = []
        for i in range(NUM_TOURS):
            dest_id       = random.choice(destination_ids)
            cat_id        = random.choice(category_ids)
            duration      = f"{random.randint(2,7)}N{random.randint(1,6)}Đ"
            dest_name     = destination_map[dest_id]
            cat_name_full = category_map[cat_id]
            tour_name     = random.choice(_NAME_TEMPLATES)(dest_name, cat_name_full, duration)
            descs         = _TOUR_DESCS.get(cat_name_full, _TOUR_DESCS['Du lịch khám phá'])
            description   = random.choice(descs)
            sample_tours.append(
                (f'T{i+1:03}', tour_name, dest_id, cat_id, duration, description)
            )
        cursor.executemany("INSERT INTO Tours VALUES (?, ?, ?, ?, ?, ?)", sample_tours)
        tour_ids = [t[0] for t in sample_tours]
        print(f"Đã tạo {len(sample_tours)} Tours.")

        # 5. Schedules & Price Policies
        GUIDE_NAMES = [
            'Trần Minh Tuấn', 'Nguyễn Thị Hoa', 'Lê Văn Bình', 'Phạm Thu Thảo',
            'Hoàng Đức Long', 'Đặng Thị Mai', 'Vũ Quang Huy', 'Bùi Thị Lan',
            'Phan Văn Tùng', 'Đinh Thị Yến', 'Hà Minh Khoa', 'Trịnh Thu Hương',
            'Ngô Đức Thành', 'Cao Thị Phượng', 'Lý Văn Nam',
        ]

        sample_schedules      = []
        sample_price_policies = []
        today      = datetime.now()
        start_date = today - timedelta(days=365 * 3)
        end_date   = today + timedelta(days=180)  # Tạo cả lịch tương lai 6 tháng tới

        for i in range(NUM_SCHEDULES):
            schedule_id  = f'SCH{i+1:03}'
            tour_id      = random.choice(tour_ids)
            departure_dt = fake.date_time_between(start_date=start_date, end_date=end_date)
            duration_days = random.randint(2, 7)
            return_dt    = departure_dt + timedelta(days=duration_days - 1)

            max_slots    = random.choice([20, 25, 30, 35, 40])
            dep_date_only = departure_dt.date()
            today_date    = today.date()
            if dep_date_only < today_date:
                status = 'Đã kết thúc'
            elif dep_date_only <= today_date + timedelta(days=3):
                status = 'Sắp khởi hành'
            else:
                status = 'Còn chỗ'

            sample_schedules.append(
                (schedule_id, tour_id,
                 departure_dt.strftime('%Y-%m-%d'),
                 return_dt.strftime('%Y-%m-%d'),
                 max_slots, 0, status,
                 random.choice(GUIDE_NAMES))
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

        cursor.executemany(
            "INSERT INTO Schedules (id, tour_id, departure_date, return_date, max_slots, booked_slots, status, guide_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            sample_schedules)
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

        # Điều chỉnh booked_slots theo tỉ lệ hợp lý cho từng trạng thái
        cursor.execute("SELECT id, max_slots, status FROM Schedules")
        for sch_id, max_sl, sch_status in cursor.fetchall():
            real_booked = bookings_to_update_slots.get(sch_id, 0)
            if sch_status == 'Đã kết thúc':
                # Lịch đã kết thúc: thực tế thường đạt 60-100% chỗ
                lo, hi = int(max_sl * 0.60), max_sl
            elif sch_status == 'Sắp khởi hành':
                # Sắp khởi hành: gần đầy, 75-100%
                lo, hi = int(max_sl * 0.75), max_sl
            else:
                # Còn chỗ (tương lai): đã có người đặt trước, 5-55%
                lo, hi = max(1, int(max_sl * 0.05)), int(max_sl * 0.55)

            target  = random.randint(lo, hi)
            booked  = min(max(real_booked, target), max_sl)
            new_status = 'Hết chỗ' if booked >= max_sl else sch_status
            cursor.execute(
                "UPDATE Schedules SET booked_slots=?, status=? WHERE id=?",
                (booked, new_status, sch_id)
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

    _GUIDE_NAMES = [
        'Trần Minh Tuấn', 'Nguyễn Thị Hoa', 'Lê Văn Bình', 'Phạm Thu Thảo',
        'Hoàng Đức Long', 'Đặng Thị Mai', 'Vũ Quang Huy', 'Bùi Thị Lan',
        'Phan Văn Tùng', 'Đinh Thị Yến', 'Hà Minh Khoa', 'Trịnh Thu Hương',
        'Ngô Đức Thành', 'Cao Thị Phượng', 'Lý Văn Nam',
    ]

    # Migration: seed bảng Guides nếu chưa có dữ liệu
    cursor.execute("SELECT COUNT(*) FROM Guides")
    if cursor.fetchone()[0] == 0:
        _mig_guides = [
            ('GD001', 'Trần Minh Tuấn',   '0912 345 001', 'tuan.tran@guide.com',   'Miền Bắc',             8),
            ('GD002', 'Nguyễn Thị Hoa',   '0912 345 002', 'hoa.nguyen@guide.com',  'Quốc tế',              5),
            ('GD003', 'Lê Văn Bình',       '0912 345 003', 'binh.le@guide.com',     'Miền Trung',           6),
            ('GD004', 'Phạm Thu Thảo',     '0912 345 004', 'thao.pham@guide.com',   'Miền Nam',             4),
            ('GD005', 'Hoàng Đức Long',    '0912 345 005', 'long.hoang@guide.com',  'Sinh thái & Trekking', 10),
            ('GD006', 'Đặng Thị Mai',      '0912 345 006', 'mai.dang@guide.com',    'Văn hóa - Lịch sử',   7),
            ('GD007', 'Vũ Quang Huy',      '0912 345 007', 'huy.vu@guide.com',      'Quốc tế',              3),
            ('GD008', 'Bùi Thị Lan',       '0912 345 008', 'lan.bui@guide.com',     'Miền Nam',             9),
            ('GD009', 'Phan Văn Tùng',     '0912 345 009', 'tung.phan@guide.com',   'Tây Nguyên',           5),
            ('GD010', 'Đinh Thị Yến',      '0912 345 010', 'yen.dinh@guide.com',    'Miền Bắc',             6),
            ('GD011', 'Hà Minh Khoa',      '0912 345 011', 'khoa.ha@guide.com',     'Sinh thái & Trekking', 4),
            ('GD012', 'Trịnh Thu Hương',   '0912 345 012', 'huong.trinh@guide.com', 'Quốc tế',              8),
            ('GD013', 'Ngô Đức Thành',     '0912 345 013', 'thanh.ngo@guide.com',   'Miền Trung',           3),
            ('GD014', 'Cao Thị Phượng',    '0912 345 014', 'phuong.cao@guide.com',  'Miền Nam',             7),
            ('GD015', 'Lý Văn Nam',        '0912 345 015', 'nam.ly@guide.com',      'Văn hóa - Lịch sử',   5),
        ]
        cursor.executemany("INSERT OR IGNORE INTO Guides VALUES (?, ?, ?, ?, ?, ?)", _mig_guides)
        print(f"Migration: Đã tạo {len(_mig_guides)} hướng dẫn viên.")

    # Migration: điền HDV cho các lịch chưa có
    cursor.execute("SELECT id FROM Schedules WHERE guide_name IS NULL OR guide_name = ''")
    no_guide = [r[0] for r in cursor.fetchall()]
    for s_id in no_guide:
        cursor.execute("UPDATE Schedules SET guide_name = ? WHERE id = ?",
                       (random.choice(_GUIDE_NAMES), s_id))
    if no_guide:
        print(f"Migration: Đã điền hướng dẫn viên cho {len(no_guide)} lịch.")

    # Migration: tạo lịch tương lai nếu DB cũ không có lịch nào sau hôm nay
    cursor.execute("SELECT COUNT(*) FROM Schedules WHERE departure_date > date('now')")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT id FROM Tours ORDER BY RANDOM() LIMIT 15")
        future_tour_ids = [r[0] for r in cursor.fetchall()]
        if future_tour_ids:
            cursor.execute("SELECT MAX(CAST(SUBSTR(id,4) AS INTEGER)) FROM Schedules WHERE id LIKE 'SCH%'")
            row = cursor.fetchone()
            next_num = (row[0] or 0) + 1
            from datetime import date as _date
            today_d = _date.today()
            for j, t_id in enumerate(future_tour_ids):
                dep = today_d + timedelta(days=random.randint(10, 150))
                ret = dep + timedelta(days=random.randint(2, 6))
                s_id = f'SCH{next_num + j:03}'
                guide = random.choice(_GUIDE_NAMES)
                cursor.execute(
                    "INSERT INTO Schedules (id, tour_id, departure_date, return_date, max_slots, booked_slots, status, guide_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (s_id, t_id, dep.isoformat(), ret.isoformat(), random.choice([20, 25, 30]), 0, 'Còn chỗ', guide)
                )
                price_adult = random.randint(20, 200) * 100_000
                cursor.execute(
                    "INSERT OR IGNORE INTO Price_Policies (schedule_id, passenger_type, price) VALUES (?, ?, ?)",
                    (s_id, 'Người lớn', price_adult)
                )
                cursor.execute(
                    "INSERT OR IGNORE INTO Price_Policies (schedule_id, passenger_type, price) VALUES (?, ?, ?)",
                    (s_id, 'Trẻ em', int(price_adult * 0.7))
                )
            print(f"Migration: Đã tạo {len(future_tour_ids)} lịch khởi hành tương lai.")

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