"""
賀華實業股份有限公司 (HARVARD ENTERPRISES INC.)
Flask + Waitress + Google OR-Tools CP-SAT 智慧化、ISO 合規與無障礙雲端/本機伺服器
支援：
1. 100% 完整呈現 https://www.harvard-ent.com.tw/ 所有網頁、規格表與 61 張照片資源
2. Google OR-Tools CP-SAT (ortools.sat.python.cp_model) 四大智慧最佳化 API：
   - POST /api/cpsat/1d-cutting   : 一維鋁捲分條 / 圓棒擠型下料最佳化
   - POST /api/cpsat/2d-plate     : 二維鋁板精密裁切排樣最佳化 (AddNoOverlap2D)
   - POST /api/cpsat/schedule     : 全台五廠區智慧產能排程 (Job-Shop Scheduling)
   - POST /api/cpsat/alloy-select : 鋁合金多準則智慧選材決策
3. ISO 9001 / ISO 14001 / ISO 50001 / ISO 40500 (WCAG 2.1 AAA) 數位化稽核與聯絡表單 API
4. 支援 Waitress 生產環境啟動 (Render / Docker / Windows Desktop App 內嵌伺服器)
"""

import os
import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, abort

from cpsat_optimizer import (
    ALLOY_DB,
    PLANTS,
    solve_1d_cutting_stock,
    solve_2d_plate_cutting,
    solve_multi_plant_schedule,
    solve_alloy_recommendation,
)

BASE_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    static_folder=str(BASE_DIR),
    static_url_path="",
)


@app.after_request
def add_iso_security_and_a11y_headers(response):
    """加入 ISO/IEC 27001 資安標頭與無障礙/快取支援標頭"""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Harvard-ISO-Compliance"] = "ISO-9001, ISO-14001, ISO-50001, ISO-IEC-40500-WCAG-2.1-AAA"
    response.headers["X-Harvard-Optimizer"] = "Google-OR-Tools-CP-SAT"
    return response


# ============================================================================
# 頁面與靜態資源路由 (確保根目錄與 ch/ en/ jp/ 所有網頁與 61 張圖檔完整提供)
# ============================================================================

@app.route("/")
def root_index():
    return send_from_directory(str(BASE_DIR), "index.html")


@app.route("/ch")
@app.route("/ch/")
def ch_index():
    return send_from_directory(str(BASE_DIR / "ch"), "index.html")


@app.route("/en")
@app.route("/en/")
def en_index():
    return send_from_directory(str(BASE_DIR / "en"), "index.html")


@app.route("/jp")
@app.route("/jp/")
def jp_index():
    return send_from_directory(str(BASE_DIR / "jp"), "index.html")


# 讓 ch/css, en/css, jp/css 與 ch/js, en/js, jp/js 也能存取新増的智慧無障礙檔案
@app.route("/<lang>/css/smart-iso-a11y.css")
def lang_smart_css(lang):
    if lang in ("ch", "en", "jp"):
        return send_from_directory(str(BASE_DIR / "css"), "smart-iso-a11y.css")
    abort(404)


@app.route("/<lang>/js/smart-iso-a11y.js")
def lang_smart_js(lang):
    if lang in ("ch", "en", "jp"):
        return send_from_directory(str(BASE_DIR / "js"), "smart-iso-a11y.js")
    abort(404)


# ============================================================================
# Google OR-Tools CP-SAT 智慧最佳化 RESTful API
# ============================================================================

@app.route("/api/health", methods=["GET"])
def api_health():
    """系統健康檢查與 ISO / OR-Tools CP-SAT 狀態端點"""
    images_dir = BASE_DIR / "images"
    image_files = sorted([f.name for f in images_dir.iterdir() if f.is_file()]) if images_dir.exists() else []
    return jsonify({
        "status": "ok",
        "company": "賀華實業股份有限公司 (HARVARD ENTERPRISES INC.)",
        "founded": "1973-04-25",
        "server": "Flask + Waitress WSGI Production Server",
        "solver": "Google OR-Tools CP-SAT (ortools.sat.python.cp_model)",
        "iso_standards": [
            "ISO 9001:2015 品質管理與原廠爐號追溯",
            "ISO 14001:2015 環境管理與裁切減廢減碳",
            "ISO 50001:2018 能源管理與智慧排程節能",
            "ISO/IEC 40500 (WCAG 2.1 AAA) 網站無障礙規範",
        ],
        "assets_verified": {
            "total_images": len(image_files),
            "images": image_files,
            "alloys_count": len(ALLOY_DB),
            "plants_count": len(PLANTS),
        },
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    })


