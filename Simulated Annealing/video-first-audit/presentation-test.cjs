const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const report={status:'PASS',note:'Testes de lógica em Node; inspeção de DOM, estilos e screenshots feita separadamente no navegador.',files:[]};
for(const [n,name] of [[2,'Simulation2_UrbanLattice.html'],[3,'Simulation3_Metropolis.html'],[4,'Simulation4_Convergence.html']]){
 const html=fs.readFileSync(path.join(root,name),'utf8'),ctx=vm.createContext({console,window:{}}),scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
 scripts.slice(0,2).forEach(s=>vm.runInContext(s,ctx));
 vm.runInContext('VideoPresentation.commonContract=()=>[]; VideoPresentation.mount=s=>{window.spec=s;};',ctx);
 vm.runInContext(scripts[2],ctx);const spec=ctx.window.spec;
 assert.equal(spec.presentationValidation.status,'PASS');
 const noop=()=>{},canvas=new Proxy({createRadialGradient:()=>({addColorStop:noop})},{get:(t,p)=>p in t?t[p]:noop,set:(t,p,v)=>(t[p]=v,true)});
 const text=[];let frames=0;
 for(let k=0;k<=spec.duration*60;k++){
  const t=k/60,f=spec.at(t);spec.draw(canvas,f,t);frames++;
  assert.ok((f.graphs||0)<=1);assert.ok(f.pair||(f.importantNumbers||0)<=3);
  if(f.P!==null&&f.P!==undefined)assert.ok(Number.isFinite(f.P)&&f.P>=0&&f.P<=1);
  if(f.scientificTime!==undefined)assert.ok(Number.isFinite(f.scientificTime));
 }
 for(const p of spec.phases){const f=spec.at(p.start+1);text.push({phase:p.name,start:p.start,text:[f.title,f.subtitle,f.panel,f.center,f.caption].filter(Boolean).join('\n').replace(/<[^>]+>/g,' ')});}
 // Seeking/restarting is pure: every scene and full export must be identical on replay.
 const exportBefore=JSON.stringify(spec.export());for(const t of [spec.duration,0,7,spec.duration/2,0])spec.at(t);
 assert.equal(JSON.stringify(spec.export()),exportBefore);
 fs.writeFileSync(path.join(__dirname,`simulation-0${n}-results.json`),JSON.stringify(spec.export(),null,2));
 report.files.push({file:name,framesAt60fps:frames,contract:spec.presentationValidation,seekDoesNotChangeScience:true,scenes:text});
 if(n===4){
  // A distinct existing seed prevents an equality in the selected run from hiding
  // an accidental finalState/bestState substitution. Production selection is untouched.
  const other=vm.createContext({console,window:{}});scripts.slice(0,2).forEach(s=>vm.runInContext(s,other));
  vm.runInContext(`Simulation04.validateAndSelect=network=>{const run=new Simulation04.AnnealingEngine(network,31415926).run();return {run,seed:31415926,report:Simulation04.validateTrajectory(run),trials:[]};};VideoPresentation.commonContract=()=>[];VideoPresentation.mount=s=>{window.spec=s;};`,other);
  vm.runInContext(scripts[2],other);const s=other.window.spec,e=s.export(),end=s.at(s.duration);
  assert.notEqual(e.finalEnergy,e.bestEnergy);assert.deepEqual(Array.from(end.mapState),Array.from(e.bestState));assert.notDeepEqual(Array.from(end.mapState),Array.from(e.finalState));
  report.bestVersusFinalWitness={seed:31415926,finalEnergy:e.finalEnergy,bestEnergy:e.bestEnergy,closingMapUsesBest:true,productionSeedUnchanged:true};
 }
 console.log(name,'PASS');
}
const before=fs.readFileSync(path.join(__dirname,'before/transitSimulation.html'),'utf8'),after=fs.readFileSync(path.join(root,'transitSimulation_legacy.html'),'utf8');
assert.equal(before.match(/<style>([\s\S]*?)<\/style>/)[1],after.match(/<style>([\s\S]*?)<\/style>/)[1]);
assert.ok(after.includes('MODELO ALTERNATIVO DE TRÁFEGO')&&after.includes('NÃO FAZ PARTE DA CADEIA SIMULAÇÃO 02 → 03 → 04 → 05'));
report.legacyIdentificationOnly=true;
fs.writeFileSync(path.join(__dirname,'presentation-results.json'),JSON.stringify(report,null,2));
