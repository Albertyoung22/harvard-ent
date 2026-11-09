import sys

# Ensure standard output supports UTF-8 on Windows command prompts
if sys.platform.startswith('win'):
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import argparse
import logging
import threading
from waitress import serve
from app import app
import tunnel

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="賀華實業 - Waitress WSGI Server")
    parser.add_argument("-p", "--port", type=int, default=5000, help="通訊埠 (預設 5000)")
    parser.add_argument("--tunnel", action="store_true", help="同時啟動 Cloudflare Tunnel 內網穿透")
    args = parser.parse_args()

    host = '0.0.0.0'
    port = args.port
    threads = 6

    print("=" * 68)
    print("  🚀 賀華實業股份有限公司 - 沉浸式互動官方網站伺服器已啟動")
    print(f"  ⚡ 核心架構: Waitress WSGI Server (執行緒數: {threads})")
    print(f"  ⚡ 後端框架: Python Flask")
    print(f"  ⚡ 語音引擎: Microsoft Edge-TTS 台灣神經網路語音")
    print(f"  🌐 本地訪問網址: http://localhost:{port}")
    print(f"  🌐 區域網路網址: http://127.0.0.1:{port}")

    if args.tunnel:
        def run_tunnel():
            # Wait 1s for server to initialize
            import time
            time.sleep(1)
            tunnel.start_tunnel(port=port, wait_for_url=True, timeout=25)

        t = threading.Thread(target=run_tunnel, daemon=True)
        t.start()
    else:
        print(f"  💡 提示: 若需外網穿透，可加入參數 --tunnel 或執行 start_with_tunnel.bat")

    print("=" * 68)
    try:
        serve(app, host=host, port=port, threads=threads)
    finally:
        if args.tunnel:
            tunnel.stop_tunnel()
