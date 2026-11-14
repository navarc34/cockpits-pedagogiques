/* Reconnaissance explicable : sélection de séances candidates, jamais de validation automatique. */
(function(root){
"use strict";
const statuses=new Set(["publié","distanciel","réalisé non publié"]);
function sessionId(s){
 if(!/^\d{4}-\d{2}-\d{2}$/.test(s.date)||!/^\d{2}:\d{2}$/.test(s.time))throw Error("Identité de séance invalide");
 return "fr-seance-"+s.date+"-"+s.time.replace(":","");
}
function candidates(objective,seances,cutoff){
 const r=objective.reconnaissance;
 if(!r||r.mode==="manuel")return [];
 const pattern=new RegExp(r.motif,"iu");
 const excluded=new Set(objective.realisation.exclues.filter(p=>p.type==="seance").map(p=>p.reference));
 const confirmed=new Set(objective.realisation.confirmees.filter(p=>p.type==="seance").map(p=>p.reference));
 const result=[];
 for(const s of seances){
  if(s.date>cutoff||!statuses.has(s.statut))continue;
  const id=sessionId(s);
  if(excluded.has(id)||confirmed.has(id))continue;
  const hits=r.champs.filter(c=>pattern.test(String(s[c]||"")));
  if(!hits.length)continue;
  result.push({id,date:s.date,time:s.time,titre:s.titre||"Séance sans titre",statut:s.statut,champs:hits,objectif:objective.id});
 }
 return result.sort((a,b)=>a.date.localeCompare(b.date)||a.time.localeCompare(b.time));
}
function audit(objective,seances,cutoff){
 const suggestions=candidates(objective,seances,cutoff);
 return {
  suggestions,
  confirmes:objective.realisation.confirmees.length,
  exclus:objective.realisation.exclues.length,
  pending:suggestions.length,
  mode:objective.reconnaissance.mode
 };
}
const api={sessionId,candidates,audit};
if(typeof module!=="undefined"&&module.exports)module.exports=api;
root.CockpitEvidence=api;
})(typeof window!=="undefined"?window:globalThis);
