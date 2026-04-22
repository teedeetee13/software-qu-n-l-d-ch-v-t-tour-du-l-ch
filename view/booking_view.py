import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import csv
from db_manager import DBManager
import auth_session

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

        ctk.CTkButton(header_frame, text="+ Thêm Đặt chỗ Mới", font=ctk.CTkFont(family="Arial", size=14, weight="bold"), fg_color="#3498db", hover_color="#2980b9", height=40, width=180, corner_radius=5, command=self.add_booking).pack(side="right")

    def create_toolbar(self):
        toolbar = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=8, border_width=1, border_color="#e0e0e0", height=60)
        toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        toolbar.grid_propagate(False)

        self.entry_search = ctk.CTkEntry(toolbar, placeholder_text="Tìm theo mã, khách hàng...", width=300, height=30, corner_radius=5, fg_color="#f0f2f5", border_color="#e0e0e0", text_color="#2c3e50")
        self.entry_search.pack(side="left", padx=(20, 10), pady=15)
        
        self.combo_filter = ctk.CTkComboBox(toolbar, values=["Tất cả", "Chờ xử lý", "Đã xác nhận", "Hủy bỏ"], width=150, height=30, corner_radius=5, fg_color="#f0f2f5", border_color="#e0e0e0", button_color="#bdc3c7", text_color="#2c3e50", command=lambda _: self.load_data())
        self.combo_filter.pack(side="left", padx=10, pady=15)
        
        ctk.CTkButton(toolbar, text="Lọc", width=80, height=30, corner_radius=5, fg_color="#2ecc71", hover_color="#27ae60", font=ctk.CTkFont(family="Arial", size=14), command=self.load_data).pack(side="left", padx=10, pady=15)

        ctk.CTkButton(toolbar, text="Xóa", fg_color="#e74c3c", hover_color="#c0392b", width=80, height=30, corner_radius=5, command=self.delete_booking).pack(side="right", padx=(5, 20), pady=15)
        ctk.CTkButton(toolbar, text="Sửa", fg_color="#f39c12", hover_color="#d35400", width=80, height=30, corner_radius=5, command=self.edit_booking).pack(side="right", padx=5, pady=15)
        ctk.CTkButton(toolbar, text="Xuất CSV", fg_color="#9b59b6", hover_color="#8e44ad", width=100, height=30, corner_radius=5, command=self.export_csv).pack(side="right", padx=5, pady=15)

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

    def load_data(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        search_kw = self.entry_search.get()
        status_flt = self.combo_filter.get()
        
        rows = self.db.get_all_bookings(search_kw, status_flt)
        for i, row in enumerate(rows):
            formatted_row = list(row)
            formatted_row[5] = f"{row[5]:,.0f}"
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=formatted_row, tags=(tag,))

    def add_booking(self):
        self.open_form()

    def edit_booking(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Lỗi", "Chọn Booking để sửa!")
            return
        data = self.tree.item(selected[0])['values']
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
        top.geometry("450x650")
        top.grab_set()

        entries = {}
        fields = [("ID", "Mã Đặt chỗ (VD: BK005):"), ("CusName", "Tên Khách hàng:"), ("TourName", "Tên Tour:"), 
                  ("Date", "Ngày đặt (DD/MM/YYYY):"), ("Count", "Số lượng khách:"), ("Price", "Tổng tiền (VNĐ):")]

        for key, label in fields:
            ctk.CTkLabel(top, text=label).pack(pady=(10,0), padx=20, anchor="w")
            ent = ctk.CTkEntry(top, width=410)
            ent.pack(pady=5, padx=20)
            entries[key] = ent

        ctk.CTkLabel(top, text="Trạng thái:").pack(pady=(10,0), padx=20, anchor="w")
        cb_status = ctk.CTkComboBox(top, values=["Chờ xử lý", "Đã xác nhận", "Hủy bỏ"], width=410)
        cb_status.pack(pady=5, padx=20)

        if data:
            entries["ID"].insert(0, data[0]); entries["ID"].configure(state="disabled")
            entries["CusName"].insert(0, data[1]); entries["TourName"].insert(0, data[2])
            entries["Date"].insert(0, data[3]); entries["Count"].insert(0, str(data[4]))
            entries["Price"].insert(0, str(data[5]).replace(",",""))
            cb_status.set(data[6])

        def save():
            vals = [e.get() for e in entries.values()]
            if not all(vals):
                messagebox.showwarning("Lỗi", "Nhập đủ thông tin!"); return
            try: 
                int(vals[4])
                int(vals[5])
            except ValueError:
                messagebox.showerror("Lỗi", "Số lượng và Giá phải là số!"); return

            if data:
                self.db.update_booking(vals[0], vals[1], vals[2], vals[3], int(vals[4]), int(vals[5]), cb_status.get())
            else:
                success, msg = self.db.add_booking(vals[0], vals[1], vals[2], vals[3], int(vals[4]), int(vals[5]), cb_status.get())
                if not success:
                    messagebox.showerror("Lỗi", msg); return
            
            top.destroy()
            self.load_data()

        ctk.CTkButton(top, text="LƯU", height=40, command=save).pack(pady=20)