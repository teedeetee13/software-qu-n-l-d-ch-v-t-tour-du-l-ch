import customtkinter as ctk
from tkinter import ttk
from db_manager import DBManager

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=10, fg_color="#f4f6f9")
        self.db = DBManager()
        
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.create_header()
        self.create_cards()
        self.create_recent_table()

    def create_header(self):
        lbl = ctk.CTkLabel(self, text="📊 Tổng quan Hệ thống", font=ctk.CTkFont(size=26, weight="bold"), text_color="#2c3e50")
        lbl.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

    def create_cards(self):
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        for i in range(4): cards_frame.grid_columnconfigure(i, weight=1)

        rev, bookings, customers, tours = self.db.get_dashboard_stats()

        self.build_card(cards_frame, 0, "💰 Tổng Doanh Thu", f"{rev:,.0f} VNĐ", "#2ecc71")
        self.build_card(cards_frame, 1, "📦 Tổng Đơn Đặt", str(bookings), "#3498db")
        self.build_card(cards_frame, 2, "👥 Khách Hàng", str(customers), "#9b59b6")
        self.build_card(cards_frame, 3, "🚩 Tour Hoạt Động", str(tours), "#f39c12")

    def build_card(self, parent, col, title, value, color):
        card = ctk.CTkFrame(parent, corner_radius=15, fg_color="white", border_width=2, border_color=color)
        card.grid(row=0, column=col, sticky="nsew", padx=10, pady=5)
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=15, weight="bold"), text_color="gray").pack(pady=(15, 5))
        ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=24, weight="bold"), text_color=color).pack(pady=(0, 15))

    def create_recent_table(self):
        table_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        table_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=20)
        table_frame.grid_rowconfigure(1, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(table_frame, text="🕒 Đơn đặt Tour mới nhất", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", padx=15, pady=15)

        columns = ("ID", "Khách hàng", "Tour", "Ngày đặt", "Trạng thái")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        for col in columns: self.tree.heading(col, text=col); self.tree.column(col, anchor="center")
        self.tree.column("Khách hàng", width=150, anchor="w"); self.tree.column("Tour", width=250, anchor="w")
        self.tree.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))

        for row in self.db.get_recent_bookings(limit=8):
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[6]))