#!/usr/bin/env python3
"""Validation du modele pedagogique avant tout commit.

Usage : python3 scripts/validate.py [chemin/vers/events.json ...]
Par defaut : valide tous les fichiers data/*/events.json.

Controles (sans dependance externe) :
  - champs requis et enums (lus depuis schemas/event.schema.json)
  - unicite et format des id
  - cibles des relations existantes
  - chemins d'assets presentes dans le depot (liens morts)
  - assets orphelins (dans assets/ mais references nulle part)
  - contrat vue <-> schema (index.html) :
      * champs lus par la page toujours presents dans le schema (bloque les breaking changes)
      * fallbacks obligatoires pour les enums rendues (type, status)
      * avertissement pour champs du schema non lus / valeurs enum sans libelle
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((ROOT / "schemas" / "event.schema.json").read_text(encoding="utf-8"))
PROPS = SCHEMA["properties"]
REQUIRED = SCHEMA["required"]

def enum_of(field):
    return set(PROPS[field].get("enum", []))

def val_enum(field, value, errors, ctx):
    if value not in enum_of(field):
        errors.append(f"{ctx} : valeur {value!r} invalide pour {field} (autorise : {', '.join(sorted(enum_of(field)))})")

PAGE = ROOT / "index.html"

# Contrat vue <-> modele : champs reels lus par index.html.
# Tout retrait ou renommage cote schema est une ERREUR de commit tant que
# la page et le JSON ne sont pas migres dans le meme commit.
FIELDS_READ_BY_PAGE = [
    "id", "title", "type", "status", "validation_status", "mode",
    "sequence", "planned_date", "actual_date", "duration_hours",
    "summary", "objectives", "notions", "todo", "absent_count",
    "sources", "relations", "review", "full_text", "provenance",
]
# Champs du schema volontairement non rendus par evenement (non bloquant).
ALLOWED_UNREAD = {"course", "assets"}
# Enums rendues via une table de libelles : fallback '||e.champ' OBLIGATOIRE.
ENUM_WITH_FALLBACK = {"type": "TYPE", "status": "STATUS"}
# Enums rendues par simple lookup dans une table (fallback non requis car valeur optionnelle).
ENUM_TABLE_ONLY = {"validation_status": "VSTAT", "mode": "MODE"}

def validate_page_contract(errors, warnings):
    page = PAGE.read_text(encoding="utf-8")
    for f in FIELDS_READ_BY_PAGE:
        if f not in PROPS:
            errors.append(f"contrat vue : champ '{f}' lu par index.html mais absent du schema (breaking change : migrer schema + page + JSON dans le meme commit)")
        if f"e.{f}" not in page:
            errors.append(f"contrat vue : champ '{f}' declare dans FIELDS_READ_BY_PAGE mais introuvable dans index.html (rebrancher le rendu ou retirer de la liste)")
    for f in PROPS:
        if f not in FIELDS_READ_BY_PAGE and f not in ALLOWED_UNREAD:
            warnings.append(f"contrat vue : champ '{f}' du schema non lu par la vue (additif, inoffensif ; a brancher si utile)")
    for f, table in ENUM_WITH_FALLBACK.items():
        if f"||e.{f}" not in page:
            errors.append(f"contrat vue : fallback '{table}[e.{f}]||e.{f}' manquant dans index.html pour l'enum '{f}'")
    for f, table in {**ENUM_WITH_FALLBACK, **ENUM_TABLE_ONLY}.items():
        if f"{table}[e.{f}]" not in page:
            errors.append(f"contrat vue : table de libelles {table} jamais utilisee pour '{f}' dans index.html")
        m = re.search(rf"var {table}=\{{(.*?)\}};", page, re.S)
        if m:
            keys = set(re.findall(r"([a-z_]+)\s*:", m.group(1)))
            for v in (PROPS.get(f, {}).get("enum") or []):
                if v not in keys:
                    warnings.append(f"contrat vue : valeur enum '{f}={v}' sans libelle dans {table} (rendue avec l'identifiant brut)")

def validate_event(ev, ids, all_ids, repo_files, errors, missing_assets, n):
    ctx = f"evenement #{n} ({ev.get('id', '?')})"
    for field in REQUIRED:
        if field not in ev:
            errors.append(f"{ctx} : champ requis manquant '{field}'")
    if "id" in ev:
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", ev["id"]):
            errors.append(f"{ctx} : id invalide (kebab-case attendu)")
        if ev["id"] in ids:
            errors.append(f"{ctx} : id duplique {ev['id']}")
        ids.add(ev["id"])
    for field in ("type", "course", "status", "validation_status"):
        if field in ev:
            val_enum(field, ev[field], errors, ctx)
    if "sequence" in ev and ev["sequence"] and ev["sequence"] not in all_ids and ev["sequence"] != ev.get("id"):
        errors.append(f"{ctx} : sequence inconnue {ev['sequence']}")
    for src in ev.get("sources", []):
        if not src.get("file_id"):
            errors.append(f"{ctx} : source sans file_id")
    for a in ev.get("assets", []):
        p = a.get("path", "")
        if not p.startswith("assets/"):
            errors.append(f"{ctx} : chemin d'asset doit commencer par assets/ ({p})")
        elif (ROOT / p) not in repo_files:
            missing_assets.append(f"{ctx} -> {p}")

def main(argv):
    targets = [Path(a) for a in argv[1:]] if len(argv) > 1 else sorted((ROOT / "data").glob("*/events.json"))
    repo_files = {p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts}
    errors, warnings, missing_assets = [], [], []
    validate_page_contract(errors, warnings)
    for target in targets:
        data = json.loads(Path(target).read_text(encoding="utf-8"))
        events = data["events"] if isinstance(data, dict) else data
        ids = set()
        all_ids = {ev.get("id") for ev in events if ev.get("id")}
        for i, ev in enumerate(events, 1):
            validate_event(ev, ids, all_ids, repo_files, errors, missing_assets, i)
        for ev in events:
            for rel in ev.get("relations", []):
                if rel["target"] not in ids:
                    errors.append(f"{ev.get('id')} : relation vers un id absent ({rel['type']} -> {rel['target']})")
        referenced = {a["path"] for ev in events for a in ev.get("assets", [])}
        orphans = [str(p) for p in (ROOT / "assets").rglob("*") if p.is_file() and str(p.relative_to(ROOT)) not in referenced]
        print(f"[{target}] {len(events)} evenements valides sur le plan structurel" if not errors else f"[{target}] {len(errors)} erreur(s)")
        for o in orphans:
            print(f"  AVERTISSEMENT asset orphelin : {o}")
    for e in errors:
        print(f"  ERREUR : {e}")
    for m in missing_assets:
        print(f"  ERREUR asset manquant : {m}")
    for w in warnings:
        print(f"  AVERTISSEMENT {w}")
    if errors or missing_assets:
        sys.exit(1)
    print("Modele valide : commit autorise.")

if __name__ == "__main__":
    main(sys.argv)
