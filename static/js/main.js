/**
 * 賀華實業股份有限公司 - 沉浸式互動核心引擎
 * HARVARD ENTERPRISE Interactive Experience & Edge-TTS Audio Engine
 */

document.addEventListener('DOMContentLoaded', () => {
    // Force view to top on fresh launch or reload to guarantee hero section appears upfront
    if (!window.location.hash) {
        window.scrollTo(0, 0);
        setTimeout(() => window.scrollTo(0, 0), 60);
        setTimeout(() => window.scrollTo(0, 0), 240);
    }
    initLatticeCanvas();
    initPageRouter();
    initAudioTour();
    initSpecsExplorer();
    initHardnessCalculator();
    initContactForm();
    initProductFilters();
    initAboutTabs();
    initTechTabs();
    initMobileUI();
    initDynamicInteractions();
});

function initAboutTabs() {
    const tabBar = document.getElementById('aboutTabBar');
    if (!tabBar) return;
    const buttons = tabBar.querySelectorAll('[data-about-tab]');
    const panels = document.querySelectorAll('[data-about-panel]');

    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.dataset.aboutTab;
            buttons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            panels.forEach(p => {
                const match = target === 'all' || p.dataset.aboutPanel === target;
                p.style.display = match ? '' : 'none';
            });
        });
    });
}

function initTechTabs() {
    const tabBar = document.getElementById('techTabBar');
    if (!tabBar) return;
    const buttons = tabBar.querySelectorAll('[data-tech-tab]');
    const panels = document.querySelectorAll('[data-tech-panel]');

    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.dataset.techTab;
            buttons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            panels.forEach(p => {
                const match = target === 'all' || p.dataset.techPanel === target;
                p.style.display = match ? '' : 'none';
            });
        });
    });
}

window.filterChemTable = function(val) {
    const query = (val || '').toLowerCase().trim();
    const rows = document.querySelectorAll('#chemTableBody tr');
    rows.forEach(r => {
        const text = r.textContent.toLowerCase();
        r.style.display = text.includes(query) ? '' : 'none';
    });
};

window.closeMobileMenu = function() {
    const overlay = document.getElementById('mobileNavOverlay');
    const menuBtn = document.getElementById('mobileMenuBtn');
    if (overlay) overlay.classList.remove('open');
    if (menuBtn) {
        menuBtn.textContent = '☰';
        menuBtn.setAttribute('aria-expanded', 'false');
    }
};

function initMobileUI() {
    const menuBtn = document.getElementById('mobileMenuBtn');
    const overlay = document.getElementById('mobileNavOverlay');
    if (menuBtn && overlay) {
        menuBtn.addEventListener('click', () => {
            const isOpen = overlay.classList.toggle('open');
            menuBtn.textContent = isOpen ? '✕' : '☰';
            menuBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        });
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) window.closeMobileMenu();
        });
        overlay.querySelectorAll('.mobile-nav-link').forEach(link => {
            link.addEventListener('click', () => window.closeMobileMenu());
        });
    }

    // Mobile Audio Dock Expandable Controls Toggle
    const dock = document.getElementById('audioDock');
    const moreBtn = document.getElementById('dockMoreBtn');
    if (dock && moreBtn) {
        moreBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isExp = dock.classList.toggle('expanded');
            moreBtn.textContent = isExp ? '收合 ▾' : '音訊 ▴';
        });
        document.addEventListener('click', (e) => {
            if (dock.classList.contains('expanded') && !dock.contains(e.target)) {
                dock.classList.remove('expanded');
                moreBtn.textContent = '音訊 ▴';
            }
        });
    }
}

/* ==========================================================================
   1. Ink-Wash Mountain Mist & Golden Bodhi Light Canvas
      (水墨宣紙遠山雲霧 · 蓮華背光暗紋 · 飄落金色菩提微光特效)
   ========================================================================== */
function initLatticeCanvas() {
    const canvas = document.getElementById('latticeCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let width = window.innerWidth;
    let height = window.innerHeight;

    function resizeCanvas() {
        width = window.innerWidth;
        height = window.innerHeight;
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    const mouse = { x: width * 0.5, y: height * 0.38, radius: 180 };
    const pulses = [];
    let lastPulseTime = 0;

    function addCyberPulse(x, y) {
        const now = performance.now();
        if (now - lastPulseTime > 220) {
            lastPulseTime = now;
            pulses.push({ x, y, r: 6, alpha: 0.55 });
            if (pulses.length > 8) pulses.shift();
        }
    }

    window.addEventListener('mousemove', (e) => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
        addCyberPulse(e.clientX, e.clientY);
    });

    window.addEventListener('touchstart', (e) => {
        if (e.touches && e.touches[0]) {
            addCyberPulse(e.touches[0].clientX, e.touches[0].clientY);
        }
    }, { passive: true });

    // Quantum Alloy Lattice Nodes
    const nodeCount = Math.min(68, Math.max(36, Math.floor((width * height) / 21000)));
    const nodes = Array.from({ length: nodeCount }, (_, i) => ({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.48,
        vy: (Math.random() - 0.5) * 0.48,
        r: Math.random() * 2.2 + 1.2,
        phase: Math.random() * Math.PI * 2,
        color: i % 4 === 0 ? '#fbbf24' : (i % 2 === 0 ? '#00e5ff' : '#38bdf8')
    }));

    let hudAngle = 0;
    let gridOffset = 0;

    function drawCyberHorizonGrid() {
        const horizonY = height * 0.72;
        const bottomY = height;
        ctx.save();

        // Subtle horizon glow
        const hGrad = ctx.createLinearGradient(0, horizonY - 40, 0, bottomY);
        hGrad.addColorStop(0, 'rgba(0, 229, 255, 0)');
        hGrad.addColorStop(0.15, 'rgba(0, 229, 255, 0.08)');
        hGrad.addColorStop(1, 'rgba(2, 132, 199, 0.14)');
        ctx.fillStyle = hGrad;
        ctx.fillRect(0, horizonY - 40, width, bottomY - horizonY + 40);

        // Perspective radial lines from vanishing point
        const vpX = width * 0.5 + (mouse.x - width * 0.5) * 0.08;
        ctx.strokeStyle = 'rgba(0, 229, 255, 0.14)';
        ctx.lineWidth = 1;
        const numCols = 18;
        for (let i = -numCols; i <= numCols; i++) {
            const xBottom = vpX + i * (width / 8);
            ctx.beginPath();
            ctx.moveTo(vpX + i * 18, horizonY);
            ctx.lineTo(xBottom, bottomY);
            ctx.stroke();
        }

        // Moving horizontal perspective scanlines
        gridOffset = (gridOffset + 0.012) % 1;
        for (let j = 0; j < 10; j++) {
            const t = (j + gridOffset) / 10;
            const y = horizonY + Math.pow(t, 1.85) * (bottomY - horizonY);
            const alpha = Math.min(0.28, t * 0.32);
            ctx.strokeStyle = `rgba(0, 229, 255, ${alpha.toFixed(3)})`;
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(width, y);
            ctx.stroke();
        }
        ctx.restore();
    }

    function drawQuantumHudCore(cx, cy, maxR) {
        ctx.save();
        ctx.translate(cx, cy);

        // Outer rotating telemetry ring
        ctx.save();
        ctx.rotate(hudAngle);
        ctx.strokeStyle = 'rgba(0, 229, 255, 0.16)';
        ctx.lineWidth = 1.5;
        ctx.setLineDash([12, 8, 4, 8]);
        ctx.beginPath();
        ctx.arc(0, 0, maxR * 0.92, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();

        // Counter-rotating precision scale ring
        ctx.save();
        ctx.rotate(-hudAngle * 1.4);
        ctx.strokeStyle = 'rgba(56, 189, 248, 0.14)';
        ctx.lineWidth = 1.2;
        ctx.setLineDash([4, 10]);
        ctx.beginPath();
        ctx.arc(0, 0, maxR * 0.68, 0, Math.PI * 2);
        ctx.stroke();

        // Hexagonal FCC Aluminum Crystal Lattice Core
        ctx.setLineDash([]);
        ctx.strokeStyle = 'rgba(0, 229, 255, 0.13)';
        ctx.lineWidth = 1.3;
        const hexR = maxR * 0.42;
        ctx.beginPath();
        for (let k = 0; k < 6; k++) {
            const ang = (Math.PI / 3) * k;
            const hx = Math.cos(ang) * hexR;
            const hy = Math.sin(ang) * hexR;
            if (k === 0) ctx.moveTo(hx, hy);
            else ctx.lineTo(hx, hy);
        }
        ctx.closePath();
        ctx.stroke();

        // Spokes connecting hexagon vertices
        for (let k = 0; k < 6; k++) {
            const ang = (Math.PI / 3) * k;
            ctx.beginPath();
            ctx.moveTo(0, 0);
            ctx.lineTo(Math.cos(ang) * hexR, Math.sin(ang) * hexR);
            ctx.stroke();
        }
        ctx.restore();
        ctx.restore();
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);
        hudAngle += 0.0015;

        // 1. Quantum HUD Telemetry Core
        const hudY = Math.min(height * 0.44, 460);
        const hudR = Math.min(width * 0.38, Math.min(height * 0.44, 460));
        drawQuantumHudCore(width * 0.5, hudY, hudR);

        // 2. 3D Perspective Cyber Horizon Grid
        drawCyberHorizonGrid();

        // 3. Interactive Cyber Sonar Pulses
        for (let i = pulses.length - 1; i >= 0; i--) {
            const p = pulses[i];
            p.r += 1.8;
            p.alpha *= 0.96;
            if (p.alpha < 0.015) {
                pulses.splice(i, 1);
                continue;
            }
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.strokeStyle = `rgba(0, 229, 255, ${p.alpha.toFixed(3)})`;
            ctx.lineWidth = 1.4;
            ctx.stroke();
        }

        // 4. Neural Constellation Nodes & Laser Connections
        for (let i = 0; i < nodes.length; i++) {
            const n = nodes[i];
            n.phase += 0.03;
            n.x += n.vx;
            n.y += n.vy;

            if (n.x < 0 || n.x > width) n.vx *= -1;
            if (n.y < 0 || n.y > height) n.vy *= -1;

            // Gentle magnetic interaction with cursor
            const dxm = mouse.x - n.x;
            const dym = mouse.y - n.y;
            const distM = Math.sqrt(dxm * dxm + dym * dym);
            if (distM < mouse.radius && distM > 1) {
                ctx.beginPath();
                ctx.moveTo(n.x, n.y);
                ctx.lineTo(mouse.x, mouse.y);
                const mAlpha = (1 - distM / mouse.radius) * 0.28;
                ctx.strokeStyle = `rgba(0, 229, 255, ${mAlpha.toFixed(3)})`;
                ctx.lineWidth = 1;
                ctx.stroke();
            }

            // Connect nearby nodes
            for (let j = i + 1; j < nodes.length; j++) {
                const n2 = nodes[j];
                const dx = n.x - n2.x;
                const dy = n.y - n2.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 135) {
                    const lAlpha = (1 - dist / 135) * 0.20;
                    ctx.beginPath();
                    ctx.moveTo(n.x, n.y);
                    ctx.lineTo(n2.x, n2.y);
                    ctx.strokeStyle = `rgba(56, 189, 248, ${lAlpha.toFixed(3)})`;
                    ctx.lineWidth = 0.9;
                    ctx.stroke();
                }
            }

            // Draw glowing node
            const glowAlpha = 0.55 + Math.sin(n.phase) * 0.3;
            ctx.beginPath();
            ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
            ctx.fillStyle = n.color;
            ctx.globalAlpha = glowAlpha;
            ctx.fill();
            ctx.globalAlpha = 1.0;
        }

        requestAnimationFrame(animate);
    }
    animate();
}

/* ==========================================================================
   2. Studio Acoustic BGM & Edge-TTS Audio Tour Engine
      (真人錄音室實錄背景輕音樂：貝森朵夫平台鋼琴 / 古典木吉他 / 傳統古琴 + 智慧語音避讓)
   ========================================================================== */
const BGM_TRACKS = {
    piano: {
        url: '/static/audio/bgm_piano.mp3',
        label: '🎹 典雅鋼琴 · 巴哈 C 大調前奏曲'
    },
    guitar: {
        url: '/static/audio/bgm_guitar.mp3',
        label: '🎸 溫潤木吉他 · 薩提《吉姆諾佩蒂》'
    },
    guqin: {
        url: '/static/audio/bgm_guqin.mp3',
        label: '🍵 東方古琴 · 《陽關三疊》'
    }
};

const StudioBgmEngine = {
    audio: null,
    fadeTimer: null,
    outroTimer: null,
    currentTrack: 'piano',
    bgmEnabled: true,
    standaloneMode: false,
    isAmbientPlaying: false,
    isInFinaleOutro: false,
    bowlVisualEnergy: 0,

    _clearTimers() {
        this.isInFinaleOutro = false;
        if (this.fadeTimer) {
            clearInterval(this.fadeTimer);
            this.fadeTimer = null;
        }
        if (this.outroTimer) {
            clearTimeout(this.outroTimer);
            this.outroTimer = null;
        }
    },

    ensureAudio() {
        if (!this.audio) {
            this.audio = new Audio();
            this.audio.loop = true;
            this.audio.preload = 'none';
            this.audio.volume = 0;
            this.audio.src = BGM_TRACKS[this.currentTrack].url;
        }
        return this.audio;
    },

    _fadeTo(targetVol, durationMs = 550, onDone = null) {
        const a = this.ensureAudio();
        if (this.fadeTimer) {
            clearInterval(this.fadeTimer);
            this.fadeTimer = null;
        }
        const startVol = a.volume;
        const steps = 16;
        const stepMs = Math.max(20, Math.floor(durationMs / steps));
        let count = 0;

        this.fadeTimer = setInterval(() => {
            count++;
            const ratio = Math.min(1, count / steps);
            a.volume = Math.max(0, Math.min(1, startVol + (targetVol - startVol) * ratio));
            if (count >= steps) {
                clearInterval(this.fadeTimer);
                this.fadeTimer = null;
                if (onDone) onDone();
            }
        }, stepMs);
    },

    startAmbient(isSpeaking = false) {
        if (!this.bgmEnabled || this.currentTrack === 'off' || !BGM_TRACKS[this.currentTrack]) return;
        this._clearTimers();
        const a = this.ensureAudio();
        const expectedUrl = BGM_TRACKS[this.currentTrack].url;
        if (!a.src || !a.src.endsWith(expectedUrl)) {
            a.src = expectedUrl;
        }
        const targetVol = isSpeaking ? 0.16 : 0.38;
        if (a.paused) {
            a.volume = 0.01;
            a.play().then(() => {
                this.isAmbientPlaying = true;
                this._fadeTo(targetVol, 700);
            }).catch(() => {});
        } else {
            this.isAmbientPlaying = true;
            this._fadeTo(targetVol, 500);
        }
    },

    setDucking(isSpeaking) {
        if (!this.audio || !this.isAmbientPlaying) return;
        if (isSpeaking) {
            this.isInFinaleOutro = false;
            this._fadeTo(0.16, 450);
        } else if (this.isInFinaleOutro) {
            return;
        } else if (this.standaloneMode && this.bgmEnabled && this.currentTrack !== 'off') {
            this._fadeTo(0.38, 600);
        } else {
            this.stopAmbient();
        }
    },

    playFinaleOutro() {
        if (!this.audio || !this.isAmbientPlaying || this.standaloneMode) return;
        this._clearTimers();
        this.isInFinaleOutro = true;
        // Gently swell music for a warm 2.6s closing cadence, then smoothly fade out to silence
        this._fadeTo(0.28, 700, () => {
            this.outroTimer = setTimeout(() => {
                this.isAmbientPlaying = false;
                this.isInFinaleOutro = false;
                this._fadeTo(0.0, 2200, () => {
                    if (!this.isAmbientPlaying && this.audio) {
                        this.audio.pause();
                    }
                });
            }, 2600);
        });
    },

    setTrack(trackKey, isVoiceActive = false) {
        if (trackKey === 'off') {
            this.currentTrack = 'off';
            this.bgmEnabled = false;
            this.standaloneMode = false;
            this.stopAmbient();
            return;
        }
        if (!BGM_TRACKS[trackKey]) return;
        this.currentTrack = trackKey;
        this.bgmEnabled = true;
        const a = this.ensureAudio();
        const wasPlaying = this.isAmbientPlaying && !a.paused;
        a.pause();
        a.src = BGM_TRACKS[trackKey].url;
        a.currentTime = 0;
        if (wasPlaying || isVoiceActive || this.standaloneMode) {
            this.startAmbient(isVoiceActive);
        }
    },

    stopAmbient() {
        this.isAmbientPlaying = false;
        if (!this.audio || this.audio.paused) return;
        this._fadeTo(0.0, 420, () => {
            if (!this.isAmbientPlaying && this.audio) {
                this.audio.pause();
            }
        });
    }
};

let audioTourState = {
    audio: new Audio(),
    cardAudio: null,
    isCardPlaying: false,
    lastCardText: '',
    lastCardBtn: null,
    chimeAdvanceTimer: null,
    isPlaying: false,
    currentChapter: 0,
    chapters: [],
    voice: 'zen-male',
    speed: 1.0,
    analyser: null,
    audioCtx: null
};

