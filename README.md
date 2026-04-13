# Phần mềm Quản lý Dịch vụ Đặt Tour Du lịch

## 1. Thành viên thực hiện
- Trần Đức Trường - 20233802
- Nguyễn Việt Thành - 2023....
- Trần Đức Duy - 2023....

## 2. Mô tả các chức năng của ứng dụng
### Phân quyền: Khách hàng (User)
- **Đăng ký/Đăng nhập:** Tạo tài khoản cá nhân.
- **Tìm kiếm Tour:** Lọc theo điểm đến, giá cả, thời gian.
- **Đặt Tour:** Chọn số lượng người và gửi yêu cầu đặt.
- **Quản lý thông tin:** Cập nhật hồ sơ cá nhân.

### Phân quyền: Quản trị viên (Admin)
- **Quản lý danh mục Tour:** Thêm, sửa, xóa các gói tour.
- **Duyệt đơn hàng:** Tiếp nhận và thay đổi trạng thái đơn đặt tour.
- **Thống kê doanh thu:** Xem báo cáo theo tháng.

## 3. Sơ đồ Use Case
```mermaid
usecaseDiagram
    actor "Khách hàng" as User
    actor "Quản trị viên" as Admin
    
    User --> (Tìm kiếm Tour)
    User --> (Đặt Tour)
    Admin --> (Quản lý Tour)
    Admin --> (Duyệt Đơn hàng)