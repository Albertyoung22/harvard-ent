# 賀華實業股份有限公司 (HARVARD ENTERPRISES INC.)
## 智慧化 × Google OR-Tools CP-SAT × ISO 認證 × WCAG 2.1 AAA 無障礙 × Web & Desktop 雙棲系統

本專案完整重現並全面升級 **[賀華實業股份有限公司 (https://www.harvard-ent.com.tw/)](https://www.harvard-ent.com.tw/)** 官方網站之**所有頁面、規格表、多語系版本（繁中/簡中/英文/日文）與全部 61 張原始照片（100% 零遺漏）**，並結合 **Python Google OR-Tools CP-SAT 約束規劃求解器 (`ortools.sat.python.cp_model`)**、**Flask + Waitress 生產級伺服器** 與 **Windows 原生桌面應用程式 (`desktop_app.py`)**。

---

## 🌟 核心功能亮點

### 1. 100% 原始網站資料與 61 張照片零遺漏
- **完整保留所有頁面**：
  - 繁體中文主站：`index.html`、`about.html`、`affiliates.html`、`service.html`、`aluminum.html`、`yongsyu.html`、`recruiting.html`、`contact.html`
  - 簡體中文 (`ch/`)、英文 (`en/`)、日文 (`jp/`) 全系列頁面
- **完整收錄 61 張原始照片 (`images/`)**：
  - 企業標誌與橫幅：`logo_brand.png`, `banner1.jpg` ~ `banner5.jpg`, `top_up.png`
  - 公司實景與首頁卡片：`a1.jpg`, `ab1.jpg`, `g1.jpg` ~ `g3.jpg`
  - 關係企業與日本合作原廠：`c-anda.png` (安達磨光鋼棒), `c-anda2.png` (永旭材料), `c-fufong.png` (古河電工 Furukawa Sky / UACJ), `c-futsu.png` (住友輕金屬 Sumitomo), `c-ikeuchi.png` (池內 Ikeuchi)
  - 永旭材料精密產線：`royal-1.png` ~ `royal-5.png`
  - 鋁材與裁切產線：`alu01.jpg` ~ `alu09.jpg`
  - 加工成品與包裝實照：`s01.jpg` ~ `s30.jpg`

### 2. Google OR-Tools CP-SAT (`ortools.sat.python.cp_model`) 四大智慧最佳化引擎 (`cpsat_optimizer.py`)
1. **一維鋁捲分條 / 圓棒裁切下料最佳化 (`solve_1d_cutting_stock`)**：
   - 支援標準母捲寬度 (`1250mm`、`1220mm`、`1524mm`) 與鋁圓棒/擠型長度 (`2500mm`、`3000mm`)，自動扣除圓盤刀縫 (`Kerf`) 與雙邊修邊 (`Trim`)，最小化母材消耗與換刀次數，並計算 **ISO 14001 減碳效益 (kg CO₂e)**。
2. **二維鋁板精密裁切排樣最佳化 (`solve_2d_plate_cutting`)**：
   - 運用 `cp_model.AddNoOverlap2D` 二維正交不重疊約束與 90° 旋轉決策變數，針對 `1220×2440mm`、`1250×2500mm`、`1524×3048mm` 母板進行最佳排樣並繪製 SVG / Canvas 裁切藍圖。
3. **全台五廠區智慧產能排程 (`solve_multi_plant_schedule`)**：
   - 針對賀華實業五大據點（**台北廠/八里倉庫、新竹廠/永旭材料、台中一廠、台中二廠、台南廠**）進行跨廠區 Job-Shop 最佳化排程，最小化總完工時間 (`Makespan`)。
4. **鋁合金多準則智慧選材決策 (`solve_alloy_recommendation`)**：
   - 針對賀華實業 12 大主力鋁合金（`1085`、`1070`、`1050`、`1100`、`2017`、`2024`、`3003`、`5052`、`5083`、`6061`、`6063`、`7075`）進行多準則評分與推薦，並內建 **ISO/JIS/CNS 鋁材重量與公差計算機**。

### 3. ISO 國際標準與 WCAG 2.1 AAA 無障礙設計 (`css/smart-iso-a11y.css`, `js/smart-iso-a11y.js`)
- **ISO/IEC 40500 (WCAG 2.1 AAA) & 台灣數位發展部無障礙規範**：
  - 跳至主要內容連結 (`Skip to Main Content`) 與三區定位導盲磚 `:::` (`Alt+U` 頂部導覽、`Alt+C` 主要內容、`Alt+Z` 頁尾聯絡資訊)
  - 61 張圖檔皆具備完整中文無障礙替代文字 (`alt`)，Google Maps `iframe` 具備明確廠區 `title`
  - 支援 **A- / A / A+ 字級縮放**、**高對比模式 (黑底黃字)**、**深色護眼模式**、**寬行距易讀模式** 與 **Web Speech API 語音朗讀導覽**
  - 所有規格表 (`table.table01`) 自動轉換為具備 `<caption>`、`scope="col"`、**即時關鍵字篩選** 與 **一鍵匯出 CSV (ISO 9001 數位表單)** 之智慧資料表

### 4. 雙模式執行：雲端 Web (Flask + Waitress) & 桌面應用程式 (Desktop App)
- **Web 伺服器 (`app.py`)**：採用 `Flask` 與生產級 WSGI 伺服器 `Waitress`，可直接部署於 **Render**。
- **原生桌面應用程式 (`desktop_app.py`)**：內建五大頁籤（1D 分條 Canvas 視覺化、2D 鋁板排樣藍圖、五廠區甘特圖、智慧選材與重量計算機、61 張照片原圖預覽器），並自動於背景啟動內嵌 Waitress 伺服器。

---

## 🚀 快速啟動指南

### 1. 安裝相依套件
```bash
pip install -r requirements.txt
```

### 2. 啟動桌面應用程式 (Desktop App)
直接雙擊 `啟動賀華實業智慧桌面端_Desktop_App.bat`，或執行：
```bash
python desktop_app.py
```

### 3. 啟動 Flask + Waitress 網頁伺服器
直接雙擊 `啟動Waitress網頁伺服器.bat`，或執行：
```bash
python app.py
```
瀏覽器開啟：`http://127.0.0.1:8080`

### 4. 部署至 Render
1. 將本儲存庫上傳至 GitHub (`https://github.com/Albertyoung22/harvard-ent`)
2. 於 Render 建立 **New Web Service** 或 **Blueprint** 連結該 GitHub 儲存庫
3. Render 會自動讀取 `render.yaml` / `Procfile`：
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
