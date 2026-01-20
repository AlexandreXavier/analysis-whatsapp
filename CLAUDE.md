# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

D3.js data visualization project for analyzing WhatsApp group chat data from "A nossa turma" (Cedros school reunion group). The project uses D3.js v7 to create interactive visualizations of messaging patterns, participation, and social network dynamics.

## Data Source

- **Location**: `../w.csv` (parent directory)
- **Format**: CSV with columns: `date (YYYY-MM-DD)`, `time (hh:mm)`, `name`, `text`
- **Content**: Portuguese-language WhatsApp messages from a school reunion group
- **Size**: ~950KB, spanning from February 2022 onwards
- **Notes**:
  - Some senders identified by phone number (e.g., `+351 xxx xxx xxx`), others by name
  - Messages may contain `<Ficheiro não revelado>` for unrevealed media files
  - Text encoding: UTF-8 with Portuguese characters

## Development Setup

### Option 1: CDN (Quick Start)
```html
<script src="https://d3js.org/d3.v7.min.js"></script>
```

### Option 2: npm
```bash
npm install d3
```

### Running Locally
Use a local server to load CSV data (required for CORS):
```bash
# Python 3
python -m http.server 8000

# Node.js
npx serve
```

## D3.js Architecture Patterns

### Data Loading
```javascript
const data = await d3.csv('../w.csv', d => ({
  date: d3.timeParse('%y-%m-%d')(d['date (YYYY-MM-DD)']),
  time: d['time (hh:mm)'],
  name: d.name,
  text: d.text
}));
```

### SVG Container Setup
```javascript
const margin = {top: 20, right: 20, bottom: 30, left: 40};
const width = 800 - margin.left - margin.right;
const height = 400 - margin.top - margin.bottom;

const svg = d3.select('#chart')
  .append('svg')
  .attr('width', width + margin.left + margin.right)
  .attr('height', height + margin.top + margin.bottom)
  .append('g')
  .attr('transform', `translate(${margin.left},${margin.top})`);
```

### Data Join Pattern
```javascript
svg.selectAll('rect')
  .data(dataArray, d => d.id)  // Key function for object constancy
  .join('rect')
  .attr('x', d => xScale(d.category))
  .attr('y', d => yScale(d.value));
```

## Visualization Ideas for This Dataset

- **Message frequency over time**: Line chart showing daily/weekly/monthly activity
- **Top contributors**: Bar chart of messages per participant
- **Activity by hour/day**: Heatmap of when messages are sent
- **Social network**: Force-directed graph of who replies to whom
- **Word cloud**: Most common words/phrases (excluding stopwords)
- **Sentiment timeline**: If sentiment analysis is applied

## Reference Resources

The `../d3-visualization/` directory contains comprehensive D3.js documentation:
- `SKILL.md` - Main entry point with workflows
- `resources/getting-started.md` - Setup and prerequisites
- `resources/scales-axes.md` - Data transformation
- `resources/selections-datajoins.md` - DOM manipulation
- `resources/workflows.md` - Step-by-step chart guides
- `resources/common-patterns.md` - Reusable templates
