# 📊 AI-Powered Sales Dashboard

> A fully **offline**, **AI-driven** RevOps dashboard built with Python & Streamlit.  
> Drop in your CRM CSV and get instant pipeline visibility — no API key required.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.18%2B-3F4F75?logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

| Section | What you get |
|---|---|
| 🔻 **Pipeline Funnel** | Visual lead progression across all CRM stages |
| 📊 **Conversion Rates** | Stage-to-stage and overall Lead → Closed Won % |
| 📈 **Revenue Trends** | Monthly & cumulative Closed Won revenue charts |
| 🤖 **AI Insights** | 8 auto-generated findings (no external API needed) |
| 🏆 **Rep Performance** | Revenue & deal-count leaderboard per sales owner |

---

## 🖼️ Preview

> Load the built-in sample data in one click to see the full dashboard instantly.

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/ai-sales-dashboard.git
cd ai-sales-dashboard
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
streamlit run app.py
```

The dashboard will open at **http://localhost:8501**.

---

## 📁 Project Structure

```
ai-sales-dashboard/
│
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
│
├── modules/
│   ├── __init__.py
│   ├── data_loader.py      # CSV ingestion & validation
│   ├── metrics.py          # KPI computation engine
│   ├── charts.py           # Plotly chart builders
│   └── ai_insights.py      # Rule-based AI insights engine
│
└── sample_data/
    └── sample_leads.csv    # Built-in demo dataset
```

---

## 📄 CSV Format

Your CSV must contain the following columns:

| Column | Type | Example |
|---|---|---|
| `lead_id` | string | `L001` |
| `company` | string | `Acme Corp` |
| `stage` | string | `Closed Won` |
| `revenue` | number | `45000` |
| `owner` | string | `Sarah` |
| `created_date` | date | `2025-09-01` |
| `close_date` | date | `2025-10-15` |

### Supported stages (in funnel order)
`Lead` → `MQL` → `SQL` → `Demo` → `Closed Won` / `Closed Lost`

---

## 🛠️ Tech Stack

- **[Streamlit](https://streamlit.io/)** — Web app framework
- **[Plotly](https://plotly.com/python/)** — Interactive charts
- **[Pandas](https://pandas.pydata.org/)** — Data processing
- **Python 3.9+**

---

## 📦 Dependencies

```
streamlit>=1.32
pandas>=2.0
plotly>=5.18
```

---

## 🤖 How the AI Insights Work

The AI engine is **fully offline** — no OpenAI key, no API calls, no cost.  
It applies a set of business rules to your actual pipeline data to surface findings like:

- Win rate benchmarking (above/below 30%)
- Average deal velocity alerts
- Best-performing rep identification
- Stage drop-off bottlenecks
- Month-over-month revenue acceleration signals

---

## 📝 License

MIT — free to use, fork, and build upon.

---

## 🙋 Contributing

Pull requests are welcome! Feel free to open an issue if you find a bug or have a feature idea.
