import customtkinter as ctk
from tkinter import ttk, messagebox
from db_manager import DBManager
import auth_session


class UserView(ctk.CTkFrame):
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

        ctk.CTkLabel(header, text="Quản lý Người Dùng & Phân Quyền",
                     font=ctk.CTkFont(family="Arial", size=28, weight="bold"),
                     text_color="#2c3e50").pack(side="left")

        if auth_session.current_role == "Admin":
            ctk.CTkButton(header, text="+ Thêm User",
                          font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
                          fg_color="#3498db", hover_color="#2980b9",
                          height=40, width=160, corner_radius=5,
                          command=self.add_user).pack(side="right")

    def create_toolbar(self):
        toolbar = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=8,
                               border_width=1, border_color="#e0e0e0", height=60)
        toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        toolbar.grid_propagate(False)

        self.entry_search = ctk.CTkEntry(
            toolbar, placeholder_text="Tìm theo tên đăng nhập, họ tên, email...",
            width=320, height=30, corner_radius=5,
            fg_color="#f0f2f5", border_color="#e0e0e0", text_color="#2c3e50")
        self.entry_search.pack(side="left", padx=(20, 10), pady=15)

        ctk.CTkButton(toolbar, text="Tìm kiếm", width=90, height=30,
                      corner_radius=5, fg_color="#2ecc71", hover_color="#27ae60",
                      font=ctk.CTkFont(family="Arial", size=14),
                      command=self.load_data).pack(side="left", padx=10, pady=15)
        self.entry_search.bind("<Return>", lambda e: self.load_data())

        if auth_session.current_role == "Admin":
            ctk.CTkButton(toolbar, text="Xóa", fg_color="#e74c3c",
                          hover_color="#c0392b", width=80, height=30,
                          corner_radius=5,
                          command=self.delete_user).pack(side="right", padx=(5, 20), pady=15)
            ctk.CTkButton(toolbar, text="Sửa", fg_color="#f39c12",
                          hover_color="#d35400", width=80, height=30,
                          corner_radius=5,
                          command=self.edit_user).pack(side="right", padx=5, pady=15)

    def create_table(self):
        table_bg = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=8,
                                border_width=1, border_color="#e0e0e0")
        table_bg.grid(row=2, column=0, sticky="nsew")
        table_bg.grid_rowconfigure(0, weight=1)
        table_bg.grid_columnconfigure(0, weight=1)

        columns = ("ID", "Tên đăng nhập", "Họ và tên", "Email", "SĐT", "Vai trò")
        self.tree = ttk.Treeview(table_bg, columns=columns,
                                  show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.column("Họ và tên", width=200, anchor="w")
        self.tree.column("Email", width=200, anchor="w")
        self.tree.column("Vai trò", width=100)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        self.tree.tag_configure('oddrow',  background="#ffffff")
        self.tree.tag_configure('evenrow', background="#f8f9fa")
        self.tree.tag_configure('Admin',   foreground="#e74c3c")
        self.tree.tag_configure('Staff',   foreground="#2980b9")

    def load_data(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        rows = self.db.get_all_users(self.entry_search.get())
        for i, row in enumerate(rows):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            role_tag = row[5]
            self.tree.insert("", "end", values=row, iid=row[0],
                             tags=(tag, role_tag))

    def add_user(self):
        self.open_form()

    def edit_user(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Lỗi", "Chọn User để sửa!")
            return
        u_id = selected[0]
        data = next((r for r in self.db.get_all_users() if r[0] == u_id), None)
        if data:
            self.open_form(data)

    def delete_user(self):
        if auth_session.current_role != "Admin":
            messagebox.showwarning("Từ chối", "Chỉ Admin được Xóa!")
            return
        selected = self.tree.selection()
        if not selected:
            return
        u_id = selected[0]
        data = next((r for r in self.db.get_all_users() if r[0] == u_id), None)
        if data and data[1] == auth_session.current_user:
            messagebox.showwarning("Không thể xóa",
                                   "Không thể xóa tài khoản đang đăng nhập!")
            return
        if data and messagebox.askyesno("Xác nhận",
                                         f"Xóa user '{data[1]}' ({data[2]})?"):
            self.db.delete_user(u_id)
            self.load_data()

    def open_form(self, data=None):
        if auth_session.current_role != "Admin":
            messagebox.showwarning("Từ chối", "Chỉ Admin được Thêm/Sửa!")
            return

        top = ctk.CTkToplevel(self)
        top.title("Thông tin Người Dùng")
        top.geometry("460x560")
        top.resizable(False, False)
        top.grab_set()

        scroll = ctk.CTkScrollableFrame(top, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=12)

        def lbl(text):
            ctk.CTkLabel(scroll, text=text, anchor="w", text_color="#34495e",
                         font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(8, 1))

        lbl("Mã User:")
        entry_id = ctk.CTkEntry(scroll, width=428, height=34,
                                fg_color="#f0f2f5", border_color="#e0e0e0",
                                text_color="#2c3e50")
        entry_id.pack(anchor="w")

        lbl("Tên đăng nhập:")
        entry_uname = ctk.CTkEntry(scroll, width=428, height=34,
                                   fg_color="#f0f2f5", border_color="#e0e0e0",
                                   text_color="#2c3e50")
        entry_uname.pack(anchor="w")

        lbl("Mật khẩu:")
        entry_pwd = ctk.CTkEntry(scroll, width=428, height=34,
                                  fg_color="#f0f2f5", border_color="#e0e0e0",
                                  text_color="#2c3e50", show="*")
        entry_pwd.pack(anchor="w")

        lbl("Họ và tên:")
        entry_name = ctk.CTkEntry(scroll, width=428, height=34,
                                   fg_color="#f0f2f5", border_color="#e0e0e0",
                                   text_color="#2c3e50")
        entry_name.pack(anchor="w")

        lbl("Email:")
        entry_email = ctk.CTkEntry(scroll, width=428, height=34,
                                    fg_color="#f0f2f5", border_color="#e0e0e0",
                                    text_color="#2c3e50")
        entry_email.pack(anchor="w")

        lbl("Số điện thoại:")
        entry_phone = ctk.CTkEntry(scroll, width=428, height=34,
                                    fg_color="#f0f2f5", border_color="#e0e0e0",
                                    text_color="#2c3e50")
        entry_phone.pack(anchor="w")

        lbl("Vai trò (Phân quyền):")
        cb_role = ctk.CTkComboBox(scroll, values=["Staff", "Admin"],
                                   width=428, height=34,
                                   fg_color="#f0f2f5", border_color="#e0e0e0",
                                   button_color="#bdc3c7", text_color="#2c3e50")
        cb_role.set("Staff")
        cb_role.pack(anchor="w")

        ctk.CTkLabel(scroll,
                     text="Admin: toàn quyền CRUD  |  Staff: chỉ xem",
                     text_color="#95a5a6",
                     font=ctk.CTkFont(size=11, slant="italic")).pack(
            anchor="w", pady=(4, 0))

        if data:
            # data = (id, username, full_name, email, phone, role)
            entry_id.insert(0, data[0])
            entry_id.configure(state="disabled")
            entry_uname.insert(0, data[1])
            entry_name.insert(0, data[2])
            entry_email.insert(0, data[3] or "")
            entry_phone.insert(0, data[4] or "")
            cb_role.set(data[5])
            ctk.CTkLabel(scroll,
                         text="Để trống mật khẩu = giữ nguyên mật khẩu cũ",
                         text_color="#f39c12",
                         font=ctk.CTkFont(size=11)).pack(anchor="w", pady=(2, 0))
        else:
            entry_id.insert(0, self.db.next_id("Users", "id", "U"))
            entry_id.configure(state="disabled")

        def save():
            u_id     = entry_id.get()
            username = entry_uname.get().strip()
            password = entry_pwd.get().strip()
            fullname = entry_name.get().strip()
            email    = entry_email.get().strip()
            phone    = entry_phone.get().strip()
            role     = cb_role.get()

            if not username or not fullname:
                messagebox.showwarning("Lỗi", "Tên đăng nhập và Họ tên không được để trống!")
                return

            if data:
                if not password:
                    # Giữ nguyên mật khẩu cũ
                    conn = self.db.connect()
                    cur  = conn.cursor()
                    cur.execute("SELECT password FROM Users WHERE id=?", (u_id,))
                    row  = cur.fetchone()
                    conn.close()
                    password = row[0] if row else ""
                success, msg = self.db.update_user(
                    u_id, username, password, fullname, email, phone, "", role)
            else:
                if not password:
                    messagebox.showwarning("Lỗi", "Mật khẩu không được để trống!")
                    return
                success, msg = self.db.add_user(
                    u_id, username, password, fullname, email, phone, "", role)

            if success:
                top.destroy()
                self.load_data()
            else:
                messagebox.showerror("Lỗi", msg)

        ctk.CTkButton(scroll, text="💾  LƯU", height=44,
                      fg_color="#3498db", hover_color="#2980b9",
                      font=ctk.CTkFont(family="Arial", size=15, weight="bold"),
                      command=save).pack(pady=(20, 8), fill="x")
