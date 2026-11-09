"""
賀華實業股份有限公司 (HARVARD ENTERPRISES INC.)
智慧製造、ISO 合規與無障礙桌面應用程式 (Desktop App)
=====================================================================
功能特色：
1. 內建 Google OR-Tools CP-SAT (ortools.sat.python.cp_model) 原生四大求解器介面：
   - Tab 1: 一維鋁捲分條 / 圓棒擠型下料最佳化 (視覺化分條配置圖 + ISO 14001 減碳指標)
   - Tab 2: 二維鋁板精密裁切排樣最佳化 (AddNoOverlap2D 視覺化 Canvas 排版圖)
   - Tab 3: 全台五廠區智慧產能排程 (台北/新竹/台中一/台中二/台南 視覺化甘特圖)
   - Tab 4: 鋁合金多準則智慧選材決策系統 & ISO/JIS/CNS 重量公差計算機
   - Tab 5: 官網完整資料庫與 61 張原始照片零遺漏預覽器 + 內嵌 Flask/Waitress 伺服器控制台
2. 支援 WCAG 2.1 AAA 高對比無障礙主題切換 (黑底黃字 / 專業工業深藍主題) 與字級放大
3. 自動於背景執行緒啟動 Flask + Waitress 伺服器，並可一鍵啟動獨立桌面視窗 (--app 模式)
"""

import os
import sys
import json
import math
import socket
import threading
import subprocess
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from cpsat_optimizer import (
    ALLOY_DB,
    PLANTS,
    solve_1d_cutting_stock,
    solve_2d_plate_cutting,
    solve_multi_plant_schedule,
    solve_alloy_recommendation,
)
from app import app as flask_app

BASE_DIR = Path(__file__).resolve().parent

IMAGE_DESCRIPTIONS = {
    "logo_brand.png": "賀華實業股份有限公司企業標誌 Logo",
    "banner1.jpg": "首頁橫幅 1：專業特殊輕金屬材料與捲片分條",
    "banner2.jpg": "首頁橫幅 2：高精度鋁捲分條與平片裁切產線",
    "banner3.jpg": "首頁橫幅 3：600mm 特厚鋁板與大型立式裁切機",
    "banner4.jpg": "首頁橫幅 4：多軸精密鋁圓棒與擠型材庫存",
    "banner5.jpg": "首頁橫幅 5：全台五大廠區智慧倉儲與物流車隊",
    "a1.jpg": "首頁關於賀華實業：廠房與大型鋁捲材料實景",
    "ab1.jpg": "公司簡介：賀華實業鋁捲大型倉儲與天車吊掛設備",
    "g1.jpg": "首頁服務卡片 1：鋁合金特性及用途",
    "g2.jpg": "首頁服務卡片 2：產品介紹與加工項目",
    "g3.jpg": "首頁服務卡片 3：賀華實業最新消息",
    "c-anda.png": "關係企業標誌：安達磨光鋼棒工業股份有限公司",
    "c-anda2.png": "關係企業標誌：永旭材料股份有限公司",
    "c-fufong.png": "日本合作原廠：日本古河電工株式會社 (Furukawa Sky / UACJ)",
    "c-futsu.png": "日本合作原廠：日本住友輕金屬工業株式會社 (Sumitomo Light Metal)",
    "c-ikeuchi.png": "日本合作原廠：株式會社池內 (Ikeuchi)",
    "royal-1.png": "永旭材料 1：德國進口高精度分條機組",
    "royal-2.png": "永旭材料 2：日本進口四重式精密冷軋壓延機",
    "royal-3.png": "永旭材料 3：無塵室等級光學電子金屬沖壓加工區",
    "royal-4.png": "永旭材料 4：精密退火爐與熱處理產線",
    "royal-5.png": "永旭材料 5：全自動張力整平與表面檢測產線",
    "alu01.jpg": "產品與設備 alu01：高表面品質鋁捲片(Coil)",
    "alu02.jpg": "產品與設備 alu02：中鋼鋁業原裝鋁捲庫存",
    "alu03.jpg": "產品與設備 alu03：高精度自動分條產線(Slitting)",
    "alu04.jpg": "產品與設備 alu04：精密裁切鋁平片(Sheet)堆疊",
    "alu05.jpg": "產品與設備 alu05：中厚鋁板(Plate)雙面貼膜保護",
    "alu06.jpg": "產品與設備 alu06：零零鋁箔與特殊薄鋁帶",
    "alu07.jpg": "產品與設備 alu07：航太與模具級鋁合金圓棒(Rod)",
    "alu08.jpg": "產品與設備 alu08：工業結構與散熱鋁擠型(Extrusion)",
    "alu09.jpg": "產品與設備 alu09：600mm 特厚鋁板立式/臥式高速鋸床",
}
for i in range(1, 31):
    key = f"s{i:02d}.jpg"
    IMAGE_DESCRIPTIONS.setdefault(key, f"賀華實業精密鋁材裁切加工與包裝成品實照 ({key})")
IMAGE_DESCRIPTIONS["top_up.png"] = "返回頁面頂端按鈕圖示 (Top Up)"

COLORS = ["#0f3d68", "#00897b", "#e65100", "#2563eb", "#7c3aed", "#059669", "#d97706", "#be123c"]


def find_free_port(preferred: int = 8080) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("127.0.0.1", preferred)) != 0:
            return preferred
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def launch_standalone_webapp_window(url: str):
    """優先以 Edge 或 Chrome 的 --app 模式開啟無網址列獨立桌面視窗，若無則使用預設瀏覽器"""
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for exe in candidates:
        if os.path.exists(exe):
            try:
                subprocess.Popen([exe, f"--app={url}", "--window-size=1400,900"])
                return
            except Exception:
                pass
    webbrowser.open(url)


