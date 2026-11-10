import os
import sys
import time
import socket
import threading
import logging
import argparse

# Ensure standard output supports UTF-8 on Windows command prompts
if sys.platform.startswith('win'):
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('harvard.enterprises.desktop.app')
    except Exception:
        pass
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from waitress import serve
from app import app
import webview
import tunnel
import subprocess
import db

# Silence verbose waitress logs in desktop mode
logging.getLogger('waitress').setLevel(logging.ERROR)

HOST = '127.0.0.1'
PORT = 5000

def send_windows_toast(title, message):
    """
    Sends a native Windows 10/11 Toast notification via PowerShell.
    Safe against quotes and special characters.
    """
    if not sys.platform.startswith('win'):
        return
    safe_title = str(title).replace('"', '`"').replace('$', '`$')
    safe_message = str(message).replace('"', '`"').replace('$', '`$')
    ps_cmd = f'''
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
$template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
$xml = [xml]$template.GetXml()
$nodes = $xml.GetElementsByTagName('text')
$nodes.Item(0).AppendChild($xml.CreateTextNode("{safe_title}")) | Out-Null
$nodes.Item(1).AppendChild($xml.CreateTextNode("{safe_message}")) | Out-Null
$toastXml = [Windows.Data.Xml.Dom.XmlDocument]::new()
$toastXml.LoadXml($xml.OuterXml)
$toast = [Windows.UI.Notifications.ToastNotification]::new($toastXml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("賀華實業股份有限公司").Show($toast)
'''
    try:
        subprocess.run(
            ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', ps_cmd],
            capture_output=True,
            timeout=5
        )
    except Exception:
        pass

def start_inquiry_monitor():
    """
    Background daemon thread that periodically checks for incoming customer inquiries
    and displays native Windows Toast Notifications to company sales engineers.
    """
    seen_ids = set()
    first_run = True

    while True:
        try:
            items = db.get_all_inquiries()
            current_ids = {item.get('id') for item in items if item.get('id')}
            if first_run:
                seen_ids = current_ids
                first_run = False
            else:
                new_ids = current_ids - seen_ids
                if new_ids:
                    for item in items:
                        if item.get('id') in new_ids:
                            cust = item.get('companyName') or item.get('contactPerson') or '新客戶'
                            mat = item.get('inquiryMaterial') or '客製鋁合金精密規格'
                            if len(mat) > 35:
                                mat = mat[:35] + '...'
                            send_windows_toast(
                                f"🔔 賀華實業 - 收到新詢價單！",
                                f"[{item.get('id')}] {cust}：{mat}"
                            )
                            seen_ids.add(item.get('id'))
        except Exception:
            pass
        time.sleep(5)

def wait_for_server(host, port, timeout=10.0):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except (OSError, ConnectionRefusedError):
            time.sleep(0.1)
    return False

def start_server():
    try:
        serve(app, host=HOST, port=PORT, threads=6)
    except Exception as e:
        print(f"Server error: {e}")

