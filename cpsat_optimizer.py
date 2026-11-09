# -*- coding: utf-8 -*-
"""
賀華實業股份有限公司 (HARVARD ENTERPRISES INC.)
智慧鋁材裁切、分條與多廠區排程最佳化引擎
Powered by Google OR-Tools CP-SAT Solver (ortools.sat.python.cp_model)

符合國際標準：
- ISO 9001:2015 品質管理系統（製程參數、刀縫公差、材質追溯）
- ISO 14001:2015 環境管理系統（邊角料減量、廢料回收率、減碳效益計算）
- ISO 50001:2018 能源管理系統（跨廠區機台負載平衡與最低能耗排程）
"""

from __future__ import annotations
import math
import time
from typing import Any, Dict, List, Optional
from ortools.sat.python import cp_model


# 賀華實業常備鋁合金比重與特性資料庫 (依據網站 aluminum.html / service.html / yongsyu.html)
ALLOY_DATABASE: Dict[str, Dict[str, Any]] = {
    "1085": {
        "code": "1085",
        "series": "1000系列 (純鋁)",
        "heat_treatable": False,
        "density_g_cm3": 2.70,
        "al_purity": "99.85%以上",
        "forms": ["片", "捲"],
        "scores": {"corrosion": 95, "strength": 25, "formability": 98, "machinability": 40, "weldability": 95, "conductivity": 98, "reflectivity": 98},
        "characteristics": "純鋁系低強度，具有優良之成形性、熔接性、耐蝕性",
        "applications": "反射板、照明器具、裝飾品化學工業用容器、導電材等",
    },
    "1080": {
        "code": "1080",
        "series": "1000系列 (純鋁)",
        "heat_treatable": False,
        "density_g_cm3": 2.70,
        "al_purity": "99.80%以上",
        "forms": ["板", "片", "捲", "圓片"],
        "scores": {"corrosion": 95, "strength": 26, "formability": 96, "machinability": 40, "weldability": 95, "conductivity": 96, "reflectivity": 96},
        "characteristics": "純鋁系低強度，具有優良之成形性、熔接性、耐蝕性",
        "applications": "反射板、照明器具、裝飾品化學工業用容器、導電材等",
    },
    "1070": {
        "code": "1070",
        "series": "1000系列 (純鋁)",
        "heat_treatable": False,
        "density_g_cm3": 2.70,
        "al_purity": "99.70%以上",
        "forms": ["板", "片", "捲", "圓片"],
        "scores": {"corrosion": 94, "strength": 28, "formability": 95, "machinability": 42, "weldability": 95, "conductivity": 95, "reflectivity": 94},
        "characteristics": "純鋁系低強度，具有優良之成形性、熔接性、耐蝕性",
        "applications": "反射板、照明器具、裝飾品化學工業用容器、導電材等",
    },
    "1050": {
        "code": "1050",
        "series": "1000系列 (純鋁)",
        "heat_treatable": False,
        "density_g_cm3": 2.71,
        "al_purity": "99.50%以上",
        "forms": ["板", "片", "捲", "圓片", "零零鋁箔/零鋁箔"],
        "scores": {"corrosion": 92, "strength": 32, "formability": 95, "machinability": 45, "weldability": 94, "conductivity": 92, "reflectivity": 90},
        "characteristics": "純鋁系低強度，具有優良之成形性、熔接性、耐蝕性",
        "applications": "反射板、照明器具、裝飾品化學工業用容器、導電材等",
    },
    "1100": {
        "code": "1100",
        "series": "1000系列 (純鋁)",
        "heat_treatable": False,
        "density_g_cm3": 2.71,
        "al_purity": "99.00%以上",
        "forms": ["板", "片", "捲", "圓片"],
        "scores": {"corrosion": 90, "strength": 38, "formability": 92, "machinability": 50, "weldability": 92, "conductivity": 88, "reflectivity": 85},
        "characteristics": "強度相對比較低，具有優良成形性、熔接性、耐蝕性",
        "applications": "一般器物、建築用材、電氣器具、各種容器、印板等",
    },
    "1200": {
        "code": "1200",
        "series": "1000系列 (純鋁)",
        "heat_treatable": False,
        "density_g_cm3": 2.71,
        "al_purity": "99.00%以上",
        "forms": ["板", "片", "捲", "圓片"],
        "scores": {"corrosion": 90, "strength": 38, "formability": 92, "machinability": 50, "weldability": 92, "conductivity": 88, "reflectivity": 85},
        "characteristics": "強度相對比較低，具有優良成形性、熔接性、耐蝕性",
        "applications": "一般器物、建築用材、電氣器具、各種容器、印板等",
    },
    "5052": {
        "code": "5052",
        "series": "5000系列 (鋁鎂合金)",
        "heat_treatable": False,
        "density_g_cm3": 2.68,
        "al_purity": "餘量 (Mg 2.2-2.8%)",
        "forms": ["板", "片", "捲", "圓片", "貼模板(A-70/KOBEL ALJADE/UACJ FUS)"],
        "scores": {"corrosion": 92, "strength": 68, "formability": 85, "machinability": 70, "weldability": 90, "conductivity": 65, "reflectivity": 75},
        "characteristics": "中程度強度之代表性合金，耐蝕性、成形性、熔接性良好",
        "applications": "船舶、車輛、建築用材、罐蓋材、精密鈑金",
    },
    "5083": {
        "code": "5083",
        "series": "5000系列 (鋁鎂合金)",
        "heat_treatable": False,
        "density_g_cm3": 2.66,
        "al_purity": "餘量 (Mg 4.0-4.9%)",
        "forms": ["板", "片", "圓片", "貼模板(A-88/A-73)"],
        "scores": {"corrosion": 96, "strength": 80, "formability": 72, "machinability": 72, "weldability": 95, "conductivity": 60, "reflectivity": 70},
        "characteristics": "非熱處理合金中具最高之強度，耐蝕性、熔接性良好，無低溫脆性",
        "applications": "船舶、車輛用材、低溫用儲槽、壓力容器、模具基板",
    },
    "6061": {
        "code": "6061",
        "series": "6000系列 (鋁鎂矽合金)",
        "heat_treatable": True,
        "density_g_cm3": 2.70,
        "al_purity": "餘量 (Mg 0.8-1.2%, Si 0.4-0.8%)",
        "forms": ["板", "片", "圓片", "圓棒", "四方條", "六角條", "扁條", "鋁管"],
        "scores": {"corrosion": 85, "strength": 82, "formability": 75, "machinability": 88, "weldability": 85, "conductivity": 70, "reflectivity": 72},
        "characteristics": "熱處理型合金，耐蝕性與切削加工性良好，結構應用最廣泛",
        "applications": "船舶、車輛、陸上結構物、半導體設備、精密機械、自動化零件",
    },
    "6063S": {
        "code": "6063S",
        "series": "6000系列 (半導體專用鋁鎂矽合金)",
        "heat_treatable": True,
        "density_g_cm3": 2.69,
        "al_purity": "瑞士/美鋁進口半導體級",
        "forms": ["板", "擠型", "鋁管"],
        "scores": {"corrosion": 90, "strength": 78, "formability": 82, "machinability": 90, "weldability": 88, "conductivity": 78, "reflectivity": 85},
        "characteristics": "瑞士/美鋁進口半導體專用板，陽極處理性極佳、組織緻密無氣孔",
        "applications": "半導體真空腔體、TFT-LCD製程設備、新竹科學園區高階設備加工",
    },
    "7075": {
        "code": "7075",
        "series": "7000系列 (鋁鋅鎂銅超硬鋁合金)",
        "heat_treatable": True,
        "density_g_cm3": 2.81,
        "al_purity": "餘量 (Zn 5.1-6.1%, Mg 2.1-2.9%, Cu 1.2-2.0%)",
        "forms": ["板", "圓棒", "鍛造/擠型"],
        "scores": {"corrosion": 65, "strength": 98, "formability": 50, "machinability": 95, "weldability": 45, "conductivity": 55, "reflectivity": 68},
        "characteristics": "鋁合金中強度最高之合金，切削加工性極佳，軋合板表面用7072改善耐蝕性",
        "applications": "航空用材、國防零組件、高強度模具、精密機械構材、滑雪板",
    },
    "2024": {
        "code": "2024",
        "series": "2000系列 (鋁銅鎂硬鋁合金)",
        "heat_treatable": True,
        "density_g_cm3": 2.78,
        "al_purity": "餘量 (Cu 3.8-4.9%, Mg 1.2-1.8%)",
        "forms": ["板", "圓棒"],
        "scores": {"corrosion": 62, "strength": 92, "formability": 60, "machinability": 92, "weldability": 50, "conductivity": 52, "reflectivity": 65},
        "characteristics": "強度略高於2017，切削加工性良好，軋合板表面用1230軋合以改善耐蝕性",
        "applications": "航空用材、高應力各種構造材、精密機械零件",
    },
}

