import customtkinter as ctk
from tkinter import ttk, messagebox
from db_manager import DBManager
import auth_session

SPECIALTIES = [
    'Miền Bắc', 'Miền Trung', 'Miền Nam', 'Tây Nguyên',
    'Quốc tế', 'Sinh thái & Trekking', 'Văn hóa - Lịch sử', 'Ẩm thực',
]


class GuideView(ctk.CTkFrame):
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
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(header, text="Quản lý Hướng Dẫn Viên",
                     font=ctk.CTkFont(family="Arial", size=28, weight="bold"),
                     text_color="#2c3e50").pack(side="left")

        if auth_session.current_role == "Admin":
            ctk.CTkButton(header, text="+ Thêm HDV",
                          font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
                          fg_color="#3498db", hover_color="#2980b9",
                          height=40, width=150, corner_radius=5,
                          command=self.add_guide).pack(side="right")

    def create_toolbar(self):
        toolbar = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=8,
                               border_width=1, border_color="#e0e0e0", height=60)
        toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        toolbar.grid_propagate(False)

        self.entry_search = ctk.CTkEntry(
            toolbar, placeholder_text="Tìm theo tên, chuyên môn, SĐT...",
            width=320, height=30, corner_radius=5,
            fg_color="#f0f2f5", border_color="#e0e0e0", text_color="#2c3e50")
        self.entry_search.pack(side="left", padx=(20, 10), pady=15)
        self.entry_search.bind("<Return>", lambda e: self.load_data())

        ctk.CTkButton(toolbar, text="Tìm kiếm", width=90, height=30,
                      corner_radius=5, fg_color="#2ecc71", hover_color="#27ae60",
                      font=ctk.CTkFont(family="Arial", size=14),
                      command=self.load_data).pack(side="left", padx=10, pady=15)

        if auth_session.current_role == "Admin":
            ctk.CTkButton(toolbar, text="Xóa", fg_color="#e74c3c",
                          hover_color="#c0392b", width=80, height=30,
                          corner_radius=5,
                          command=self.delete_guide).pack(side="right", padx=(5, 20), pady=15)
            ctk.CTkButton(toolbar, text="Sửa", fg_color="#f39c12",
                          hover_color="#d35400", width=80, height=30,
                          corner_radius=5,
                          command=self.edit_guide).pack(side="right", padx=5, pady=15)

    def create_table(self):
        table_bg = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=8,
                                border_width=1, border_color="#e0e0e0")
        table_bg.grid(row=2, column=0, sticky="nsew")
        table_bg.grid_rowconfigure(0, weight=1)
        table_bg.grid_columnconfigure(0, weight=1)

        columns = ("Mã HDV", "Họ và tên", "SĐT", "Email", "Chuyên môn", "Kinh nghiệm (năm)")
        self.tree = ttk.Treeview(table_bg, columns=columns,
                                  show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=100)
        self.tree.column("Họ và tên",         width=200, anchor="w")
        self.tree.column("Email",              width=220, anchor="w")
        self.tree.column("Chuyên môn",        width=180)
        self.tree.column("Kinh nghiệm (năm)", width=130)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        self.tree.tag_configure('oddrow',  background="#ffffff")
        self.tree.tag_configure('evenrow', background="#f8f9fa")

    def load_data(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        rows = self.db.get_all_guides(self.entry_search.get())
        for i, row in enumerate(rows):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=row, iid=row[0], tags=(tag,))

    def add_guide(self):
        self.open_form()

    def edit_guide(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Lỗi", "Chọn HDV để sửa!")
            return
        g_id = selected[0]
        data = next((r for r in self.db.get_all_guides() if r[0] == g_id), None)
        if data:
            self.open_form(data)

    def delete_guide(self):
        if auth_session.current_role != "Admin":
            messagebox.showwarning("Từ chối", "Chỉ Admin được Xóa!")
            return
        selected = self.tree.selection()
        if not selected:
            return
        g_id = selected[0]
        data = next((r for r in self.db.get_all_guides() if r[0] == g_id), None)
        if data and messagebox.askyesno("Xác nhận",
                                         f"Xóa hướng dẫn viên '{data[1]}'?"):
            self.db.delete_guide(g_id)
            self.load_data()

    def open_form(self, data=None):
        if auth_session.current_role != "Admin":
            messagebox.showwarning("Từ chối", "Chỉ Admin được Thêm/Sửa!")
            return

        top = ctk.CTkToplevel(self)
        top.title("Thông tin Hướng Dẫn Viên")
        top.geometry("460x500")
        top.resizable(False, False)
        top.grab_set()

        scroll = ctk.CTkScrollableFrame(top, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=12)

        def lbl(text):
            ctk.CTkLabel(scroll, text=text, anchor="w", text_color="#34495e",
                         font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(8, 1))

        lbl("Mã HDV:")
        entry_id = ctk.CTkEntry(scroll, width=428, height=34,
                                fg_color="#f0f2f5", border_color="#e0e0e0",
                                text_color="#2c3e50")
        entry_id.pack(anchor="w")

        lbl("Họ và tên:")
        entry_name = ctk.CTkEntry(scroll, width=428, height=34,
                                   fg_color="#f0f2f5", border_color="#e0e0e0",
                                   text_color="#2c3e50")
        entry_name.pack(anchor="w")

        lbl("Số điện thoại:")
        entry_phone = ctk.CTkEntry(scroll, width=428, height=34,
                                    fg_color="#f0f2f5", border_color="#e0e0e0",
                                    text_color="#2c3e50")
        entry_phone.pack(anchor="w")

        lbl("Email:")
        entry_email = ctk.CTkEntry(scroll, width=428, height=34,
                                    fg_color="#f0f2f5", border_color="#e0e0e0",
                                    text_color="#2c3e50")
        entry_email.pack(anchor="w")

        lbl("Chuyên môn:")
        cb_specialty = ctk.CTkComboBox(scroll, values=SPECIALTIES,
                                        width=428, height=34,
                                        fg_color="#f0f2f5", border_color="#e0e0e0",
                                        button_color="#bdc3c7", text_color="#2c3e50")
        cb_specialty.set(SPECIALTIES[0])
        cb_specialty.pack(anchor="w")

        lbl("Kinh nghiệm (số năm):")
        entry_exp = ctk.CTkEntry(scroll, width=428, height=34,
                                  placeholder_text="0",
                                  fg_color="#f0f2f5", border_color="#e0e0e0",
                                  text_color="#2c3e50")
        entry_exp.pack(anchor="w")

        if data:
            # data = (id, full_name, phone, email, specialty, experience_years)
            entry_id.insert(0, data[0])
            entry_id.configure(state="disabled")
            entry_name.insert(0, data[1])
            entry_phone.insert(0, data[2] or "")
            entry_email.insert(0, data[3] or "")
            cb_specialty.set(data[4] or SPECIALTIES[0])
            entry_exp.insert(0, str(data[5]))
        else:
            entry_id.insert(0, self.db.next_id("Guides", "id", "GD"))
            entry_id.configure(state="disabled")
            entry_exp.insert(0, "0")

        def save():
            g_id     = entry_id.get()
            fullname = entry_name.get().strip()
            phone    = entry_phone.get().strip()
            email    = entry_email.get().strip()
            spec     = cb_specialty.get()
            exp_str  = entry_exp.get().strip()

            if not fullname:
                messagebox.showwarning("Lỗi", "Họ tên không được để trống!")
                return
            try:
                exp = int(exp_str) if exp_str else 0
            except ValueError:
                messagebox.showerror("Lỗi", "Kinh nghiệm phải là số nguyên!")
                return

            if data:
                success, msg = self.db.update_guide(g_id, fullname, phone, email, spec, exp)
            else:
                success, msg = self.db.add_guide(g_id, fullname, phone, email, spec, exp)

            if success:
                top.destroy()
                self.load_data()
            else:
                messagebox.showerror("Lỗi", msg)

        ctk.CTkButton(scroll, text="💾  LƯU", height=44,
                      fg_color="#3498db", hover_color="#2980b9",
                      font=ctk.CTkFont(family="Arial", size=15, weight="bold"),
                      command=save).pack(pady=(20, 8), fill="x")
