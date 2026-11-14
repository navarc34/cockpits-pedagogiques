#!/usr/bin/env python3
"""Validation du pilotage v2, références et cas volontairement invalides."""
import copy
import json
from datetime import date
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas/pilotage.schema.json").read_text(encoding="utf-8"))
DATA = json.loads((ROOT / "data/pilotage.json").read_text(encoding="utf-8"))
FR = json.loads((ROOT / "data/fr.json").read_text(encoding="utf-8"))
CHECKER = Draft202012Validator(SCHEMA, format_checker=FormatChecker())

def validate(payload=DATA, fr=FR):
    errors = [str(e) for e in CHECKER.iter_errors(payload)]
    ids = [j.get("id") for j in fr["jalons"] if j.get("id")]
    if len(ids) != len(set(ids)):
        errors.append("identifiant de jalon dupliqué")
    jalons = {j["id"]: j for j in fr["jalons"] if j.get("id")}
    for course_id in ("fr",):
        course = payload.get(course_id, {})
        for group in ("objectifs", "actions"):
            values = course.get(group, [])
            keys = [v.get("id") for v in values]
            if len(keys) != len(set(keys)):
                errors.append(f"{course_id}.{group}: identifiants dupliqués")
        for a in course.get("actions", []):
            j = jalons.get(a.get("jalonId"))
            if not j:
                errors.append(f"{a.get('id')}: jalonId absent")
            elif j["date"] != a["echeance"]:
                errors.append(f"{a['id']}: échéance différente de celle du jalon")
        for o in course.get("objectifs", []):
            s = o.get("source", {})
            if s.get("document") == "jalons du français" and s.get("reference") not in jalons:
                errors.append(f"{o['id']}: source jalon inconnue")
            all_proofs = [
                x for group in ("confirmees", "candidates", "exclues")
                for x in o.get("realisation", {}).get(group, [])
            ]
            refs = [x.get("id") for x in all_proofs]
            if len(refs) != len(set(refs)):
                errors.append(f"{o['id']}: même preuve plusieurs fois")
    return errors

def expect_invalid(name, mutate):
    copy_data = copy.deepcopy(DATA)
    mutate(copy_data)
    assert validate(copy_data), f"Cas invalide accepté: {name}"

def main():
    Draft202012Validator.check_schema(SCHEMA)
    assert not validate(), "\\n".join(validate())
    expect_invalid("date invalide", lambda x: x["fr"]["actions"][0].update(echeance="2026-19-42"))
    expect_invalid("cible non numérique", lambda x: x["fr"]["objectifs"][0].update(cible="douze"))
    expect_invalid("source absente", lambda x: x["fr"]["objectifs"][0].pop("source"))
    expect_invalid("jalon fantôme", lambda x: x["fr"]["actions"][0].update(jalonId="fantome"))
    expect_invalid("id dupliqué", lambda x: x["fr"]["objectifs"][1].update(id=x["fr"]["objectifs"][0]["id"]))
    expect_invalid("preuve dupliquée", lambda x: x["fr"]["objectifs"][0]["realisation"].update(
        candidates=[{"id":"preuve-un","date":"2026-11-10","type":"document","reference":"document test"}],
        confirmees=[{"id":"preuve-un","date":"2026-11-10","type":"document","reference":"document test"}]
    ))

    for o in DATA["fr"]["objectifs"]:
        r = o["reconnaissance"]
        if r["mode"] == "regex":
            import re
            try:
                re.compile(r["motif"], re.I)
            except re.error as exc:
                raise AssertionError(f"Expression de reconnaissance invalide : {o['id']} ({exc})")
    expect_invalid("règle regex absente", lambda x: x["fr"]["objectifs"][0].pop("reconnaissance"))
    expect_invalid("mode manuel avec motif", lambda x: x["fr"]["objectifs"][1]["reconnaissance"].update(motif=".*"))
    print("Pilotage : schéma, cohérence et tests négatifs OK")

if __name__ == "__main__":
    main()