const TOUR_CHAPTERS_I18N = {
    'zh-TW': [
        { title: "賀華實業 · 企業簡介", script: "歡迎蒞臨賀華實業股份有限公司。賀華實業創立於 1973 年，深耕台灣近四十載。我們致力於建構全方位、彈性且強大的鋁合金材料供應鏈與精密加工一站式平台，秉持以鋁為本、服務為先的理念，是全台高科技產業最堅實的後盾。" },
        { title: "關於我們 · 沿革與願景", script: "賀華實業自 1973 年創立以來，由早期進出口貿易穩健轉型為具備龐大現貨庫存與精密裁切加工能力的綜合材料供應商。我們秉持誠信立基、整合共榮的經營理念，橫跨鋁材、不鏽鋼、鎂合金、銅材與精密加工九大營業範疇，服務涵蓋半導體、航太、醫療與機電等十一大產業，矢志讓台灣精密製造實力在世界舞台發光。" },
        { title: "北中南服務網絡佈局", script: "為了滿足全台客戶即時調料與加工需求，賀華實業建立了綿密的北中南服務網。包括台北松山總公司、鄰近沙鹿交流道的台中物流裁切中心、以及台南佳里一廠與麻豆二廠雙廠區編制，龐大現貨與專屬車隊，提供最快速的材料調撥與配送。" },
        { title: "精選旗艦鋁材介紹", script: "在材料供應方面，我們主力引進日本原裝 UACJ 5052 貼膜鋁板，其獨特壓延工藝有效降低內部殘留應力，切削後絕不翹曲；同時常備 7075 航太級超硬鋁合金、6061 結構鋁板、5083 耐蝕船用板，以及兩千、五千、六千與七千系列鋁擠型型材，現貨規格全台最齊全。" },
        { title: "現貨與模具規格檢索", script: "在現貨與模具規格方面，賀華實業為您建置了超過三千零七十項的即時檢索資料庫，完整涵蓋五百一十四項常備鋁板、圓棒與扁條現貨，以及兩千五百五十七種免開模費的鋁擠型標準斷面模具。您只需輸入材質、尺寸或模具編號，即可即時查詢並一鍵帶入詢價單。" },
        { title: "高階加工與製程實力", script: "賀華實業不僅供應材料，更具備強大的精密加工能量。廠內整合 CNC 高速銑床、精密車床、航太級五軸同動加工、大型龍門銑床、沖剪折床以及表面陽極與拋光拉絲工藝，能從 3D 繪圖開模到微米級精密加工，為您一貫化高效完成。" },
        { title: "半導體與航太實績", script: "我們深度參與半導體設備真空腔體底座、蝕刻機台部件以及航太高強度結構件的開發與製造，以優異的真平度控制與原廠材質證明，徹底解決客戶應力變形與輕量化挑戰，深獲國際級設備大廠的肯定與長期指名。" },
        { title: "國際硬度換算與技術辭典", script: "為了協助研發與採購工程師快速比對材料規範，我們特別整理了國際標準金屬硬度即時試算器，支援布氏、洛氏、維氏與肖氏硬度對照，並提供鋁合金熱處理與調質代號辭典，成為您日常選材的得力助手。" },
        { title: "即時諮詢與圓滿結語", script: "感謝您撥冗聆聽賀華實業企業導覽。無論您需要特殊規格調料、現貨精密裁切，或是圖面加工估價，歡迎直接填寫本頁線上估價單，或致電台北總公司、台中廠與台南雙廠區，我們的專業工程團隊將於二十四小時內竭誠為您服務。賀華實業，以鋁為本、服務為先，誠摯期盼與您攜手共創卓越價值，敬祝您事業順心、鴻圖大展，謝謝您！" }
    ],
    'en': [
        { title: "HARVARD Enterprises · Corporate Overview", script: "Welcome to HARVARD Enterprises Co., Ltd. Founded in 1973 and rooted in Taiwan for nearly four decades, we are dedicated to building a comprehensive, resilient aluminum alloy supply chain and high-precision CNC machining platform. Embracing our core philosophy of alloy excellence and customer service, HARVARD is a trusted partner for aerospace, semiconductor, and advanced precision manufacturing." },
        { title: "About Us · History & Vision", script: "Since its establishment in 1973, HARVARD Enterprises has steadily evolved from international metals trading into an integrated materials supplier boasting extensive stock inventory and precision CNC machining capabilities. Guided by integrity and mutual growth, we cover nine core service domains across aluminum, stainless steel, and copper alloys, serving eleven major industrial sectors worldwide." },
        { title: "Nationwide Logistics & Branches", script: "To promptly meet customer demands across Taiwan, HARVARD has built an expansive logistics network. This includes our Taipei Songshan Headquarters, the Taichung Logistics and Precision Cutting Center near Shalu Interchange, and our dual plants in Tainan (Jiali and Madou). With extensive stock and dedicated fleet delivery, we ensure the fastest material dispatch." },
        { title: "Flagship Aluminum & Specialty Alloys", script: "In material supply, we specialize in genuine Japanese UACJ 5052 masked aluminum plates, renowned for low residual stress and distortion-free CNC machining. We also maintain extensive stock of 7075 aerospace-grade ultra-hard alloys, 6061 structural plates, 5083 marine corrosion-resistant plates, and a comprehensive range of custom extrusions." },
        { title: "Real-Time Stock & Mold Specs", script: "For inventory specifications, HARVARD provides a real-time database of over 3,080 items, including 514 stock plates, rods, and flat bars, alongside 2,557 standard extrusion mold profiles requiring zero tooling fees. Search by alloy, dimension, or mold number to add items directly to your RFQ inquiry." },
        { title: "High-End Precision Machining", script: "Beyond raw materials, HARVARD delivers robust manufacturing power. Our facilities integrate high-speed CNC milling, multi-axis lathes, aerospace 5-axis simultaneous machining, large gantry milling, and automated anodizing surface treatments, achieving micron-level precision from 3D drawings to final parts." },
        { title: "Semiconductor & Aerospace Track Record", script: "We collaborate closely in developing semiconductor vacuum chamber bases, etching equipment parts, and aerospace structural components. Through strict flatness control and certified mill sheets, we resolve stress deformation and lightweighting challenges for global technology leaders." },
        { title: "Hardness Conversion & Metallurgy Dict", script: "To assist R&D and procurement engineers in cross-referencing metal specifications, we provide an interactive hardness calculator supporting Brinell, Rockwell, Vickers, and Shore scales, along with a comprehensive metallurgical temper designation dictionary." },
        { title: "Direct Inquiry & Closing Remarks", script: "Thank you for taking the time to listen to the HARVARD Enterprises audio guide. Whether you require custom dimensions, on-demand sawing, or online CAD drawing quotation, feel free to submit an RFQ or contact our Taipei, Taichung, and Tainan logistics hubs. Our professional team will gladly respond within 24 hours. HARVARD Enterprises — aluminum rooted, service foremost. We look forward to partnering with you for mutual success!" }
    ],
    'ja': [
        { title: "賀華実業 · 企業概要", script: "賀華実業有限公司の音声ガイドへようこそ。1973年創立以来、台湾で40年近くの信頼と実績を築いてまいりました。私たちは総合アルミニウム材料サプライチェーンと高度精密加工の一貫体制を確立し、「アルミを原点とし、顧客第一主義」をモットーに、最先端ハイテク産業の確かなパートナーとして貢献しています。" },
        { title: "会社概要 · 沿革と将来ビジョン", script: "1973年の設立以来、賀華実業は国際貿易からスタートし、豊富な常備在庫と高精度CNC切断加工力を兼ね備えた総合材料サプライヤーへと進化しました。誠実と共栄を胸に、アルミニウム、ステンレス、銅、精密加工など9大事業を展開し、半導体・航空宇宙・医療機器など11大産業を力強くサポートしています。" },
        { title: "台湾全域サービス物流拠点", script: "お客様の緊急な素材需要に応えるため、賀華実業は台湾全土に直営拠点を整備しています。台北本社、台中物流切断センター、そして台南二大工場を連携させ、豊富な常備在庫と自社配送トラック便により、迅速な調達と配送を実現しています。" },
        { title: "旗艦アルミニウム材料紹介", script: "材料供給において、当社は日本原装のUACJ 5052貼合アルミ厚板を主力展開。独自の圧延技術により残留応力を極小化し、切削後の反りを防ぎます。さらに7075航空宇宙用超硬合金、6061構造用厚板、5083耐食海洋板、各種アルミ押出形材を常備しています。" },
        { title: "常備在庫・金型スペック検索", script: "在庫と金型仕様において、賀華実業は3,080件を超えるリアルタイム検索データベースを構築。514項目の常備在庫アルミ板・丸棒・平角棒と、金型代無料の2,557種類の押出型材を網羅。材質や寸法、型番を入力するだけで即座に検索し、お見積もりに追加いただけます。" },
        { title: "高度精密加工と製造技術", script: "材料の供給にとどまらず、賀華実業は高度な精密加工設備を完備。CNC高速フライス盤、精密旋盤、航空機規格の5軸マシニングセンタ、大型門型機、そして表面アルマイト処理までの一貫体制により、3D図面からミクロン単位の精密部品を高効率に仕上げます。" },
        { title: "半導体・航空宇宙主要実績", script: "半導体真空チャンバーベース、エッチング装置構造部品、航空宇宙高強度部品の製造に深く携わり、卓越した平面度管理と原廠ミルシートにより、残留応力による変形や軽量化の課題を解決。世界的大手装置メーカーから高い信頼を得ています。" },
        { title: "国際硬度換算と調質記号辞書", script: "研究開発および購買エンジニアをサポートするため、ブリネル、ロックウェル、ビッカース、ショア硬度に対応した国際標準リアルタイム硬度換算ツールと、アルミニウム調質記号辞典を完備。材料選定の信頼できるツールとしてご活用いただけます。" },
        { title: "お問い合わせと結びの挨拶", script: "賀華実業の企業音声ガイドをお聞きいただき、誠にありがとうございました。特注寸法の手配、高精度切断、図面お見積もりなど、本ページのオンライン見積りフォームまたは各拠点へお気軽にお問い合わせください。専門エンジニアが24時間以内に迅速に対応いたします。賀華実業はアルミを礎に、お客様と共に卓越した価値を創造してまいります。" }
    ],
    'ko': [
        { title: "하바드실업(賀華實業) · 기업 개요", script: "하바드실업(賀華實業) 유한회사에 오신 것을 환영합니다. 1973년 설립 이래 40여 년간 대만에서 신뢰를 쌓아온 하바드실업(賀華實業)은 종합 알루미늄 소재 공급망과 초정밀 가공 플랫폼을 구축해 왔습니다. 알루미늄의 기본, 고객 최우선의 신념으로 반도체와 항공우주 등 첨단 정밀 산업의 든든한 파트너가 되겠습니다." },
        { title: "회사소개 · 연혁 및 비전", script: "1973년 설립 이래 하바드실업(賀華實業)은 비철금속 무역을 시작으로 방대한 상시 재고와 정밀 CNC 절단 가공 기술을 갖춘 종합 소재 기업으로 발전했습니다. 신뢰와 상생을 바탕으로 알루미늄, 스테인리스, 특수 동합금 및 정밀 가공 등 9대 핵심 사업을 운영하며 반도체와 항공우주를 비롯한 11대 첨단 산업에 필수 소재를 공급합니다." },
        { title: "대만 전국 물류 거점망", script: "신속한 자재 수급과 가공 수요에 대응하기 위해 하바드실업(賀華實業)은 타이베이 본사, 타이중 물류 절단 센터, 타이난 자리 및 마두 2대 공장을 연결하는 전국 물류망을 구축했습니다. 상시 보유 재고와 전용 직영 운송 시스템으로 신속한 전국 배송을 보장합니다." },
        { title: "주요 알루미늄 소재 소개", script: "소재 공급에 있어 일본 정품 UACJ 5052 필름 알루미늄 판재를 주력으로 공급합니다. 내부 잔류 응력을 제거하여 가공 후 뒤틀림이 없으며, 7075 항공우주용 초경질 알루미늄, 6061 구조용 판재, 5083 내식 해양용 판재 및 다양한 압출 형재를 전국 최대 규모로 보유하고 있습니다." },
        { title: "실시간 재고 및 금형 규격", script: "재고 및 금형 규격 시스템을 통해 3,080개 이상의 실시간 데이터베이스를 제공합니다. 514종의 상시 보유 판재/환봉/평철 규격과 금형비가 들지 않는 2,557종의 알루미늄 압출 금형을 손쉽게 검색하여 견적서에 바로 추가할 수 있습니다." },
        { title: "초정밀 가공 및 제조 역량", script: "단순 소재 공급을 넘어 초정밀 가공 역량을 자랑합니다. 고속 CNC 밀링, 정밀 선반, 항공우주용 5축 동시 가공기, 대형 갠트리 밀링 및 아노다이징 표면처리까지 원스톱으로 연동하여 3D 도면 기반의 마이크론 단위 정밀 가공을 신속하게 완수합니다." },
        { title: "반도체 및 항공우주 주요 실적", script: "반도체 진공 챔버 베이스, 식각 장비 핵심 부품 및 항공우주 구조 부품 개발에 참여하고 있습니다. 탁월한 진평도 제어와 정품 밀시트를 통해 가공 변형과 경량화 과제를 완벽히 해결하여 글로벌 장비 제조사들의 오랜 신뢰를 받고 있습니다." },
        { title: "국제 경도 환산 및 기술 사전", script: "연구개발 및 구매 엔지니어를 위해 브리넬, 로크웰, 비커스, 쇼어 경도를 실시간으로 상호 환산할 수 있는 국제 표준 경도 계산기와 알루미늄 조질 열처리 기호 사전을 구축하여 일상적인 소재 선정을 돕습니다." },
        { title: "실시간 문의 및 맺음말", script: "하바드실업(賀華實業) 기업 음성 가이드 투어를 경청해 주셔서 대단히 감사합니다. 특수 규격 자재 수급, 정밀 절단 또는 도면 견적 문의는 온라인 견적서를 작성하시거나 타이베이, 타이중, 타이난 거점으로 문의해 주시면 24시간 이내에 신속히 답변드리겠습니다. 하바드실업(賀華實業)은 고객사와 함께 미래를 열어가겠습니다. 감사합니다!" }
    ]
};

function getLocalizedChapter(index, lang) {
    if (!lang) lang = window.getCurrentLanguage ? window.getCurrentLanguage() : 'zh-TW';
    const langDict = TOUR_CHAPTERS_I18N[lang] || TOUR_CHAPTERS_I18N['zh-TW'];
    if (langDict && langDict[index]) {
        return langDict[index];
    }
    const defaultCh = (audioTourState.chapters && audioTourState.chapters[index]) || {};
    return {
        title: defaultCh.title || `Chapter ${index + 1}`,
        script: defaultCh.script || ''
    };
}

function updateTourChaptersDropdown(lang) {
    const chapterSelect = document.getElementById('dockChapterSelect');
    if (!chapterSelect || !audioTourState.chapters.length) return;
    if (!lang) lang = window.getCurrentLanguage ? window.getCurrentLanguage() : 'zh-TW';

    chapterSelect.innerHTML = audioTourState.chapters.map((ch, idx) => {
        const loc = getLocalizedChapter(idx, lang);
        return `<option value="${idx}">${idx + 1}. ${loc.title}</option>`;
    }).join('');

    chapterSelect.value = audioTourState.currentChapter;
    const trackTitle = document.getElementById('dockTrackTitle');
    if (trackTitle) {
        trackTitle.textContent = getLocalizedChapter(audioTourState.currentChapter, lang).title;
    }
}

function getChapterAudioUrl(ch) {
    if (!ch || !ch.audio_file) return '';
    if (audioTourState.voice === 'zen-male' || audioTourState.voice === 'zh-TW-YunJheNeural') {
        return ch.audio_file.replace(/\.mp3$/i, '_male.mp3');
    }
    if (audioTourState.voice === 'zen-female') {
        return ch.audio_file.replace(/\.mp3$/i, '_zen_female.mp3');
    }
    return ch.audio_file;
}

function clearChimeTimer() {
    if (audioTourState.chimeAdvanceTimer) {
        clearTimeout(audioTourState.chimeAdvanceTimer);
        audioTourState.chimeAdvanceTimer = null;
    }
}

function initAudioTour() {
    const playBtn = document.getElementById('dockPlayBtn');
    const prevBtn = document.getElementById('dockPrevBtn');
    const nextBtn = document.getElementById('dockNextBtn');
    const chapterSelect = document.getElementById('dockChapterSelect');
    const bgmSelect = document.getElementById('dockBgmSelect');
    const voiceSelect = document.getElementById('dockVoiceSelect');
    const speedSelect = document.getElementById('dockSpeedSelect');
    const zenBgmBtn = document.getElementById('dockZenBgmBtn');
    
    // Read chapters from embedded data
    if (window.SITE_DATA && window.SITE_DATA.tour_chapters) {
        audioTourState.chapters = window.SITE_DATA.tour_chapters;
    }

    if (!audioTourState.chapters.length) return;

    // Sync initial dropdown states
    if (voiceSelect && voiceSelect.value) {
        audioTourState.voice = voiceSelect.value;
    }
    if (speedSelect && speedSelect.value) {
        audioTourState.speed = parseFloat(speedSelect.value) || 1.0;
    }

    // Populate chapters dropdown with localized titles
    if (chapterSelect) {
        const initLang = window.getCurrentLanguage ? window.getCurrentLanguage() : 'zh-TW';
        updateTourChaptersDropdown(initLang);
        
        chapterSelect.addEventListener('change', (e) => {
            clearChimeTimer();
            stopCardAudio();
            selectChapter(parseInt(e.target.value), true);
        });
    }

    // Studio Acoustic Background Music Toggle & Selector
    if (zenBgmBtn) {
        zenBgmBtn.addEventListener('click', () => {
            const isVoiceSpeaking = audioTourState.isPlaying || audioTourState.isCardPlaying;
            if (StudioBgmEngine.isAmbientPlaying) {
                StudioBgmEngine.bgmEnabled = false;
                StudioBgmEngine.standaloneMode = false;
                StudioBgmEngine.stopAmbient();
                zenBgmBtn.classList.remove('active');
                if (bgmSelect) bgmSelect.value = 'off';
                showToast("🔇 已關閉背景輕音樂（保留純淨人聲導覽）");
            } else {
                if (StudioBgmEngine.currentTrack === 'off') {
                    StudioBgmEngine.currentTrack = 'piano';
                }
                StudioBgmEngine.bgmEnabled = true;
                StudioBgmEngine.standaloneMode = !isVoiceSpeaking;
                zenBgmBtn.classList.add('active');
                if (bgmSelect) bgmSelect.value = StudioBgmEngine.currentTrack;
                StudioBgmEngine.startAmbient(isVoiceSpeaking);
                showToast(`🎵 正在播放：${BGM_TRACKS[StudioBgmEngine.currentTrack].label}`);
            }
        });
    }

    if (bgmSelect) {
        bgmSelect.addEventListener('change', (e) => {
            const val = e.target.value;
            const isVoiceSpeaking = audioTourState.isPlaying || audioTourState.isCardPlaying;
            if (val === 'off') {
                StudioBgmEngine.setTrack('off', isVoiceSpeaking);
                if (zenBgmBtn) zenBgmBtn.classList.remove('active');
                showToast("🔇 已關閉背景配樂");
            } else {
                if (!isVoiceSpeaking) {
                    StudioBgmEngine.standaloneMode = true;
                }
                StudioBgmEngine.setTrack(val, isVoiceSpeaking);
                if (zenBgmBtn) zenBgmBtn.classList.add('active');
                showToast(`🎵 已切換曲目：${BGM_TRACKS[val].label}`);
            }
        });
    }

    // Voice & Speed change
    if (voiceSelect) {
        voiceSelect.addEventListener('change', (e) => {
            clearChimeTimer();
            const wasTourPlaying = audioTourState.isPlaying;
            const wasCardPlaying = audioTourState.isCardPlaying;
            audioTourState.voice = e.target.value;
            showToast(`🎙️ 已切換導覽人聲：${e.target.options[e.target.selectedIndex].text}`);

            if (wasCardPlaying && audioTourState.lastCardText) {
                stopCardAudio();
                window.readAloudText(audioTourState.lastCardText, audioTourState.lastCardBtn);
            } else {
                selectChapter(audioTourState.currentChapter, wasTourPlaying);
            }
        });
    }

    if (speedSelect) {
        speedSelect.addEventListener('change', (e) => {
            audioTourState.speed = parseFloat(e.target.value);
            audioTourState.audio.playbackRate = audioTourState.speed;
            if (audioTourState.cardAudio) {
                audioTourState.cardAudio.playbackRate = audioTourState.speed;
            }
        });
    }

    // Audio Event listeners
    audioTourState.audio.addEventListener('ended', () => {
        if (audioTourState.currentChapter < audioTourState.chapters.length - 1) {
            clearChimeTimer();
            audioTourState.chimeAdvanceTimer = setTimeout(() => {
                selectChapter(audioTourState.currentChapter + 1, true);
            }, 650);
        } else {
            audioTourState.isPlaying = false;
            StudioBgmEngine.playFinaleOutro();
            selectChapter(0, false);
            showToast("✨ 感謝聆聽賀華實業企業導覽 · 歡迎隨時線上諮詢估價！");
        }
    });

    audioTourState.audio.addEventListener('play', () => {
        audioTourState.isPlaying = true;
        updatePlayButtonUI();
        if (StudioBgmEngine.bgmEnabled && StudioBgmEngine.currentTrack !== 'off') {
            StudioBgmEngine.startAmbient(true);
        }
    });

    audioTourState.audio.addEventListener('pause', () => {
        if (!audioTourState.audio.ended) {
            audioTourState.isPlaying = false;
            updatePlayButtonUI();
            StudioBgmEngine.setDucking(false);
        }
    });

    // If a voice-specific chapter file fails, fall back to the base file, then browser TTS
    audioTourState.audio.addEventListener('error', () => {
        const ch = audioTourState.chapters[audioTourState.currentChapter];
        if (!ch) return;
        const cur = audioTourState.audio.src || '';
        if (ch.audio_file && !cur.endsWith(ch.audio_file)) {
            audioTourState.audio.src = ch.audio_file;
            audioTourState.audio.play().catch(() => {});
        } else if (ch.text || ch.script) {
            audioTourState.isPlaying = false;
            updatePlayButtonUI();
            speakWithBrowserTTS(ch.text || ch.script);
        }
    });

    // Button actions
    if (playBtn) {
        playBtn.addEventListener('click', () => {
            togglePlay();
        });
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            if (audioTourState.currentChapter > 0) {
                clearChimeTimer();
                selectChapter(audioTourState.currentChapter - 1, true);
            }
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            if (audioTourState.currentChapter < audioTourState.chapters.length - 1) {
                clearChimeTimer();
                selectChapter(audioTourState.currentChapter + 1, true);
            }
        });
    }

    // Floating hero trigger
    const startTourHeroBtn = document.getElementById('startTourHeroBtn');
    if (startTourHeroBtn) {
        startTourHeroBtn.addEventListener('click', (e) => {
            e.preventDefault();
            clearChimeTimer();
            if (StudioBgmEngine.bgmEnabled) {
                StudioBgmEngine.startAmbient(true);
            }
            selectChapter(0, true);
        });
    }

    // Init first chapter
    selectChapter(0, false);
    initAudioVisualizer();
}

function stopCardAudio() {
    if (audioTourState.cardAudio) {
        audioTourState.cardAudio.pause();
        audioTourState.cardAudio.currentTime = 0;
        audioTourState.cardAudio = null;
    }
    if ('speechSynthesis' in window && window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
    }
    audioTourState.isCardPlaying = false;
    document.querySelectorAll('.btn-read-tts.playing, .ai-bubble-audio-btn.playing').forEach(b => {
        b.classList.remove('playing');
        const eq = b.querySelector('.audio-equalizer-bars');
        if (eq) eq.classList.remove('playing');
    });
}

