import os
import io
import csv
import sys
import time
import hmac
import json
import re
import hashlib
import asyncio
import datetime
import threading
import urllib.request
from functools import wraps
from flask import Flask, Response, render_template, request, jsonify, session, send_from_directory
import edge_tts
import mailer

# Support PyInstaller bundled environment
BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.before_request
def restore_missing_drawing_on_demand():
    """
    If Render container restarted/redeployed and wiped static/uploads/drawings/,
    automatically restore the requested drawing file from the database before Flask serves it.
    """
    if request.path.startswith('/static/uploads/drawings/'):
        fname = os.path.basename(request.path)
        if fname:
            local_file = os.path.join(DRAWINGS_DIR, fname)
            if not os.path.exists(local_file):
                rec = db.get_drawing_file(fname)
                if rec and rec.get('file_bytes'):
                    try:
                        os.makedirs(DRAWINGS_DIR, exist_ok=True)
                        with open(local_file, 'wb') as f:
                            f.write(rec['file_bytes'])
                    except Exception:
                        return Response(rec['file_bytes'], mimetype=rec.get('content_type', 'application/octet-stream'))


@app.after_request
def add_no_cache_headers(response):
    # Ensure client browsers always get fresh dynamic rendering and styles without stale caching
    if 'text/css' in response.headers.get('Content-Type', '') or 'javascript' in response.headers.get('Content-Type', '') or 'text/html' in response.headers.get('Content-Type', ''):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

# Deterministic secret key across multi-worker Gunicorn instances unless overridden
_raw_secret = os.environ.get('SECRET_KEY') or f"harvard-rfq-admin-{mailer.get_admin_password()}"
app.secret_key = hashlib.sha256(_raw_secret.encode('utf-8')).hexdigest()

INQUIRIES_LOCK = threading.Lock()
INQUIRIES_FILE = os.path.join(BASE_DIR, 'data', 'inquiries.json')

