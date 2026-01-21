# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

D3.js data visualization dashboard for analyzing WhatsApp group chat data from "A nossa turma" (Cedros school alumni group). Displays interactive charts: heatmap, word cloud, hourly/daily distributions, monthly timeline, and participant rankings.

## Architecture

```
w.csv (raw data, gitignored)
    ↓
scripts/generate_aggregated_data.py
    ↓
data/whatsapp-aggregated.json (pre-computed stats)
    ↓
activity-visualization.html (D3.js dashboard)
```

The dashboard loads pre-aggregated JSON (not raw CSV) to enable static deployment on Vercel without exposing personal data.

## Commands

### Regenerate aggregated data (after CSV changes)
```bash
python scripts/generate_aggregated_data.py
```

### Run locally
```bash
python -m http.server 8000
# Open http://localhost:8000/activity-visualization.html
```

### Deploy
Push to main branch - Vercel auto-deploys. The `vercel.json` rewrites `/` to `/activity-visualization.html`.

## Key Files

| File | Purpose |
|------|---------|
| `activity-visualization.html` | Main dashboard - all D3.js visualizations in single file |
| `scripts/generate_aggregated_data.py` | Processes raw CSV → JSON with stats, hourly/daily/monthly counts, heatmap data, contributor rankings, word frequencies |
| `data/whatsapp-aggregated.json` | Pre-computed data consumed by the dashboard |
| `whatsapp_analysis.ipynb` | Jupyter notebook for exploratory analysis |
| `w.csv` | Raw WhatsApp export (gitignored for privacy) |

## Data Format

**Raw CSV** (`w.csv`): `date (YYYY-MM-DD)`, `time (hh:mm)`, `name`, `text`
- Date format is actually `YY-MM-DD` (e.g., `22-02-18`)
- Names may be phone numbers (`+351 xxx xxx xxx`) - mapped to real names in `nameMapping` object in the HTML

**Aggregated JSON** structure:
```javascript
{
  stats: { totalMessages, uniqueParticipants, activeDays, avgPerDay },
  hourly: [{ hour, count }],      // 0-23
  daily: [{ day, count }],        // 0=Monday, 6=Sunday
  monthly: [{ month, count }],    // "YYYY-MM" format
  heatmap: [{ day, hour, count }],
  contributors: [{ name, count }],
  wordfreq: [{ word, count }]     // Top 100 words
}
```

## D3.js Patterns Used

The dashboard uses D3.js v7 with d3-cloud for word clouds. All charts follow the same pattern:

```javascript
// Portuguese locale for date formatting
const localePt = d3.timeFormatLocale({...});

// Color scales
const heatmapColors = d3.scaleSequential(d3.interpolateYlOrRd);

// Standard margin convention
const margin = { top: 20, right: 20, bottom: 40, left: 50 };

// Data join with .join() (modern D3 pattern)
g.selectAll('rect').data(data).join('rect')
  .attr('x', d => xScale(d.hour))
  .on('mouseover', (event, d) => { tooltip... });
```

## Privacy Notes

- Raw CSV and images are gitignored
- Only aggregated statistics are committed/deployed
- Phone numbers in the HTML `nameMapping` should not be committed to public repos
