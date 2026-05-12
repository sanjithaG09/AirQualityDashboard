# 🌍 Air Quality Monitoring Dashboard
**Real-Time Air Quality Insights, Visualized**

Monitor live pollution levels, track trends, and explore air quality data across cities — all in one clean, interactive dashboard.

---

**Features • How It Works • Tech Stack • Project Structure • Getting Started**

---

## 📖 Overview

The **Air Quality Monitoring Dashboard** is a real-time interactive web application built with Python and Streamlit. It fetches live pollutant data from the **OpenAQ API** and presents it in a clean, visual, and easy-to-understand format.

The dashboard supports address-based geocoding to locate nearby monitoring stations, displays the latest readings for key pollutants, and plots daily air quality trends over a user-selected date range using interactive charts — giving you a clear picture of the air you breathe.

---

## ✨ Features

| Capability | Description |
|---|---|
| Live Data Fetching | Pulls real-time pollutant data from the OpenAQ API |
| Address-Based Geocoding | Locates nearby monitoring stations using an entered address |
| Multi-Pollutant Support | Tracks PM2.5, PM10, CO, NO₂, SO₂, and O₃ |
| Date Range Selection | Plot daily air quality trends over a custom date range |
| Interactive Charts | Visualizations built with Plotly for an engaging experience |
| City & Pollutant Selector | Streamlit widgets let users filter by city and pollutant |

---

## 🔄 How It Works

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   OpenAQ API    │────▶│  Python Backend  │────▶│   Streamlit UI  │
│  (Live Data)    │     │  Pandas + Geopy  │     │  (Dashboard)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                │
                                ▼
                        ┌──────────────┐
                        │    Plotly    │
                        │   (Charts)   │
                        └──────────────┘
```

**End-to-End Flow**

1. User enters an address or city in the dashboard
2. **Geopy** geocodes the address to coordinates
3. App sends API requests to **OpenAQ** to fetch nearby station data
4. Data is cleaned and aggregated using **Pandas**
5. Streamlit widgets let users select pollutants and date ranges
6. **Plotly** renders interactive trend charts and current readings

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Web app framework and UI |
| OpenAQ API | Live air quality data source |
| Pandas | Data cleaning and aggregation |
| Plotly | Interactive charts and visualizations |
| Geopy | Address-based geocoding |

---

## 📁 Project Structure

```
AIR_QUALITY/
├── streamlit_app.py        # Main app entry point
├── requirements.txt        # Python dependencies
├── notebooks/              # Exploratory data analysis
├── .devcontainer/
│   └── devcontainer.json   # Dev container configuration
├── secrets.json            # API keys (gitignored)
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python ≥ 3.9
- pip
- OpenAQ API Key (free at [openaq.org](https://openaq.org))

### 1. Clone the Repository

```bash
git clone https://github.com/sanjithaG09/AirQualityDashboard.git
cd AirQualityDashboard
```

### 2. Set Up Environment

Create a `secrets.json` file in the project root:

```json
{
  "OPENAQ_API_KEY": "your_openaq_api_key_here"
}
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
streamlit run streamlit_app.py
```

The dashboard will open at `http://localhost:8501`.

---

## 📝 Notes

- Data availability depends on nearby monitoring stations — some cities may have limited or delayed readings
- Date range trends require historical data to be available for the selected station and pollutant
- Geocoding accuracy depends on the specificity of the entered address

---

*Built to make air quality data accessible and understandable.*
