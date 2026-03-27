"""
=============================================================================
  小児粉薬 用量チェッカー - Streamlit スマホWebアプリ
  app.py  /  起動: streamlit run app.py
=============================================================================
"""

import json
import os
import re
import unicodedata
from dataclasses import dataclass, asdict
from datetime import date
from typing import Optional
import streamlit as st

# ─────────────────────────────────────────────────────────
#  ページ設定（必ず最初に呼ぶ）
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="小児粉薬チェッカー",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────
#  カスタム CSS（スマホ最適化 + 医療グレードデザイン）
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ─────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&family=DM+Mono:wght@400;500&display=swap');

/* ── CSS変数 ─────────────────────────────────────── */
:root {
    --bg:           #0d1117;
    --surface:      #161b22;
    --surface2:     #1c2333;
    --border:       #30363d;
    --teal:         #00d4b1;
    --teal-dim:     #00a88e;
    --teal-glow:    rgba(0,212,177,0.15);
    --red:          #ff4b6e;
    --red-dim:      #cc2244;
    --red-bg:       rgba(255,75,110,0.12);
    --amber:        #ffb347;
    --amber-bg:     rgba(255,179,71,0.12);
    --blue:         #4d9fff;
    --blue-bg:      rgba(77,159,255,0.12);
    --green:        #3dd68c;
    --green-bg:     rgba(61,214,140,0.12);
    --purple:       #c084fc;
    --purple-bg:    rgba(192,132,252,0.12);
    --text:         #e6edf3;
    --text-muted:   #8b949e;
    --text-dim:     #6e7681;
    --radius:       12px;
    --radius-lg:    18px;
    --font:         'Noto Sans JP', sans-serif;
    --mono:         'DM Mono', monospace;
}

/* ── ベースリセット ───────────────────────────────── */
html, body, [class*="css"] {
    font-family: var(--font) !important;
    color: var(--text);
}
.stApp {
    background: var(--bg);
    min-height: 100vh;
}
.block-container {
    padding: 1rem 1rem 4rem !important;
    max-width: 600px !important;
    margin: 0 auto;
}

/* ── ヘッダー ─────────────────────────────────────── */
.app-header {
    background: linear-gradient(135deg, #0d2137 0%, #0d1117 60%);
    border: 1px solid var(--border);
    border-bottom: 2px solid var(--teal);
    border-radius: var(--radius-lg);
    padding: 1.4rem 1.6rem 1.2rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
}
.app-header::before {
    content: "";
    position: absolute;
    top: -60px; right: -60px;
    width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(0,212,177,0.1) 0%, transparent 70%);
    pointer-events: none;
}
.app-header h1 {
    font-size: 1.5rem;
    font-weight: 900;
    letter-spacing: -0.5px;
    margin: 0 0 0.15rem;
    color: #fff;
}
.app-header h1 span { color: var(--teal); }
.app-header p {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin: 0;
    line-height: 1.5;
}
.version-badge {
    display: inline-block;
    background: var(--teal-glow);
    border: 1px solid var(--teal);
    color: var(--teal);
    font-size: 0.65rem;
    font-weight: 700;
    font-family: var(--mono);
    padding: 0.1rem 0.45rem;
    border-radius: 20px;
    margin-bottom: 0.5rem;
    letter-spacing: 0.05em;
}

/* ── セクションカード ─────────────────────────────── */
.section-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.2rem 1.2rem 1rem;
    margin-bottom: 1rem;
}
.section-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.8rem;
    font-weight: 700;
    color: var(--text-muted);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.9rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid var(--border);
}
.section-title .dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--teal);
    box-shadow: 0 0 6px var(--teal);
}

/* ── フォーム要素 ─────────────────────────────────── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div,
.stTextArea > div > div > textarea {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
    font-size: 1rem !important;
    padding: 0.6rem 0.8rem !important;
    min-height: 44px;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: var(--teal) !important;
    box-shadow: 0 0 0 3px var(--teal-glow) !important;
}
label {
    color: var(--text-muted) !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
}

/* ── ボタン ─────────────────────────────────────────── */
.stButton > button {
    width: 100%;
    min-height: 52px;
    font-family: var(--font) !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.03em;
    border-radius: 10px !important;
    border: none !important;
    cursor: pointer;
    transition: all 0.15s ease;
}
.stButton > button[kind="primary"],
.stButton > button:not([kind]) {
    background: linear-gradient(135deg, var(--teal) 0%, var(--teal-dim) 100%) !important;
    color: #0d1117 !important;
    box-shadow: 0 4px 20px rgba(0,212,177,0.3);
}
.stButton > button[kind="primary"]:hover,
.stButton > button:not([kind]):hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 24px rgba(0,212,177,0.4);
}
.stButton > button[kind="secondary"] {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}

