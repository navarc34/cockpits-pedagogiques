#!/usr/bin/env python3
"""Validation du dépôt avant tout commit (CI + local).

Usage : python3 scripts/validate.py

Contrôles :
  1. CONFIDENTIALITÉ (bloquant) — liste noire insensible à la casse sur tous les
     fichiers de contenu (data/*.json, index.html, cours.html, README.md,
     schemas/*.json) : noms propres, établissement, code de classe, liens privés
     (visio, pads, Drive), adresses e-mail. Le dépôt est public : toute fuite
     est bloquée au build, pas au moment où on s'en souvient.
  2. Structure v1 (data/*/events.json) : champs requis et enums lus depuis
     schemas/event.schema.json, unicité des id, cibles des relations,
     chemins d'assets existants.
  3. Structure v2 : tous les data/*.json doivent parser et exposer les clés
     attendues (meta + courses|seances).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- confidentialité
# Motifs interdits, insensibles à la casse, dans le CONTENU des fichiers scannés.
BLACKLIST = [
    "urfe", "honoré", "st2s3", "dufêtre", "durieux", "guillaume", "hugonnet",
    "nicolas", "ac-lyon", "1llcal1",
    "cv-aura.apps.education.fr", "digipad.app/p/", "chat.mistral.ai",
    "drive.google.com", "docs.google.com",
]
# Adresses e-mail (aucune adresse ne doit figurer dans les données).
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

def scan_paths():
    paths = list((ROOT / "data").glob("*.json"))
    paths += list((ROOT / "data").glob("*/events.json"))
    paths += list((ROOT / "schemas").glob("*.json"))
    for name in ("index.html", "cours.html", "README.md"):
        p = ROOT / name
        if p.exists():
            paths.append(p)
    return paths

def validate_privacy(errors):
    for p in scan_paths():
        text = p.read_text(encoding="utf-8", errors="replace")
        low = text.lower()
        for pat in BLACKLIST:
            if pat in low:
                idx = low.index(pat)
                errors.append(f"CONFIDENTIALITÉ [{p}] : motif interdit « {pat} » → …{text[max(0, idx-40):idx+60]}…")
        if p.suffix == ".json":
            for m in EMAIL_RE.finditer(text):
                errors.append(f"CONFIDENTIALITÉ [{p}] : adresse e-mail détectée « {m.group(0)} »")

# ---------------------------------------------------------------- structure v1
SCHEMA_PATH = ROOT / "schemas" / "event.schema.json"

def load_schema():
    if SCHEMA_PATH.exists():
        return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return None

def validate_events_file(target, schema, errors, warnings):
    props = (schema or {}).get("properties", {})
    required = (schema or {}).get("required", [])
    data = json.loads(Path(target).read_text(encoding="utf-8"))
    events = data["events"] if isinstance(data, dict) else data
    ids = set()
    for i, ev in enumerate(events, 1):
        ctx = f"[{target}] évément #{i} ({ev.get('id', '?')})"
        for field in required:
            if field not in ev:
                errors.append(f"{ctx} : champ requis manquant '{field}'")
        eid = ev.get("id", "")
        if eid:
            if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", eid):
                errors.append(f"{ctx} : id invalide (kebab-case attendu)")
            if eid in ids:
                errors.append(f"{ctx} : id dupliqué {eid}")
            ids.add(eid)
        for field in ("type", "course", "status", "validation_status"):
            allowed = props.get(field, {}).get("enum")
            if allowed and ev.get(field) and ev[field] not in allowed:
                errors.append(f"{ctx} : valeur {ev[field]!r} invalide pour {field}")
    for ev in events:
        for rel in ev.get("relations", []):
            if rel["target"] not in ids:
                errors.append(f"[{target}] {ev.get('id')} : relation vers un id absent ({rel['type']} -> {rel['target']})")

# ---------------------------------------------------------------- structure v2
V2_REQUIRED = {
    "global.json": {"meta", "courses", "prioritesGlobales", "calendrier"},
    "fr.json": {"meta", "budget", "priorites", "jalons", "seances"},
    "option.json": {"meta", "budget", "priorites", "jalons", "seances"},
    "spe.json": {"meta", "budget", "priorites", "jalons", "seances"},
}

def validate_v2(errors, warnings):
    for name, keys in V2_REQUIRED.items():
        p = ROOT / "data" / name
        if not p.exists():
            warnings.append(f"data/{name} absent (toléré si non déployé)")
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        missing = keys - set(d.keys())
        if missing:
            errors.append(f"[data/{name}] clés manquantes : {', '.join(sorted(missing))}")
        if "meta" in d and "id" in d["meta"] and d["meta"]["id"] != name[:-5]:
            errors.append(f"[data/{name}] meta.id ({d['meta']['id']}) != nom de fichier")

# ---------------------------------------------------------------- main
def main():
    errors, warnings = [], []
    validate_privacy(errors)
    schema = load_schema()
    for target in sorted((ROOT / "data").glob("*/events.json")):
        validate_events_file(target, schema, errors, warnings)
    validate_v2(errors, warnings)
    for w in warnings:
        print(f"  AVERTISSEMENT {w}")
    for e in errors:
        print(f"  ERREUR : {e}")
    if errors:
        print(f"\n{len(errors)} erreur(s) — commit refusé.")
        sys.exit(1)
    print("Dépôt valide : commit autorisé.")

if __name__ == "__main__":
    main()