function selectChapter(index, autoPlay = false) {
    if (index < 0 || index >= audioTourState.chapters.length) return;
    stopCardAudio();
    audioTourState.currentChapter = index;
    const ch = audioTourState.chapters[index];
    const curLang = window.getCurrentLanguage ? window.getCurrentLanguage() : 'zh-TW';
    const localizedCh = getLocalizedChapter(index, curLang);

    // Update UI title
    const trackTitle = document.getElementById('dockTrackTitle');
    if (trackTitle) trackTitle.textContent = localizedCh.title;

    const chapterSelect = document.getElementById('dockChapterSelect');
    if (chapterSelect) chapterSelect.value = index;

    if (curLang === 'zh-TW') {
        const targetSrc = getChapterAudioUrl(ch);
        audioTourState.audio.pause();
        audioTourState.audio.src = targetSrc;
        audioTourState.audio.playbackRate = audioTourState.speed || 1.0;

        if (autoPlay) {
            audioTourState.audio.play().then(() => {
                audioTourState.isPlaying = true;
                audioTourState.audio.playbackRate = audioTourState.speed || 1.0;
                updatePlayButtonUI();
                highlightAndScrollToSection(ch.section_id);
            }).catch(err => {
                console.warn("Auto-play prevented:", err);
            });
        } else {
            audioTourState.isPlaying = false;
            updatePlayButtonUI();
        }
    } else {
        // Multi-language Neural TTS synthesis
        let voice = audioTourState.voice;
        if (!voice || (curLang === 'en' && !voice.startsWith('en-')) || (curLang === 'ja' && !voice.startsWith('ja-')) || (curLang === 'ko' && !voice.startsWith('ko-'))) {
            if (curLang === 'en') voice = 'en-US-JennyNeural';
            else if (curLang === 'ja') voice = 'ja-JP-NanamiNeural';
            else if (curLang === 'ko') voice = 'ko-KR-SunHiNeural';
            audioTourState.voice = voice;
        }

        audioTourState.audio.pause();
        if (autoPlay) {
            audioTourState.isPlaying = true;
            updatePlayButtonUI();
            highlightAndScrollToSection(ch.section_id);
        }

        const url = `/api/tts?text=${encodeURIComponent(localizedCh.script)}&voice=${encodeURIComponent(voice)}`;
        fetch(url)
            .then(res => res.json())
            .then(data => {
                if (data && data.url) {
                    audioTourState.audio.src = data.url;
                    audioTourState.audio.playbackRate = audioTourState.speed || 1.0;
                    if (autoPlay) {
                        audioTourState.audio.play().then(() => {
                            audioTourState.isPlaying = true;
                            audioTourState.audio.playbackRate = audioTourState.speed || 1.0;
                            updatePlayButtonUI();
                        }).catch(err => console.warn("Auto-play prevented:", err));
                    }
                }
            })
            .catch(err => {
                console.error("Failed to load localized audio tour:", err);
            });
    }
}

function togglePlay() {
    clearChimeTimer();
    stopCardAudio();
    if (audioTourState.isPlaying) {
        StudioBgmEngine.standaloneMode = false;
        audioTourState.audio.pause();
    } else {
        if (StudioBgmEngine.bgmEnabled && StudioBgmEngine.currentTrack !== 'off') {
            StudioBgmEngine.startAmbient(true);
        }
        const curLang = window.getCurrentLanguage ? window.getCurrentLanguage() : 'zh-TW';
        if (curLang !== 'zh-TW' && (!audioTourState.audio.src || !audioTourState.audio.src.includes('tts_'))) {
            selectChapter(audioTourState.currentChapter, true);
        } else {
            const ch = audioTourState.chapters[audioTourState.currentChapter];
            if (curLang === 'zh-TW') {
                const expectedUrl = getChapterAudioUrl(ch);
                if (!audioTourState.audio.src || !audioTourState.audio.src.endsWith(expectedUrl)) {
                    audioTourState.audio.src = expectedUrl;
                }
            }
            audioTourState.audio.playbackRate = audioTourState.speed || 1.0;
            audioTourState.audio.play().then(() => {
                audioTourState.audio.playbackRate = audioTourState.speed || 1.0;
                highlightAndScrollToSection(ch.section_id);
            }).catch(err => {
                selectChapter(audioTourState.currentChapter, true);
            });
        }
    }
}

function updatePlayButtonUI() {
    const playBtn = document.getElementById('dockPlayBtn');
    const heroBtn = document.getElementById('startTourHeroBtn');
    if (!playBtn) return;
    if (audioTourState.isPlaying) {
        playBtn.innerHTML = '⏸';
        playBtn.title = '暫停導覽';
        playBtn.style.boxShadow = '0 0 22px rgba(180, 130, 45, 0.55)';
        if (heroBtn) {
            heroBtn.classList.add('playing');
            const eq = heroBtn.querySelector('.audio-equalizer-bars');
            if (eq) eq.classList.add('playing');
        }
    } else {
        playBtn.innerHTML = '▶';
        playBtn.title = '啟動語音導覽';
        playBtn.style.boxShadow = '0 4px 16px rgba(166, 44, 34, 0.3)';
        if (heroBtn) {
            heroBtn.classList.remove('playing');
            const eq = heroBtn.querySelector('.audio-equalizer-bars');
            if (eq) eq.classList.remove('playing');
        }
    }
}

function highlightAndScrollToSection(sectionId) {
    if (!sectionId) return;
    if (window.navigateToPage) {
        window.navigateToPage(sectionId, { fromTour: true });
    }
    const el = document.getElementById(sectionId);
    if (!el) return;
    
    // Temporary glow highlight
    el.classList.add('active-tour-section');
    setTimeout(() => {
        el.classList.remove('active-tour-section');
    }, 4500);
}

// Waveform visualizer
function initAudioVisualizer() {
    const canvas = document.getElementById('audioWaveCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    let waveOffset = 0;
    
    function drawWave() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        const width = canvas.width;
        const height = canvas.height;
        const mid = height / 2;
        
        if (StudioBgmEngine.bowlVisualEnergy > 0.01) {
            StudioBgmEngine.bowlVisualEnergy *= 0.965;
        } else {
            StudioBgmEngine.bowlVisualEnergy = 0;
        }

        const isSpeaking = audioTourState.isPlaying || audioTourState.isCardPlaying;
        const isAmbient = StudioBgmEngine.isAmbientPlaying;
        const bowlBoost = StudioBgmEngine.bowlVisualEnergy * 11;

        ctx.beginPath();
        ctx.moveTo(0, mid);
        
        const amplitude = (isSpeaking ? 9 : (isAmbient ? 4.5 : 1.8)) + bowlBoost;
        const speed = isSpeaking ? 0.11 : (isAmbient ? 0.05 : 0.025);
        waveOffset += speed;

        for (let x = 0; x < width; x++) {
            const y = mid + Math.sin(x * 0.045 + waveOffset) * amplitude * Math.sin((x / width) * Math.PI);
            ctx.lineTo(x, y);
        }
        
        const strokeColor = isSpeaking ? '#00e5ff' : (isAmbient ? '#38bdf8' : 'rgba(0, 229, 255, 0.35)');
        ctx.strokeStyle = strokeColor;
        ctx.lineWidth = 2;
        ctx.shadowColor = (isSpeaking || isAmbient) ? 'rgba(180, 128, 36, 0.45)' : 'transparent';
        ctx.shadowBlur = (isSpeaking || isAmbient) ? 7 : 0;
        ctx.stroke();
        
        requestAnimationFrame(drawWave);
    }
    drawWave();
}

// Browser-native speech fallback (used when the neural TTS server is unreachable)
function speakWithBrowserTTS(text, onDone) {
    if (!('speechSynthesis' in window)) {
        showToast("語音合成服務暫時無法使用，請稍後重試");
        if (onDone) onDone();
        return false;
    }
    try {
        window.speechSynthesis.cancel();
        const utter = new SpeechSynthesisUtterance(String(text).slice(0, 1200));
        utter.lang = 'zh-TW';
        utter.rate = Math.min(1.6, Math.max(0.6, (audioTourState.speed || 1.0) * 0.95));
        const voices = window.speechSynthesis.getVoices() || [];
        const preferFemale = audioTourState.voice !== 'zen-male';
        const zhVoices = voices.filter(v => /zh[-_](TW|HK|CN)/i.test(v.lang) || /Chinese|中文|國語/i.test(v.name));
        const tw = zhVoices.filter(v => /TW/i.test(v.lang));
        const pool = tw.length ? tw : zhVoices;
        let pick = pool.find(v => preferFemale ? /female|Hsiao|Yating|Hanhan|女/i.test(v.name) : /male|Yun|Zhiwei|男/i.test(v.name));
        if (!pick && pool.length) pick = pool[0];
        if (pick) utter.voice = pick;

        utter.onstart = () => { audioTourState.isCardPlaying = true; StudioBgmEngine.setDucking(true); };
        const finish = () => {
            audioTourState.isCardPlaying = false;
            StudioBgmEngine.setDucking(false);
            if (onDone) onDone();
        };
        utter.onend = finish;
        utter.onerror = finish;
        window.speechSynthesis.speak(utter);
        showToast("🎙️ 正在為您朗讀內容（瀏覽器語音）...");
        return true;
    } catch (e) {
        console.error(e);
        if (onDone) onDone();
        return false;
    }
}
if ('speechSynthesis' in window) {
    // Warm up voice list (Chrome loads asynchronously)
    window.speechSynthesis.getVoices();
    window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
}

window.getLocalizedSpeech = function(text, lang) {
    if (!lang || lang === 'zh-TW') return text;
    // Map common card narrations
    if (text.includes('成立概要') || text.includes('企業沿革')) {
        if (lang === 'en') return "Company Overview: Founded in 1973, HARVARD Enterprises has grown into an integrated aluminum supply chain provider with vast on-hand inventory and precision CNC machining capabilities. We are dedicated to supporting high-tech manufacturing with certified mill sheets and swift delivery.";
        if (lang === 'ja') return "設立概要：1973年創立以来、賀華実業は豊富な常備在庫と高精度CNC切断加工力を兼ね備えた総合材料サプライヤーとして成長しました。全ロットに原廠ミルシートを添付し、迅速で確実な供給体制をお約束します。";
        if (lang === 'ko') return "회사 개요: 1973년 설립된 하바드실업(賀華實業)은 방대한 상시 재고와 정밀 CNC 절단 가공 기술을 갖춘 종합 알루미늄 전문 기업입니다. 전 품목 정품 밀시트 발행과 신속한 전국 배송으로 고객사의 든든한 파트너가 되겠습니다.";
    }
    if (text.includes('經營理念') || text.includes('未來願景') || text.includes('誠信立基')) {
        if (lang === 'en') return "Philosophy & Vision: Integrity First and Mutual Growth. HARVARD expands automated warehousing and high-speed CNC centers to supply specialized aerospace and semiconductor alloys while establishing sustainable green recycling supply chains.";
        if (lang === 'ja') return "経営理念とビジョン：誠実と共栄。スマート物流倉庫と高速CNC加工機への設備投資を強化し、半導体真空チャンバーや航空宇宙専用合金のラインナップを拡充。持続可能なリサイクル供給体制を推進します。";
        if (lang === 'ko') return "경영 이념 및 비전: 신뢰 기반과 동반 성장. 스마트 물류 창고와 초고속 CNC 가공 장비 투자를 확대하여 반도체 및 항공우주 전용 합금을 공급하고 지속 가능한 친환경 순환 공급망을 구축합니다.";
    }
    if (text.includes('台北總公司') || text.includes('台北市松山區')) {
        if (lang === 'en') return "Taipei Headquarters: International trade hub, import and export customs clearance, and northern administrative center. Telephone: +886-2-2718-3134.";
        if (lang === 'ja') return "台北本社：国際貿易ハブ、輸出入通関および北部営業管理センター。電話番号：(02) 2718-3134。";
        if (lang === 'ko') return "타이베이 본사: 국제 무역 허브, 수출입 통관 및 북부 영업 관리 센터. 전화: (02) 2718-3134.";
    }
    if (text.includes('台中物流中心') || text.includes('台中廠')) {
        if (lang === 'en') return "Taichung Logistics Center: Located near National Highway 1, maintaining extensive inventory of alloy plates, rods, and pipes with large-scale precision sawing. Telephone: +886-4-2258-4931.";
        if (lang === 'ja') return "台中物流センター：国道1号に隣接し、常備在庫の厚板・棒・パイプと大径精密切断加工を完備。電話番号：(04) 2258-4931。";
        if (lang === 'ko') return "타이중 물류센터: 국도 1호선 인근, 판재/환봉/파이프 상시 보유 및 대형 정밀 절단 설비 완비. 전화: (04) 2258-4931.";
    }
    if (text.includes('佳里') || text.includes('麻豆') || text.includes('台南')) {
        if (lang === 'en') return "Tainan Logistics and Manufacturing Plants (Jiali and Madou): Deeply rooted in southern Taiwan's semiconductor corridor, equipped with automated cutting equipment and spacious storage. Telephone: +886-6-726-3666.";
        if (lang === 'ja') return "台南物流・二大工場（佳里・麻豆）：南部半導体・先端産業クラスターに密着し、最新自動化設備と広大な倉庫を配備。電話番号：(06) 726-3666。";
        if (lang === 'ko') return "타이난 물류 및 제조 거점 (자리/마두 2대 공장): 남부 반도체 및 첨단 기술 산업단지 지원, 최신 자동화 절단 설비와 대규모 물류 창고 보유. 전화: (06) 726-3666.";
    }
    if (text.includes('UACJ') || text.includes('5052') || text.includes('貼膜')) {
        if (lang === 'en') return "Genuine Japanese UACJ 5052 masked aluminum plates: Minimized residual stress through unique rolling process, preventing warpage after extensive CNC milling. Designed for semiconductor vacuum chambers and optoelectronics.";
        if (lang === 'ja') return "日本原装 UACJ 5052 貼合アルミ板：独自の圧延技術により残留応力を極小化し、大量の精密フライス加工後も反りが発生しません。半導体真空チャンバーや光電装置の指定材料です。";
        if (lang === 'ko') return "일본 정품 UACJ 5052 필름 알루미늄 판재: 독자적인 압연 공정으로 잔류 응력을 제거하여 대량 절삭 가공 후에도 뒤틀림이 없습니다. 반도체 진공 챔버 및 광전자 장비의 필수 소재입니다.";
    }
    if (text.includes('AI 智慧工程客服') || text.includes('智能工程客服')) {
        if (lang === 'en') return "Hello! I am the HARVARD AI Engineering Assistant. You can inquire via voice or text for stock specifications, alloy selection, or use AI for cutting stock optimization!";
        if (lang === 'ja') return "こんにちは！賀華実業 AI 営業技術アシスタントです。在庫規格の検索や合金選定、AI による定寸切断の最適化計算をご案内いたします！";
        if (lang === 'ko') return "안녕하십니까! 하바드실업(賀華實業) AI 엔지니어링 챗봇입니다. 재고 규격 검색과 소재 추천, AI 모재 절단 최적화 솔루션을 제공합니다!";
    }
    return text;
};

// On-demand dynamic TTS read-aloud for cards
window.readAloudText = function(text, btnElement) {
    if (!text) return;
    
    clearChimeTimer();
    stopCardAudio();
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    audioTourState.lastCardText = text;
    audioTourState.lastCardBtn = btnElement || null;

    const voiceSelect = document.getElementById('dockVoiceSelect');
    if (voiceSelect && voiceSelect.value) {
        audioTourState.voice = voiceSelect.value;
    }

    if (StudioBgmEngine.bgmEnabled && StudioBgmEngine.currentTrack !== 'off') {
        StudioBgmEngine.startAmbient(true);
    }

    const originalText = btnElement ? btnElement.innerHTML : '';
    const restoreBtn = () => {
        if (btnElement) {
            btnElement.innerHTML = originalText;
            btnElement.disabled = false;
        }
    };
    if (btnElement) {
        btnElement.innerHTML = '⏳ 語音載入中...';
        btnElement.disabled = true;
    }

    if (audioTourState.isPlaying) {
        audioTourState.audio.pause();
    }
    
    const curLang = window.getCurrentLanguage ? window.getCurrentLanguage() : 'zh-TW';
    const speechText = window.getLocalizedSpeech(text, curLang);
    let voice = audioTourState.voice;
    if (!voice || (curLang === 'en' && !voice.startsWith('en-')) || (curLang === 'ja' && !voice.startsWith('ja-')) || (curLang === 'ko' && !voice.startsWith('ko-')) || (curLang === 'zh-TW' && !voice.startsWith('zh-') && !voice.startsWith('zen-'))) {
        if (curLang === 'en') voice = 'en-US-JennyNeural';
        else if (curLang === 'ja') voice = 'ja-JP-NanamiNeural';
        else if (curLang === 'ko') voice = 'ko-KR-SunHiNeural';
        else voice = 'zen-male';
        audioTourState.voice = voice;
    }
    const url = `/api/tts?text=${encodeURIComponent(speechText)}&voice=${encodeURIComponent(voice)}`;

    const controller = ('AbortController' in window) ? new AbortController() : null;
    const timeoutId = setTimeout(() => { if (controller) controller.abort(); }, 25000);
    
    fetch(url, controller ? { signal: controller.signal } : {})
        .then(res => res.json().catch(() => ({})).then(data => ({ ok: res.ok, data })))
        .then(({ ok, data }) => {
            clearTimeout(timeoutId);
            restoreBtn();
            if (!ok || !data.url) {
                speakWithBrowserTTS(text);
                return;
            }
            const speechAudio = new Audio(data.url);
            speechAudio.playbackRate = audioTourState.speed || 1.0;
            audioTourState.cardAudio = speechAudio;
            speechAudio.addEventListener('play', () => {
                audioTourState.isCardPlaying = true;
                StudioBgmEngine.setDucking(true);
                if (btnElement) {
                    btnElement.classList.add('playing');
                    let eq = btnElement.querySelector('.audio-equalizer-bars');
                    if (!eq) {
                        eq = document.createElement('span');
                        eq.className = 'audio-equalizer-bars';
                        eq.innerHTML = '<span></span><span></span><span></span><span></span>';
                        btnElement.appendChild(eq);
                    }
                    eq.classList.add('playing');
                }
            });
            speechAudio.addEventListener('ended', () => {
                audioTourState.isCardPlaying = false;
                StudioBgmEngine.setDucking(false);
                if (btnElement) {
                    btnElement.classList.remove('playing');
                    const eq = btnElement.querySelector('.audio-equalizer-bars');
                    if (eq) eq.classList.remove('playing');
                }
            });
            speechAudio.addEventListener('pause', () => {
                audioTourState.isCardPlaying = false;
                StudioBgmEngine.setDucking(false);
                if (btnElement) {
                    btnElement.classList.remove('playing');
                    const eq = btnElement.querySelector('.audio-equalizer-bars');
                    if (eq) eq.classList.remove('playing');
                }
            });
            speechAudio.addEventListener('error', () => {
                audioTourState.cardAudio = null;
                speakWithBrowserTTS(text);
            });
            const p = speechAudio.play();
            if (p && typeof p.then === 'function') {
                p.then(() => showToast("🎙️ 正在為您朗讀內容..."))
                 .catch(err => {
                     console.warn('Audio play rejected:', err);
                     audioTourState.cardAudio = null;
                     speakWithBrowserTTS(text);
                 });
            }
        })
        .catch(err => {
            clearTimeout(timeoutId);
            console.error(err);
            restoreBtn();
            speakWithBrowserTTS(text);
        });
};

/* ==========================================================================
   3. Stock Specs Explorer (現貨規格即時篩選查詢)
   ========================================================================== */