/* ── タブ ─────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface2);
    border-radius: 10px;
    padding: 3px;
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: var(--text-muted) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1rem !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: var(--surface) !important;
    color: var(--teal) !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.3) !important;
}

/* ── カメラ・ファイルアップロード ─────────────────── */
.stCameraInput, .uploadedFile {
    background: var(--surface2) !important;
    border: 2px dashed var(--border) !important;
    border-radius: var(--radius) !important;
}
[data-testid="stFileUploadDropzone"] {
    background: var(--surface2) !important;
    border: 2px dashed var(--border) !important;
    border-radius: var(--radius) !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: var(--teal) !important;
}

/* ── 判定結果カード ─────────────────────────────── */
.result-card {
    border-radius: var(--radius);
    padding: 1rem 1.1rem;
    margin-bottom: 0.7rem;
    border-left: 4px solid;
    position: relative;
    overflow: hidden;
}
.result-card::before {
    content: "";
    position: absolute;
    inset: 0;
    opacity: 0.06;
    pointer-events: none;
}
.result-ok     { background: var(--green-bg);  border-color: var(--green);  }
.result-warn   { background: var(--amber-bg);  border-color: var(--amber);  }
.result-over   { background: var(--red-bg);    border-color: var(--red);    }
.result-under  { background: var(--blue-bg);   border-color: var(--blue);   }
.result-manual { background: var(--purple-bg); border-color: var(--purple); }
.result-notfound { background: var(--surface2); border-color: var(--border); }

.result-drug-name {
    font-weight: 700;
    font-size: 0.95rem;
    margin-bottom: 0.3rem;
    color: #fff;
}
.result-matched {
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-bottom: 0.5rem;
}
.result-badge {
    display: inline-block;
    font-weight: 700;
    font-size: 0.78rem;
    font-family: var(--mono);
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    margin-bottom: 0.5rem;
    letter-spacing: 0.05em;
}
.badge-ok     { background: var(--green-bg);  color: var(--green);  border: 1px solid var(--green); }
.badge-warn   { background: var(--amber-bg);  color: var(--amber);  border: 1px solid var(--amber); }
.badge-over   { background: var(--red-bg);    color: var(--red);    border: 1px solid var(--red); }
.badge-under  { background: var(--blue-bg);   color: var(--blue);   border: 1px solid var(--blue); }
.badge-manual { background: var(--purple-bg); color: var(--purple); border: 1px solid var(--purple); }
.badge-notfound { background: var(--surface2); color: var(--text-muted); border: 1px solid var(--border); }

.dose-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.4rem;
    margin-top: 0.5rem;
}
.dose-item {
    background: rgba(255,255,255,0.04);
    border-radius: 6px;
    padding: 0.35rem 0.55rem;
}
.dose-label {
    font-size: 0.65rem;
    color: var(--text-dim);
    margin-bottom: 0.1rem;
    font-weight: 500;
}
.dose-value {
    font-family: var(--mono);
    font-size: 0.88rem;
    font-weight: 500;
    color: var(--text);
}
.result-message {
    font-size: 0.78rem;
    color: var(--text-muted);
    margin-top: 0.45rem;
    line-height: 1.5;
    padding-top: 0.45rem;
    border-top: 1px solid rgba(255,255,255,0.06);
}
.result-notes {
    font-size: 0.72rem;
    color: var(--amber);
    margin-top: 0.3rem;
    line-height: 1.5;
}

/* ── サマリーバー ─────────────────────────────────── */
.summary-bar {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1rem 1.2rem;
    margin-bottom: 1.2rem;
}
.summary-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
    flex-wrap: wrap;
}
.summary-count {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.82rem;
    font-weight: 700;
    font-family: var(--mono);
}
.attention-banner {
    background: var(--red-bg);
    border: 1px solid var(--red);
    border-radius: 8px;
    padding: 0.6rem 0.9rem;
    margin-top: 0.7rem;
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--red);
    text-align: center;
    letter-spacing: 0.02em;
}
.all-ok-banner {
    background: var(--green-bg);
    border: 1px solid var(--green);
    border-radius: 8px;
    padding: 0.6rem 0.9rem;
    margin-top: 0.7rem;
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--green);
    text-align: center;
}