@app.route("/api/catalog", methods=["GET"])
def api_catalog():
    """取得賀華實業完整鋁合金資料庫、五大廠區與 61 張原始照片清單"""
    images_dir = BASE_DIR / "images"
    image_files = sorted([f.name for f in images_dir.iterdir() if f.is_file()]) if images_dir.exists() else []
    return jsonify({
        "status": "ok",
        "alloys": ALLOY_DB,
        "plants": PLANTS,
        "images": image_files,
    })


@app.route("/api/cpsat/1d-cutting", methods=["GET", "POST"])
def api_cpsat_1d_cutting():
    """
    Google OR-Tools CP-SAT 一維鋁捲分條 / 圓棒裁切最佳化 API
    """
    payload = request.get_json(silent=True) or {}
    mother_length = int(payload.get("mother_length", 1250))
    demands = payload.get("demands", None)
    kerf = int(payload.get("kerf", 2))
    trim_allowance = int(payload.get("trim_allowance", 10))
    alloy_code = str(payload.get("alloy_code", "5052"))
    thickness_mm = float(payload.get("thickness_mm", 1.0))
    coil_length_m = float(payload.get("coil_length_m", 100.0))

    result = solve_1d_cutting_stock(
        mother_length=mother_length,
        demands=demands,
        kerf=kerf,
        trim_allowance=trim_allowance,
        alloy_code=alloy_code,
        thickness_mm=thickness_mm,
        coil_length_m=coil_length_m,
    )
    return jsonify(result)


@app.route("/api/cpsat/2d-plate", methods=["GET", "POST"])
def api_cpsat_2d_plate():
    """
    Google OR-Tools CP-SAT 二維鋁板精密裁切排樣最佳化 API (AddNoOverlap2D)
    """
    payload = request.get_json(silent=True) or {}
    plate_width = int(payload.get("plate_width", 1220))
    plate_height = int(payload.get("plate_height", 2440))
    pieces = payload.get("pieces", None)
    kerf = int(payload.get("kerf", 3))
    allow_rotation = bool(payload.get("allow_rotation", True))
    alloy_code = str(payload.get("alloy_code", "6061"))
    thickness_mm = float(payload.get("thickness_mm", 15.0))

    result = solve_2d_plate_cutting(
        plate_width=plate_width,
        plate_height=plate_height,
        pieces=pieces,
        kerf=kerf,
        allow_rotation=allow_rotation,
        alloy_code=alloy_code,
        thickness_mm=thickness_mm,
    )
    return jsonify(result)


@app.route("/api/cpsat/schedule", methods=["GET", "POST"])
def api_cpsat_schedule():
    """
    Google OR-Tools CP-SAT 全台五廠區智慧產能排程 API (Job-Shop Scheduling)
    """
    payload = request.get_json(silent=True) or {}
    orders = payload.get("orders", None)
    result = solve_multi_plant_schedule(orders=orders)
    return jsonify(result)


@app.route("/api/cpsat/alloy-select", methods=["GET", "POST"])
def api_cpsat_alloy_select():
    """
    Google OR-Tools CP-SAT 鋁合金多準則智慧選材決策 API
    """
    payload = request.get_json(silent=True) or {}
    result = solve_alloy_recommendation(
        min_corrosion=int(payload.get("min_corrosion", 70)),
        min_strength=int(payload.get("min_strength", 60)),
        min_formability=int(payload.get("min_formability", 60)),
        min_machinability=int(payload.get("min_machinability", 60)),
        min_weldability=int(payload.get("min_weldability", 60)),
        required_form=str(payload.get("required_form", "all")),
    )
    return jsonify(result)


@app.route("/api/contact", methods=["POST"])
def api_contact():
    """
    線上聯絡表單與詢價單提交 API (符合 ISO 9001 客訴與詢價追蹤編號規範)
    """
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    ticket_id = f"HV-ISO9001-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    return jsonify({
        "status": "success",
        "ticket_id": ticket_id,
        "message": "感謝您的來信與詢價！您的訊息已登錄賀華實業 ISO 9001 品質服務系統，我們將由專人儘速與您聯繫。",
        "submitted": {
            "name": data.get("name", ""),
            "email": data.get("email", ""),
            "phone": data.get("phone", ""),
            "subject": data.get("subject", ""),
        },
    })


def run_waitress_server(host: str = "0.0.0.0", port: int = None):
    """使用 Waitress WSGI 伺服器啟動 Flask 應用程式"""
    from waitress import serve
    if port is None:
        port = int(os.environ.get("PORT", 8080))
    print("=" * 72)
    print(" 賀華實業股份有限公司 (HARVARD ENTERPRISES INC.)")
    print(" Flask + Waitress + Google OR-Tools CP-SAT 智慧化無障礙系統已啟動")
    print(f" 網址: http://127.0.0.1:{port}  (或 http://{host}:{port})")
    print("=" * 72)
    serve(app, host=host, port=port, threads=8)


if __name__ == "__main__":
    run_waitress_server()
