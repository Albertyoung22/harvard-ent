# 賀華實業股份有限公司 | HARVARD ENTERPRISES INC. — 智慧科技互動系統 & 桌面應用程式

> **深耕台灣逾 50 載（創立於 1973 年 4 月 25 日） · 全方位鋁合金供應鏈、雙面精銑分條與 Google OR-Tools CP-SAT 智慧工程平台**  
> **視覺風格**：未來科技感 · 深空量子藍與霓虹電漿青主題 (Futuristic High-Tech Cyber-Metallurgy Theme)  
> **核心引擎**：`Python Flask` + `Waitress` + `Google OR-Tools CP-SAT (ortools.sat.python.cp_model)` + `Microsoft Edge-TTS` + `Windows WebView2 (pywebview)`

---

## 🌟 系統核心亮點

1. **100% 完整保留官網資料與 61 張原始實拍圖鑑（一樣不漏）**
   - 完整收錄 `https://www.harvard-ent.com.tw/` 繁中 (`ch/`)、英文 (`en/`)、日文 (`jp/`) 所有內容與 **61 張原始高畫質照片**（`banner1~5.jpg`, `a1.jpg`, `ab1.jpg`, `alu01~09.jpg`, `g1~3.jpg`, `s01~30.jpg`, `royal-1~5.png`, `c-anda.png`, `c-anda2.png`, `c-fufong.png`, `c-futsu.png`, `c-ikeuchi.png`, `logo_brand.png`, `top_up.png`）。
   - 完整呈現 **全台五大廠區**：台北廠 (八里倉庫)、新竹廠 (永旭材料)、台中一廠 (神岡)、台中二廠 (神岡薄板分條中心)、台南廠 (永康)，以及關係企業（安達磨光鋼棒、日本池內 IKEUCHI 二流體噴嘴）。

2. **未來科技感 (High-Tech Sci-Fi Cybernetic UI) 沉浸式互動體驗**
   - **3D 量子晶格與雷射透視網格動態背景 (`#latticeCanvas`)**：全息投影 HUD 陀螺儀、FCC 鋁原子六方晶格、3D 透視地平線掃描網格、70+ 量子節點星座連線與滑鼠聲納脈衝特效。
   - **無縫 SPA 九大分頁架構**：首頁總覽 (`/`)、關於我們 (`/about`)、服務網絡 (`/network`)、旗艦材料 (`/products`)、現貨規格 (`/specs` 3,081 筆)、精密加工 (`/machining`)、代表實績 (`/cases`)、技術知識庫 (`/tech`)、聯絡諮詢 (`/contact`)。
   - **四國語言即時切換 (`zh-TW` / `en` / `ja` / `ko`)** + **Edge-TTS 真人神經網路語音導覽與錄音室背景輕音樂自動避讓 (Audio Ducking)**。

3. **Google OR-Tools CP-SAT (`ortools.sat.python.cp_model`) 四大整數約束規劃引擎**
   - **1D 母材定寸裁切排料 (`solve_1d_cutting_stock` / `solve_cutting_stock_cpsat`)**：計算最少母材支數、考慮鋸縫損耗 (Kerf) 並即時繪製互動式 SVG 排刀視覺圖。
   - **2D 鋁板矩形無重疊排樣 (`solve_2d_plate_cutting` 使用 `model.AddNoOverlap2D`)**：支援 90° 旋轉決策變數與二維幾何不重疊約束，提升大尺寸厚板利用率。
   - **全台五廠區智慧產能甘特圖排程 (`solve_multi_plant_schedule` 使用 `model.AddNoOverlap`)**：最小化跨廠區總完工時間 (Makespan) 與跨區物流碳足跡。
   - **CP-SAT 多目標合金選型推薦 (`solve_alloy_recommendation`)**：依據抗拉強度、耐蝕性、真平度與加工性自動推薦最適鋁材牌號。

4. **Windows WebView2 原生桌面應用程式 (`desktop_app.py`)**
   - 採用 `pywebview` (`gui='edgechromium'`) 搭配背景多執行緒 `Waitress` 伺服器，具備自訂企業圖示 (`app.ico`)、Windows 10/11 原生 Toast 詢價通知推播與桌面捷徑 (`賀華實業 - 智慧科技互動系統.lnk`)。

5. **ISO 國際認證與 WCAG 2.1 AA 無障礙合規**
   - 內建 ISO 9001:2015、AS9100D、ISO 14001、EU RoHS 2.0 / REACH SVHC 品質保證專區與高對比無障礙鍵盤導覽支援。

---

## 🚀 快速啟動方式

### 1. 啟動 Windows 桌面應用程式 (Desktop App)
雙擊桌面上的 **「賀華實業 - 智慧科技互動系統」** 捷徑，或執行：
```bash
start_desktop.bat
# 或
python desktop_app.py
```

### 2. 啟動 Waitress + Flask 生產級網頁伺服器
```bash
start_server.bat
# 或
python run.py
```
瀏覽器開啟：`http://localhost:5000`（管理後台：`http://localhost:5000/admin`）

### 3. 部署至 Render 雲端平台
本專案已內建 `Procfile` 與 `render.yaml`：
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `waitress-serve --host=0.0.0.0 --port=$PORT --threads=8 app:app`