# Ensure required directories exist in working directory
os.makedirs(os.path.join(BASE_DIR, 'static', 'audio', 'cache'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)
DRAWINGS_DIR = os.path.join(BASE_DIR, 'static', 'uploads', 'drawings')
os.makedirs(DRAWINGS_DIR, exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Load data
DATA_PATH = os.path.join(BASE_DIR, 'data', 'harvard_complete_data.json')
SPECS_PATH = os.path.join(BASE_DIR, 'data', 'inventory_specs.json')

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    SITE_DATA = json.load(f)

import db

try:
    INVENTORY_DATA = db.get_all_specs()
    if not INVENTORY_DATA:
        with open(SPECS_PATH, 'r', encoding='utf-8') as f:
            INVENTORY_DATA = json.load(f)
except Exception:
    INVENTORY_DATA = []

# ==========================================================================
#  全自動 Self-Ping 防休眠背景線程 (Keep-Alive Thread for Render)
# ==========================================================================
APP_START_TIME = datetime.datetime.now()
_KEEP_ALIVE_THREAD = None
_KEEP_ALIVE_LOCK = threading.Lock()

@app.route('/api/health')
@app.route('/healthz')
def api_health():
    uptime_sec = int((datetime.datetime.now() - APP_START_TIME).total_seconds())
    return jsonify({
        "status": "healthy",
        "service": "harvard-enterprises-cpsat",
        "uptime_sec": uptime_sec,
        "timestamp": datetime.datetime.now().isoformat(),
        "is_render": bool(os.environ.get('RENDER') or os.environ.get('RENDER_EXTERNAL_URL'))
    })

@app.route('/api/keep-alive-status')
def api_keep_alive_status():
    is_alive = _KEEP_ALIVE_THREAD is not None and _KEEP_ALIVE_THREAD.is_alive()
    target_base = (
        os.environ.get('KEEP_ALIVE_URL')
        or os.environ.get('RENDER_EXTERNAL_URL')
        or "https://harvard-ent.onrender.com"
    ).rstrip('/')
    return jsonify({
        "active": is_alive,
        "target_url": f"{target_base}/api/health",
        "thread_name": _KEEP_ALIVE_THREAD.name if _KEEP_ALIVE_THREAD else None
    })

def start_keep_alive_thread(interval_sec=600):
    """
    全自動 Self-Ping 防休眠背景線程 (start_keep_alive_thread)
    定時向伺服器自身公開網址發送 HTTP GET 請求，防止 Render / 雲端容器因 15 分鐘無流量而自動休眠凍結。
    """
    global _KEEP_ALIVE_THREAD
    with _KEEP_ALIVE_LOCK:
        if _KEEP_ALIVE_THREAD is not None and _KEEP_ALIVE_THREAD.is_alive():
            return _KEEP_ALIVE_THREAD

        def _ping_loop():
            # 延遲 15 秒等待 Gunicorn / Flask 服務完全就緒監聽
            time.sleep(15)
            
            target_base = (
                os.environ.get('KEEP_ALIVE_URL')
                or os.environ.get('RENDER_EXTERNAL_URL')
                or "https://harvard-ent.onrender.com"
            ).rstrip('/')
            target_url = f"{target_base}/api/health"

            print(f"🚀 [Keep-Alive] 全自動防休眠背景線程啟動成功！目標: {target_url}，排程間隔: {interval_sec}秒")

            while True:
                try:
                    req = urllib.request.Request(
                        target_url,
                        headers={'User-Agent': 'HARVARD-KeepAlive-Worker/1.0'}
                    )
                    with urllib.request.urlopen(req, timeout=15) as resp:
                        status_code = resp.getcode()
                        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        print(f"💓 [Keep-Alive] Self-Ping 成功: {target_url} (HTTP {status_code}) at {now_str}")
                except Exception as e:
                    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"⚠️ [Keep-Alive] Self-Ping 嘗試中: {e} at {now_str}")

                time.sleep(interval_sec)

        _KEEP_ALIVE_THREAD = threading.Thread(
            target=_ping_loop,
            daemon=True,
            name="HARVARD-KeepAlive-Worker"
        )
        _KEEP_ALIVE_THREAD.start()
        return _KEEP_ALIVE_THREAD

# 於伺服器模組載入時自動啟動防休眠背景線程 (預設每 10 分鐘 Self-Ping 一次)
start_keep_alive_thread(interval_sec=600)

# Tunnel helper
import tunnel

@app.route('/api/tunnel-status')
def api_tunnel_status():
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url or os.environ.get('RENDER'):
        return jsonify({
            "running": True,
            "url": render_url or request.host_url.rstrip('/')
        })
    url = tunnel.get_public_url()
    is_running = tunnel.tunnel_process is not None and tunnel.tunnel_process.poll() is None
    return jsonify({
        "running": is_running,
        "url": url if is_running else None
    })

@app.route('/api/tunnel/start', methods=['POST'])
def api_tunnel_start():
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url or os.environ.get('RENDER'):
        return jsonify({
            "success": True,
            "url": render_url or request.host_url.rstrip('/'),
            "message": "目前已運行於 Render 雲端公開伺服器"
        })
    port = request.json.get('port', 5000) if request.json else 5000
    if tunnel.tunnel_process and tunnel.tunnel_process.poll() is None:
        return jsonify({"success": True, "url": tunnel.get_public_url(), "message": "Tunnel 已經在運行中"})
    try:
        url = tunnel.start_tunnel(port=port, wait_for_url=True, timeout=25)
        return jsonify({"success": True, "url": url, "message": "Tunnel 已成功建立！"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/tunnel/stop', methods=['POST'])
def api_tunnel_stop():
    tunnel.stop_tunnel()
    return jsonify({"success": True, "message": "Tunnel 已停止"})

@app.after_request
def add_header(response):
    if response.mimetype == 'text/html':
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

PAGE_META = {
    'hero': {
        'path': '/',
        'label': '首頁總覽',
        'title': '賀華實業股份有限公司 | HARVARD ENTERPRISES INC. - 鋁合金特殊輕金屬材料與精密加工領航者',
        'desc': '賀華實業股份有限公司創立於1973年，深耕台灣逾50年。專營中鋼鋁業全系列鋁合金、零零鋁箔、鋁捲片、平片、600mm特厚鋁板、圓棒及擠型精密分條裁切加工。'
    },
    'about': {
        'path': '/about',
        'label': '關於賀華 · 成立概要與經營理念',
        'title': '關於賀華 · 成立概要、基本資料與經營理念 | 賀華實業股份有限公司',
        'desc': '賀華實業創立於1973年，秉持「創新求是、追求卓越，互勉互惠、同享繁榮」理念，整合中鋼鋁業與日本住友輕金屬、日本大東工機等原廠資源，建構完整材料與設備服務體系。'
    },
    'network': {
        'path': '/network',
        'label': '全台服務網絡與廠區據點',
        'title': '全台營運據點 · 台北總公司、八里廠、新竹廠永旭材料、台中一廠、台中二廠、台南廠 | 賀華實業股份有限公司',
        'desc': '賀華實業立足全台六大營運及加工據點：台北總公司、台北八里倉儲中心、新竹廠永旭材料、台中一廠、台中二廠（Coil Slitting）及台南廠，提供即時裁切與物流調撥。'
    },
    'products': {
        'path': '/products',
        'label': '核心產品與旗艦材料系列',
        'title': '零零鋁箔、鋁捲片、平片、600mm特厚鋁板、圓棒與擠型 | 賀華實業股份有限公司',
        'desc': '常備1000至7000系列鋁合金板、捲、片、零零鋁箔、圓棒、擠型及精密分條機刀具配件，附原廠檢驗證明書。'
    },
    'specs': {
        'path': '/specs',
        'label': '現貨規格與現有模具檢索',
        'title': '現貨規格表與鋁擠型現有模具檢索 (3,081筆) | 賀華實業股份有限公司',
        'desc': '即時查詢賀華實業514項常備鋁板、圓棒、扁條現貨規格，以及2,557種免開模鋁圓管、扁條、方管、六角條現有模具尺寸資料庫。'
    },
    'machining': {
        'path': '/machining',
        'label': '工廠設備與精密加工能量',
        'title': '工廠設備 · 600mm特厚板立式裁切機、紅外線裁切機、精密分條機與貼膜壓平 | 賀華實業股份有限公司',
        'desc': '配備600mm特厚板立式裁切機、高精準直角度紅外線裁切機、台中二廠薄板分條機、永旭材料冷軋壓延機、退火熱處理爐與自動化倉儲設備。'
    },
    'cases': {
        'path': '/cases',
        'label': '代表實績與應用領域',
        'title': '代表實績案例 · 半導體、精密機械、光電與航太結構 | 賀華實業股份有限公司',
        'desc': '賀華實業以高品質鋁合金材料與高精度分條裁切技術，深耕半導體、航太、光電、車用電子與精密機械等各領域大廠客戶。'
    },
    'tech': {
        'path': '/tech',
        'label': '鋁的世界 · 特性選用與規範',
        'title': '鋁的世界 · 15大材料特性、選用原則、產品分類與常用標準規範 | 賀華實業股份有限公司',
        'desc': '深入解析鋁之輕量性、耐蝕性、導電導熱性等15大基本特性，提供耐蝕、強度、成型、切削、熔接選用原則與CNS/JIS/ASTM常用規範對照。'
    },
    'contact': {
        'path': '/contact',
        'label': '聯絡我們與線上估價諮詢',
        'title': '聯絡我們 · 台北總公司、八里廠、新竹廠、台中廠、台南廠 | 賀華實業股份有限公司',
        'desc': '賀華實業全台六大營運據點，歡迎透過線上表單、電話或傳真諮詢各類鋁合金材料、零零鋁箔、分條整平與特厚板裁切需求。'
    }
}


def _render_portal_page(page_key):
    meta = PAGE_META.get(page_key, PAGE_META['hero'])
    return render_template(
        'index.html',
        data=SITE_DATA,
        inventory_count=len(INVENTORY_DATA),
        active_page=page_key,
        page_meta=meta,
        all_pages_meta=PAGE_META
    )


@app.route('/')
def index():
    return _render_portal_page('hero')


@app.route('/about', strict_slashes=False)
def page_about():
    return _render_portal_page('about')


@app.route('/network', strict_slashes=False)
def page_network():
    return _render_portal_page('network')


@app.route('/products', strict_slashes=False)
@app.route('/materials', strict_slashes=False)
def page_products():
    return _render_portal_page('products')


@app.route('/specs', strict_slashes=False)
def page_specs():
    return _render_portal_page('specs')


@app.route('/machining', strict_slashes=False)
def page_machining():
    return _render_portal_page('machining')


@app.route('/cases', strict_slashes=False)
def page_cases():
    return _render_portal_page('cases')


@app.route('/tech', strict_slashes=False)
def page_tech():
    return _render_portal_page('tech')


@app.route('/contact', strict_slashes=False)
def page_contact():
    return _render_portal_page('contact')

@app.route('/api/site-data')
def api_site_data():
    return jsonify(SITE_DATA)

@app.route('/api/specs')
def api_specs():
    query = request.args.get('q', '').strip().lower()
    category = request.args.get('category', '').strip()
    group = request.args.get('group', '').strip()
    
    results = INVENTORY_DATA
    if group in ('stock', 'mold'):
        results = [item for item in results if item.get('group') == group]
        
    if category and category != '全部':
        results = [item for item in results if item.get('category') == category]
        
    if query:
        results = [
            item for item in results
            if query in item.get('material', '').lower()
            or query in item.get('dimension', '').lower()
            or query in item.get('size', '').lower()
            or query in item.get('note', '').lower()
            or query in item.get('category', '').lower()
            or query == str(item.get('no', '')).lower()
        ]
        
    # Categories list for filter dropdown
    categories = sorted(list(set(item['category'] for item in INVENTORY_DATA)))
    
    # Pagination
    try:
        page = max(1, int(request.args.get('page', 1)))
        per_page = max(10, min(100, int(request.args.get('per_page', 25))))
    except ValueError:
        page = 1
        per_page = 25
        
    total = len(results)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = results[start:end]
    
    return jsonify({
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
        "categories": categories,
        "items": paginated
    })

def _prune_tts_cache_if_needed(max_size_mb=120):
    try:
        cache_dir = os.path.join(BASE_DIR, 'static', 'audio', 'cache')
        if not os.path.exists(cache_dir):
            return
        files = [os.path.join(cache_dir, f) for f in os.listdir(cache_dir) if f.endswith('.mp3')]
        total_size = sum(os.path.getsize(p) for p in files if os.path.exists(p))
        if total_size > max_size_mb * 1024 * 1024:
            files.sort(key=lambda p: os.path.getmtime(p) if os.path.exists(p) else 0)
            while files and total_size > (max_size_mb * 0.7) * 1024 * 1024:
                oldest = files.pop(0)
                try:
                    total_size -= os.path.getsize(oldest)
                    os.remove(oldest)
                except OSError:
                    pass
    except Exception:
        pass


@app.route('/manifest.json')
def serve_manifest():
    return app.send_static_file('manifest.json')


@app.route('/api/tts')
def api_tts():
    text = request.args.get('text', '').strip()
    voice_key = request.args.get('voice', 'zen-male').strip()
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
        
    # Limit length for safety
    if len(text) > 800:
        text = text[:800]

    clean_text = _sanitize_tts_text(text)
    if not clean_text:
        return jsonify({"error": "No speakable text"}), 400

    # Map multi-language and Zen prosody presets
    if voice_key in ('en', 'en-US', 'en-US-JennyNeural', 'en-female'):
        actual_voice = 'en-US-JennyNeural'
        rate = '+0%'
        pitch = '+0Hz'
        speak_text = clean_text
    elif voice_key in ('en-male', 'en-US-GuyNeural'):
        actual_voice = 'en-US-GuyNeural'
        rate = '+0%'
        pitch = '+0Hz'
        speak_text = clean_text
    elif voice_key in ('ja', 'ja-JP', 'ja-JP-NanamiNeural', 'ja-female'):
        actual_voice = 'ja-JP-NanamiNeural'
        rate = '+0%'
        pitch = '+0Hz'
        speak_text = clean_text
    elif voice_key in ('ja-male', 'ja-JP-KeitaNeural'):
        actual_voice = 'ja-JP-KeitaNeural'
        rate = '+0%'
        pitch = '+0Hz'
        speak_text = clean_text
    elif voice_key in ('ko', 'ko-KR', 'ko-KR-SunHiNeural', 'ko-female'):
        actual_voice = 'ko-KR-SunHiNeural'
        rate = '+0%'
        pitch = '+0Hz'
        speak_text = clean_text
    elif voice_key in ('ko-male', 'ko-KR-InJoonNeural'):
        actual_voice = 'ko-KR-InJoonNeural'
        rate = '+0%'
        pitch = '+0Hz'
        speak_text = clean_text
    elif voice_key in ('zh-CN', 'zh-Hans', 'zh-CN-XiaoxiaoNeural', 'zh-female'):
        actual_voice = 'zh-CN-XiaoxiaoNeural'
        rate = '+0%'
        pitch = '+0Hz'
        speak_text = clean_text
    elif voice_key in ('zh-CN-male', 'zh-CN-YunjianNeural'):
        actual_voice = 'zh-CN-YunjianNeural'
        rate = '+0%'
        pitch = '+0Hz'
        speak_text = clean_text
    elif voice_key in ('zen-male', 'zh-TW-YunJheNeural'):
        actual_voice = 'zh-TW-YunJheNeural'
        rate = '-18%'
        pitch = '-10Hz'
        speak_text = clean_text.replace('。', '。…… ').replace('；', '；… ')
    elif voice_key == 'zen-female':
        actual_voice = 'zh-TW-HsiaoChenNeural'
        rate = '-15%'
        pitch = '-4Hz'
        speak_text = clean_text.replace('。', '。…… ').replace('；', '；… ')
    else:
        actual_voice = 'zh-TW-HsiaoChenNeural'
        rate = '+0%'
        pitch = '+0Hz'
        speak_text = clean_text

    # Generate unique cache hash including prosody parameters
    text_hash = hashlib.md5(f"{actual_voice}_{rate}_{pitch}_{speak_text}".encode('utf-8')).hexdigest()
    cache_dir = os.path.join(BASE_DIR, 'static', 'audio', 'cache')
    os.makedirs(cache_dir, exist_ok=True)
    cache_filename = f"tts_{text_hash}.mp3"
    cache_path = os.path.join(cache_dir, cache_filename)
    audio_url = f"/static/audio/cache/{cache_filename}"

    if os.path.exists(cache_path) and os.path.getsize(cache_path) > 500:
        return jsonify({"url": audio_url, "cached": True})

    # Fallback chain: preferred prosody -> neutral prosody -> plain text -> alternate voice
    if actual_voice.startswith('en-'):
        alt_voice = 'en-US-GuyNeural' if actual_voice == 'en-US-JennyNeural' else 'en-US-JennyNeural'
    elif actual_voice.startswith('ja-'):
        alt_voice = 'ja-JP-KeitaNeural' if actual_voice == 'ja-JP-NanamiNeural' else 'ja-JP-NanamiNeural'
    elif actual_voice.startswith('ko-'):
        alt_voice = 'ko-KR-InJoonNeural' if actual_voice == 'ko-KR-SunHiNeural' else 'ko-KR-SunHiNeural'
    else:
        alt_voice = 'zh-TW-HsiaoChenNeural' if actual_voice == 'zh-TW-YunJheNeural' else 'zh-TW-YunJheNeural'

    attempts = [
        (speak_text, actual_voice, rate, pitch),
        (clean_text, actual_voice, '+0%', '+0Hz'),
        (clean_text, alt_voice, '+0%', '+0Hz'),
    ]
    last_error = None
    for a_text, a_voice, a_rate, a_pitch in attempts:
        ok, err = _synthesize_tts_to_file(a_text, a_voice, a_rate, a_pitch, cache_path)
        if ok:
            _prune_tts_cache_if_needed()
            return jsonify({"url": audio_url, "cached": False})
        last_error = err

    return jsonify({"error": f"TTS unavailable: {last_error}", "fallback": "browser"}), 503


def _sanitize_tts_text(text):
    """Normalize text so the Edge neural voice reliably produces audio."""
    t = str(text or '')
    t = re.sub(r'(\d)xxx', r'\g<1>000 系列', t, flags=re.IGNORECASE)
    t = t.replace('·', '，').replace('／', '、').replace(' / ', '、').replace('/', '、')
    t = t.replace('φ', '直徑').replace('ψ', '直徑').replace('×', '乘').replace('*', '乘')
    t = t.replace('±', '正負').replace('≥', '大於等於').replace('≤', '小於等於').replace('≈', '約')
    t = t.replace('「', '').replace('」', '').replace('"', '').replace("'", '')
    t = t.replace('<', ' ').replace('>', ' ').replace('&', '與')
    t = re.sub(r'。{2,}', '。', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t[:800]


def _synthesize_tts_to_file(text, voice, rate, pitch, final_path):
    tmp_path = final_path + '.part'
    try:
        async def do_tts():
            tts = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
            await tts.save(tmp_path)

        asyncio.run(do_tts())
        if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 500:
            os.replace(tmp_path, final_path)
            return True, None
        return False, 'empty audio'
    except Exception as e:
        return False, str(e)
    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except OSError:
            pass

# Rate limiter for RFQ inquiries
CONTACT_RATE_LIMIT = {}
CONTACT_RATE_LOCK = threading.Lock()

def _is_contact_rate_limited(client_ip, max_requests=5, window_seconds=60):
    now = time.time()
    with CONTACT_RATE_LOCK:
        history = CONTACT_RATE_LIMIT.get(client_ip, [])
        history = [t for t in history if now - t < window_seconds]
        if len(history) >= max_requests:
            CONTACT_RATE_LIMIT[client_ip] = history
            return True
        history.append(now)
        CONTACT_RATE_LIMIT[client_ip] = history
        return False

def _normalize_inquiry(item):
    item.setdefault('status', 'pending')      # pending | quoting | closed | archived
    item.setdefault('branch', '未指派')        # 未指派 | 台北總公司 | 台中廠 | 台南雙廠區
    item.setdefault('adminNote', '')
    item.setdefault('drawingUrl', '')
    item.setdefault('updatedAt', item.get('timestamp', ''))
    item.setdefault('emailSent', False)
    return item


def load_inquiries():
    try:
        items = db.get_all_inquiries()
        if items:
            return items
    except Exception:
        pass

    with INQUIRIES_LOCK:
        if not os.path.exists(INQUIRIES_FILE):
            return []
        try:
            with open(INQUIRIES_FILE, 'r', encoding='utf-8') as f:
                items = json.load(f)
                return [_normalize_inquiry(i) for i in items if isinstance(i, dict)]
        except Exception:
            return []


def save_inquiries(items, sync_cloud=False):
    try:
        for it in items:
            db.add_inquiry(it, sync_cloud=sync_cloud)
    except Exception:
        pass

    with INQUIRIES_LOCK:
        os.makedirs(os.path.dirname(INQUIRIES_FILE), exist_ok=True)
        try:
            with open(INQUIRIES_FILE, 'w', encoding='utf-8') as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


def _next_ticket_id(items=None):
    try:
        return db.next_ticket_id()
    except Exception:
        pass
    items = items or []
    max_num = 1000
    for item in items:
        raw_id = str(item.get('id', ''))
        if raw_id.startswith('REQ-'):
            try:
                max_num = max(max_num, int(raw_id.split('-', 1)[1]))
            except ValueError:
                pass
    return f"REQ-{max_num + 1}"


def _async_notify_inquiry(inquiry_copy):
    cfg = mailer.get_smtp_config()
    if not cfg.get('enabled'):
        return
    tid = inquiry_copy.get('id')
    try:
        mailer.send_inquiry_email(inquiry_copy, custom_cfg=cfg)
        if tid:
            db.update_inquiry(tid, {'emailSent': True, 'emailError': ''})
    except Exception as e:
        if tid:
            db.update_inquiry(tid, {'emailSent': False, 'emailError': str(e)})


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get('is_admin'):
            return jsonify({"success": False, "error": "未授權，請先登入管理後台"}), 401
        return fn(*args, **kwargs)
    return wrapper


@app.route('/api/contact', methods=['POST'])
def api_contact():
    try:
        raw = request.get_json(silent=True) or request.form.to_dict() or {}
        
        # 1. Anti-bot Honeypot check: If the hidden honeypot field is filled, silently pretend success
        if raw.get('website_hp'):
            return jsonify({
                "success": True,
                "message": "感謝您的諮詢！我們的業務工程師將於 24 小時內與您聯繫。",
                "ticket_id": "REQ-1000"
            })

        # 2. Rate limiting check (max 5 submissions per 60s per client IP)
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr or 'unknown').split(',')[0].strip()
        if _is_contact_rate_limited(client_ip):
            return jsonify({
                "success": False,
                "error": "您的詢價提交過於頻繁，請稍候 1 分鐘後再送出。"
            }), 429

        # 3. Input validation
        company = str(raw.get('companyName', '')).strip()
        person = str(raw.get('contactPerson', '')).strip()
        phone = str(raw.get('contactPhone', '')).strip()
        email = str(raw.get('contactEmail', '')).strip()
        material = str(raw.get('inquiryMaterial', '')).strip()
        message = str(raw.get('inquiryMessage', '')).strip()
        drawing_url = str(raw.get('drawingUrl', '')).strip()

        if not (company or person) and not (phone or email):
            return jsonify({
                "success": False,
                "error": "請填寫您的聯絡人姓名與聯絡電話或電子郵件，以便業務工程師向您回覆報價。"
            }), 400

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        inquiries = load_inquiries()
        ticket_id = _next_ticket_id(inquiries)

        # Handle optional CAD/PDF/DXF drawing file upload
        drawing_file = request.files.get('drawing_file')
        if drawing_file and drawing_file.filename:
            orig_name = drawing_file.filename
            ext = os.path.splitext(orig_name)[1].lower()
            allowed = {'.pdf', '.dxf', '.dwg', '.step', '.stp', '.iges', '.igs', '.png', '.jpg', '.jpeg', '.zip', '.rar', '.7z'}
            if ext in allowed:
                os.makedirs(DRAWINGS_DIR, exist_ok=True)
                clean_name = re.sub(r'[^\w\.-]', '_', os.path.basename(orig_name))
                saved_filename = f"{ticket_id}_{int(time.time())}_{clean_name}"
                dest_path = os.path.join(DRAWINGS_DIR, saved_filename)
                file_bytes = drawing_file.read()
                with open(dest_path, 'wb') as f:
                    f.write(file_bytes)
                # Persist binary drawing into Cloud/SQLite DB so it survives Render container resets
                db.save_drawing_file(saved_filename, ticket_id, drawing_file.mimetype, file_bytes)
                file_rel_url = f"/static/uploads/drawings/{saved_filename}"
                if drawing_url:
                    drawing_url = f"{file_rel_url} | 雲端連結: {drawing_url}"
                else:
                    drawing_url = file_rel_url

        new_item = {
            "id": ticket_id,
            "companyName": company,
            "contactPerson": person,
            "contactPhone": phone,
            "contactEmail": email,
            "inquiryMaterial": material,
            "inquiryMessage": message,
            "drawingUrl": drawing_url,
            "timestamp": now_str,
            "updatedAt": now_str,
            "status": "pending",
            "branch": "未指派",
            "adminNote": "",
            "emailSent": False
        }
        db.add_inquiry(new_item, sync_cloud=True)
        inquiries.append(new_item)
        save_inquiries(inquiries, sync_cloud=False)

        # Background SMTP notification
        threading.Thread(target=_async_notify_inquiry, args=(dict(new_item),), daemon=True).start()

        return jsonify({
            "success": True,
            "message": "感謝您的諮詢！我們的業務工程師將於 24 小時內與您聯繫。",
            "ticket_id": new_item['id'],
            "drawing_url": drawing_url
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================================================
#  Official Quotation & Printable PDF Export Routes
# ==========================================================================

@app.route('/quotation/<ticket_id>')
def view_quotation(ticket_id):
    ticket_id = ticket_id.strip()
    inquiry = None
    try:
        inquiry = db.get_inquiry_by_id(ticket_id)
    except Exception:
        pass
    if not inquiry:
        # Fallback to inquiries file/cache
        for item in load_inquiries():
            if str(item.get('id', '')).upper() == ticket_id.upper():
                inquiry = item
                break
    if not inquiry:
        inquiry = {
            "id": ticket_id,
            "companyName": "貴客戶",
            "contactPerson": "採購專員",
            "contactPhone": "—",
            "contactEmail": "—",
            "inquiryMaterial": "客製鋁合金規格材料",
            "inquiryMessage": "請聯繫賀華實業業務工程師進行細部圖面與精密切割規格確認。",
            "drawingUrl": "",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d"),
            "status": "pending",
            "branch": "台北廠(八里倉庫) / 台中神岡雙廠區"
        }
    return render_template('quotation.html', inquiry=inquiry)


@app.route('/quotation/preview', methods=['GET', 'POST'])
def preview_quotation():
    raw = request.get_json(silent=True) or request.form.to_dict() or request.args.to_dict() or {}
    ticket_id = f"QPREV-{datetime.datetime.now().strftime('%Y%m%d%H%M')}"
    inquiry = {
        "id": raw.get('id') or ticket_id,
        "companyName": raw.get('companyName') or raw.get('company') or "貴客戶",
        "contactPerson": raw.get('contactPerson') or raw.get('person') or "採購主管 / 工程師",
        "contactPhone": raw.get('contactPhone') or raw.get('phone') or "—",
        "contactEmail": raw.get('contactEmail') or raw.get('email') or "—",
        "inquiryMaterial": raw.get('material') or raw.get('inquiryMaterial') or "客製鋁合金規格材料",
        "inquiryMessage": raw.get('message') or raw.get('inquiryMessage') or "依據線上工程計算機試算結果產出之估價意向明細。",
        "detectedAlloy": raw.get('alloy') or "AL 鋁合金",
        "itemQty": raw.get('qty') or "1",
        "calcWeight": raw.get('weight') or "依試算",
        "machiningReq": raw.get('machining') or "精密切割 / 表面保護",
        "drawingUrl": raw.get('drawingUrl') or "",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": "pending",
        "branch": "台北廠(八里倉庫) / 台中神岡雙廠區"
    }
    return render_template('quotation.html', inquiry=inquiry)


# ==========================================================================
#  Admin Backend Routes (/admin & /api/admin/*)
# ==========================================================================

@app.route('/admin')
def admin_dashboard():
    is_logged_in = bool(session.get('is_admin'))
    is_render = bool(os.environ.get('RENDER') or os.environ.get('RENDER_EXTERNAL_URL'))
    return render_template('admin.html', is_logged_in=is_logged_in, is_render=is_render)


@app.route('/api/admin/login', methods=['POST'])
def api_admin_login():
    body = request.json or {}
    password = str(body.get('password', '')).strip()
    expected = mailer.get_admin_password()
    if password and hmac.compare_digest(password.encode('utf-8'), expected.encode('utf-8')):
        session['is_admin'] = True
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "管理密碼錯誤，請重新輸入"}), 401


@app.route('/api/admin/logout', methods=['POST'])
def api_admin_logout():
    session.pop('is_admin', None)
    return jsonify({"success": True})


@app.route('/api/admin/inquiries', methods=['GET'])
@admin_required
def api_admin_inquiries():
    items = load_inquiries()
    items_sorted = list(reversed(items))
    stats = {
        "total": len(items),
        "pending": sum(1 for i in items if i.get('status') == 'pending'),
        "quoting": sum(1 for i in items if i.get('status') == 'quoting'),
        "closed": sum(1 for i in items if i.get('status') == 'closed'),
        "archived": sum(1 for i in items if i.get('status') == 'archived'),
    }
    smtp_cfg = mailer.get_smtp_config()
    storage_status = db.get_storage_status()
    return jsonify({
        "success": True,
        "items": items_sorted,
        "stats": stats,
        "smtpEnabled": smtp_cfg['enabled'],
        "notifyEmail": smtp_cfg['notify_email'],
        "isRender": bool(os.environ.get('RENDER') or os.environ.get('RENDER_EXTERNAL_URL')),
        "storage": storage_status
    })


@app.route('/api/admin/inquiries/<ticket_id>', methods=['PATCH'])
@admin_required
def api_admin_update_inquiry(ticket_id):
    body = request.json or {}
    updates = {}
    if 'status' in body and body['status'] in ('pending', 'quoting', 'closed', 'archived'):
        updates['status'] = body['status']
    if 'branch' in body:
        updates['branch'] = str(body['branch']).strip() or '未指派'
    if 'adminNote' in body:
        updates['adminNote'] = str(body['adminNote']).strip()

    updated = db.update_inquiry(ticket_id, updates)
    if not updated:
        return jsonify({"success": False, "error": "找不到該筆詢價單"}), 404

    items = load_inquiries()
    save_inquiries(items, sync_cloud=False)
    return jsonify({"success": True, "item": updated})


@app.route('/api/admin/inquiries', methods=['POST'])
@admin_required
def api_admin_create_inquiry():
    raw = request.json or {}
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    item = {
        "id": db.next_ticket_id(),
        "companyName": str(raw.get('companyName', '')).strip(),
        "contactPerson": str(raw.get('contactPerson', '')).strip(),
        "contactPhone": str(raw.get('contactPhone', '')).strip(),
        "contactEmail": str(raw.get('contactEmail', '')).strip(),
        "inquiryMaterial": str(raw.get('inquiryMaterial', '')).strip(),
        "inquiryMessage": str(raw.get('inquiryMessage', '')).strip(),
        "drawingUrl": str(raw.get('drawingUrl', '')).strip(),
        "timestamp": now_str,
        "updatedAt": now_str,
        "status": str(raw.get('status', 'pending')).strip() or 'pending',
        "branch": str(raw.get('branch', '未指派')).strip() or '未指派',
        "adminNote": str(raw.get('adminNote', '')).strip(),
        "emailSent": False
    }
    saved = db.add_inquiry(item)
    return jsonify({"success": True, "item": saved, "message": "詢價單已成功手動建立！"})


@app.route('/api/admin/inquiries/<ticket_id>', methods=['DELETE'])
@admin_required
def api_admin_delete_inquiry(ticket_id):
    db.delete_inquiry(ticket_id)
    items = load_inquiries()
    new_items = [i for i in items if i.get('id') != ticket_id]
    try:
        with open(INQUIRIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_items, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return jsonify({"success": True, "message": "詢價單已成功刪除"})


# ==========================================================================
#  Specs CRUD APIs (/api/admin/specs)
# ==========================================================================

@app.route('/api/admin/specs', methods=['GET', 'POST'])
@admin_required
def api_admin_specs():
    global INVENTORY_DATA
    if request.method == 'POST':
        data = request.json or {}
        mat = str(data.get('material', '')).strip()
        dim = str(data.get('dimension', '')).strip()
        if not mat and not dim:
            return jsonify({"success": False, "error": "請至少填寫材質或規格尺寸"}), 400

        new_spec = db.add_spec(data)
        INVENTORY_DATA = db.get_all_specs()
        # Backup to JSON
        try:
            with open(SPECS_PATH, 'w', encoding='utf-8') as f:
                json.dump(INVENTORY_DATA, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        return jsonify({"success": True, "item": new_spec, "message": "現貨規格已成功新增！"})

    # GET Specs list with pagination
    q = request.args.get('q', '').strip().lower()
    cat = request.args.get('category', '').strip()
    group = request.args.get('group', '').strip()

    results = INVENTORY_DATA
    if group in ('stock', 'mold'):
        results = [x for x in results if x.get('group') == group]
    if cat and cat != '全部':
        results = [x for x in results if x.get('category') == cat]
    if q:
        results = [
            x for x in results
            if q in str(x.get('material', '')).lower()
            or q in str(x.get('dimension', '')).lower()
            or q in str(x.get('size', '')).lower()
            or q in str(x.get('note', '')).lower()
            or q in str(x.get('category', '')).lower()
            or q == str(x.get('no', '')).lower()
            or q == str(x.get('id', '')).lower()
        ]

    try:
        page = max(1, int(request.args.get('page', 1)))
        per_page = max(10, min(100, int(request.args.get('per_page', 25))))
    except ValueError:
        page = 1
        per_page = 25

    total = len(results)
    start = (page - 1) * per_page
    paginated = results[start:start + per_page]
    categories = sorted(list(set(x['category'] for x in INVENTORY_DATA if x.get('category'))))

    return jsonify({
        "success": True,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
        "categories": categories,
        "items": paginated
    })


@app.route('/api/admin/specs/<int:spec_id>', methods=['PUT', 'DELETE'])
@admin_required
def api_admin_spec_detail(spec_id):
    global INVENTORY_DATA
    if request.method == 'DELETE':
        ok = db.delete_spec(spec_id)
        if not ok:
            return jsonify({"success": False, "error": "找不到該筆規格或已被刪除"}), 404
        INVENTORY_DATA = db.get_all_specs()
        # Backup to JSON
        try:
            with open(SPECS_PATH, 'w', encoding='utf-8') as f:
                json.dump(INVENTORY_DATA, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        return jsonify({"success": True, "message": "規格已成功自資料庫刪除"})

    # PUT: Edit
    data = request.json or {}
    updated = db.update_spec(spec_id, data)
    if not updated:
        return jsonify({"success": False, "error": "找不到該筆規格"}), 404
    INVENTORY_DATA = db.get_all_specs()
    # Backup to JSON
    try:
        with open(SPECS_PATH, 'w', encoding='utf-8') as f:
            json.dump(INVENTORY_DATA, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return jsonify({"success": True, "item": updated, "message": "規格已成功儲存更新！"})


@app.route('/api/admin/inquiries/<ticket_id>/resend-email', methods=['POST'])
@admin_required
def api_admin_resend_email(ticket_id):
    items = load_inquiries()
    target = next((i for i in items if i.get('id') == ticket_id), None)
    if not target:
        return jsonify({"success": False, "error": "找不到該筆詢價單"}), 404
    try:
        mailer.send_inquiry_email(target)
        db.update_inquiry(ticket_id, {'emailSent': True, 'emailError': ''})
        return jsonify({"success": True, "message": "已成功補寄通知信！"})
    except Exception as e:
        db.update_inquiry(ticket_id, {'emailSent': False, 'emailError': str(e)})
        return jsonify({"success": False, "error": str(e)}), 400


@app.route('/api/admin/inquiries/export', methods=['GET'])
@admin_required
def api_admin_export_csv():
    status_filter = request.args.get('status', 'all')
    items = list(reversed(load_inquiries()))
    if status_filter and status_filter != 'all':
        items = [i for i in items if i.get('status') == status_filter]

    status_labels = {
        'pending': '待處理',
        'quoting': '已報價/跟進中',
        'closed': '已成交結案',
        'archived': '已取消/歸檔'
    }

    output = io.StringIO()
    output.write('\ufeff')  # UTF-8 BOM for Microsoft Excel Traditional Chinese compatibility
    writer = csv.writer(output)
    writer.writerow([
        '詢價單號', '處理狀態', '指派廠區', '建立時間', '最後更新',
        '公司寶號', '聯絡人', '聯絡電話', '電子郵件',
        '材料型號與規格需求', '圖面連結/說明', '需求數量與加工說明', '內部業務備註', 'Email通知狀態'
    ])
    for i in items:
        writer.writerow([
            i.get('id', ''),
            status_labels.get(i.get('status', 'pending'), i.get('status', '')),
            i.get('branch', '未指派'),
            i.get('timestamp', ''),
            i.get('updatedAt', ''),
            i.get('companyName', ''),
            i.get('contactPerson', ''),
            i.get('contactPhone', ''),
            i.get('contactEmail', ''),
            i.get('inquiryMaterial', ''),
            i.get('drawingUrl', ''),
            i.get('inquiryMessage', ''),
            i.get('adminNote', ''),
            '已寄送' if i.get('emailSent') else '未寄送'
        ])

    filename = f"harvard_inquiries_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    return Response(
        output.getvalue(),
        mimetype='text/csv; charset=utf-8',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )


@app.route('/api/admin/settings', methods=['GET', 'POST'])
@admin_required
def api_admin_settings():
    if request.method == 'GET':
        cfg = mailer.get_smtp_config()
        storage = db.get_storage_status()
        return jsonify({
            "success": True,
            "smtp_host": cfg['smtp_host'],
            "smtp_port": cfg['smtp_port'],
            "smtp_user": cfg['smtp_user'],
            "has_smtp_pass": bool(cfg['smtp_pass']),
            "notify_email": cfg['notify_email'],
            "enabled": cfg['enabled'],
            "from_env": cfg['from_env'],
            "has_env_admin_pwd": bool(os.environ.get('ADMIN_PASSWORD')),
            "github_repo": storage['github_repo'],
            "github_branch": storage['github_branch'],
            "has_github_token": storage['has_github_token'],
            "google_sheets_webhook_url": storage['gsheets_url'],
            "storage": storage
        })

    body = request.json or {}
    updates = {}
    if 'smtp_host' in body:
        updates['smtp_host'] = str(body['smtp_host']).strip() or 'smtp.gmail.com'
    if 'smtp_port' in body:
        try:
            updates['smtp_port'] = int(body['smtp_port'])
        except ValueError:
            updates['smtp_port'] = 587
    if 'smtp_user' in body:
        updates['smtp_user'] = str(body['smtp_user']).strip()
    if body.get('smtp_pass'):
        updates['smtp_pass'] = str(body['smtp_pass']).strip()
    if 'notify_email' in body:
        updates['notify_email'] = str(body['notify_email']).strip()
    if body.get('new_admin_password'):
        updates['admin_password'] = str(body['new_admin_password']).strip()
    if 'github_repo' in body:
        updates['github_repo'] = str(body['github_repo']).strip() or 'Albertyoung22/harvard-ent'
    if 'github_branch' in body:
        updates['github_branch'] = str(body['github_branch']).strip() or 'cloud-backup'
    if body.get('github_token'):
        updates['github_token'] = str(body['github_token']).strip()
    if 'google_sheets_webhook_url' in body:
        updates['google_sheets_webhook_url'] = str(body['google_sheets_webhook_url']).strip()

    mailer.save_local_config(updates)
    cfg = mailer.get_smtp_config()
    storage = db.get_storage_status()
    return jsonify({
        "success": True,
        "enabled": cfg['enabled'],
        "storage": storage,
        "message": "設定已儲存！"
    })


@app.route('/api/admin/sync-github', methods=['POST'])
@admin_required
def api_admin_sync_github():
    body = request.json or {}
    updates = {}
    if body.get('github_repo'):
        updates['github_repo'] = str(body['github_repo']).strip()
    if body.get('github_branch'):
        updates['github_branch'] = str(body['github_branch']).strip()
    if body.get('github_token'):
        updates['github_token'] = str(body['github_token']).strip()
    if updates:
        mailer.save_local_config(updates)
    try:
        res = db.sync_all_to_github(custom_cfg={
            'repo': body.get('github_repo'),
            'branch': body.get('github_branch'),
            'token': body.get('github_token')
        })
        return jsonify({
            "success": True,
            "message": f"GitHub 雙向同步成功！已備份 {res['pushed']} 筆詢價單至 {res['repo']} ({res['branch']} 分支)，並自雲端還原 {res['restored']} 筆紀錄。",
            "details": res
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"GitHub 同步失敗：{e}"}), 400


@app.route('/api/admin/sync-gsheets', methods=['POST'])
@admin_required
def api_admin_sync_gsheets():
    body = request.json or {}
    custom_url = str(body.get('google_sheets_webhook_url', '')).strip()
    if custom_url:
        mailer.save_local_config({'google_sheets_webhook_url': custom_url})
    try:
        res = db.sync_all_to_google_sheets(custom_url=custom_url or None)
        return jsonify({
            "success": True,
            "message": f"Google 試算表雙向同步成功！已上傳 {res['pushed']} 筆詢價單，並自雲端還原 {res['restored']} 筆歷史紀錄。",
            "details": res
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"同步失敗：{e}"}), 400


@app.route('/api/admin/test-email', methods=['POST'])
@admin_required
def api_admin_test_email():
    body = request.json or {}
    current_cfg = mailer.get_smtp_config()
    test_cfg = {
        'smtp_host': str(body.get('smtp_host') or current_cfg['smtp_host']).strip(),
        'smtp_port': int(body.get('smtp_port') or current_cfg['smtp_port']),
        'smtp_user': str(body.get('smtp_user') or current_cfg['smtp_user']).strip(),
        'smtp_pass': str(body.get('smtp_pass') or current_cfg['smtp_pass']).strip(),
        'notify_email': str(body.get('notify_email') or current_cfg['notify_email']).strip(),
    }
    test_cfg['enabled'] = bool(test_cfg['smtp_host'] and test_cfg['smtp_user'] and test_cfg['smtp_pass'] and test_cfg['notify_email'])
    try:
        mailer.send_test_email(custom_cfg=test_cfg)
        return jsonify({"success": True, "message": f"測試信已成功寄送至 {test_cfg['notify_email']}！請檢查收件匣。"})
    except Exception as e:
        return jsonify({"success": False, "error": f"寄送失敗：{e}"}), 400


# ==========================================================================
#  AI Customer Service & Google OR-Tools CP-SAT Optimization APIs
# ==========================================================================
import ai_assistant


@app.route('/api/ai/chat', methods=['POST'])
def api_ai_chat():
    body = request.json or {}
    msg = str(body.get('message', '')).strip()
    lang = str(body.get('lang', 'zh-TW')).strip()
    result = ai_assistant.process_ai_chat(msg, INVENTORY_DATA, lang=lang)
    return jsonify({"success": True, **result})


@app.route('/api/ai/cutting-stock', methods=['POST'])
def api_ai_cutting_stock():
    body = request.json or {}
    stock_len = body.get('stock_length_mm', 3000)
    kerf = body.get('kerf_mm', 3)
    demands = body.get('demands', [])
    plan = ai_assistant.solve_cutting_stock_cpsat(
        stock_length_mm=stock_len,
        kerf_mm=kerf,
        demands=demands
    )
    return jsonify(plan)



# ==========================================================================
#  Harvard Original 61 Images & Google OR-Tools CP-SAT Extended Endpoints
# ==========================================================================
import cpsat_optimizer

@app.route('/images/<path:filename>')
def serve_harvard_images(filename):
    clean_name = os.path.basename(filename)
    search_dirs = [
        os.path.join(BASE_DIR, 'images'),
        os.path.join(BASE_DIR, 'static', 'images'),
        os.path.join(BASE_DIR, 'static', 'img_crawled'),
        os.path.join(BASE_DIR, 'ch', 'images'),
        os.path.join(BASE_DIR, 'en', 'images'),
        os.path.join(BASE_DIR, 'jp', 'images')
    ]
    for d in search_dirs:
        p1 = os.path.join(d, filename)
        if os.path.isfile(p1):
            return send_from_directory(d, filename)
        p2 = os.path.join(d, clean_name)
        if os.path.isfile(p2):
            return send_from_directory(d, clean_name)
    return send_from_directory(os.path.join(BASE_DIR, 'static', 'images'), 'logo_brand.png')

@app.route('/api/alloys', methods=['GET'])
def api_get_alloys():
    return jsonify({
        "count": len(cpsat_optimizer.ALLOY_DB),
        "alloys": cpsat_optimizer.ALLOY_DB,
        "plants": cpsat_optimizer.PLANTS
    })

@app.route('/api/cpsat/1d-cutting', methods=['POST'])
def api_cpsat_1d_cutting():
    payload = request.get_json(silent=True) or {}
    mother_len = int(payload.get("mother_length") or payload.get("stock_length") or 3000)
    kerf = int(float(payload.get("kerf", 3)))
    raw_demands = payload.get("demands", [
        {"width": 800, "qty": 3, "label": "結構件A"},
        {"width": 550, "qty": 4, "label": "精密治具B"},
        {"width": 420, "qty": 5, "label": "半導體支架C"},
    ])
    norm_demands = []
    for idx, d in enumerate(raw_demands):
        w = int(d.get("width") or d.get("length") or 100)
        q = int(d.get("qty") or 1)
        norm_demands.append({"id": d.get("id", f"ITEM-{idx+1}"), "label": d.get("label", f"{w}mm"), "width": w, "qty": q})
    result = cpsat_optimizer.solve_1d_cutting_stock(mother_length=mother_len, demands=norm_demands, kerf=kerf, trim_allowance=0)
    return jsonify(result)

@app.route('/api/cpsat/2d-plate', methods=['POST'])
def api_cpsat_2d_plate():
    payload = request.get_json(silent=True) or {}
    plate_width = int(payload.get("plate_width", 1250))
    plate_height = int(payload.get("plate_height", 2500))
    kerf = int(payload.get("kerf", 4))
    allow_rotation = bool(payload.get("allow_rotation", True))
    raw_pieces = payload.get("pieces", [
        {"w": 600, "h": 800, "qty": 2, "label": "腔體底板A"},
        {"w": 500, "h": 600, "qty": 3, "label": "精密治具板B"},
        {"w": 400, "h": 450, "qty": 3, "label": "光學支撐板C"},
    ])
    norm_pieces = []
    for idx, p in enumerate(raw_pieces):
        w = int(p.get("w") or p.get("width") or 300)
        h = int(p.get("h") or p.get("height") or 300)
        q = int(p.get("qty") or 1)
        norm_pieces.append({"id": p.get("id", f"P{idx+1}"), "label": p.get("label", f"{w}x{h}"), "w": w, "h": h, "qty": q})
    result = cpsat_optimizer.solve_2d_plate_cutting(
        plate_width=plate_width,
        plate_height=plate_height,
        pieces=norm_pieces,
        kerf=kerf,
        allow_rotation=allow_rotation,
    )
    # Provide flat placements of Plate #1 for convenient single-SVG rendering as well
    first_plate_placements = result.get("plates", [{}])[0].get("placements", []) if result.get("plates") else []
    result["placements"] = first_plate_placements
    result["placed_count"] = result.get("total_pieces_placed", len(first_plate_placements))
    result["total_requested"] = sum(p["qty"] for p in norm_pieces)
    result["area_efficiency_pct"] = result.get("overall_utilization_pct", 0)
    result["bounding_height"] = max((p["y"] + p["h"] for p in first_plate_placements), default=0)
    return jsonify(result)

@app.route('/api/cpsat/schedule', methods=['POST'])
def api_cpsat_schedule():
    payload = request.get_json(silent=True) or {}
    orders = payload.get("orders", None)
    result = cpsat_optimizer.solve_multi_plant_schedule(orders=orders)
    result["makespan_hours"] = result.get("makespan_hr", 0)
    result["schedule"] = [
        {
            "plant_name": a["assigned_plant_name"],
            "machine": a["process_type"],
            "job_name": f"{a['customer']} · {a['product']}",
            "start_hr": a["start_hr"],
            "end_hr": a["end_hr"],
            "duration_hr": a["duration_hr"]
        }
        for a in result.get("assignments", [])
    ]
    return jsonify(result)

@app.route('/api/cpsat/alloy-select', methods=['POST'])
def api_cpsat_alloy_select():
    payload = request.get_json(silent=True) or {}
    min_tensile = int(payload.get("min_tensile_mpa", 250))
    min_strength_score = min(98, max(40, int(min_tensile / 5.5)))
    weights = payload.get("weights", {})
    min_corr = 85 if weights.get("corrosion", 5) >= 9 else 65
    result = cpsat_optimizer.solve_alloy_recommendation(
        min_corrosion=min_corr,
        min_strength=min_strength_score,
        min_formability=55,
        min_machinability=65,
        min_weldability=50
    )
    recs = []
    for r in result.get("top_recommendations", []):
        recs.append({
            "code": r["code"],
            "temper": "T6 / T651 / H112" if r["heat_treatable"] else "H14 / H32 / O",
            "name_zh": f"{r['series']} · {r['characteristics']}",
            "cpsat_score": r["match_score"],
            "tensile_mpa": r["scores"]["strength"] * 5,
            "yield_mpa": int(r["scores"]["strength"] * 4.2),
            "hardness_hb": int(r["scores"]["strength"] * 1.5),
            "applications": r["applications"]
        })
    result["recommendations"] = recs
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    try:
        from waitress import serve
        print(f"[Waitress] Starting Harvard Enterprises High-Tech Server on http://0.0.0.0:{port}")
        serve(app, host='0.0.0.0', port=port, threads=8)
    except ImportError:
        app.run(host='0.0.0.0', port=port, debug=False)