/* ── 処方薬リスト（手動入力） ─────────────────────── */
.drug-entry {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.8rem 0.9rem;
    margin-bottom: 0.5rem;
    position: relative;
}
.drug-entry-header {
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--teal);
    font-family: var(--mono);
    margin-bottom: 0.4rem;
    letter-spacing: 0.05em;
}

/* ── モックOCR結果表示 ───────────────────────────── */
.ocr-result-box {
    background: var(--surface2);
    border: 1px dashed var(--border);
    border-radius: 10px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.8rem;
    font-size: 0.8rem;
    color: var(--text-muted);
}
.ocr-result-box strong { color: var(--teal); }

/* ── フッター ─────────────────────────────────────── */
.footer-note {
    text-align: center;
    font-size: 0.7rem;
    color: var(--text-dim);
    padding: 1rem 0 0.5rem;
    line-height: 1.7;
}

/* ── Streamlitデフォルト要素の上書き ─────────────── */
.stAlert { border-radius: var(--radius) !important; }
hr { border-color: var(--border) !important; }
.stSpinner > div { border-top-color: var(--teal) !important; }
[data-testid="stMetricValue"] { font-family: var(--mono) !important; color: var(--teal) !important; }
[data-testid="stMetricLabel"] { color: var(--text-muted) !important; font-size: 0.75rem !important; }

/* ── スマホ特有の調整 ─────────────────────────────── */
@media (max-width: 480px) {
    .block-container { padding: 0.75rem 0.75rem 4rem !important; }
    .app-header { padding: 1.1rem 1.1rem 0.9rem; }
    .app-header h1 { font-size: 1.3rem; }
    .dose-grid { grid-template-columns: 1fr; }
}

