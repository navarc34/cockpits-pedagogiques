#!/usr/bin/env python3
"""Contrat de versionnement : application, révisions publiques et scénarios."""
import json,re
from datetime import date
from pathlib import Path
R=Path(__file__).resolve().parents[1]
m=json.loads((R/"data/release.json").read_text(encoding="utf-8"))
p=json.loads((R/"data/progression-scenarios.json").read_text(encoding="utf-8"))
global_data=json.loads((R/"data/global.json").read_text(encoding="utf-8"))
def date_check(x):
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}",x)
    date.fromisoformat(x)
assert m["schemaVersion"]==1 and p["schemaVersion"]==1
a=m["application"];d=m["data"]
assert re.fullmatch(r"0\.\d+\.\d+-beta\.\d+",a["version"])
assert a["channel"]=="beta"
date_check(a["releasedOn"]);date_check(d["arrete"])
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}\.\d+",d["revision"])
assert d["arrete"]==global_data["meta"]["arrete"]
assert p["meta"]["arrete"]==d["arrete"]
assert p["meta"]["revision"]==d["revision"]
assert d["lastSuccessfulSync"] is None or isinstance(d["lastSuccessfulSync"],str)
assert d["collection"]=="manuelle" if d["lastSuccessfulSync"] is None else True
assert set(m["planning"])=={"fr","option","spe"}
assert set(p["cours"])==set(m["planning"])
for key in m["planning"]:
    assert m["planning"][key]["status"]==p["cours"][key]["status"]
    assert m["planning"][key]["status"] in {"brouillon","en construction","validée"}
    assert isinstance(p["cours"][key]["propositions"],list)
    for scenario in p["cours"][key]["propositions"]:
        assert scenario["statut"] in {"proposition","à instruire","validée","écartée"}
        assert scenario["source"] and scenario["id"]
for page in ["index.html","cours.html","trajectoire.html"]:
    assert '<script src="assets/version.js"></script>' in (R/page).read_text(encoding="utf-8")
print("Versionnement : application, données, scénarios et intégration OK")