def main():
    parser = argparse.ArgumentParser(description="賀華實業 - 沉浸式桌面應用程式")
    parser.add_argument("--tunnel", action="store_true", help="同時建立 Cloudflare Tunnel 外網網址")
    parser.add_argument("--headless-test", action="store_true", help="執行自動化無頭自我檢測")
    args = parser.parse_args()

    print("=" * 65)
    print("  🖥️  賀華實業股份有限公司 - 沉浸式桌面應用程式 (Desktop App)")
    print(f"  ⚡ 引擎核心: Windows WebView2 (Chromium) + Waitress + Flask")
    print(f"  ⚡ 語音引擎: Microsoft Edge-TTS 台灣神經網路語音")
    print(f"  ⚡ 桌面推播: Windows 原生 Toast 氣泡通知 (即時監控新詢價單)")
    if args.tunnel:
        print(f"  🌐 外網穿透: 已啟用 Cloudflare Tunnel")
    print("=" * 65)

    if getattr(args, 'headless_test', False):
        with app.test_client() as c:
            r1 = c.get('/')
            r2 = c.get('/api/specs')
            r3 = c.post('/api/cpsat/1d-cutting', json={'stock_length': 3000, 'kerf': 3, 'demands': [{'length': 800, 'qty': 2}]})
            assert r1.status_code == 200 and r2.status_code == 200 and r3.status_code == 200
            print("  ✅ Headless self-test PASSED! WebView2 Desktop App ready.")
        return
    
    # 1. Start Waitress WSGI Server in background daemon thread if not already running
    if not wait_for_server(HOST, PORT, timeout=0.5):
        print("  正在啟動本機伺服器服務...")
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        
        if not wait_for_server(HOST, PORT, timeout=10.0):
            print("  [錯誤] 本機伺服器啟動超時！")
            sys.exit(1)
        print("  ✓ 本機伺服器連線就緒！")
    else:
        print("  ✓ 偵測到本機伺服器已在運行中，直接連線！")

    # Start background inquiry monitor for desktop toast notifications
    threading.Thread(target=start_inquiry_monitor, daemon=True).start()

    if args.tunnel:
        threading.Thread(target=lambda: tunnel.start_tunnel(port=PORT, wait_for_url=True), daemon=True).start()

    # 2. Window Settings & High-Precision Icon Resolution
    window_title = "賀華實業股份有限公司 | HARVARD ENTERPRISES INC. - 全方位鋁合金材料供應鏈與精密加工 (沉浸式互動系統)"
    url = f"http://{HOST}:{PORT}"
    
    icon_ico_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'app.ico'))
    if not os.path.exists(icon_ico_path):
        icon_ico_path = os.path.abspath('app.ico')

    # 3. Create Native Desktop Window with Edge WebView2
    window = webview.create_window(
        title=window_title,
        url=url,
        width=1440,
        height=920,
        min_size=(1024, 680),
        text_select=True,
        confirm_close=False,
        background_color='#ffffff'
    )

    def on_window_ready():
        # Ensure desktop window always initializes from top hero section
        try:
            window.evaluate_js("window.scrollTo(0, 0);")
        except Exception:
            pass

    window.events.loaded += on_window_ready

    def apply_window_icon():
        if not sys.platform.startswith('win') or not os.path.exists(icon_ico_path):
            return
        import ctypes
        user32 = ctypes.windll.user32
        WM_SETICON = 0x0080
        ICON_SMALL = 0
        ICON_BIG = 1
        IMAGE_ICON = 1
        LR_LOADFROMFILE = 0x0010
        LR_DEFAULTSIZE = 0x0040
        try:
            hIconBig = user32.LoadImageW(None, icon_ico_path, IMAGE_ICON, 0, 0, LR_LOADFROMFILE | LR_DEFAULTSIZE)
            hIconSmall = user32.LoadImageW(None, icon_ico_path, IMAGE_ICON, 16, 16, LR_LOADFROMFILE)

            # 1. WinForms native Form.Icon
            if hasattr(window, 'native') and window.native:
                try:
                    import clr
                    clr.AddReference('System.Drawing')
                    from System.Drawing import Icon
                    window.native.Icon = Icon(icon_ico_path)
                except Exception:
                    pass

            # 2. Win32 HWND WM_SETICON for Taskbar and Titlebar
            hwnd = None
            if hasattr(window, 'native') and hasattr(window.native, 'Handle'):
                hwnd = window.native.Handle.ToInt32()
            if not hwnd:
                hwnd = user32.FindWindowW(None, window.title)

            if hwnd:
                user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hIconBig)
                user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hIconSmall)
        except Exception as e:
            pass

    # Background enforcer ensures icon binds cleanly after Edge WebView2 creates its window handle
    def icon_enforcer():
        for delay in [0.3, 0.8, 1.8, 3.0]:
            time.sleep(delay)
            apply_window_icon()

    threading.Thread(target=icon_enforcer, daemon=True).start()

    print("  🚀 正在開啟桌面視窗...")
    # gui='edgechromium' uses Microsoft Edge Chromium runtime on Windows
    webview.start(gui='edgechromium', debug=False)
    print("  桌面視窗已關閉，感謝使用！")

if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()
    try:
        main()
    except Exception as e:
        import traceback
        with open("crash_log.txt", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise

