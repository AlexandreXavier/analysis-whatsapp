import json
from pathlib import Path

from scripts import generate_aggregated_data as gen


def write_sample_csv(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "date (YYYY-MM-DD),time (hh:mm),name,text",
                "24-01-01,12:00,Alice,Olá a todos",
                "24-01-01,12:03,Bob,Olá Alice",
                "24-01-01,14:00,Alice,Conversa diferente",
                "24-01-01,14:04,Charlie,Resposta rápida",
                "24-01-02,09:00,Bob,Bom dia",
            ]
        ),
        encoding="utf-8",
    )


def test_generate_aggregated_json(tmp_path, monkeypatch):
    csv_path = tmp_path / "w.csv"
    data_dir = tmp_path / "data"
    output_path = data_dir / "whatsapp-aggregated.json"

    data_dir.mkdir()
    write_sample_csv(csv_path)

    monkeypatch.setattr(gen, "CSV_PATH", csv_path)
    monkeypatch.setattr(gen, "OUTPUT_PATH", output_path)

    gen.main()

    assert output_path.exists(), "O ficheiro JSON agregado deveria ser criado"

    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert data["stats"]["totalMessages"] == 5
    assert data["stats"]["uniqueParticipants"] == 3
    assert len(data["hourly"]) == 24
    assert len(data["daily"]) == 7
    assert len(data["interactions"]) >= 2

    pair_names = {(i["source"], i["target"]) for i in data["interactions"]}
    assert ("Alice", "Bob") in pair_names or ("Bob", "Alice") in pair_names
