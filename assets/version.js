/* Identité de version, métadonnées de collecte et statut des progressions. */
(function(){
"use strict";
const esc=s=>String(s??"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
const q=new URLSearchParams(location.search), id=q.get("id"),context=id==="fr"||id==="option"||id==="spe"?id:location.pathname.endsWith("trajectoire.html")?"fr":null;
fetch("data/release.json",{cache:"no-store"}).then(r=>{if(!r.ok)throw Error("version indisponible");return r.json();}).then(m=>{
 const a=m.application,d=m.data,planning=context?m.planning[context]:null;
 const footer=document.createElement("div");footer.id="cockpit-release";
 footer.setAttribute("role","contentinfo");
 footer.style.cssText="max-width:1460px;margin:20px auto 35px;padding:12px 22px;border-top:1px solid var(--line,#ddd);font:11px/1.6 Inter,sans-serif;color:var(--soft,#666)";
 const pieces=["<strong>"+esc(a.version)+"</strong> · "+esc(a.channel),
   "Données "+esc(d.revision)+" · arrêtées au "+esc(d.arrete),
   d.lastSuccessfulSync?"Mis à jour le "+esc(new Date(d.lastSuccessfulSync).toLocaleDateString("fr-FR"))+" à "+esc(new Date(d.lastSuccessfulSync).toLocaleTimeString("fr-FR",{hour:"2-digit",minute:"2-digit"})):"Collecte automatique non activée"];
 if(planning)pieces.push("Progression "+esc(context)+" : "+esc(planning.status));
 pieces.push('<a href="changelog.html" target="_blank" rel="noopener" style="color:inherit">Historique des versions</a>');
 footer.innerHTML=pieces.join(" · ");
 document.body.appendChild(footer);
}).catch(()=>{const status=document.createElement("small");status.textContent="Métadonnées de version indisponibles";status.style.cssText="display:block;padding:10px;color:var(--soft,#666)";document.body.appendChild(status);});
})();
