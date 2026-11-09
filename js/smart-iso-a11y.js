/**
 * 賀華實業股份有限公司 (HARVARD ENTERPRISES INC.)
 * 智慧化 (Google OR-Tools CP-SAT)、ISO 標準認證與 WCAG 2.1 AAA 無障礙前端互動引擎
 */
(function () {
    "use strict";

    // 全站 61 張圖片之完整無障礙替代文字對照表 (確保每一張圖片皆具備精確語意描述)
    const IMAGE_ALT_MAP = {
        "logo_brand.png": "賀華實業股份有限公司 HARVARD ENTERPRISES INC. 企業標誌",
        "top_up.png": "回到頁面頂端按鈕圖示",
        "a1.jpg": "賀華實業股份有限公司自動化鋁材廠房與精密裁切產線實景",
        "ab1.jpg": "賀華實業股份有限公司廠區物流與重型鋁材吊掛設備實景",
        "banner1.jpg": "賀華實業主視覺橫幅：創新求是、追求卓越 (INNOVATION & PROMINENCE)",
        "banner2.jpg": "賀華實業主視覺橫幅：互勉互惠、同享繁榮 (MUTUALISM & CO-PROSPERITY)",
        "banner3.jpg": "賀華實業服務項目：各國精密鋁合金板、捲、片與中鋼鋁業特約經銷倉儲",
        "banner4.jpg": "賀華實業工廠設備：600mm特厚板立式裁切機、紅外線裁切機與自動化倉儲",
        "banner5.jpg": "賀華實業企業基本資料與精密分條裁切設備展示",
        "g1.jpg": "產品資訊：鋁捲片與鋁平片 (Aluminum Alloy Coil & Sheet)",
        "g2.jpg": "產品資訊：高強度精密鋁板 (Aluminum Alloy Plate)",
        "g3.jpg": "產品資訊：鋁圓棒、鋁管與擠型材 (Aluminum Rod, Bar & Extrusions)",
        "c-futsu.png": "關聯企業：互助營造股份有限公司 企業標誌",
        "c-anda.png": "關聯企業：安大營造股份有限公司 企業標誌",
        "c-fufong.png": "關聯企業：互豐建設股份有限公司 企業標誌",
        "c-anda2.png": "關聯企業：安大建設股份有限公司 企業標誌",
        "c-ikeuchi.png": "關聯企業：中日噴霧股份有限公司 (IKEUCHI TAIWAN) 企業標誌",
        "royal-1.png": "關聯企業：老爺酒店集團與老爺管理顧問公司 標誌",
        "royal-2.png": "關聯企業：新竹、知本、礁溪、台北、北投老爺酒店 標誌",
        "royal-3.png": "關聯企業：台南、宜蘭傳藝、台中大毅、南港老爺行旅 (The Place) 標誌",
        "royal-4.png": "關聯企業：老爺會館台北南西與台北林森 (Royal Inn) 標誌",
        "royal-5.png": "關聯企業：帛琉、西貢、模里西斯、尼加拉瓜海外老爺酒店與關西老爺高爾夫球場 標誌",
        "s01.jpg": "鋁捲片/平片服務實景 (一)：大型精密鋁捲庫存與包裝",
        "s02.jpg": "鋁捲片/平片服務實景 (二)：高速金屬分條機生產線",
        "s03.jpg": "鋁捲片/平片服務實景 (三)：整平裁片與皮帶式張力壓料作業",
        "s04.jpg": "鋁捲片/平片服務實景 (四)：精密分條後之窄帶鋁捲成品",
        "s05.jpg": "鋁捲片/平片服務實景 (五)：鋁平片自動堆疊與雙面保護貼膜",
        "s06.jpg": "鋁捲片/平片服務實景 (六)：自動化鋁捲倉儲管理區",
        "s07.jpg": "鋁板服務實景 (一)：特厚固溶鋁板 (6061/7075/5083) 庫存區",
        "s08.jpg": "鋁板服務實景 (二)：可裁切600mm特厚板之立式裁切機作業",
        "s09.jpg": "鋁板服務實景 (三)：高精準直角度紅外線裁切機作業",
        "s10.jpg": "鋁板服務實景 (四)：精密裁切完成之厚鋁板斷面品質展示",
        "s11.jpg": "鋁板服務實景 (五)：鋁板表面壓平與雙面保護貼膜機",
        "s12.jpg": "鋁板服務實景 (六)：立體自動化倉儲系統 (AS/RS) 鋁板儲位",
        "s13.jpg": "圓棒/擠型服務實景 (一)：6061與7075各尺寸鋁圓棒常備庫存",
        "s14.jpg": "圓棒/擠型服務實景 (二)：鋁管、四方條、六角條與扁條擠型材",
        "s15.jpg": "圓棒/擠型服務實景 (三)：高速圓棒裁切機精密定尺加工",
        "s16.jpg": "新竹廠 永旭材料股份有限公司 (一)：廠區外觀與物流出貨中心",
        "s17.jpg": "新竹廠 永旭材料股份有限公司 (二)：半導體專用 6061/6063S 鋁板自動倉儲",
        "s18.jpg": "新竹廠 永旭材料股份有限公司 (三)：大型精密龍門立式帶鋸裁切設備",
        "s19.jpg": "新竹廠 永旭材料股份有限公司 (四)：紅外線定位精密鋁板裁切機",
        "s20.jpg": "新竹廠 永旭材料股份有限公司 (五)：進口瑞士/美鋁/韓鋁貼模板材庫存",
        "s21.jpg": "新竹廠 永旭材料股份有限公司 (六)：厚板精密裁切作業現場",
        "s22.jpg": "新竹廠 永旭材料股份有限公司 (七)：廠內天車吊掛與重型板材搬運系統",
        "s23.jpg": "新竹廠 永旭材料股份有限公司 (八)：精密量測、品檢與貼膜包裝產線",
        "s24.jpg": "新竹廠 永旭材料股份有限公司 (九)：成品待出貨區與防撞包裝保護",
        "s25.jpg": "零零鋁箔/零鋁箔 (一)：現代化潔淨鋁箔軋延與分條廠房全景",
        "s26.jpg": "零零鋁箔/零鋁箔 (二)：高精密零鋁箔輥輪張力控制與表面檢驗",
        "s27.jpg": "零零鋁箔/零鋁箔 (三)：3噸天車與多機台鋁箔高速分條產線",
        "s28.jpg": "零零鋁箔/零鋁箔 (四)：整齊排列於鞍座上之高純度零零鋁箔母捲",
        "s29.jpg": "零零鋁箔/零鋁箔 (五)：超薄鋁箔導輪精密傳動特寫",
        "s30.jpg": "零零鋁箔/零鋁箔 (六)：伺服控制精密圓刀分條裁切頭特寫",
        "alu01.jpg": "鋁的世界 基本特性 (一)：輕量化高強度鋁合金工業應用展示",
        "alu02.jpg": "鋁的世界 基本特性 (二)：優良耐蝕性與表面陽極處理鋁材",
        "alu03.jpg": "鋁的世界 基本特性 (三)：高導熱與高導電散熱鋁合金組件",
        "alu04.jpg": "鋁的世界 選用原則 (一)：精密化學成份與機械性能檢測",
        "alu05.jpg": "鋁的世界 選用原則 (二)：切削加工性與成型性評估樣件",
        "alu06.jpg": "鋁的世界 選用原則 (三)：國際標準認證鋁材品質檢驗",
        "alu07.jpg": "鋁的世界 鋁製品分類 (一)：軋延製品 (Sheet, Plate, Coil, Strip)",
        "alu08.jpg": "鋁的世界 鋁製品分類 (二)：擠型製品 (Tube, Rod, Bar, Profiles)",
        "alu09.jpg": "鋁的世界 鋁製品分類 (三)：鑄造與鍛造客製化鋁合金製品 (Tailor-made)"
    };

    // 1. 無障礙狀態管理
    const a11yState = {
        fontScale: parseFloat(localStorage.getItem("hv_font_scale") || "1"),
        highContrast: localStorage.getItem("hv_high_contrast") === "1",
        darkMode: localStorage.getItem("hv_dark_mode") === "1",
        readableSpacing: localStorage.getItem("hv_readable_spacing") === "1",
        reduceMotion: localStorage.getItem("hv_reduce_motion") === "1"
    };

    function applyA11yState() {
        document.documentElement.style.setProperty("--hv-font-scale", a11yState.fontScale);
        document.body.classList.toggle("hv-high-contrast", a11yState.highContrast);
        document.body.classList.toggle("hv-dark-mode", a11yState.darkMode && !a11yState.highContrast);
        document.body.classList.toggle("hv-readable-spacing", a11yState.readableSpacing);
        document.body.classList.toggle("hv-reduce-motion", a11yState.reduceMotion);

        const btnHC = document.getElementById("hv-btn-hc");
        if (btnHC) btnHC.setAttribute("aria-pressed", String(a11yState.highContrast));
        const btnDM = document.getElementById("hv-btn-dm");
        if (btnDM) btnDM.setAttribute("aria-pressed", String(a11yState.darkMode));
        const btnRS = document.getElementById("hv-btn-rs");
        if (btnRS) btnRS.setAttribute("aria-pressed", String(a11yState.readableSpacing));
    }

    // 2. 自動補齊所有圖片 alt、iframe title 與無障礙結構
    function enhanceSemanticsAndImages() {
        const lang = document.documentElement.lang || "zh-Hant";
        document.querySelectorAll("img").forEach((img) => {
            const src = img.getAttribute("src") || "";
            const fname = src.split("/").pop().split("?")[0];
            const currentAlt = (img.getAttribute("alt") || "").trim();
            if (!currentAlt && IMAGE_ALT_MAP[fname]) {
                img.setAttribute("alt", IMAGE_ALT_MAP[fname]);
            } else if (!currentAlt) {
                img.setAttribute("alt", "賀華實業股份有限公司鋁合金產品與廠房設備圖 - " + fname);
            }
            img.setAttribute("loading", "lazy");
        });

        // 替所有 Google Maps 與影片 iframe 補上無障礙 title (WCAG 4.1.2)
        document.querySelectorAll("iframe").forEach((ifr, idx) => {
            if (!ifr.getAttribute("title")) {
                const src = ifr.getAttribute("src") || "";
                if (src.includes("google.com/maps")) {
                    const card = ifr.closest(".address-info");
                    const heading = card ? card.querySelector("h6") : null;
                    const locName = heading ? heading.textContent.trim() : "賀華實業廠區位置圖 " + (idx + 1);
                    ifr.setAttribute("title", "Google 地圖：" + locName);
                } else {
                    ifr.setAttribute("title", "賀華實業多媒體介紹影片 " + (idx + 1));
                }
            }
        });

        // 強化表單欄位無障礙標籤 (WCAG 1.3.1 / 3.3.2)
        document.querySelectorAll("form input, form textarea, form select").forEach((inp) => {
            if (inp.type === "submit" || inp.type === "button" || inp.type === "hidden") return;
            if (!inp.getAttribute("aria-label") && !inp.id) {
                const ph = inp.getAttribute("placeholder") || inp.getAttribute("name") || "表單輸入欄位";
                inp.setAttribute("aria-label", ph);
            }
        });
    }

    // 3. 強化所有資料表格 (table.table01)：支援即時篩選、無障礙標記、CSV 下載
    function enhanceTables() {
        document.querySelectorAll("table.table01").forEach((tbl, idx) => {
            if (tbl.dataset.hvEnhanced === "1") return;
            tbl.dataset.hvEnhanced = "1";

            const section = tbl.closest("section");
            const secTitleEl = section ? section.querySelector("h3.tittle, h4.tittle") : null;
            const tableTitle = secTitleEl ? secTitleEl.textContent.trim() + " 規格表 #" + (idx + 1) : "鋁材規格資料表 #" + (idx + 1);

            if (!tbl.querySelector("caption")) {
                const cap = document.createElement("caption");
                cap.className = "sr-only";
                cap.textContent = tableTitle + "（可使用上方搜尋框即時篩選規格或匯出 CSV）";
                tbl.prepend(cap);
            }

            tbl.querySelectorAll("th").forEach((th) => {
                if (!th.getAttribute("scope")) {
                    th.setAttribute("scope", "col");
                }
            });

            // 建立工具列與響應式外框
            const toolbar = document.createElement("div");
            toolbar.className = "hv-table-toolbar";
            toolbar.innerHTML = `
                <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                    <strong style="color:#0f3d68;"><i class="fas fa-table" aria-hidden="true"></i> ${tableTitle}</strong>
                    <span class="hv-badge" style="background:#0f3d68;color:#fff;" id="hv-tbl-count-${idx}">共 ${tbl.querySelectorAll("tr").length} 列</span>
                </div>
                <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                    <label for="hv-tbl-filter-${idx}" class="sr-only">篩選 ${tableTitle}</label>
                    <input type="search" id="hv-tbl-filter-${idx}" placeholder="🔍 輸入合金編號、厚度或尺寸篩選..." aria-label="篩選 ${tableTitle}">
                    <button type="button" class="hv-btn-secondary" data-export-tbl="${idx}" style="padding:5px 12px;font-size:0.82rem;">
                        <i class="fas fa-download" aria-hidden="true"></i> 匯出 CSV (ISO 9001 文件)
                    </button>
                </div>
            `;

            const wrapper = document.createElement("div");
            wrapper.className = "hv-table-responsive";
            wrapper.setAttribute("role", "region");
            wrapper.setAttribute("aria-label", tableTitle);
            wrapper.setAttribute("tabindex", "0");

            tbl.parentNode.insertBefore(toolbar, tbl);
            tbl.parentNode.insertBefore(wrapper, tbl);
            wrapper.appendChild(tbl);

            const filterInput = toolbar.querySelector(`#hv-tbl-filter-${idx}`);
            const countBadge = toolbar.querySelector(`#hv-tbl-count-${idx}`);
            filterInput.addEventListener("input", function () {
                const q = this.value.trim().toLowerCase();
                const rows = Array.from(tbl.querySelectorAll("tr"));
                let visible = 0;
                rows.forEach((tr) => {
                    if (tr.querySelector("th")) {
                        tr.classList.remove("hv-row-hidden");
                        return;
                    }
                    const txt = tr.textContent.toLowerCase();
                    const match = !q || txt.includes(q);
                    tr.classList.toggle("hv-row-hidden", !match);
                    if (match) visible++;
                });
                countBadge.textContent = q ? `符合 ${visible} 列` : `共 ${rows.length} 列`;
            });

            const exportBtn = toolbar.querySelector(`[data-export-tbl="${idx}"]`);
            exportBtn.addEventListener("click", function () {
                const rows = Array.from(tbl.querySelectorAll("tr")).filter((r) => !r.classList.contains("hv-row-hidden"));
                const csvLines = rows.map((r) => {
                    return Array.from(r.querySelectorAll("th, td"))
                        .map((cell) => `"${cell.textContent.replace(/\s+/g, " ").trim().replace(/"/g, '""')}"`)
                        .join(",");
                });
                const blob = new Blob(["\uFEFF" + csvLines.join("\r\n")], { type: "text/csv;charset=utf-8;" });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `harvard_ent_spec_table_${idx + 1}.csv`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            });
        });
    }

    // 4. 語音朗讀功能 (Web Speech API)
    let isSpeaking = false;
    function toggleSpeech() {
        if (!("speechSynthesis" in window)) {
            alert("您的瀏覽器不支援 Web Speech 語音合成功能。");
            return;
        }
        const btn = document.getElementById("hv-btn-tts");
        if (isSpeaking) {
            window.speechSynthesis.cancel();
            isSpeaking = false;
            if (btn) btn.innerHTML = '<i class="fas fa-volume-up" aria-hidden="true"></i> 語音導覽';
            return;
        }
        const sel = window.getSelection().toString().trim();
        const mainEl = document.getElementById("main-content") || document.body;
        const textToRead = sel || (
            "歡迎光臨賀華實業股份有限公司智慧化無障礙網站。本公司創立於1973年4月25日，專營鋁合金特殊輕金屬材料、中鋼鋁業全系列鋁合金、零零鋁箔、鋁捲片、平片、600mm特厚鋁板、圓棒及擠型裁切加工，並導入 Google OR-Tools CP-SAT 數學規劃求解器，提供一維分條、二維鋁板排樣與全台五廠區智慧產能排程。"
        );
        const utter = new SpeechSynthesisUtterance(textToRead);
        utter.lang = document.documentElement.lang === "en" ? "en-US" : (document.documentElement.lang === "ja" ? "ja-JP" : "zh-TW");
        utter.onend = function () {
            isSpeaking = false;
            if (btn) btn.innerHTML = '<i class="fas fa-volume-up" aria-hidden="true"></i> 語音導覽';
        };
        isSpeaking = true;
        if (btn) btn.innerHTML = '<i class="fas fa-stop-circle" aria-hidden="true"></i> 停止朗讀';
        window.speechSynthesis.speak(utter);
    }

    // 5. 注入頂部無障礙工具列與導盲磚 (若頁面尚未包含)
    function injectAccessibilityTopbar() {
        if (document.getElementById("hv-iso-topbar")) return;

        const skipLink = document.createElement("a");
        skipLink.href = "#main-content";
        skipLink.className = "skip-link";
        skipLink.textContent = "跳至主要內容區 (Skip to Main Content)";
        document.body.prepend(skipLink);

        const topbar = document.createElement("div");
        topbar.id = "hv-iso-topbar";
        topbar.className = "hv-iso-topbar";
        topbar.setAttribute("role", "region");
        topbar.setAttribute("aria-label", "ISO 國際認證與無障礙輔助工具列");
        topbar.innerHTML = `
            <div class="topbar-inner">
                <div class="hv-iso-badges">
                    <a href="#top-nav" accesskey="U" class="accesskey-brick" title="上方功能導覽區 (Alt+U)">:::</a>
                    <span class="hv-badge badge-cpsat"><i class="fas fa-microchip" aria-hidden="true"></i> OR-Tools CP-SAT 智慧引擎已啟用</span>
                    <span class="hv-badge"><i class="fas fa-certificate" aria-hidden="true"></i> ISO 9001 品質追溯</span>
                    <span class="hv-badge"><i class="fas fa-leaf" aria-hidden="true"></i> ISO 14001 綠色減碳</span>
                    <span class="hv-badge badge-a11y"><i class="fas fa-universal-access" aria-hidden="true"></i> WCAG 2.1 AAA 無障礙</span>
                </div>
                <div class="hv-a11y-quickbar" role="group" aria-label="字級與視覺無障礙調整">
                    <button type="button" class="hv-a11y-btn" id="hv-btn-font-dec" title="縮小字級 (A-)" aria-label="縮小字級">A-</button>
                    <button type="button" class="hv-a11y-btn" id="hv-btn-font-reset" title="標準字級 (A)" aria-label="標準字級">A</button>
                    <button type="button" class="hv-a11y-btn" id="hv-btn-font-inc" title="放大字級 (A+)" aria-label="放大字級">A+</button>
                    <button type="button" class="hv-a11y-btn" id="hv-btn-hc" aria-pressed="false" title="切換高對比模式 (黑底黃字)">
                        <i class="fas fa-adjust" aria-hidden="true"></i> 高對比
                    </button>
                    <button type="button" class="hv-a11y-btn" id="hv-btn-dm" aria-pressed="false" title="切換護眼深色模式">
                        <i class="fas fa-moon" aria-hidden="true"></i> 深色
                    </button>
                    <button type="button" class="hv-a11y-btn" id="hv-btn-rs" aria-pressed="false" title="切換寬行距易讀模式">
                        <i class="fas fa-text-width" aria-hidden="true"></i> 易讀間距
                    </button>
                    <button type="button" class="hv-a11y-btn" id="hv-btn-tts" title="語音朗讀網頁資訊">
                        <i class="fas fa-volume-up" aria-hidden="true"></i> 語音導覽
                    </button>
                </div>
            </div>
        `;
        document.body.insertBefore(topbar, skipLink.nextSibling);

        // 確保主要內容區具有 #main-content 與導盲磚 Alt+C
        const firstSection = document.querySelector("section");
        if (firstSection && !document.getElementById("main-content")) {
            firstSection.id = "main-content";
            firstSection.setAttribute("tabindex", "-1");
            const brickC = document.createElement("a");
            brickC.href = "#main-content";
            brickC.accessKey = "C";
            brickC.className = "accesskey-brick";
            brickC.title = "中央主要內容區 (Alt+C)";
            brickC.textContent = ":::";
            const container = firstSection.querySelector(".container") || firstSection;
            container.prepend(brickC);
        }

        // 確保頁尾具有導盲磚 Alt+Z
        const footer = document.querySelector(".copyright");
        if (footer) {
            footer.setAttribute("role", "contentinfo");
            const brickZ = document.createElement("a");
            brickZ.href = "#footer-info";
            brickZ.id = "footer-info";
            brickZ.accessKey = "Z";
            brickZ.className = "accesskey-brick";
            brickZ.title = "下方頁尾聯絡資訊區 (Alt+Z)";
            brickZ.textContent = ":::";
            const fContainer = footer.querySelector(".copyrightbottom") || footer;
            fContainer.prepend(brickZ);
        }

        // 綁定工具列按鈕事件
        document.getElementById("hv-btn-font-dec").addEventListener("click", () => {
            a11yState.fontScale = Math.max(0.85, +(a11yState.fontScale - 0.1).toFixed(2));
            localStorage.setItem("hv_font_scale", a11yState.fontScale);
            applyA11yState();
        });
        document.getElementById("hv-btn-font-reset").addEventListener("click", () => {
            a11yState.fontScale = 1.0;
            localStorage.setItem("hv_font_scale", a11yState.fontScale);
            applyA11yState();
        });
        document.getElementById("hv-btn-font-inc").addEventListener("click", () => {
            a11yState.fontScale = Math.min(1.35, +(a11yState.fontScale + 0.1).toFixed(2));
            localStorage.setItem("hv_font_scale", a11yState.fontScale);
            applyA11yState();
        });
        document.getElementById("hv-btn-hc").addEventListener("click", () => {
            a11yState.highContrast = !a11yState.highContrast;
            localStorage.setItem("hv_high_contrast", a11yState.highContrast ? "1" : "0");
            applyA11yState();
        });
        document.getElementById("hv-btn-dm").addEventListener("click", () => {
            a11yState.darkMode = !a11yState.darkMode;
            if (a11yState.darkMode) a11yState.highContrast = false;
            localStorage.setItem("hv_dark_mode", a11yState.darkMode ? "1" : "0");
            localStorage.setItem("hv_high_contrast", "0");
            applyA11yState();
        });
        document.getElementById("hv-btn-rs").addEventListener("click", () => {
            a11yState.readableSpacing = !a11yState.readableSpacing;
            localStorage.setItem("hv_readable_spacing", a11yState.readableSpacing ? "1" : "0");
            applyA11yState();
        });
        document.getElementById("hv-btn-tts").addEventListener("click", toggleSpeech);
    }

    // 6. 建立並綁定 Google OR-Tools CP-SAT 智慧最佳化中心介面
    function initCpSatHub() {
        const hubContainer = document.getElementById("hv-cpsat-hub-mount");
        if (!hubContainer) return;

        // 切換頁籤邏輯
        const tabBtns = hubContainer.querySelectorAll(".hv-tab-btn");
        const tabPanels = hubContainer.querySelectorAll(".hv-tab-panel");
        tabBtns.forEach((btn) => {
            btn.addEventListener("click", function () {
                const targetId = this.getAttribute("aria-controls");
                tabBtns.forEach((b) => b.setAttribute("aria-selected", "false"));
                tabPanels.forEach((p) => p.classList.remove("active"));
                this.setAttribute("aria-selected", "true");
                const panel = document.getElementById(targetId);
                if (panel) panel.classList.add("active");
            });
        });

        // 綁定 1D 鋁捲分條 / 圓棒裁切 CP-SAT 求解
        const btnSolve1D = document.getElementById("btn-solve-1d");
        if (btnSolve1D) {
            btnSolve1D.addEventListener("click", runSolve1D);
        }
        const btnAdd1DRow = document.getElementById("btn-add-1d-row");
        if (btnAdd1DRow) {
            btnAdd1DRow.addEventListener("click", function () {
                const tbody = document.getElementById("cpsat-1d-demands-body");
                const idx = tbody.querySelectorAll("tr").length + 1;
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td><input type="text" class="form-control d1-label" value="客製分條規格 #${idx}" aria-label="規格名稱"></td>
                    <td><input type="number" class="form-control d1-width" value="150" min="10" max="6000" aria-label="寬度或長度(mm)"></td>
                    <td><input type="number" class="form-control d1-qty" value="2" min="1" max="50" aria-label="需求數量"></td>
                    <td><button type="button" class="hv-btn-secondary btn-rm-row" aria-label="刪除此列">✕</button></td>
                `;
                tbody.appendChild(tr);
                tr.querySelector(".btn-rm-row").addEventListener("click", () => tr.remove());
            });
        }
        hubContainer.querySelectorAll(".btn-rm-row").forEach((b) => {
            b.addEventListener("click", function () {
                const tr = this.closest("tr");
                if (tr && tr.parentNode.querySelectorAll("tr").length > 1) tr.remove();
            });
        });

        // 綁定 2D 鋁板裁切 CP-SAT 求解
        const btnSolve2D = document.getElementById("btn-solve-2d");
        if (btnSolve2D) {
            btnSolve2D.addEventListener("click", runSolve2D);
        }
        const btnAdd2DRow = document.getElementById("btn-add-2d-row");
        if (btnAdd2DRow) {
            btnAdd2DRow.addEventListener("click", function () {
                const tbody = document.getElementById("cpsat-2d-pieces-body");
                const idx = tbody.querySelectorAll("tr").length + 1;
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td><input type="text" class="form-control d2-label" value="精密裁切板件 P${idx}" aria-label="零件名稱"></td>
                    <td><input type="number" class="form-control d2-w" value="400" min="50" max="3000" aria-label="寬度(mm)"></td>
                    <td><input type="number" class="form-control d2-h" value="500" min="50" max="4000" aria-label="長度(mm)"></td>
                    <td><input type="number" class="form-control d2-qty" value="2" min="1" max="10" aria-label="數量"></td>
                    <td><button type="button" class="hv-btn-secondary btn-rm-row" aria-label="刪除此列">✕</button></td>
                `;
                tbody.appendChild(tr);
                tr.querySelector(".btn-rm-row").addEventListener("click", () => tr.remove());
            });
        }

        // 綁定多廠區排程 CP-SAT 求解
        const btnSolveSched = document.getElementById("btn-solve-schedule");
        if (btnSolveSched) {
            btnSolveSched.addEventListener("click", runSolveSchedule);
        }

        // 綁定智慧選材與重量計算
        const btnSolveAlloy = document.getElementById("btn-solve-alloy");
        if (btnSolveAlloy) {
            btnSolveAlloy.addEventListener("click", runSolveAlloy);
        }
        const btnCalcWeight = document.getElementById("btn-calc-weight");
        if (btnCalcWeight) {
            btnCalcWeight.addEventListener("click", calculateWeightAndTolerance);
        }

        // 頁面載入後自動執行預設最佳化展示
        runSolve1D();
        runSolve2D();
        runSolveSchedule();
        runSolveAlloy();
        calculateWeightAndTolerance();
    }

    const COLORS = ["#0f3d68", "#00897b", "#e65100", "#2563eb", "#7c3aed", "#059669", "#d97706", "#be123c"];

    async function runSolve1D() {
        const outEl = document.getElementById("cpsat-1d-result");
        if (!outEl) return;
        outEl.innerHTML = '<p><i class="fas fa-spinner fa-spin"></i> 正在呼叫 Python <code>ortools.sat.python.cp_model</code> CP-SAT 求解器計算最佳分條/裁切方案...</p>';

        const motherLen = parseInt(document.getElementById("c1d-mother").value || "1250", 10);
        const alloy = document.getElementById("c1d-alloy").value || "5052";
        const thickness = parseFloat(document.getElementById("c1d-thickness").value || "1.0");
        const kerf = parseInt(document.getElementById("c1d-kerf").value || "2", 10);
        const trim = parseInt(document.getElementById("c1d-trim").value || "10", 10);

        const demands = [];
        document.querySelectorAll("#cpsat-1d-demands-body tr").forEach((tr, i) => {
            const label = tr.querySelector(".d1-label")?.value || `規格#${i + 1}`;
            const width = parseInt(tr.querySelector(".d1-width")?.value || "200", 10);
            const qty = parseInt(tr.querySelector(".d1-qty")?.value || "1", 10);
            demands.push({ id: `ORD-${i + 1}`, label, width, qty });
        });

        try {
            const resp = await fetch("/api/cpsat/1d-cutting", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    mother_length: motherLen,
                    alloy_code: alloy,
                    thickness_mm: thickness,
                    kerf: kerf,
                    trim_allowance: trim,
                    demands: demands
                })
            });
            const data = await resp.json();
            render1DResult(outEl, data);
        } catch (err) {
            outEl.innerHTML = `<div class="alert alert-warning">請透過 Flask/Waitress 伺服器啟動以連線後端 Python OR-Tools CP-SAT API（錯誤：${err.message}）。</div>`;
        }
    }

    function render1DResult(container, data) {
        if (!data || (data.status !== "OPTIMAL" && data.status !== "FEASIBLE")) {
            container.innerHTML = `<div class="alert alert-danger"><strong>求解狀態：${data?.status || "ERROR"}</strong> - ${data?.message || "請調整輸入參數"}</div>`;
            return;
        }
        let barsHtml = "";
        (data.schedules || []).forEach((s) => {
            let segs = "";
            s.cuts.forEach((c, cIdx) => {
                const pct = ((c.subtotal_mm / s.mother_length_mm) * 100).toFixed(2);
                const bg = COLORS[cIdx % COLORS.length];
                segs += `<div class="hv-slit-seg" style="width:${pct}%;background:${bg};" title="${c.label}: ${c.width}mm × ${c.count}條 = ${c.subtotal_mm}mm">${c.width}×${c.count}</div>`;
            });
            const lossPct = (100 - s.utilization_pct).toFixed(2);
            if (lossPct > 0) {
                segs += `<div class="hv-slit-seg" style="width:${lossPct}%;background:#94a3b8;color:#0f172a;" title="修邊與餘料損耗: ${s.total_loss_mm}mm">餘料 ${s.total_loss_mm}mm</div>`;
            }
            const cutDesc = s.cuts.map((c) => `<span class="badge badge-info" style="background:#0f3d68;color:#fff;padding:4px 8px;margin-right:6px;">${c.label}: ${c.width}mm × ${c.count}條</span>`).join("");
            barsHtml += `
                <div class="hv-slit-bar-wrap">
                    <div style="display:flex;justify-content:space-between;flex-wrap:wrap;margin-bottom:6px;font-weight:700;">
                        <span>母材 #${s.mother_index}（總寬 ${s.mother_length_mm}mm │ 有效產出 ${s.used_mm}mm │ 刀具數 ${s.knives_used} 把）</span>
                        <span style="color:#00897b;">利用率：${s.utilization_pct}%（餘料/修邊：${s.total_loss_mm}mm）</span>
                    </div>
                    <div class="hv-slit-bar" role="img" aria-label="母材 ${s.mother_index} 裁切配置圖，利用率 ${s.utilization_pct}%">${segs}</div>
                    <div style="margin-top:8px;">${cutDesc}</div>
                </div>
            `;
        });

        container.innerHTML = `
            <div class="hv-kpi-grid">
                <div class="hv-kpi-card kpi-green">
                    <div class="hv-kpi-label">CP-SAT 求解狀態</div>
                    <div class="hv-kpi-value">${data.status} <small style="font-size:0.8rem;">(${data.solve_time_ms}ms)</small></div>
                </div>
                <div class="hv-kpi-card">
                    <div class="hv-kpi-label">最少母捲/母棒數</div>
                    <div class="hv-kpi-value">${data.total_mothers_used} 支</div>
                </div>
                <div class="hv-kpi-card kpi-green">
                    <div class="hv-kpi-label">整體材料利用率</div>
                    <div class="hv-kpi-value">${data.overall_utilization_pct}%</div>
                </div>
                <div class="hv-kpi-card kpi-orange">
                    <div class="hv-kpi-label">成品淨重 / 總重</div>
                    <div class="hv-kpi-value">${data.net_product_weight_kg} / ${data.total_weight_kg} kg</div>
                </div>
                <div class="hv-kpi-card kpi-green">
                    <div class="hv-kpi-label">ISO 14001 減碳效益</div>
                    <div class="hv-kpi-value">-${data.iso14001_carbon_saved_kg_co2e} <small style="font-size:0.75rem;">kg CO₂e</small></div>
                </div>
            </div>
            <p style="font-weight:600;color:#0f3d68;"><i class="fas fa-industry"></i> 建議派工廠區：${data.recommended_plant} │ 求解引擎：<code>${data.solver}</code></p>
            ${barsHtml}
        `;
    }

    async function runSolve2D() {
        const outEl = document.getElementById("cpsat-2d-result");
        if (!outEl) return;
        outEl.innerHTML = '<p><i class="fas fa-spinner fa-spin"></i> 正在呼叫 Python <code>cp_model.AddNoOverlap2D</code> 計算鋁板二維最佳裁切排樣...</p>';

        const plateSize = (document.getElementById("c2d-plate")?.value || "1220x2440").split("x");
        const pw = parseInt(plateSize[0], 10);
        const ph = parseInt(plateSize[1], 10);
        const alloy = document.getElementById("c2d-alloy")?.value || "6061";
        const thickness = parseFloat(document.getElementById("c2d-thickness")?.value || "15.0");
        const kerf = parseInt(document.getElementById("c2d-kerf")?.value || "3", 10);
        const allowRot = document.getElementById("c2d-rot")?.value === "1";

        const pieces = [];
        document.querySelectorAll("#cpsat-2d-pieces-body tr").forEach((tr, i) => {
            const label = tr.querySelector(".d2-label")?.value || `零件P${i + 1}`;
            const w = parseInt(tr.querySelector(".d2-w")?.value || "400", 10);
            const h = parseInt(tr.querySelector(".d2-h")?.value || "500", 10);
            const qty = parseInt(tr.querySelector(".d2-qty")?.value || "1", 10);
            pieces.push({ id: `P${i + 1}`, label, w, h, qty });
        });

        try {
            const resp = await fetch("/api/cpsat/2d-plate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    plate_width: pw,
                    plate_height: ph,
                    alloy_code: alloy,
                    thickness_mm: thickness,
                    kerf: kerf,
                    allow_rotation: allowRot,
                    pieces: pieces
                })
            });
            const data = await resp.json();
            render2DResult(outEl, data);
        } catch (err) {
            outEl.innerHTML = `<div class="alert alert-warning">連線失敗：${err.message}</div>`;
        }
    }

    function render2DResult(container, data) {
        if (!data || (data.status !== "OPTIMAL" && data.status !== "FEASIBLE")) {
            container.innerHTML = `<div class="alert alert-danger"><strong>求解狀態：${data?.status || "ERROR"}</strong> - ${data?.message || "無法排入母板"}</div>`;
            return;
        }
        let svgHtml = "";
        (data.plates || []).forEach((pl) => {
            let rects = "";
            pl.placements.forEach((p, idx) => {
                const color = COLORS[idx % COLORS.length];
                const cx = p.x + p.w / 2;
                const cy = p.y + p.h / 2;
                const rotMark = p.rotated ? " ↻" : "";
                rects += `
                    <g>
                        <rect x="${p.x}" y="${p.y}" width="${p.w}" height="${p.h}" fill="${color}" fill-opacity="0.86" stroke="#ffffff" stroke-width="6" rx="4">
                            <title>${p.uid} (${p.label}): ${p.w}×${p.h}mm @ X=${p.x}, Y=${p.y}${rotMark}</title>
                        </rect>
                        <text x="${cx}" y="${cy - 14}" fill="#ffffff" font-size="34" font-weight="bold" text-anchor="middle" dominant-baseline="central">${p.uid}${rotMark}</text>
                        <text x="${cx}" y="${cy + 28}" fill="#f8fafc" font-size="28" text-anchor="middle" dominant-baseline="central">${p.w}×${p.h}</text>
                    </g>
                `;
            });
            svgHtml += `
                <div style="flex:1;min-width:290px;background:#f8fafc;border:1px solid #cbd5e1;border-radius:12px;padding:16px;">
                    <div style="display:flex;justify-content:space-between;font-weight:700;margin-bottom:10px;">
                        <span>母板 #${pl.plate_index} (${pl.plate_width}×${pl.plate_height}mm)</span>
                        <span style="color:#00897b;">板材利用率：${pl.utilization_pct}%（共 ${pl.pieces_count} 件）</span>
                    </div>
                    <svg viewBox="0 0 ${pl.plate_width} ${pl.plate_height}" style="width:100%;max-height:420px;background:#e2e8f0;border:3px solid #0f3d68;border-radius:6px;" role="img" aria-label="鋁板二維裁切排樣圖 母板 ${pl.plate_index}">
                        <defs>
                            <pattern id="grid-${pl.plate_index}" width="100" height="100" patternUnits="userSpaceOnUse">
                                <path d="M 100 0 L 0 0 0 100" fill="none" stroke="#cbd5e1" stroke-width="2"/>
                            </pattern>
                        </defs>
                        <rect width="${pl.plate_width}" height="${pl.plate_height}" fill="url(#grid-${pl.plate_index})" />
                        ${rects}
                    </svg>
                </div>
            `;
        });

        container.innerHTML = `
            <div class="hv-kpi-grid">
                <div class="hv-kpi-card kpi-green">
                    <div class="hv-kpi-label">CP-SAT 2D 狀態</div>
                    <div class="hv-kpi-value">${data.status} <small style="font-size:0.8rem;">(${data.solve_time_ms}ms)</small></div>
                </div>
                <div class="hv-kpi-card">
                    <div class="hv-kpi-label">使用母板張數 / 總件數</div>
                    <div class="hv-kpi-value">${data.total_plates_used} 張 / ${data.total_pieces_placed} 件</div>
                </div>
                <div class="hv-kpi-card kpi-green">
                    <div class="hv-kpi-label">板材面積利用率</div>
                    <div class="hv-kpi-value">${data.overall_utilization_pct}%</div>
                </div>
                <div class="hv-kpi-card kpi-orange">
                    <div class="hv-kpi-label">裁切成品淨重 / 母板總重</div>
                    <div class="hv-kpi-value">${data.net_parts_weight_kg} / ${data.total_plate_weight_kg} kg</div>
                </div>
            </div>
            <p style="font-weight:600;color:#0f3d68;"><i class="fas fa-cogs"></i> 建議裁切機台：${data.recommended_equipment} │ 求解約束：<code>cp_model.AddNoOverlap2D</code></p>
            <div style="display:flex;flex-wrap:wrap;gap:18px;margin-top:14px;">${svgHtml}</div>
        `;
    }

    async function runSolveSchedule() {
        const outEl = document.getElementById("cpsat-schedule-result");
        if (!outEl) return;
        outEl.innerHTML = '<p><i class="fas fa-spinner fa-spin"></i> 正在呼叫 Python CP-SAT 排程全台五廠區最佳派工甘特圖...</p>';
        try {
            const resp = await fetch("/api/cpsat/schedule", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({})
            });
            const data = await resp.json();
            renderScheduleResult(outEl, data);
        } catch (err) {
            outEl.innerHTML = `<div class="alert alert-warning">排程連線失敗：${err.message}</div>`;
        }
    }

    function renderScheduleResult(container, data) {
        if (!data || !data.assignments) return;
        const maxHr = Math.max(data.makespan_hr || 12, 10);
        let rowsHtml = "";
        (data.plants || []).forEach((p) => {
            const jobs = data.assignments.filter((a) => a.assigned_plant_id === p.id);
            let bars = "";
            jobs.forEach((j, idx) => {
                const leftPct = ((j.start_hr / maxHr) * 100).toFixed(2);
                const widthPct = ((j.duration_hr / maxHr) * 100).toFixed(2);
                const bg = COLORS[idx % COLORS.length];
                bars += `
                    <div style="position:absolute;left:${leftPct}%;width:${widthPct}%;top:4px;bottom:4px;background:${bg};color:#fff;border-radius:6px;padding:2px 6px;font-size:0.76rem;font-weight:700;overflow:hidden;white-space:nowrap;display:flex;align-items:center;" title="${j.job_id} ${j.customer} - ${j.product} (${j.start_hr}h ~ ${j.end_hr}h)">
                        ${j.job_id}: ${j.product} (${j.duration_hr}h)
                    </div>
                `;
            });
            rowsHtml += `
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
                    <div style="width:230px;font-weight:700;font-size:0.88rem;color:#0f3d68;">
                        ${p.name}<br><small style="color:#475569;font-weight:500;">${p.specialty}</small>
                    </div>
                    <div style="flex:1;position:relative;height:42px;background:#e2e8f0;border-radius:8px;border:1px solid #94a3b8;">
                        ${bars}
                    </div>
                </div>
            `;
        });

        container.innerHTML = `
            <div class="hv-kpi-grid">
                <div class="hv-kpi-card kpi-green">
                    <div class="hv-kpi-label">CP-SAT 排程狀態</div>
                    <div class="hv-kpi-value">${data.status} <small style="font-size:0.8rem;">(${data.solve_time_ms}ms)</small></div>
                </div>
                <div class="hv-kpi-card">
                    <div class="hv-kpi-label">總完工時間 (Makespan)</div>
                    <div class="hv-kpi-value">${data.makespan_hr} 小時</div>
                </div>
                <div class="hv-kpi-card kpi-green">
                    <div class="hv-kpi-label">調度廠區數 / 總工單數</div>
                    <div class="hv-kpi-value">5 廠區 / ${data.total_jobs} 筆工單</div>
                </div>
            </div>
            <div style="background:#f8fafc;border:1px solid #cbd5e1;border-radius:12px;padding:18px;margin-top:12px;">
                <h4 style="font-size:1.05rem;font-weight:700;margin-bottom:14px;color:#0f3d68;"><i class="fas fa-tasks"></i> 賀華實業全台五廠區 CP-SAT 智慧產能排程甘特圖 (0 ~ ${maxHr} 小時)</h4>
                ${rowsHtml}
            </div>
        `;
    }

    async function runSolveAlloy() {
        const outEl = document.getElementById("cpsat-alloy-result");
        if (!outEl) return;
        const corr = parseInt(document.getElementById("al-corr")?.value || "80", 10);
        const str = parseInt(document.getElementById("al-str")?.value || "70", 10);
        const form = parseInt(document.getElementById("al-form")?.value || "65", 10);
        const mach = parseInt(document.getElementById("al-mach")?.value || "70", 10);
        const weld = parseInt(document.getElementById("al-weld")?.value || "60", 10);
        const reqForm = document.getElementById("al-req-form")?.value || "all";

        try {
            const resp = await fetch("/api/cpsat/alloy-select", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    min_corrosion: corr,
                    min_strength: str,
                    min_formability: form,
                    min_machinability: mach,
                    min_weldability: weld,
                    required_form: reqForm
                })
            });
            const data = await resp.json();
            if (!data || !data.top_recommendations) return;
            const cards = data.top_recommendations.map((a, idx) => `
                <div class="hv-iso-card" style="border-top-color:${idx === 0 ? '#e65100' : '#0f3d68'};">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <h4 style="margin:0;">${idx === 0 ? '🏆 首選推薦：' : ''}${a.code} 鋁合金</h4>
                        <span class="hv-badge badge-cpsat">適配度 ${a.match_score}%</span>
                    </div>
                    <p style="font-size:0.86rem;color:#475569;margin:6px 0;"><strong>${a.series}</strong> │ 比重：${a.density_g_cm3} g/cm³ │ 供應形狀：${a.forms.join("、")}</p>
                    <p style="font-size:0.9rem;color:#1e293b;margin-bottom:6px;"><strong>特性：</strong>${a.characteristics}</p>
                    <p style="font-size:0.88rem;color:#334155;margin:0;"><strong>典型用途：</strong>${a.applications}</p>
                </div>
            `).join("");
            outEl.innerHTML = `<div class="hv-iso-grid" style="margin-top:14px;">${cards}</div>`;
        } catch (err) {
            outEl.innerHTML = `<div class="alert alert-warning">選材計算連線錯誤：${err.message}</div>`;
        }
    }

    function calculateWeightAndTolerance() {
        const outEl = document.getElementById("hv-weight-calc-out");
        if (!outEl) return;
        const shape = document.getElementById("wc-shape")?.value || "plate";
        const density = parseFloat(document.getElementById("wc-alloy")?.value || "2.70");
        const d1 = parseFloat(document.getElementById("wc-d1")?.value || "15");   // 厚度 或 外徑
        const d2 = parseFloat(document.getElementById("wc-d2")?.value || "1220"); // 寬度 或 內徑
        const d3 = parseFloat(document.getElementById("wc-d3")?.value || "2440"); // 長度
        const qty = parseInt(document.getElementById("wc-qty")?.value || "1", 10);

        let volCm3 = 0;
        if (shape === "plate") {
            volCm3 = (d1 / 10) * (d2 / 10) * (d3 / 10);
        } else if (shape === "rod") {
            const rCm = (d1 / 2) / 10;
            volCm3 = Math.PI * rCm * rCm * (d3 / 10);
        } else if (shape === "tube") {
            const rOut = (d1 / 2) / 10;
            const rIn = Math.min(rOut, (d2 / 2) / 10);
            volCm3 = Math.PI * (rOut * rOut - rIn * rIn) * (d3 / 10);
        }
        const singleKg = (volCm3 * density) / 1000;
        const totalKg = singleKg * qty;
        // CNS / JIS / ASTM 標準厚度與裁切公差參考
        const thickTol = d1 <= 1.0 ? "±0.04mm" : (d1 <= 6.0 ? "±0.12mm" : (d1 <= 50 ? "±0.50mm" : "±1.20mm"));
        outEl.innerHTML = `
            <div style="background:#f0fdf4;border:2px solid #00897b;border-radius:10px;padding:14px;margin-top:12px;">
                <strong><i class="fas fa-balance-scale"></i> 計算結果（依據 ISO / JIS / CNS 鋁合金比重規範）：</strong><br>
                單件理論重量：<strong style="font-size:1.25rem;color:#0f3d68;">${singleKg.toFixed(3)} kg</strong> │
                總重量 (${qty} 件)：<strong style="font-size:1.35rem;color:#e65100;">${totalKg.toFixed(2)} kg</strong> │
                標準厚度公差參考：<strong>${thickTol}</strong>（紅外線/立式裁切長度公差：+1.5/-0mm）
            </div>
        `;
    }

    document.addEventListener("DOMContentLoaded", function () {
        injectAccessibilityTopbar();
        applyA11yState();
        enhanceSemanticsAndImages();
        enhanceTables();
        initCpSatHub();
    });
})();

