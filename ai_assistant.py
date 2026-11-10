# -*- coding: utf-8 -*-
"""
Harvard Enterprises AI Customer Service & Google OR-Tools CP-SAT Optimization Engine
================================================================================
Uses `ortools.sat.python.cp_model` to provide:
1. 1D Cutting Stock Optimization (母材定寸裁切餘料最小化求解)
2. Optimal Inventory Specification Matching (3,071 筆現貨與模具智能選料求解)
3. Multi-Criteria Alloy Recommendation & Natural Language Metallurgy QA
"""

import re
import math
from ortools.sat.python import cp_model


# ==============================================================================
#  1. Google OR-Tools CP-SAT: 1D Cutting Stock Solver (一維母材下料最佳化)
# ==============================================================================
def solve_cutting_stock_cpsat(stock_length_mm=3000, kerf_mm=3, demands=None):
    """
    Solves the 1D Cutting Stock Problem using Google OR-Tools CP-SAT (`cp_model`).

    Parameters:
        stock_length_mm (int): Standard mother bar/plate length in mm (default 3000mm).
        kerf_mm (int): Saw blade kerf loss per cut in mm (default 3mm).
        demands (list of dict): [{"length": 680, "qty": 3}, {"length": 450, "qty": 4}, ...]

    Returns:
        dict: Optimal cutting plan, utilization rate, waste stats, and solver metadata.
    """
    if not demands:
        demands = [
            {"length": 800, "qty": 3},
            {"length": 550, "qty": 4},
            {"length": 420, "qty": 5}
        ]

    stock_L = max(100, min(12000, int(stock_length_mm)))
    kerf = max(0, min(20, int(kerf_mm)))

    valid_demands = []
    for d in demands:
        try:
            length = int(float(d.get("length", 0)))
            qty = int(float(d.get("qty", 0)))
            if 10 <= length <= stock_L and 1 <= qty <= 100:
                valid_demands.append({"length": length, "qty": qty})
        except (ValueError, TypeError):
            continue

    if not valid_demands:
        return {
            "success": False,
            "error": f"請輸入有效的裁切長度（10mm ~ {stock_L}mm）與數量（1 ~ 100支）。"
        }

    # Upper bound on number of stock bars needed
    max_bars = 0
    for d in valid_demands:
        max_per_bar = max(1, (stock_L + kerf) // (d["length"] + kerf))
        max_bars += math.ceil(d["qty"] / max_per_bar)
    max_bars = min(max_bars, 60)

    model = cp_model.CpModel()
    num_items = len(valid_demands)

    # Decision variables:
    # y[b]: 1 if bar b is used, 0 otherwise
    y = [model.NewBoolVar(f"bar_used_{b}") for b in range(max_bars)]

    # x[i, b]: number of pieces of demand i cut from bar b
    x = {}
    for i, d in enumerate(valid_demands):
        max_possible = min(d["qty"], (stock_L + kerf) // (d["length"] + kerf))
        for b in range(max_bars):
            x[(i, b)] = model.NewIntVar(0, max_possible, f"x_{i}_{b}")

    # Constraint 1: Every demand quantity must be exactly satisfied
    for i, d in enumerate(valid_demands):
        model.Add(sum(x[(i, b)] for b in range(max_bars)) == d["qty"])

    # Constraint 2: Total cut lengths + kerf on bar b cannot exceed stock_L * y[b]
    # Note: If k pieces are cut on a bar, there are at most k saw cuts (each piece + kerf <= stock_L + kerf)
    for b in range(max_bars):
        used_len = sum(x[(i, b)] * (valid_demands[i]["length"] + kerf) for i in range(num_items))
        model.Add(used_len <= (stock_L + kerf) * y[b])

    # Constraint 3: Symmetry breaking (use lower-indexed bars first, and order by used length)
    for b in range(max_bars - 1):
        model.Add(y[b] >= y[b + 1])

    # Objective: Minimize total bars used (primary weight = 100,000),
    # and slightly prefer concentrating cuts on earlier bars so the last bar has maximum reusable offcut
    objective_terms = []
    for b in range(max_bars):
        # Primary cost: using a bar costs 100000; secondary bonus: earlier bars have slightly lower weight
        objective_terms.append(y[b] * (100000 + b * 10))
        for i in range(num_items):
            objective_terms.append(x[(i, b)] * b)

    model.Minimize(sum(objective_terms))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 3.0
    solver.parameters.num_search_workers = 4
    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {
            "success": False,
            "error": "CP-SAT 求解器無法在限制內找到可行裁切方案，請確認單支裁切長度未超過母材總長。"
        }

    bars_plan = []
    total_net_cut_mm = 0
    total_kerf_mm = 0

    for b in range(max_bars):
        if solver.Value(y[b]) == 1:
            cuts_on_bar = []
            pieces_count = 0
            net_mm = 0
            for i, d in enumerate(valid_demands):
                cnt = solver.Value(x[(i, b)])
                if cnt > 0:
                    cuts_on_bar.append({
                        "length": d["length"],
                        "count": cnt,
                        "label": f"{d['length']}mm × {cnt}支"
                    })
                    pieces_count += cnt
                    net_mm += d["length"] * cnt

            # Kerf count: if pieces occupy full bar, pieces_count - 1; else pieces_count cuts
            kerf_used = pieces_count * kerf
            if net_mm + kerf_used > stock_L:
                kerf_used = max(0, (pieces_count - 1) * kerf)

            rem_mm = max(0, stock_L - net_mm - kerf_used)
            utilization = round((net_mm / stock_L) * 100, 1)

            total_net_cut_mm += net_mm
            total_kerf_mm += kerf_used

            # Build exact linear cut segments for SVG CAD visualization
            linear_segments = []
            curr_pos = 0
            piece_idx = 1
            for c in cuts_on_bar:
                for _ in range(c["count"]):
                    linear_segments.append({
                        "type": "piece",
                        "index": piece_idx,
                        "start_mm": curr_pos,
                        "length_mm": c["length"],
                        "end_mm": curr_pos + c["length"],
                        "label": f"{c['length']}mm"
                    })
                    curr_pos += c["length"]
                    piece_idx += 1
                    if kerf > 0 and (curr_pos + kerf <= stock_L):
                        linear_segments.append({
                            "type": "kerf",
                            "start_mm": curr_pos,
                            "length_mm": kerf,
                            "end_mm": curr_pos + kerf,
                            "label": f"鋸縫 {kerf}mm"
                        })
                        curr_pos += kerf

            if rem_mm > 0:
                linear_segments.append({
                    "type": "remnant",
                    "start_mm": curr_pos,
                    "length_mm": rem_mm,
                    "end_mm": stock_L,
                    "label": f"餘料 {rem_mm}mm"
                })

            bars_plan.append({
                "bar_no": len(bars_plan) + 1,
                "cuts": cuts_on_bar,
                "cuts_summary": " + ".join(c["label"] for c in cuts_on_bar),
                "net_used_mm": net_mm,
                "kerf_loss_mm": kerf_used,
                "remnant_mm": rem_mm,
                "utilization_pct": utilization,
                "segments": linear_segments
            })

    total_bars_used = len(bars_plan)
    total_stock_mm = total_bars_used * stock_L
    overall_utilization = round((total_net_cut_mm / total_stock_mm) * 100, 2) if total_stock_mm else 0
    total_remnant_mm = max(0, total_stock_mm - total_net_cut_mm - total_kerf_mm)

    # Generate humanized conversational voice commentary script for Edge-TTS
    first_bar = bars_plan[0] if bars_plan else None
    first_cuts_desc = first_bar["cuts_summary"] if first_bar else ""
    speech_commentary = (
        f"您好！我是賀華實業的 AI 工程師。透過 AI 運籌學求解器運算，"
        f"為您規劃出全域最省料的排版方案。這批裁切需求共需使用 {total_bars_used} 支標準 {stock_L} 毫米母材，"
        f"整體材料利用率達到 {overall_utilization} 百分比。"
    )
    if first_bar:
        speech_commentary += f"第 1 支母材為您裁切 {first_cuts_desc}，扣除鋸縫損耗後，保留了 {first_bar['remnant_mm']} 毫米的可用餘料。"
    if total_bars_used > 1:
        speech_commentary += f"其餘母材亦已緊湊排程，將切屑廢料降至最低。您可以直接帶入詢價單，或由我們安排專車裁切配送！"
    else:
        speech_commentary += "此方案材料浪費極少，您可以直接帶入詢價單，我們隨時為您備料裁切！"

    return {
        "success": True,
        "solver_status": "OPTIMAL (全域最佳解)" if status == cp_model.OPTIMAL else "FEASIBLE (可行優化解)",
        "solve_time_ms": round(solver.WallTime() * 1000, 2),
        "stock_length_mm": stock_L,
        "kerf_mm": kerf,
        "total_bars_used": total_bars_used,
        "total_pieces_cut": sum(d["qty"] for d in valid_demands),
        "overall_utilization_pct": overall_utilization,
        "total_net_cut_mm": total_net_cut_mm,
        "total_kerf_mm": total_kerf_mm,
        "total_remnant_mm": total_remnant_mm,
        "demands": valid_demands,
        "bars_plan": bars_plan,
        "speech_commentary": speech_commentary
    }


# ==============================================================================
#  2. Google OR-Tools CP-SAT: Optimal Alloy & Spec Selection (最佳材質與規格選型求解)
# ==============================================================================
ALLOY_PROFILES = [
    {"alloy": "6061-T651", "strength": 86, "corrosion": 88, "machinability": 92, "anodizing": 96, "weldability": 85, "cost_efficiency": 90, "desc": "精密機械、自動化夾治具、半導體腔體與陽極處理主力"},
    {"alloy": "7075-T651", "strength": 98, "corrosion": 65, "machinability": 96, "anodizing": 78, "weldability": 40, "cost_efficiency": 65, "desc": "航太超硬鋁、高應力模具、軍工與高剛性傳動零件首選"},
    {"alloy": "5052-H32",  "strength": 62, "corrosion": 96, "machinability": 72, "anodizing": 88, "weldability": 95, "cost_efficiency": 90, "desc": "耐海水腐蝕、折彎鈑金外殼、船舶與機箱結構主力"},
    {"alloy": "5083-H112", "strength": 75, "corrosion": 98, "machinability": 75, "anodizing": 86, "weldability": 96, "cost_efficiency": 82, "desc": "大型船用結構、低溫壓力容器與高耐蝕厚板"},
    {"alloy": "2024-T351", "strength": 90, "corrosion": 58, "machinability": 90, "anodizing": 68, "weldability": 45, "cost_efficiency": 68, "desc": "高疲勞強度航太結構、飛機骨架與高應力扣件"},
    {"alloy": "1050-H14",  "strength": 35, "corrosion": 98, "machinability": 55, "anodizing": 95, "weldability": 98, "cost_efficiency": 96, "desc": "高導電導熱純鋁、反射板、散熱鰭片與深抽沖壓件"},
    {"alloy": "Korea 4N 超平板", "strength": 78, "corrosion": 95, "machinability": 92, "anodizing": 98, "weldability": 90, "cost_efficiency": 75, "desc": "南韓進口超低殘留內應力精密銑面鋁板，雙面公差極致穩定"}
]


def solve_optimal_alloy_cpsat(weights=None, min_constraints=None):
    """
    Uses Google OR-Tools CP-SAT (`cp_model.CpModel`) to select the optimal alloy
    given engineering priority weights and minimum threshold constraints.
    """
    weights = weights or {"strength": 5, "corrosion": 5, "machinability": 5, "anodizing": 5, "weldability": 3, "cost_efficiency": 5}
    min_constraints = min_constraints or {}

    model = cp_model.CpModel()
    n = len(ALLOY_PROFILES)
    select = [model.NewBoolVar(f"select_alloy_{i}") for i in range(n)]

    # Must pick exactly 1 primary recommendation
    model.Add(sum(select) == 1)

    # Apply hard engineering constraints if feasible
    for i, prof in enumerate(ALLOY_PROFILES):
        for prop, min_val in min_constraints.items():
            if prof.get(prop, 0) < min_val:
                model.Add(select[i] == 0)

    # Objective: Maximize weighted engineering score
    scores = []
    for i, prof in enumerate(ALLOY_PROFILES):
        score = sum(prof.get(k, 50) * int(weights.get(k, 5)) for k in weights)
        scores.append((score, i, prof))

    model.Maximize(sum(score * select[i] for score, i, _ in scores))

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for score, i, prof in scores:
            if solver.Value(select[i]) == 1:
                ranked = sorted(scores, key=lambda x: x[0], reverse=True)
                return {
                    "primary": prof,
                    "alternatives": [r[2] for r in ranked if r[2]["alloy"] != prof["alloy"]][:2]
                }

    # Fallback if hard constraints were too strict: relax constraints and pick top weighted
    ranked = sorted(scores, key=lambda x: x[0], reverse=True)
    return {
        "primary": ranked[0][2],
        "alternatives": [r[2] for r in ranked[1:3]]
    }


def extract_number(text):
    m = re.search(r'(\d+(?:\.\d+)?)', str(text))
    return float(m.group(1)) if m else None


def find_optimal_inventory_specs_cpsat(query_text, inventory_data):
    """
    Searches inventory_data and uses CP-SAT to rank/select the closest available
    stock/mold specifications with minimal machining allowance waste when a target dimension is requested.
    """
    q = query_text.lower().strip()

    # Extract alloy if mentioned
    target_alloy = None
    for al in ["7075", "6061", "5083", "5052", "2024", "1050", "4n"]:
        if al in q:
            target_alloy = al
            break

    # Extract target shape
    target_shape = None
    shape_keywords = [
        ("圓棒", ["圓棒", "丸棒", "round bar", "棒"]),
        ("圓管", ["圓管", "管", "tube", "pipe"]),
        ("扁條", ["扁條", "鋁排", "扁鋁", "flat"]),
        ("四方條", ["四方條", "方棒", "方條"]),
        ("正方管", ["正方管", "方管"]),
        ("長方管", ["長方管", "矩管"]),
        ("六角條", ["六角", "六方"]),
        ("鋁板", ["鋁板", "厚", "板", "plate", "sheet"])
    ]
    for shape_label, kw_list in shape_keywords:
        if any(k in q for k in kw_list):
            target_shape = shape_label
            break

    # Extract target dimension (e.g. 厚 10mm, 直徑 50mm, 25mm)
    dim_match = re.search(r'(?:厚|直徑|外徑|對邊|dia\.?|φ|ψ|t\s*=?\s*)?\s*(\d+(?:\.\d+)?)\s*(?:mm|公厘|ミリ)?', q)
    target_dim = float(dim_match.group(1)) if dim_match else None
    if target_dim in (6061, 7075, 5052, 5083, 2024, 1050, 3000):
        # Look for another number that is not the alloy code
        nums = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', q) if float(x) not in (6061, 7075, 5052, 5083, 2024, 1050, 3000)]
        target_dim = nums[0] if nums else None

    candidates = []
    for item in inventory_data:
        cat = str(item.get("category", ""))
        mat = str(item.get("material", ""))
        dim = str(item.get("dimension", ""))
        size = str(item.get("size", ""))

        if target_alloy and target_alloy not in mat.lower() and target_alloy not in cat.lower():
            continue
        if target_shape and target_shape not in cat:
            continue

        item_dim_val = extract_number(dim)
        candidates.append((item, item_dim_val))

    if not candidates:
        candidates = [(item, extract_number(item.get("dimension", ""))) for item in inventory_data[:100]]

    # If target_dim is specified, use CP-SAT to select up to 5 optimal specs that satisfy
    # dimension >= target_dim (machining allowance >= 0) while minimizing overshoot + prioritizing stock
    if target_dim is not None:
        valid_cands = [(it, d) for it, d in candidates if d is not None and d >= target_dim and (d - target_dim) <= max(30.0, target_dim * 0.6)]
        if not valid_cands:
            valid_cands = [(it, d) for it, d in candidates if d is not None]

        valid_cands = valid_cands[:80]
        if valid_cands:
            model = cp_model.CpModel()
            k_pick = min(5, len(valid_cands))
            pick = [model.NewBoolVar(f"pick_{i}") for i in range(len(valid_cands))]
            model.Add(sum(pick) == k_pick)

            penalties = []
            for i, (it, d) in enumerate(valid_cands):
                overshoot = abs(d - target_dim)
                under_penalty = 5000 if d < target_dim else 0
                mold_penalty = 20 if it.get("group") == "mold" else 0
                cost = int(overshoot * 100) + under_penalty + mold_penalty
                penalties.append(cost * pick[i])

            model.Minimize(sum(penalties))
            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = 1.0
            status = solver.Solve(model)

            if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                selected = [valid_cands[i][0] for i in range(len(valid_cands)) if solver.Value(pick[i]) == 1]
                selected.sort(key=lambda x: abs((extract_number(x.get("dimension", "")) or 0) - target_dim))
                return selected

    return [c[0] for c in candidates[:6]]


# ==============================================================================
#  3. Main Conversational AI Handler (AI 客服對話大腦)
# ==============================================================================
def process_ai_chat(message, inventory_data, lang='zh-TW'):
    """
    Processes user message and returns an AI response with structured cards,
    CP-SAT optimization results, and quick RFQ actions in the user's selected language.
    """
    msg = (message or "").strip()
    low = msg.lower()
    is_en = lang == 'en' or any(k in low for k in ['hello', 'hi', 'cut', 'cutting', 'stock', 'quote', 'recommend', 'alloy', 'mtr'])
    is_ja = lang == 'ja' or any(k in low for k in ['こんにちは', '見積', '切断', '歩留', '合金', '規格', 'アルミニウム'])
    is_ko = lang == 'ko' or any(k in low for k in ['안녕', '견적', '절단', '규격', '합금', '알루미늄', '재고'])

    if not msg or low in ["hello", "hi", "hey", "help", "你好", "您好", "哈囉", "嗨", "こんにちは", "안녕", "안녕하세요"]:
        if is_en:
            return {"reply": "Hello! I am the **Harvard Enterprises AI Engineering Assistant**. Would you like to check current stock specifications, get alloy recommendations, or calculate 1D cutting stock optimization?", "specs": [], "cutting_plan": None}
        elif is_ja:
            return {"reply": "こんにちは！**賀華実業（HARVARD）AI 営業技術アシスタント**です。在庫規格の検索、材料選定のご相談、または定寸切断の最適化計算をご案内いたします。", "specs": [], "cutting_plan": None}
        elif is_ko:
            return {"reply": "안녕하십니까! **하버드실업(HARVARD) AI 엔지니어링 챗봇**입니다. 재고 규격 검색, 소재 추천, 또는 모재 절단 최적화 계산을 도와드릴까요?", "specs": [], "cutting_plan": None}
        return {
            "reply": "您好！我是 **賀華實業 AI 智能工程客服**。請問今天需要查詢現貨規格、鋁合金選料建議，還是進行母材定寸裁切下料最佳化計算呢？",
            "specs": [],
            "cutting_plan": None
        }

    # 1. Check if the user is asking for Cutting Stock Optimization (下料 / 裁切 / CP-SAT 算料)
    if any(k in low for k in ["下料", "排料", "裁切優化", "裁切最佳化", "cp-sat", "ortools", "餘料", "幾支母材", "切", "cut", "cutting", "stock len", "切断", "歩留", "절단", "모재"]):
        pairs = re.findall(r'(\d{2,4})\s*(?:mm|公厘)?\s*[x*×,，:：\s]\s*(\d{1,3})\s*(?:支|件|段|片|pcs|ea)?', low)
        stock_match = re.search(r'(?:母材|總長|標準長|原料|stock|raw|定尺)\s*(\d{3,5})', low)
        stock_len = int(stock_match.group(1)) if stock_match else 3000

        demands = []
        for l_str, q_str in pairs:
            l_val = int(l_str)
            q_val = int(q_str)
            if l_val != stock_len and 10 <= l_val <= stock_len and 1 <= q_val <= 100:
                demands.append({"length": l_val, "qty": q_val})

        if demands:
            plan = solve_cutting_stock_cpsat(stock_length_mm=stock_len, kerf_mm=3, demands=demands)
            if plan.get("success"):
                if is_en:
                    reply_lines = [
                        f"🧮 **Cutting Stock Optimization Solved!**",
                        f"• **Solver Status**: `{plan['solver_status']}` (computed in `{plan['solve_time_ms']} ms`)",
                        f"• **Stock Length**: `{plan['stock_length_mm']} mm` (Kerf blade width `{plan['kerf_mm']} mm`)",
                        f"• **Total Stock Bars Needed**: **`{plan['total_bars_used']} bars`** (Total `{plan['total_pieces_cut']} cut segments`)",
                        f"• **Overall Utilization**: **`{plan['overall_utilization_pct']}%`** (Total Scrap `{plan['total_remnant_mm']} mm`)",
                        "",
                        "📋 **Optimal Cutting Schedule Detail**:"
                    ]
                    for b in plan["bars_plan"]:
                        reply_lines.append(
                            f"  - **Bar #{b['bar_no']}**: Cuts `{b['cuts_summary']}` ｜ Net `{b['net_used_mm']}mm` ｜ Remnant `{b['remnant_mm']}mm` (Yield {b['utilization_pct']}%)"
                        )
                    voice_script = f"Cutting stock calculation completed. A total of {plan['total_bars_used']} stock bars are needed with an overall utilization of {plan['overall_utilization_pct']} percent."
                elif is_ja:
                    reply_lines = [
                        f"🧮 **定寸切断最適化計算が完了しました！**",
                        f"• **求解状態**：`{plan['solver_status']}`（計算時間 `{plan['solve_time_ms']} ms`）",
                        f"• **母材定尺**：`{plan['stock_length_mm']} mm`（鋸刃切り代 `{plan['kerf_mm']} mm`）",
                        f"• **必要母材本数**：**`{plan['total_bars_used']} 本`**（合計切断 `{plan['total_pieces_cut']} 点`）",
                        f"• **総合歩留まり率**：**`{plan['overall_utilization_pct']}%`**（総端材 `{plan['total_remnant_mm']} mm`）",
                        "",
                        "📋 **最適切断スケジュール詳細**："
                    ]
                    for b in plan["bars_plan"]:
                        reply_lines.append(
                            f"  - **第 {b['bar_no']} 本目**：切断 `{b['cuts_summary']}` ｜ 実消費 `{b['net_used_mm']}mm` ｜ 残材 `{b['remnant_mm']}mm` (歩留まり {b['utilization_pct']}%)"
                        )
                    voice_script = f"定寸切断の最適化が完了しました。必要な母材は合計{plan['total_bars_used']}本、歩留まり率は{plan['overall_utilization_pct']}パーセントです。"
                elif is_ko:
                    reply_lines = [
                        f"🧮 **모재 절단 최적화 계산 완료!**",
                        f"• **해결 상태**：`{plan['solver_status']}`（소요 시간 `{plan['solve_time_ms']} ms`）",
                        f"• **원자재 규격**：`{plan['stock_length_mm']} mm`（톱날 손실 `{plan['kerf_mm']} mm` 포함）",
                        f"• **최소 필요 모재**：**`{plan['total_bars_used']} 본`**（총 절단 `{plan['total_pieces_cut']} 개`）",
                        f"• **종합 수율(이용률)**：**`{plan['overall_utilization_pct']}%`**（총 잔재 `{plan['total_remnant_mm']} mm`）",
                        "",
                        "📋 **최적 절단 스케줄 상세**："
                    ]
                    for b in plan["bars_plan"]:
                        reply_lines.append(
                            f"  - **제 {b['bar_no']} 본**：절단 `{b['cuts_summary']}` ｜ 실사용 `{b['net_used_mm']}mm` ｜ 잔여 `{b['remnant_mm']}mm` (수율 {b['utilization_pct']}%)"
                        )
                    voice_script = f"모재 절단 최적화 계산이 완료되었습니다. 최소 {plan['total_bars_used']}본의 원자재가 필요하며 종합 수율은 {plan['overall_utilization_pct']}퍼센트입니다."
                else:
                    reply_lines = [
                        f"🧮 **智慧母材下料最佳化計算完成！**",
                        f"• **求解狀態**：`{plan['solver_status']}`（耗時 `{plan['solve_time_ms']} ms`）",
                        f"• **母材長度**：`{plan['stock_length_mm']} mm`（含每刀鋸縫損耗 `{plan['kerf_mm']} mm`）",
                        f"• **最少需用母材**：**`{plan['total_bars_used']} 支`**（共裁切 `{plan['total_pieces_cut']} 段`）",
                        f"• **材料總利用率**：**`{plan['overall_utilization_pct']}%`**（總餘料 `{plan['total_remnant_mm']} mm`）",
                        "",
                        "📋 **最佳裁切排程明細**："
                    ]
                    for b in plan["bars_plan"]:
                        reply_lines.append(
                            f"  - **第 {b['bar_no']} 支**：裁切 `{b['cuts_summary']}` ｜ 實耗 `{b['net_used_mm']}mm` ｜ 餘料 `{b['remnant_mm']}mm` (利用率 {b['utilization_pct']}%)"
                        )
                    voice_script = plan.get("speech_commentary")

                return {
                    "reply": "\n".join(reply_lines),
                    "specs": [],
                    "cutting_plan": plan,
                    "voice_script": voice_script
                }

    # 2. Check if user asks for Alloy Selection / Recommendation (選料 / 推薦 / 陽極 / 海水 / 航太 / 哪種鋁)
    if any(k in low for k in ["推薦", "選料", "適合", "哪種", "差在哪", "比較", "陽極", "海水", "耐蝕", "航太", "高強度", "超平板", "變形", "recommend", "alloy", "anodiz", "strength", "corrosion", "アルマイト", "強度", "耐食", "추천", "합금", "아노다이징", "내식"]):
        weights = {"strength": 5, "corrosion": 5, "machinability": 5, "anodizing": 5, "weldability": 3, "cost_efficiency": 5}
        min_cons = {}
        if any(k in low for k in ["陽極", "外觀", "染色", "硬陽", "anodiz", "アルマイト", "아노다이징"]):
            weights["anodizing"] = 15
            min_cons["anodizing"] = 85
        if any(k in low for k in ["高強", "航太", "超硬", "模具", "剛性", "strength", "aerospace", "強度", "강도", "항공"]):
            weights["strength"] = 18
            min_cons["strength"] = 85
        if any(k in low for k in ["海水", "船舶", "耐蝕", "防鏽", "折彎", "鈑金", "corrosion", "marine", "耐食", "내식", "해수"]):
            weights["corrosion"] = 16
            weights["weldability"] = 12
            min_cons["corrosion"] = 90
        if any(k in low for k in ["超平", "不變形", "低應力", "半導體", "真空腔", "semiconductor", "半導体", "반도체"]):
            weights["anodizing"] = 15
            weights["corrosion"] = 15

        rec = solve_optimal_alloy_cpsat(weights, min_cons)
        prim = rec["primary"]
        alts = rec["alternatives"]
        matched_specs = find_optimal_inventory_specs_cpsat(prim["alloy"][:4], inventory_data)

        if is_en:
            reply = (
                f"🔬 **Engineering Alloy Selection Recommendation**:\n\n"
                f"🏆 **Top Recommended Alloy: `{prim['alloy']}`**\n"
                f"• **Key Advantage**: {prim['desc']}\n"
                f"• **Performance**: Strength `{prim['strength']}` ｜ Corrosion `{prim['corrosion']}` ｜ Machinability `{prim['machinability']}` ｜ Anodizing `{prim['anodizing']}`\n\n"
                f"💡 **Secondary Alternatives**: `{alts[0]['alloy']}`, `{alts[1]['alloy']}`\n"
                f"Real-time stock specs from Harvard Enterprises have been retrieved below for quick quotation:"
            )
            voice_script = f"Our top recommended alloy is {prim['alloy']}. Matching stock inventory is listed below."
        elif is_ja:
            reply = (
                f"🔬 **材料選定・合金エンジニアリング推奨**：\n\n"
                f"🏆 **第一推奨合金：`{prim['alloy']}`**\n"
                f"• **主な特徴**：{prim['desc']}\n"
                f"• **評価指標**：強度スコア `{prim['strength']}` ｜ 耐食性 `{prim['corrosion']}` ｜ 切削性 `{prim['machinability']}` ｜ アルマイト適性 `{prim['anodizing']}`\n\n"
                f"💡 **代替候補合金**：`{alts[0]['alloy']}`、`{alts[1]['alloy']}`\n"
                f"現在庫の規格を下に一覧表示しました。ワンクリックで見積りに追加可能です："
            )
            voice_script = f"最適な推奨合金は {prim['alloy']} です。該当する在庫規格を下に表示しました。"
        elif is_ko:
            reply = (
                f"🔬 **엔지니어링 소재 선정 추천**：\n\n"
                f"🏆 **1순위 추천 합금：`{prim['alloy']}`**\n"
                f"• **핵심 장점**：{prim['desc']}\n"
                f"• **성능 지표**：강도 점수 `{prim['strength']}` ｜ 내식성 `{prim['corrosion']}` ｜ 절삭성 `{prim['machinability']}` ｜ 아노다이징 `{prim['anodizing']}`\n\n"
                f"💡 **대체 후보 합금**：`{alts[0]['alloy']}`、`{alts[1]['alloy']}`\n"
                f"하버드실업 보유 실시간 재고 규격을 아래에 연동했습니다. 바로 견적에 추가하실 수 있습니다："
            )
            voice_script = f"가장 추천하는 합금은 {prim['alloy']}입니다. 아래에서 보유 재고를 확인해 보세요."
        else:
            reply = (
                f"🔬 **智慧工程材質選型建議**：\n\n"
                f"🏆 **首選推薦牌號：`{prim['alloy']}`**\n"
                f"• **核心優勢**：{prim['desc']}\n"
                f"• **工程指標**：強度評分 `{prim['strength']}` ｜ 耐蝕性 `{prim['corrosion']}` ｜ 切削性 `{prim['machinability']}` ｜ 陽極效果 `{prim['anodizing']}`\n\n"
                f"💡 **次要替代方案**：`{alts[0]['alloy']}`（{alts[0]['desc']}）、`{alts[1]['alloy']}`\n"
                f"下方已為您同步檢索賀華實業現有庫存規格，可一鍵加入詢價單："
            )
            voice_script = (
                f"為您推薦首選合金牌號為 {prim['alloy']}，核心特點是：{prim['desc']}。"
                f"若有其他考量，亦可參考次選 {alts[0]['alloy']}。下方已為您同步檢索庫存規格，歡迎直接加入詢價單！"
            )

        return {
            "reply": reply,
            "specs": matched_specs[:5],
            "cutting_plan": None,
            "voice_script": voice_script
        }

    # 3. Check if user asks about company branch / contact / delivery / mill certificate
    if any(k in low for k in ["據點", "電話", "地址", "台北", "八里", "新竹", "台中", "台南", "聯絡", "配送", "送貨", "材質證明", "檢驗", "rohs", "branch", "taipei", "phone", "address", "mtr", "cert", "拠点", "ミルシート", "전화", "주소", "밀시트"]):
        if is_en:
            reply = (
                "📍 **Harvard Enterprises Nationwide Hubs & Service Network**:\n\n"
                "• **Taipei Headquarters**: 11F-1, No. 27, Sec. 1, Zhongshan N. Rd., Taipei (Mutual Building) ｜ ☎️ `+886-2-2542-4323`\n"
                "• **Taipei Plant / Bali Warehouse**: No. 201-28, Sec. 2, Zhonghua Rd., Bali Dist., New Taipei City ｜ ☎️ `+886-2-8630-2258`\n"
                "• **Hsinchu Plant (Yongsyu)**: No. 56, Zhonghe St., Zhubei City, Hsinchu County ｜ ☎️ `+886-3-656-9699`\n"
                "• **Taichung Plant 1**: No. 5, Industrial 23rd Rd., Nantun Dist., Taichung City ｜ ☎️ `+886-4-2350-8800`\n"
                "• **Taichung Plant 2 (Slitting Center)**: No. 3, Industrial 23rd Rd., Nantun Dist., Taichung City ｜ ☎️ `+886-4-2355-8855`\n"
                "• **Tainan Plant**: No. 58, Zhongyi 1st St., Rende Dist., Tainan City ｜ ☎️ `+886-6-270-2885`\n\n"
                "✅ **Certified Quality Assurance**: Original Mill Test Sheets (MTR), RoHS 2.0, and REACH conformity declarations are supplied with all shipments."
            )
            voice_script = "Harvard Enterprises operates direct offices and plants in Taipei, Bali, Hsinchu, Taichung, and Tainan with dedicated delivery fleets and certified mill sheets."
        elif is_ja:
            reply = (
                "📍 **賀華実業（HARVARD）全台湾6大直営拠点とサービス網**：\n\n"
                "• **台北本社**：台北市中山区中山北路一段27号11階之1（互助ビル） ｜ ☎️ `+886-2-2542-4323`\n"
                "• **台北工場／八里倉庫**：新北市八里区中華路二段201-28号 ｜ ☎️ `+886-2-8630-2258`\n"
                "• **新竹工場（永旭材料）**：新竹県竹北市中和街56号 ｜ ☎️ `+886-3-656-9699`\n"
                "• **台中一工場**：台中市南屯区工業区二十三路5号 ｜ ☎️ `+886-4-2350-8800`\n"
                "• **台中二工場（スリッター加工センター）**：台中市南屯区工業区二十三路3号 ｜ ☎️ `+886-4-2355-8855`\n"
                "• **台南工場**：台南市仁徳区忠義一街58号 ｜ ☎️ `+886-6-270-2885`\n\n"
                "✅ **品質保証と検査証明書**：全出荷材に対して原廠ミルシート（MTR）、RoHS / REACH 国際環境基準の適合証明を発行いたします。"
            )
            voice_script = "賀華実業は台北、八里、新竹、台中、台南に直営拠点を構え、全品に原廠ミルシートと環境証明書を添付しております。"
        elif is_ko:
            reply = (
                "📍 **하버드실업(HARVARD) 전국 6대 직영 거점 및 서비스 네트워크**：\n\n"
                "• **타이베이 본사**：타이베이시 중산구 중산북로 1단 27호 11층의 1 (호조빌딩) ｜ ☎️ `+886-2-2542-4323`\n"
                "• **타이베이 공장 / 팔리 창고**：신베이시 팔리구 중화로 2단 201-28호 ｜ ☎️ `+886-2-8630-2258`\n"
                "• **신주 공장 (영욱재료)**：신주현 주베이시 중화가 56호 ｜ ☎️ `+886-3-656-9699`\n"
                "• **타이중 제1공장**：타이중시 난툰구 공업구 23로 5호 ｜ ☎️ `+886-4-2350-8800`\n"
                "• **타이중 제2공장 (슬리터 가공센터)**：타이중시 난툰구 공업구 23로 3호 ｜ ☎️ `+886-4-2355-8855`\n"
                "• **타이난 공장**：타이난시 런더구 중의1가 58호 ｜ ☎️ `+886-6-270-2885`\n\n"
                "✅ **품질 검사 및 인증서 제공**：모든 출하 소재에 대해 정품 밀시트(MTR) 및 RoHS, REACH 환경 인증서가 동봉됩니다."
            )
            voice_script = "하버드실업은 타이베이, 팔리, 신주, 타이중, 타이난 거점을 통해 정품 밀시트와 함께 신속한 전국 배송을 제공합니다."
        else:
            reply = (
                "📍 **賀華實業全台直營樞紐與服務據點（官方真實資料）**：\n\n"
                "• **台北總公司**：104 台北市中山區中山北路一段27號11樓之1（互助大樓） ｜ ☎️ `(02) 2542-4323`\n"
                "• **台北廠／八里倉庫**：249 新北市八里區中華路二段201-28號 ｜ ☎️ `(02) 8630-2258`\n"
                "• **新竹廠（永旭材料）**：302 新竹縣竹北市中和街56號 ｜ ☎️ `(03) 656-9699`\n"
                "• **台中一廠**：408 台中市南屯區工業區二十三路5號 ｜ ☎️ `(04) 2350-8800`\n"
                "• **台中二廠（分條加工中心）**：408 台中市南屯區工業區二十三路3號 ｜ ☎️ `(04) 2355-8855`\n"
                "• **台南廠**：717 台南市仁德區忠義一街58號 ｜ ☎️ `(06) 270-2885`\n\n"
                "✅ **隨貨檢附證明**：每批出廠鋁材皆可提供原廠材質證明書（Mill Sheet / MTR）、RoHS / REACH 國際無毒環保檢驗報告。"
            )
            voice_script = "賀華實業在台北、八里、新竹、台中及台南皆設有直營廠區與分條加工中心，全台專車配送。每批出廠鋁材均可檢附原廠材質分析證明單及環保認證！"

        return {"reply": reply, "specs": [], "cutting_plan": None, "voice_script": voice_script}

    # 4. Inventory / Mold Specification Search with CP-SAT Minimal Machining Allowance Matching
    matched_specs = find_optimal_inventory_specs_cpsat(msg, inventory_data)
    if matched_specs:
        if is_en:
            reply = (
                f"📦 **Optimal Stock & Mold Specifications for \"`{msg}`\"**:\n"
                f"Click **\"＋RFQ\"** below to add items to your inquiry, or switch to **\"🧮 Cutting Stock Optimizer\"** for 1D bar optimization!"
            )
            voice_script = f"Found stock specifications matching {msg}. You can add them directly to your quote."
        elif is_ja:
            reply = (
                f"📦 **「`{msg}`」に最適な在庫および金型スペックを検索しました**：\n"
                f"下の **「＋見積り」** をクリックして見積一覧に追加するか、**「🧮 定寸切断最適化」** で歩留り計算を行えます！"
            )
            voice_script = f"{msg} に該当する在庫規格が見つかりました。見積りに追加可能です。"
        elif is_ko:
            reply = (
                f"📦 **\"`{msg}`\" 최적 재고 및 금형 규격을 검색했습니다**：\n"
                f"아래 **\"＋견적\"** 버튼을 클릭해 견적서에 추가하거나, **\"🧮 절단 최적화\"** 탭에서 수율 계산을 진행하세요!"
            )
            voice_script = f"{msg} 에 해당하는 재고 규격을 검색했습니다. 견적서에 바로 추가하실 수 있습니다."
        else:
            reply = (
                f"📦 **已為您智慧檢索「`{msg}`」的最佳現貨與模具規格**（優先挑選加工裕度最接近、切削餘料最少之項目）：\n"
                f"您可以直接點擊下方規格旁的 **「＋詢價」** 按鈕帶入詢價單，或切換至 **「🧮 CP-SAT 下料優化」** 計算定寸裁切方案！"
            )
            voice_script = f"已為您檢索到最接近 {msg} 的現貨庫存與模具規格。您可以直接點選加入詢價單，或切換至排版優化計算！"

        return {
            "reply": reply,
            "specs": matched_specs[:6],
            "cutting_plan": None,
            "voice_script": voice_script
        }

    if is_en:
        return {
            "reply": (
                "Hello! I am the Harvard Enterprises AI Engineering Assistant. You can try asking:\n"
                "1️⃣ **Stock & Mold Specs**: \"`6061 Round Bar Dia 50mm`\", \"`7075 Plate Thk 20mm`\", \"`Flat Bar`\"\n"
                "2️⃣ **Cutting Stock Optimizer**: \"`Raw stock 3000mm cut 800*3, 550*4, 420*5`\" or open the **\"🧮 Cutting Stock Optimizer\"** tab\n"
                "3️⃣ **Alloy Advice**: \"`Recommend aluminum for hard anodizing & aerospace`\""
            ),
            "specs": [],
            "cutting_plan": None
        }
    elif is_ja:
        return {
            "reply": (
                "こんにちは！賀華実業（HARVARD）AI 営業技術アシスタントです。以下のようなご質問にお答えできます：\n"
                "1️⃣ **在庫・金型検索**：「`6061 丸棒 直径 50mm`」、「`7075 アルミ板 厚さ 20mm`」\n"
                "2️⃣ **定寸切断最適化**：「`母材 3000mm 切断 800*3, 550*4, 420*5`」または上部の **「🧮 定寸切断最適化」** タブ\n"
                "3️⃣ **合金選定相談**：「`硬質アルマイトと高強度に適したアルミ材`」"
            ),
            "specs": [],
            "cutting_plan": None
        }
    elif is_ko:
        return {
            "reply": (
                "안녕하십니까! 하버드실업(HARVARD) AI 엔지니어링 챗봇입니다. 다음과 같이 질문해 보세요：\n"
                "1️⃣ **재고/금형 검색**：「`6061 환봉 직경 50mm`」、「`7075 알루미늄 판재 20mm`」\n"
                "2️⃣ **모재 절단 최적화**：「`원자재 3000mm 절단 800*3, 550*4, 420*5`」 또는 상단 **「🧮 절단 최적화」** 탭\n"
                "3️⃣ **합금 소재 추천**：「`하드 아노다이징 및 고강도에 적합한 알루미늄`」"
            ),
            "specs": [],
            "cutting_plan": None
        }

    return {
        "reply": (
            "您好！我是賀華實業 AI 智能工程客服。您可以試著問我：\n"
            "1️⃣ **查現貨與模具**：「`6061 圓棒 直徑 50mm`」、「`7075 鋁板 厚 20mm`」、「`鋁扁條`」\n"
            "2️⃣ **CP-SAT 母材裁切優化**：「`母材 3000mm 切 800*3, 550*4, 420*5`」或點擊上方 **「🧮 CP-SAT 下料計算」** 頁籤\n"
            "3️⃣ **工程選料建議**：「`推薦適合硬陽與高強度的鋁合金`」、「`海水耐蝕鈑金用哪種鋁？`」"
        ),
        "specs": [],
        "cutting_plan": None,
        "voice_script": "您好！我是賀華實業 AI 智慧工程客服。您可以透過語音或文字向我查詢現貨庫存、工程選料，或是使用 AI 進行母材下料裁切最佳化計算！"
    }
