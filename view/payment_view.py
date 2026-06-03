import customtkinter as ctk
from tkinter import ttk, messagebox
import datetime
from db_manager import DBManager
import auth_session
from view.schedule_view import DatePickerWidget

class PaymentView(ctk.CTkFrame):
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
        
        lbl = ctk.CTkLabel(header_frame, text="Quản lý Giao dịch Thanh toán", font=ctk.CTkFont(family="Arial", size=28, weight="bold"), text_color="#2c3e50")
        lbl.pack(side="left")

        ctk.CTkButton(header_frame, text="+ Thêm Giao dịch", font=ctk.CTkFont(family="Arial", size=14, weight="bold"), fg_color="#3498db", hover_color="#2980b9", height=40, width=160, corner_radius=5, command=self.add_payment).pack(side="right")

    def create_toolbar(self):
        toolbar = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=8, border_width=1, border_color="#e0e0e0", height=60)
        toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        toolbar.grid_propagate(False)

        self.entry_search = ctk.CTkEntry(toolbar, placeholder_text="Tìm mã giao dịch, mã booking...", width=300, height=30, corner_radius=5, fg_color="#f0f2f5", border_color="#e0e0e0", text_color="#2c3e50")
        self.entry_search.pack(side="left", padx=(20, 10), pady=15)
        
        ctk.CTkButton(toolbar, text="Tìm kiếm", width=80, height=30, corner_radius=5, fg_color="#2ecc71", hover_color="#27ae60", font=ctk.CTkFont(family="Arial", size=14), command=self.load_data).pack(side="left", padx=10, pady=15)

        ctk.CTkButton(toolbar, text="Xóa", fg_color="#e74c3c", hover_color="#c0392b", width=80, height=30, corner_radius=5, command=self.delete_payment).pack(side="right", padx=(5, 20), pady=15)
        ctk.CTkButton(toolbar, text="Sửa", fg_color="#f39c12", hover_color="#d35400", width=80, height=30, corner_radius=5, command=self.edit_payment).pack(side="right", padx=5, pady=15)

    def create_table(self):
        table_bg = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=8, border_width=1, border_color="#e0e0e0")
        table_bg.grid(row=2, column=0, sticky="nsew")
        table_bg.grid_rowconfigure(0, weight=1)
        table_bg.grid_columnconfigure(0, weight=1)

        columns = ("ID Thanh Toán", "Mã Đặt Chỗ", "Số Tiền (VNĐ)", "Phương Thức", "Ngày Thanh Toán", "Mã GD Ngân Hàng", "Trạng Thái")
        self.tree = ttk.Treeview(table_bg, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        self.tree.tag_configure('oddrow', background="#ffffff")
        self.tree.tag_configure('evenrow', background="#f8f9fa")

    def load_data(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        search_kw = self.entry_search.get()
        
        rows = self.db.get_all_payments(search_kw)
        for i, row in enumerate(rows):
            formatted_row = list(row)
            formatted_row[2] = f"{row[2]:,.0f}" # Format tiền
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=formatted_row, tags=(tag,))

    def add_payment(self):
        self.open_form()

    def edit_payment(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Lỗi", "Chọn Giao dịch để sửa!")
            return
        data = self.tree.item(selected[0])['values']
        self.open_form(data)

    def delete_payment(self):
        if auth_session.current_role != "Admin":
            messagebox.showwarning("Từ chối", "Chỉ Admin được Xóa!")
            return
        selected = self.tree.selection()
        if not selected: return
        p_id = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Xác nhận", "Xóa Giao dịch này?"):
            self.db.delete_payment(p_id)
            self.load_data()

    def open_form(self, data=None):
        if auth_session.current_role != "Admin":
            messagebox.showwarning("Từ chối", "Chỉ Admin được Thêm/Sửa!")
            return

        top = ctk.CTkToplevel(self)
        top.title("Thông tin Thanh Toán")
        top.geometry("420x600")
        top.grab_set()

        entries = {}
        fields = [("ID", "Mã Giao dịch:"), ("Booking", "Mã Đặt chỗ (VD: BK001):"), 
                  ("Amount", "Số tiền (VNĐ):"), ("Method", "Phương thức (Tiền mặt/Chuyển khoản):"),
                  ("TransID", "Mã giao dịch ngân hàng:")]

        for key, label in fields:
            ctk.CTkLabel(top, text=label).pack(pady=(5,0), padx=20, anchor="w")
            ent = ctk.CTkEntry(top, width=380)
            ent.pack(pady=2, padx=20)
            entries[key] = ent

        # DatePicker ngày thanh toán
        ctk.CTkLabel(top, text="Ngày thanh toán:").pack(pady=(5,0), padx=20, anchor="w")
        dp_date = DatePickerWidget(top, width=380)
        dp_date.pack(pady=2, padx=20, anchor="w")

        ctk.CTkLabel(top, text="Trạng thái:").pack(pady=(5,0), padx=20, anchor="w")
        cb_status = ctk.CTkComboBox(top, values=["Thành công", "Chờ xử lý", "Thất bại", "Hoàn tiền"], width=380)
        cb_status.pack(pady=2, padx=20)

        if data:
            entries["ID"].insert(0, data[0]); entries["ID"].configure(state="disabled")
            entries["Booking"].insert(0, data[1])
            entries["Amount"].insert(0, str(data[2]).replace(",",""))
            entries["Method"].insert(0, data[3])
            dp_date.set(data[4])
            entries["TransID"].insert(0, data[5] if data[5] else "")
            cb_status.set(data[6] if len(data) > 6 else "Thành công")
        else:
            entries["ID"].insert(0, self.db.next_id("Payments", "id", "PAY"))
            entries["ID"].configure(state="disabled")
            cb_status.set("Thành công")

        def save():
            p_id    = entries["ID"].get()
            b_id    = entries["Booking"].get()
            amount  = entries["Amount"].get()
            method  = entries["Method"].get()
            p_date  = dp_date.get()
            trans_id = entries["TransID"].get()
            status  = cb_status.get()

            if not all([p_id, b_id, amount, method, p_date, status]):
                messagebox.showwarning("Lỗi", "Nhập đủ thông tin!"); return

            try:
                datetime.date.fromisoformat(p_date)
            except ValueError:
                messagebox.showerror("Lỗi", "Ngày thanh toán không hợp lệ!"); return

            if data:
                self.db.update_payment(p_id, b_id, int(amount), method, p_date, trans_id, status)
            else:
                success, msg = self.db.add_payment(p_id, b_id, int(amount), method, p_date, trans_id, status)
                if not success:
                    messagebox.showerror("Lỗi", msg); return

            top.destroy()
            self.load_data()

        ctk.CTkButton(top, text="LƯU", height=40, command=save).pack(pady=20)