const SPEC_CATEGORY_I18N = {
    '1050 / 5052 鋁板現貨': {
        'en': '1050 / 5052 Aluminum Plate Stock',
        'ja': '1050 / 5052 アルミ板在庫',
        'ko': '1050 / 5052 알루미늄 판재 재고'
    },
    '5083 鋁合金板現貨': {
        'en': '5083 Aluminum Alloy Plate Stock',
        'ja': '5083 アルミ合金板在庫',
        'ko': '5083 알루미늄 합금판재 재고'
    },
    '6061 鋁合金板現貨': {
        'en': '6061 Aluminum Alloy Plate Stock',
        'ja': '6061 アルミ合金板在庫',
        'ko': '6061 알루미늄 합금판재 재고'
    },
    '6061 鋁圓棒現貨': {
        'en': '6061 Aluminum Round Bar Stock',
        'ja': '6061 アルミ丸棒在庫',
        'ko': '6061 알루미늄 환봉 재고'
    },
    '6061 鋁扁條現貨': {
        'en': '6061 Aluminum Flat Bar Stock',
        'ja': '6061 アルミ平角棒在庫',
        'ko': '6061 알루미늄 평각봉 재고'
    },
    '7075 鋁合金板現貨': {
        'en': '7075 Aerospace Aluminum Plate Stock',
        'ja': '7075 航空宇宙用アルミ板在庫',
        'ko': '7075 항공 알루미늄 판재 재고'
    },
    '7075 鋁圓棒現貨': {
        'en': '7075 Aluminum Round Bar Stock',
        'ja': '7075 アルミ丸棒在庫',
        'ko': '7075 알루미늄 환봉 재고'
    },
    '壓花鋁板現貨': {
        'en': 'Embossed Aluminum Tread Plate Stock',
        'ja': 'アルミ縞板・チェッカープレート在庫',
        'ko': '체크/무늬 알루미늄 판재 재고'
    },
    '日本進口 5052 貼膜鋁板現貨': {
        'en': 'Japan UACJ 5052 Masked Plate Stock',
        'ja': '日本直輸入 5052 貼合アルミ板在庫',
        'ko': '일본 수입 5052 필름 판재 재고'
    },
    '現有模具 · 6061 鋁圓棒': {
        'en': 'Tooling Available · 6061 Round Bar',
        'ja': '保有金型 · 6061 丸棒',
        'ko': '보유 금형 · 6061 환봉'
    },
    '現有模具 · 鋁六角條': {
        'en': 'Tooling Available · Hex Bar',
        'ja': '保有金型 · 六角棒',
        'ko': '보유 금형 · 육각봉'
    },
    '現有模具 · 鋁四方條': {
        'en': 'Tooling Available · Square Bar',
        'ja': '保有金型 · 角棒',
        'ko': '보유 금형 · 사각봉'
    },
    '現有模具 · 鋁圓管': {
        'en': 'Tooling Available · Round Tube',
        'ja': '保有金型 · 丸管',
        'ko': '보유 금型 · 원형관'
    },
    '現有模具 · 鋁扁條': {
        'en': 'Tooling Available · Flat Bar',
        'ja': '保有金型 · 平角棒',
        'ko': '보유 금형 · 평각봉'
    },
    '現有模具 · 鋁正方管': {
        'en': 'Tooling Available · Square Tube',
        'ja': '保有金型 · 正方形管',
        'ko': '보유 금형 · 정사각형관'
    },
    '現有模具 · 鋁長方管': {
        'en': 'Tooling Available · Rectangular Tube',
        'ja': '保有金型 · 長方形管',
        'ko': '보유 금형 · 직사각형관'
    }
};

function formatSpecCategory(cat, lang) {
    if (!cat) return '-';
    if (!lang || lang === 'zh-TW') return cat;
    const trans = SPEC_CATEGORY_I18N[cat];
    return (trans && trans[lang]) || cat;
}

function formatSpecDimension(dim, lang) {
    if (!dim) return '-';
    if (!lang || lang === 'zh-TW') return dim;
    let s = dim;
    if (lang === 'en') {
        s = s.replace(/^厚\s*/, 'Thick ')
             .replace(/^(直徑|外徑)\s*/, 'Dia. ')
             .replace(/^方寬\s*/, 'Sq. ')
             .replace(/^對邊\s*/, 'AF ')
             .replace(/^寬\s*/, 'Width ')
             .replace(/^規格\s*/, 'Spec ');
    } else if (lang === 'ja') {
        s = s.replace(/^厚\s*/, '厚み ')
             .replace(/^(直徑|外徑)\s*/, '外径 ')
             .replace(/^方寬\s*/, '正方形幅 ')
             .replace(/^對邊\s*/, '対辺 ')
             .replace(/^寬\s*/, '幅 ')
             .replace(/^規格\s*/, '規格 ');
    } else if (lang === 'ko') {
        s = s.replace(/^厚\s*/, '두께 ')
             .replace(/^(直徑|外徑)\s*/, '외경 ')
             .replace(/^方寬\s*/, '정사각 폭 ')
             .replace(/^對邊\s*/, '대변 ')
             .replace(/^寬\s*/, '폭 ')
             .replace(/^規格\s*/, '규격 ');
    }
    return s;
}

function formatSpecNote(note, group, lang) {
    if (!lang || lang === 'zh-TW') {
        return note || (group === 'mold' ? '現有模具' : '現貨庫存');
    }
    const isEn = lang === 'en';
    const isJa = lang === 'ja';
    const isKo = lang === 'ko';

    if (!note) {
        return group === 'mold'
            ? (isEn ? 'Tooling Ready' : isJa ? '保有金型' : '보유 금형')
            : (isEn ? 'In Stock' : isJa ? '在庫あり' : '상시 재고');
    }

    if (note.startsWith('單米重')) {
        const wtVal = note.replace(/^單米重\s*/, '').trim();
        return isEn ? `Wt: ${wtVal}/m` : isJa ? `単重: ${wtVal}/m` : `단위중량: ${wtVal}/m`;
    }
    if (note.includes('五爪壓花')) return isEn ? '5-Bar Tread' : isJa ? '5本線縞板' : '5바 무늬판';
    if (note.includes('人字壓花')) return isEn ? 'Herringbone' : isJa ? '杉綾模様' : '헤링본 패턴';
    if (note.includes('六角花')) return isEn ? 'Hex Tread' : isJa ? '六角花縞板' : '육각형 무늬판';
    if (note.includes('鑽石壓花')) return isEn ? 'Diamond Tread' : isJa ? 'ダイヤ目' : '다이아몬드 무늬';
    if (note.includes('免開模')) return isEn ? 'Tooling Ready' : isJa ? '金型代無料' : '보유 금형';
    if (note.includes('A料正T6')) return isEn ? 'Prime T6 Stock' : isJa ? 'A級 T6在庫' : 'A급 정품 T6';
    if (note.includes('B料正T6')) return isEn ? 'Grade B T6' : isJa ? 'B級 T6' : 'B급 T6';
    if (note.includes('貼膜板')) return isEn ? 'Masked Plate' : isJa ? '保護フィルム付' : '필름 부착재';
    if (note.includes('進口料')) return isEn ? 'Imported Stock' : isJa ? '輸入素材' : '수입 소재';
    if (note.includes('精抽')) return isEn ? 'Precision Drawn' : isJa ? '精密引抜' : '정밀 인발';
    if (note.includes('現貨')) return isEn ? 'In Stock' : isJa ? '在庫あり' : '상시 재고';

    return note;
}

function updateSpecsCatSelectOptions(lang) {
    const sel = document.getElementById('specsCatSelect');
    if (!sel) return;
    const isEn = lang === 'en';
    const isJa = lang === 'ja';
    const isKo = lang === 'ko';

    const optgroups = sel.querySelectorAll('optgroup');
    if (optgroups.length >= 3) {
        optgroups[0].label = isEn ? '📦 In-Stock Aluminum Plate Specifications' : isJa ? '📦 アルミ合金板 常備在庫規格表' : isKo ? '📦 알루미늄 판재 상시 재고 규격표' : '📦 鋁合金板常備現貨規格表';
        optgroups[1].label = isEn ? '📦 In-Stock Aluminum Extrusion Specifications' : isJa ? '📦 アルミ押出形材 常備在庫規格表' : isKo ? '📦 알루미늄 압출재 상시 재고 규격표' : '📦 鋁擠型常備現貨規格表';
        optgroups[2].label = isEn ? '📐 Active Extrusion Molds (Free Tooling Fee)' : isJa ? '📐 保有押出金型スペック表（金型代無料）' : isKo ? '📐 보유 압출 금형 규격표 (금형비 면제)' : '📐 現有模具規格表（免開模費）';
    }

    sel.querySelectorAll('option').forEach(opt => {
        const val = opt.value;
        if (val === '全部') {
            opt.textContent = isEn ? 'All 16 Catalogs (3,081 Items)' : isJa ? '全16大規格表 (3,081件)' : isKo ? '전체 16대 규격표 (3,081건)' : '全部 16 大規格表 (3,081 筆)';
        } else {
            const trans = formatSpecCategory(val, lang);
            if (trans && trans !== val) {
                const countMatch = opt.textContent.match(/\((\d+)\)/);
                const countStr = countMatch ? ` (${countMatch[1]})` : '';
                opt.textContent = `${trans}${countStr}`;
            }
        }
    });
}

function initSpecsExplorer() {
    const searchInput = document.getElementById('specsSearchInput');
    const catSelect = document.getElementById('specsCatSelect');
    const groupTabs = document.getElementById('specsGroupTabs');
    const tableBody = document.getElementById('specsTableBody');
    const totalCountEl = document.getElementById('specsTotalCount');
    const pageNumEl = document.getElementById('specsPageNum');
    const prevPageBtn = document.getElementById('specsPrevBtn');
    const nextPageBtn = document.getElementById('specsNextBtn');
    
    if (!tableBody) return;

    let currentPage = 1;
    let totalPages = 1;
    let currentGroup = 'all';
    let debounceTimer;

    function syncGroupTabUI(grp) {
        currentGroup = grp;
        if (groupTabs) {
            groupTabs.querySelectorAll('[data-spec-group]').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.specGroup === grp);
            });
        }
    }

    function fetchSpecs(page = 1) {
        currentPage = page;
        const q = searchInput ? searchInput.value.trim() : '';
        const category = catSelect ? catSelect.value : '';

        const curLang = window.getCurrentLanguage ? window.getCurrentLanguage() : 'zh-TW';
        const loadingText = curLang === 'en' ? '🔍 Searching live specifications database...' : curLang === 'ja' ? '🔍 規格データベースを検索中...' : curLang === 'ko' ? '🔍 실시간 규격 데이터베이스 검색 중...' : '🔍 正在檢索官網同步規格資料庫...';
        tableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 30px; color: #94a3b8;">${loadingText}</td></tr>`;

        fetch(`/api/specs?q=${encodeURIComponent(q)}&category=${encodeURIComponent(category)}&group=${encodeURIComponent(currentGroup)}&page=${page}&per_page=25`)
            .then(res => res.json())
            .then(data => {
                totalPages = data.total_pages || 1;
                if (totalCountEl) totalCountEl.textContent = data.total;
                if (pageNumEl) pageNumEl.textContent = `${data.page} / ${totalPages}`;
                
                if (prevPageBtn) prevPageBtn.disabled = data.page <= 1;
                if (nextPageBtn) nextPageBtn.disabled = data.page >= totalPages;

                if (!data.items || data.items.length === 0) {
                    const noResultText = curLang === 'en'
                        ? 'No specifications found matching your criteria. Try switching to "All Specs" or searching for thickness, OD, or alloy (e.g. 5052, 6061, 7075, FT001).'
                        : curLang === 'ja'
                        ? '条件に一致する規格が見つかりません。上の「すべての規格」に切り替えるか、厚み、外径、合金型番で再検索してください。'
                        : curLang === 'ko'
                        ? '조건에 맞는 규격을 찾을 수 없습니다. 상단의 "전체 규격"을 선택하거나 두께, 외경, 합금 모델명으로 검색해 보세요.'
                        : '找不到符合條件的規格，建議切換上方「全部規格」或輸入厚度、外徑、合金型號（如 5052、6061、7075、FT001、PW5168）。';
                    tableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 30px; color: #94a3b8;">${noResultText}</td></tr>`;
                    return;
                }

                tableBody.innerHTML = data.items.map((item, idx) => {
                    const rowNo = item.no || ((data.page - 1) * 25 + idx + 1);
                    const safeSpec = `${item.category} ${item.material} ${item.dimension} ${item.size}`.replace(/\\/g, '\\\\').replace(/'/g, "\\'");
                    const badgeStyle = item.group === 'mold'
                        ? 'background:rgba(53,89,122,0.12); color:#2b4c6b; border-color:rgba(53,89,122,0.3);'
                        : '';
                    const addQuoteText = curLang === 'en' ? 'Add to RFQ' : curLang === 'ja' ? '見積り追加' : curLang === 'ko' ? '견적 추가' : '加入詢價';
                    const categoryDisplay = formatSpecCategory(item.category, curLang);
                    const dimensionDisplay = formatSpecDimension(item.dimension, curLang);
                    const noteDisplay = formatSpecNote(item.note, item.group, curLang);
                    return `
                    <tr class="spec-row-item">
                        <td style="color: var(--accent-cinnabar); font-weight:700;">#${rowNo}</td>
                        <td><span style="font-weight:700; color:var(--text-main);">${categoryDisplay}</span></td>
                        <td><span class="chip" style="color:var(--accent-amber); font-weight:700;">${item.material}</span></td>
                        <td style="font-weight:600; color:var(--text-main);">${dimensionDisplay || '-'}</td>
                        <td>${item.size || '-'}</td>
                        <td class="spec-action-cell">
                            <span class="badge-stock" style="${badgeStyle}">${noteDisplay}</span>
                            <button class="btn-outline spec-quote-btn" style="padding:4px 12px; font-size:0.78rem; margin-left:8px; border-radius:6px;" onclick="addSpecToQuote('${safeSpec}')">${addQuoteText}</button>
                        </td>
                    </tr>`;
                }).join('');
            })
            .catch(err => {
                console.error(err);
                tableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 20px; color:#ef4444;">資料庫讀取失敗</td></tr>`;
            });
    }

    if (groupTabs) {
        groupTabs.querySelectorAll('[data-spec-group]').forEach(btn => {
            btn.addEventListener('click', () => {
                syncGroupTabUI(btn.dataset.specGroup);
                if (catSelect) catSelect.value = '全部';
                fetchSpecs(1);
            });
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => fetchSpecs(1), 260);
        });
    }

    if (catSelect) {
        catSelect.addEventListener('change', () => {
            const val = catSelect.value;
            if (val !== '全部') {
                syncGroupTabUI(val.startsWith('現有模具') ? 'mold' : 'stock');
            }
            fetchSpecs(1);
        });
    }

    if (prevPageBtn) {
        prevPageBtn.addEventListener('click', () => {
            if (currentPage > 1) fetchSpecs(currentPage - 1);
        });
    }

    if (nextPageBtn) {
        nextPageBtn.addEventListener('click', () => {
            if (currentPage < totalPages) fetchSpecs(currentPage + 1);
        });
    }

    // Re-render specs table and category select when language switches
    window.addEventListener('fapo-language-changed', (e) => {
        const lang = e.detail ? e.detail.lang : (window.getCurrentLanguage ? window.getCurrentLanguage() : 'zh-TW');
        updateSpecsCatSelectOptions(lang);
        fetchSpecs(currentPage);
        if (typeof updateWeightShapeInputs === 'function') {
            const s = document.getElementById('wtShapeSelect');
            if (s) updateWeightShapeInputs();
        }
    });

    const initLang = window.getCurrentLanguage ? window.getCurrentLanguage() : 'zh-TW';
    updateSpecsCatSelectOptions(initLang);

    window._setSpecsGroupUI = syncGroupTabUI;
    fetchSpecs(1);
}

window.addSpecToQuote = function(specText) {
    const inquiryMaterial = document.getElementById('inquiryMaterial');
    const inquiryMessage = document.getElementById('inquiryMessage');
    
    if (inquiryMaterial) {
        if (!inquiryMaterial.value.trim()) {
            inquiryMaterial.value = specText;
        } else if (!inquiryMaterial.value.includes(specText)) {
            inquiryMaterial.value += '、' + specText;
        }
    }
    if (inquiryMessage) {
        if (!inquiryMessage.value.trim()) {
            inquiryMessage.value = `您好，我需要詢問以下現貨規格的報價與交期：\n1. 【規格】${specText}\n   【預計數量】1 件\n   【加工需求】精密切割/依指定尺寸`;
        } else {
            inquiryMessage.value += `\n\n+ 【規格】${specText}\n   【預計數量】1 件\n   【加工需求】依指定尺寸`;
        }
    }
    
    if (window.navigateToPage) {
        window.navigateToPage('contact', { scrollTarget: 'quoteFormCard' });
    }
    showToast(`📋 已帶入規格「${specText}」至詢價清單`);
};

window.copyRfqDraft = function() {
    const mat = document.getElementById('inquiryMaterial')?.value || '';
    const msg = document.getElementById('inquiryMessage')?.value || '';
    const comp = document.getElementById('companyName')?.value || '';
    const contact = document.getElementById('contactPerson')?.value || '';
    const phone = document.getElementById('contactPhone')?.value || '';

    const textToCopy = `【賀華實業 RFQ 詢價需求草稿】\n公司：${comp || '未填'}\n聯絡人：${contact || '未填'} (${phone || '未填'})\n材料規格：${mat || '未填'}\n備註與需求：\n${msg || '無'}`;
    navigator.clipboard.writeText(textToCopy).then(() => {
        showToast('📋 已複製詢價需求草稿至剪貼簿！可直接貼至 LINE 或採購單');
    }).catch(() => {
        showToast('請手動選取並複製內容');
    });
};

/* ==========================================================================
   4. Hardness Converter (國際標準金屬硬度對照計算器)
   ========================================================================== */
window.applyHbPreset = function(val) {
    const hbInput = document.getElementById('calcHbInput');
    if (hbInput) {
        hbInput.value = val;
        hbInput.dispatchEvent(new Event('input'));
    }
};

function initHardnessCalculator() {
    const hbInput = document.getElementById('calcHbInput');
    const hrcVal = document.getElementById('calcHrcVal');
    const hrbVal = document.getElementById('calcHrbVal');
    const hvVal = document.getElementById('calcHvVal');
    const shoreVal = document.getElementById('calcShoreVal');
    const tensileVal = document.getElementById('calcTensileVal');

    if (!hbInput || !window.SITE_DATA || !window.SITE_DATA.hardness_data) return;

    const data = window.SITE_DATA.hardness_data;

    function convertHardness(hb) {
        if (isNaN(hb) || hb <= 0) return;

        // Find closest point or interpolate
        let closest = data[0];
        let minDiff = Math.abs(data[0].HB - hb);

        for (let i = 1; i < data.length; i++) {
            const diff = Math.abs(data[i].HB - hb);
            if (diff < minDiff) {
                minDiff = diff;
                closest = data[i];
            }
        }

        if (hrcVal) hrcVal.textContent = closest.HRC !== '-' ? `${closest.HRC} HRC` : '—';
        if (hrbVal) hrbVal.textContent = closest.HRB !== '-' ? `${closest.HRB} HRB` : '—';
        if (hvVal) hvVal.textContent = `${closest.HV} HV`;
        if (shoreVal) shoreVal.textContent = `${closest.shore} HS`;
        if (tensileVal) tensileVal.textContent = `≈ ${closest.tensile_approx} MPa`;
    }

    hbInput.addEventListener('input', (e) => {
        convertHardness(parseFloat(e.target.value));
    });

    convertHardness(parseFloat(hbInput.value) || 229);
}

/* ==========================================================================
   5. Product Filter Tabs & Image Lightbox
   ========================================================================== */
function initProductFilters() {
    const filterBtns = document.querySelectorAll('#products .filter-btn[data-filter]');
    const productCards = document.querySelectorAll('#products .product-card');
    const embossedPanel = document.getElementById('embossedGalleryPanel');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const filter = btn.getAttribute('data-filter');
            productCards.forEach(card => {
                const cat = card.getAttribute('data-category');
                if (filter === 'all' || cat === filter) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });

            if (embossedPanel) {
                embossedPanel.style.display = (filter === 'all' || filter === '鋁合金板材') ? '' : 'none';
            }
        });
    });
}

window.openImageLightbox = function(src, caption) {
    const modal = document.getElementById('imageLightboxModal');
    const img = document.getElementById('lightboxImg');
    const cap = document.getElementById('lightboxCaption');
    if (!modal || !img) return;
    img.src = src;
    if (cap) cap.textContent = caption || '';
    modal.classList.add('open');
};

window.closeImageLightbox = function() {
    const modal = document.getElementById('imageLightboxModal');
    if (modal) modal.classList.remove('open');
};

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        window.closeImageLightbox();
    }
});

