#!/usr/bin/env python3
"""Contrat du calendrier prévisionnel."""
import json,re
from datetime import date
from pathlib import Path
root=Path(__file__).resolve().parents[1]
d=json.loads((root/"data/calendrier-pilotage.json").read_text(encoding="utf-8"))
p=d["fr"]
def valid_date(s):
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}",s)
    date.fromisoformat(s)
assert d["version"]==1
assert d["meta"]["statut"]=="hypothèse à confirmer"
assert p["calendrierValide"] is False
assert p["joursFeriesVerifies"] is False
for k in ("debut","fin"):valid_date(p[k])
assert p["debut"]<p["fin"]
valid_date(p["alternance"]["lundiAncre"])
assert date.fromisoformat(p["alternance"]["lundiAncre"]).weekday()==0
assert len(p["alternance"]["semaines"])==2
for slot in p["hebdomadaire"]+p["alternance"]["semaines"]:
    assert slot["jour"] in range(7)
    assert re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d",slot["heure"])
for key in ("exclusions","inclusions"):
    found=set()
    for e in p[key]:
        valid_date(e["date"])
        assert p["debut"]<=e["date"]<=p["fin"]
        assert re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d",e["heure"])
        assert e["motif"]
        if key=="inclusions":assert e["hours"]>0
        pair=(e["date"],e["heure"])
        assert pair not in found
        found.add(pair)
w=p["objectifFenetre"]
valid_date(w["debut"]);valid_date(w["fin"])
assert p["debut"]<=w["debut"]<=w["fin"]<=p["fin"]
print("Contrat calendrier OK")
