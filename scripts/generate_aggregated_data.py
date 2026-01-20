"""
Generate aggregated WhatsApp activity data for the static dashboard.

This script reads the raw `w.csv` export (ignored from git for privacy reasons),
computes the aggregates required by the front-end visualizations and writes them
to `data/whatsapp-aggregated.json`, which can be safely deployed.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT_DIR / "w.csv"
OUTPUT_PATH = ROOT_DIR / "data" / "whatsapp-aggregated.json"

DATE_REGEX = re.compile(r"^\d{2}-\d{2}-\d{2}$")


def parse_row(row: dict[str, str]) -> dict[str, object] | None:
    """Validate and parse a CSV row into the fields required downstream."""
    date_str = (row.get("date (YYYY-MM-DD)") or "").strip()
    time_str = (row.get("time (hh:mm)") or "").strip()

    if not date_str or not DATE_REGEX.match(date_str):
        return None

    try:
        date = datetime.strptime(date_str, "%y-%m-%d")
    except ValueError:
        return None

    hour_str = time_str.split(":")[0] if ":" in time_str else None
    try:
        hour = int(hour_str)
    except (TypeError, ValueError):
        return None

    name = (row.get("name") or "").strip()

    return {
        "date": date,
        "hour": hour,
        "day_mon": date.weekday(),  # Monday = 0
        "year_month": date.strftime("%Y-%m"),
        "name": name or "Desconhecido",
    }


def build_aggregates(parsed_rows: list[dict[str, object]]) -> dict[str, object]:
    total_messages = len(parsed_rows)
    if total_messages == 0:
        raise ValueError("Nenhuma mensagem válida encontrada em w.csv")

    hours_counter = Counter()
    daily_counter = Counter()
    monthly_counter = Counter()
    heatmap_counter = Counter()
    contributor_counter = Counter()
    day_set = set()

    min_date = parsed_rows[0]["date"]
    max_date = parsed_rows[0]["date"]

    for entry in parsed_rows:
        date = entry["date"]
        hour = entry["hour"]
        day_mon = entry["day_mon"]
        year_month = entry["year_month"]
        name = entry["name"]

        hours_counter[hour] += 1
        daily_counter[day_mon] += 1
        monthly_counter[year_month] += 1
        heatmap_counter[(day_mon, hour)] += 1
        contributor_counter[name] += 1
        day_set.add(date.strftime("%Y-%m-%d"))

        if date < min_date:
            min_date = date
        if date > max_date:
            max_date = date

    active_days = len(day_set)
    days_span = (max_date - min_date).days

    stats = {
        "totalMessages": total_messages,
        "uniqueParticipants": len(contributor_counter),
        "daysSpan": days_span,
        "activeDays": active_days,
        "avgPerDay": round(total_messages / active_days, 1) if active_days else 0.0,
    }

    hourly = [{"hour": hour, "count": hours_counter.get(hour, 0)} for hour in range(24)]

    daily = [{"day": day, "count": daily_counter.get(day, 0)} for day in range(7)]

    monthly = [
        {"month": month, "count": monthly_counter[month]}
        for month in sorted(monthly_counter.keys())
    ]

    heatmap = [
        {"day": day, "hour": hour, "count": heatmap_counter.get((day, hour), 0)}
        for day in range(7)
        for hour in range(24)
    ]

    contributors = [
        {"name": name, "count": count}
        for name, count in contributor_counter.most_common()
    ]

    return {
        "generatedAt": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "stats": stats,
        "hourly": hourly,
        "daily": daily,
        "monthly": monthly,
        "heatmap": heatmap,
        "contributors": contributors,
    }


def main() -> None:
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Ficheiro {CSV_PATH} não encontrado. Exportar o chat WhatsApp como w.csv."
        )

    parsed_rows: list[dict[str, object]] = []

    with CSV_PATH.open(encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            parsed = parse_row(row)
            if parsed:
                parsed_rows.append(parsed)

    aggregates = build_aggregates(parsed_rows)
    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as fp:
        json.dump(aggregates, fp, ensure_ascii=False, indent=2)

    print(
        f"✅ Dados agregados gerados em {OUTPUT_PATH} ({aggregates['stats']['totalMessages']} mensagens)"
    )


if __name__ == "__main__":
    main()
