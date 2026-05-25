# my-streamlit-app

---

# 💻 Laptop Wake Insights Dashboard

A Streamlit dashboard that analyzes **Windows Event Logs** to visualize and diagnose laptop wake events (when your machine wakes from sleep/hibernate). It provides daily/weekly charts, root cause analysis, and a downloadable ledger.

---

## 📂 Project Structure

```
project/
│── app.py                # Your Streamlit script (the one you shared)
│── requirements.txt       # Python dependencies
```

---

## ⚙️ Requirements

### 1. Operating System
- **Windows only** (uses `win32evtlog` to read system event logs).
- Tested on Windows 10/11.

### 2. Python Version
- Python **3.9+** recommended.

### 3. Dependencies
Create a `requirements.txt` file with:

```
streamlit
pandas
pywin32
altair
```

---

## 🛠️ Installation & Setup

### Step 1: Install Python
Ensure Python is installed. Verify with:
```bash
python --version
```

### Step 2: Create Virtual Environment (recommended)
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Verify pywin32 Installation
`pywin32` provides `win32evtlog`. If issues occur:
```bash
pip install pywin32
```

---

## ▶️ Running the App

From the project folder:
```bash
streamlit run app.py
```

This will:
- Launch a local server.
- Open the dashboard in your default browser (usually at `http://localhost:8501`).

---

## 📊 Features

### 1. **Sidebar Controls**
- Adjust historical lookback window (7–90 days).
- Shows connection status to Windows Event Log.

### 2. **Metrics**
- **Total Logged Wakes**: Sum of wake events.
- **Daily Average**: Mean wake events per day.
- **Primary Wake Trigger**: Most frequent wake source.

### 3. **Charts**
- **Daily Wake Distribution**: Bar chart of daily wake counts.
- **Weekly Aggregated Views**: Weekly totals (last 5 weeks).
- **Global Root Cause Analysis**: Donut chart of wake reasons.

### 4. **Diagnostic Ledger**
- Tabular view of wake events with:
  - Date
  - Wake Events
  - Primary Wake Reason
- Export option: Download as CSV.

---

## 🔍 How It Works

1. **Event Log Access**  
   Uses `win32evtlog` to read the **System** log on Windows.

2. **Filtering**  
   - EventID `1` → Wake events.
   - Filters by date range (default: last 30 days).

3. **Wake Reason Extraction**  
   - Parses `StringInserts` for human‑readable sources (lid, button, keyboard, mouse, USB, network, timer).
   - Falls back to executables/drivers (`.exe`, `.sys`).
   - Maps known processes (e.g., `svchost.exe` → Background Service).

4. **Aggregation**  
   - Daily counts.
   - Weekly totals (Sunday start).
   - Top wake reason per day.

5. **Visualization**  
   - Altair charts for daily, weekly, and donut breakdowns.
   - Streamlit metrics and styled components.

---

## 🧪 Example Usage

1. Run the app:
   ```bash
   streamlit run app.py
   ```
2. In the sidebar, set **Historical Lookback (Days)** to 30.
3. View:
   - Daily wake counts (red if ≥10 wakes).
   - Weekly totals.
   - Donut chart of wake sources.
4. Scroll down to export the **CSV ledger**.

---

## ⚠️ Notes & Limitations

- Requires **Windows Event Log access** (admin privileges may be needed).
- Works only on **local machine logs** (`server='localhost'`).
- If no wake events are found, dashboard shows warnings.
- Background services may appear as executables (`svchost.exe`, `NgcIso.exe`, etc.).

---

## 📥 Exporting Data

- Click **⬇️ Export Structural Ledger (CSV)**.
- File: `laptop_wake_diagnostics.csv`.

---

## ✅ Quick Start (One‑liner)

```bash
pip install streamlit pandas pywin32 altair && streamlit run app.py
```

---