window.quickFilterExtrusion = function(filterCat) {
    const catSelect = document.getElementById('specsCatSelect');
    const searchInput = document.getElementById('specsSearchInput');
    const explorerCard = document.getElementById('specsExplorerCard');
    if (filterCat && catSelect) {
        if (searchInput) searchInput.value = '';
        catSelect.value = filterCat;
        catSelect.dispatchEvent(new Event('change'));
        if (explorerCard) {
            explorerCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        showToast(`📐 已切換至「${filterCat}」規格表`);
    }
};

window.quickFilterAlloy = function(alloyCode) {
    const searchInput = document.getElementById('specsSearchInput');
    const catSelect = document.getElementById('specsCatSelect');
    const explorerCard = document.getElementById('specsExplorerCard');
    if (catSelect) {
        catSelect.value = '';
        catSelect.dispatchEvent(new Event('change'));
    }
    if (searchInput) {
        searchInput.value = alloyCode;
        searchInput.dispatchEvent(new Event('input'));
    }
    if (explorerCard) {
        explorerCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    showToast(`🔍 已為您檢索「${alloyCode}」系列現貨與模具規格`);
};

/* ==========================================================================
   6. Contact Form & Quotation Workflow (附圖面拖曳上傳與估價單)
   ========================================================================== */
function initContactForm() {
    const form = document.getElementById('quoteForm');
    if (!form) return;

    // Drawing drag & drop setup
    const dropzone = document.getElementById('drawingDropzone');
    const fileInput = document.getElementById('drawingFileInput');
    const badge = document.getElementById('fileSelectedBadge');
    const fileNameEl = document.getElementById('fileSelectedName');
    const fileSizeEl = document.getElementById('fileSelectedSize');
    const removeBtn = document.getElementById('fileRemoveBtn');

    function updateFileDisplay(file) {
        if (!file) {
            if (badge) badge.style.display = 'none';
            if (fileInput) fileInput.value = '';
            return;
        }
        if (badge) badge.style.display = 'flex';
        if (fileNameEl) fileNameEl.textContent = file.name;
        if (fileSizeEl) {
            const kb = (file.size / 1024).toFixed(1);
            fileSizeEl.textContent = file.size > 1048576 ? `(${(file.size / 1048576).toFixed(2)} MB)` : `(${kb} KB)`;
        }
    }

    if (fileInput) {
        fileInput.addEventListener('change', () => {
            if (fileInput.files && fileInput.files[0]) {
                updateFileDisplay(fileInput.files[0]);
            }
        });
    }

    if (removeBtn) {
        removeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            updateFileDisplay(null);
        });
    }

    if (dropzone) {
        ['dragenter', 'dragover'].forEach(evt => {
            dropzone.addEventListener(evt, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add('dragover');
            });
        });
        ['dragleave', 'drop'].forEach(evt => {
            dropzone.addEventListener(evt, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove('dragover');
            });
        });
        dropzone.addEventListener('drop', (e) => {
            if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]) {
                fileInput.files = e.dataTransfer.files;
                updateFileDisplay(e.dataTransfer.files[0]);
            }
        });
    }

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '送出中...';
        submitBtn.disabled = true;

        const formData = new FormData(form);

        fetch('/api/contact', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
            if (data.success) {
                showSuccessModal(data.ticket_id, data.message);
                form.reset();
                updateFileDisplay(null);
            } else {
                showToast("送出失敗：" + (data.error || '未預期錯誤'));
            }
        })
        .catch(err => {
            console.error(err);
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
            showToast("網路錯誤，請稍後再試或致電各廠區");
        });
    });
}

function showSuccessModal(ticketId, message) {
    const modal = document.getElementById('successModal');
    const modalMsg = document.getElementById('modalMessage');
    const modalTicket = document.getElementById('modalTicket');
    const pdfBtn = document.getElementById('modalPrintPdfBtn');
    if (modal) {
        if (modalMsg) modalMsg.textContent = message;
        if (modalTicket) modalTicket.textContent = `諮詢單號：${ticketId}`;
        if (pdfBtn) {
            pdfBtn.href = `/quotation/${encodeURIComponent(ticketId)}`;
        }
        modal.classList.add('open');
    }
}

window.closeModal = function() {
    const modal = document.getElementById('successModal');
    if (modal) modal.classList.remove('open');
};

/* ==========================================================================
   7. Seamless Multi-Page SPA Router (無縫分頁切換與獨立網址引擎)
   ========================================================================== */
const PORTAL_PAGES = [
    { id: 'hero', path: '/', short: '首頁總覽', label: '首頁總覽' },
    { id: 'about', path: '/about', short: '關於我們', label: '關於我們 · 成立概要與願景' },
    { id: 'network', path: '/network', short: '服務網絡', label: '全台北中南服務網絡' },
    { id: 'products', path: '/products', short: '旗艦材料', label: '精選旗艦材料與壓花板圖鑑' },
    { id: 'specs', path: '/specs', short: '現貨規格', label: '現貨規格與現有模具檢索' },
    { id: 'machining', path: '/machining', short: '精密加工', label: '高階精密加工與實品圖鑑' },
    { id: 'cases', path: '/cases', short: '代表實績', label: '半導體與航太代表實績' },
    { id: 'tech', path: '/tech', short: '技術硬度', label: '國際硬度換算與熱處理辭典' },
    { id: 'contact', path: '/contact', short: '聯絡諮詢', label: '即時諮詢與線上圖面估價' }
];

window.CURRENT_PAGE_ID = 'hero';

window.getPageLabel = function(pageId, type = 'label') {
    const lang = window.getCurrentLanguage ? window.getCurrentLanguage() : 'zh-TW';
    const dict = {
        'zh-TW': {
            'hero': { short: '首頁', label: '首頁總覽' },
            'about': { short: '關於我們', label: '關於我們 · 成立概要與願景' },
            'network': { short: '服務網絡', label: '全台北中南服務網絡' },
            'products': { short: '旗艦材料', label: '精選旗艦材料與壓花板圖鑑' },
            'specs': { short: '現貨規格', label: '現貨規格與現有模具檢索' },
            'machining': { short: '精密加工', label: '高階精密加工與實品圖鑑' },
            'cases': { short: '代表實績', label: '半導體與航太代表實績' },
            'tech': { short: '技術硬度', label: '國際硬度換算與熱處理辭典' },
            'contact': { short: '聯絡諮詢', label: '即時諮詢與線上圖面估價' }
        },
        'en': {
            'hero': { short: 'Home', label: 'Home Overview' },
            'about': { short: 'About Us', label: 'About HARVARD · History & Vision' },
            'network': { short: 'Network', label: 'Nationwide Logistics & Branches' },
            'products': { short: 'Materials', label: 'Flagship Aluminum & Alloys' },
            'specs': { short: 'Stock Specs', label: 'Inventory & Mold Specs Explorer' },
            'machining': { short: 'Machining', label: 'High-End Precision Machining' },
            'cases': { short: 'Case Studies', label: 'Track Record & Industry Cases' },
            'tech': { short: 'Tech Hub', label: 'Hardness Conversion & Temper Dict' },
            'contact': { short: 'Contact Us', label: 'Direct Inquiry & Online RFQ' }
        },
        'ja': {
            'hero': { short: 'ホーム', label: 'ホーム概要' },
            'about': { short: '会社概要', label: '会社概要 · 沿革と将来ビジョン' },
            'network': { short: '拠点網', label: '台湾全域サービス物流拠点' },
            'products': { short: '旗艦材料', label: '厳選旗艦アルミニウム材料' },
            'specs': { short: '在庫規格', label: '常備在庫・金型スペック検索' },
            'machining': { short: '精密加工', label: '高度精密加工・表面エンジニアリング' },
            'cases': { short: '実績紹介', label: '半導体・航空宇宙主要実績' },
            'tech': { short: '技術硬度', label: '国際硬度換算と調質記号辞書' },
            'contact': { short: 'お問い合わせ', label: 'お問い合わせ・オンライン見積り' }
        },
        'ko': {
            'hero': { short: '홈', label: '홈 개요' },
            'about': { short: '회사소개', label: '회사소개 · 연혁 및 비전' },
            'network': { short: '거점망', label: '대만 전국 물류 및 서비스 거점' },
            'products': { short: '주요소재', label: '엄선된 주요 알루미늄 합금' },
            'specs': { short: '재고규격', label: '재고 규격 및 보유 금형 검색' },
            'machining': { short: '정밀가공', label: '초정밀 가공 및 표면처리' },
            'cases': { short: '대표실적', label: '반도체 및 항공우주 주요실적' },
            'tech': { short: '기술지식', label: '국제 경도 환산 및 조질 기호 사전' },
            'contact': { short: '문의하기', label: '실시간 상담 및 온라인 견적' }
        }
    };
    const langDict = dict[lang] || dict['zh-TW'];
    return (langDict[pageId] && langDict[pageId][type]) || pageId;
};

window.updateSubpageCrumbAndPager = function(pageId) {
    const crumbLabel = document.getElementById('subpageCrumbLabel');
    const prevBtn = document.getElementById('pagerPrevBtn');
    const nextBtn = document.getElementById('pagerNextBtn');
    const curLang = window.getCurrentLanguage ? window.getCurrentLanguage() : 'zh-TW';

    const idx = PORTAL_PAGES.findIndex(p => p.id === pageId);
    const safeIdx = idx >= 0 ? idx : 0;
    const page = PORTAL_PAGES[safeIdx];

    if (crumbLabel) {
        crumbLabel.textContent = window.getPageLabel(pageId, 'label');
    }

    if (prevBtn && nextBtn) {
        const prevPage = PORTAL_PAGES[safeIdx - 1] || PORTAL_PAGES[0];
        const nextPage = PORTAL_PAGES[safeIdx + 1] || PORTAL_PAGES[3];

        const prevShort = window.getPageLabel(prevPage.id, 'short');
        const nextShort = window.getPageLabel(nextPage.id, 'short');

        prevBtn.href = prevPage.path;
        prevBtn.setAttribute('data-nav-page', prevPage.id);
        if (prevPage.id === 'hero') {
            prevBtn.textContent = curLang === 'en' ? '← Back to Home' : curLang === 'ja' ? '← ホーム概要に戻る' : curLang === 'ko' ? '← 홈으로 돌아가기' : '← 返回首頁總覽';
        } else {
            prevBtn.textContent = curLang === 'en' ? `← Previous: ${prevShort}` : curLang === 'ja' ? `← 前へ：${prevShort}` : curLang === 'ko' ? `← 이전：${prevShort}` : `← 上一頁：${prevPage.short}`;
        }

        nextBtn.href = nextPage.path;
        nextBtn.setAttribute('data-nav-page', nextPage.id);
        nextBtn.textContent = curLang === 'en' ? `Next: ${nextShort} →` : curLang === 'ja' ? `次へ：${nextShort} →` : curLang === 'ko' ? `다음：${nextShort} →` : `下一頁：${nextPage.short} →`;
    }
};

function initPageRouter() {
    // Disable browser aggressive scroll restoration on refresh so user always starts cleanly from page top
    if ('scrollRestoration' in history) {
        try { history.scrollRestoration = 'manual'; } catch (e) {}
    }

    function resolveFromUrl() {
        const hashId = (window.location.hash || '').replace(/^#/, '').trim();
        if (hashId && PORTAL_PAGES.some(p => p.id === hashId)) {
            return { pageId: hashId, replaceUrl: true };
        }
        const cleanPath = (window.location.pathname || '/').replace(/\/+$/, '') || '/';
        const matched = PORTAL_PAGES.find(p => p.path === cleanPath);
        if (matched) {
            return { pageId: matched.id, replaceUrl: false };
        }
        return { pageId: window.INITIAL_PAGE || 'hero', replaceUrl: false };
    }

    window.navigateToPage = function(targetId, opts = {}) {
        const idx = PORTAL_PAGES.findIndex(p => p.id === targetId);
        const safeIdx = idx >= 0 ? idx : 0;
        const page = PORTAL_PAGES[safeIdx];
        const pageId = page.id;

        // 1. Toggle active page view cleanly
        document.querySelectorAll('.page-view').forEach(sec => {
            const isMatch = sec.getAttribute('data-page-view') === pageId;
            sec.classList.toggle('active-page', isMatch);
        });

        // 2. Sync active state across navbar, mobile drawer, and subpage pill strip
        document.querySelectorAll('.nav-item[data-nav-page], .mobile-nav-link[data-nav-page], .subpage-pill[data-nav-page]').forEach(el => {
            el.classList.toggle('active', el.getAttribute('data-nav-page') === pageId);
        });

        // 3. Center active pill horizontally inside subpage strip without affecting vertical scroll
        const strip = document.getElementById('subpagePillStrip');
        const activePill = strip ? strip.querySelector(`.subpage-pill[data-nav-page="${pageId}"]`) : null;
        if (strip && activePill) {
            const targetLeft = activePill.offsetLeft - (strip.clientWidth / 2) + (activePill.offsetWidth / 2);
            strip.scrollTo({ left: Math.max(0, targetLeft), behavior: 'smooth' });
        }

        // 4. Update subpage breadcrumb & sequential bottom pager
        const isSubpage = pageId !== 'hero';
        const topBar = document.getElementById('subpageTopBar');
        const pagerBar = document.getElementById('subpagePagerBar');

        if (topBar) topBar.classList.toggle('visible', isSubpage);
        if (pagerBar) pagerBar.classList.toggle('visible', isSubpage);

        window.CURRENT_PAGE_ID = pageId;
        window.updateSubpageCrumbAndPager(pageId);

        // 5. Push or replace clean URL in browser history
        if (!opts.skipHistory) {
            const currentClean = (window.location.pathname || '/').replace(/\/+$/, '') || '/';
            if (opts.replace) {
                window.history.replaceState({ pageId }, document.title, page.path);
            } else if (currentClean !== page.path || window.location.hash) {
                window.history.pushState({ pageId }, document.title, page.path);
            }
        }

        // 6. Close mobile drawer if open
        if (window.closeMobileMenu) {
            window.closeMobileMenu();
        }

        // 7. Scroll to top or specific target element
        if (opts.scrollTarget) {
            requestAnimationFrame(() => {
                const targetEl = document.getElementById(opts.scrollTarget);
                if (targetEl) {
                    targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
                } else {
                    window.scrollTo({ top: 0, behavior: 'auto' });
                }
            });
        } else if (!opts.preserveScroll) {
            window.scrollTo({ top: 0, behavior: 'auto' });
        }
    };

    // Intercept internal [data-nav-page] clicks for 0ms SPA transition
    document.addEventListener('click', (e) => {
        const link = e.target.closest('[data-nav-page]');
        if (!link) return;
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || (typeof e.button === 'number' && e.button !== 0)) {
            return;
        }
        e.preventDefault();
        const targetId = link.getAttribute('data-nav-page');
        window.navigateToPage(targetId);
    });

    // Support browser Back / Forward buttons seamlessly
    window.addEventListener('popstate', (e) => {
        const stateId = e.state && e.state.pageId;
        const resolved = stateId || resolveFromUrl().pageId;
        window.navigateToPage(resolved, { skipHistory: true });
    });

    // Initial hydration (handles direct URLs AND legacy #hash links)
    const initial = resolveFromUrl();
    window.navigateToPage(initial.pageId, {
        replace: initial.replaceUrl,
        skipHistory: !initial.replaceUrl,
        preserveScroll: false
    });
}

/* ==========================================================================
   8. Cloudflare Tunnel Management
   ========================================================================== */
window.openTunnelModal = function() {
    const modal = document.getElementById('tunnelModal');
    if (modal) modal.classList.add('open');
    checkTunnelStatus();
};

window.closeTunnelModal = function() {
    const modal = document.getElementById('tunnelModal');
    if (modal) modal.classList.remove('open');
};

function checkTunnelStatus() {
    const input = document.getElementById('tunnelUrlInput');
    const openLink = document.getElementById('tunnelOpenLink');
    if (!input) return;

    input.value = "連線狀態檢測中...";

    fetch('/api/tunnel-status')
        .then(res => res.json())
        .then(data => {
            if (data.running && data.url) {
                input.value = data.url;
                if (openLink) {
                    openLink.href = data.url;
                    openLink.style.display = 'inline-flex';
                }
            } else {
                input.value = "尚未建立穿透，請點擊下方按鈕建立";
                if (openLink) openLink.style.display = 'none';
            }
        })
        .catch(() => {
            input.value = "無法取得 Tunnel 狀態";
        });
}

window.toggleTunnelAction = function() {
    const input = document.getElementById('tunnelUrlInput');
    const btn = document.getElementById('btnToggleTunnel');
    const openLink = document.getElementById('tunnelOpenLink');

    if (input) input.value = "正在自動調用 cloudflared 穿透中...";
    if (btn) {
        btn.innerHTML = "⏳ 正在與 Cloudflare 連線中...";
        btn.disabled = true;
    }

    fetch('/api/tunnel/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ port: 5000 })
    })
    .then(res => res.json())
    .then(data => {
        if (btn) {
            btn.innerHTML = "⚡ 重新取得外網網址";
            btn.disabled = false;
        }
        if (data.success && data.url) {
            if (input) input.value = data.url;
            if (openLink) {
                openLink.href = data.url;
                openLink.style.display = 'inline-flex';
            }
            showToast("🌐 Cloudflare Tunnel 已就緒！");
        } else {
            if (input) input.value = "建立失敗：" + (data.error || '請檢查網路連線');
            showToast("穿透建立失敗");
        }
    })
    .catch(err => {
        if (btn) {
            btn.innerHTML = "⚡ 建立 / 重新取得外網網址";
            btn.disabled = false;
        }
        if (input) input.value = "網路請求失敗";
        showToast("伺服器請求超時");
    });
};

window.copyTunnelUrl = function() {
    const input = document.getElementById('tunnelUrlInput');
    if (!input || !input.value.startsWith('http')) {
        showToast("尚無有效的公開網址可供複製");
        return;
    }
    navigator.clipboard.writeText(input.value).then(() => {
        showToast("📋 已複製 Cloudflare 公開網址到剪貼簿！");
    }).catch(() => {
        input.select();
        document.execCommand('copy');
        showToast("📋 已複製！");
    });
};

function showToast(msg) {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = msg;
    container.appendChild(toast);
    setTimeout(() => {
        toast.remove();
    }, 3500);
}


/* ==========================================================================
   HARVARD AI Customer Service & Google OR-Tools CP-SAT Interactive Client
   ========================================================================== */

window.toggleAiChatWidget = function(forceState) {
    const widget = document.getElementById('aiChatWidget');
    const launcher = document.getElementById('aiChatLauncher');
    if (!widget) return;
    if (typeof forceState === 'boolean') {
        if (forceState) widget.classList.add('open');
        else widget.classList.remove('open');
    } else {
        widget.classList.toggle('open');
    }
    const isOpen = widget.classList.contains('open');
    if (launcher) launcher.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    if (isOpen) {
        const inp = document.getElementById('aiChatInput');
        if (inp) setTimeout(() => inp.focus(), 150);
        const box = document.getElementById('aiChatMessages');
        if (box) setTimeout(() => { box.scrollTop = box.scrollHeight; }, 100);
    }
};

// Global escape key listener to close AI Chat Widget gracefully
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' || e.keyCode === 27) {
        const widget = document.getElementById('aiChatWidget');
        if (widget && widget.classList.contains('open')) {
            window.toggleAiChatWidget(false);
        }
    }
});

window.switchAiMode = function(mode) {
    const btnChat = document.getElementById('aiTabBtnChat');
    const btnCpsat = document.getElementById('aiTabBtnCpsat');
    const panelChat = document.getElementById('aiPanelChat');
    const panelCpsat = document.getElementById('aiPanelCpsat');
    if (!panelChat || !panelCpsat) return;

    if (mode === 'cpsat') {
        btnChat.classList.remove('active');
        btnCpsat.classList.add('active');
        panelChat.style.display = 'none';
        panelCpsat.style.display = 'flex';
    } else {
        btnCpsat.classList.remove('active');
        btnChat.classList.add('active');
        panelCpsat.style.display = 'none';
        panelChat.style.display = 'flex';
    }
};