/* ── expander ─────────────────────────────────────── */
.streamlit-expanderHeader {
    background: var(--surface2) !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    color: var(--text-muted) !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
#  定数
# ─────────────────────────────────────────────────────────
MASTER_JSON_PATH = "pediatric_master_full.json"
UNDERDOSE_LOWER_RATIO = 0.80
WARNING_UPPER_RATIO   = 1.20

JUDGMENT_OK       = "OK"
JUDGMENT_OVERDOSE = "Overdose"
JUDGMENT_UNDERDOSE= "Underdose"
JUDGMENT_WARNING  = "Warning"
JUDGMENT_NOT_FOUND= "NotFound"
JUDGMENT_DISABLED = "DisabledDrug"
JUDGMENT_MANUAL   = "ManualCheck"

BADGE_CONFIG = {
    JUDGMENT_OK:       ("✅ 適正",      "badge-ok",      "result-ok"),
    JUDGMENT_WARNING:  ("⚠️ 要確認",    "badge-warn",    "result-warn"),
    JUDGMENT_OVERDOSE: ("🚨 過量投与",  "badge-over",    "result-over"),
    JUDGMENT_UNDERDOSE:("📉 過少投与",  "badge-under",   "result-under"),
    JUDGMENT_NOT_FOUND:("❓ 未収載",    "badge-notfound","result-notfound"),
    JUDGMENT_DISABLED: ("🚫 中止品",    "badge-manual",  "result-manual"),
    JUDGMENT_MANUAL:   ("📋 手動確認",  "badge-manual",  "result-manual"),
}


# ─────────────────────────────────────────────────────────
#  薬剤マスターローダー
# ─────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_master(json_path: str) -> list[dict]:
    if not os.path.exists(json_path):
        st.error(f"薬剤マスターファイルが見つかりません: {json_path}")
        return []
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_name(name: str) -> str:
    name = unicodedata.normalize("NFKC", name).upper()
    name = re.sub(r"[\s　「」【】『』（）()\[\]・\-_/\\]", "", name)
    return name.replace("％", "%")


@st.cache_data(show_spinner=False)
def build_index(json_path: str) -> dict[str, dict]:
    master = load_master(json_path)
    return {normalize_name(e["medicine_name"]): e for e in master}


def find_drug(medicine_name: str, index: dict) -> Optional[dict]:
    q = normalize_name(medicine_name)
    if q in index:
        return index[q]
    # 部分一致
    candidates = [(len(k), v) for k, v in index.items() if q in k or k in q]
    if candidates:
        return sorted(candidates, key=lambda x: -x[0])[0][1]
    # トークン一致
    tokens = re.split(r"[\d%．\.]+", q)
    base = tokens[0] if tokens else q
    if len(base) >= 4:
        candidates = [(len(k), v) for k, v in index.items() if base in k]
        if candidates:
            return sorted(candidates, key=lambda x: -x[0])[0][1]
    return None


# ─────────────────────────────────────────────────────────
#  投与量計算
# ─────────────────────────────────────────────────────────
def calc_standard_dose(entry: dict, weight_kg: float) -> tuple[Optional[float], Optional[float]]:
    form = entry.get("form", "散剤")
    if form == "散剤":
        dmin = entry.get("daily_dose_min_g_per_kg")
        dmax = entry.get("daily_dose_max_g_per_kg")
        if dmin is None:
            amin = entry.get("dose_per_admin_min_g_per_kg")
            amax = entry.get("dose_per_admin_max_g_per_kg")
            if amin:
                return (amin * weight_kg, (amax or amin) * weight_kg)
            return (None, None)
        return (dmin * weight_kg, (dmax or dmin) * weight_kg)
    else:
        dmin = entry.get("daily_dose_min_ml_per_kg")
        dmax = entry.get("daily_dose_max_ml_per_kg")
        if dmin is None:
            amin = entry.get("dose_per_admin_min_ml_per_kg")
            amax = entry.get("dose_per_admin_max_ml_per_kg")
            if amin:
                return (amin * weight_kg, (amax or amin) * weight_kg)
            return (None, None)
        return (dmin * weight_kg, (dmax or dmin) * weight_kg)


def g_to_mg(dose_g: Optional[float], content: Optional[float]) -> Optional[float]:
    if dose_g is None or content is None:
        return None
    return dose_g * content


# ─────────────────────────────────────────────────────────
#  判定エンジン
# ─────────────────────────────────────────────────────────
def judge(prescribed_g: float, std_min_g: Optional[float],
          std_max_g: Optional[float], entry: Optional[dict]) -> tuple[str, str]:
    if entry is None:
        return JUDGMENT_NOT_FOUND, "薬剤マスターに収載されていません。手動確認が必要です。"
    if entry.get("discontinued", False):
        return JUDGMENT_DISABLED, f"販売中止・経過措置品です。代替薬を検討してください。"
    if std_min_g is None or std_max_g is None:
        return JUDGMENT_MANUAL, "固定用量・年齢別投与量の薬剤です。備考欄を確認してください。"

    lower  = std_min_g * UNDERDOSE_LOWER_RATIO
    upper1 = std_max_g * 1.0
    upper2 = std_max_g * WARNING_UPPER_RATIO

    if prescribed_g < lower:
        pct = (1 - prescribed_g / std_min_g) * 100
        return JUDGMENT_UNDERDOSE, f"標準最小量({std_min_g:.2f}g)の{pct:.0f}%不足。治療効果不足の可能性。要疑義照会。"
    elif prescribed_g <= upper1:
        return JUDGMENT_OK, f"適正範囲内（{std_min_g:.2f}〜{std_max_g:.2f}g/日）"
    elif prescribed_g <= upper2:
        pct = (prescribed_g / std_max_g - 1) * 100
        return JUDGMENT_WARNING, f"標準最大量({std_max_g:.2f}g)を{pct:.0f}%超過。処方意図を確認。要疑義照会。"
    else:
        pct = (prescribed_g / std_max_g - 1) * 100
        return JUDGMENT_OVERDOSE, f"標準最大量({std_max_g:.2f}g)を{pct:.0f}%超過（過量投与）。直ちに疑義照会。"


# ─────────────────────────────────────────────────────────
#  メイン判定処理
# ─────────────────────────────────────────────────────────
def run_check(weight_kg: float, drugs: list[dict], index: dict) -> list[dict]:
    results = []
    for drug in drugs:
        name     = drug["medicine_name"]
        daily_g  = drug["daily_dose_g"]
        entry    = find_drug(name, index)

        std_min_g, std_max_g = (None, None)
        prescribed_mg = std_min_mg = std_max_mg = None

        if entry:
            std_min_g, std_max_g = calc_standard_dose(entry, weight_kg)
            content = entry.get("content_mg_per_g") or entry.get("content_mg_per_ml")
            prescribed_mg = g_to_mg(daily_g, content)
            std_min_mg    = g_to_mg(std_min_g, content)
            std_max_mg    = g_to_mg(std_max_g, content)

        jcode, msg = judge(daily_g, std_min_g, std_max_g, entry)

        results.append({
            "medicine_name":         name,
            "matched_name":          entry["medicine_name"] if entry else None,
            "form":                  entry.get("form") if entry else None,
            "category":              f"{entry.get('category','')}/{entry.get('subcategory','')}" if entry else None,
            "prescribed_g":          daily_g,
            "prescribed_mg":         round(prescribed_mg, 2) if prescribed_mg else None,
            "std_min_g":             round(std_min_g, 3) if std_min_g else None,
            "std_max_g":             round(std_max_g, 3) if std_max_g else None,
            "std_min_mg":            round(std_min_mg, 2) if std_min_mg else None,
            "std_max_mg":            round(std_max_mg, 2) if std_max_mg else None,
            "days_supplied":         drug.get("days_supplied", 0),
            "judgment":              jcode,
            "message":               msg,
            "notes":                 entry.get("notes", "") if entry else "",
        })
    return results


# ─────────────────────────────────────────────────────────
#  モック OCR（処方箋解析ダミー）
# ─────────────────────────────────────────────────────────
MOCK_SCENARIOS = {
    "正常処方（5歳・18kg）": {
        "patient": {"age_label": "5歳", "weight_kg": 18.0},
        "drugs": [
            {"medicine_name": "アモキシシリン細粒10%「TCK」",  "daily_dose_g": 5.4, "days_supplied": 5},
            {"medicine_name": "ムコダインDS50%",               "daily_dose_g": 1.1, "days_supplied": 5},
            {"medicine_name": "ムコサールドライシロップ1.5%",   "daily_dose_g": 1.0, "days_supplied": 5},
        ]
    },
    "過量投与（3歳・14kg）": {
        "patient": {"age_label": "3歳", "weight_kg": 14.0},
        "drugs": [
            {"medicine_name": "クラリスドライシロップ10%",      "daily_dose_g": 4.0, "days_supplied": 7},
            {"medicine_name": "カロナール細粒50%",              "daily_dose_g": 2.5, "days_supplied": 3},
        ]
    },
    "過少投与（7歳・22kg）": {
        "patient": {"age_label": "7歳", "weight_kg": 22.0},
        "drugs": [
            {"medicine_name": "セフゾン細粒小児用10%",          "daily_dose_g": 0.5, "days_supplied": 5},
            {"medicine_name": "アスベリンドライシロップ2%",      "daily_dose_g": 0.6, "days_supplied": 5},
        ]
    },
    "混合判定（4歳・16kg）": {
        "patient": {"age_label": "4歳", "weight_kg": 16.0},
        "drugs": [
            {"medicine_name": "ジスロマック細粒小児用10%",       "daily_dose_g": 1.9, "days_supplied": 3},
            {"medicine_name": "アスベリンドライシロップ2%",      "daily_dose_g": 1.2, "days_supplied": 5},
            {"medicine_name": "ホクナリンドライシロップ0.1%小児用","daily_dose_g": 0.64,"days_supplied": 5},
        ]
    },
    "乳児（8ヶ月・8kg）": {
        "patient": {"age_label": "8ヶ月", "weight_kg": 8.0},
        "drugs": [
            {"medicine_name": "タミフルドライシロップ3%",        "daily_dose_g": 1.6, "days_supplied": 5},
            {"medicine_name": "ホクナリンドライシロップ0.1%小児用","daily_dose_g": 0.3,"days_supplied": 5},
        ]
    },
}

def mock_extract_data_from_image(scenario_key: str) -> dict:
    """
    [モック] 処方箋画像のOCR解析を模倣する関数。
    実装時は外部OCR API（Google Vision / AWS Textract 等）の
    レスポンスをパースしてこの形式で返す。
    """
    return MOCK_SCENARIOS[scenario_key]


# ─────────────────────────────────────────────────────────
#  結果カード HTML生成
# ─────────────────────────────────────────────────────────
def render_result_card(r: dict):
    j = r["judgment"]
    badge_label, badge_cls, card_cls = BADGE_CONFIG.get(j, ("不明", "badge-notfound", "result-notfound"))

    matched_str = f"照合: {r['matched_name']}" if r["matched_name"] else "マスター未収載"
    cat_str     = r["category"].strip("/") if r["category"] else ""

    dose_html = ""
    if r["std_min_g"] is not None:
        dose_html = f"""
        <div class="dose-grid">
          <div class="dose-item">
            <div class="dose-label">処方製剤量</div>
            <div class="dose-value">{r['prescribed_g']:.2f} g/日</div>
          </div>
          <div class="dose-item">
            <div class="dose-label">適正範囲（製剤）</div>
            <div class="dose-value">{r['std_min_g']:.3f}〜{r['std_max_g']:.3f} g</div>
          </div>
          {"" if r['prescribed_mg'] is None else f'''
          <div class="dose-item">
            <div class="dose-label">処方力価</div>
            <div class="dose-value">{r['prescribed_mg']:.1f} mg/日</div>
          </div>''' }
          {"" if r['std_min_mg'] is None else f'''
          <div class="dose-item">
            <div class="dose-label">適正範囲（力価）</div>
            <div class="dose-value">{r['std_min_mg']:.1f}〜{r['std_max_mg']:.1f} mg</div>
          </div>''' }
        </div>"""
    else:
        dose_html = f"""
        <div class="dose-grid">
          <div class="dose-item">
            <div class="dose-label">処方製剤量</div>
            <div class="dose-value">{r['prescribed_g']:.2f} g/日</div>
          </div>
        </div>"""

    notes_html = f'<div class="result-notes">⚠ {r["notes"]}</div>' if r["notes"] else ""

    html = f"""
    <div class="result-card {card_cls}">
      <div class="result-drug-name">{r['medicine_name']}</div>
      <div class="result-matched">{matched_str}　{cat_str}</div>
      <span class="result-badge {badge_cls}">{badge_label}</span>
      {dose_html}
      <div class="result-message">{r['message']}</div>
      {notes_html}
    </div>"""
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
#  サマリーバー HTML
# ─────────────────────────────────────────────────────────
def render_summary(results: list[dict]):
    total     = len(results)
    ok        = sum(1 for r in results if r["judgment"] == JUDGMENT_OK)
    warn      = sum(1 for r in results if r["judgment"] == JUDGMENT_WARNING)
    over      = sum(1 for r in results if r["judgment"] == JUDGMENT_OVERDOSE)
    under     = sum(1 for r in results if r["judgment"] == JUDGMENT_UNDERDOSE)
    attention = warn + over + under + \
                sum(1 for r in results if r["judgment"] in [JUDGMENT_NOT_FOUND, JUDGMENT_DISABLED])

    banner = (f'<div class="attention-banner">⚠️ {attention}件の薬剤に要確認あり — 疑義照会を実施してください</div>'
              if attention > 0 else
              '<div class="all-ok-banner">✅ 全薬剤 適正範囲内</div>')

    st.markdown(f"""
    <div class="summary-bar">
      <div class="summary-row">
        <span class="summary-count" style="color:#8b949e">全{total}薬剤</span>
        <span class="summary-count" style="color:#3dd68c">✅ OK:{ok}</span>
        <span class="summary-count" style="color:#ffb347">⚠ Warning:{warn}</span>
        <span class="summary-count" style="color:#ff4b6e">🚨 Over:{over}</span>
        <span class="summary-count" style="color:#4d9fff">📉 Under:{under}</span>
      </div>
      {banner}
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
#  SESSION STATE 初期化
# ─────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "check_results":      None,
        "patient_weight":     10.0,
        "patient_age":        "3歳",
        "drugs":              [{"medicine_name": "", "daily_dose_g": 0.0, "days_supplied": 3}],
        "ocr_ran":            False,
        "selected_scenario":  list(MOCK_SCENARIOS.keys())[0],
        "active_tab":         0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ─────────────────────────────────────────────────────────
#  マスター読み込み
# ─────────────────────────────────────────────────────────
master_index = build_index(MASTER_JSON_PATH)
master_list  = load_master(MASTER_JSON_PATH)
master_names = [e["medicine_name"] for e in master_list if not e.get("discontinued", False)]


# ═════════════════════════════════════════════════════════
#  ページ描画開始
# ═════════════════════════════════════════════════════════

# ── ヘッダー ──────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div class="version-badge">PROTOTYPE v1.0</div>
  <h1>💊 小児粉薬<span>チェッカー</span></h1>
  <p>処方箋の用法・用量を薬剤マスターと照合し、<br>過量・過少投与を自動判定します。</p>
</div>
""", unsafe_allow_html=True)


# ── STEP 1: 処方箋読み取り ────────────────────────────────
st.markdown("""
<div class="section-card">
  <div class="section-title"><span class="dot"></span>STEP 1 　処方箋読み取り</div>
</div>
""", unsafe_allow_html=True)

input_tab1, input_tab2 = st.tabs(["📷 カメラ / ファイル", "🧪 デモデータ"])

with input_tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    capture_mode = st.radio("入力方法", ["カメラで撮影", "ファイルを選択"], horizontal=True, label_visibility="collapsed")

    uploaded_image = None
    if capture_mode == "カメラで撮影":
        uploaded_image = st.camera_input("処方箋を撮影してください", label_visibility="collapsed")
    else:
        uploaded_image = st.file_uploader("処方箋画像を選択", type=["jpg", "jpeg", "png"],
                                          label_visibility="collapsed")

    if uploaded_image:
        st.image(uploaded_image, caption="取り込んだ処方箋", use_column_width=True)
        st.info("📝 OCR解析（実装時はここで画像→テキスト変換）\n\n"
                "現在はデモシナリオのダミーデータで動作します。\n"
                "「デモデータ」タブからシナリオを選んで実行してください。", icon="ℹ️")

with input_tab2:
    scenario_key = st.selectbox(
        "テストシナリオを選択",
        list(MOCK_SCENARIOS.keys()),
        index=0,
        key="selected_scenario_select"
    )
    scenario = MOCK_SCENARIOS[scenario_key]

    st.markdown(f"""
    <div class="ocr-result-box">
      <strong>📋 OCR解析結果（モック）</strong><br>
      患者: {scenario['patient']['age_label']} / {scenario['patient']['weight_kg']}kg<br>
      処方薬剤: {len(scenario['drugs'])}件
      <ul style="margin:0.3rem 0 0; padding-left:1.2rem; font-size:0.78rem;">
        {"".join(f"<li>{d['medicine_name']}　{d['daily_dose_g']}g/日 × {d['days_supplied']}日</li>" for d in scenario['drugs'])}
      </ul>
    </div>""", unsafe_allow_html=True)

    if st.button("📥 このシナリオのデータを読み込む", use_container_width=True, type="secondary"):
        ocr = mock_extract_data_from_image(scenario_key)
        st.session_state["patient_weight"] = ocr["patient"]["weight_kg"]
        st.session_state["patient_age"]    = ocr["patient"]["age_label"]
        st.session_state["drugs"]          = [
            {"medicine_name": d["medicine_name"], "daily_dose_g": d["daily_dose_g"],
             "days_supplied": d["days_supplied"]}
            for d in ocr["drugs"]
        ]
        st.session_state["ocr_ran"]  = True
        st.session_state["check_results"] = None
        st.success("データを読み込みました。下のフォームで確認・修正できます。")
        st.rerun()


# ── STEP 2: 患者情報・処方内容の確認・修正 ───────────────
st.markdown("""
<div class="section-card" style="margin-top:0.5rem">
  <div class="section-title"><span class="dot"></span>STEP 2 　患者情報・処方内容 確認・修正</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])
with col1:
    st.session_state["patient_age"] = st.text_input(
        "年齢", value=st.session_state["patient_age"], placeholder="例: 3歳 / 8ヶ月"
    )
with col2:
    st.session_state["patient_weight"] = st.number_input(
        "体重 (kg)", min_value=0.5, max_value=80.0,
        value=float(st.session_state["patient_weight"]),
        step=0.5, format="%.1f"
    )

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("**処方薬剤リスト**", help="薬剤名はマスターの正式名称に近い形で入力してください。")

# 処方薬剤の入力行
updated_drugs = []
for i, drug in enumerate(st.session_state["drugs"]):
    st.markdown(f'<div class="drug-entry-header">処方 #{i+1}</div>', unsafe_allow_html=True)

    d_col1, d_col2, d_col3 = st.columns([5, 2, 2])
    with d_col1:
        name = st.selectbox(
            "薬剤名", options=[""] + master_names,
            index=(master_names.index(drug["medicine_name"]) + 1
                   if drug["medicine_name"] in master_names else 0),
            key=f"drug_name_{i}", label_visibility="collapsed",
            placeholder="薬剤名を選択..."
        )
    with d_col2:
        dose_g = st.number_input(
            "1日量(g)", min_value=0.0, max_value=50.0,
            value=float(drug["daily_dose_g"]), step=0.1, format="%.2f",
            key=f"drug_dose_{i}", label_visibility="collapsed"
        )
    with d_col3:
        days = st.number_input(
            "日数", min_value=1, max_value=90,
            value=int(drug["days_supplied"]), step=1,
            key=f"drug_days_{i}", label_visibility="collapsed"
        )

    updated_drugs.append({"medicine_name": name, "daily_dose_g": dose_g, "days_supplied": days})

st.session_state["drugs"] = updated_drugs

# 薬剤追加・削除
add_col, del_col = st.columns([3, 1])
with add_col:
    if st.button("＋ 薬剤を追加", use_container_width=True, type="secondary"):
        st.session_state["drugs"].append({"medicine_name": "", "daily_dose_g": 0.0, "days_supplied": 3})
        st.rerun()
with del_col:
    if len(st.session_state["drugs"]) > 1:
        if st.button("削除", use_container_width=True, type="secondary"):
            st.session_state["drugs"].pop()
            st.session_state["check_results"] = None
            st.rerun()


# ── STEP 3: 判定実行 ─────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

run_disabled = (
    st.session_state["patient_weight"] <= 0
    or not any(d["medicine_name"] for d in st.session_state["drugs"])
)

if st.button("🔍　計算・判定を実行する", use_container_width=True,
             type="primary", disabled=run_disabled):
    valid_drugs = [d for d in st.session_state["drugs"] if d["medicine_name"]]
    with st.spinner("判定中..."):
        results = run_check(
            weight_kg=st.session_state["patient_weight"],
            drugs=valid_drugs,
            index=master_index
        )
    st.session_state["check_results"] = results


# ── STEP 4: 結果表示 ─────────────────────────────────────
if st.session_state["check_results"]:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="section-title" style="margin-bottom:0.7rem">
      <span class="dot" style="background:#ff4b6e;box-shadow:0 0 6px #ff4b6e"></span>
      STEP 3 　判定結果
    </div>""", unsafe_allow_html=True)

    results = st.session_state["check_results"]
    render_summary(results)

    for r in results:
        render_result_card(r)

    # JSON出力
    with st.expander("📄 判定結果 JSON（連携用）", expanded=False):
        report = {
            "check_date": date.today().isoformat(),
            "patient_info": {
                "age":    st.session_state["patient_age"],
                "weight": f"{st.session_state['patient_weight']}kg",
            },
            "results": results,
            "summary": {
                "total":    len(results),
                "ok":       sum(1 for r in results if r["judgment"] == JUDGMENT_OK),
                "warning":  sum(1 for r in results if r["judgment"] == JUDGMENT_WARNING),
                "overdose": sum(1 for r in results if r["judgment"] == JUDGMENT_OVERDOSE),
                "underdose":sum(1 for r in results if r["judgment"] == JUDGMENT_UNDERDOSE),
            }
        }
        st.json(report)
        st.download_button(
            "💾 JSONをダウンロード",
            data=json.dumps(report, ensure_ascii=False, indent=2),
            file_name=f"dosage_check_{date.today().isoformat()}.json",
            mime="application/json",
            use_container_width=True,
        )

# ── フッター ─────────────────────────────────────────────
st.markdown("""
<div class="footer-note">
  💊 小児粉薬チェッカー — Prototype v1.0<br>
  本システムの判定結果は参考情報です。最終判断は必ず薬剤師が行ってください。<br>
  薬剤マスター: 管理薬剤師.com（小児薬用量一覧表）参照
</div>
""", unsafe_allow_html=True)