class HarvardDesktopApp(tk.Tk):
    def __init__(self, server_port: int = 8080):
        super().__init__()
        self.server_port = server_port
        self.base_url = f"http://127.0.0.1:{self.server_port}"
        self.high_contrast = False
        self.font_size = 10
        self.last_results = {}
        self._current_photo = None

        self.title("賀華實業股份有限公司 (HARVARD ENTERPRISES INC.) - Google OR-Tools CP-SAT 智慧製造與無障礙桌面系統")
        self.geometry("1360x860")
        self.minsize(1100, 720)

        self.style = ttk.Style(self)
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")

        self._apply_theme()
        self._build_header()
        self._build_notebook()
        self._build_statusbar()

        # 初次載入自動執行四大 CP-SAT 最佳化求解
        self.after(150, self._run_initial_solves)

    def _apply_theme(self):
        bg = "#000000" if self.high_contrast else "#f1f5f9"
        fg = "#ffff00" if self.high_contrast else "#0f172a"
        card_bg = "#111111" if self.high_contrast else "#ffffff"
        accent = "#00ffff" if self.high_contrast else "#0f3d68"

        self.configure(bg=bg)
        font_main = ("Microsoft JhengHei UI", self.font_size)
        font_bold = ("Microsoft JhengHei UI", self.font_size, "bold")

        self.style.configure(".", background=bg, foreground=fg, font=font_main)
        self.style.configure("TFrame", background=bg)
        self.style.configure("Card.TFrame", background=card_bg)
        self.style.configure("TLabel", background=bg, foreground=fg, font=font_main)
        self.style.configure("Header.TLabel", background=accent, foreground="#ffff00" if self.high_contrast else "#ffffff", font=("Microsoft JhengHei UI", self.font_size + 3, "bold"))
        self.style.configure("TNotebook", background=bg)
        self.style.configure("TNotebook.Tab", font=font_bold, padding=(14, 8))
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", accent)],
            foreground=[("selected", "#ffff00" if self.high_contrast else "#ffffff")],
        )
        self.style.configure("Accent.TButton", font=font_bold, padding=(12, 6), background="#e65100", foreground="#ffffff")
        self.style.configure("Primary.TButton", font=font_bold, padding=(10, 5), background=accent, foreground="#ffff00" if self.high_contrast else "#ffffff")
        self.style.configure("Treeview", font=font_main, rowheight=int(self.font_size * 2.6), background=card_bg, fieldbackground=card_bg, foreground=fg)
        self.style.configure("Treeview.Heading", font=font_bold, background=accent, foreground="#ffff00" if self.high_contrast else "#ffffff")

    def _build_header(self):
        hdr = tk.Frame(self, bg="#0f3d68", padx=16, pady=10)
        hdr.pack(fill="x")

        left = tk.Frame(hdr, bg="#0f3d68")
        left.pack(side="left")
        tk.Label(
            left,
            text="賀華實業股份有限公司 HARVARD ENTERPRISES INC.",
            bg="#0f3d68",
            fg="#ffffff",
            font=("Microsoft JhengHei UI", 14, "bold"),
        ).pack(anchor="w")
        tk.Label(
            left,
            text="Google OR-Tools CP-SAT 智慧裁切、排樣、五廠排程與 ISO 9001 / 14001 / WCAG 2.1 AAA 桌面端系統",
            bg="#0f3d68",
            fg="#bae6fd",
            font=("Microsoft JhengHei UI", 9),
        ).pack(anchor="w")

        right = tk.Frame(hdr, bg="#0f3d68")
        right.pack(side="right")

        tk.Button(
            right,
            text="🌐 啟動獨立 Web App 視窗 (--app)",
            bg="#e65100",
            fg="#ffffff",
            font=("Microsoft JhengHei UI", 9, "bold"),
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2",
            command=lambda: launch_standalone_webapp_window(self.base_url),
        ).pack(side="left", padx=4)

        tk.Button(
            right,
            text="🎨 高對比無障礙 (Alt+H)",
            bg="#1e293b",
            fg="#facc15",
            font=("Microsoft JhengHei UI", 9, "bold"),
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2",
            command=self.toggle_high_contrast,
        ).pack(side="left", padx=4)

        tk.Button(
            right,
            text="A+",
            bg="#334155",
            fg="#ffffff",
            font=("Microsoft JhengHei UI", 9, "bold"),
            relief="flat",
            padx=8,
            pady=5,
            command=lambda: self.adjust_font(1),
        ).pack(side="left", padx=2)

        tk.Button(
            right,
            text="A-",
            bg="#334155",
            fg="#ffffff",
            font=("Microsoft JhengHei UI", 9, "bold"),
            relief="flat",
            padx=8,
            pady=5,
            command=lambda: self.adjust_font(-1),
        ).pack(side="left", padx=2)

        tk.Button(
            right,
            text="💾 匯出 CP-SAT 報告",
            bg="#00897b",
            fg="#ffffff",
            font=("Microsoft JhengHei UI", 9, "bold"),
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2",
            command=self.export_json_report,
        ).pack(side="left", padx=4)

    def _build_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=8)

        self.tab_1d = ttk.Frame(self.notebook)
        self.tab_2d = ttk.Frame(self.notebook)
        self.tab_sched = ttk.Frame(self.notebook)
        self.tab_alloy = ttk.Frame(self.notebook)
        self.tab_assets = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_1d, text=" ⚡ 1. 鋁捲分條/圓棒裁切 (1D CP-SAT) ")
        self.notebook.add(self.tab_2d, text=" 📐 2. 鋁板二維排樣 (2D AddNoOverlap2D) ")
        self.notebook.add(self.tab_sched, text=" 🏭 3. 全台五廠區智慧排程 (Job-Shop) ")
        self.notebook.add(self.tab_alloy, text=" 🧪 4. 智慧選材 & 重量公差計算機 ")
        self.notebook.add(self.tab_assets, text=" 🖼️ 5. 官網 61 張照片與全站資料庫 ")

        self._init_tab_1d()
        self._init_tab_2d()
        self._init_tab_sched()
        self._init_tab_alloy()
        self._init_tab_assets()

    def _build_statusbar(self):
        self.status_var = tk.StringVar(
            value=f"✅ Waitress 內嵌伺服器運行中: {self.base_url}  |  求解引擎: Google OR-Tools CP-SAT (ortools.sat.python.cp_model)  |  ISO 9001 / 14001 / WCAG 2.1 AAA 已啟用"
        )
        bar = tk.Label(
            self,
            textvariable=self.status_var,
            bg="#0f172a",
            fg="#38bdf8",
            anchor="w",
            padx=12,
            pady=5,
            font=("Microsoft JhengHei UI", 9),
        )
        bar.pack(fill="x", side="bottom")

    def toggle_high_contrast(self):
        self.high_contrast = not self.high_contrast
        self._apply_theme()
        self._run_initial_solves()

    def adjust_font(self, delta: int):
        self.font_size = max(9, min(14, self.font_size + delta))
        self._apply_theme()

    def export_json_report(self):
        path = filedialog.asksaveasfilename(
            title="匯出 Google OR-Tools CP-SAT 智慧最佳化報告 (ISO 9001 數位紀錄)",
            defaultextension=".json",
            initialfile="harvard_cpsat_optimization_report.json",
            filetypes=[("JSON Report", "*.json"), ("All Files", "*.*")],
        )
        if path:
            Path(path).write_text(json.dumps(self.last_results, ensure_ascii=False, indent=2), encoding="utf-8")
            messagebox.showinfo("匯出成功", f"已成功匯出 ISO 9001 / CP-SAT 最佳化報告至：\n{path}")

    # ========================================================================
    # Tab 1: 1D Cutting Stock Optimization
    # ========================================================================
    def _init_tab_1d(self):
        paned = ttk.PanedWindow(self.tab_1d, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=6, pady=6)

        left = ttk.Frame(paned, padding=8)
        right = ttk.Frame(paned, padding=8)
        paned.add(left, weight=2)
        paned.add(right, weight=3)

        ttk.Label(left, text="母捲寬度 / 圓棒母材參數設定", font=("Microsoft JhengHei UI", 11, "bold")).pack(anchor="w", pady=(0, 6))

        form = ttk.Frame(left)
        form.pack(fill="x", pady=4)

        ttk.Label(form, text="母材總寬/總長 (mm):").grid(row=0, column=0, sticky="w", pady=3)
        self.v1d_mother = tk.StringVar(value="1250")
        ttk.Combobox(form, textvariable=self.v1d_mother, values=["1250", "1220", "1524", "2500", "3000"], width=12).grid(row=0, column=1, sticky="w", padx=6)

        ttk.Label(form, text="鋁合金編號:").grid(row=0, column=2, sticky="w", pady=3)
        self.v1d_alloy = tk.StringVar(value="5052")
        ttk.Combobox(form, textvariable=self.v1d_alloy, values=[a["code"] for a in ALLOY_DB], width=10).grid(row=0, column=3, sticky="w", padx=6)

        ttk.Label(form, text="厚度 (mm):").grid(row=1, column=0, sticky="w", pady=3)
        self.v1d_thick = tk.StringVar(value="1.0")
        ttk.Entry(form, textvariable=self.v1d_thick, width=10).grid(row=1, column=1, sticky="w", padx=6)

        ttk.Label(form, text="刀縫 Kerf (mm):").grid(row=1, column=2, sticky="w", pady=3)
        self.v1d_kerf = tk.StringVar(value="2")
        ttk.Entry(form, textvariable=self.v1d_kerf, width=10).grid(row=1, column=3, sticky="w", padx=6)

        ttk.Label(form, text="雙邊修邊 Trim (mm):").grid(row=2, column=0, sticky="w", pady=3)
        self.v1d_trim = tk.StringVar(value="10")
        ttk.Entry(form, textvariable=self.v1d_trim, width=10).grid(row=2, column=1, sticky="w", padx=6)

        ttk.Label(left, text="客戶分條 / 裁切需求清單", font=("Microsoft JhengHei UI", 10, "bold")).pack(anchor="w", pady=(10, 4))

        cols = ("label", "width", "qty")
        self.tree_1d = ttk.Treeview(left, columns=cols, show="headings", height=7)
        self.tree_1d.heading("label", text="規格品名 / 用途")
        self.tree_1d.heading("width", text="寬度/長度 (mm)")
        self.tree_1d.heading("qty", text="需求數量")
        self.tree_1d.column("label", width=180)
        self.tree_1d.column("width", width=110, anchor="center")
        self.tree_1d.column("qty", width=80, anchor="center")
        self.tree_1d.pack(fill="x", pady=4)

        default_1d = [
            ("電子散熱鰭片鋁帶", 280, 4),
            ("車用精密沖壓鋁條", 210, 5),
            ("光學鏡頭遮光圈料", 165, 4),
            ("銘牌與面板飾條料", 120, 4),
        ]
        for row in default_1d:
            self.tree_1d.insert("", "end", values=row)

        add_frame = ttk.Frame(left)
        add_frame.pack(fill="x", pady=4)
        self.v1d_new_lbl = tk.StringVar(value="客製分條鋁帶")
        self.v1d_new_w = tk.StringVar(value="150")
        self.v1d_new_q = tk.StringVar(value="3")
        ttk.Entry(add_frame, textvariable=self.v1d_new_lbl, width=16).pack(side="left", padx=2)
        ttk.Entry(add_frame, textvariable=self.v1d_new_w, width=8).pack(side="left", padx=2)
        ttk.Entry(add_frame, textvariable=self.v1d_new_q, width=6).pack(side="left", padx=2)
        ttk.Button(add_frame, text="＋新增", command=self._add_1d_row).pack(side="left", padx=4)
        ttk.Button(add_frame, text="－刪除選取", command=self._del_1d_row).pack(side="left", padx=2)

        ttk.Button(
            left,
            text="⚡ 執行 OR-Tools CP-SAT 1D 分條最佳化求解",
            style="Accent.TButton",
            command=self.solve_1d_ui,
        ).pack(fill="x", pady=10)

        self.lbl_1d_summary = ttk.Label(left, text="", justify="left", wraplength=430)
        self.lbl_1d_summary.pack(fill="x", pady=4)

        ttk.Label(right, text="CP-SAT 一維母捲分條 / 圓棒裁切視覺化配置圖", font=("Microsoft JhengHei UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        self.canvas_1d = tk.Canvas(right, bg="#ffffff", highlightthickness=1, highlightbackground="#cbd5e1")
        self.canvas_1d.pack(fill="both", expand=True)

    def _add_1d_row(self):
        try:
            w = int(self.v1d_new_w.get())
            q = int(self.v1d_new_q.get())
            self.tree_1d.insert("", "end", values=(self.v1d_new_lbl.get(), w, q))
        except ValueError:
            messagebox.showwarning("輸入錯誤", "寬度與數量請輸入整數。")

    def _del_1d_row(self):
        for sel in self.tree_1d.selection():
            self.tree_1d.delete(sel)

    def solve_1d_ui(self):
        demands = []
        for idx, iid in enumerate(self.tree_1d.get_children()):
            lbl, w, q = self.tree_1d.item(iid, "values")
            demands.append({"id": f"D{idx+1}", "label": lbl, "width": int(w), "qty": int(q)})

        res = solve_1d_cutting_stock(
            mother_length=int(self.v1d_mother.get() or 1250),
            demands=demands,
            kerf=int(self.v1d_kerf.get() or 2),
            trim_allowance=int(self.v1d_trim.get() or 10),
            alloy_code=self.v1d_alloy.get() or "5052",
            thickness_mm=float(self.v1d_thick.get() or 1.0),
        )
        self.last_results["1d_cutting"] = res
        if res.get("status") not in ("OPTIMAL", "FEASIBLE"):
            self.lbl_1d_summary.config(text=f"求解失敗: {res.get('message', '')}")
            return

        summary_txt = (
            f"【求解狀態】{res['status']} ({res['solve_time_ms']} ms)\n"
            f"【最少母材數】{res['total_mothers_used']} 支 (母材寬 {res['mother_length_mm']} mm)\n"
            f"【整體材料利用率】{res['overall_utilization_pct']}%\n"
            f"【成品淨重 / 總重】{res['net_product_weight_kg']} kg / {res['total_weight_kg']} kg\n"
            f"【ISO 14001 減碳效益】-{res['iso14001_carbon_saved_kg_co2e']} kg CO₂e\n"
            f"【建議派工廠區】{res['recommended_plant']}"
        )
        self.lbl_1d_summary.config(text=summary_txt)
        self._draw_1d_canvas(res)

    def _draw_1d_canvas(self, res: dict):
        c = self.canvas_1d
        c.delete("all")
        c.update_idletasks()
        cw = max(c.winfo_width(), 640)
        margin_x = 24
        bar_w = cw - 2 * margin_x
        y = 24
        mother_len = res["mother_length_mm"]

        for sched in res.get("schedules", []):
            c.create_text(
                margin_x,
                y,
                anchor="nw",
                text=f"母材 #{sched['mother_index']}  |  有效產出: {sched['used_mm']}/{mother_len} mm  |  利用率: {sched['utilization_pct']}%  |  圓盤刀數: {sched['knives_used']} 把",
                font=("Microsoft JhengHei UI", 10, "bold"),
                fill="#0f3d68",
            )
            y += 24
            x = margin_x
            bar_h = 44
            for idx, cut in enumerate(sched["cuts"]):
                seg_w = (cut["subtotal_mm"] / mother_len) * bar_w
                color = COLORS[idx % len(COLORS)]
                c.create_rectangle(x, y, x + seg_w, y + bar_h, fill=color, outline="#ffffff", width=2)
                c.create_text(
                    x + seg_w / 2,
                    y + bar_h / 2,
                    text=f"{cut['label']}\n{cut['width']}mm × {cut['count']}",
                    fill="#ffffff",
                    font=("Microsoft JhengHei UI", 8, "bold"),
                    justify="center",
                )
                x += seg_w
            if x < margin_x + bar_w:
                c.create_rectangle(x, y, margin_x + bar_w, y + bar_h, fill="#cbd5e1", outline="#ffffff", width=1)
                c.create_text(
                    (x + margin_x + bar_w) / 2,
                    y + bar_h / 2,
                    text=f"餘料 {sched['total_loss_mm']}mm",
                    fill="#1e293b",
                    font=("Microsoft JhengHei UI", 8),
                )
            y += bar_h + 26

    # ========================================================================
    # Tab 2: 2D Plate Cutting Optimization (AddNoOverlap2D)
    # ========================================================================
    def _init_tab_2d(self):
        paned = ttk.PanedWindow(self.tab_2d, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=6, pady=6)

        left = ttk.Frame(paned, padding=8)
        right = ttk.Frame(paned, padding=8)
        paned.add(left, weight=2)
        paned.add(right, weight=3)

        ttk.Label(left, text="鋁母板規格與二維排樣設定 (AddNoOverlap2D)", font=("Microsoft JhengHei UI", 11, "bold")).pack(anchor="w", pady=(0, 6))

        form = ttk.Frame(left)
        form.pack(fill="x", pady=4)

        ttk.Label(form, text="母板尺寸 (mm):").grid(row=0, column=0, sticky="w", pady=3)
        self.v2d_plate = tk.StringVar(value="1220x2440")
        ttk.Combobox(form, textvariable=self.v2d_plate, values=["1220x2440", "1250x2500", "1524x3048"], width=14).grid(row=0, column=1, sticky="w", padx=6)

        ttk.Label(form, text="鋁板材質:").grid(row=0, column=2, sticky="w", pady=3)
        self.v2d_alloy = tk.StringVar(value="6061")
        ttk.Combobox(form, textvariable=self.v2d_alloy, values=["6061", "7075", "5083", "5052"], width=10).grid(row=0, column=3, sticky="w", padx=6)

        ttk.Label(form, text="板厚 (mm):").grid(row=1, column=0, sticky="w", pady=3)
        self.v2d_thick = tk.StringVar(value="15.0")
        ttk.Entry(form, textvariable=self.v2d_thick, width=10).grid(row=1, column=1, sticky="w", padx=6)

        ttk.Label(form, text="鋸路 Kerf (mm):").grid(row=1, column=2, sticky="w", pady=3)
        self.v2d_kerf = tk.StringVar(value="3")
        ttk.Entry(form, textvariable=self.v2d_kerf, width=10).grid(row=1, column=3, sticky="w", padx=6)

        self.v2d_rot = tk.BooleanVar(value=True)
        ttk.Checkbutton(form, text="允許 90° 旋轉排樣", variable=self.v2d_rot).grid(row=2, column=0, columnspan=2, sticky="w", pady=3)

        cols = ("label", "w", "h", "qty")
        self.tree_2d = ttk.Treeview(left, columns=cols, show="headings", height=7)
        self.tree_2d.heading("label", text="零件名稱")
        self.tree_2d.heading("w", text="寬 (mm)")
        self.tree_2d.heading("h", text="長 (mm)")
        self.tree_2d.heading("qty", text="數量")
        self.tree_2d.column("label", width=160)
        self.tree_2d.column("w", width=80, anchor="center")
        self.tree_2d.column("h", width=80, anchor="center")
        self.tree_2d.column("qty", width=65, anchor="center")
        self.tree_2d.pack(fill="x", pady=4)

        default_2d = [
            ("半導體腔體底板", 600, 800, 2),
            ("自動化機台側板", 550, 750, 2),
            ("光學治具安裝板", 400, 500, 3),
            ("散熱模組基板", 350, 400, 2),
        ]
        for r in default_2d:
            self.tree_2d.insert("", "end", values=r)

        ttk.Button(
            left,
            text="📐 執行 OR-Tools CP-SAT 2D 鋁板排樣求解",
            style="Accent.TButton",
            command=self.solve_2d_ui,
        ).pack(fill="x", pady=10)

        self.lbl_2d_summary = ttk.Label(left, text="", justify="left", wraplength=430)
        self.lbl_2d_summary.pack(fill="x", pady=4)

        ttk.Label(right, text="CP-SAT 二維鋁板精密裁切排樣藍圖 (AddNoOverlap2D)", font=("Microsoft JhengHei UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        self.canvas_2d = tk.Canvas(right, bg="#f8fafc", highlightthickness=1, highlightbackground="#cbd5e1")
        self.canvas_2d.pack(fill="both", expand=True)

    def solve_2d_ui(self):
        pw, ph = [int(x) for x in (self.v2d_plate.get() or "1220x2440").split("x")]
        pieces = []
        for idx, iid in enumerate(self.tree_2d.get_children()):
            lbl, w, h, q = self.tree_2d.item(iid, "values")
            pieces.append({"id": f"P{idx+1}", "label": lbl, "w": int(w), "h": int(h), "qty": int(q)})

        res = solve_2d_plate_cutting(
            plate_width=pw,
            plate_height=ph,
            pieces=pieces,
            kerf=int(self.v2d_kerf.get() or 3),
            allow_rotation=bool(self.v2d_rot.get()),
            alloy_code=self.v2d_alloy.get() or "6061",
            thickness_mm=float(self.v2d_thick.get() or 15.0),
        )
        self.last_results["2d_plate"] = res
        if res.get("status") not in ("OPTIMAL", "FEASIBLE"):
            self.lbl_2d_summary.config(text=f"求解失敗: {res.get('message', '')}")
            return

        self.lbl_2d_summary.config(
            text=(
                f"【求解狀態】{res['status']} ({res['solve_time_ms']} ms)\n"
                f"【使用母板數】{res['total_plates_used']} 張 ({pw}×{ph} mm) / 共 {res['total_pieces_placed']} 件\n"
                f"【板材面積利用率】{res['overall_utilization_pct']}%\n"
                f"【成品淨重 / 母板總重】{res['net_parts_weight_kg']} kg / {res['total_plate_weight_kg']} kg\n"
                f"【建議裁切機台】{res['recommended_equipment']}"
            )
        )
        self._draw_2d_canvas(res)

    def _draw_2d_canvas(self, res: dict):
        c = self.canvas_2d
        c.delete("all")
        c.update_idletasks()
        cw = max(c.winfo_width(), 640)
        ch = max(c.winfo_height(), 460)

        plates = res.get("plates", [])
        if not plates:
            return

        n = len(plates)
        slot_w = (cw - 30) / n
        for idx, pl in enumerate(plates):
            pw = pl["plate_width"]
            ph = pl["plate_height"]
            scale = min((slot_w - 24) / pw, (ch - 60) / ph)
            ox = 18 + idx * slot_w
            oy = 36
            c.create_text(
                ox,
                10,
                anchor="nw",
                text=f"母板 #{pl['plate_index']} ({pw}×{ph}mm) - 利用率 {pl['utilization_pct']}%",
                font=("Microsoft JhengHei UI", 10, "bold"),
                fill="#0f3d68",
            )
            c.create_rectangle(ox, oy, ox + pw * scale, oy + ph * scale, fill="#e2e8f0", outline="#0f3d68", width=2)
            for p_idx, p in enumerate(pl["placements"]):
                x1 = ox + p["x"] * scale
                y1 = oy + p["y"] * scale
                x2 = x1 + p["w"] * scale
                y2 = y1 + p["h"] * scale
                color = COLORS[p_idx % len(COLORS)]
                c.create_rectangle(x1, y1, x2, y2, fill=color, outline="#ffffff", width=2)
                rot = " ↻" if p.get("rotated") else ""
                c.create_text(
                    (x1 + x2) / 2,
                    (y1 + y2) / 2,
                    text=f"{p['uid']}{rot}\n{p['w']}×{p['h']}",
                    fill="#ffffff",
                    font=("Microsoft JhengHei UI", 8, "bold"),
                    justify="center",
                )

    # ========================================================================
    # Tab 3: Multi-Plant Job-Shop Scheduling
    # ========================================================================
    def _init_tab_sched(self):
        top = ttk.Frame(self.tab_sched, padding=8)
        top.pack(fill="x")
        ttk.Label(
            top,
            text="賀華實業全台五廠區 (台北廠/新竹永旭廠/台中一廠/台中二廠/台南廠) CP-SAT 智慧產能排程",
            font=("Microsoft JhengHei UI", 11, "bold"),
        ).pack(side="left")
        ttk.Button(top, text="🔄 重新執行五廠排程最佳化", style="Accent.TButton", command=self.solve_sched_ui).pack(side="right")

        self.lbl_sched_kpi = ttk.Label(self.tab_sched, text="", font=("Microsoft JhengHei UI", 10, "bold"), padding=(8, 2))
        self.lbl_sched_kpi.pack(fill="x")

        self.canvas_sched = tk.Canvas(self.tab_sched, bg="#ffffff", height=270, highlightthickness=1, highlightbackground="#cbd5e1")
        self.canvas_sched.pack(fill="x", padx=8, pady=6)

        cols = ("job_id", "customer", "product", "plant", "start", "end", "dur")
        self.tree_sched = ttk.Treeview(self.tab_sched, columns=cols, show="headings", height=7)
        for col, txt, w in [
            ("job_id", "工單編號", 90),
            ("customer", "客戶名稱", 140),
            ("product", "加工鋁材品項", 240),
            ("plant", "CP-SAT 指派最佳廠區", 180),
            ("start", "開始 (hr)", 90),
            ("end", "完工 (hr)", 90),
            ("dur", "工時 (hr)", 90),
        ]:
            self.tree_sched.heading(col, text=txt)
            self.tree_sched.column(col, width=w, anchor="center" if col in ("job_id", "start", "end", "dur") else "w")
        self.tree_sched.pack(fill="both", expand=True, padx=8, pady=4)

    def solve_sched_ui(self):
        res = solve_multi_plant_schedule()
        self.last_results["schedule"] = res
        self.lbl_sched_kpi.config(
            text=f"【CP-SAT 排程狀態】{res['status']} ({res['solve_time_ms']} ms)   |   【總完工時間 Makespan】{res['makespan_hr']} 小時   |   【調度工單數】{res['total_jobs']} 筆跨廠區工單"
        )
        for iid in self.tree_sched.get_children():
            self.tree_sched.delete(iid)
        for a in res.get("assignments", []):
            self.tree_sched.insert(
                "",
                "end",
                values=(a["job_id"], a["customer"], a["product"], a["assigned_plant_name"], f"{a['start_hr']}h", f"{a['end_hr']}h", f"{a['duration_hr']}h"),
            )
        self._draw_sched_canvas(res)

    def _draw_sched_canvas(self, res: dict):
        c = self.canvas_sched
        c.delete("all")
        c.update_idletasks()
        cw = max(c.winfo_width(), 900)
        left_w = 210
        chart_w = cw - left_w - 30
        max_hr = max(res.get("makespan_hr", 10), 10)

        for idx, p in enumerate(res.get("plants", [])):
            y = 18 + idx * 48
            c.create_text(12, y + 16, anchor="w", text=p["name"], font=("Microsoft JhengHei UI", 9, "bold"), fill="#0f3d68")
            c.create_rectangle(left_w, y, left_w + chart_w, y + 34, fill="#f1f5f9", outline="#cbd5e1")
            jobs = [a for a in res.get("assignments", []) if a["assigned_plant_id"] == p["id"]]
            for j_idx, j in enumerate(jobs):
                x1 = left_w + (j["start_hr"] / max_hr) * chart_w
                x2 = left_w + (j["end_hr"] / max_hr) * chart_w
                color = COLORS[(idx + j_idx) % len(COLORS)]
                c.create_rectangle(x1, y + 3, x2, y + 31, fill=color, outline="#ffffff", width=1)
                c.create_text(
                    (x1 + x2) / 2,
                    y + 17,
                    text=f"{j['job_id']} {j['customer']} ({j['duration_hr']}h)",
                    fill="#ffffff",
                    font=("Microsoft JhengHei UI", 8, "bold"),
                )

    # ========================================================================
    # Tab 4: Smart Alloy Selection & Weight Calculator
    # ========================================================================
    def _init_tab_alloy(self):
        paned = ttk.PanedWindow(self.tab_alloy, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=6, pady=6)

        left = ttk.Frame(paned, padding=8)
        right = ttk.Frame(paned, padding=8)
        paned.add(left, weight=3)
        paned.add(right, weight=2)

        ttk.Label(left, text="CP-SAT 鋁合金多準則智慧選材決策系統", font=("Microsoft JhengHei UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        f_al = ttk.Frame(left)
        f_al.pack(fill="x", pady=4)

        self.val_corr = tk.IntVar(value=80)
        self.val_str = tk.IntVar(value=65)
        self.val_form = tk.IntVar(value=65)
        self.val_mach = tk.IntVar(value=60)
        self.val_weld = tk.IntVar(value=60)

        for r_idx, (lbl, var) in enumerate([
            ("最低耐蝕性 (0~100):", self.val_corr),
            ("最低機械強度 (0~100):", self.val_str),
            ("最低成形性 (0~100):", self.val_form),
            ("最低切削加工性 (0~100):", self.val_mach),
            ("最低熔接性 (0~100):", self.val_weld),
        ]):
            ttk.Label(f_al, text=lbl).grid(row=r_idx // 3, column=(r_idx % 3) * 2, sticky="w", pady=3)
            ttk.Spinbox(f_al, from_=0, to=100, textvariable=var, width=7).grid(row=r_idx // 3, column=(r_idx % 3) * 2 + 1, sticky="w", padx=6)

        ttk.Button(left, text="🔍 執行 CP-SAT 鋁合金智慧推薦", style="Accent.TButton", command=self.solve_alloy_ui).pack(fill="x", pady=8)

        cols = ("code", "series", "score", "density", "forms", "applications")
        self.tree_alloy = ttk.Treeview(left, columns=cols, show="headings", height=11)
        for col, txt, w in [
            ("code", "合金編號", 80),
            ("series", "合金系列", 130),
            ("score", "CP-SAT 適配度", 100),
            ("density", "比重", 65),
            ("forms", "供應形態", 160),
            ("applications", "典型用途與特性", 260),
        ]:
            self.tree_alloy.heading(col, text=txt)
            self.tree_alloy.column(col, width=w)
        self.tree_alloy.pack(fill="both", expand=True, pady=4)

        # Right: Weight & Tolerance Calculator
        ttk.Label(right, text="ISO / JIS / CNS 鋁材重量與公差計算機", font=("Microsoft JhengHei UI", 11, "bold")).pack(anchor="w", pady=(0, 8))
        fc = ttk.Frame(right)
        fc.pack(fill="x")

        self.vwc_shape = tk.StringVar(value="鋁板/平片 (Plate/Sheet)")
        self.vwc_density = tk.StringVar(value="2.70")
        self.vwc_d1 = tk.StringVar(value="15.0")
        self.vwc_d2 = tk.StringVar(value="1220.0")
        self.vwc_d3 = tk.StringVar(value="2440.0")
        self.vwc_qty = tk.StringVar(value="2")

        for r_idx, (lbl, var, vals) in enumerate([
            ("材料形狀:", self.vwc_shape, ["鋁板/平片 (Plate/Sheet)", "實心鋁圓棒 (Rod)", "中空鋁圓管 (Tube)"]),
            ("鋁合金比重 (g/cm³):", self.vwc_density, ["2.71", "2.73", "2.68", "2.66", "2.70", "2.78", "2.81"]),
            ("厚度 或 外徑 (mm):", self.vwc_d1, None),
            ("寬度 或 內徑 (mm):", self.vwc_d2, None),
            ("長度 (mm):", self.vwc_d3, None),
            ("數量 (件/支):", self.vwc_qty, None),
        ]):
            ttk.Label(fc, text=lbl).grid(row=r_idx, column=0, sticky="w", pady=5)
            if vals:
                ttk.Combobox(fc, textvariable=var, values=vals, width=22).grid(row=r_idx, column=1, sticky="w", padx=8)
            else:
                ttk.Entry(fc, textvariable=var, width=24).grid(row=r_idx, column=1, sticky="w", padx=8)

        ttk.Button(right, text="⚖️ 立即計算理論重量與標準公差", style="Primary.TButton", command=self.calc_weight_ui).pack(fill="x", pady=12)
        self.lbl_weight_out = ttk.Label(right, text="", font=("Microsoft JhengHei UI", 10, "bold"), justify="left", wraplength=360)
        self.lbl_weight_out.pack(fill="x", pady=8)

    def solve_alloy_ui(self):
        res = solve_alloy_recommendation(
            min_corrosion=int(self.val_corr.get()),
            min_strength=int(self.val_str.get()),
            min_formability=int(self.val_form.get()),
            min_machinability=int(self.val_mach.get()),
            min_weldability=int(self.val_weld.get()),
        )
        self.last_results["alloy_select"] = res
        for iid in self.tree_alloy.get_children():
            self.tree_alloy.delete(iid)
        for a in res.get("all_alloys", []):
            self.tree_alloy.insert(
                "",
                "end",
                values=(a["code"], a["series"], f"{a['match_score']}%", a["density_g_cm3"], "、".join(a["forms"]), a["applications"]),
            )

    def calc_weight_ui(self):
        try:
            shape = self.vwc_shape.get()
            density = float(self.vwc_density.get())
            d1 = float(self.vwc_d1.get())
            d2 = float(self.vwc_d2.get())
            d3 = float(self.vwc_d3.get())
            qty = int(self.vwc_qty.get())
            if "圓棒" in shape:
                r = (d1 / 2.0) / 10.0
                vol = math.pi * r * r * (d3 / 10.0)
            elif "圓管" in shape:
                ro = (d1 / 2.0) / 10.0
                ri = min(ro, (d2 / 2.0) / 10.0)
                vol = math.pi * (ro * ro - ri * ri) * (d3 / 10.0)
            else:
                vol = (d1 / 10.0) * (d2 / 10.0) * (d3 / 10.0)
            single_kg = (vol * density) / 1000.0
            total_kg = single_kg * qty
            tol = "±0.04mm" if d1 <= 1.0 else ("±0.12mm" if d1 <= 6.0 else ("±0.50mm" if d1 <= 50 else "±1.20mm"))
            self.lbl_weight_out.config(
                text=(
                    f"● 單件理論重量：{single_kg:.3f} kg\n"
                    f"● 總重量 ({qty} 件)：{total_kg:.2f} kg\n"
                    f"● CNS/JIS 厚度公差參考：{tol}\n"
                    f"● 精密裁切長度公差：+1.5 / -0 mm"
                )
            )
        except Exception as e:
            self.lbl_weight_out.config(text=f"計算參數錯誤: {e}")

    # ========================================================================
    # Tab 5: Complete 61 Photos & Full Website Explorer
    # ========================================================================
    def _init_tab_assets(self):
        paned = ttk.PanedWindow(self.tab_assets, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=6, pady=6)

        left = ttk.Frame(paned, padding=8)
        right = ttk.Frame(paned, padding=8)
        paned.add(left, weight=2)
        paned.add(right, weight=3)

        ttk.Label(left, text="官網全部 61 張原始照片資產清單 (點擊即時預覽)", font=("Microsoft JhengHei UI", 11, "bold")).pack(anchor="w", pady=(0, 6))

        cols = ("fname", "desc")
        self.tree_imgs = ttk.Treeview(left, columns=cols, show="headings", height=16)
        self.tree_imgs.heading("fname", text="檔案名稱")
        self.tree_imgs.heading("desc", text="WCAG 2.1 無障礙圖說與內容描述")
        self.tree_imgs.column("fname", width=120)
        self.tree_imgs.column("desc", width=320)
        self.tree_imgs.pack(fill="both", expand=True, pady=4)

        img_dir = BASE_DIR / "images"
        if img_dir.exists():
            for f in sorted(img_dir.iterdir()):
                if f.is_file():
                    self.tree_imgs.insert("", "end", values=(f.name, IMAGE_DESCRIPTIONS.get(f.name, f.name)))

        self.tree_imgs.bind("<<TreeviewSelect>>", self._on_select_image)

        ttk.Label(right, text="照片原圖預覽與全站網頁快速開啟", font=("Microsoft JhengHei UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        self.lbl_img_title = ttk.Label(right, text="請由左側清單點擊任一照片預覽", font=("Microsoft JhengHei UI", 10, "bold"))
        self.lbl_img_title.pack(anchor="w", pady=4)

        self.canvas_img = tk.Canvas(right, bg="#1e293b", height=360, highlightthickness=1, highlightbackground="#cbd5e1")
        self.canvas_img.pack(fill="both", expand=True, pady=4)

        pages_box = ttk.Frame(right)
        pages_box.pack(fill="x", pady=6)
        ttk.Label(pages_box, text="一鍵開啟全站頁面：", font=("Microsoft JhengHei UI", 9, "bold")).pack(anchor="w", pady=2)

        btn_row = ttk.Frame(pages_box)
        btn_row.pack(fill="x")
        for label, page in [
            ("首頁 index", "index.html"),
            ("關於賀華 about", "about.html"),
            ("關係企業 affiliates", "affiliates.html"),
            ("產品服務 service", "service.html"),
            ("鋁合金介紹 aluminum", "aluminum.html"),
            ("永旭材料 yongsyu", "yongsyu.html"),
            ("人才招募 recruiting", "recruiting.html"),
            ("聯絡我們 contact", "contact.html"),
        ]:
            ttk.Button(
                btn_row,
                text=label,
                command=lambda p=page: launch_standalone_webapp_window(f"{self.base_url}/{p}"),
            ).pack(side="left", padx=2, pady=2)

    def _on_select_image(self, _event=None):
        sel = self.tree_imgs.selection()
        if not sel:
            return
        fname, desc = self.tree_imgs.item(sel[0], "values")
        img_path = BASE_DIR / "images" / fname
        self.lbl_img_title.config(text=f"📷 {fname} — {desc}")
        self.canvas_img.delete("all")
        if not img_path.exists():
            return

        cw = max(self.canvas_img.winfo_width(), 520)
        ch = max(self.canvas_img.winfo_height(), 340)

        if HAS_PIL:
            pil_img = Image.open(img_path)
            pil_img.thumbnail((cw - 20, ch - 20))
            self._current_photo = ImageTk.PhotoImage(pil_img)
            self.canvas_img.create_image(cw // 2, ch // 2, image=self._current_photo, anchor="center")
        else:
            self.canvas_img.create_text(cw // 2, ch // 2, text=f"{fname}\n({desc})", fill="#ffffff", font=("Microsoft JhengHei UI", 12, "bold"))

    def _run_initial_solves(self):
        self.solve_1d_ui()
        self.solve_2d_ui()
        self.solve_sched_ui()
        self.solve_alloy_ui()
        self.calc_weight_ui()
        children = self.tree_imgs.get_children()
        if children:
            self.tree_imgs.selection_set(children[0])
            self._on_select_image()


def start_background_waitress(port: int):
    from waitress import serve
    t = threading.Thread(
        target=lambda: serve(flask_app, host="127.0.0.1", port=port, threads=6),
        daemon=True,
    )
    t.start()
    return t


def run_self_test():
    """提供自動化驗證模式 (--test)，確認四大 CP-SAT 求解器與 61 張圖檔皆正常運作"""
    r1 = solve_1d_cutting_stock()
    r2 = solve_2d_plate_cutting()
    r3 = solve_multi_plant_schedule()
    r4 = solve_alloy_recommendation()
    imgs = list((BASE_DIR / "images").glob("*.*"))
    assert r1["status"] in ("OPTIMAL", "FEASIBLE"), "1D CP-SAT failed"
    assert r2["status"] in ("OPTIMAL", "FEASIBLE"), "2D CP-SAT failed"
    assert r3["status"] in ("OPTIMAL", "FEASIBLE"), "Schedule CP-SAT failed"
    assert r4["status"] == "OPTIMAL", "Alloy CP-SAT failed"
    assert len(imgs) == 61, f"Expected 61 images, got {len(imgs)}"
    print("DESKTOP_APP_SELF_TEST_OK")
    print(f" - 1D Cutting: {r1['status']} ({r1['overall_utilization_pct']}%)")
    print(f" - 2D Plate  : {r2['status']} ({r2['overall_utilization_pct']}%)")
    print(f" - Schedule  : {r3['status']} (Makespan {r3['makespan_hr']}h)")
    print(f" - Alloy Rec : {r4['status']} (Top: {r4['top_recommendations'][0]['code']})")
    print(f" - Images    : {len(imgs)} verified")


if __name__ == "__main__":
    if "--test" in sys.argv:
        run_self_test()
        sys.exit(0)

    port = find_free_port(8080)
    start_background_waitress(port)
    app_win = HarvardDesktopApp(server_port=port)
    app_win.mainloop()