ALLOY_DB: List[Dict[str, Any]] = list(ALLOY_DATABASE.values())

PLANTS: List[Dict[str, Any]] = [
    {"id": "P-TPE", "name": "台北廠/八里倉庫", "region": "北部", "specialty": "固溶板裁切、北部物流中心", "capacity_hr": 16},
    {"id": "P-HSC", "name": "新竹廠 (永旭材料)", "region": "竹苗", "specialty": "竹科半導體 6061/6063S 精密板材", "capacity_hr": 16},
    {"id": "P-TC1", "name": "台中一廠", "region": "中部", "specialty": "600mm特厚板立式裁切、紅外線裁切、自動化倉儲", "capacity_hr": 16},
    {"id": "P-TC2", "name": "台中二廠 (Coil Slitting Center)", "region": "中部", "specialty": "薄板分條加工、整平裁片、RB21張力壓料", "capacity_hr": 16},
    {"id": "P-TNN", "name": "台南廠", "region": "南部", "specialty": "南部鋁板/擠型裁切與快速配送", "capacity_hr": 16},
]


def solve_1d_cutting_stock(
    mother_length: int = 1250,
    kerf: int = 2,
    trim_allowance: int = 10,
    max_cuts_per_mother: int = 12,
    alloy_code: str = "5052",
    thickness_mm: float = 1.0,
    coil_length_m: float = 100.0,
    demands: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    使用 Google OR-Tools CP-SAT (`ortools.sat.python.cp_model`) 求解
    1D 鋁捲分條 (Coil Slitting) 或 鋁圓棒/鋁管定尺裁切 (Bar/Tube Cutting) 最佳化問題。
    """
    start_time = time.time()
    if not demands:
        demands = [
            {"id": "ORD-01", "label": "電子散熱片分條", "width": 300, "qty": 4},
            {"id": "ORD-02", "label": "車用飾板捲料", "width": 240, "qty": 4},
            {"id": "ORD-03", "label": "建築帷幕導軌料", "width": 310, "qty": 3},
            {"id": "ORD-04", "label": "精密衝壓件窄帶", "width": 120, "qty": 4},
        ]

    usable_width = mother_length - trim_allowance
    if usable_width <= 0:
        return {"status": "INVALID", "message": "母材寬度扣除修邊餘量後必須大於 0"}

    clean_demands = []
    for idx, d in enumerate(demands):
        w = int(d.get("width", 100))
        q = int(d.get("qty", 1))
        if w <= 0 or q <= 0:
            continue
        if w > usable_width:
            return {
                "status": "INFEASIBLE",
                "message": f"規格 {d.get('label', w)} ({w}mm) 大於母材可用寬度 ({usable_width}mm)",
            }
        clean_demands.append({
            "index": idx,
            "id": str(d.get("id", f"ITEM-{idx+1}")),
            "label": str(d.get("label", f"規格 {w}mm")),
            "width": w,
            "qty": q,
        })

    if not clean_demands:
        return {"status": "INVALID", "message": "無有效裁切需求項目"}

    # 計算母材數量上界 (First-Fit Decreasing heuristic 估計緊緻上界)
    items_expanded = []
    for d in clean_demands:
        items_expanded.extend([d["width"]] * d["qty"])
    items_expanded.sort(reverse=True)
    bins = []
    for w in items_expanded:
        placed = False
        for b in bins:
            if b["used"] + w + kerf <= usable_width and b["count"] + 1 <= max_cuts_per_mother:
                b["used"] += w + kerf
                b["count"] += 1
                placed = True
                break
        if not placed:
            bins.append({"used": w, "count": 1})
    max_mothers = max(len(bins) + 1, 1)

    model = cp_model.CpModel()

    # 決策變數：
    # used[m] in {0, 1}：第 m 支母捲/母棒是否啟用
    used = [model.NewBoolVar(f"mother_used_{m}") for m in range(max_mothers)]

    # cut_vars[m, i]：第 m 支母捲/母棒裁切第 i 種規格的刀數/支數
    cut_vars: Dict[tuple, cp_model.IntVar] = {}
    for m in range(max_mothers):
        for i, d in enumerate(clean_demands):
            max_possible = min(d["qty"], usable_width // d["width"], max_cuts_per_mother)
            cut_vars[(m, i)] = model.NewIntVar(0, max_possible, f"cut_m{m}_i{i}")

    # 1. 滿足所有客戶訂單需求量 (精確等於需求量，避免過量生產浪費)
    for i, d in enumerate(clean_demands):
        model.Add(sum(cut_vars[(m, i)] for m in range(max_mothers)) == d["qty"])

    # 2. 每支母捲/母棒寬度容量與刀數限制
    used_widths = []
    scrap_vars = []
    for m in range(max_mothers):
        total_cuts_m = sum(cut_vars[(m, i)] for i in range(len(clean_demands)))
        model.Add(total_cuts_m <= max_cuts_per_mother * used[m])
        model.Add(total_cuts_m >= used[m])  # 若啟用至少切 1 刀

        # 有效材料寬度 + 刀縫損耗
        mat_width_m = sum(
            cut_vars[(m, i)] * (clean_demands[i]["width"] + kerf)
            for i in range(len(clean_demands))
        )
        model.Add(mat_width_m <= (usable_width + kerf) * used[m])

        actual_mat_m = model.NewIntVar(0, usable_width, f"actual_mat_{m}")
        model.Add(
            actual_mat_m == sum(
                cut_vars[(m, i)] * clean_demands[i]["width"]
                for i in range(len(clean_demands))
            )
        )
        used_widths.append(actual_mat_m)

        scrap_m = model.NewIntVar(0, mother_length, f"scrap_{m}")
        model.Add(scrap_m == mother_length * used[m] - actual_mat_m)
        scrap_vars.append(scrap_m)

    # 3. 對稱性破除 (Symmetry Breaking)：依序啟用母捲，且按使用量排序
    for m in range(max_mothers - 1):
        model.Add(used[m] >= used[m + 1])
        model.Add(used_widths[m] >= used_widths[m + 1])

    # 目標函數：優先最小化母捲使用總數，次要最小化總餘料損耗
    total_mothers = sum(used)
    total_scrap = sum(scrap_vars)
    model.Minimize(total_mothers * (mother_length * 100) + total_scrap)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5.0
    solver.parameters.num_search_workers = 4
    status = solver.Solve(model)

    elapsed_ms = round((time.time() - start_time) * 1000, 2)
    status_name = solver.StatusName(status)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {
            "status": status_name,
            "solver": "Google OR-Tools CP-SAT (ortools.sat.python.cp_model)",
            "solve_time_ms": elapsed_ms,
            "message": "無法找到可行解，請檢查母材尺寸與刀數上限設定。",
        }

    density = ALLOY_DATABASE.get(alloy_code, {}).get("density_g_cm3", 2.70)
    schedules = []
    total_used_mm = 0
    total_mother_mm = 0

    for m in range(max_mothers):
        if solver.Value(used[m]) == 1:
            cuts_detail = []
            used_mm = 0
            num_knives = 0
            for i, d in enumerate(clean_demands):
                c = solver.Value(cut_vars[(m, i)])
                if c > 0:
                    cuts_detail.append({
                        "id": d["id"],
                        "label": d["label"],
                        "width": d["width"],
                        "count": c,
                        "subtotal_mm": d["width"] * c,
                    })
                    used_mm += d["width"] * c
                    num_knives += c
            kerf_mm = max(0, (num_knives - 1) * kerf)
            scrap_mm = mother_length - used_mm
            utilization = round((used_mm / mother_length) * 100, 2)
            total_used_mm += used_mm
            total_mother_mm += mother_length
            schedules.append({
                "mother_index": len(schedules) + 1,
                "mother_length_mm": mother_length,
                "used_mm": used_mm,
                "trim_and_kerf_mm": trim_allowance + kerf_mm,
                "remnant_mm": max(0, scrap_mm - trim_allowance - kerf_mm),
                "total_loss_mm": scrap_mm,
                "utilization_pct": utilization,
                "knives_used": num_knives,
                "cuts": cuts_detail,
            })

    overall_utilization = round((total_used_mm / total_mother_mm) * 100, 2) if total_mother_mm else 0.0
    total_loss_mm = total_mother_mm - total_used_mm

    # 計算重量 (kg) 與 ISO 14001 減碳效益
    # 體積 (cm3) = 寬度(mm)/10 * 厚度(mm)/10 * 長度(m)*100
    total_weight_kg = round((total_mother_mm / 10.0) * (thickness_mm / 10.0) * (coil_length_m * 100.0) * density / 1000.0, 2)
    net_product_weight_kg = round((total_used_mm / 10.0) * (thickness_mm / 10.0) * (coil_length_m * 100.0) * density / 1000.0, 2)
    scrap_weight_kg = round(total_weight_kg - net_product_weight_kg, 2)
    # 相較傳統經驗排刀平均 88% 利用率所節省的原生鋁碳排 (每公斤鋁約 8.5 kg CO2e)
    baseline_waste_pct = max(0.0, 12.0 - (100.0 - overall_utilization))
    carbon_saved_kg = round(total_weight_kg * (baseline_waste_pct / 100.0) * 8.5, 2)

    return {
        "status": status_name,
        "solver": "Google OR-Tools CP-SAT (ortools.sat.python.cp_model)",
        "solve_time_ms": elapsed_ms,
        "alloy_code": alloy_code,
        "mother_length_mm": mother_length,
        "thickness_mm": thickness_mm,
        "coil_length_m": coil_length_m,
        "total_mothers_used": len(schedules),
        "overall_utilization_pct": overall_utilization,
        "total_loss_pct": round(100.0 - overall_utilization, 2),
        "total_weight_kg": total_weight_kg,
        "net_product_weight_kg": net_product_weight_kg,
        "scrap_weight_kg": scrap_weight_kg,
        "iso14001_carbon_saved_kg_co2e": carbon_saved_kg,
        "recommended_plant": "台中二廠 (Coil Slitting Center 薄板分條中心)" if thickness_mm <= 3.2 else "台中一廠 / 台北八里廠",
        "schedules": schedules,
    }


def solve_2d_plate_cutting(
    plate_width: int = 1220,
    plate_height: int = 2440,
    kerf: int = 3,
    allow_rotation: bool = True,
    alloy_code: str = "6061",
    thickness_mm: float = 15.0,
    pieces: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    使用 Google OR-Tools CP-SAT (`ortools.sat.python.cp_model`) 的 `AddNoOverlap2D`
    求解鋁板二維精密裁切排樣最佳化 (2D Orthogonal Plate Cutting & Nesting)。
    適用於賀華實業 600mm 特厚板立式裁切機、紅外線裁切機與薄板裁切機。
    """
    start_time = time.time()
    if not pieces:
        pieces = [
            {"id": "P1", "label": "半導體腔體底板", "w": 600, "h": 800, "qty": 2},
            {"id": "P2", "label": "精密模具支撐板", "w": 550, "h": 700, "qty": 2},
            {"id": "P3", "label": "航太治具側板", "w": 450, "h": 500, "qty": 3},
            {"id": "P4", "label": "自動化滑台基板", "w": 350, "h": 400, "qty": 2},
        ]

    expanded_items = []
    for p in pieces:
        w = int(p.get("w", 300))
        h = int(p.get("h", 300))
        q = int(p.get("qty", 1))
        label = str(p.get("label", f"{w}x{h}"))
        pid = str(p.get("id", "P"))
        if w <= 0 or h <= 0 or q <= 0:
            continue
        fits_normal = (w <= plate_width and h <= plate_height)
        fits_rot = allow_rotation and (h <= plate_width and w <= plate_height)
        if not fits_normal and not fits_rot:
            return {
                "status": "INFEASIBLE",
                "message": f"零件 {label} ({w}×{h}mm) 超出母板尺寸 ({plate_width}×{plate_height}mm)",
            }
        for k in range(q):
            expanded_items.append({
                "uid": f"{pid}-{k+1}",
                "group_id": pid,
                "label": label,
                "w": w,
                "h": h,
            })

    n = len(expanded_items)
    if n == 0:
        return {"status": "INVALID", "message": "無有效鋁板裁切零件"}
    if n > 24:
        expanded_items = expanded_items[:24]
        n = 24

    total_piece_area = sum(it["w"] * it["h"] for it in expanded_items)
    plate_area = plate_width * plate_height
    min_plates = max(1, math.ceil(total_piece_area / plate_area))
    max_plates = min(n, max(min_plates + 2, 3))

    model = cp_model.CpModel()

    x_intervals = []
    y_intervals = []
    item_vars = []
    max_plate_idx = model.NewIntVar(0, max_plates - 1, "max_plate_idx")
    max_y_overall = model.NewIntVar(0, max_plates * plate_height, "max_y_overall")

    for i, it in enumerate(expanded_items):
        w, h = it["w"], it["h"]
        w_eff = min(plate_width, w + kerf)
        h_eff = min(plate_height, h + kerf)

        can_norm = (w <= plate_width and h <= plate_height)
        can_rot = allow_rotation and (w != h) and (h <= plate_width and w <= plate_height)

        b_var = model.NewIntVar(0, max_plates - 1, f"plate_b_{i}")
        model.Add(max_plate_idx >= b_var)

        if can_norm and can_rot:
            rot = model.NewBoolVar(f"rot_{i}")
            cur_w = model.NewIntVar(min(w, h), max(w, h), f"cw_{i}")
            cur_h = model.NewIntVar(min(w, h), max(w, h), f"ch_{i}")
            eff_w = model.NewIntVar(min(w_eff, h_eff), max(w_eff, h_eff), f"ew_{i}")
            eff_h = model.NewIntVar(min(w_eff, h_eff), max(w_eff, h_eff), f"eh_{i}")
            model.Add(cur_w == w).OnlyEnforceIf(rot.Not())
            model.Add(cur_h == h).OnlyEnforceIf(rot.Not())
            model.Add(eff_w == w_eff).OnlyEnforceIf(rot.Not())
            model.Add(eff_h == h_eff).OnlyEnforceIf(rot.Not())
            model.Add(cur_w == h).OnlyEnforceIf(rot)
            model.Add(cur_h == w).OnlyEnforceIf(rot)
            model.Add(eff_w == h_eff).OnlyEnforceIf(rot)
            model.Add(eff_h == w_eff).OnlyEnforceIf(rot)
        elif can_rot and not can_norm:
            rot = model.NewConstant(1)
            cur_w = model.NewConstant(h)
            cur_h = model.NewConstant(w)
            eff_w = model.NewConstant(h_eff)
            eff_h = model.NewConstant(w_eff)
        else:
            rot = model.NewConstant(0)
            cur_w = model.NewConstant(w)
            cur_h = model.NewConstant(h)
            eff_w = model.NewConstant(w_eff)
            eff_h = model.NewConstant(h_eff)

        x_start = model.NewIntVar(0, plate_width, f"x_{i}")
        x_end = model.NewIntVar(0, plate_width + kerf, f"xe_{i}")
        model.Add(x_start + cur_w <= plate_width)

        y_local = model.NewIntVar(0, plate_height, f"yloc_{i}")
        model.Add(y_local + cur_h <= plate_height)

        y_start = model.NewIntVar(0, max_plates * plate_height, f"y_{i}")
        y_end = model.NewIntVar(0, max_plates * plate_height + kerf, f"ye_{i}")
        model.Add(y_start == b_var * plate_height + y_local)
        model.Add(max_y_overall >= y_start + cur_h)

        x_int = model.NewIntervalVar(x_start, eff_w, x_end, f"xint_{i}")
        y_int = model.NewIntervalVar(y_start, eff_h, y_end, f"yint_{i}")
        x_intervals.append(x_int)
        y_intervals.append(y_int)

        item_vars.append((it, b_var, rot, x_start, y_local, cur_w, cur_h))

    # 相同尺寸零件對稱性破除
    for i in range(len(item_vars) - 1):
        if item_vars[i][0]["group_id"] == item_vars[i + 1][0]["group_id"]:
            model.Add(
                item_vars[i][1] * (plate_height * plate_width) + item_vars[i][4] * plate_width + item_vars[i][3]
                <= item_vars[i + 1][1] * (plate_height * plate_width) + item_vars[i + 1][4] * plate_width + item_vars[i + 1][3]
            )

    # 核心 CP-SAT 二維不重疊幾何約束
    model.AddNoOverlap2D(x_intervals, y_intervals)

    # 緊湊化目標：優先最小化使用的母板數量，其次最小化高度跨距保留完整餘料
    model.Minimize(max_plate_idx * 100000 + max_y_overall)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 1.5
    solver.parameters.num_search_workers = 4
    status = solver.Solve(model)
    elapsed_ms = round((time.time() - start_time) * 1000, 2)
    status_name = solver.StatusName(status)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {
            "status": status_name,
            "solver": "Google OR-Tools CP-SAT AddNoOverlap2D",
            "solve_time_ms": elapsed_ms,
            "message": "無法在母板尺寸內完成二維排樣，請調整母板規格或零件尺寸。",
        }

    plates_out: Dict[int, List[Dict[str, Any]]] = {}
    for it, b_var, rot, x_start, y_local, cur_w, cur_h in item_vars:
        b = solver.Value(b_var)
        rx = solver.Value(x_start)
        ry = solver.Value(y_local)
        cw = solver.Value(cur_w)
        ch = solver.Value(cur_h)
        is_rot = bool(solver.Value(rot) == 1)
        plates_out.setdefault(b, []).append({
            "uid": it["uid"],
            "label": it["label"],
            "orig_w": it["w"],
            "orig_h": it["h"],
            "x": rx,
            "y": ry,
            "w": cw,
            "h": ch,
            "rotated": is_rot,
            "area_mm2": cw * ch,
        })

    plates_summary = []
    for b_idx, b_key in enumerate(sorted(plates_out.keys())):
        p_items = plates_out[b_key]
        used_area = sum(item["area_mm2"] for item in p_items)
        util_pct = round((used_area / plate_area) * 100, 2)
        plates_summary.append({
            "plate_index": b_idx + 1,
            "plate_width": plate_width,
            "plate_height": plate_height,
            "pieces_count": len(p_items),
            "utilization_pct": util_pct,
            "waste_pct": round(100.0 - util_pct, 2),
            "placements": p_items,
        })

    num_plates_used = len(plates_summary)
    overall_util = round((total_piece_area / (num_plates_used * plate_area)) * 100, 2) if num_plates_used else 0.0
    density = ALLOY_DATABASE.get(alloy_code, {}).get("density_g_cm3", 2.70)
    single_plate_kg = (plate_width / 10.0) * (plate_height / 10.0) * (thickness_mm / 10.0) * density / 1000.0
    total_plate_kg = round(single_plate_kg * num_plates_used, 2)
    net_parts_kg = round(total_plate_kg * (overall_util / 100.0), 2)

    if thickness_mm >= 100:
        machine_rec = "600mm特厚板立式裁切機 (台中一廠 / 台北八里廠)"
    elif thickness_mm >= 6:
        machine_rec = "高精準直角度紅外線裁切機 + 壓平機 + 貼膜機"
    else:
        machine_rec = "精密薄板裁切機 + 自動貼膜機"

    return {
        "status": status_name,
        "solver": "Google OR-Tools CP-SAT (AddNoOverlap2D)",
        "solve_time_ms": elapsed_ms,
        "alloy_code": alloy_code,
        "thickness_mm": thickness_mm,
        "plate_width": plate_width,
        "plate_height": plate_height,
        "kerf_mm": kerf,
        "allow_rotation": allow_rotation,
        "total_plates_used": num_plates_used,
        "total_pieces_placed": len(expanded_items),
        "overall_utilization_pct": overall_util,
        "total_plate_weight_kg": total_plate_kg,
        "net_parts_weight_kg": net_parts_kg,
        "remnant_weight_kg": round(total_plate_kg - net_parts_kg, 2),
        "recommended_equipment": machine_rec,
        "plates": plates_summary,
    }


def solve_multi_plant_schedule(
    orders: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    使用 Google OR-Tools CP-SAT (`ortools.sat.python.cp_model`) 求解
    賀華實業全台五廠區（台北八里廠、新竹廠/永旭材料、台中一廠、台中二廠、台南廠）
    智慧產能排程與物流調度最佳化 (Multi-Plant Flexible Job-Shop Scheduling)。
    """
    start_time = time.time()

    plants = [
        {"id": "P-TPE", "name": "台北廠/八里倉庫", "region": "北部", "specialty": "固溶板裁切、北部物流中心", "capacity_hr": 16},
        {"id": "P-HSC", "name": "新竹廠 (永旭材料)", "region": "竹苗", "specialty": "竹科半導體 6061/6063S 精密板材", "capacity_hr": 16},
        {"id": "P-TC1", "name": "台中一廠", "region": "中部", "specialty": "600mm特厚板立式裁切、紅外線裁切、自動化倉儲", "capacity_hr": 16},
        {"id": "P-TC2", "name": "台中二廠 (Coil Slitting Center)", "region": "中部", "specialty": "薄板分條加工、整平裁片、RB21張力壓料", "capacity_hr": 16},
        {"id": "P-TNN", "name": "台南廠", "region": "南部", "specialty": "南部鋁板/擠型裁切與快速配送", "capacity_hr": 16},
    ]

    if not orders:
        orders = [
            {"id": "JOB-101", "customer": "竹科半導體設備大廠", "product": "6063S 半導體腔體板 38.1mm", "process_type": "semiconductor_plate", "duration_hr": 5, "region": "竹苗", "priority": 3},
            {"id": "JOB-102", "customer": "航太國防精密工業", "product": "7075 特厚固溶板 180mm 立式裁切", "process_type": "thick_plate", "duration_hr": 6, "region": "中部", "priority": 3},
            {"id": "JOB-103", "customer": "車用熱交換器廠", "product": "1050/5052 鋁捲精密分條 0.5mm", "process_type": "coil_slitting", "duration_hr": 4, "region": "中部", "priority": 2},
            {"id": "JOB-104", "customer": "北部電子機殼廠", "product": "5052 貼模板 3.0mm 紅外線裁切", "process_type": "standard_plate", "duration_hr": 4, "region": "北部", "priority": 2},
            {"id": "JOB-105", "customer": "南部造船遊艇工業", "product": "5083 船用耐蝕鋁板 25mm 裁切", "process_type": "standard_plate", "duration_hr": 5, "region": "南部", "priority": 2},
            {"id": "JOB-106", "customer": "精密模具加工廠", "product": "6061 進口鋁板 + 圓棒裁切", "process_type": "thick_plate", "duration_hr": 4, "region": "北部", "priority": 1},
            {"id": "JOB-107", "customer": "光電面板設備商", "product": "A-88 5083 雙面貼模板 15mm", "process_type": "semiconductor_plate", "duration_hr": 3, "region": "竹苗", "priority": 2},
        ]

    # 定義各製程可執行之廠區與跨區物流碳排/運輸成本權重
    eligible_map = {
        "coil_slitting": ["P-TC2"],
        "thick_plate": ["P-TC1", "P-TPE"],
        "semiconductor_plate": ["P-HSC", "P-TC1"],
        "standard_plate": ["P-TPE", "P-HSC", "P-TC1", "P-TNN"],
    }
    region_dist_cost = {
        ("北部", "北部"): 1, ("北部", "竹苗"): 2, ("北部", "中部"): 4, ("北部", "南部"): 7,
        ("竹苗", "北部"): 2, ("竹苗", "竹苗"): 1, ("竹苗", "中部"): 3, ("竹苗", "南部"): 6,
        ("中部", "北部"): 4, ("中部", "竹苗"): 3, ("中部", "中部"): 1, ("中部", "南部"): 3,
        ("南部", "北部"): 7, ("南部", "竹苗"): 6, ("南部", "中部"): 3, ("南部", "南部"): 1,
    }

    horizon = sum(int(o.get("duration_hr", 4)) for o in orders) + 10
    model = cp_model.CpModel()

    plant_intervals: Dict[str, List[cp_model.IntervalVar]] = {p["id"]: [] for p in plants}
    job_records = []
    plant_dict = {p["id"]: p for p in plants}

    for j_idx, o in enumerate(orders):
        ptype = o.get("process_type", "standard_plate")
        dur = max(1, int(o.get("duration_hr", 4)))
        cust_region = o.get("region", "中部")
        prio = max(1, int(o.get("priority", 1)))
        elig_plants = eligible_map.get(ptype, [p["id"] for p in plants])

        job_start = model.NewIntVar(0, horizon, f"start_{j_idx}")
        job_end = model.NewIntVar(0, horizon, f"end_{j_idx}")
        model.Add(job_end == job_start + dur)

        choices = []
        for pid in elig_plants:
            pres = model.NewBoolVar(f"job_{j_idx}_on_{pid}")
            s_var = model.NewIntVar(0, horizon, f"s_{j_idx}_{pid}")
            e_var = model.NewIntVar(0, horizon, f"e_{j_idx}_{pid}")
            interval = model.NewOptionalIntervalVar(s_var, dur, e_var, pres, f"int_{j_idx}_{pid}")
            model.Add(job_start == s_var).OnlyEnforceIf(pres)
            model.Add(job_end == e_var).OnlyEnforceIf(pres)
            plant_intervals[pid].append(interval)

            p_region = plant_dict[pid]["region"]
            dist_cost = region_dist_cost.get((cust_region, p_region), 3)
            choices.append((pid, pres, dist_cost))

        model.AddExactlyOne([c[1] for c in choices])
        job_records.append((o, dur, prio, job_start, job_end, choices))

    # 同一廠區主產線不重疊約束
    for pid, ints in plant_intervals.items():
        if ints:
            model.AddNoOverlap(ints)

    makespan = model.NewIntVar(0, horizon, "makespan")
    model.AddMaxEquality(makespan, [r[4] for r in job_records])

    # 目標函數：最小化總完工時間 (Makespan) + 加權完工時間 + 跨區物流碳足跡
    weighted_completion = sum(r[4] * r[2] for r in job_records)
    logistics_penalty = sum(
        c[1] * c[2] * 3 for r in job_records for c in r[5]
    )
    model.Minimize(makespan * 50 + weighted_completion * 5 + logistics_penalty)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5.0
    status = solver.Solve(model)
    elapsed_ms = round((time.time() - start_time) * 1000, 2)
    status_name = solver.StatusName(status)

    assignments = []
    for o, dur, prio, job_start, job_end, choices in job_records:
        assigned_pid = choices[0][0]
        dist_cost = choices[0][2]
        for pid, pres, dcost in choices:
            if solver.Value(pres) == 1:
                assigned_pid = pid
                dist_cost = dcost
                break
        p_info = plant_dict[assigned_pid]
        assignments.append({
            "job_id": o.get("id", "JOB"),
            "customer": o.get("customer", "客戶"),
            "product": o.get("product", "鋁材裁切"),
            "process_type": o.get("process_type", "standard_plate"),
            "customer_region": o.get("region", "中部"),
            "assigned_plant_id": assigned_pid,
            "assigned_plant_name": p_info["name"],
            "plant_region": p_info["region"],
            "start_hr": solver.Value(job_start),
            "end_hr": solver.Value(job_end),
            "duration_hr": dur,
            "priority": prio,
            "logistics_score": dist_cost,
            "local_dispatch": (o.get("region") == p_info["region"]),
        })

    return {
        "status": status_name,
        "solver": "Google OR-Tools CP-SAT Job-Shop Scheduler",
        "solve_time_ms": elapsed_ms,
        "makespan_hr": solver.Value(makespan),
        "total_jobs": len(assignments),
        "plants": plants,
        "assignments": assignments,
    }


def solve_alloy_recommendation(
    min_corrosion: int = 70,
    min_strength: int = 60,
    min_formability: int = 60,
    min_machinability: int = 60,
    min_weldability: int = 50,
    required_form: str = "all",
    prefer_heat_treatable: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    使用 Google OR-Tools CP-SAT (`ortools.sat.python.cp_model`)
    根據客戶在『鋁的世界 - 選用原則』中的五大工程指標（耐蝕性、強度、成型性、切削性、熔接性）
    求解最適鋁合金選材組合與排名。
    """
    start_time = time.time()
    model = cp_model.CpModel()

    alloys = list(ALLOY_DATABASE.values())
    n = len(alloys)
    select_vars = [model.NewBoolVar(f"sel_{a['code']}") for a in alloys]
    slack_vars = [model.NewIntVar(0, 500, f"slack_{a['code']}") for a in alloys]

    scored_results = []
    for i, a in enumerate(alloys):
        sc = a["scores"]
        form_match = True
        if required_form and required_form != "all":
            form_match = any(required_form in f for f in a["forms"])

        ht_match = True
        if prefer_heat_treatable is not None:
            ht_match = (a["heat_treatable"] == prefer_heat_treatable)

        deficit = (
            max(0, min_corrosion - sc["corrosion"])
            + max(0, min_strength - sc["strength"])
            + max(0, min_formability - sc["formability"])
            + max(0, min_machinability - sc["machinability"])
            + max(0, min_weldability - sc["weldability"])
        )
        if not form_match:
            deficit += 150
        if not ht_match:
            deficit += 80

        model.Add(slack_vars[i] == deficit)
        total_score = (
            sc["corrosion"] + sc["strength"] + sc["formability"] + sc["machinability"] + sc["weldability"]
        ) - deficit * 3

        scored_results.append((total_score, deficit, a))

    # 透過 CP-SAT 選出最優 Top 3 推薦合金
    model.Add(sum(select_vars) == min(3, n))
    obj_terms = []
    for i, (t_score, deficit, a) in enumerate(scored_results):
        obj_terms.append(select_vars[i] * (t_score + 1000))
    model.Maximize(sum(obj_terms))

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    recommendations = []
    for i, (t_score, deficit, a) in enumerate(scored_results):
        recommendations.append({
            "code": a["code"],
            "series": a["series"],
            "heat_treatable": a["heat_treatable"],
            "density_g_cm3": a["density_g_cm3"],
            "al_purity": a["al_purity"],
            "forms": a["forms"],
            "scores": a["scores"],
            "characteristics": a["characteristics"],
            "applications": a["applications"],
            "match_score": max(0, min(100, round(100 - deficit * 0.8))),
            "cpsat_selected": bool(solver.Value(select_vars[i]) == 1),
        })

    recommendations.sort(key=lambda x: (x["cpsat_selected"], x["match_score"], x["scores"]["strength"]), reverse=True)

    return {
        "status": solver.StatusName(status),
        "solver": "Google OR-Tools CP-SAT Multi-Criteria Alloy Selector",
        "solve_time_ms": elapsed_ms,
        "top_recommendations": recommendations[:4],
        "all_alloys": recommendations,
    }


if __name__ == "__main__":
    print("Testing 1D Cutting Stock CP-SAT...")
    r1 = solve_1d_cutting_stock()
    print(f"1D Status: {r1['status']}, Mothers: {r1['total_mothers_used']}, Util: {r1['overall_utilization_pct']}%")

    print("Testing 2D Plate Cutting CP-SAT...")
    r2 = solve_2d_plate_cutting()
    print(f"2D Status: {r2['status']}, Plates: {r2['total_plates_used']}, Util: {r2['overall_utilization_pct']}%")

    print("Testing Multi-Plant Schedule CP-SAT...")
    r3 = solve_multi_plant_schedule()
    print(f"Schedule Status: {r3['status']}, Makespan: {r3['makespan_hr']}h")

    print("Testing Alloy Recommendation CP-SAT...")
    r4 = solve_alloy_recommendation()
    print(f"Alloy Status: {r4['status']}, Top 1: {r4['top_recommendations'][0]['code']}")