function formatAiMarkdown(text) {
    return String(text || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/`([^`]+)`/g, '<code style="background:rgba(182,59,46,0.1);color:var(--accent-cinnabar);padding:1px 5px;border-radius:4px;font-weight:700;">$1</code>')
        .replace(/\n/g, '<br>');
}

window.sendAiQuickPrompt = function(promptText) {
    const inp = document.getElementById('aiChatInput');
    if (inp) {
        inp.value = promptText;
        sendAiChatMessage();
    }
};

window.sendAiChatMessage = function() {
    const inp = document.getElementById('aiChatInput');
    const box = document.getElementById('aiChatMessages');
    if (!inp || !box) return;

    const text = inp.value.trim();
    if (!text) return;
    inp.value = '';

    // Append user bubble
    const userDiv = document.createElement('div');
    userDiv.className = 'ai-msg ai-msg-user';
    userDiv.innerHTML = `<div class="ai-msg-bubble">${formatAiMarkdown(text)}</div>`;
    box.appendChild(userDiv);
    box.scrollTop = box.scrollHeight;

    // Append loading bubble
    const botDiv = document.createElement('div');
    botDiv.className = 'ai-msg ai-msg-bot';
    botDiv.innerHTML = `<div class="ai-msg-bubble">⏳ 正在智慧檢索規格與計算最佳方案...</div>`;
    box.appendChild(botDiv);
    box.scrollTop = box.scrollHeight;

    const currentLang = window.getCurrentLanguage ? window.getCurrentLanguage() : 'zh-TW';
    fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, lang: currentLang })
    })
    .then(r => r.json())
    .then(data => {
        let html = `<div class="ai-msg-bubble">${formatAiMarkdown(data.reply || '')}`;

        if (data.specs && data.specs.length > 0) {
            html += `<div class="ai-spec-cards">`;
            data.specs.forEach(s => {
                const safeSpec = `${s.category} ${s.material} ${s.dimension || ''} ${s.size || ''}`.replace(/'/g, "\'");
                html += `
                    <div class="ai-spec-mini-card">
                        <div class="ai-spec-mini-info">
                            <strong>${s.material} · ${s.dimension || '-'}</strong>
                            <span>${s.category} (${s.size || '常備規格'})</span>
                        </div>
                        <button type="button" class="ai-spec-mini-btn" onclick="addSpecToQuote('${safeSpec}')">＋詢價</button>
                    </div>
                `;
            });
            html += `</div>`;
        }

        if (data.cutting_plan && data.cutting_plan.success) {
            const p = data.cutting_plan;
            const quoteSummary = `[最佳化裁切需求] 母材 ${p.stock_length_mm}mm 共需 ${p.total_bars_used} 支 (利用率 ${p.overall_utilization_pct}%): ` +
                p.bars_plan.map(b => `第${b.bar_no}支(${b.cuts_summary})`).join('；');
            const safeQuote = quoteSummary.replace(/'/g, "\'");
            html += `
                <div style="margin-top:10px;">
                    <button type="button" class="ai-spec-mini-btn" style="width:100%;padding:7px;" onclick="addSpecToQuote('${safeQuote}')">
                        📋 將此最佳裁切方案加入詢價單
                    </button>
                </div>
            `;
        }

        const voiceText = data.voice_script || (data.reply || '').replace(/[*`#|•📍✅📦🧮📋💡☎️]/g, '').replace(/\[.*?\]\(.*?\)/g, '').trim().substring(0, 300);
        const safeVoiceText = voiceText.replace(/'/g, "\\'").replace(/"/g, '&quot;').replace(/\n/g, ' ');
        html += `
            <div style="margin-top:8px;">
                <button type="button" class="ai-bubble-audio-btn" onclick="readAloudText('${safeVoiceText}', this)" title="播放擬人化語音解說">
                    🔊 聽取 AI 語音解說
                </button>
            </div>
        `;

        html += `</div>`;
        botDiv.innerHTML = html;
        box.scrollTop = box.scrollHeight;
    })
    .catch(() => {
        botDiv.innerHTML = `<div class="ai-msg-bubble">⚠️ 連線發生異常，請稍後再試。</div>`;
    });
};

window.addCpsatDemandRow = function() {
    const list = document.getElementById('cpsatDemandList');
    if (!list) return;
    const row = document.createElement('div');
    row.className = 'cpsat-demand-row';
    row.innerHTML = `
        <input type="number" class="cpsat-len-input" value="500" placeholder="長度 mm" min="10">
        <span>×</span>
        <input type="number" class="cpsat-qty-input" value="2" placeholder="支數" min="1">
        <button type="button" class="cpsat-del-btn" onclick="this.parentElement.remove()">✕</button>
    `;
    list.appendChild(row);
};

window.runInteractiveCpsatSolver = function() {
    const stockLen = parseInt(document.getElementById('cpsatStockLen')?.value || '3000', 10);
    const kerf = parseInt(document.getElementById('cpsatKerf')?.value || '3', 10);
    const rows = document.querySelectorAll('#cpsatDemandList .cpsat-demand-row');
    const resBox = document.getElementById('cpsatResultBox');
    const solveBtn = document.getElementById('cpsatSolveBtn');

    if (!resBox) return;

    const demands = [];
    rows.forEach(r => {
        const l = parseInt(r.querySelector('.cpsat-len-input')?.value || '0', 10);
        const q = parseInt(r.querySelector('.cpsat-qty-input')?.value || '0', 10);
        if (l > 0 && q > 0) demands.push({ length: l, qty: q });
    });

    resBox.style.display = 'block';
    resBox.innerHTML = `⏳ 正在執行最佳化下料運算...`;
    if (solveBtn) solveBtn.disabled = true;

    fetch('/api/ai/cutting-stock', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            stock_length_mm: stockLen,
            kerf_mm: kerf,
            demands: demands
        })
    })
    .then(r => r.json())
    .then(plan => {
        if (solveBtn) solveBtn.disabled = false;
        if (!plan.success) {
            resBox.innerHTML = `<div style="color:#b91c1c;font-weight:700;">❌ ${plan.error || '求解失敗'}</div>`;
            return;
        }

        let barsHtml = '';
        const colorPalette = ['#b83b26', '#1d4ed8', '#059669', '#d97706', '#7c3aed', '#0891b2', '#c026d3'];

        plan.bars_plan.forEach(b => {
            const stockL = plan.stock_length_mm;
            let svgElements = '';
            
            // Background track representing the mother standard bar
            svgElements += `<rect x="0" y="2" width="1000" height="38" rx="4" fill="#07142c" stroke="#1e3a5f" stroke-width="1.2" />`;

            if (b.segments && b.segments.length > 0) {
                b.segments.forEach(seg => {
                    const x = (seg.start_mm / stockL) * 1000;
                    const w = Math.max(1.2, (seg.length_mm / stockL) * 1000);
                    if (seg.type === 'piece') {
                        const col = colorPalette[Math.abs(seg.length_mm * 11 + seg.index) % colorPalette.length];
                        svgElements += `
                            <g class="cpsat-svg-piece">
                                <rect x="${x.toFixed(1)}" y="4" width="${w.toFixed(1)}" height="34" rx="2" fill="${col}">
                                    <title>工件 #${seg.index}：長度 ${seg.length_mm} mm (位置 ${seg.start_mm} ~ ${seg.end_mm} mm)</title>
                                </rect>
                                ${w > 36 ? `<text x="${(x + w/2).toFixed(1)}" y="25" fill="#ffffff" font-size="11" font-weight="700" text-anchor="middle" pointer-events="none">${seg.length_mm}</text>` : ''}
                            </g>
                        `;
                    } else if (seg.type === 'kerf') {
                        const kw = Math.max(1.8, w);
                        svgElements += `
                            <rect x="${x.toFixed(1)}" y="2" width="${kw.toFixed(1)}" height="38" fill="#ef4444">
                                <title>鋸縫損耗：${seg.length_mm} mm</title>
                            </rect>
                        `;
                    } else if (seg.type === 'remnant') {
                        svgElements += `
                            <g class="cpsat-svg-remnant">
                                <rect x="${x.toFixed(1)}" y="4" width="${w.toFixed(1)}" height="34" rx="2" fill="rgba(148,163,184,0.2)" stroke="#94a3b8" stroke-dasharray="3,2">
                                    <title>可用餘料：${seg.length_mm} mm (${((seg.length_mm / stockL) * 100).toFixed(1)}%)</title>
                                </rect>
                                ${w > 45 ? `<text x="${(x + w/2).toFixed(1)}" y="25" fill="#475569" font-size="10" font-weight="700" text-anchor="middle" pointer-events="none">餘 ${seg.length_mm}mm</text>` : ''}
                            </g>
                        `;
                    }
                });
            } else {
                let segsHtml = '';
                b.cuts.forEach((c, idx) => {
                    const pct = Math.max(8, Math.round(((c.length * c.count) / plan.stock_length_mm) * 100));
                    const bgColors = ['#a83327', '#b87b28', '#2b5b84', '#3d7a5a'];
                    const bg = bgColors[idx % bgColors.length];
                    segsHtml += `<div class="cpsat-seg" style="width:${pct}%;background:${bg};" title="${c.label}">${c.length}×${c.count}</div>`;
                });
                if (b.remnant_mm > 0) {
                    const remPct = Math.max(6, Math.round((b.remnant_mm / plan.stock_length_mm) * 100));
                    segsHtml += `<div class="cpsat-seg-rem" style="width:${remPct}%;" title="餘料 ${b.remnant_mm}mm">餘${b.remnant_mm}</div>`;
                }
                svgElements = segsHtml;
            }

            barsHtml += `
                <div style="margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;font-weight:700;font-size:0.78rem;margin-bottom:3px;">
                        <span>母材 #${b.bar_no}：${b.cuts_summary}</span>
                        <span style="color:var(--accent-cinnabar);background:rgba(182,59,46,0.08);padding:2px 6px;border-radius:4px;">利用率 ${b.utilization_pct}% (餘 ${b.remnant_mm}mm)</span>
                    </div>
                    <div class="cpsat-svg-wrap">
                        <svg class="cpsat-svg-bar" viewBox="0 0 1000 44" preserveAspectRatio="none">
                            ${svgElements}
                        </svg>
                        <div style="display:flex;justify-content:space-between;font-size:9px;color:#94a3b8;font-family:monospace;margin-top:2px;padding:0 2px;">
                            <span>0 mm</span>
                            <span style="color:#ef4444;">紅線: 鋸縫 ${plan.kerf_mm}mm</span>
                            <span>${stockL} mm (滿料)</span>
                        </div>
                    </div>
                </div>
            `;
        });

        const quoteSummary = `[最佳化裁切需求] 母材 ${plan.stock_length_mm}mm 共需 ${plan.total_bars_used} 支 (利用率 ${plan.overall_utilization_pct}%): ` +
            plan.bars_plan.map(b => `第${b.bar_no}支(${b.cuts_summary})`).join('；');
        const safeQuote = quoteSummary.replace(/'/g, "\'");

        const speechComm = plan.speech_commentary || `母材 ${plan.stock_length_mm}mm 最少需用 ${plan.total_bars_used} 支，材料利用率達 ${plan.overall_utilization_pct}%。`;
        const safeCommentary = speechComm.replace(/'/g, "\\'").replace(/"/g, '&quot;').replace(/\n/g, ' ');

        resBox.innerHTML = `
            <div style="margin-bottom:10px;border-bottom:1px solid rgba(180,160,120,0.35);padding-bottom:8px;">
                <div style="font-weight:800;color:var(--accent-cinnabar);font-size:0.86rem;">
                    ✅ ${plan.solver_status}（耗時 ${plan.solve_time_ms} ms）
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:6px;">
                    <div>最少需用母材：<strong>${plan.total_bars_used} 支</strong></div>
                    <div>總材料利用率：<strong>${plan.overall_utilization_pct}%</strong></div>
                    <div>總裁切段數：<strong>${plan.total_pieces_cut} 支</strong></div>
                    <div>總餘料長度：<strong>${plan.total_remnant_mm} mm</strong></div>
                </div>
            </div>
            <button type="button" class="ai-bubble-audio-btn" style="width:100%;justify-content:center;padding:8px;background:var(--accent-cinnabar);color:#ffffff;border-color:var(--accent-cinnabar);font-size:0.8rem;margin-bottom:10px;" onclick="readAloudText('${safeCommentary}', this)">
                🔊 聽取 AI 工程師解說排版方案
            </button>
            ${barsHtml}
            <div style="display:flex;flex-direction:column;gap:6px;margin-top:8px;">
                <button type="button" class="ai-spec-mini-btn" style="width:100%;padding:8px;" onclick="addSpecToQuote('${safeQuote}')">
                    📋 將此最佳裁切明細帶入詢價單
                </button>
                <button type="button" class="ai-spec-mini-btn" style="width:100%;padding:8px;background:#1e293b;color:#ffffff;" onclick="window.open('/quotation/preview?material=' + encodeURIComponent('母材 ${plan.stock_length_mm}mm 定寸最佳化裁切方案 (${plan.total_bars_used} 支)') + '&message=' + encodeURIComponent('${safeQuote}') + '&qty=${plan.total_bars_used}', '_blank')">
                    📄 匯出此裁切工單 (PDF / 列印)
                </button>
            </div>
        `;
    })
    .catch(() => {
        if (solveBtn) solveBtn.disabled = false;
        resBox.innerHTML = `<div style="color:#b91c1c;">⚠️ 求解器連線異常</div>`;
    });
};

/* ==========================================================================
   AI Voice Speech Recognition (語音輸入與對話模式)
   ========================================================================== */
let aiSpeechRecognition = null;
let isAiListening = false;

window.toggleAiVoiceRecognition = function() {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    const btn = document.getElementById('aiVoiceInputBtn');
    const input = document.getElementById('aiChatInput');

    if (!SpeechRec) {
        showToast("您的瀏覽器暫未支援語音辨識，請使用文字鍵盤輸入。");
        return;
    }

    if (isAiListening && aiSpeechRecognition) {
        aiSpeechRecognition.stop();
        return;
    }

    try {
        aiSpeechRecognition = new SpeechRec();
        const curLang = (window.getCurrentLanguage ? window.getCurrentLanguage() : 'zh-TW');
        const langMap = { 'zh-TW': 'zh-TW', 'en': 'en-US', 'ja': 'ja-JP', 'ko': 'ko-KR' };
        aiSpeechRecognition.lang = langMap[curLang] || 'zh-TW';
        aiSpeechRecognition.continuous = false;
        aiSpeechRecognition.interimResults = true;

        aiSpeechRecognition.onstart = function() {
            isAiListening = true;
            if (btn) btn.classList.add('listening');
            if (input) input.placeholder = '🎙️ 正在聆聽，請說出規格或裁切尺寸...';
        };

        aiSpeechRecognition.onresult = function(e) {
            let transcript = '';
            for (let i = e.resultIndex; i < e.results.length; ++i) {
                transcript += e.results[i][0].transcript;
            }
            if (input) input.value = transcript;
        };

        aiSpeechRecognition.onerror = function(e) {
            console.warn('Speech rec error:', e);
            if (btn) btn.classList.remove('listening');
            isAiListening = false;
            if (input) input.placeholder = '輸入或以語音說出規格需求、裁切尺寸...';
        };

        aiSpeechRecognition.onend = function() {
            isAiListening = false;
            if (btn) btn.classList.remove('listening');
            if (input) {
                input.placeholder = '輸入或以語音說出規格需求、裁切尺寸...';
                if (input.value.trim().length > 0) {
                    sendAiChatMessage();
                }
            }
        };

        aiSpeechRecognition.start();
    } catch (err) {
        console.error('Failed to start speech rec:', err);
        if (btn) btn.classList.remove('listening');
        isAiListening = false;
        showToast("啟動麥克風失敗，請確認已授權瀏覽器麥克風權限");
    }
};


/* ==========================================================================
   Industrial Metal Weight & Volume Calculator
   ========================================================================== */

window.applyRoundBarPreset = function(dia, len) {
    const d1Input = document.getElementById('wtDim1');
    const lenInput = document.getElementById('wtLength');
    if (d1Input) d1Input.value = dia;
    if (lenInput && len) lenInput.value = len;
    calculateMetalWeight();
};

window.applyLengthPreset = function(len) {
    const lenInput = document.getElementById('wtLength');
    if (lenInput) lenInput.value = len;
    calculateMetalWeight();
};

window.updateWeightShapeInputs = function() {
    const shape = document.getElementById('wtShapeSelect')?.value || 'plate';
    const d1Wrap = document.getElementById('wtDim1Wrap');
    const d2Wrap = document.getElementById('wtDim2Wrap');
    const d3Wrap = document.getElementById('wtDim3Wrap');
    const d1Label = document.getElementById('wtDim1Label');
    const d2Label = document.getElementById('wtDim2Label');
    const d3Label = document.getElementById('wtDim3Label');
    const d1Input = document.getElementById('wtDim1');
    const d2Input = document.getElementById('wtDim2');
    const d3Input = document.getElementById('wtDim3');
    const lenInput = document.getElementById('wtLength');
    const presetRow = document.getElementById('wtPresetRow');
    const formulaDesc = document.getElementById('wtFormulaDesc');

    if (!d1Wrap || !d2Wrap || !d3Wrap) return;

    if (shape === 'plate') {
        d1Label.innerHTML = '<span data-i18n="calc_lbl_t">厚度 T (mm)：</span>';
        d2Wrap.style.display = '';
        d2Label.innerHTML = '<span data-i18n="calc_lbl_w">寬度 W (mm)：</span>';
        d3Wrap.style.display = 'none';
        if (presetRow) {
            presetRow.style.display = 'flex';
            presetRow.innerHTML = `
                <span style="font-size: 0.78rem; color: var(--text-muted); align-self: center;" data-i18n="calc_lbl_presets">常用板規快選：</span>
                <button type="button" class="cpsat-add-btn" onclick="applyPlatePreset(1220, 2440)">4'×8' (1220×2440)</button>
                <button type="button" class="cpsat-add-btn" onclick="applyPlatePreset(914, 1829)">3'×6' (914×1829)</button>
                <button type="button" class="cpsat-add-btn" onclick="applyPlatePreset(1524, 3048)">5'×10' (1524×3048)</button>
                <button type="button" class="cpsat-add-btn" onclick="applyPlatePreset(1000, 2000)">1m×2m (1000×2000)</button>
            `;
        }
        if (formulaDesc) formulaDesc.innerHTML = '<span data-i18n="calc_formula_plate">計算公式：厚(mm) × 寬(mm) × 長(mm) × 比重 ÷ 1,000,000</span>';
    } else if (shape === 'round_bar') {
        d1Label.innerHTML = '<span data-i18n="calc_lbl_dia">外徑 D (mm)：</span>';
        d1Input.value = '50';
        lenInput.value = '3000';
        d2Wrap.style.display = 'none';
        d3Wrap.style.display = 'none';
        if (presetRow) {
            presetRow.style.display = 'flex';
            presetRow.innerHTML = `
                <span style="font-size: 0.78rem; color: var(--text-muted); align-self: center;" data-i18n="calc_lbl_bar_presets">常用棒徑快選：</span>
                <button type="button" class="cpsat-add-btn" onclick="applyRoundBarPreset(20, 1000)">Ø20</button>
                <button type="button" class="cpsat-add-btn" onclick="applyRoundBarPreset(30, 1000)">Ø30</button>
                <button type="button" class="cpsat-add-btn" onclick="applyRoundBarPreset(50, 1000)">Ø50</button>
                <button type="button" class="cpsat-add-btn" onclick="applyRoundBarPreset(80, 1000)">Ø80</button>
                <button type="button" class="cpsat-add-btn" onclick="applyRoundBarPreset(100, 1000)">Ø100</button>
                <button type="button" class="cpsat-add-btn" onclick="applyRoundBarPreset(150, 1000)">Ø150</button>
            `;
        }
        if (formulaDesc) formulaDesc.innerHTML = '<span data-i18n="calc_formula_round">計算公式：π × (外徑/2)² × 長(mm) × 比重 ÷ 1,000,000</span>';
    } else if (shape === 'round_tube') {
        d1Label.innerHTML = '<span data-i18n="calc_lbl_od">外徑 OD (mm)：</span>';
        d1Input.value = '60';
        d2Wrap.style.display = 'none';
        d3Wrap.style.display = '';
        d3Label.innerHTML = '<span data-i18n="calc_lbl_wall">管壁厚 t (mm)：</span>';
        d3Input.value = '5';
        lenInput.value = '3000';
        if (presetRow) {
            presetRow.style.display = 'flex';
            presetRow.innerHTML = `
                <span style="font-size: 0.78rem; color: var(--text-muted); align-self: center;" data-i18n="calc_lbl_len_presets">定尺長度快選：</span>
                <button type="button" class="cpsat-add-btn" onclick="applyLengthPreset(1000)">1m (1000mm)</button>
                <button type="button" class="cpsat-add-btn" onclick="applyLengthPreset(2000)">2m (2000mm)</button>
                <button type="button" class="cpsat-add-btn" onclick="applyLengthPreset(3000)">3m (3000mm)</button>
                <button type="button" class="cpsat-add-btn" onclick="applyLengthPreset(6000)">6m (6000mm)</button>
            `;
        }
        if (formulaDesc) formulaDesc.innerHTML = '<span data-i18n="calc_formula_rtube">計算公式：π × ((外徑/2)² - (內徑/2)²) × 長(mm) × 比重 ÷ 1,000,000</span>';
    } else if (shape === 'square_bar') {
        d1Label.innerHTML = '<span data-i18n="calc_lbl_sq_w">四方邊寬 W (mm)：</span>';
        d1Input.value = '40';
        lenInput.value = '3000';
        d2Wrap.style.display = 'none';
        d3Wrap.style.display = 'none';
        if (presetRow) {
            presetRow.style.display = 'flex';
            presetRow.innerHTML = `
                <span style="font-size: 0.78rem; color: var(--text-muted); align-self: center;" data-i18n="calc_lbl_len_presets">定尺長度快選：</span>
                <button type="button" class="cpsat-add-btn" onclick="applyLengthPreset(1000)">1m</button>
                <button type="button" class="cpsat-add-btn" onclick="applyLengthPreset(2000)">2m</button>
                <button type="button" class="cpsat-add-btn" onclick="applyLengthPreset(3000)">3m</button>
                <button type="button" class="cpsat-add-btn" onclick="applyLengthPreset(4000)">4m</button>
            `;
        }
        if (formulaDesc) formulaDesc.innerHTML = '<span data-i18n="calc_formula_sqbar">計算公式：邊寬² × 長(mm) × 比重 ÷ 1,000,000</span>';
    } else if (shape === 'hex_bar') {
        d1Label.innerHTML = '<span data-i18n="calc_lbl_hex_d">六角對邊 D (mm)：</span>';
        d1Input.value = '30';
        lenInput.value = '3000';
        d2Wrap.style.display = 'none';
        d3Wrap.style.display = 'none';
        if (presetRow) {
            presetRow.style.display = 'flex';
            presetRow.innerHTML = `
                <span style="font-size: 0.78rem; color: var(--text-muted); align-self: center;" data-i18n="calc_lbl_len_presets">定尺長度快選：</span>
                <button type="button" class="cpsat-add-btn" onclick="applyLengthPreset(1000)">1m</button>
                <button type="button" class="cpsat-add-btn" onclick="applyLengthPreset(2000)">2m</button>
                <button type="button" class="cpsat-add-btn" onclick="applyLengthPreset(3000)">3m</button>
            `;
        }
        if (formulaDesc) formulaDesc.innerHTML = '<span data-i18n="calc_formula_hex">計算公式：0.866025 × 對邊² × 長(mm) × 比重 ÷ 1,000,000</span>';
    } else if (shape === 'rect_tube') {
        d1Label.innerHTML = '<span data-i18n="calc_lbl_rect_w">管寬 W (mm)：</span>';
        d1Input.value = '60';
        d2Wrap.style.display = '';
        d2Label.innerHTML = '<span data-i18n="calc_lbl_rect_h">管高 H (mm)：</span>';
        d2Input.value = '40';
        d3Wrap.style.display = '';
        d3Label.innerHTML = '<span data-i18n="calc_lbl_wall">管壁厚 t (mm)：</span>';
        d3Input.value = '3';
        lenInput.value = '3000';
        if (presetRow) presetRow.style.display = 'none';
        if (formulaDesc) formulaDesc.innerHTML = '<span data-i18n="calc_formula_rect">計算公式：(W×H - (W-2t)×(H-2t)) × 長(mm) × 比重 ÷ 1,000,000</span>';
    }
    const currentLang = window.getCurrentLanguage ? window.getCurrentLanguage() : 'zh-TW';
    if (window.applyTranslations) window.applyTranslations(currentLang);
    calculateMetalWeight();
};

