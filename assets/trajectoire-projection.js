/* Simulation non persistante et projection à données sourcées. */
(function(root){
"use strict";
const sum=xs=>xs.reduce((a,x)=>a+x.heures,0);
const utc=s=>Date.parse(s+"T12:00:00Z");
const addDays=(s,n)=>new Date(utc(s)+n*86400000).toISOString().slice(0,10);
function validatePlan(model,budget){
 if(model.version!==1||!model.reference||!model.meta)throw Error("Trajectoire incompatible");
 if(model.meta.arrete!==budget.arrete)throw Error("Arrêté de la trajectoire différent du budget source");
 if(model.reference.budgetHeures!==budget.aVenir)throw Error("Le budget du plan ne correspond plus au budget source");
 const blocs=model.reference.blocs;
 if(new Set(blocs.map(x=>x.id)).size!==blocs.length)throw Error("Identifiants de blocs dupliqués");
 if(blocs.filter(x=>x.type==="reserve").length!==1)throw Error("Une réserve unique est requise");
 if(blocs.some(x=>x.heures<0||x.debut>x.fin))throw Error("Allocation ou intervalle invalide");
 if(sum(blocs)!==model.reference.budgetHeures)throw Error("Le plan ne répartit pas exactement le budget restant");
 return true;
}
function scenario(model,id,delta){
 if(!Number.isInteger(delta))throw Error("Variation entière requise");
 const original=model.reference.blocs;
 const target=original.find(x=>x.id===id);
 const reserve=original.find(x=>x.type==="reserve");
 if(!target||target.type==="reserve")throw Error("Bloc ajustable introuvable");
 // Ne modifie jamais le modèle reçu.
 const blocs=original.map(x=>({...x}));
 blocs.find(x=>x.id===id).heures+=delta;
 blocs.find(x=>x.type==="reserve").heures-=delta;
 const feasible=blocs.every(x=>x.heures>=0);
 return {blocs,feasible,solde:reserve.heures-delta,variation:delta,id,
   motif:feasible?"Réallocation sans dépasser la réserve déclarée.":"Réserve insuffisante ou allocation négative ; arbitrage nécessaire."};
}
function capacity(calendar,vacances,from,to){
 if(!calendar||!calendar.generate)throw Error("Moteur calendrier indisponible");
 const slots=calendar.generate(to.config,vacances,from,to.end);
 return slots.reduce((s,x)=>s+x.hours,0);
}
function projection(model,calendar,calendarConfig,vacances,day){
 const blocks=model.reference.blocs;
 const active=day>=model.meta.arrete;
 const plan=calendar.generate(calendarConfig,vacances,addDays(model.meta.arrete,1),calendarConfig.fin);
 const possible=plan.reduce((a,x)=>a+x.hours,0);
 const budget=model.reference.budgetHeures;
 const windows=blocks.map(b=>{
   const windowSlots=calendar.generate(calendarConfig,vacances,b.debut,b.fin);
   return {...b,capaciteTheorique:windowSlots.reduce((a,x)=>a+x.hours,0),partagee:b.type!=="sequence"};
 });
 const past=plan.filter(x=>x.date<day).reduce((a,x)=>a+x.hours,0);
 return {active,budget,capaciteTheorique:possible,difference:possible-budget,fenetres:windows,
   reserve:blocks.find(b=>b.type==="reserve").heures,
   heuresEcouleesTheoriques:past,
   avertissement:"Capacité reconstruite à partir d’une hypothèse de récurrence non validée. Les heures transversales partagent les mêmes créneaux que les séquences : ne pas additionner les capacités par bloc."};
}
const api={validatePlan,scenario,projection};
if(typeof module!=="undefined"&&module.exports)module.exports=api;
root.CockpitProjection=api;
})(typeof window!=="undefined"?window:globalThis);
