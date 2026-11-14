#!/usr/bin/env python3
"""Validation des cockpits pedagogiques v2 et du modele legacy v1.

Sans dependance externe. Le script verifie :
- parsing JSON de toutes les sources publiques ;
- contrat minimal global.json / fr.json / option.json / spe.json ;
- coherence des budgets et identifiants de cours ;
- champs essentiels des seances ;
- absence des marqueurs d'identification interdits dans les fichiers publics ;
- validation structurelle minimale de data/francais/events.json (legacy v1).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
errors = []
warnings = []

BANNED = [
    r"Honor[eé] d['’]Urf[eé]", r"ST2S3", r"Duf[eê]tre", r"Durieux",
    r"nicolas\.guillaume@ac-lyon\.fr", r"nguillaume", r"1LLCAL1", r"cv-aura", r"digipad\.app",
    r"chat\.mistral", r"drive\.google"
]
COURSE_IDS = {"fr", "option", "spe"}

def err(msg):
    errors.append(msg)

def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        err(f"{path.relative_to(ROOT)} : JSON invalide ({exc})")
        return None

def need(obj, keys, ctx):
    if not isinstance(obj, dict):
        err(f"{ctx} : objet attendu")
        return
    for key in keys:
        if key not in obj:
            err(f"{ctx} : champ requis manquant '{key}'")

def validate_budget(b, ctx):
    need(b, ["total", "consomme", "aVenir", "unite"], ctx)
    if not isinstance(b, dict):
        return
    vals=[b.get("total"), b.get("consomme"), b.get("aVenir")]
    if not all(isinstance(v, (int, float)) for v in vals):
        err(f"{ctx} : total/consomme/aVenir doivent etre numeriques")
    elif abs(b["total"] - b["consomme"] - b["aVenir"]) > 1e-9:
        err(f"{ctx} : total != consomme + aVenir")

def validate_global():
    p=DATA/"global.json"; d=load(p)
    if d is None: return
    need(d, ["meta","courses","prioritesGlobales","calendrier"], "global.json")
    if not isinstance(d.get("courses"), list) or len(d["courses"]) != 3:
        err("global.json : exactement 3 cours attendus")
        return
    ids=set()
    for i,c in enumerate(d["courses"]):
        ctx=f"global.json courses[{i}]"
        need(c, ["id","nom","couleur","href","budget","progressionStatut","resume","prochainJalon"], ctx)
        ids.add(c.get("id"))
        validate_budget(c.get("budget"), ctx+" budget")
    if ids != COURSE_IDS:
        err(f"global.json : ids cours attendus {sorted(COURSE_IDS)}, obtenus {sorted(x for x in ids if x)}")
    pg=d.get("prioritesGlobales",{})
    need(pg, ["court","moyen","long"], "global.json prioritesGlobales")

def validate_course(cid):
    p=DATA/f"{cid}.json"; d=load(p)
    if d is None: return
    ctx=f"data/{cid}.json"
    need(d, ["meta","budget","priorites","jalons","vacances","seances","programme","grammaire","culture","progression"], ctx)
    if d.get("meta",{}).get("id") != cid:
        err(f"{ctx} : meta.id doit valoir '{cid}'")
    validate_budget(d.get("budget"), ctx+" budget")
    need(d.get("priorites",{}), ["court","moyen","long"], ctx+" priorites")
    for i,s in enumerate(d.get("seances",[])):
        sctx=f"{ctx} seances[{i}]"
        need(s, ["date","time","hours","titre","statut","theme","cat","contenu","resume","elements","afaire","absents"], sctx)
        if s.get("statut") not in {"publié","réalisé non publié","distanciel","à saisir"}:
            err(f"{sctx} : statut inconnu {s.get('statut')!r}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(s.get("date",""))):
            err(f"{sctx} : date ISO attendue")
    for i,b in enumerate(d.get("programme",[])):
        need(b, ["bloc","items"], f"{ctx} programme[{i}]")
        for j,item in enumerate(b.get("items",[])):
            need(item, ["label","n"], f"{ctx} programme[{i}].items[{j}]")
            if not isinstance(item.get("n"), int) or item.get("n",0) < 0:
                err(f"{ctx} programme[{i}].items[{j}] : n doit etre un entier >= 0")

def validate_legacy():
    p=DATA/"francais"/"events.json"
    d=load(p)
    if d is None: return
    events=d.get("events") if isinstance(d,dict) else d
    if not isinstance(events,list):
        err("data/francais/events.json : liste events attendue")
        return
    ids=set()
    for i,e in enumerate(events):
        ctx=f"legacy event[{i}]"
        if not isinstance(e,dict):
            err(f"{ctx} : objet attendu"); continue
        for k in ("id","title","type","course","status"):
            if k not in e: err(f"{ctx} : champ requis manquant '{k}'")
        eid=e.get("id")
        if eid:
            if eid in ids: err(f"{ctx} : id duplique {eid}")
            ids.add(eid)
    print(f"[legacy] {len(events)} evenement(s) charges")

def validate_anonymisation():
    public_paths=[
        ROOT/"index.html", ROOT/"cours.html", ROOT/"README.md",
        DATA/"global.json", DATA/"fr.json", DATA/"option.json", DATA/"spe.json",
        DATA/"francais"/"events.json", DATA/"francais"/"events-public.json"
    ]
    for p in public_paths:
        if not p.exists(): continue
        txt=p.read_text(encoding="utf-8", errors="replace")
        for pattern in BANNED:
            if re.search(pattern, txt, re.I):
                err(f"{p.relative_to(ROOT)} : marqueur interdit detecte /{pattern}/")

def main():
    validate_global()
    for cid in sorted(COURSE_IDS):
        validate_course(cid)
    validate_legacy()
    validate_anonymisation()
    if errors:
        for e in errors: print("ERREUR :", e)
        print(f"Validation refusee : {len(errors)} erreur(s).")
        sys.exit(1)
    for w in warnings: print("AVERTISSEMENT :", w)
    print("Cockpits v2 + legacy : modele valide, anonymisation controlee.")

if __name__ == "__main__":
    main()
