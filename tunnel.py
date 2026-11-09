import os
import sys
import re
import time
import shutil
import urllib.request
import subprocess
import threading

CLOUDFLARED_URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
BIN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
CLOUDFLARED_EXE = os.path.join(BIN_DIR, "cloudflared.exe")
FALLBACK_EXISTING = r"D:\PythonTest\AduinoTest\cloudflared.exe"

tunnel_process = None
public_url = None

def ensure_cloudflared():
    """確保 cloudflared.exe 核心存在，若無則自動複製或從 Cloudflare 官方下載"""
    os.makedirs(BIN_DIR, exist_ok=True)
    if os.path.exists(CLOUDFLARED_EXE) and os.path.getsize(CLOUDFLARED_EXE) > 10000000:
        return CLOUDFLARED_EXE

    # 優先從本機既有快取目錄複製
    if os.path.exists(FALLBACK_EXISTING) and os.path.getsize(FALLBACK_EXISTING) > 10000000:
        print(f"[*] 正在從本機既有快取複製 cloudflared 核心: {FALLBACK_EXISTING} -> {CLOUDFLARED_EXE}")
        shutil.copy2(FALLBACK_EXISTING, CLOUDFLARED_EXE)
        return CLOUDFLARED_EXE

    # 自官方 GitHub 下載
    print(f"[*] 正在從 Cloudflare 官方下載最新版 cloudflared 核心...")
    print(f"    下載來源: {CLOUDFLARED_URL}")
    try:
        def progress(count, block_size, total_size):
            percent = int(count * block_size * 100 / total_size)
            sys.stdout.write(f"\r    下載進度: {percent}% [{count * block_size // (1024*1024)}MB / {total_size // (1024*1024)}MB]")
            sys.stdout.flush()

        urllib.request.urlretrieve(CLOUDFLARED_URL, CLOUDFLARED_EXE, reporthook=progress)
        print("\n[*] cloudflared 下載完成！")
        return CLOUDFLARED_EXE
    except Exception as e:
        print(f"\n[!] 自動下載 cloudflared 失敗: {e}")
        if os.path.exists(CLOUDFLARED_EXE):
            os.remove(CLOUDFLARED_EXE)
        raise

def start_tunnel(port=5000, wait_for_url=True, timeout=30):
    """
    啟動 Cloudflare Quick Tunnel 穿透指定的本地 Port，並自動捕獲 trycloudflare.com 網址
    """
    global tunnel_process, public_url
    exe_path = ensure_cloudflared()

    target_local = f"http://127.0.0.1:{port}"
    print(f"[*] 正在啟動 Cloudflare Tunnel 穿透 {target_local} ...")

    cmd = [
        exe_path,
        "tunnel",
        "--url", target_local,
        "--no-autoupdate"
    ]

    # Cloudflare prints connection info to stderr
    tunnel_process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        encoding="utf-8",
        errors="ignore",
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )

    url_event = threading.Event()
    public_url = None

    def read_output(pipe):
        global public_url
        url_regex = re.compile(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com')
        for line in iter(pipe.readline, ''):
            if not line:
                break
            match = url_regex.search(line)
            if match and not public_url:
                public_url = match.group(0)
                # 儲存至 data/public_url.txt
                os.makedirs("data", exist_ok=True)
                with open("data/public_url.txt", "w", encoding="utf-8") as f:
                    f.write(public_url)
                url_event.set()

    # 監聽 stdout 與 stderr
    t1 = threading.Thread(target=read_output, args=(tunnel_process.stdout,), daemon=True)
    t2 = threading.Thread(target=read_output, args=(tunnel_process.stderr,), daemon=True)
    t1.start()
    t2.start()

    if wait_for_url:
        print(f"[*] 等待 Cloudflare 分配公開網址 (最長 {timeout} 秒)...")
        if url_event.wait(timeout=timeout):
            print("\n" + "=" * 65)
            print("  🌐 Cloudflare Tunnel 內網穿透已成功建立！")
            print(f"  🔗 公開外網網址: {public_url}")
            print(f"  ⚡ 本地轉發目標: {target_local}")
            print(f"  📱 外網任何裝置（手機/平板/遠端電腦）均可直接存取！")
            print("=" * 65 + "\n")
            return public_url
        else:
            print("[!] 等待 Cloudflare 公開網址超時")
            return None

    return None

def get_public_url():
    """取得當前公開網址"""
    global public_url
    if public_url:
        return public_url
    url_file = "data/public_url.txt"
    if os.path.exists(url_file):
        try:
            with open(url_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return content
        except:
            pass
    return None

def stop_tunnel():
    """關閉穿透行程"""
    global tunnel_process
    if tunnel_process:
        print("[*] 正在關閉 Cloudflare Tunnel...")
        tunnel_process.terminate()
        try:
            tunnel_process.wait(timeout=3)
        except:
            tunnel_process.kill()
        tunnel_process = None

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Cloudflare Tunnel 內網穿透工具")
    parser.add_argument("-p", "--port", type=int, default=5000, help="本地轉發通訊埠 (預設 5000)")
    args = parser.parse_args()

    try:
        url = start_tunnel(port=args.port, wait_for_url=True)
        if url:
            print("按 Ctrl+C 結束穿透通道...")
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] 接收到中斷訊號")
    finally:
        stop_tunnel()

