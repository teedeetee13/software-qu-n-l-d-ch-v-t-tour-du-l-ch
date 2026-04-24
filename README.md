# Phần mềm Quản lý Dịch vụ Đặt Tour Du lịch (Admin Panel)

## 1. Thành viên thực hiện
- Trần Đức Trường - 20233802
- Nguyễn Việt Thành - 2023....
- Trần Đức Duy - 2023....

## 2. Mô tả tổng quan
Đây là một ứng dụng Desktop được xây dựng bằng Python với giao diện đồ họa `CustomTkinter`, đóng vai trò là một hệ thống quản trị (Admin Panel) cho một công ty du lịch. Ứng dụng cho phép quản trị viên và nhân viên quản lý các hoạt động cốt lõi như tour, đặt chỗ, khách hàng và xem các báo cáo thống kê.

## 3. Công nghệ sử dụng
- **Ngôn ngữ lập trình:** Python 3
- **Giao diện đồ họa (GUI):** `CustomTkinter` để tạo giao diện hiện đại và tùy biến cao.
- **Trực quan hóa dữ liệu:** `Matplotlib` để vẽ các biểu đồ thống kê.
- **Cơ sở dữ liệu:** `SQLite3` - một CSDL gọn nhẹ, không cần cài đặt server.

## 4. Hướng dẫn cài đặt và sử dụng
1.  **Clone repository:**
    ```bash
    git clone <your-repository-url>
    ```
2.  **Cài đặt các thư viện cần thiết:**
    ```bash
    pip install customtkinter matplotlib
    ```
3.  **Khởi tạo cơ sở dữ liệu:**
    Chạy file `database.py` để tạo file `tour_management.db` cùng các bảng và dữ liệu mẫu.
    ```bash
    python database.py
    ```
4.  **Khởi chạy ứng dụng:**
    ```bash
    python main.py
    ```
5.  **Đăng nhập:**
    Sử dụng tài khoản mẫu đã được tạo sẵn trong `database.py`:
    -   **Tài khoản Admin:**
        -   Username: `admin`
        -   Password: `123456`
    -   **Tài khoản Nhân viên:**
        -   Username: `staff`
        -   Password: `123456`

## 5. Cấu trúc dự án
```
BTL_Py_QLDichVuDatTourDuLich/
├── view/
│   ├── login_view.py
│   ├── dashboard_view.py
│   ├── tour_view.py
│   ├── booking_view.py
│   ├── customer_view.py
│   └── report_view.py
├── main.py             # File khởi chạy chính, quản lý giao diện tổng thể
├── database.py         # Script khởi tạo CSDL và dữ liệu mẫu
├── db_manager.py       # Lớp quản lý các thao tác với CSDL
├── auth_session.py     # Module quản lý phiên đăng nhập
└── README.md
```

## 6. Mô tả chi tiết các chức năng

### Phân quyền người dùng
- **Admin:** Có toàn quyền truy cập tất cả các chức năng: Xem, Thêm, Sửa, Xóa dữ liệu trên toàn hệ thống.
- **Staff (Nhân viên):** Quyền hạn chế, chỉ có thể xem dữ liệu (tour, đặt chỗ, khách hàng, báo cáo) nhưng không thể thực hiện các thao tác Thêm, Sửa, Xóa.

### Các màn hình chính
1.  **Dashboard (Bảng điều khiển):**
    -   Hiển thị các thẻ thống kê nhanh về tổng doanh thu, số tour đang hoạt động, và khách hàng mới.
    -   Biểu đồ cột doanh thu 6 tháng gần nhất với hiệu ứng động khi tải trang.
    -   Biểu đồ tròn thể hiện tỷ lệ đặt chỗ của các tour phổ biến.
    -   **Lưu ý:** Dữ liệu trên trang này hiện là dữ liệu giả lập (hard-coded) để minh họa giao diện.

2.  **Quản lý Tour:**
    -   Hiển thị danh sách các tour dưới dạng bảng.
    -   Chức năng **Thêm, Sửa, Xóa** tour (chỉ Admin).
    -   Tìm kiếm tour theo Tên hoặc Điểm đến.
    -   Lọc tour theo trạng thái: "Hoạt động", "Tạm dừng".
    -   Xuất danh sách tour ra file CSV.

3.  **Quản lý Đặt chỗ:**
    -   Hiển thị danh sách các đơn đặt tour của khách hàng.
    -   Chức năng **Thêm, Sửa, Xóa** đơn đặt chỗ (chỉ Admin).
    -   Tìm kiếm theo Tên khách hàng hoặc Tên tour.
    -   Lọc đơn theo trạng thái: "Chờ xử lý", "Đã xác nhận", "Hủy bỏ".
    -   Xuất danh sách ra file CSV.

4.  **Quản lý Khách hàng:**
    -   Hiển thị danh sách thông tin khách hàng.
    -   Chức năng **Thêm, Sửa, Xóa** khách hàng (chỉ Admin).
    -   Tìm kiếm khách hàng theo Tên, Email hoặc Số điện thoại.
    -   Xuất danh sách ra file CSV.

5.  **Báo cáo:**
    -   Cung cấp giao diện để xem các báo cáo thống kê chi tiết.
    -   Hiển thị biểu đồ đường (line chart) về doanh thu theo 12 tháng và một bảng tổng hợp dữ liệu.
    -   **Lưu ý:** Các bộ lọc và dữ liệu trên trang này hiện là giả lập để minh họa.

## 7. Sơ đồ Use Case (Thực tế của Admin Panel)
```mermaid
graph LR
    %% Định nghĩa các Actor
    Admin((Quản trị viên))
    Staff((Nhân viên))

    %% Định nghĩa các Use Case
    subgraph "Chức năng hệ thống"
        UC_CRUD(Quản lý CRUD \n<font size=1>Tour, Đặt chỗ, Khách hàng</font>)
        UC_View(Xem dữ liệu & Báo cáo)
        UC_Export(Xuất file CSV)
    end

    %% Kết nối
    Admin -- toàn quyền --> UC_CRUD
    Admin --- UC_View
    Admin --- UC_Export
    Staff -- chỉ xem --> UC_View