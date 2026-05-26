import streamlit as st
import requests
import json
import io
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from geopy.geocoders import Nominatim

try:
    from streamlit_js_eval import get_geolocation
    GEO_AVAILABLE = True
except ImportError:
    GEO_AVAILABLE = False

st.set_page_config(
    page_title="Air Quality Monitor",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Base CSS (always applied) ─────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global ── */
[data-testid="stAppViewContainer"] { background: #f8fafc; }

/* ── Alerts / warnings / info — force dark text ── */
[data-testid="stAlert"] { color: #111827 !important; }
[data-testid="stAlert"] p,
[data-testid="stAlert"] span { color: #111827 !important; }
.block-container, .stMainBlockContainer {
    max-width: 100% !important;
    padding: 1.8rem 2.5rem 4rem 2rem !important;
}
/* Ensure main area doesn't overflow right edge */
[data-testid="stMain"] > div {
    overflow-x: hidden !important;
}

/* ── Text input — no border, shadow, BLACK text + caret ── */
.stTextInput > div,
.stTextInput > div > div {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
}
.stTextInput > div > div > input {
    border-radius: 14px !important;
    border: none !important;
    outline: none !important;
    background: #ffffff !important;
    padding: 0 1.2rem !important;
    font-size: 0.97rem !important;
    color: #111827 !important;
    caret-color: #111827 !important;
    box-shadow: 0 4px 18px rgba(0,0,0,0.09) !important;
    height: 52px !important;
}
.stTextInput > div > div > input:focus {
    box-shadow: 0 4px 22px rgba(59,130,246,0.22) !important;
}
.stTextInput > div > div > input::placeholder { color: #b0b8c4 !important; }

/* ── Date input — no border ── */
[data-testid="stDateInput"] > div > div {
    background: #ffffff !important;
    border: none !important;
    border-radius: 14px !important;
    box-shadow: 0 4px 18px rgba(0,0,0,0.09) !important;
}
[data-testid="stDateInput"] input {
    background: transparent !important;
    border: none !important;
    font-size: 0.93rem !important;
    color: #111827 !important;
    caret-color: #111827 !important;
}
[data-testid="stDateInput"] > div > div:focus-within {
    box-shadow: 0 4px 22px rgba(59,130,246,0.22) !important;
}

/* ── Landing primary button (gradient) ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #3b82f6, #22c55e) !important;
    color: white !important; border: none !important;
    border-radius: 12px !important; font-weight: 600 !important;
    font-size: 1rem !important; height: 48px !important; width: 100% !important;
    transition: opacity 0.15s !important;
}
.stButton > button[kind="primary"]:hover { opacity: 0.9 !important; }

/* ── Secondary button ── */
.stButton > button[kind="secondary"] {
    background: #ffffff !important; color: #374151 !important;
    border: 1.5px solid #e5e7eb !important; border-radius: 12px !important;
    font-weight: 500 !important; height: 48px !important; width: 100% !important;
}
.stButton > button[kind="secondary"]:hover { background: #f9fafb !important; }

/* ── Hide sidebar toggle button everywhere ── */
[data-testid="collapsedControl"] { display: none !important; }

/* ── SIDEBAR (results page) ── */
section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #f0f2f5 !important;
    min-width: 260px !important; max-width: 260px !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding: 1.2rem 1rem 1rem !important;
    min-width: 260px !important;
}
/* Sidebar input — gray bg with border */
[data-testid="stSidebar"] .stTextInput > div > div > input {
    background: #f5f7fa !important;
    box-shadow: none !important;
    border: 1.5px solid #e8ecf0 !important;
    border-radius: 10px !important;
    height: 44px !important;
    color: #111827 !important;
    caret-color: #111827 !important;
    font-size: 0.9rem !important;
    padding: 0 0.9rem !important;
}
[data-testid="stSidebar"] .stTextInput > div > div > input:focus {
    border-color: #3b82f6 !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stTextInput > div > div > input::placeholder {
    color: #9ca3af !important;
}
/* Sidebar primary button — solid black */
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: #111827 !important;
    color: #ffffff !important; border: none !important;
    border-radius: 10px !important; font-weight: 600 !important;
    height: 44px !important; font-size: 0.92rem !important;
    letter-spacing: 0.01em !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    background: #1f2937 !important; opacity: 1 !important;
}
/* Sidebar secondary button */
[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    background: #f5f7fa !important; color: #374151 !important;
    border: 1px solid #e8ecf0 !important; border-radius: 10px !important;
    height: 40px !important; font-size: 0.88rem !important;
}
/* Sidebar date input */
[data-testid="stSidebar"] [data-testid="stDateInput"] > div > div {
    background: #f5f7fa !important; border: 1.5px solid #e8ecf0 !important;
    border-radius: 10px !important; box-shadow: none !important;
}
[data-testid="stSidebar"] [data-testid="stDateInput"] input {
    color: #111827 !important; caret-color: #111827 !important;
}
/* Sidebar labels */
[data-testid="stSidebar"] label {
    color: #6b7280 !important; font-size: 0.76rem !important;
    font-weight: 600 !important; text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
/* Sidebar download button */
[data-testid="stSidebar"] .stDownloadButton > button {
    background: #f5f7fa !important; color: #374151 !important;
    border: 1px solid #e8ecf0 !important; border-radius: 10px !important;
    font-size: 0.85rem !important; width: 100% !important;
}
/* Sidebar expander box (Export Data) */
[data-testid="stSidebar"] [data-testid="stExpander"] {
    border: 1.5px solid #d1d5db !important;
    border-radius: 10px !important;
    background: #f5f7fa !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary {
    color: #374151 !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary svg,
[data-testid="stSidebar"] [data-testid="stExpander"] summary p {
    color: #374151 !important;
    fill: #374151 !important;
}

/* ── Feature pill ── */
.feature-pill {
    background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 16px;
    padding: 1.2rem 0.8rem; text-align: center;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}
.fp-icon { font-size: 2rem; margin-bottom: 0.4rem; }
.fp-label { font-size: 0.82rem; color: #374151; font-weight: 600; }

/* ── Equal-height columns ── */
div[data-testid="stHorizontalBlock"] { align-items: stretch !important; }
div[data-testid="stColumn"] > div { height: 100% !important; }
div[data-testid="stColumn"] > div > div[data-testid="stVerticalBlock"] { height: 100% !important; }

/* ── Pollutant card ── */
.aq-card {
    background: #ffffff; border: 1px solid #f0f2f5; border-radius: 14px;
    padding: 1.1rem 1rem 1rem; box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    margin-bottom: 0.5rem; height: 100%; min-height: 158px;
    display: flex; flex-direction: column;
    position: relative; cursor: default;
}
/* ── Pollutant card tooltip ── */
.aq-card[data-tooltip]:hover::after {
    content: attr(data-tooltip);
    position: absolute; bottom: calc(100% + 8px); left: 50%;
    transform: translateX(-50%);
    background: #1f2937; color: #f9fafb;
    font-size: 0.78rem; line-height: 1.5;
    padding: 0.5rem 0.75rem; border-radius: 8px;
    width: 220px; white-space: normal; text-align: left;
    box-shadow: 0 4px 16px rgba(0,0,0,0.18);
    z-index: 999; pointer-events: none;
}
.aq-card[data-tooltip]:hover::before {
    content: '';
    position: absolute; bottom: calc(100% + 2px); left: 50%;
    transform: translateX(-50%);
    border: 6px solid transparent;
    border-top-color: #1f2937;
    z-index: 999; pointer-events: none;
}
.c-label { font-size: 0.82rem; font-weight: 500; color: #9ca3af; }
.c-value { font-size: 2.1rem; font-weight: 800; line-height: 1.1; color: #111827; margin: 0.45rem 0 0.15rem; }
.c-unit  { font-size: 0.78rem; color: #9ca3af; margin-bottom: 0.7rem; flex: 1; }
.c-dot   { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }

/* ── AQI pill ── */
.aqi-pill {
    display: inline-flex; align-items: center; gap: 5px;
    border-radius: 999px; padding: 0.22rem 0.85rem;
    font-weight: 700; font-size: 0.82rem;
}

/* ── AQI banner ── */
.aqi-banner {
    border-radius: 18px; padding: 1.6rem 1.8rem; border: 1.5px solid;
    display: flex; align-items: center; gap: 1.2rem; margin-bottom: 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    box-sizing: border-box; width: 100%;
}

/* ── Section header ── */
.sec-header {
    font-size: 1.15rem; font-weight: 700; color: #111827;
    margin: 1.5rem 0 0.75rem;
}

/* ── Health card ── */
.health-card {
    border-radius: 14px; padding: 1.3rem 1.2rem; border: 1px solid #f0f2f5;
    background: #ffffff; height: 100%;
}
.hc-icon-circle {
    width: 46px; height: 46px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem; margin-bottom: 0.85rem;
}
.hc-title { font-size: 1rem; font-weight: 700; color: #111827; margin-bottom: 0.55rem; }
.hc-body  { font-size: 0.85rem; line-height: 1.65; color: #6b7280; }

/* ── Stat card ── */
.stat-card {
    background: #ffffff; border: 1px solid #f0f2f5; border-radius: 14px;
    padding: 1.15rem 1rem; box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    margin-bottom: 0.75rem;
}
.sc-head {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 0.9rem; padding-bottom: 0.75rem; border-bottom: 1px solid #f5f6f8;
}
.sc-name { font-size: 0.95rem; font-weight: 600; color: #111827; }
.sc-row  { display: flex; justify-content: space-between; padding: 0.32rem 0; font-size: 0.85rem; }
.sc-key  { color: #9ca3af; display: flex; align-items: center; gap: 5px; }
.sc-val  { font-weight: 700; color: #111827; }
.sc-green { color: #16a34a !important; }
.sc-red   { color: #dc2626 !important; }
.sc-worst { margin-top: 0.65rem; padding-top: 0.65rem; border-top: 1px solid #f5f6f8; }
.sc-worst-label { font-size: 0.78rem; color: #9ca3af; margin-bottom: 0.15rem; display: flex; align-items: center; gap: 4px; }
.sc-worst-val   { font-size: 0.9rem; font-weight: 700; color: #111827; }

/* ── Det pill ── */
.det-pill {
    background: #eff6ff; border: 1px solid #bfdbfe; border-left: 3px solid #3b82f6;
    border-radius: 8px; padding: 0.5rem 0.85rem;
    font-size: 0.82rem; color: #1e40af; margin: 0.4rem 0;
}

/* ── Trend chart white cards (columns only, not the full-width bar chart) ── */
[data-testid="stColumn"] [data-testid="stPlotlyChart"] {
    background: #ffffff !important;
    border-radius: 16px !important;
    border: 1px solid #f0f2f5 !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06) !important;
    padding: 0.75rem 0.5rem 0 !important;
    margin-bottom: 0.5rem !important;
}
</style>
""", unsafe_allow_html=True)

# ── Secrets / API ─────────────────────────────────────────────────────────────
try:
    api_key = st.secrets["openaq-api-key"]
except (KeyError, FileNotFoundError):
    import json
    with open('secrets.json') as f:
        secrets = json.load(f)
    api_key = secrets['openaq-api-key']

# ── Colour / AQI helpers ──────────────────────────────────────────────────────
POLLUTANT_COLORS = {
    "pm25": "#eab308", "pm10": "#22c55e", "no2": "#f97316",
    "o3":   "#3b82f6", "co":   "#a855f7", "so2": "#ec4899",
    "no":   "#ec4899", "bc":   "#6b7280",
}

POLLUTANT_INFO = {
    "pm25":             "Fine particles ≤2.5 µm — penetrate deep into lungs and bloodstream, linked to heart and lung disease.",
    "pm10":             "Coarse particles ≤10 µm — irritate airways and can worsen asthma and bronchitis.",
    "no2":              "Nitrogen dioxide from vehicle exhaust and power plants — inflames airways and reduces lung function.",
    "o3":               "Ground-level ozone formed by sunlight reacting with pollutants — causes chest pain and airway irritation.",
    "co":               "Carbon monoxide from incomplete combustion — reduces the blood's ability to carry oxygen.",
    "so2":              "Sulfur dioxide from burning fossil fuels — irritates the respiratory system and forms acid rain.",
    "no":               "Nitric oxide from combustion — a precursor to NO₂ and ground-level ozone.",
    "nox":              "Mixed nitrogen oxides (NO + NO₂) from traffic and industry — contribute to smog and acid rain.",
    "bc":               "Black carbon (soot) from diesel engines and biomass burning — linked to heart disease and climate warming.",
    "relativehumidity": "Relative humidity — the percentage of moisture in the air; affects how pollutants disperse.",
    "temperature":      "Ambient air temperature — influences chemical reactions that form or break down pollutants.",
    "wind_speed":       "Wind speed — faster winds disperse pollutants more quickly, improving air quality.",
    "wind_direction":   "Wind direction — indicates where air masses (and any pollutants they carry) are coming from.",
}
CHART_TEMPLATE = "plotly_white"

def pollutant_color(name):
    return POLLUTANT_COLORS.get((name or "").lower(), "#3b82f6")

def hex_to_rgba(hex_color, alpha=0.15):
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

AQI_BREAKPOINTS = {
    "pm25": [(0.0,12.0,0,50),(12.1,35.4,51,100),(35.5,55.4,101,150),(55.5,150.4,151,200),(150.5,250.4,201,300),(250.5,500.4,301,500)],
    "pm10": [(0,54,0,50),(55,154,51,100),(155,254,101,150),(255,354,151,200),(355,424,201,300),(425,604,301,500)],
    "o3":   [(0,54,0,50),(55,70,51,100),(71,85,101,150),(86,105,151,200),(106,200,201,300)],
    "co":   [(0.0,4.4,0,50),(4.5,9.4,51,100),(9.5,12.4,101,150),(12.5,15.4,151,200),(15.5,30.4,201,300),(30.5,50.4,301,500)],
    "no2":  [(0,53,0,50),(54,100,51,100),(101,360,101,150),(361,649,151,200),(650,1249,201,300),(1250,2049,301,500)],
    "so2":  [(0,35,0,50),(36,75,51,100),(76,185,101,150),(186,304,151,200),(305,604,201,300),(605,1004,301,500)],
}
AQI_LEVELS = [
    (50,  "Good",                           "#166534", "#f0fdf4", "#bbf7d0", "✅"),
    (100, "Moderate",                       "#854d0e", "#fefce8", "#fef08a", "⚠️"),
    (150, "Unhealthy for Sensitive Groups", "#9a3412", "#fff7ed", "#fed7aa", "🟠"),
    (200, "Unhealthy",                      "#991b1b", "#fef2f2", "#fecaca", "🔴"),
    (300, "Very Unhealthy",                 "#581c87", "#faf5ff", "#e9d5ff", "🟣"),
    (500, "Hazardous",                      "#7f1d1d", "#fee2e2", "#fca5a5", "☠️"),
]

# Saturated colors for pills/circles (used where pastel would blend into the bg)
AQI_SOLID = {
    "Good":                           ("#22c55e", "#ffffff"),
    "Moderate":                       ("#ca8a04", "#ffffff"),
    "Unhealthy for Sensitive Groups": ("#ea580c", "#ffffff"),
    "Unhealthy":                      ("#dc2626", "#ffffff"),
    "Very Unhealthy":                 ("#9333ea", "#ffffff"),
    "Hazardous":                      ("#7f1d1d", "#ffffff"),
}

def aqi_level(aqi_val):
    if aqi_val is None:
        return None
    for (cap, label, tc, bg, bc, icon) in AQI_LEVELS:
        if aqi_val <= cap:
            color, toc = AQI_SOLID.get(label, ("#6b7280", "#ffffff"))
            return {"label": label, "tc": tc, "bg": bg, "bc": bc, "icon": icon,
                    "color": color, "toc": toc}
    color, toc = AQI_SOLID.get("Hazardous", ("#7f1d1d", "#ffffff"))
    return {"label": "Hazardous", "tc": "#7f1d1d", "bg": "#fee2e2", "bc": "#fca5a5",
            "icon": "☠️", "color": color, "toc": toc}

def calc_aqi(value, pollutant):
    key = (pollutant or "").lower()
    bps = AQI_BREAKPOINTS.get(key)
    if not bps or value is None:
        return None
    for (c_lo, c_hi, aqi_lo, aqi_hi) in bps:
        if c_lo <= value <= c_hi:
            return round(((aqi_hi - aqi_lo) / (c_hi - c_lo)) * (value - c_lo) + aqi_lo)
    return None

HEALTH = {
    "Good": (
        "Air quality is ideal. Enjoy outdoor jogging, cycling, or sports freely.",
        "No restrictions for sensitive individuals. Normal outdoor exposure is safe.",
        "Open windows and doors to let fresh air circulate through your home.",
        "Great conditions for outdoor children's play and elderly walks.",
    ),
    "Moderate": (
        "Limit intense outdoor exercise if you notice any throat or eye irritation.",
        "People with asthma or allergies should carry their inhaler when going out.",
        "Ventilate your home in the morning; close windows during afternoon traffic peaks.",
        "Children with respiratory conditions should limit prolonged outdoor play.",
    ),
    "Unhealthy for Sensitive Groups": (
        "Avoid outdoor jogging or heavy exertion — switch to indoor workouts today.",
        "Heart and lung patients should stay indoors and keep medication accessible.",
        "Close windows, use an air purifier, and avoid cooking with open flames indoors.",
        "Keep children and elderly indoors; short supervised outdoor time only.",
    ),
    "Unhealthy": (
        "Everyone should avoid prolonged outdoor activity, even light walking.",
        "Wear an N95 mask if you must go outside. Limit trips to essentials only.",
        "Run HEPA air purifiers on high. Seal gaps under doors and around windows.",
        "Elderly, pregnant women, and children should remain indoors throughout the day.",
    ),
    "Very Unhealthy": (
        "Stay indoors — all outdoor physical activity should be cancelled.",
        "Wear an N95/P100 respirator if outdoor exposure is unavoidable.",
        "Create a clean-air room: run air purifiers, seal vents, and minimise indoor pollution sources.",
        "Monitor for symptoms (coughing, chest tightness, dizziness) and seek medical help if they appear.",
    ),
    "Hazardous": (
        "Health emergency — do not go outside under any circumstances.",
        "Seek immediate medical attention if experiencing breathing difficulty or chest pain.",
        "Seal all windows and doors with wet towels or tape to block polluted air.",
        "Evacuate or relocate to a clean-air shelter if air purification is not available indoors.",
    ),
}

# ── API helpers ───────────────────────────────────────────────────────────────
def get_coordinates(address):
    loc = Nominatim(user_agent="air_quality_monitor").geocode(address)
    return (loc.latitude, loc.longitude) if loc else (None, None)

def reverse_geocode(lat, lon):
    try:
        loc = Nominatim(user_agent="air_quality_monitor").reverse(f"{lat},{lon}", language='en')
        return loc.address if loc else None
    except Exception:
        return None

def _dist_km(lat1, lon1, lat2, lon2):
    dlat = lat2 - lat1
    dlon = (lon2 - lon1) * np.cos(np.radians((lat1 + lat2) / 2))
    return 111.0 * (dlat ** 2 + dlon ** 2) ** 0.5

def _sort_by_dist(results, lat, lon):
    def key(loc):
        c = loc.get('coordinates') or {}
        return _dist_km(lat, lon, c.get('latitude', lat), c.get('longitude', lon))
    return sorted(results, key=key)

def _nearest_dist_km(results, lat, lon):
    c = (results[0].get('coordinates') or {})
    return round(_dist_km(lat, lon, c.get('latitude', lat), c.get('longitude', lon)))

def _get_country_code(lat, lon):
    try:
        loc = Nominatim(user_agent="air_quality_monitor").reverse(
            f"{lat},{lon}", language='en')
        if loc:
            return loc.raw.get('address', {}).get('country_code', '').upper()
    except Exception:
        pass
    return None

def _radius_search(lat, lon, seen_ids):
    """Stations within 5/10/25 km of (lat, lon), skipping already-seen IDs."""
    candidates = []
    for radius in [5000, 10000, 25000]:
        r = requests.get("https://api.openaq.org/v3/locations",
            headers={"X-API-Key": api_key},
            params={"coordinates": f"{lat},{lon}", "radius": radius, "limit": 50})
        if r.status_code != 200:
            continue
        for loc in r.json().get('results', []):
            if loc['id'] not in seen_ids:
                seen_ids.add(loc['id'])
                c = (loc.get('coordinates') or {})
                d = _dist_km(lat, lon, c.get('latitude', lat), c.get('longitude', lon))
                candidates.append((d, loc))
    return candidates


def find_best_station(lat, lon):
    """
    Expand radius ring by ring: 5 km → 10 km → 25 km.
    If nothing found, sweep outward in 8 directions (step = 0.5°, up to 2.5°)
    so anomalously-indexed stations like Thiruvananthapuram are discovered.
    Last resort: country-wide search sorted by distance.

    Returns (location, sensors, latest_raw, dist_km).
    """
    MIN_SENSORS = 3
    seen_ids    = set()

    # ── Phase 1: ring-by-ring at the geocoded point (up to 25 km) ────────────
    all_candidates = _radius_search(lat, lon, seen_ids)

    # ── Phase 2: directional grid sweep when Phase 1 finds nothing ───────────
    # Step 0.5° (~55 km) at a time in 8 directions; stop as soon as any hit.
    if not all_candidates:
        directions = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
        step = 0.5
        while step <= 2.5 and not all_candidates:
            for dlat, dlon in directions:
                hits = _radius_search(lat + dlat * step, lon + dlon * step, seen_ids)
                for _, loc in hits:
                    c = (loc.get('coordinates') or {})
                    d_orig = _dist_km(lat, lon, c.get('latitude', lat), c.get('longitude', lon))
                    all_candidates.append((d_orig, loc))
            step += 0.5

    # ── Phase 3: country-wide fallback ───────────────────────────────────────
    if not all_candidates:
        cc = _get_country_code(lat, lon)
        params = {"limit": 1000}
        if cc:
            params["country_id"] = cc
        r = requests.get("https://api.openaq.org/v3/locations",
            headers={"X-API-Key": api_key}, params=params)
        if r.status_code == 200:
            for loc in r.json().get('results', []):
                if loc['id'] not in seen_ids:
                    seen_ids.add(loc['id'])
                    c = (loc.get('coordinates') or {})
                    d = _dist_km(lat, lon, c.get('latitude', lat), c.get('longitude', lon))
                    all_candidates.append((d, loc))

    if not all_candidates:
        return None, [], None, None

    all_candidates.sort(key=lambda x: x[0])

    # Walk nearest-to-farthest; return first station with valid latest readings
    for dist, loc in all_candidates:
        snsr = get_sensors(loc['id'])
        if len(snsr) < MIN_SENSORS:
            continue
        latest = get_latest(loc['id'])
        if latest and latest.get('results'):
            return loc, snsr, latest, round(dist)

    # Nothing had latest readings — return nearest station regardless
    _, loc = all_candidates[0]
    return loc, get_sensors(loc['id']), get_latest(loc['id']), round(all_candidates[0][0])

def get_sensors(location_id):
    r = requests.get(f"https://api.openaq.org/v3/locations/{location_id}/sensors",
        headers={"X-API-Key": api_key})
    return r.json().get('results', []) if r.status_code == 200 else []

def get_daily_measurements(sensor_id, date_from, date_to):
    r = requests.get(f"https://api.openaq.org/v3/sensors/{sensor_id}/measurements/daily",
        headers={"X-API-Key": api_key},
        params={"datetime_from": date_from, "datetime_to": date_to, "limit": 100})
    return r.json().get('results', []) if r.status_code == 200 else []

def get_latest(location_id):
    r = requests.get(f"https://api.openaq.org/v3/locations/{location_id}/latest",
        headers={"X-API-Key": api_key})
    return r.json() if r.status_code == 200 else None

def df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def df_to_excel(frames):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as w:
        for sheet, df in frames.items():
            df = df.copy()
            for col in df.select_dtypes(include=['datetimetz']).columns:
                df[col] = df[col].dt.tz_localize(None)
            df.to_excel(w, sheet_name=sheet[:31], index=False)
    return buf.getvalue()

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [('address', ''), ('auto_locate', False), ('detected_addr', None),
             ('searched', False), ('date_from', None), ('date_to', None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Geolocation ───────────────────────────────────────────────────────────────
if GEO_AVAILABLE and st.session_state.auto_locate:
    raw = get_geolocation()
    if raw and isinstance(raw, dict) and 'coords' in raw:
        lat_g, lon_g = raw['coords']['latitude'], raw['coords']['longitude']
        addr = reverse_geocode(lat_g, lon_g)
        st.session_state.detected_addr = addr or f"{lat_g:.5f}, {lon_g:.5f}"
        st.session_state.auto_locate = False
        st.rerun()

# ═════════════════════════════════════════════════════════════════════════════
# LANDING PAGE
# ═════════════════════════════════════════════════════════════════════════════
if not st.session_state.searched:
    # Hide sidebar + set gradient bg + zero padding for landing
    st.markdown("""
    <style>
    section[data-testid="stSidebar"],
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stMain"] {
        background: linear-gradient(135deg, #dbeafe 0%, #ffffff 55%, #dcfce7 100%);
    }
    .block-container, .stMainBlockContainer {
        padding: 0 !important; max-width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

    _, center, _ = st.columns([1.4, 1.6, 1.4])
    with center:
        st.markdown("""
        <div style="text-align:center;padding:2.8rem 0 1.6rem">
            <div style="width:72px;height:72px;border-radius:50%;margin:0 auto 1.2rem;
                        background:linear-gradient(135deg,#06b6d4,#22c55e);
                        display:flex;align-items:center;justify-content:center;font-size:2rem;
                        box-shadow:0 8px 28px rgba(6,182,212,0.28)">☁️</div>
            <div style="font-size:2.4rem;font-weight:800;margin-bottom:0.4rem;
                        background:linear-gradient(90deg,#2563eb,#16a34a);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                        line-height:1.2;letter-spacing:-0.5px">Air Quality Monitor</div>
            <div style="font-size:0.97rem;color:#6b7280;line-height:1.6;margin-top:0.25rem">
                Real-time air quality data and health insights for your location
            </div>
        </div>
        """, unsafe_allow_html=True)

        center_addr = st.text_input("",
            value=st.session_state.address,
            placeholder="Enter city, address, or place...",
            label_visibility="collapsed", key='center_addr')

        st.markdown("<p style='font-size:0.75rem;font-weight:600;color:#9ca3af;letter-spacing:0.05em;text-transform:uppercase;margin:0.8rem 0 0.25rem'>Date Range</p>",
                    unsafe_allow_html=True)
        center_dates = st.date_input("", [], label_visibility="collapsed", key='c_dates')

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        if GEO_AVAILABLE:
            btn1, btn2 = st.columns([3, 2])
        else:
            btn1 = st.columns([1])[0]
            btn2 = None

        with btn1:
            if st.button("🔍  Search Location", key='c_search', use_container_width=True, type='primary'):
                if not center_addr.strip():
                    st.error("Please enter a location.")
                elif not (isinstance(center_dates, (list, tuple)) and len(center_dates) == 2):
                    st.error("Please select a date range.")
                else:
                    st.session_state.address   = center_addr.strip()
                    st.session_state.date_from = center_dates[0]
                    st.session_state.date_to   = center_dates[1]
                    st.session_state.searched  = True
                    st.rerun()

        if btn2 is not None:
            with btn2:
                if st.button("📍  Auto-detect", key='c_geo', use_container_width=True):
                    st.session_state.auto_locate = True
                    st.rerun()

        if st.session_state.detected_addr:
            short = st.session_state.detected_addr[:65] + ("…" if len(st.session_state.detected_addr) > 65 else "")
            st.markdown(f'<div class="det-pill" style="margin-top:0.6rem">📍 {short}</div>',
                        unsafe_allow_html=True)
            if st.button("✓ Use This Location", key='use_det_c', use_container_width=True):
                st.session_state.address = st.session_state.detected_addr
                st.session_state.detected_addr = None
                st.rerun()

        st.markdown("<div style='height:2.2rem'></div>", unsafe_allow_html=True)
        fp1, fp2, fp3 = st.columns(3)
        for col, icon, label in [(fp1, "🌍", "Global Coverage"),
                                  (fp2, "📊", "Real-time Data"),
                                  (fp3, "💚", "Health Insights")]:
            col.markdown(f"""
            <div class="feature-pill">
                <div class="fp-icon">{icon}</div>
                <div class="fp-label">{label}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

    st.stop()

# ═════════════════════════════════════════════════════════════════════════════
# RESULTS — sidebar + main content
# ═════════════════════════════════════════════════════════════════════════════
address   = st.session_state.address
date_from = st.session_state.date_from
date_to   = st.session_state.date_to

if not address or not date_from or not date_to:
    st.warning("Please complete your search.")
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:1.3rem">
        <div style="width:40px;height:40px;border-radius:10px;flex-shrink:0;
                    background:linear-gradient(135deg,#06b6d4,#22c55e);
                    display:flex;align-items:center;justify-content:center;font-size:1.25rem">☁️</div>
        <div>
            <div style="font-weight:700;font-size:0.97rem;color:#111827;line-height:1.2">Air Quality</div>
            <div style="font-size:0.75rem;color:#9ca3af">Dashboard</div>
        </div>
    </div>
    <div style="height:1px;background:#f0f2f5;margin-bottom:1.1rem"></div>
    """, unsafe_allow_html=True)

    # Location search
    sb_addr = st.text_input("", value=address, placeholder="Search location…",
                             label_visibility="collapsed", key="sb_addr")
    if st.button("Update Location", key="sb_update", type="primary", use_container_width=True):
        if sb_addr.strip():
            st.session_state.address = sb_addr.strip()
            st.session_state.searched = True
            st.rerun()

    if GEO_AVAILABLE:
        if st.button("📍 Auto-detect", key="sb_geo", use_container_width=True):
            st.session_state.auto_locate = True
            st.rerun()
    if st.session_state.detected_addr:
        short = st.session_state.detected_addr[:50] + "…"
        st.markdown(f'<div class="det-pill">📍 {short}</div>', unsafe_allow_html=True)
        if st.button("✓ Use Detected", key="sb_use_det"):
            st.session_state.address = st.session_state.detected_addr
            st.session_state.detected_addr = None
            st.rerun()

    st.markdown("<div style='height:1px;background:#f0f2f5;margin:1rem 0'></div>", unsafe_allow_html=True)

    # Date range
    st.markdown("<p style='font-size:0.75rem;font-weight:600;color:#9ca3af;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:0.3rem'>Date Range</p>",
                unsafe_allow_html=True)
    sb_dates = st.date_input("", [date_from, date_to], label_visibility="collapsed", key="sb_dates")

    # Apply date change
    if isinstance(sb_dates, (list, tuple)) and len(sb_dates) == 2:
        if sb_dates[0] != date_from or sb_dates[1] != date_to:
            st.session_state.date_from = sb_dates[0]
            st.session_state.date_to   = sb_dates[1]

    st.markdown("<div style='height:1px;background:#f0f2f5;margin:1rem 0'></div>", unsafe_allow_html=True)

    # Export placeholder — filled by a second sidebar block after data loads
    st.markdown('<div id="sb-export-anchor"></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1px;background:#f0f2f5;margin:1rem 0'></div>", unsafe_allow_html=True)

    # Current location + status boxes
    short_addr = address.split(',')[0].strip()
    st.markdown(f"""
    <div style="background:#f8fafc;border:1px solid #f0f2f5;border-radius:12px;
                padding:0.85rem 1rem;margin-bottom:0.6rem">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.25rem">
            <span style="font-size:1rem">📍</span>
            <span style="font-size:0.72rem;color:#9ca3af;font-weight:600;text-transform:uppercase;letter-spacing:0.04em">Current Location</span>
        </div>
        <div style="font-size:0.95rem;font-weight:700;color:#111827;padding-left:1.5rem">{short_addr}</div>
    </div>
    <div style="background:#f0fdf4;border:1px solid #86efac;border-radius:12px;padding:0.85rem 1rem">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.25rem">
            <span style="font-size:1rem">📈</span>
            <span style="font-size:0.72rem;color:#6b7280;font-weight:600;text-transform:uppercase;letter-spacing:0.04em">Data Status</span>
        </div>
        <div style="font-size:0.95rem;font-weight:700;color:#15803d;padding-left:1.5rem">🟢 Live Updates</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size:0.72rem;color:#c4c9d4;text-align:center;margin-top:1.2rem'>Data updated every hour · OpenAQ</div>",
                unsafe_allow_html=True)

    if st.button("↩ New Search", key="sb_reset"):
        st.session_state.searched = False
        st.session_state.address  = ''
        st.rerun()

# ═════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═════════════════════════════════════════════════════════════════════════════
with st.spinner("Resolving location…"):
    lat, lon = get_coordinates(address)

if lat is None:
    st.error("Location not found. Try a different address.")
    st.stop()

fallback_lat, fallback_lon = lat, lon

with st.spinner("Searching for nearest station with data…"):
    location, sensors, latest_raw, found_radius_km = find_best_station(lat, lon)

if location is None:
    st.error(
        f"No air quality monitoring stations found near **{address}**. "
        "OpenAQ's network covers major cities — try a specific city name."
    )
    st.stop()

location_id   = location['id']
location_name = location.get('name', f"Station {location_id}")
sensor_id_to_param = {s['id']: s['parameter'] for s in sensors}

# Dashboard title
short_addr = address.split(',')[0].strip()
loc_city   = location.get('locality') or location.get('city') or ''
loc_country= location.get('country', {}).get('name', '') if isinstance(location.get('country'), dict) else ''
station_place = ", ".join(p for p in [loc_city, loc_country] if p) or location_name

used_fallback = (fallback_lat != lat or fallback_lon != lon)
fallback_note = (f' <span style="color:#f97316;font-size:0.8rem">'
                 f'(no stations near "{short_addr}" — showing capital city data)</span>'
                 if used_fallback else "")

st.markdown(f"""
<h1 style="font-size:2rem;font-weight:800;color:#111827;margin-bottom:0.3rem;margin-top:0.5rem">
    Air Quality Dashboard
</h1>
<p style="color:#9ca3af;font-size:0.88rem;margin-bottom:0.4rem">
    Searched: <strong style="color:#374151">{short_addr}</strong>
    &nbsp;·&nbsp; Geocoded to: <strong style="color:#374151">{fallback_lat:.4f}°N, {fallback_lon:.4f}°E</strong>
    {fallback_note}
</p>
<p style="color:#9ca3af;font-size:0.88rem;margin-bottom:1rem">
    Station: <strong style="color:#374151">{location_name}</strong>
    &nbsp;({station_place})&nbsp;·&nbsp; {found_radius_km} km away &nbsp;·&nbsp; {date_from} → {date_to}
</p>
""", unsafe_allow_html=True)

# ── Far-station / stale-data warning ─────────────────────────────────────────
from datetime import datetime, timezone as _tz
_station_dt_last = location.get('datetimeLast', {})
_dt_last_str = _station_dt_last.get('utc', '') if isinstance(_station_dt_last, dict) else ''
_data_age_days = None
if _dt_last_str:
    try:
        _data_age_days = (datetime.now(_tz.utc) -
                          datetime.fromisoformat(_dt_last_str.replace('Z', '+00:00'))).days
    except Exception:
        pass

if isinstance(found_radius_km, (int, float)) and found_radius_km > 100:
    st.warning(
        f"No OpenAQ monitoring stations were found near **{short_addr}**. "
        f"The nearest station is **{location_name}** in **{station_place}**, "
        f"which is **{found_radius_km} km away**. Data shown is for that location, not {short_addr}."
    )
elif _data_age_days is not None and _data_age_days > 60:
    st.warning(
        f"The nearest station (**{location_name}**) has not reported data in **{_data_age_days} days**. "
        "Readings shown may be outdated."
    )

# ── Build latest dataframe ────────────────────────────────────────────────────
df_latest   = pd.DataFrame()
worst_label = None
worst_aqi   = None

if latest_raw and latest_raw.get('results'):
    df_latest = pd.json_normalize(latest_raw['results'])
    df_latest['parameter_obj'] = df_latest['sensorsId'].map(sensor_id_to_param)
    df_latest['parameter'] = df_latest['parameter_obj'].apply(
        lambda x: x['displayName'] if isinstance(x, dict) else None)
    df_latest['param_key'] = df_latest['parameter_obj'].apply(
        lambda x: x['name'] if isinstance(x, dict) else None)
    df_latest['unit'] = df_latest['parameter_obj'].apply(
        lambda x: x.get('units', '') if isinstance(x, dict) else '')
    df_latest = df_latest[['parameter', 'param_key', 'value', 'unit']].dropna(subset=['parameter', 'value'])
    # Average across multiple sensors reporting the same pollutant
    df_latest = (df_latest
                 .groupby(['parameter', 'param_key', 'unit'], as_index=False)['value']
                 .mean())
    df_latest['aqi'] = df_latest.apply(lambda r: calc_aqi(r['value'], r['param_key']), axis=1)

    df_aqi = df_latest.dropna(subset=['aqi'])
    if not df_aqi.empty:
        idx         = df_aqi['aqi'].idxmax()
        worst_aqi   = int(df_aqi.loc[idx, 'aqi'])
        worst_label = df_aqi.loc[idx, 'parameter']
        worst_level = aqi_level(worst_aqi)

# ── Section A: Overall AQI Banner ─────────────────────────────────────────────
if worst_aqi is not None:
    lv           = worst_level
    lv_label     = lv['label']
    health_general = HEALTH.get(lv_label, ("", "", ""))[0]
    st.markdown(f"""
    <div class="aqi-banner" style="background:{lv['bg']};border-color:{lv['bc']}">
        <div style="width:62px;height:62px;border-radius:50%;background:{lv['color']};flex-shrink:0;
                    display:flex;align-items:center;justify-content:center;font-size:1.8rem">{lv['icon']}</div>
        <div style="flex:1">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:9px">
                <span style="font-size:1.2rem;font-weight:700;color:{lv['tc']}">Overall Air Quality</span>
                <span class="aqi-pill" style="background:{lv['color']};color:{lv['toc']};font-size:0.92rem;padding:0.3rem 1rem">{worst_aqi} · {lv_label}</span>
            </div>
            <div style="font-size:0.93rem;line-height:1.6;color:{lv['tc']};margin-bottom:7px">{health_general}</div>
            <div style="font-size:0.83rem;color:#6b7280">Primary pollutant: <strong style="color:{lv['tc']}">{worst_label}</strong></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Section B: Health Recommendations ────────────────────────────────────────
if worst_aqi is not None:
    lv_label = aqi_level(worst_aqi)['label'] if aqi_level(worst_aqi) else "Good"
    tips     = HEALTH.get(lv_label, ("", "", "", ""))

    st.markdown('<div class="sec-header">Health Recommendations</div>', unsafe_allow_html=True)
    cards = [
        ("🏃", "Outdoor Activity",     "#dbeafe", tips[0]),
        ("❤️", "Sensitive Groups",     "#fee2e2", tips[1]),
        ("🏠", "Indoor Air Quality",   "#dcfce7", tips[2]),
        ("👶", "Children & Elderly",   "#fef9c3", tips[3]),
    ]
    row1, row2 = st.columns(2), st.columns(2)
    for (col, (icon, title, icon_bg, body)) in zip(row1 + row2, cards):
        col.markdown(f"""
        <div class="health-card">
            <div class="hc-icon-circle" style="background:{icon_bg}">{icon}</div>
            <div class="hc-title">{title}</div>
            <div class="hc-body">{body}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Section C: Latest Readings (pollutant cards) ──────────────────────────────
st.markdown('<div class="sec-header">Latest Readings</div>', unsafe_allow_html=True)

if not df_latest.empty:
    for row_df in [df_latest.iloc[i:i + 3] for i in range(0, len(df_latest), 3)]:
        cols = st.columns(3)
        for col, (_, r) in zip(cols, row_df.iterrows()):
            color = pollutant_color(r['param_key'])
            aqi_v = r['aqi']
            badge = ""
            if pd.notna(aqi_v):
                lv = aqi_level(int(aqi_v))
                if lv:
                    badge = f'<span class="aqi-pill" style="background:{lv["color"]};color:{lv["toc"]}">{int(aqi_v)} · {lv["label"]}</span>'
            tooltip = POLLUTANT_INFO.get((r['param_key'] or '').lower(), '')
            col.markdown(f"""
            <div class="aq-card" data-tooltip="{tooltip}">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <span class="c-label">{r['parameter']}</span>
                    <span class="c-dot" style="background:{color}"></span>
                </div>
                <div class="c-value">{r['value']:.1f}</div>
                <div class="c-unit">{r['unit']}</div>
                {badge}
            </div>
            """, unsafe_allow_html=True)
else:
    st.warning("No live readings available for this station.")

# ── Section D: Current Pollutant Levels (bar chart) ──────────────────────────
if not df_latest.empty:
    st.markdown('<div class="sec-header">Current Pollutant Levels</div>', unsafe_allow_html=True)
    df_bar = df_latest.dropna(subset=['aqi'])
    fig_bar = go.Figure(go.Bar(
        x=df_bar['parameter'], y=df_bar['aqi'],
        marker=dict(color=[('#22c55e' if v <= 50 else
                            '#eab308' if v <= 100 else
                            '#f97316' if v <= 150 else
                            '#ef4444' if v <= 200 else
                            '#a855f7' if v <= 300 else '#7f1d1d')
                           for v in df_bar['aqi']]),
        text=[str(int(v)) for v in df_bar['aqi']],
        textposition='outside',
        hovertemplate="<b>%{x}</b><br>AQI: %{y:.0f}<extra></extra>",
        marker_cornerradius=6,
    ))
    fig_bar.update_layout(
        template=CHART_TEMPLATE,
        paper_bgcolor="#ffffff", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="#f3f4f6", showline=False, tickfont=dict(size=11, color='#374151')),
        yaxis=dict(gridcolor="#f3f4f6", title=dict(text="AQI", font=dict(color='#374151')),
                   showline=False, tickfont=dict(color='#374151')),
        margin=dict(t=20, b=10, l=0, r=0), showlegend=False, height=300,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("""
    <div style="display:flex;flex-wrap:wrap;gap:0.6rem 1.2rem;padding:0.75rem 1rem;
                background:#f8fafc;border-radius:10px;border:1px solid #f0f2f5;margin-top:-0.5rem">
        <span style="font-size:0.72rem;font-weight:600;color:#9ca3af;text-transform:uppercase;
                     letter-spacing:0.05em;align-self:center;margin-right:0.4rem">AQI Scale</span>
        <span style="display:flex;align-items:center;gap:5px;font-size:0.8rem;color:#374151">
            <span style="width:11px;height:11px;border-radius:50%;background:#22c55e;display:inline-block"></span>Good (0–50)
        </span>
        <span style="display:flex;align-items:center;gap:5px;font-size:0.8rem;color:#374151">
            <span style="width:11px;height:11px;border-radius:50%;background:#eab308;display:inline-block"></span>Moderate (51–100)
        </span>
        <span style="display:flex;align-items:center;gap:5px;font-size:0.8rem;color:#374151">
            <span style="width:11px;height:11px;border-radius:50%;background:#f97316;display:inline-block"></span>Unhealthy for Sensitive (101–150)
        </span>
        <span style="display:flex;align-items:center;gap:5px;font-size:0.8rem;color:#374151">
            <span style="width:11px;height:11px;border-radius:50%;background:#ef4444;display:inline-block"></span>Unhealthy (151–200)
        </span>
        <span style="display:flex;align-items:center;gap:5px;font-size:0.8rem;color:#374151">
            <span style="width:11px;height:11px;border-radius:50%;background:#a855f7;display:inline-block"></span>Very Unhealthy (201–300)
        </span>
        <span style="display:flex;align-items:center;gap:5px;font-size:0.8rem;color:#374151">
            <span style="width:11px;height:11px;border-radius:50%;background:#7f1d1d;display:inline-block"></span>Hazardous (300+)
        </span>
    </div>
    """, unsafe_allow_html=True)

# ── Section E: Daily Trends + Summary Stats ───────────────────────────────────
# US EPA standard thresholds
thresholds = {"pm25": 35.4, "pm10": 154.0, "o3": 70.0,
              "no2": 100.0, "co": 9.4,      "so2": 75.0}

chart_data    = []
all_daily_dfs = []

for sensor in sensors:
    sensor_id    = sensor['id']
    param_info   = sensor.get('parameter', {})
    display_name = param_info.get('displayName', str(sensor_id)) if isinstance(param_info, dict) else str(param_info)
    param_key    = param_info.get('name', '')   if isinstance(param_info, dict) else ''
    unit         = param_info.get('units', '')  if isinstance(param_info, dict) else ''

    results = get_daily_measurements(sensor_id, date_from.isoformat(), date_to.isoformat())
    if not results:
        continue
    df_d = pd.json_normalize(results)
    df_d['utc']   = pd.to_datetime(df_d['period.datetimeFrom.utc'])
    df_d['value'] = pd.to_numeric(df_d['value'], errors='coerce')
    df_d.dropna(subset=['utc', 'value'], inplace=True)
    if df_d.empty:
        continue

    chart_data.append((display_name, param_key, unit, df_d))
    edf = df_d[['utc', 'value']].copy()
    edf.columns = ['date', 'value']
    edf['pollutant'] = display_name
    edf['unit']      = unit
    all_daily_dfs.append(edf)

st.markdown('<div class="sec-header">Daily Trends (Last Selected Period)</div>', unsafe_allow_html=True)

if not chart_data:
    st.info("No daily trend data for the selected date range. Try selecting a wider range (at least 3–7 days).")

if chart_data:
    # Trend charts (2-column grid)
    for i in range(0, len(chart_data), 2):
        cols = st.columns(2)
        for col, (display_name, param_key, unit, df_d) in zip(cols, chart_data[i:i + 2]):
            color     = pollutant_color(param_key)
            threshold = thresholds.get(param_key.lower())
            df_d      = df_d.sort_values('utc').copy()
            df_d['rolling7'] = df_d['value'].rolling(7, min_periods=1).mean()
            exceeded  = df_d[df_d['value'] > threshold] if threshold is not None else pd.DataFrame()
            normal    = df_d[df_d['value'] <= threshold] if threshold is not None else df_d

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_d['utc'], y=df_d['value'], mode='lines',
                line=dict(color=color, width=2.5),
                fill='tozeroy', fillcolor=hex_to_rgba(color, 0.1),
                showlegend=True, name='Daily Value',
                hovertemplate=f"<b>{display_name}</b><br>%{{x|%b %d}}: %{{y:.2f}} {unit}<extra></extra>",
            ))
            if not exceeded.empty:
                fig.add_trace(go.Scatter(
                    x=exceeded['utc'], y=exceeded['value'], mode='markers',
                    marker=dict(size=9, color='#ef4444', line=dict(color='white', width=2)),
                    name='Exceeded', showlegend=True,
                    hovertemplate=f"<b>⚠️ Exceeded</b><br>%{{x|%b %d}}: %{{y:.2f}} {unit}<extra></extra>",
                ))
            fig.add_trace(go.Scatter(
                x=df_d['utc'], y=df_d['rolling7'], mode='lines',
                line=dict(color='#eab308', width=1.8, dash='dot'),
                name='7-day Average', showlegend=True,
                hovertemplate=f"7-day avg: %{{y:.2f}} {unit}<extra></extra>",
            ))
            if threshold is not None:
                fig.add_hline(y=threshold,
                    line=dict(color='#ef4444', width=1.5, dash='dash'),
                    annotation_text="Threshold",
                    annotation_position="top right",
                    annotation_font=dict(color='#ef4444', size=10))

            n_exc = len(exceeded)
            fig.update_layout(
                template=CHART_TEMPLATE,
                title=dict(text=f"<b>{display_name} Trend</b>",
                           font=dict(size=13, color='#111827'), x=0),
                paper_bgcolor="#ffffff", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(gridcolor="#f3f4f6", showline=False, tickformat="%m-%d",
                           tickfont=dict(size=10, color='#374151')),
                yaxis=dict(gridcolor="#f3f4f6", title=dict(text=unit, font=dict(color='#374151')),
                           showline=False, tickfont=dict(size=10, color='#374151')),
                margin=dict(t=45, b=5, l=5, r=5),
                legend=dict(orientation='h', y=-0.22, font=dict(size=9, color='#6b7280'),
                            bgcolor='rgba(0,0,0,0)', tracegroupgap=12),
                height=300,
            )
            if n_exc > 0:
                fig.add_annotation(
                    text=f'{n_exc} day{"s" if n_exc != 1 else ""} exceeded',
                    xref='paper', yref='paper', x=0.99, y=1.08,
                    showarrow=False, font=dict(size=10.5, color='#ef4444'),
                    xanchor='right', yanchor='middle',
                )
            col.plotly_chart(fig, use_container_width=True)

    # ── Period Summary Statistics ─────────────────────────────────────────────
    st.markdown('<div class="sec-header" style="margin-top:2.5rem">Period Summary Statistics</div>', unsafe_allow_html=True)
    stat_cols = st.columns(3)
    for i, (display_name, param_key, unit, df_d) in enumerate(chart_data):
        col       = stat_cols[i % 3]
        color     = pollutant_color(param_key)
        worst_day = df_d.loc[df_d['value'].idxmax(), 'utc'].strftime('%b %d, %Y')
        avg_v     = df_d['value'].mean()
        min_v     = df_d['value'].min()
        max_v     = df_d['value'].max()
        col.markdown(f"""
        <div class="stat-card">
            <div class="sc-head">
                <span class="sc-name">{display_name}</span>
                <span style="width:10px;height:10px;border-radius:50%;background:{color};display:inline-block"></span>
            </div>
            <div class="sc-row">
                <span class="sc-key">Average</span>
                <span class="sc-val">{avg_v:.1f} {unit}</span>
            </div>
            <div class="sc-row">
                <span class="sc-key">↘ Min</span>
                <span class="sc-val sc-green">{min_v:.1f} {unit}</span>
            </div>
            <div class="sc-row">
                <span class="sc-key">↗ Max</span>
                <span class="sc-val sc-red">{max_v:.1f} {unit}</span>
            </div>
            <div class="sc-worst">
                <div class="sc-worst-label">📅 Worst Day</div>
                <div class="sc-worst-val">{worst_day}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Download Data ────────────────────────────────────────────────────────────
combined_df = pd.concat(all_daily_dfs, ignore_index=True) if all_daily_dfs else pd.DataFrame()
cols_e = [c for c in ['parameter', 'param_key', 'value', 'unit', 'aqi'] if c in df_latest.columns]

# Persist in session state so the sidebar expander also works on subsequent reruns
if not combined_df.empty:
    st.session_state.export_daily = df_to_csv(combined_df)
if not df_latest.empty and not combined_df.empty:
    st.session_state.export_excel = df_to_excel({
        "Latest Readings": df_latest[cols_e], "Daily Trends": combined_df})
if not df_latest.empty:
    st.session_state.export_latest = df_to_csv(df_latest[cols_e])

st.markdown('<div class="sec-header" style="margin-top:2rem">Download Data</div>', unsafe_allow_html=True)
dc1, dc2, dc3 = st.columns(3)
if not df_latest.empty:
    dc1.download_button(
        "⬇ Latest Readings (CSV)", df_to_csv(df_latest[cols_e]),
        "air_quality_latest.csv", "text/csv", use_container_width=True)
if not combined_df.empty:
    dc2.download_button(
        "⬇ Daily Trends (CSV)", df_to_csv(combined_df),
        "air_quality_daily.csv", "text/csv", use_container_width=True)
if not df_latest.empty and not combined_df.empty:
    dc3.download_button(
        "⬇ All Data (Excel)",
        df_to_excel({"Latest Readings": df_latest[cols_e], "Daily Trends": combined_df}),
        "air_quality_all.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True)

# ── Sidebar export (second block — rendered after data is ready) ──────────────
with st.sidebar:
    st.markdown("<div style='height:1px;background:#f0f2f5;margin:0.5rem 0 0.8rem'></div>",
                unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.75rem;font-weight:600;color:#9ca3af;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:0.5rem'>Export Data</p>",
                unsafe_allow_html=True)
    if not df_latest.empty:
        st.download_button("⬇ Latest Readings (CSV)", df_to_csv(df_latest[cols_e]),
            "air_quality_latest.csv", "text/csv",
            use_container_width=True, key="sb2_dl_latest")
    if not combined_df.empty:
        st.download_button("⬇ Daily Trends (CSV)", df_to_csv(combined_df),
            "air_quality_daily.csv", "text/csv",
            use_container_width=True, key="sb2_dl_daily")
    if not df_latest.empty and not combined_df.empty:
        st.download_button("⬇ All Data (Excel)",
            df_to_excel({"Latest Readings": df_latest[cols_e], "Daily Trends": combined_df}),
            "air_quality_all.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True, key="sb2_dl_excel")
    if df_latest.empty and combined_df.empty:
        st.caption("No data available to export.")