window.applyPlatePreset = function(w, l) {
    const d2 = document.getElementById('wtDim2');
    const len = document.getElementById('wtLength');
    if (d2) d2.value = w;
    if (len) len.value = l;
    calculateMetalWeight();
};

window.calculateMetalWeight = function() {
    const alloyRaw = document.getElementById('wtAlloySelect')?.value || '2.70|6061';
    const density = parseFloat(alloyRaw.split('|')[0]) || 2.70;
    const shape = document.getElementById('wtShapeSelect')?.value || 'plate';
    const d1 = Math.max(0, parseFloat(document.getElementById('wtDim1')?.value || '0'));
    const d2 = Math.max(0, parseFloat(document.getElementById('wtDim2')?.value || '0'));
    const d3 = Math.max(0, parseFloat(document.getElementById('wtDim3')?.value || '0'));
    const length = Math.max(0, parseFloat(document.getElementById('wtLength')?.value || '0'));
    const qty = Math.max(1, parseInt(document.getElementById('wtQty')?.value || '1', 10));

    let areaMm2 = 0;
    if (shape === 'plate') {
        areaMm2 = d1 * d2;
    } else if (shape === 'round_bar') {
        areaMm2 = Math.PI * Math.pow(d1 / 2, 2);
    } else if (shape === 'round_tube') {
        const od = d1;
        const id = Math.max(0, od - 2 * d3);
        areaMm2 = Math.PI * (Math.pow(od / 2, 2) - Math.pow(id / 2, 2));
    } else if (shape === 'square_bar') {
        areaMm2 = d1 * d1;
    } else if (shape === 'hex_bar') {
        areaMm2 = (Math.sqrt(3) / 2) * d1 * d1;
    } else if (shape === 'rect_tube') {
        const innerW = Math.max(0, d1 - 2 * d3);
        const innerH = Math.max(0, d2 - 2 * d3);
        areaMm2 = (d1 * d2) - (innerW * innerH);
    }

    const volumeCm3 = (areaMm2 * length) / 1000.0;
    const singleKg = (areaMm2 * length * density) / 1000000.0;
    const perMeterKg = (areaMm2 * 1000.0 * density) / 1000000.0;
    const totalKg = singleKg * qty;

    const elSingle = document.getElementById('wtSingleKg');
    const elMeter = document.getElementById('wtPerMeterKg');
    const elVol = document.getElementById('wtVolumeCm3');
    const elTotal = document.getElementById('wtTotalKg');

    if (elSingle) elSingle.textContent = `${singleKg.toFixed(2)} kg`;
    if (elMeter) elMeter.textContent = `${perMeterKg.toFixed(2)} kg/m`;
    if (elVol) elVol.textContent = `${Math.round(volumeCm3).toLocaleString()} cm³`;
    if (elTotal) elTotal.textContent = `${totalKg.toFixed(2)} kg`;
};

window.addCalculatedWeightToQuote = function() {
    const alloyRaw = document.getElementById('wtAlloySelect')?.value || '2.70|6061 鋁合金';
    const alloyName = alloyRaw.split('|')[1] || '6061 鋁合金';
    const shape = document.getElementById('wtShapeSelect')?.value || 'plate';
    const d1 = document.getElementById('wtDim1')?.value || '0';
    const d2 = document.getElementById('wtDim2')?.value || '0';
    const d3 = document.getElementById('wtDim3')?.value || '0';
    const length = document.getElementById('wtLength')?.value || '0';
    const qty = document.getElementById('wtQty')?.value || '1';
    const totalTxt = document.getElementById('wtTotalKg')?.textContent || '';

    let dimStr = '';
    if (shape === 'plate') dimStr = `鋁板/扁條 厚${d1} × 寬${d2} × 長${length}mm`;
    else if (shape === 'round_bar') dimStr = `圓棒 φ${d1} × 長${length}mm`;
    else if (shape === 'round_tube') dimStr = `圓管 OD${d1} × 壁厚${d3} × 長${length}mm`;
    else if (shape === 'square_bar') dimStr = `四方條 ${d1}×${d1} × 長${length}mm`;
    else if (shape === 'hex_bar') dimStr = `六角條 對邊${d1} × 長${length}mm`;
    else if (shape === 'rect_tube') dimStr = `方矩管 ${d1}×${d2}×壁厚${d3} × 長${length}mm`;

    const summary = `[算料詢價] ${alloyName} · ${dimStr} × ${qty}件 (預估總重 ${totalTxt})`;
    if (typeof window.addSpecToQuote === 'function') {
        window.addSpecToQuote(summary);
    }
};

window.exportCalculatedWeightToPdf = function() {
    const alloyRaw = document.getElementById('wtAlloySelect')?.value || '2.70|6061 鋁合金';
    const alloyName = alloyRaw.split('|')[1] || '6061 鋁合金';
    const shape = document.getElementById('wtShapeSelect')?.value || 'plate';
    const d1 = document.getElementById('wtDim1')?.value || '0';
    const d2 = document.getElementById('wtDim2')?.value || '0';
    const d3 = document.getElementById('wtDim3')?.value || '0';
    const length = document.getElementById('wtLength')?.value || '0';
    const qty = document.getElementById('wtQty')?.value || '1';
    const singleTxt = document.getElementById('wtSingleKg')?.textContent || '—';
    const totalTxt = document.getElementById('wtTotalKg')?.textContent || '—';

    let dimStr = '';
    if (shape === 'plate') dimStr = `厚 ${d1}mm × 寬 ${d2}mm × 長 ${length}mm`;
    else if (shape === 'round_bar') dimStr = `圓棒 φ${d1}mm × 長 ${length}mm`;
    else if (shape === 'round_tube') dimStr = `圓管 外徑φ${d1}mm × 壁厚${d3}mm × 長 ${length}mm`;
    else if (shape === 'square_bar') dimStr = `四方條 ${d1}×${d1}mm × 長 ${length}mm`;
    else if (shape === 'hex_bar') dimStr = `六角條 對邊${d1}mm × 長 ${length}mm`;
    else if (shape === 'rect_tube') dimStr = `方矩管 ${d1}×${d2}mm × 壁厚${d3}mm × 長 ${length}mm`;

    const mat = `${alloyName} · ${dimStr}`;
    const msg = `需求數量 ${qty} 件，單件重量約 ${singleTxt}，整批預估總重約 ${totalTxt}。`;
    const url = `/quotation/preview?material=${encodeURIComponent(mat)}&message=${encodeURIComponent(msg)}&qty=${encodeURIComponent(qty)}&weight=${encodeURIComponent(totalTxt)}&alloy=${encodeURIComponent(alloyName)}`;
    window.open(url, '_blank');
};

/* ==========================================================================
   精美動態風格與微互動 (Dynamic Styling & Micro-Interactions)
   ========================================================================== */

function initDynamicInteractions() {
    initScrollProgressAndBackToTop();
    initStatCounters();
    initScrollReveal();
    initInteractiveTilt();
    initButtonRipple();
}

/**
 * 1. 頂部閱讀進度條與圓環返回頂端按鈕
 */
function initScrollProgressAndBackToTop() {
    const progressBar = document.getElementById('scrollProgressBar');
    const backBtn = document.getElementById('backToTopBtn');
    const ringCircle = document.getElementById('backToTopCircle');
    const circumference = 2 * Math.PI * 20; // ~125.66

    if (ringCircle) {
        ringCircle.style.strokeDasharray = `${circumference}`;
        ringCircle.style.strokeDashoffset = `${circumference}`;
    }

    function handleScroll() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const progress = scrollHeight > 0 ? Math.min(Math.max(scrollTop / scrollHeight, 0), 1) : 0;

        if (progressBar) {
            progressBar.style.width = `${(progress * 100).toFixed(2)}%`;
        }

        if (ringCircle) {
            const offset = circumference - (progress * circumference);
            ringCircle.style.strokeDashoffset = offset;
        }

        if (backBtn) {
            if (scrollTop > 260) {
                backBtn.classList.add('visible');
            } else {
                backBtn.classList.remove('visible');
            }
        }
    }

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();

    if (backBtn) {
        backBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
}

/**
 * 2. 數據指標動態跳動計數器 (Hero Stat Number Counters)
 */
function initStatCounters() {
    const counterElements = document.querySelectorAll('[data-counter-target]');
    if (!counterElements.length) return;

    if (!('IntersectionObserver' in window)) {
        counterElements.forEach(el => animateSingleCounter(el));
        return;
    }

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.dataset.counted) {
                entry.target.dataset.counted = "true";
                animateSingleCounter(entry.target);
            }
        });
    }, { threshold: 0.25 });

    counterElements.forEach(el => observer.observe(el));
}

function animateSingleCounter(el) {
    const target = parseFloat(el.getAttribute('data-counter-target')) || 0;
    const suffix = el.getAttribute('data-counter-suffix') || '';
    const prefix = el.getAttribute('data-counter-prefix') || '';
    const duration = 1600; // ms
    const startTime = performance.now();

    function update(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        // Smooth ease-out cubic
        const ease = 1 - Math.pow(1 - progress, 3);
        const currentVal = Math.round(target * ease);

        const formatted = currentVal >= 1000 ? currentVal.toLocaleString('en-US') : currentVal;
        el.textContent = `${prefix}${formatted}${suffix}`;

        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            const finalVal = target >= 1000 ? target.toLocaleString('en-US') : target;
            el.textContent = `${prefix}${finalVal}${suffix}`;
        }
    }

    requestAnimationFrame(update);
}

/**
 * 3. 視窗滾動平滑淡入 (Scroll-Reveal Stagger Animation)
 */
function initScrollReveal() {
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        document.querySelectorAll('.reveal-on-scroll').forEach(el => el.classList.add('is-revealed'));
        return;
    }

    // Auto mark cards and headers if not marked
    const revealTargets = document.querySelectorAll(
        '.reveal-on-scroll, .section-header, .glass-card:not(.hero-preview-card):not(.ai-chat-widget):not(.modal-content), .product-card, .network-card, .case-card, .calc-card'
    );

    revealTargets.forEach(el => {
        if (!el.classList.contains('reveal-on-scroll')) {
            el.classList.add('reveal-on-scroll');
        }
    });

    if (!('IntersectionObserver' in window)) {
        revealTargets.forEach(el => el.classList.add('is-revealed'));
        return;
    }

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-revealed');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.08,
        rootMargin: '0px 0px -30px 0px'
    });

    revealTargets.forEach(el => observer.observe(el));
}

/**
 * 4. 3D 擬真鋁合金卡片微傾斜 (Interactive 3D Card Tilt)
 */
function initInteractiveTilt() {
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    if (window.innerWidth < 992) return; // Desktop only for smooth performance

    const tiltTargets = document.querySelectorAll('.hero-preview-card, .product-card, .calc-card');
    tiltTargets.forEach(card => {
        let bounds = null;
        let rafId = null;

        card.addEventListener('mouseenter', () => {
            bounds = card.getBoundingClientRect();
            card.style.transition = 'transform 0.12s ease-out, box-shadow 0.25s ease';
        });

        card.addEventListener('mousemove', (e) => {
            if (!bounds) bounds = card.getBoundingClientRect();
            if (rafId) cancelAnimationFrame(rafId);
            rafId = requestAnimationFrame(() => {
                const mouseX = e.clientX - bounds.left;
                const mouseY = e.clientY - bounds.top;
                const pctX = (mouseX / bounds.width) - 0.5;
                const pctY = (mouseY / bounds.height) - 0.5;
                const tiltX = (pctY * -8).toFixed(2);
                const tiltY = (pctX * 8).toFixed(2);
                card.style.transform = `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) translateY(-4px) scale3d(1.012, 1.012, 1.012)`;
            });
        });

        card.addEventListener('mouseleave', () => {
            if (rafId) cancelAnimationFrame(rafId);
            bounds = null;
            card.style.transition = 'transform 0.45s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s ease';
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0) scale3d(1, 1, 1)';
        });
    });
}

/**
 * 5. 按鈕點擊材質水波光暈 (Button Click Ripple Wave)
 */
function initButtonRipple() {
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.btn, .btn-primary, .btn-outline, .btn-read-tts, .chip, .subpage-pill');
        if (!btn) return;

        const rect = btn.getBoundingClientRect();
        const diameter = Math.max(rect.width, rect.height);
        const radius = diameter / 2;

        const ripple = document.createElement('span');
        ripple.className = 'btn-ripple-wave';
        ripple.style.width = ripple.style.height = `${diameter}px`;
        ripple.style.left = `${e.clientX - rect.left - radius}px`;
        ripple.style.top = `${e.clientY - rect.top - radius}px`;

        const prevRipple = btn.querySelector('.btn-ripple-wave');
        if (prevRipple) prevRipple.remove();

        btn.appendChild(ripple);
        setTimeout(() => {
            ripple.remove();
        }, 650);
    });
}

// Multi-Language Dynamic Dock Voice Adaptation
window.addEventListener('fapo-language-changed', (e) => {
    const lang = (e.detail && e.detail.lang) || 'zh-TW';
    const voiceSelect = document.getElementById('dockVoiceSelect');
    if (!voiceSelect) return;

    if (lang === 'en') {
        voiceSelect.innerHTML = `
            <option value="en-US-JennyNeural" selected>🎙️ Jenny (Clear Female)</option>
            <option value="en-US-GuyNeural">🎙️ Guy (Professional Male)</option>
        `;
        audioTourState.voice = 'en-US-JennyNeural';
    } else if (lang === 'ja') {
        voiceSelect.innerHTML = `
            <option value="ja-JP-NanamiNeural" selected>🎙️ 七海 (落ち着いた女性)</option>
            <option value="ja-JP-KeitaNeural">🎙️ 圭太 (信頼の男性)</option>
        `;
        audioTourState.voice = 'ja-JP-NanamiNeural';
    } else if (lang === 'ko') {
        voiceSelect.innerHTML = `
            <option value="ko-KR-SunHiNeural" selected>🎙️ 선희 (차분한 여성)</option>
            <option value="ko-KR-InJoonNeural">🎙️ 인준 (신뢰의 남성)</option>
        `;
        audioTourState.voice = 'ko-KR-SunHiNeural';
    } else {
        voiceSelect.innerHTML = `
            <option value="zen-male" selected>🎙️ 沉穩專業男聲</option>
            <option value="zen-female">🎙️ 溫潤柔和女聲</option>
            <option value="zh-TW-HsiaoChenNeural">🎙️ 現代俐落女聲</option>
        `;
        audioTourState.voice = 'zen-male';
    }

    if (window.updateSubpageCrumbAndPager) {
        window.updateSubpageCrumbAndPager(window.CURRENT_PAGE_ID || 'hero');
    }

    if (typeof updateTourChaptersDropdown === 'function') {
        updateTourChaptersDropdown(lang);
    }

    if (audioTourState.isPlaying) {
        selectChapter(audioTourState.currentChapter, true);
    }
});

/* ==========================================================================
   Google OR-Tools CP-SAT Cutting Stock Optimization Engineering Workbench
   ========================================================================== */
window.applyCpsatPreset = function(type) {
    const stockInput = document.getElementById('wbStockLen');
    const kerfInput = document.getElementById('wbKerf');
    const list = document.getElementById('wbDemandList');
    if (!stockInput || !kerfInput || !list) return;

    let stock = 3000;
    let kerf = 3;
    let rows = [];

    if (type === 'aerospace') {
        stock = 3000;
        kerf = 3;
        rows = [
            { len: 800, qty: 3 },
            { len: 550, qty: 4 },
            { len: 420, qty: 5 }
        ];
    } else if (type === 'long_bar') {
        stock = 6000;
        kerf = 3;
        rows = [
            { len: 1250, qty: 4 },
            { len: 850, qty: 3 },
            { len: 400, qty: 6 }
        ];
    } else if (type === 'custom') {
        stock = 4000;
        kerf = 2.5;
        rows = [
            { len: 950, qty: 3 },
            { len: 620, qty: 4 },
            { len: 310, qty: 5 }
        ];
    }

    stockInput.value = stock;
    kerfInput.value = kerf;
    list.innerHTML = '';
    rows.forEach(r => window.addWbDemandRow(r.len, r.qty));

    // Automatically trigger calculation for real-time responsiveness
    window.runWorkbenchCpsatSolver();
};

window.addWbDemandRow = function(len = 600, qty = 2) {
    const list = document.getElementById('wbDemandList');
    if (!list) return;
    const row = document.createElement('div');
    row.className = 'wb-demand-row';
    row.style.cssText = 'display: flex; gap: 10px; align-items: center;';
    row.innerHTML = `
        <input type="number" class="wb-len-input" value="${len}" min="10" placeholder="長度 mm" style="flex: 2; padding: 9px 12px; border-radius: 8px; border: 1px solid var(--border-subtle); font-weight: 600;">
        <input type="number" class="wb-qty-input" value="${qty}" min="1" placeholder="支數" style="flex: 1; padding: 9px 12px; border-radius: 8px; border: 1px solid var(--border-subtle); font-weight: 600;">
        <button type="button" class="btn-outline" onclick="this.parentElement.remove()" style="padding: 8px 12px; border-color: #ef4444; color: #ef4444; border-radius: 8px; cursor: pointer;" title="刪除此列">✕</button>
    `;
    list.appendChild(row);
};

