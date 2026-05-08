import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import csv
from db_manager import DBManager
import auth_session

class CustomerView(ctk.CTkFrame):
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
        
        lbl = ctk.CTkLabel(header_frame, text="Danh sách Khách hàng", font=ctk.CTkFont(family="Arial", size=28, weight="bold"), text_color="#2c3e50")
        lbl.pack(side="left")

        if auth_session.current_role == "Admin":
            ctk.CTkButton(header_frame, text="+ Thêm Khách hàng", font=ctk.CTkFont(family="Arial", size=14, weight="bold"), fg_color="#3498db", hover_color="#2980b9", height=40, width=160, corner_radius=5, command=self.add_customer).pack(side="right")

    def create_toolbar(self):
        toolbar = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=8, border_width=1, border_color="#e0e0e0", height=60)
        toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        toolbar.grid_propagate(False)

        self.entry_search = ctk.CTkEntry(toolbar, placeholder_text="Tìm kiếm theo tên, email, SĐT...", width=300, height=30, corner_radius=5, fg_color="#f0f2f5", border_color="#e0e0e0", text_color="#2c3e50")
        self.entry_search.pack(side="left", padx=(20, 10), pady=15)
        
        ctk.CTkButton(toolbar, text="Tìm kiếm", width=80, height=30, corner_radius=5, fg_color="#2ecc71", hover_color="#27ae60", font=ctk.CTkFont(family="Arial", size=14), command=self.load_data).pack(side="left", padx=10, pady=15)

        if auth_session.current_role == "Admin":
            ctk.CTkButton(toolbar, text="Xóa", fg_color="#e74c3c", hover_color="#c0392b", width=80, height=30, corner_radius=5, command=self.delete_customer).pack(side="right", padx=(5, 20), pady=15)
            ctk.CTkButton(toolbar, text="Sửa", fg_color="#f39c12", hover_color="#d35400", width=80, height=30, corner_radius=5, command=self.edit_customer).pack(side="right", padx=5, pady=15)
        
        ctk.CTkButton(toolbar, text="Xuất CSV", fg_color="#9b59b6", hover_color="#8e44ad", width=100, height=30, corner_radius=5, command=self.export_csv).pack(side="right", padx=(5, 20) if auth_session.current_role != "Admin" else 5, pady=15)

    def create_table(self):
        table_bg = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=8, border_width=1, border_color="#e0e0e0")
        table_bg.grid(row=2, column=0, sticky="nsew")
        table_bg.grid_rowconfigure(0, weight=1)
        table_bg.grid_columnconfigure(0, weight=1)

        columns = ("ID", "Họ Tên", "Email", "Số điện thoại", "Địa chỉ") # Giữ nguyên cột
        self.tree = ttk.Treeview(table_bg, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.column("ID", width=80)
        self.tree.column("Họ Tên", width=250, anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        self.tree.tag_configure('oddrow', background="#ffffff")
        self.tree.tag_configure('evenrow', background="#f8f9fa")

    def load_data(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        search_kw = self.entry_search.get()
        
        rows = self.db.get_all_users(role='Customer', search_text=search_kw)
        for i, row in enumerate(rows):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=row, tags=(tag,))

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
            self.db.delete_user(c_id)
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
        top.geometry("400x600")
        top.grab_set()

        entries = {}
        fields = [("ID", "Mã KH:"), ("Username", "Tên đăng nhập:"), ("Password", "Mật khẩu:"),
                  ("Name", "Họ Tên:"), ("Email", "Email:"), 
                  ("Phone", "Số điện thoại:"), ("Address", "Địa chỉ:")]

        for key, label in fields:
            ctk.CTkLabel(top, text=label).pack(pady=(5,0), padx=20, anchor="w")
            ent = ctk.CTkEntry(top, width=360)
            if key == "Password":
                ent.configure(show="*")
            ent.pack(pady=2, padx=20)
            entries[key] = ent

        if data:
            entries["ID"].insert(0, data[0]); entries["ID"].configure(state="disabled")
            # Khi sửa, không cho sửa username và không cần hiển thị password
            entries["Username"].configure(state="disabled")
            entries["Password"].pack_forget() # Ẩn field mật khẩu
            top.winfo_children()[-2].pack_forget() # Ẩn label mật khẩu
            
            entries["Name"].insert(0, data[1])
            entries["Email"].insert(0, data[2])
            entries["Phone"].insert(0, data[3])
            entries["Address"].insert(0, data[4])
        else:
            # Tự động điền ID khi THÊM MỚI
            entries["ID"].insert(0, self.db.next_id("Users", "id", "C"))
            entries["ID"].configure(state="disabled")

        def save():
            # Lấy giá trị từ các entry
            user_id = entries["ID"].get()
            username = entries["Username"].get()
            password = entries["Password"].get()
            full_name = entries["Name"].get()
            email = entries["Email"].get()
            phone = entries["Phone"].get()
            address = entries["Address"].get()

            if not (user_id and username and full_name and email and phone and address and (password or data)):
                messagebox.showwarning("Lỗi", "Nhập đủ thông tin!"); return

            if data:
                self.db.update_user(user_id, full_name, email, phone, address)
            else:
                success, msg = self.db.add_user(user_id, username, password, full_name, email, phone, address, 'Customer')
                if not success:
                    messagebox.showerror("Lỗi", msg); return
            
            top.destroy()
            self.load_data()

        ctk.CTkButton(top, text="LƯU", height=40, command=save).pack(pady=20)