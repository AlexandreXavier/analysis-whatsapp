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
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

# Portuguese stopwords - common words to exclude from word cloud
PORTUGUESE_STOPWORDS = {
    # Articles
    "o", "a", "os", "as", "um", "uma", "uns", "umas",
    # Prepositions
    "de", "da", "do", "das", "dos", "em", "na", "no", "nas", "nos",
    "por", "para", "com", "sem", "sob", "sobre", "entre", "até",
    "desde", "durante", "perante", "após", "ante",
    # Contractions
    "ao", "aos", "à", "às", "pelo", "pela", "pelos", "pelas",
    "num", "numa", "nuns", "numas", "dum", "duma", "duns", "dumas",
    "neste", "nesta", "nestes", "nestas", "nesse", "nessa", "nesses", "nessas",
    "naquele", "naquela", "naqueles", "naquelas", "nisto", "nisso", "naquilo",
    "deste", "desta", "destes", "destas", "desse", "dessa", "desses", "dessas",
    "daquele", "daquela", "daqueles", "daquelas", "disto", "disso", "daquilo",
    # Pronouns
    "eu", "tu", "ele", "ela", "nós", "vós", "eles", "elas",
    "me", "te", "se", "lhe", "nos", "vos", "lhes",
    "meu", "minha", "meus", "minhas", "teu", "tua", "teus", "tuas",
    "seu", "sua", "seus", "suas", "nosso", "nossa", "nossos", "nossas",
    "vosso", "vossa", "vossos", "vossas",
    "este", "esta", "estes", "estas", "esse", "essa", "esses", "essas",
    "aquele", "aquela", "aqueles", "aquelas", "isto", "isso", "aquilo",
    "que", "quem", "qual", "quais", "quanto", "quanta", "quantos", "quantas",
    "onde", "como", "quando", "porque", "porquê",
    # Conjunctions
    "e", "ou", "mas", "porém", "contudo", "todavia", "entretanto",
    "porque", "pois", "como", "se", "embora", "conquanto", "quando",
    "enquanto", "logo", "portanto", "então", "assim", "nem",
    # Verbs (common forms)
    "ser", "estar", "ter", "haver", "ir", "vir", "fazer", "poder", "dever",
    "é", "são", "foi", "era", "eram", "será", "seria", "seja", "sejam",
    "está", "estão", "estava", "estavam", "esteve", "estiveram",
    "tem", "têm", "tinha", "tinham", "teve", "tiveram", "terá", "teria",
    "há", "havia", "houve", "haverá", "haveria",
    "vai", "vão", "ia", "iam", "foi", "foram", "irá", "iria",
    "vem", "vêm", "vinha", "vinham", "veio", "vieram",
    "faz", "fazem", "fazia", "faziam", "fez", "fizeram", "fará", "faria",
    "pode", "podem", "podia", "podiam", "pôde", "puderam",
    "deve", "devem", "devia", "deviam",
    # Adverbs
    "não", "sim", "já", "ainda", "sempre", "nunca", "jamais",
    "muito", "pouco", "mais", "menos", "bem", "mal",
    "aqui", "ali", "lá", "cá", "aí", "onde", "aonde",
    "hoje", "ontem", "amanhã", "agora", "depois", "antes", "logo",
    "também", "só", "apenas", "mesmo", "próprio",
    # Other common words
    "coisa", "coisas", "vez", "vezes", "dia", "dias", "ano", "anos",
    "parte", "partes", "lado", "lados", "tempo", "tempos",
    "forma", "formas", "modo", "modos", "tipo", "tipos",
    "todo", "toda", "todos", "todas", "tudo", "nada", "algo", "alguém", "ninguém",
    "cada", "outro", "outra", "outros", "outras", "algum", "alguma", "alguns", "algumas",
    "nenhum", "nenhuma", "nenhuns", "nenhumas",
    "tal", "tais", "tanto", "tanta", "tantos", "tantas",
    # Chat-specific words to filter
    "http", "https", "www", "com", "pt", "br", "org",
    "ficheiro", "não", "revelado", "media", "omitted", "image", "video", "audio",
    "mensagem", "mensagens", "apagada", "apagadas",
}

# Media marker patterns to filter
MEDIA_MARKERS = [
    "<Ficheiro não revelado>",
    "<ficheiro de multimédia oculto>",
    "<Media omitted>",
    "image omitted",
    "video omitted",
    "audio omitted",
    "sticker omitted",
    "GIF omitted",
    "document omitted",
]


