#!/usr/bin/env node
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const R=path.resolve(__dirname,"..");
const j=p=>JSON.parse(fs.readFileSync(path.join(R,p),"utf8"));
const m=j("data/trajectoire.json"),fr=j("data/fr.json"),cal=j("data/calendrier-pilotage.json");
const engine=require("../assets/trajectoire-projection.js");
const calendar=require("../assets/trajectoire-calendar.js");
assert(engine.validatePlan(m,{...fr.budget,arrete:fr.meta.arrete}));
const p=engine.projection(m,calendar,cal.fr,fr.vacances,"2026-11-14");
assert.equal(p.budget,m.reference.budgetHeures);assert.equal(p.fenetres.length,6);
assert.equal(p.reserve,m.reference.blocs.find(x=>x.type==="reserve").heures);assert(p.capaciteTheorique>0);
assert(p.fenetres.find(x=>x.id==="rimbaud").capaciteTheorique>0);
assert.equal(p.fenetres.find(x=>x.id==="rimbaud").heures,10);
const modified=structuredClone(m);modified.reference.blocs[0].heures++;
assert.throws(()=>engine.validatePlan(modified,{...fr.budget,arrete:fr.meta.arrete}));
console.log("Projection : solde, scénarios, immutabilité et capacité OK");
