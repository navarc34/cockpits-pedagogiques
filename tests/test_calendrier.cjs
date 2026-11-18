#!/usr/bin/env node
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const base=path.resolve(__dirname,"..");
const cfg=JSON.parse(fs.readFileSync(path.join(base,"data/calendrier-pilotage.json"),"utf8")).fr;
const fr=JSON.parse(fs.readFileSync(path.join(base,"data/fr.json"),"utf8"));
const {generate,reconcile}=require("../assets/trajectoire-calendar.js");
const s=generate(cfg,fr.vacances,"2026-09-04","2026-11-20");
const has=(day,h)=>s.some(x=>x.date===day&&x.heure===h);
assert(has("2026-09-11","13:00"));
assert(has("2026-09-14","15:00"));
assert(has("2026-11-02","11:00"));
assert(!has("2026-10-19","11:00"));
assert(has("2026-11-20","13:00"));
const past=generate(cfg,fr.vacances,"2026-09-04","2026-11-13");
const report=reconcile(past,fr.seances,"2026-11-13");
assert(report.prevu>0&&report.documente>0);
assert(report.documente<=report.prevu);
// Aucun dossier à vérifier est un état normal quand le suivi est à jour.
assert(Number.isInteger(report.aVerifier) && report.aVerifier >= 0);
assert.equal(
  report.aVerifier,
  report.rows.filter(x=>x.qualification==="à vérifier").length
);
assert(!report.rows.some(x=>x.qualification==="retard"));
const withExtra={...cfg,inclusions:[{date:"2026-10-19",heure:"11:00",hours:1,motif:"séance exceptionnelle"}]};
assert.equal(generate(withExtra,fr.vacances,"2026-10-19","2026-10-19").length,1);
const cancelled={...cfg,exclusions:[{date:"2026-11-02",heure:"11:00",motif:"annulation"}]};
assert(!generate(cancelled,fr.vacances,"2026-11-02","2026-11-02").some(x=>x.heure==="11:00"));
console.log("Calendrier : alternance, vacances, exceptions et rapprochement OK");