def _normalize_for_stopword(word: str) -> str:
    """Remove accents for stopword matching."""
    nfkd = unicodedata.normalize("NFKD", word.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


# Create normalized stopwords set for accent-insensitive matching
NORMALIZED_STOPWORDS = {_normalize_for_stopword(w) for w in PORTUGUESE_STOPWORDS}

ROOT_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT_DIR / "w.csv"
OUTPUT_PATH = ROOT_DIR / "data" / "whatsapp-aggregated.json"

DATE_REGEX = re.compile(r"^\d{2}-\d{2}-\d{2}$")
WORD_REGEX = re.compile(r"[a-záàâãéèêíìîóòôõúùûç]+", re.IGNORECASE)


def normalize_text(text: str) -> str:
    """Normalize text: lowercase and remove accents for comparison."""
    text = text.lower()
    # Remove accents for stopword matching
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def extract_words(text: str) -> list[str]:
    """Extract valid words from text, filtering stopwords and short words."""
    if not text:
        return []

    # Skip media markers
    text_lower = text.lower()
    for marker in MEDIA_MARKERS:
        if marker.lower() in text_lower:
            return []

    # Skip URLs
    if "http://" in text_lower or "https://" in text_lower:
        return []

    # Extract words using regex
    words = WORD_REGEX.findall(text.lower())

    # Filter: min length 3, not a stopword, not a number
    valid_words = []
    for word in words:
        if len(word) < 3:
            continue
        normalized = normalize_text(word)
        # Check normalized word against normalized stopwords
        if normalized in NORMALIZED_STOPWORDS:
            continue
        if word.isdigit():
            continue
        valid_words.append(word)

    return valid_words


def parse_row(row: dict[str, str]) -> dict[str, object] | None:
    """Validate and parse a CSV row into the fields required downstream."""
    date_str = (row.get("date (YYYY-MM-DD)") or "").strip()
    time_str = (row.get("time (hh:mm)") or "").strip()

    if not date_str or not DATE_REGEX.match(date_str):
        return None

    try:
        dt = datetime.strptime(f"{date_str} {time_str}", "%y-%m-%d %H:%M")
    except ValueError:
        return None

    hour = dt.hour

    name = (row.get("name") or "").strip()

    return {
        "date": dt.date(),
        "datetime": dt,
        "hour": hour,
        "day_mon": dt.weekday(),  # Monday = 0
        "year_month": dt.strftime("%Y-%m"),
        "name": name or "Desconhecido",
    }


def build_interactions(parsed_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Build interaction pairs based on consecutive messages within a time window."""
    interaction_counter = Counter()

    sorted_rows = sorted(
        [r for r in parsed_rows if r.get("datetime")],
        key=lambda x: x["datetime"]
    )

    for idx, entry in enumerate(sorted_rows):
        if idx > 0:
            prev = sorted_rows[idx - 1]
            if entry["name"] != prev["name"]:
                diff_minutes = (
                    entry["datetime"] - prev["datetime"]
                ).total_seconds() / 60
                if diff_minutes <= 5:
                    pair = tuple(sorted([entry["name"], prev["name"]]))
                    interaction_counter[pair] += 1

    # Convert to list of dicts for JSON
    interactions = [
        {"source": pair[0], "target": pair[1], "value": count}
        for pair, count in interaction_counter.most_common()
    ]

    return interactions


def build_aggregates(parsed_rows: list[dict[str, object]]) -> dict[str, object]:
    total_messages = len(parsed_rows)
    if total_messages == 0:
        raise ValueError("Nenhuma mensagem válida encontrada em w.csv")

    hours_counter = Counter()
    daily_counter = Counter()
    monthly_counter = Counter()
    heatmap_counter = Counter()
    contributor_counter = Counter()
    word_counter = Counter()
    day_set = set()
    interaction_counter = Counter()

    min_date = parsed_rows[0]["date"]
    max_date = parsed_rows[0]["date"]

    sorted_rows = sorted(parsed_rows, key=lambda r: r["datetime"])

    for idx, entry in enumerate(sorted_rows):
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

        if idx > 0:
            prev = sorted_rows[idx - 1]
            if name != prev["name"]:
                diff_minutes = (
                    entry["datetime"] - prev["datetime"]
                ).total_seconds() / 60
                if diff_minutes <= 5:
                    pair = tuple(sorted([name, prev["name"]]))
                    interaction_counter[pair] += 1

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

    interactions = [
        {"source": pair[0], "target": pair[1], "value": count}
        for pair, count in interaction_counter.most_common()
    ]

    return {
        "generatedAt": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "stats": stats,
        "hourly": hourly,
        "daily": daily,
        "monthly": monthly,
        "heatmap": heatmap,
        "contributors": contributors,
        "interactions": interactions,
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
