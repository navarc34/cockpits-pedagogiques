#!/usr/bin/env python3
"""Cohérence d'un cap annuel de travail, indépendant des fichiers Pronote."""
import copy,json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
ROOT=Path(__file__).resolve().parents[1]
m=json.loads((ROOT/"data/trajectoire.json").read_text(encoding="utf-8"))
schema=json.loads((ROOT/"schemas/trajectoire.schema.json").read_text(encoding="utf-8"))
fr=json.loads((ROOT/"data/fr.json").read_text(encoding="utf-8"))
def validate(x):
    errors=[str(e) for e in Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(x)]
    b=x.get("reference",{}).get("blocs",[])
    if len({v.get("id") for v in b})!=len(b):errors.append("bloc dupliqué")
    if len([v for v in b if v.get("type")=="reserve"])!=1:errors.append("réserve non unique")
    if any(v.get("debut","")>v.get("fin","") for v in b):errors.append("intervalle inversé")
    if sum(v.get("heures",0) for v in b)!=x["reference"]["budgetHeures"]:errors.append("allocation inégale")
    if x["reference"]["budgetHeures"]!=fr["budget"]["aVenir"]:errors.append("budget source divergent")
    if x["meta"]["arrete"]!=fr["meta"]["arrete"]:errors.append("arrêté divergent")
    return errors
assert not validate(m),"\n".join(validate(m))
assert m["meta"]["statut"]=="brouillon"
for name,mutate in [
 ("budget impossible",lambda x:x["reference"]["blocs"][0].update(heures=999)),
 ("date invalide",lambda x:x["reference"]["blocs"][0].update(debut="2026-19-40")),
 ("bloc dupliqué",lambda x:x["reference"]["blocs"][1].update(id=x["reference"]["blocs"][0]["id"])),
 ("réserve absente",lambda x:x["reference"]["blocs"][-1].update(type="sequence"))
]:
 c=copy.deepcopy(m);mutate(c);assert validate(c),name
print("Trajectoire : contrat, budget, chronologie et tests négatifs OK")
