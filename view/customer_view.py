import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import csv
from db_manager import DBManager
import auth_session

class CustomerView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=10, fg_color="#f4f6f9")
        self.db = DBManager()
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.create_header()
        self.create_toolbar()
        self.create_table()
        self.load_data()

    def create_header(self):
        lbl = ctk.CTkLabel(self, text="Quản lý Khách hàng", font=ctk.CTkFont(size=24, weight="bold"))
        lbl.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

    def create_toolbar(self):
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))

        # Công cụ Tìm kiếm
        self.entry_search = ctk.CTkEntry(toolbar, placeholder_text="Tìm tên KH, số điện thoại...", width=250)
        self.entry_search.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(toolbar, text="Tìm", width=60, command=self.load_data).pack(side="left")

        # Nút chức năng
        ctk.CTkButton(toolbar, text="Xóa", fg_color="#e74c3c", hover_color="#c0392b", width=80, command=self.delete_customer).pack(side="right", padx=5)
        ctk.CTkButton(toolbar, text="Sửa", fg_color="#f39c12", hover_color="#d35400", width=80, command=self.edit_customer).pack(side="right", padx=5)
        ctk.CTkButton(toolbar, text="📥 Xuất CSV", fg_color="#8e44ad", hover_color="#9b59b6", width=100, command=self.export_csv).pack(side="right", padx=5)
        ctk.CTkButton(toolbar, text="+ Thêm KH", fg_color="#2ecc71", hover_color="#27ae60", width=120, command=self.add_customer).pack(side="right", padx=5)

    def create_table(self):
        columns = ("ID", "Họ Tên", "Email", "Số điện thoại")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.column("Họ Tên", width=250, anchor="w")
        self.tree.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))

    def load_data(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        search_kw = self.entry_search.get()
        
        rows = self.db.get_all_customers(search_kw)
        for row in rows:
            self.tree.insert("", "end", values=row)

    def add_customer(self):
        self.open_form()

    def edit_customer(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Lỗi", "Chọn Khách hàng để sửa!")
            return
        data = self.tree.item(selected[0])['values']
        self.open_form(data)

    def delete_customer(self):
        if auth_session.current_role != "Admin":
            messagebox.showwarning("Từ chối", "Chỉ Admin được Xóa!")
            return
        selected = self.tree.selection()
        if not selected: return
        c_id = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Xác nhận", "Xóa Khách hàng này?"):
            self.db.delete_customer(c_id)
            self.load_data()

    def export_csv(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")], title="Lưu danh sách Khách hàng")
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
        top.title("Thông tin Khách hàng")
        top.geometry("400x450")
        top.grab_set()

        entries = {}
        fields = [("ID", "Mã KH (VD: KH005):"), ("Name", "Họ Tên:"), ("Email", "Email:"), 
                  ("Phone", "Số điện thoại:")]

        for key, label in fields:
            ctk.CTkLabel(top, text=label).pack(pady=(10,0), padx=20, anchor="w")
            ent = ctk.CTkEntry(top, width=360)
            ent.pack(pady=5, padx=20)
            entries[key] = ent

        if data:
            entries["ID"].insert(0, data[0]); entries["ID"].configure(state="disabled")
            entries["Name"].insert(0, data[1]); entries["Email"].insert(0, data[2])
            phone_val = "0" + str(data[3]) if len(str(data[3])) == 9 else str(data[3])
            entries["Phone"].insert(0, phone_val)

        def save():
            vals = [e.get() for e in entries.values()]
            if not all(vals):
                messagebox.showwarning("Lỗi", "Nhập đủ thông tin!"); return

            if data:
                self.db.update_customer(vals[0], vals[1], vals[2], vals[3])
            else:
                success, msg = self.db.add_customer(vals[0], vals[1], vals[2], vals[3])
                if not success:
                    messagebox.showerror("Lỗi", msg); return
            
            top.destroy()
            self.load_data()

        ctk.CTkButton(top, text="LƯU", height=40, command=save).pack(pady=20)