window.runWorkbenchCpsatSolver = function() {
    const stockLen = parseInt(document.getElementById('wbStockLen')?.value || '3000', 10);
    const kerf = parseFloat(document.getElementById('wbKerf')?.value || '3');
    const rows = document.querySelectorAll('#wbDemandList .wb-demand-row');
    const resBox = document.getElementById('wbResultBox');
    const solveBtn = document.getElementById('wbSolveBtn');

    if (!resBox) return;

    const demands = [];
    rows.forEach(r => {
        const l = parseInt(r.querySelector('.wb-len-input')?.value || '0', 10);
        const q = parseInt(r.querySelector('.wb-qty-input')?.value || '0', 10);
        if (l > 0 && q > 0) demands.push({ length: l, qty: q });
    });

    if (demands.length === 0) {
        resBox.style.display = 'block';
        resBox.innerHTML = `<div style="color:#b91c1c;font-weight:700;padding:12px;background:#fef2f2;border-radius:8px;">⚠️ 請至少填寫一組有效的裁切尺寸與數量！</div>`;
        return;
    }

    resBox.style.display = 'block';
    resBox.innerHTML = `
        <div style="text-align: center; padding: 24px; color: var(--text-secondary);">
            <div style="font-size: 2rem; margin-bottom: 8px; animation: spin 1s infinite linear;">⚙️</div>
            <strong style="color: var(--text-primary); font-size: 1rem;">AI 求解器運算中...</strong>
            <p style="font-size: 0.85rem; margin-top: 4px;">正在建立整數線性約束模型，計算全局最少母材數與餘料最小化排版...</p>
        </div>
    `;
    if (solveBtn) solveBtn.disabled = true;

    fetch('/api/ai/cutting-stock', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            stock_length_mm: stockLen,
            kerf_mm: kerf,
            demands: demands
        })
    })
    .then(r => r.json())
    .then(plan => {
        if (solveBtn) solveBtn.disabled = false;
        if (!plan.success) {
            resBox.innerHTML = `<div style="color:#b91c1c;font-weight:700;padding:14px;background:#fef2f2;border-radius:8px;">❌ 求解失敗：${plan.error || '無可行解或參數超出邊界'}</div>`;
            return;
        }

        let barsHtml = '';
        const colorPalette = ['#b83b26', '#1d4ed8', '#059669', '#d97706', '#7c3aed', '#0891b2', '#c026d3', '#2563eb', '#0d9488'];

        plan.bars_plan.forEach(b => {
            const stockL = plan.stock_length_mm;
            let svgElements = '';
            
            // Background track representing the mother standard bar
            svgElements += `<rect x="0" y="2" width="1000" height="38" rx="4" fill="#07142c" stroke="#1e3a5f" stroke-width="1.2" />`;

            if (b.segments && b.segments.length > 0) {
                b.segments.forEach(seg => {
                    const x = (seg.start_mm / stockL) * 1000;
                    const w = Math.max(1.2, (seg.length_mm / stockL) * 1000);
                    if (seg.type === 'piece') {
                        const col = colorPalette[Math.abs(seg.length_mm * 11 + seg.index) % colorPalette.length];
                        svgElements += `
                            <g class="cpsat-svg-piece">
                                <rect x="${x.toFixed(1)}" y="4" width="${w.toFixed(1)}" height="34" rx="2" fill="${col}">
                                    <title>工件 #${seg.index}：長度 ${seg.length_mm} mm (位置 ${seg.start_mm} ~ ${seg.end_mm} mm)</title>
                                </rect>
                                ${w > 36 ? `<text x="${(x + w/2).toFixed(1)}" y="25" fill="#ffffff" font-size="11" font-weight="700" text-anchor="middle" pointer-events="none">${seg.length_mm}</text>` : ''}
                            </g>
                        `;
                    } else if (seg.type === 'kerf') {
                        const kw = Math.max(1.8, w);
                        svgElements += `
                            <rect x="${x.toFixed(1)}" y="2" width="${kw.toFixed(1)}" height="38" fill="#ef4444">
                                <title>鋸縫損耗：${seg.length_mm} mm</title>
                            </rect>
                        `;
                    } else if (seg.type === 'remnant') {
                        svgElements += `
                            <g class="cpsat-svg-remnant">
                                <rect x="${x.toFixed(1)}" y="4" width="${w.toFixed(1)}" height="34" rx="2" fill="rgba(148,163,184,0.2)" stroke="#94a3b8" stroke-dasharray="3,2">
                                    <title>可用餘料：${seg.length_mm} mm (${((seg.length_mm / stockL) * 100).toFixed(1)}%)</title>
                                </rect>
                                ${w > 45 ? `<text x="${(x + w/2).toFixed(1)}" y="25" fill="#475569" font-size="10" font-weight="700" text-anchor="middle" pointer-events="none">餘 ${seg.length_mm}mm</text>` : ''}
                            </g>
                        `;
                    }
                });
            }

            barsHtml += `
                <div style="margin-bottom: 16px; background: rgba(10, 24, 50, 0.9); padding: 12px 16px; border-radius: 10px; border: 1px solid var(--border-subtle); box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                    <div style="display:flex; justify-content:space-between; align-items:center; font-weight:700; font-size:0.86rem; margin-bottom: 6px; flex-wrap: wrap; gap: 8px;">
                        <span style="color: var(--text-primary);">🔩 母材 #${b.bar_no}：${b.cuts_summary}</span>
                        <span style="color:var(--accent-cinnabar); background:rgba(182,59,46,0.08); padding:3px 8px; border-radius:6px; font-size:0.8rem;">利用率 <strong>${b.utilization_pct}%</strong> (可用餘料 ${b.remnant_mm}mm)</span>
                    </div>
                    <div class="cpsat-svg-wrap" style="position: relative; width: 100%;">
                        <svg class="cpsat-svg-bar" viewBox="0 0 1000 44" preserveAspectRatio="none" style="width: 100%; height: 42px; display: block; border-radius: 6px; overflow: hidden;">
                            ${svgElements}
                        </svg>
                        <div style="display:flex; justify-content:space-between; font-size:10px; color:#64748b; font-family:monospace; margin-top:4px; padding:0 2px;">
                            <span>0 mm</span>
                            <span style="color:#ef4444; font-weight: 600;">刀縫損耗: ${plan.kerf_mm}mm</span>
                            <span>${stockL} mm (滿料定寸)</span>
                        </div>
                    </div>
                </div>
            `;
        });

        const quoteSummary = `[AI 最佳化裁切] 母材規格 ${plan.stock_length_mm}mm 共需 ${plan.total_bars_used} 支 (綜合利用率 ${plan.overall_utilization_pct}%): ` +
            plan.bars_plan.map(b => `第${b.bar_no}支(${b.cuts_summary}, 餘${b.remnant_mm}mm)`).join('；');
        const safeQuote = quoteSummary.replace(/'/g, "\\'");

        const speechComm = plan.speech_commentary || `AI 求解完成：母材 ${plan.stock_length_mm}mm 最少僅需 ${plan.total_bars_used} 支，總材料利用率達 ${plan.overall_utilization_pct}%，有效消除裁切浪費。`;
        const safeCommentary = speechComm.replace(/'/g, "\\'").replace(/"/g, '&quot;').replace(/\n/g, ' ');

        resBox.innerHTML = `
            <div style="margin-bottom: 16px; padding-bottom: 14px; border-bottom: 1px solid var(--border-subtle);">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 10px;">
                    <span style="font-weight: 800; color: #166534; background: #dcfce7; padding: 4px 10px; border-radius: 6px; font-size: 0.88rem;">
                        ✅ ${plan.solver_status} · 耗時僅 ${plan.solve_time_ms} ms (AI 求解器)
                    </span>
                    <button type="button" class="btn btn-outline btn-sm" onclick="readAloudText('${safeCommentary}', this)" style="font-size: 0.82rem; padding: 4px 10px;">
                        🔊 語音解說此排料方案
                    </button>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; text-align: center;">
                    <div style="padding: 10px; background: rgba(10, 24, 50, 0.9); border-radius: 8px; border: 1px solid var(--border-subtle);">
                        <div style="font-size: 0.76rem; color: var(--text-secondary);">最少需用母材</div>
                        <div style="font-size: 1.25rem; font-weight: 800; color: var(--accent-cinnabar);">${plan.total_bars_used} <span style="font-size: 0.8rem;">支</span></div>
                    </div>
                    <div style="padding: 10px; background: rgba(10, 24, 50, 0.9); border-radius: 8px; border: 1px solid var(--border-subtle);">
                        <div style="font-size: 0.76rem; color: var(--text-secondary);">綜合材料利用率</div>
                        <div style="font-size: 1.25rem; font-weight: 800; color: #166534;">${plan.overall_utilization_pct}%</div>
                    </div>
                    <div style="padding: 10px; background: rgba(10, 24, 50, 0.9); border-radius: 8px; border: 1px solid var(--border-subtle);">
                        <div style="font-size: 0.76rem; color: var(--text-secondary);">總產出工件</div>
                        <div style="font-size: 1.25rem; font-weight: 800; color: var(--text-primary);">${plan.total_pieces_cut} <span style="font-size: 0.8rem;">段</span></div>
                    </div>
                    <div style="padding: 10px; background: rgba(10, 24, 50, 0.9); border-radius: 8px; border: 1px solid var(--border-subtle);">
                        <div style="font-size: 0.76rem; color: var(--text-secondary);">總剩餘料長度</div>
                        <div style="font-size: 1.25rem; font-weight: 800; color: #475569;">${plan.total_remnant_mm} <span style="font-size: 0.8rem;">mm</span></div>
                    </div>
                </div>
            </div>

            <div style="margin-bottom: 16px;">
                <h4 style="font-size: 0.95rem; font-weight: 700; color: var(--text-primary); margin: 0 0 10px 0;">📊 各母材定寸裁切排版圖 (SVG 視覺化)：</h4>
                ${barsHtml}
            </div>

            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <button type="button" class="btn btn-primary" style="flex: 2; justify-content: center; padding: 12px; font-weight: 700;" onclick="addSpecToQuote('${safeQuote}')">
                    📋 將此最佳排料明細一鍵帶入詢價單
                </button>
                <button type="button" class="btn btn-outline" style="flex: 1; justify-content: center; padding: 12px; font-weight: 700; background: #1e293b; color: #ffffff; border-color: #1e293b;" onclick="window.open('/quotation/preview?material=' + encodeURIComponent('母材 ${plan.stock_length_mm}mm 定寸裁切方案 (${plan.total_bars_used} 支)') + '&message=' + encodeURIComponent('${safeQuote}') + '&qty=${plan.total_bars_used}', '_blank')">
                    📄 匯出工單 / 列印 PDF
                </button>
            </div>
        `;
    })
    .catch(err => {
        if (solveBtn) solveBtn.disabled = false;
        resBox.innerHTML = `<div style="color:#b91c1c;font-weight:700;padding:12px;background:#fef2f2;border-radius:8px;">❌ 網路或後端求解器連線異常，請稍後重試。</div>`;
        console.error('CP-SAT solve error:', err);
    });
};


/* ==========================================================================
   Multi-Engine CP-SAT Workbench Extensions (2D Plate, 5-Plant Gantt, Alloy)
   ========================================================================== */
window.switchWbTab = function(tab) {
    const tabs = ['1d', '2d', 'sched', 'alloy'];
    tabs.forEach(t => {
        const btn = document.getElementById('wbTabBtn' + (t === '1d' ? '1d' : t === '2d' ? '2d' : t === 'sched' ? 'Sched' : 'Alloy'));
        const panel = document.getElementById('wbPanel' + (t === '1d' ? '1d' : t === '2d' ? '2d' : t === 'sched' ? 'Sched' : 'Alloy'));
        if (btn) btn.classList.toggle('active', t === tab);
        if (panel) panel.style.display = (t === tab) ? 'block' : 'none';
    });
};

window.addWb2dRow = function() {
    const list = document.getElementById('wb2dList');
    if (!list) return;
    const row = document.createElement('div');
    row.className = 'wb2d-row';
    row.style.cssText = 'display:grid; grid-template-columns: 1.2fr 1fr 1fr 0.8fr auto; gap:8px; align-items:center;';
    row.innerHTML = `
        <input type="text" class="wb2d-lbl" value="客製板件" style="padding:8px 10px; border-radius:8px; border:1px solid var(--border-subtle); background:rgba(6,16,36,0.9); color:var(--text-main);">
        <input type="number" class="wb2d-w" value="350" placeholder="寬mm" style="padding:8px 10px; border-radius:8px; border:1px solid var(--border-subtle); background:rgba(6,16,36,0.9); color:var(--text-main);">
        <input type="number" class="wb2d-h" value="500" placeholder="長mm" style="padding:8px 10px; border-radius:8px; border:1px solid var(--border-subtle); background:rgba(6,16,36,0.9); color:var(--text-main);">
        <input type="number" class="wb2d-q" value="2" placeholder="數量" style="padding:8px 10px; border-radius:8px; border:1px solid var(--border-subtle); background:rgba(6,16,36,0.9); color:var(--text-main);">
        <button type="button" class="btn-outline" onclick="this.parentElement.remove()" style="padding:7px 11px; color:#ef4444; border-color:#ef4444; border-radius:8px;">✕</button>
    `;
    list.appendChild(row);
};

window.runWb2DPlateSolver = function() {
    const pw = parseInt(document.getElementById('wb2dWidth')?.value || '1250', 10);
    const ph = parseInt(document.getElementById('wb2dHeight')?.value || '2500', 10);
    const kerf = parseInt(document.getElementById('wb2dKerf')?.value || '4', 10);
    const rot = !!document.getElementById('wb2dRotate')?.checked;
    const resBox = document.getElementById('wb2dResultBox');
    if (!resBox) return;

    const pieces = [];
    document.querySelectorAll('#wb2dList .wb2d-row').forEach(r => {
        const label = r.querySelector('.wb2d-lbl')?.value || '板件';
        const w = parseInt(r.querySelector('.wb2d-w')?.value || '0', 10);
        const h = parseInt(r.querySelector('.wb2d-h')?.value || '0', 10);
        const qty = parseInt(r.querySelector('.wb2d-q')?.value || '0', 10);
        if (w > 0 && h > 0 && qty > 0) pieces.push({ label, width: w, height: h, qty });
    });

    resBox.style.display = 'block';
    resBox.innerHTML = `<div style="text-align:center; padding:18px; color:var(--accent-cyan);">⚙️ Google OR-Tools CP-SAT <code>AddNoOverlap2D</code> 正在計算最佳二維鋁板排樣...</div>`;

    fetch('/api/cpsat/2d-plate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plate_width: pw, plate_height: ph, kerf, allow_rotation: rot, pieces })
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) {
            resBox.innerHTML = `<div style="color:#ef4444; font-weight:700;">❌ ${data.error}</div>`;
            return;
        }
        const colors = ['#0284c7', '#0891b2', '#059669', '#7c3aed', '#d97706', '#2563eb', '#db2777'];
        let rectsSvg = `<rect x="0" y="0" width="${pw}" height="${ph}" fill="#061229" stroke="#00e5ff" stroke-width="6"/>`;
        (data.placements || []).forEach((p, idx) => {
            const col = colors[idx % colors.length];
            rectsSvg += `
                <g>
                    <rect x="${p.x}" y="${p.y}" width="${p.w}" height="${p.h}" fill="${col}" fill-opacity="0.82" stroke="#f0f7ff" stroke-width="3">
                        <title>${p.label}: ${p.w}×${p.h}mm @ (${p.x}, ${p.y})</title>
                    </rect>
                    <text x="${p.x + p.w/2}" y="${p.y + p.h/2}" fill="#ffffff" font-size="${Math.max(26, Math.min(p.w, p.h)*0.11)}" font-weight="700" text-anchor="middle" dominant-baseline="middle">${p.label} (${p.w}×${p.h})</text>
                </g>
            `;
        });

        resBox.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:14px;">
                <span style="color:#10b981; font-weight:800;">✅ CP-SAT AddNoOverlap2D 求解狀態：${data.status} (耗時 ${data.solve_time_ms} ms)</span>
                <span style="color:var(--accent-cyan); font-weight:700;">已排入 ${data.placed_count}/${data.total_requested} 件 ｜ 面積利用率 ${data.area_efficiency_pct}% ｜ 包絡長 ${data.bounding_height} mm</span>
            </div>
            <div style="max-width:560px; margin:0 auto; background:#030916; padding:12px; border-radius:10px; border:1px solid rgba(0,229,255,0.28);">
                <svg viewBox="0 0 ${pw} ${ph}" style="width:100%; height:auto; max-height:380px; display:block;">
                    ${rectsSvg}
                </svg>
            </div>
        `;
    })
    .catch(err => {
        resBox.innerHTML = `<div style="color:#ef4444;">❌ 2D 排樣求解連線異常：${err.message}</div>`;
    });
};

window.runWbScheduleSolver = function() {
    const resBox = document.getElementById('wbSchedResultBox');
    if (!resBox) return;
    resBox.style.display = 'block';
    resBox.innerHTML = `<div style="text-align:center; padding:18px; color:var(--accent-cyan);">⚙️ Google OR-Tools CP-SAT 正在排程全台五大廠區訂單甘特圖...</div>`;

    fetch('/api/cpsat/schedule', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
    })
    .then(r => r.json())
    .then(data => {
        const maxTime = Math.max(data.makespan_hours || 20, 1);
        const rowsHtml = (data.schedule || []).map(item => {
            const leftPct = ((item.start_hr / maxTime) * 100).toFixed(1);
            const widthPct = Math.max(8, ((item.duration_hr / maxTime) * 100)).toFixed(1);
            return `
                <div style="margin-bottom:10px; padding:10px 12px; background:rgba(10,24,50,0.88); border-radius:8px; border:1px solid rgba(0,229,255,0.2);">
                    <div style="display:flex; justify-content:space-between; font-size:0.84rem; margin-bottom:5px; flex-wrap:wrap; gap:6px;">
                        <strong style="color:var(--accent-cyan);">🏭 ${item.plant_name} · ${item.machine}</strong>
                        <span style="color:var(--text-main);">${item.job_name} (${item.start_hr}h ~ ${item.end_hr}h，共 ${item.duration_hr}h)</span>
                    </div>
                    <div style="position:relative; height:22px; background:#040b18; border-radius:6px; overflow:hidden; border:1px solid rgba(0,229,255,0.2);">
                        <div style="position:absolute; left:${leftPct}%; width:${widthPct}%; top:2px; bottom:2px; background:linear-gradient(90deg, #0284c7, #00e5ff); border-radius:4px; display:flex; align-items:center; justify-content:center; color:#030914; font-size:0.74rem; font-weight:800;">
                            ${item.start_hr}h - ${item.end_hr}h
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        resBox.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:14px;">
                <span style="color:#10b981; font-weight:800;">✅ CP-SAT 五廠區排程狀態：${data.status} (耗時 ${data.solve_time_ms} ms)</span>
                <span style="color:var(--accent-amber); font-weight:800;">全局最短總完工時間 (Makespan)：${data.makespan_hours} 小時</span>
            </div>
            ${rowsHtml}
        `;
    })
    .catch(err => {
        resBox.innerHTML = `<div style="color:#ef4444;">❌ 排程求解連線異常：${err.message}</div>`;
    });
};

window.runWbAlloySolver = function() {
    const minTensile = parseInt(document.getElementById('wbAlloyTensile')?.value || '280', 10);
    const thick = parseFloat(document.getElementById('wbAlloyThick')?.value || '25');
    const prio = document.getElementById('wbAlloyPriority')?.value || 'flatness';
    const resBox = document.getElementById('wbAlloyResultBox');
    if (!resBox) return;

    resBox.style.display = 'block';
    resBox.innerHTML = `<div style="text-align:center; padding:18px; color:var(--accent-cyan);">⚙️ CP-SAT 多目標合金選型引擎運算中...</div>`;

    const weights = {
        flatness: prio === 'flatness' ? 10 : 5,
        strength: prio === 'strength' ? 10 : 5,
        corrosion: prio === 'corrosion' ? 10 : 4,
        anodizing: prio === 'anodizing' ? 10 : 5,
        machinability: 7
    };

    fetch('/api/cpsat/alloy-select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ min_tensile_mpa: minTensile, thickness_mm: thick, weights })
    })
    .then(r => r.json())
    .then(data => {
        const recs = data.recommendations || [];
        if (!recs.length) {
            resBox.innerHTML = `<div style="color:#fbbf24;">⚠️ 無完全符合該嚴苛條件之單一牌號，建議放寬抗拉強度或厚度限制。</div>`;
            return;
        }
        resBox.innerHTML = `
            <div style="margin-bottom:12px; color:#10b981; font-weight:800;">
                ✅ CP-SAT 多目標選料完成 (${data.status}，耗時 ${data.solve_time_ms} ms) — 為您推薦最佳前 ${recs.length} 名賀華常備材質：
            </div>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap:12px;">
                ${recs.map((a, i) => `
                    <div style="padding:14px; border-radius:10px; background:rgba(10,24,50,0.92); border:1px solid ${i===0 ? '#00e5ff' : 'rgba(0,229,255,0.22)'};">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                            <strong style="font-size:1.05rem; color:var(--accent-cyan);">#${i+1} ${a.code} (${a.temper})</strong>
                            <span class="chip" style="color:#fbbf24;">綜合評分 ${a.cpsat_score}</span>
                        </div>
                        <div style="font-size:0.84rem; color:var(--text-main); margin-bottom:6px;">${a.name_zh}</div>
                        <div style="font-size:0.8rem; color:var(--text-dim); margin-bottom:10px;">
                            抗拉強度：${a.tensile_mpa} MPa ｜ 降伏：${a.yield_mpa} MPa ｜ 硬度：${a.hardness_hb} HB
                        </div>
                        <button type="button" class="btn btn-outline btn-sm" style="width:100%; justify-content:center;" onclick="addSpecToQuote('${a.code} (${a.name_zh}) 厚 ${thick}mm')">
                            ＋ 加入詢價單
                        </button>
                    </div>
                `).join('')}
            </div>
        `;
    })
    .catch(err => {
        resBox.innerHTML = `<div style="color:#ef4444;">❌ 選型求解異常：${err.message}</div>`;
    });
};
