# WhatsApp Group Analysis - Cedros

Interactive D3.js visualization and data analysis of WhatsApp group chat patterns.

## Features

- **Activity Heatmap**: Hour × Day of week visualization
- **Temporal Analysis**: Hourly, daily, and monthly activity patterns
- **Participant Rankings**: All 40 group members ranked by activity
- **Interactive Charts**: Hover tooltips with detailed statistics

## Screenshots

![Dashboard Preview](docs/preview.png)

## Getting Started

### Prerequisites

- Python 3.x (for local server)
- Modern web browser
- WhatsApp chat export (CSV format)

### Running Locally

1. Clone the repository:
```bash
git clone https://github.com/AlexandreXavier/analysis-whatsapp.git
cd analysis-whatsapp
```

2. Place your WhatsApp CSV export as `../w.csv` (parent directory)

3. Start a local server:
```bash
python -m http.server 8000
```

4. Open in browser: `http://localhost:8000/activity-visualization.html`

## Data Format

The expected CSV format:
```csv
date (YYYY-MM-DD),time (hh:mm),name,text
22-02-18,20:22,John Doe,"Hello everyone!",
```

## Files

- `activity-visualization.html` - Main D3.js interactive dashboard
- `whatsapp_analysis.ipynb` - Jupyter notebook with Python analysis
- `CLAUDE.md` - Development guidance for AI assistants

## Key Findings

- **9,470 messages** from **40 participants** over ~4 years
- **Peak activity**: Lunch time (13:00) and Tuesdays
- **Top 10 contributors** account for ~70% of messages
- Group culture: Birthday celebrations ("parabéns") and warm greetings ("abraço")

## Technologies

- D3.js v7 for visualizations
- Pandas for data analysis
- Vanilla JavaScript (no frameworks)

## Privacy

This project is designed for personal use. The `.gitignore` excludes:
- CSV data files (contain personal messages)
- Screenshots with personal information
- Any files with phone numbers or names

## License

MIT License
