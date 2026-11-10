import os
import sys
import json
import base64
import sqlite3
import datetime
import threading
import urllib.request
import urllib.parse
import urllib.error

BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'harvard.db')
SPECS_JSON_PATH = os.path.join(BASE_DIR, 'data', 'inventory_specs.json')
INQUIRIES_JSON_PATH = os.path.join(BASE_DIR, 'data', 'inquiries.json')
INQUIRIES_EXAMPLE_PATH = os.path.join(BASE_DIR, 'data', 'inquiries.example.json')
LOCAL_CONFIG_PATH = os.path.join(BASE_DIR, 'data', 'admin_config.json')

DB_LOCK = threading.Lock()

# Check for external Cloud PostgreSQL connection string (Neon / Supabase / Render Postgres)
def _get_postgres_url():
    url = (
        os.environ.get('DATABASE_URL', '').strip()
        or os.environ.get('POSTGRES_URL', '').strip()
    )
    if not url and os.path.exists(LOCAL_CONFIG_PATH):
        try:
            with open(LOCAL_CONFIG_PATH, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                url = str(cfg.get('database_url', '')).strip()
        except Exception:
            pass
    if url.startswith('postgres://'):
        url = 'postgresql://' + url[len('postgres://'):]
    return url

POSTGRES_URL = _get_postgres_url()
USE_POSTGRES = False
psycopg2 = None
RealDictCursor = None

if POSTGRES_URL:
    try:
        import psycopg2 as _psycopg2
        from psycopg2.extras import RealDictCursor as _RealDictCursor, execute_batch as _pg_execute_batch
        psycopg2 = _psycopg2
        RealDictCursor = _RealDictCursor
        USE_POSTGRES = True
    except ImportError:
        print("[!] 偵測到 DATABASE_URL 但尚未安裝 psycopg2-binary，將自動降級使用本機 SQLite。")
        USE_POSTGRES = False


class _DBSession:
    """
    Unified context manager for both Cloud PostgreSQL and Local SQLite.
    Automatically translates parameter placeholders ('?' -> '%s') when running on PostgreSQL.
    """
    def __init__(self):
        self.conn = None
        self.is_pg = USE_POSTGRES

    def __enter__(self):
        if self.is_pg:
            self.conn = psycopg2.connect(POSTGRES_URL, connect_timeout=15)
        else:
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
            self.conn = sqlite3.connect(DB_PATH, timeout=20.0)
            self.conn.row_factory = sqlite3.Row
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            try:
                if exc_type is None:
                    self.conn.commit()
                else:
                    self.conn.rollback()
            except Exception:
                pass
            finally:
                try:
                    self.conn.close()
                except Exception:
                    pass

    def _adapt_sql(self, sql):
        if self.is_pg:
            return sql.replace('?', '%s')
        return sql

    def execute(self, sql, params=()):
        adapted = self._adapt_sql(sql)
        if self.is_pg:
            cur = self.conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(adapted, params)
            return cur
        else:
            return self.conn.execute(adapted, params)

    def executemany(self, sql, seq_of_params):
        adapted = self._adapt_sql(sql)
        if self.is_pg:
            cur = self.conn.cursor()
            _pg_execute_batch(cur, adapted, seq_of_params, page_size=500)
            return cur
        else:
            return self.conn.executemany(adapted, seq_of_params)


def get_connection():
    """Backwards-compatible helper returning a unified _DBSession."""
    return _DBSession()


def get_storage_status():
    """Returns diagnostic status of current persistence layer for /admin dashboard."""
    gsheets_url = get_google_sheets_webhook_url()
    gh_cfg = get_github_config()
    return {
        "db_engine": "postgresql" if USE_POSTGRES else "sqlite",
        "postgres_configured": bool(USE_POSTGRES),
        "github_configured": bool(gh_cfg['enabled']),
        "github_repo": gh_cfg['repo'],
        "github_branch": gh_cfg['branch'],
        "has_github_token": bool(gh_cfg['token']),
        "gsheets_configured": bool(gsheets_url),
        "gsheets_url": gsheets_url,
        "cloud_persisted": bool(USE_POSTGRES or gh_cfg['enabled'] or gsheets_url)
    }


# ==========================================================================
#  GitHub Repository Auto-Backup & Restore Engine (Method 3)
# ==========================================================================

GITHUB_SYNC_LOCK = threading.Lock()
DEFAULT_GITHUB_REPO = "Albertyoung22/harvard-ent"
DEFAULT_GITHUB_BRANCH = "cloud-backup"


def _normalize_github_repo(raw_repo):
    r = str(raw_repo or '').strip()
    if not r:
        return DEFAULT_GITHUB_REPO
    for prefix in ('https://github.com/', 'http://github.com/', 'git@github.com:'):
        if r.startswith(prefix):
            r = r[len(prefix):]
    if r.endswith('.git'):
        r = r[:-4]
    return r.strip('/') or DEFAULT_GITHUB_REPO


def get_github_config():
    local_cfg = {}
    if os.path.exists(LOCAL_CONFIG_PATH):
        try:
            with open(LOCAL_CONFIG_PATH, 'r', encoding='utf-8') as f:
                local_cfg = json.load(f)
        except Exception:
            pass
    db_cfg = get_app_settings()
    merged = {**local_cfg, **db_cfg}

    token = (
        os.environ.get('GITHUB_TOKEN', '').strip()
        or os.environ.get('GH_TOKEN', '').strip()
        or str(merged.get('github_token', '')).strip()
    )
    repo = _normalize_github_repo(
        os.environ.get('GITHUB_REPO', '').strip()
        or merged.get('github_repo', '')
        or DEFAULT_GITHUB_REPO
    )
    branch = (
        os.environ.get('GITHUB_BRANCH', '').strip()
        or str(merged.get('github_branch', '')).strip()
        or DEFAULT_GITHUB_BRANCH
    )
    return {
        'token': token,
        'repo': repo,
        'branch': branch,
        'enabled': bool(token and repo)
    }


def _github_api_request(url, method='GET', token='', payload=None, timeout=20):
    headers = {
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'HARVARD-Enterprise-GitHubSync/1.0',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'
    data_bytes = None
    if payload is not None:
        headers['Content-Type'] = 'application/json; charset=utf-8'
        data_bytes = json.dumps(payload, ensure_ascii=False).encode('utf-8')

    req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8', errors='replace'))


def _ensure_github_branch(repo, branch, token):
    """Ensures the target backup branch (e.g. 'cloud-backup') exists on GitHub so main branch never has push conflicts."""
    ref_url = f"https://api.github.com/repos/{repo}/git/ref/heads/{ urllib.parse.quote(branch) }"
    try:
        _github_api_request(ref_url, method='GET', token=token)
        return branch
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise

    # Branch doesn't exist yet -> create it from default branch (main or master)
    base_sha = None
    for base_br in ('main', 'master'):
        try:
            base_info = _github_api_request(
                f"https://api.github.com/repos/{repo}/git/ref/heads/{base_br}",
                method='GET',
                token=token
            )
            base_sha = base_info.get('object', {}).get('sha')
            if base_sha:
                break
        except Exception:
            continue

    if not base_sha:
        return 'main'

    try:
        _github_api_request(
            f"https://api.github.com/repos/{repo}/git/refs",
            method='POST',
            token=token,
            payload={
                'ref': f'refs/heads/{branch}',
                'sha': base_sha
            }
        )
        return branch
    except Exception:
        return 'main'


def _github_put_file(repo, branch, token, file_path, raw_bytes, commit_message):
    with GITHUB_SYNC_LOCK:
        target_branch = _ensure_github_branch(repo, branch, token)
        api_url = f"https://api.github.com/repos/{repo}/contents/{file_path}"

        existing_sha = None
        try:
            info = _github_api_request(f"{api_url}?ref={urllib.parse.quote(target_branch)}", method='GET', token=token)
            existing_sha = info.get('sha')
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise

        payload = {
            'message': f"📦 [skip ci] {commit_message}",
            'content': base64.b64encode(raw_bytes).decode('ascii'),
            'branch': target_branch
        }
        if existing_sha:
            payload['sha'] = existing_sha

        return _github_api_request(api_url, method='PUT', token=token, payload=payload, timeout=25)


def _push_inquiries_to_github_async(reason="自動同步客戶詢價單資料"):
    cfg = get_github_config()
    if not cfg['enabled']:
        return

    def _worker():
        try:
            all_items = get_all_inquiries()
            raw_bytes = json.dumps(all_items, ensure_ascii=False, indent=2).encode('utf-8')
            _github_put_file(
                cfg['repo'],
                cfg['branch'],
                cfg['token'],
                'data/inquiries.json',
                raw_bytes,
                f"{reason} (共 {len(all_items)} 筆)"
            )
        except Exception as e:
            print(f"[!] GitHub 自動備份提示: {e}")

    threading.Thread(target=_worker, daemon=True).start()


def _push_drawing_to_github_async(filename, file_bytes):
    cfg = get_github_config()
    if not cfg['enabled'] or not filename or not file_bytes:
        return

    def _worker():
        try:
            _github_put_file(
                cfg['repo'],
                cfg['branch'],
                cfg['token'],
                f"static/uploads/drawings/{filename}",
                file_bytes,
                f"上傳客戶工程圖檔 {filename}"
            )
        except Exception as e:
            print(f"[!] GitHub 圖檔備份提示 ({filename}): {e}")

    threading.Thread(target=_worker, daemon=True).start()


def _fetch_drawing_from_github(filename):
    cfg = get_github_config()
    repo = cfg['repo']
    if not repo or not filename:
        return None
    for br in (cfg['branch'], 'main'):
        try:
            api_url = f"https://api.github.com/repos/{repo}/contents/static/uploads/drawings/{urllib.parse.quote(filename)}?ref={urllib.parse.quote(br)}"
            info = _github_api_request(api_url, method='GET', token=cfg['token'], timeout=15)
            content_b64 = info.get('content', '')
            if content_b64:
                return base64.b64decode(content_b64)
        except Exception:
            continue
    return None


def restore_inquiries_from_github(custom_cfg=None):
    """
    Pulls data/inquiries.json from GitHub ('cloud-backup' branch or 'main') and merges into DB.
    Ensures zero data loss when Render wakes up from sleep or redeploys a new version.
    """
    cfg = custom_cfg or get_github_config()
    repo = _normalize_github_repo(cfg.get('repo'))
    branch = cfg.get('branch') or DEFAULT_GITHUB_BRANCH
    token = cfg.get('token', '')

    if not repo:
        return 0

    remote_items = None
    for br in (branch, 'main'):
        try:
            api_url = f"https://api.github.com/repos/{repo}/contents/data/inquiries.json?ref={urllib.parse.quote(br)}"
            info = _github_api_request(api_url, method='GET', token=token, timeout=15)
            content_b64 = info.get('content', '')
            if content_b64:
                raw_json = base64.b64decode(content_b64).decode('utf-8', errors='replace')
                parsed = json.loads(raw_json)
                if isinstance(parsed, list):
                    remote_items = parsed
                    break
        except Exception:
            continue

    if not remote_items:
        return 0

    restored = 0
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with DB_LOCK:
        with get_connection() as conn:
            cur = conn.execute("SELECT id, updated_at FROM inquiries")
            existing_map = {r['id']: (r['updated_at'] or '') for r in cur.fetchall()}

            for item in remote_items:
                if not isinstance(item, dict):
                    continue
                tid = str(item.get('id', '')).strip()
                if not tid:
                    continue
                remote_updated = str(item.get('updatedAt') or item.get('timestamp') or '')
                local_updated = existing_map.get(tid)

                # Insert if missing locally, or update if remote record on GitHub is newer
                if local_updated is None or (remote_updated and remote_updated > local_updated):
                    _insert_or_replace_inquiry_conn(conn, {
                        'id': tid,
                        'companyName': item.get('companyName', ''),
                        'contactPerson': item.get('contactPerson', ''),
                        'contactPhone': item.get('contactPhone', ''),
                        'contactEmail': item.get('contactEmail', ''),
                        'inquiryMaterial': item.get('inquiryMaterial', ''),
                        'inquiryMessage': item.get('inquiryMessage', ''),
                        'drawingUrl': item.get('drawingUrl', ''),
                        'timestamp': item.get('timestamp', now_str),
                        'updatedAt': item.get('updatedAt', now_str),
                        'status': item.get('status', 'pending'),
                        'branch': item.get('branch', '未指派'),
                        'adminNote': item.get('adminNote', ''),
                        'emailSent': bool(item.get('emailSent')),
                        'emailError': item.get('emailError', '')
                    })
                    existing_map[tid] = remote_updated
                    restored += 1

    if restored > 0:
        print(f"🐙 [GitHub Sync] 已自動從 GitHub ({repo}@{branch}) 還原/更新 {restored} 筆客戶詢價單資料！")
    return restored


def sync_all_to_github(custom_cfg=None):
    """One-click test and bidirectional sync with GitHub repository."""
    base_cfg = get_github_config()
    cfg = {
        'token': (custom_cfg.get('token') if custom_cfg else '') or base_cfg['token'],
        'repo': _normalize_github_repo((custom_cfg.get('repo') if custom_cfg else '') or base_cfg['repo']),
        'branch': (custom_cfg.get('branch') if custom_cfg else '') or base_cfg['branch'] or DEFAULT_GITHUB_BRANCH
    }
    if not cfg['token']:
        raise ValueError("請填入有效的 GitHub Personal Access Token (ghp_... 或 github_pat_...)")

    # 1. First pull and merge any remote inquiries from GitHub so nothing is overwritten
    restored_count = restore_inquiries_from_github(custom_cfg=cfg)

    # 2. Push the merged inquiries list to GitHub
    all_items = get_all_inquiries()
    raw_bytes = json.dumps(all_items, ensure_ascii=False, indent=2).encode('utf-8')
    res = _github_put_file(
        cfg['repo'],
        cfg['branch'],
        cfg['token'],
        'data/inquiries.json',
        raw_bytes,
        f"手動雙向同步客戶詢價單 (共 {len(all_items)} 筆)"
    )
    html_url = res.get('content', {}).get('html_url') or f"https://github.com/{cfg['repo']}/blob/{cfg['branch']}/data/inquiries.json"
    return {
        'success': True,
        'pushed': len(all_items),
        'restored': restored_count,
        'repo': cfg['repo'],
        'branch': cfg['branch'],
        'html_url': html_url
    }


# ==========================================================================
#  Google Sheets Cloud Webhook Two-Way Sync & Auto-Restore
# ==========================================================================

def get_google_sheets_webhook_url():
    env_url = os.environ.get('GOOGLE_SHEETS_WEBHOOK_URL', '').strip()
    if env_url:
        return env_url
    settings = get_app_settings()
    if settings.get('google_sheets_webhook_url'):
        return str(settings['google_sheets_webhook_url']).strip()
    if os.path.exists(LOCAL_CONFIG_PATH):
        try:
            with open(LOCAL_CONFIG_PATH, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                return str(cfg.get('google_sheets_webhook_url', '')).strip()
        except Exception:
            pass
    return ''


def _push_to_google_sheets_async(action, payload):
    url = get_google_sheets_webhook_url()
    if not url or not url.startswith('https://script.google.com/'):
        return

    def _worker():
        try:
            body = json.dumps({"action": action, **payload}, ensure_ascii=False).encode('utf-8')
            req = urllib.request.Request(
                url,
                data=body,
                headers={'Content-Type': 'application/json; charset=utf-8', 'User-Agent': 'HARVARD-CloudSync/1.0'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                resp.read()
        except Exception as e:
            print(f"[!] Google Sheets 雲端同步提示 ({action}): {e}")

    threading.Thread(target=_worker, daemon=True).start()


def sync_all_to_google_sheets(custom_url=None):
    """Pushes all current inquiries to Google Sheets and pulls any remote-only inquiries."""
    url = (custom_url or get_google_sheets_webhook_url()).strip()
    if not url or not url.startswith('https://script.google.com/'):
        raise ValueError("請填寫有效的 Google Apps Script 網頁應用程式網址 (https://script.google.com/macros/s/.../exec)")

    # 1. Pull remote inquiries first so we don't lose any historical cloud records
    pulled_count = restore_inquiries_from_google_sheets(custom_url=url)

    # 2. Push all local/merged inquiries up to Google Sheets
    all_items = get_all_inquiries()
    body = json.dumps({
        "action": "sync_all_inquiries",
        "items": all_items
    }, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=body,
        headers={'Content-Type': 'application/json; charset=utf-8', 'User-Agent': 'HARVARD-CloudSync/1.0'},
        method='POST'
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw_res = resp.read().decode('utf-8', errors='replace')
        try:
            res_json = json.loads(raw_res)
        except Exception:
            res_json = {"success": True, "raw": raw_res[:200]}

    return {
        "success": True,
        "pushed": len(all_items),
        "restored": pulled_count,
        "remote": res_json
    }


def restore_inquiries_from_google_sheets(custom_url=None):
    """
    Fetches historical inquiries from Google Sheets and restores any missing records into the DB.
    Ensures zero data loss when Render wakes up from sleep or redeploys a fresh container.
    """
    url = (custom_url or get_google_sheets_webhook_url()).strip()
    if not url or not url.startswith('https://script.google.com/'):
        return 0

    try:
        sep = '&' if '?' in url else '?'
        fetch_url = f"{url}{sep}action=list_inquiries"
        req = urllib.request.Request(
            fetch_url,
            headers={'User-Agent': 'HARVARD-CloudSync/1.0'},
            method='GET'
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8', errors='replace'))

        remote_items = data.get('items', []) if isinstance(data, dict) else []
        if not remote_items:
            return 0

        restored = 0
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with DB_LOCK:
            with get_connection() as conn:
                cur = conn.execute("SELECT id FROM inquiries")
                existing_ids = {r['id'] for r in cur.fetchall()}

                for item in remote_items:
                    if not isinstance(item, dict):
                        continue
                    tid = str(item.get('id', '')).strip()
                    if not tid or tid in existing_ids:
                        continue
                    _insert_or_replace_inquiry_conn(conn, {
                        'id': tid,
                        'companyName': item.get('companyName', ''),
                        'contactPerson': item.get('contactPerson', ''),
                        'contactPhone': item.get('contactPhone', ''),
                        'contactEmail': item.get('contactEmail', ''),
                        'inquiryMaterial': item.get('inquiryMaterial', ''),
                        'inquiryMessage': item.get('inquiryMessage', ''),
                        'drawingUrl': item.get('drawingUrl', ''),
                        'timestamp': item.get('timestamp', now_str),
                        'updatedAt': item.get('updatedAt', now_str),
                        'status': item.get('status', 'pending'),
                        'branch': item.get('branch', '未指派'),
                        'adminNote': item.get('adminNote', ''),
                        'emailSent': bool(item.get('emailSent')),
                        'emailError': item.get('emailError', '')
                    })
                    existing_ids.add(tid)
                    restored += 1

        if restored > 0:
            print(f"☁️ [Cloud Sync] 已自動從 Google 試算表還原 {restored} 筆客戶詢價單資料！")
        return restored
    except Exception as e:
        print(f"[!] 從 Google 試算表讀取備份略過: {e}")
        return 0


# ==========================================================================
#  Database Initialization & Schema Migration
# ==========================================================================

def init_db():
    global USE_POSTGRES
    if not USE_POSTGRES:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    try:
        _init_tables_and_seed()
    except Exception as e:
        if USE_POSTGRES:
            print(f"[!] 雲端 PostgreSQL 連線初始化失敗 ({e})，自動切換至本機 SQLite 備援模式。")
            USE_POSTGRES = False
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
            _init_tables_and_seed()
        else:
            raise


def _init_tables_and_seed():
    with DB_LOCK:
        with get_connection() as conn:
            # 1. Specs Table
            if USE_POSTGRES:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS inventory_specs (
                        id SERIAL PRIMARY KEY,
                        no TEXT,
                        spec_group TEXT,
                        category TEXT,
                        material TEXT,
                        dimension TEXT,
                        size TEXT,
                        note TEXT,
                        created_at TEXT,
                        updated_at TEXT
                    )
                """)
            else:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS inventory_specs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        no TEXT,
                        spec_group TEXT,
                        category TEXT,
                        material TEXT,
                        dimension TEXT,
                        size TEXT,
                        note TEXT,
                        created_at TEXT,
                        updated_at TEXT
                    )
                """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_specs_group ON inventory_specs(spec_group)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_specs_category ON inventory_specs(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_specs_material ON inventory_specs(material)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_specs_no ON inventory_specs(no)")

            # 2. Inquiries Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS inquiries (
                    id TEXT PRIMARY KEY,
                    company_name TEXT,
                    contact_person TEXT,
                    contact_phone TEXT,
                    contact_email TEXT,
                    inquiry_material TEXT,
                    inquiry_message TEXT,
                    drawing_url TEXT,
                    timestamp TEXT,
                    updated_at TEXT,
                    status TEXT DEFAULT 'pending',
                    branch TEXT DEFAULT '未指派',
                    admin_note TEXT DEFAULT '',
                    email_sent INTEGER DEFAULT 0,
                    email_error TEXT DEFAULT ''
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_inq_status ON inquiries(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_inq_timestamp ON inquiries(timestamp)")

            # 3. Uploaded Drawings Binary Table (Protects customer drawings against Render container resets)
            blob_type = "BYTEA" if USE_POSTGRES else "BLOB"
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS uploaded_drawings (
                    filename TEXT PRIMARY KEY,
                    ticket_id TEXT,
                    content_type TEXT,
                    file_data {blob_type},
                    file_size INTEGER DEFAULT 0,
                    created_at TEXT
                )
            """)

            # 4. App Settings Table (Persists SMTP, Admin Password & Webhook settings in Cloud DB)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS app_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT
                )
            """)

            # Seed Specs from JSON if table is empty
            cur = conn.execute("SELECT COUNT(*) AS cnt FROM inventory_specs")
            row = cur.fetchone()
            spec_count = row['cnt'] if isinstance(row, dict) else row[0]

            if spec_count == 0 and os.path.exists(SPECS_JSON_PATH):
                try:
                    with open(SPECS_JSON_PATH, 'r', encoding='utf-8') as f:
                        raw_specs = json.load(f)
                    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    batch = []
                    for s in raw_specs:
                        batch.append((
                            str(s.get('no', '')),
                            s.get('group', 'stock'),
                            s.get('category', ''),
                            s.get('material', ''),
                            s.get('dimension', ''),
                            s.get('size', ''),
                            s.get('note', ''),
                            now_str,
                            now_str
                        ))
                    conn.executemany("""
                        INSERT INTO inventory_specs (no, spec_group, category, material, dimension, size, note, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, batch)
                    engine_label = "Cloud PostgreSQL" if USE_POSTGRES else "SQLite"
                    print(f"[*] {engine_label} 自動匯入完成: {len(batch)} 筆現貨規格資料！")
                except Exception as e:
                    print(f"[!] 匯入 specs_json 失敗: {e}")

            # Seed Inquiries from JSON if table is empty
            cur = conn.execute("SELECT COUNT(*) AS cnt FROM inquiries")
            row = cur.fetchone()
            inq_count = row['cnt'] if isinstance(row, dict) else row[0]

            if inq_count == 0:
                inq_file = INQUIRIES_JSON_PATH if os.path.exists(INQUIRIES_JSON_PATH) else INQUIRIES_EXAMPLE_PATH
                if os.path.exists(inq_file):
                    try:
                        with open(inq_file, 'r', encoding='utf-8') as f:
                            raw_inqs = json.load(f)
                        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        for item in raw_inqs:
                            if isinstance(item, dict) and item.get('id'):
                                _insert_or_replace_inquiry_conn(conn, {
                                    'id': item.get('id'),
                                    'companyName': item.get('companyName', ''),
                                    'contactPerson': item.get('contactPerson', ''),
                                    'contactPhone': item.get('contactPhone', ''),
                                    'contactEmail': item.get('contactEmail', ''),
                                    'inquiryMaterial': item.get('inquiryMaterial', ''),
                                    'inquiryMessage': item.get('inquiryMessage', ''),
                                    'drawingUrl': item.get('drawingUrl', ''),
                                    'timestamp': item.get('timestamp', now_str),
                                    'updatedAt': item.get('updatedAt', now_str),
                                    'status': item.get('status', 'pending'),
                                    'branch': item.get('branch', '未指派'),
                                    'adminNote': item.get('adminNote', ''),
                                    'emailSent': bool(item.get('emailSent')),
                                    'emailError': item.get('emailError', '')
                                })
                    except Exception as e:
                        print(f"[!] 匯入 inquiries 失敗: {e}")

    # Automatically restore any missing cloud inquiries from GitHub & Google Sheets on startup
    threading.Thread(target=restore_inquiries_from_github, daemon=True).start()
    if get_google_sheets_webhook_url():
        threading.Thread(target=restore_inquiries_from_google_sheets, daemon=True).start()


def _insert_or_replace_inquiry_conn(conn, item):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    params = (
        item['id'],
        item.get('companyName', ''),
        item.get('contactPerson', ''),
        item.get('contactPhone', ''),
        item.get('contactEmail', ''),
        item.get('inquiryMaterial', ''),
        item.get('inquiryMessage', ''),
        item.get('drawingUrl', ''),
        item.get('timestamp', now_str),
        item.get('updatedAt', now_str),
        item.get('status', 'pending'),
        item.get('branch', '未指派'),
        item.get('adminNote', ''),
        1 if item.get('emailSent') else 0,
        item.get('emailError', '')
    )
    if USE_POSTGRES:
        conn.execute("""
            INSERT INTO inquiries (
                id, company_name, contact_person, contact_phone, contact_email,
                inquiry_material, inquiry_message, drawing_url, timestamp, updated_at,
                status, branch, admin_note, email_sent, email_error
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (id) DO UPDATE SET
                company_name = EXCLUDED.company_name,
                contact_person = EXCLUDED.contact_person,
                contact_phone = EXCLUDED.contact_phone,
                contact_email = EXCLUDED.contact_email,
                inquiry_material = EXCLUDED.inquiry_material,
                inquiry_message = EXCLUDED.inquiry_message,
                drawing_url = EXCLUDED.drawing_url,
                timestamp = EXCLUDED.timestamp,
                updated_at = EXCLUDED.updated_at,
                status = EXCLUDED.status,
                branch = EXCLUDED.branch,
                admin_note = EXCLUDED.admin_note,
                email_sent = EXCLUDED.email_sent,
                email_error = EXCLUDED.email_error
        """, params)
    else:
        conn.execute("""
            INSERT OR REPLACE INTO inquiries (
                id, company_name, contact_person, contact_phone, contact_email,
                inquiry_material, inquiry_message, drawing_url, timestamp, updated_at,
                status, branch, admin_note, email_sent, email_error
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, params)


# ==========================================================================
#  App Settings & Uploaded Drawings Cloud Persistence
# ==========================================================================

def get_app_settings():
    try:
        with DB_LOCK:
            with get_connection() as conn:
                cur = conn.execute("SELECT key, value FROM app_settings")
                rows = cur.fetchall()
                result = {}
                for r in rows:
                    k = r['key']
                    v = r['value']
                    try:
                        result[k] = json.loads(v)
                    except Exception:
                        result[k] = v
                return result
    except Exception:
        return {}


def save_app_settings(data_dict):
    if not data_dict:
        return
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with DB_LOCK:
            with get_connection() as conn:
                for k, v in data_dict.items():
                    val_str = json.dumps(v, ensure_ascii=False)
                    if USE_POSTGRES:
                        conn.execute("""
                            INSERT INTO app_settings (key, value, updated_at)
                            VALUES (?, ?, ?)
                            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = EXCLUDED.updated_at
                        """, (str(k), val_str, now_str))
                    else:
                        conn.execute("""
                            INSERT OR REPLACE INTO app_settings (key, value, updated_at)
                            VALUES (?, ?, ?)
                        """, (str(k), val_str, now_str))
    except Exception as e:
        print(f"[!] 儲存 app_settings 失敗: {e}")


def save_drawing_file(filename, ticket_id, content_type, file_bytes):
    """Stores uploaded customer drawing file in DB so it survives Render container resets."""
    if not filename or not file_bytes:
        return
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with DB_LOCK:
            with get_connection() as conn:
                blob_val = psycopg2.Binary(file_bytes) if USE_POSTGRES else sqlite3.Binary(file_bytes)
                if USE_POSTGRES:
                    conn.execute("""
                        INSERT INTO uploaded_drawings (filename, ticket_id, content_type, file_data, file_size, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ON CONFLICT (filename) DO UPDATE SET
                            file_data = EXCLUDED.file_data,
                            file_size = EXCLUDED.file_size,
                            content_type = EXCLUDED.content_type
                    """, (filename, ticket_id, content_type or 'application/octet-stream', blob_val, len(file_bytes), now_str))
                else:
                    conn.execute("""
                        INSERT OR REPLACE INTO uploaded_drawings (filename, ticket_id, content_type, file_data, file_size, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (filename, ticket_id, content_type or 'application/octet-stream', blob_val, len(file_bytes), now_str))
        # Also push drawing file to GitHub backup branch if configured
        _push_drawing_to_github_async(filename, file_bytes)
    except Exception as e:
        print(f"[!] 寫入圖檔至資料庫失敗 ({filename}): {e}")


def get_drawing_file(filename):
    """Retrieves customer drawing file from DB or GitHub if local disk was wiped on Render restart."""
    if not filename:
        return None
    try:
        with DB_LOCK:
            with get_connection() as conn:
                cur = conn.execute(
                    "SELECT filename, ticket_id, content_type, file_data, file_size FROM uploaded_drawings WHERE filename = ?",
                    (filename,)
                )
                r = cur.fetchone()
                if r and r['file_data']:
                    raw_bytes = bytes(r['file_data'])
                    return {
                        'filename': r['filename'],
                        'ticket_id': r['ticket_id'],
                        'content_type': r['content_type'] or 'application/octet-stream',
                        'file_bytes': raw_bytes,
                        'file_size': r['file_size']
                    }
    except Exception:
        pass

    # Fallback: try recovering the drawing file from GitHub backup branch
    gh_bytes = _fetch_drawing_from_github(filename)
    if gh_bytes:
        return {
            'filename': filename,
            'ticket_id': '',
            'content_type': 'application/octet-stream',
            'file_bytes': gh_bytes,
            'file_size': len(gh_bytes)
        }
    return None


# ==========================================================================
#  Specs CRUD Operations
# ==========================================================================

def get_all_specs():
    with DB_LOCK:
        with get_connection() as conn:
            cur = conn.execute("""
                SELECT id, no, spec_group, category, material, dimension, size, note, created_at, updated_at
                FROM inventory_specs
                ORDER BY id ASC
            """)
            rows = cur.fetchall()
            return [
                {
                    'id': r['id'],
                    'no': r['no'],
                    'group': r['spec_group'],
                    'category': r['category'],
                    'material': r['material'],
                    'dimension': r['dimension'],
                    'size': r['size'],
                    'note': r['note'],
                    'createdAt': r['created_at'],
                    'updatedAt': r['updated_at']
                }
                for r in rows
            ]


def get_spec_by_id(spec_id):
    with DB_LOCK:
        with get_connection() as conn:
            cur = conn.execute("SELECT * FROM inventory_specs WHERE id = ?", (spec_id,))
            r = cur.fetchone()
            if not r:
                return None
            return {
                'id': r['id'],
                'no': r['no'],
                'group': r['spec_group'],
                'category': r['category'],
                'material': r['material'],
                'dimension': r['dimension'],
                'size': r['size'],
                'note': r['note'],
                'createdAt': r['created_at'],
                'updatedAt': r['updated_at']
            }


def add_spec(data):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    no_val = str(data.get('no', '')).strip()
    group_val = str(data.get('group', 'stock')).strip() or 'stock'
    cat_val = str(data.get('category', '')).strip() or '未分類規格'
    mat_val = str(data.get('material', '')).strip()
    dim_val = str(data.get('dimension', '')).strip()
    size_val = str(data.get('size', '')).strip()
    note_val = str(data.get('note', '')).strip() or ('現貨庫存' if group_val == 'stock' else '免開模現有模具')

    with DB_LOCK:
        with get_connection() as conn:
            if not no_val:
                cur = conn.execute("SELECT no FROM inventory_specs WHERE category = ?", (cat_val,))
                max_no = 0
                for r in cur.fetchall():
                    try:
                        max_no = max(max_no, int(str(r['no']).strip()))
                    except ValueError:
                        pass
                no_val = str(max_no + 1)

            if USE_POSTGRES:
                cur = conn.execute("""
                    INSERT INTO inventory_specs (no, spec_group, category, material, dimension, size, note, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    RETURNING id
                """, (no_val, group_val, cat_val, mat_val, dim_val, size_val, note_val, now_str, now_str))
                spec_id = cur.fetchone()['id']
            else:
                cur = conn.execute("""
                    INSERT INTO inventory_specs (no, spec_group, category, material, dimension, size, note, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (no_val, group_val, cat_val, mat_val, dim_val, size_val, note_val, now_str, now_str))
                spec_id = cur.lastrowid

    return get_spec_by_id(spec_id)


def update_spec(spec_id, data):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fields = []
    params = []

    mapping = {
        'no': 'no',
        'group': 'spec_group',
        'category': 'category',
        'material': 'material',
        'dimension': 'dimension',
        'size': 'size',
        'note': 'note'
    }

    for key, col in mapping.items():
        if key in data:
            fields.append(f"{col} = ?")
            params.append(str(data[key]).strip())

    if not fields:
        return get_spec_by_id(spec_id)

    fields.append("updated_at = ?")
    params.append(now_str)
    params.append(spec_id)

    with DB_LOCK:
        with get_connection() as conn:
            conn.execute(f"UPDATE inventory_specs SET {', '.join(fields)} WHERE id = ?", params)

    return get_spec_by_id(spec_id)


def delete_spec(spec_id):
    with DB_LOCK:
        with get_connection() as conn:
            cur = conn.execute("DELETE FROM inventory_specs WHERE id = ?", (spec_id,))
            return cur.rowcount > 0


# ==========================================================================
#  Inquiries CRUD Operations
# ==========================================================================

def get_all_inquiries():
    with DB_LOCK:
        with get_connection() as conn:
            cur = conn.execute("SELECT * FROM inquiries ORDER BY timestamp ASC")
            rows = cur.fetchall()
            return [
                {
                    'id': r['id'],
                    'companyName': r['company_name'] or '',
                    'contactPerson': r['contact_person'] or '',
                    'contactPhone': r['contact_phone'] or '',
                    'contactEmail': r['contact_email'] or '',
                    'inquiryMaterial': r['inquiry_material'] or '',
                    'inquiryMessage': r['inquiry_message'] or '',
                    'drawingUrl': r['drawing_url'] or '',
                    'timestamp': r['timestamp'] or '',
                    'updatedAt': r['updated_at'] or '',
                    'status': r['status'] or 'pending',
                    'branch': r['branch'] or '未指派',
                    'adminNote': r['admin_note'] or '',
                    'emailSent': bool(r['email_sent']),
                    'emailError': r['email_error'] or ''
                }
                for r in rows
            ]


def get_inquiry_by_id(ticket_id):
    with DB_LOCK:
        with get_connection() as conn:
            cur = conn.execute("SELECT * FROM inquiries WHERE id = ?", (ticket_id,))
            r = cur.fetchone()
            if not r:
                return None
            return {
                'id': r['id'],
                'companyName': r['company_name'] or '',
                'contactPerson': r['contact_person'] or '',
                'contactPhone': r['contact_phone'] or '',
                'contactEmail': r['contact_email'] or '',
                'inquiryMaterial': r['inquiry_material'] or '',
                'inquiryMessage': r['inquiry_message'] or '',
                'drawingUrl': r['drawing_url'] or '',
                'timestamp': r['timestamp'] or '',
                'updatedAt': r['updated_at'] or '',
                'status': r['status'] or 'pending',
                'branch': r['branch'] or '未指派',
                'adminNote': r['admin_note'] or '',
                'emailSent': bool(r['email_sent']),
                'emailError': r['email_error'] or ''
            }


def next_ticket_id():
    with DB_LOCK:
        with get_connection() as conn:
            cur = conn.execute("SELECT id FROM inquiries")
            ids = [r['id'] for r in cur.fetchall()]
    max_num = 1000
    for tid in ids:
        if str(tid).startswith('REQ-'):
            try:
                max_num = max(max_num, int(str(tid).split('-', 1)[1]))
            except ValueError:
                pass
    return f"REQ-{max_num + 1}"


def add_inquiry(item, sync_cloud=True):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tid = item.get('id') or next_ticket_id()
    item['id'] = tid
    item.setdefault('timestamp', now_str)
    item.setdefault('updatedAt', now_str)
    item.setdefault('status', 'pending')
    item.setdefault('branch', '未指派')
    item.setdefault('adminNote', '')
    item.setdefault('emailSent', False)
    item.setdefault('drawingUrl', '')

    with DB_LOCK:
        with get_connection() as conn:
            _insert_or_replace_inquiry_conn(conn, item)

    if sync_cloud:
        _push_inquiries_to_github_async(f"新增詢價單 {tid}")
        _push_to_google_sheets_async("upsert_inquiry", {"item": item})

    return item


def update_inquiry(ticket_id, updates):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fields = []
    params = []

    mapping = {
        'companyName': 'company_name',
        'contactPerson': 'contact_person',
        'contactPhone': 'contact_phone',
        'contactEmail': 'contact_email',
        'inquiryMaterial': 'inquiry_material',
        'inquiryMessage': 'inquiry_message',
        'drawingUrl': 'drawing_url',
        'status': 'status',
        'branch': 'branch',
        'adminNote': 'admin_note',
        'emailSent': 'email_sent',
        'emailError': 'email_error'
    }

    for key, col in mapping.items():
        if key in updates:
            fields.append(f"{col} = ?")
            val = updates[key]
            if key == 'emailSent':
                val = 1 if val else 0
            params.append(val)

    if not fields:
        return get_inquiry_by_id(ticket_id)

    fields.append("updated_at = ?")
    params.append(now_str)
    params.append(ticket_id)

    with DB_LOCK:
        with get_connection() as conn:
            conn.execute(f"UPDATE inquiries SET {', '.join(fields)} WHERE id = ?", params)

    updated_item = get_inquiry_by_id(ticket_id)
    if updated_item:
        _push_inquiries_to_github_async(f"更新詢價單 {ticket_id}")
        _push_to_google_sheets_async("upsert_inquiry", {"item": updated_item})
    return updated_item


def delete_inquiry(ticket_id):
    with DB_LOCK:
        with get_connection() as conn:
            cur = conn.execute("DELETE FROM inquiries WHERE id = ?", (ticket_id,))
            deleted = cur.rowcount > 0
    if deleted:
        _push_inquiries_to_github_async(f"刪除詢價單 {ticket_id}")
        _push_to_google_sheets_async("delete_inquiry", {"id": ticket_id})
    return deleted


# Initialize DB on load
init_db()
