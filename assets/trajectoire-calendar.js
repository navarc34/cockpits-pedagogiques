/* Calendrier prévisionnel statique, explicitement hypothétique. */
(function(root){
"use strict";
const utc=s=>Date.parse(s+"T12:00:00Z");
const iso=t=>new Date(t).toISOString().slice(0,10);
const wd=t=>new Date(t).getUTCDay();
const monday=t=>t-((wd(t)+6)%7)*86400000;
const key=e=>e.date+"|"+e.heure;
function generate(config,vacances,from,to){
 const start=Math.max(utc(from||config.debut),utc(config.debut));
 const end=Math.min(utc(to||config.fin),utc(config.fin));
 if(end<start)return [];
 const output=[],anchor=monday(utc(config.alternance.lundiAncre));
 const excluded=new Set(config.exclusions.map(key));
 for(let t=start;t<=end;t+=86400000){
   const d=iso(t),vac=(vacances||[]).some(v=>d>=v.debut&&d<v.fin);
   const week=Math.floor((monday(t)-anchor)/604800000);
   const index=((week%config.alternance.semaines.length)+config.alternance.semaines.length)%config.alternance.semaines.length;
   const slots=[...config.hebdomadaire,config.alternance.semaines[index]];
   for(const s of slots){
     if(s.jour!==wd(t))continue;
     const item={date:d,heure:s.heure,hours:config.heuresParCreneau,libelle:s.libelle,origine:"récurrence"};
     if(!vac&&!excluded.has(key(item)))output.push(item);
   }
 }
 for(const e of config.inclusions){
   if(e.date<iso(start)||e.date>iso(end))continue;
   const item={date:e.date,heure:e.heure,hours:e.hours,libelle:e.motif,origine:"exception"};
   const at=output.findIndex(x=>key(x)===key(item));
   if(at>=0)output.splice(at,1);
   output.push(item);
 }
 return output.sort((a,b)=>key(a).localeCompare(key(b)));
}
function reconcile(slots,seances,cutoff){
 const records=new Map();
 for(const s of seances.filter(x=>x.date<=cutoff)){
   const k=s.date+"|"+s.time;
   if(!records.has(k))records.set(k,[]);
   records.get(k).push(s);
 }
 const matched=new Set();
 const rows=slots.filter(s=>s.date<=cutoff).map(s=>{
   const rs=records.get(key(s))||[];matched.add(key(s));
   const state=rs.some(x=>x.statut==="publié"||x.statut==="distanciel")?"documenté":rs.length?"à vérifier":"sans trace";
   return {...s,qualification:state,documents:rs};
 });
 const extras=[...records].filter(([k])=>!matched.has(k)).flatMap(([,rs])=>rs);
 return {
   rows,horsModele:extras,
   prevu:rows.reduce((n,x)=>n+x.hours,0),
   documente:rows.filter(x=>x.qualification==="documenté").reduce((n,x)=>n+x.hours,0),
   aVerifier:rows.filter(x=>x.qualification==="à vérifier").length,
   sansTrace:rows.filter(x=>x.qualification==="sans trace").length
 };
}
const api={generate,reconcile};
if(typeof module!=="undefined"&&module.exports)module.exports=api;
root.CockpitCalendar=api;
})(typeof window!=="undefined"?window:globalThis);
