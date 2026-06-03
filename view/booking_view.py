import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import csv
import calendar
import datetime
from db_manager import DBManager
import auth_session
from view.schedule_view import DatePickerWidget

class BookingView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0, fg_color="#f0f2f5")
        self.db = DBManager()
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.create_header()
        self.create_toolbar()
        self.create_table()
        self.load_data()

    def create_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        lbl = ctk.CTkLabel(header_frame, text="Danh sách Đặt chỗ", font=ctk.CTkFont(family="Arial", size=28, weight="bold"), text_color="#2c3e50")
        lbl.pack(side="left")

        self.btn_add = ctk.CTkButton(header_frame, text="+ Thêm Đặt chỗ Mới", font=ctk.CTkFont(family="Arial", size=14, weight="bold"), fg_color="#3498db", hover_color="#2980b9", height=40, width=180, corner_radius=5, command=self.add_booking)
        if auth_session.current_role == "Admin":
            self.btn_add.pack(side="right")

    def create_toolbar(self):
        toolbar = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=8, border_width=1, border_color="#e0e0e0", height=60)
        toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        toolbar.grid_propagate(False)

        self.entry_search = ctk.CTkEntry(toolbar, placeholder_text="Tìm theo mã, khách hàng...", width=300, height=30, corner_radius=5, fg_color="#f0f2f5", border_color="#e0e0e0", text_color="#2c3e50")
        self.entry_search.pack(side="left", padx=(20, 10), pady=15)
        
        self.combo_filter = ctk.CTkComboBox(toolbar, values=["Tất cả", "Đã xác nhận", "Chờ xử lý", "Đã hủy"], width=150, height=30, corner_radius=5, fg_color="#f0f2f5", border_color="#e0e0e0", button_color="#bdc3c7", text_color="#2c3e50", command=lambda _: self.load_data())
        self.combo_filter.pack(side="left", padx=10, pady=15)
        
        ctk.CTkButton(toolbar, text="Lọc", width=80, height=30, corner_radius=5, fg_color="#2ecc71", hover_color="#27ae60", font=ctk.CTkFont(family="Arial", size=14), command=self.load_data).pack(side="left", padx=10, pady=15)

        self.btn_delete = ctk.CTkButton(toolbar, text="Xóa", fg_color="#e74c3c", hover_color="#c0392b", width=80, height=30, corner_radius=5, command=self.delete_booking)
        self.btn_edit = ctk.CTkButton(toolbar, text="Sửa", fg_color="#f39c12", hover_color="#d35400", width=80, height=30, corner_radius=5, command=self.edit_booking)
        
        # Chỉ pack (hiển thị) các nút Xóa, Sửa nếu là Admin
        if auth_session.current_role == "Admin":
            self.btn_delete.pack(side="right", padx=(5, 20), pady=15)
            self.btn_edit.pack(side="right", padx=5, pady=15)
            
        ctk.CTkButton(toolbar, text="Xuất CSV", fg_color="#9b59b6", hover_color="#8e44ad", width=100, height=30, corner_radius=5, command=self.export_csv).pack(side="right", padx=(5, 20) if auth_session.current_role != "Admin" else 5, pady=15)

    def create_table(self):
        table_bg = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=8, border_width=1, border_color="#e0e0e0")
        table_bg.grid(row=2, column=0, sticky="nsew")
        table_bg.grid_rowconfigure(0, weight=1)
        table_bg.grid_columnconfigure(0, weight=1)

        columns = ("ID", "Khách hàng", "Tour", "Ngày đặt", "Số lượng", "Tổng tiền (VNĐ)", "Trạng thái")
        self.tree = ttk.Treeview(table_bg, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.column("Khách hàng", width=150, anchor="w")
        self.tree.column("Tour", width=200, anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        self.tree.tag_configure('oddrow', background="#ffffff")
        self.tree.tag_configure('evenrow', background="#f8f9fa")
        # Thêm màu sắc cho trạng thái để bớt khô khan
        self.tree.tag_configure('Chờ xử lý', foreground="#f39c12") # Vàng cam
        self.tree.tag_configure('Đã xác nhận', foreground="#27ae60") # Xanh lá
        self.tree.tag_configure('Đã hủy', foreground="#c0392b") # Đỏ

    def load_data(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        search_kw = self.entry_search.get()
        status_flt = self.combo_filter.get()
        
        rows = self.db.get_all_bookings(search_kw, status_flt)
        for i, row in enumerate(rows):
            formatted_row = list(row)
            formatted_row[5] = f"{row[5]:,.0f}"
            display_row = formatted_row[:7] # Chỉ hiển thị 7 cột đầu
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            status_tag = row[6]
            self.tree.insert("", "end", values=display_row, iid=row[0]) # Dùng iid để lưu id gốc

    def add_booking(self):
        self.open_form()

    def edit_booking(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Lỗi", "Chọn Booking để sửa!")
            return
        
        b_id = selected[0]
        # Lấy dữ liệu gốc từ DB để sửa cho chính xác
        data = next((row for row in self.db.get_all_bookings() if row[0] == b_id), None)
        self.open_form(data)

    def delete_booking(self):
        if auth_session.current_role != "Admin":
            messagebox.showwarning("Từ chối", "Chỉ Admin được Xóa!")
            return
        selected = self.tree.selection()
        if not selected: return
        b_id = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Xác nhận", "Xóa Booking này?"):
            self.db.delete_booking(b_id)
            self.load_data()

    def export_csv(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")], title="Lưu file Báo cáo Đặt chỗ")
        if not filepath:
            return
        try:
            with open(filepath, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                headers = [self.tree.heading(col)['text'] for col in self.tree['columns']]
                writer.writerow(headers)
                for row_id in self.tree.get_children():
                    writer.writerow(self.tree.item(row_id)['values'])
            messagebox.showinfo("Thành công", f"Đã xuất dữ liệu thành công:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất file: {e}")

    def open_form(self, data=None):
        if auth_session.current_role != "Admin":
            messagebox.showwarning("Từ chối", "Chỉ Admin được Thêm/Sửa!")
            return

        top = ctk.CTkToplevel(self)
        top.title("Thông tin Đặt chỗ")
        top.geometry("520x740")
        top.resizable(False, True)
        top.grab_set()

        scroll = ctk.CTkScrollableFrame(top, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=12)

        def lbl(text):
            ctk.CTkLabel(scroll, text=text, anchor="w", text_color="#34495e",
                         font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(8, 1))

        # ── Mã đặt chỗ ──────────────────────────────────────
        lbl("Mã đặt chỗ:")
        entry_id = ctk.CTkEntry(scroll, width=488, height=34,
                                fg_color="#f0f2f5", border_color="#e0e0e0",
                                text_color="#2c3e50")
        entry_id.pack(anchor="w")

        # ── Tìm khách hàng ───────────────────────────────────
        ctk.CTkLabel(scroll, text="Tìm khách hàng",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#2c3e50").pack(anchor="w", pady=(12, 2))

        search_row = ctk.CTkFrame(scroll, fg_color="transparent")
        search_row.pack(fill="x")
        entry_search_cust = ctk.CTkEntry(search_row,
                                         placeholder_text="Nhập tên, SĐT hoặc email...",
                                         height=34, fg_color="#f0f2f5",
                                         border_color="#e0e0e0", text_color="#2c3e50")
        entry_search_cust.pack(side="left", fill="x", expand=True, padx=(0, 8))

        selected_customer = {"id": None, "name": ""}

        # Treeview kết quả tìm khách
        tree_frame = ctk.CTkFrame(scroll, fg_color="#ffffff",
                                  corner_radius=6, border_width=1,
                                  border_color="#e0e0e0")
        tree_frame.pack(fill="x", pady=(4, 0))
        tree_cust = ttk.Treeview(tree_frame,
                                  columns=("ID", "Họ tên", "SĐT", "Email"),
                                  show="headings", height=4)
        for col, w in [("ID", 70), ("Họ tên", 180), ("SĐT", 110), ("Email", 160)]:
            tree_cust.heading(col, text=col)
            tree_cust.column(col, width=w, anchor="w")
        tree_cust.pack(fill="x", padx=2, pady=2)

        lbl_selected_cust = ctk.CTkLabel(scroll, text="Chưa chọn khách hàng",
                                          text_color="#e74c3c",
                                          font=ctk.CTkFont(size=12, slant="italic"))
        lbl_selected_cust.pack(anchor="w")

        def do_search_customer(event=None):
            kw = entry_search_cust.get().strip()
            results = self.db.search_customers(kw)
            for r in tree_cust.get_children():
                tree_cust.delete(r)
            for row in results:
                tree_cust.insert("", "end", values=row)

        def on_cust_select(event):
            sel = tree_cust.selection()
            if sel:
                vals = tree_cust.item(sel[0])["values"]
                selected_customer["id"] = vals[0]
                selected_customer["name"] = vals[1]
                lbl_selected_cust.configure(
                    text=f"Đã chọn: {vals[1]} ({vals[0]})",
                    text_color="#27ae60")

        ctk.CTkButton(search_row, text="Tìm", width=80, height=34,
                      fg_color="#2ecc71", hover_color="#27ae60",
                      command=do_search_customer).pack(side="left")
        entry_search_cust.bind("<Return>", do_search_customer)
        tree_cust.bind("<<TreeviewSelect>>", on_cust_select)

        # ── Chọn Tour → Lịch khởi hành ──────────────────────
        ctk.CTkLabel(scroll, text="Chọn Tour & Lịch",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#2c3e50").pack(anchor="w", pady=(12, 2))

        lbl("Tour:")
        tours_data = self.db.get_all_tours()
        tour_map = {t[1]: t[0] for t in tours_data}

        current_schedule_map = {}

        cb_tour = ctk.CTkComboBox(scroll, values=list(tour_map.keys()),
                                   width=488, height=34,
                                   fg_color="#f0f2f5", border_color="#e0e0e0",
                                   button_color="#bdc3c7", text_color="#2c3e50")
        cb_tour.pack(anchor="w")
        cb_tour.set("-- Chọn Tour --")

        lbl("Lịch khởi hành:")
        cb_schedule = ctk.CTkComboBox(scroll, values=[],
                                       width=488, height=34,
                                       fg_color="#f0f2f5", border_color="#e0e0e0",
                                       button_color="#bdc3c7", text_color="#2c3e50")
        cb_schedule.pack(anchor="w")
        cb_schedule.set("-- Chọn Tour trước --")

        # ── Số lượng & Tính tiền tự động ─────────────────────
        ctk.CTkLabel(scroll, text="Số lượng & Tính tiền (tự động)",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#2c3e50").pack(anchor="w", pady=(12, 2))

        price_box = ctk.CTkFrame(scroll, fg_color="#f8f9fa",
                                  corner_radius=8, border_width=1,
                                  border_color="#e0e0e0")
        price_box.pack(fill="x")

        current_prices = {"Người lớn": 0, "Trẻ em": 0}

        def make_count_row(parent, label_text, key):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=6)
            ctk.CTkLabel(row, text=label_text, width=90, anchor="w",
                         text_color="#34495e").pack(side="left")
            ent = ctk.CTkEntry(row, width=70, height=32,
                               fg_color="#ffffff", border_color="#e0e0e0",
                               text_color="#2c3e50")
            ent.insert(0, "0")
            ent.pack(side="left", padx=8)
            price_lbl = ctk.CTkLabel(row, text="× 0 VNĐ/người",
                                      text_color="#7f8c8d", anchor="w")
            price_lbl.pack(side="left")
            return ent, price_lbl

        entry_adult, lbl_adult_price = make_count_row(price_box, "Người lớn:", "Người lớn")
        entry_child, lbl_child_price = make_count_row(price_box, "Trẻ em:", "Trẻ em")

        sep = ctk.CTkFrame(price_box, height=1, fg_color="#e0e0e0")
        sep.pack(fill="x", padx=12, pady=2)

        total_row = ctk.CTkFrame(price_box, fg_color="transparent")
        total_row.pack(fill="x", padx=12, pady=8)
        ctk.CTkLabel(total_row, text="Tổng tiền đoàn:",
                     font=ctk.CTkFont(weight="bold"),
                     text_color="#2c3e50").pack(side="left")
        lbl_total = ctk.CTkLabel(total_row, text="0 VNĐ",
                                  font=ctk.CTkFont(size=15, weight="bold"),
                                  text_color="#e74c3c")
        lbl_total.pack(side="right")

        def recalc_price(event=None):
            try:
                adults = max(0, int(entry_adult.get() or 0))
                children = max(0, int(entry_child.get() or 0))
            except ValueError:
                return
            ap = current_prices.get("Người lớn", 0)
            cp = current_prices.get("Trẻ em", 0)
            total = adults * ap + children * cp
            lbl_total.configure(text=f"{total:,.0f} VNĐ")

        entry_adult.bind("<KeyRelease>", recalc_price)
        entry_child.bind("<KeyRelease>", recalc_price)

        def on_schedule_change(choice):
            s_id = current_schedule_map.get(choice)
            if not s_id:
                return
            prices = self.db.get_prices_for_schedule(s_id)
            current_prices.update({"Người lớn": 0, "Trẻ em": 0})
            current_prices.update(prices)
            ap = current_prices.get("Người lớn", 0)
            cp = current_prices.get("Trẻ em", 0)
            lbl_adult_price.configure(text=f"× {ap:,.0f} VNĐ/người")
            lbl_child_price.configure(
                text=f"× {cp:,.0f} VNĐ/người" if cp else "× Không áp dụng")
            recalc_price()

        def on_tour_change(choice):
            t_id = tour_map.get(choice)
            if not t_id:
                return
            rows = self.db.get_schedules_by_tour_for_form(t_id)
            current_schedule_map.clear()
            current_schedule_map.update({r[1]: r[0] for r in rows})
            names = list(current_schedule_map.keys())
            cb_schedule.configure(values=names)
            cb_schedule.set(names[0] if names else "Không có lịch khả dụng")
            if names:
                on_schedule_change(names[0])

        cb_tour.configure(command=on_tour_change)
        cb_schedule.configure(command=on_schedule_change)

        # ── Ngày đặt & Trạng thái ────────────────────────────
        lbl("Ngày đặt:")
        dp_date = DatePickerWidget(scroll, width=488)
        dp_date.pack(anchor="w")

        lbl("Trạng thái:")
        cb_status = ctk.CTkComboBox(scroll,
                                     values=["Chờ xử lý", "Đã xác nhận", "Đã hủy"],
                                     width=488, height=34,
                                     fg_color="#f0f2f5", border_color="#e0e0e0",
                                     button_color="#bdc3c7", text_color="#2c3e50")
        cb_status.set("Chờ xử lý")
        cb_status.pack(anchor="w")

        # ── Điền dữ liệu khi SỬA ─────────────────────────────
        if data:
            # data = (id, full_name, tour_name, booking_date, guest_count, total_price, status, customer_id, schedule_id)
            entry_id.insert(0, data[0])
            entry_id.configure(state="disabled")

            # Điền khách hàng
            selected_customer["id"] = data[7]
            selected_customer["name"] = data[1]
            lbl_selected_cust.configure(
                text=f"Đã chọn: {data[1]} ({data[7]})", text_color="#27ae60")

            # Điền tour từ schedule_id
            all_scheds = self.db.get_all_schedules()
            sched_info = next((s for s in all_scheds if s[0] == data[8]), None)
            if sched_info:
                tour_name = sched_info[2]
                cb_tour.set(tour_name)
                on_tour_change(tour_name)
                # Tìm display name của schedule
                sched_display = next(
                    (k for k, v in current_schedule_map.items() if v == data[8]), "")
                if sched_display:
                    cb_schedule.set(sched_display)
                    on_schedule_change(sched_display)

            entry_adult.delete(0, "end")
            entry_adult.insert(0, str(data[4]))
            dp_date.set(data[3])
            cb_status.set(data[6])
            recalc_price()
        else:
            entry_id.insert(0, self.db.next_id("Bookings", "id", "BK"))
            entry_id.configure(state="disabled")
            # Tải sẵn danh sách khách để tiện tra cứu
            do_search_customer()

        # ── Lưu ─────────────────────────────────────────────
        def save():
            b_id = entry_id.get()
            booking_date = dp_date.get()
            customer_id = selected_customer["id"]
            schedule_id = current_schedule_map.get(cb_schedule.get())

            if not customer_id:
                messagebox.showwarning("Lỗi", "Vui lòng tìm và chọn khách hàng!")
                return
            if not schedule_id:
                messagebox.showwarning("Lỗi", "Vui lòng chọn Tour và Lịch khởi hành!")
                return

            try:
                adults = max(0, int(entry_adult.get() or 0))
                children = max(0, int(entry_child.get() or 0))
            except ValueError:
                messagebox.showerror("Lỗi", "Số lượng khách phải là số nguyên!")
                return

            guest_count = adults + children
            if guest_count == 0:
                messagebox.showwarning("Lỗi", "Số lượng khách phải lớn hơn 0!")
                return

            ap = current_prices.get("Người lớn", 0)
            cp = current_prices.get("Trẻ em", 0)
            total_price = adults * ap + children * cp

            try:
                datetime.date.fromisoformat(booking_date)
            except ValueError:
                messagebox.showerror("Lỗi", "Ngày đặt không hợp lệ!")
                return

            if data:
                self.db.update_booking(b_id, customer_id, schedule_id,
                                       booking_date, guest_count,
                                       total_price, cb_status.get())
            else:
                success, msg = self.db.add_booking(b_id, customer_id, schedule_id,
                                                    booking_date, guest_count,
                                                    total_price, cb_status.get())
                if not success:
                    messagebox.showerror("Lỗi", msg)
                    return

            top.destroy()
            self.load_data()

        ctk.CTkButton(scroll, text="💾  LƯU ĐẶT CHỖ", height=44,
                      fg_color="#3498db", hover_color="#2980b9",
                      font=ctk.CTkFont(family="Arial", size=15, weight="bold"),
                      command=save).pack(pady=(20, 8), fill="x")