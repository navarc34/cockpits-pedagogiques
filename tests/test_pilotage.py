import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
d=json.loads((root/"data/pilotage.json").read_text(encoding="utf-8"))
assert d["version"]==1
assert d["fr"]["objectifs"] and d["fr"]["actions"]
for group in ("objectifs","actions"):
    items=d["fr"][group]
    assert len({e["id"] for e in items})==len(items),f"identifiants dupliques : {group}"
    for e in items:
        assert e["echeance"].startswith("202")
for o in d["fr"]["objectifs"]:
    assert o["cible"]>0 and "valeurConfirmee" in o
for a in d["fr"]["actions"]:
    assert 1<=a["importance"]<=3 and a["justification"] and a["sourceRecherche"]
print("Contrat pilotage : OK")
