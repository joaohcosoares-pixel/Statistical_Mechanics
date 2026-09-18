const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),assert=require('node:assert/strict');
const {block,load}=require('./regression.cjs');
const root=path.resolve(__dirname,'..'),files=['Simulation2_UrbanLattice.html','Simulation3_Metropolis.html','Simulation4_Convergence.html','index.html'];
const report={status:'PASS',method:'Frame logic and draw calls at 60 fps in Node VM. DOM/CSS verified separately in Chromium.',files:[]};
function presentation(html,id,mode='video',inject=''){
 const alerts=[],elements={error:{hidden:true},panel:{},center:{}};
 const document={documentElement:{lang:'pt-BR'},querySelectorAll:s=>s==='#scene'?[{}]:[],querySelector:()=>null,styleSheets:[{cssRules:[{cssText:'.recording #controls {display: none !important;cursor: none !important;}'}]}],getElementById:key=>key==='simulation04-reference'?{textContent:block(html,key)}:elements[key]};
 const ctx=vm.createContext({console:{info:()=>{},log:()=>{},warn:()=>{},error:e=>alerts.push(e.message)},window:{},document,location:{search:'?mode='+mode},URLSearchParams,TextEncoder});
 if(id===5)vm.runInContext(block(html,'scientific-core'),ctx);
 vm.runInContext(block(html,'model'),ctx);
 vm.runInContext(block(html,'presentation-common'),ctx);
 vm.runInContext('VideoPresentation.mount=s=>{window.spec=s;};',ctx);
 vm.runInContext(block(html,'presentation-modes'),ctx);
 if(inject)vm.runInContext(inject,ctx);
 vm.runInContext(block(html,'presentation'),ctx);
 return {spec:ctx.window.spec,ctx,alerts,elements};
}
const noop=()=>{},canvas=new Proxy({createRadialGradient:()=>({addColorStop:noop})},{get:(t,p)=>p in t?t[p]:noop,set:(t,p,v)=>(t[p]=v,true)});
for(const [i,file] of files.entries()){
 const id=i+2,html=fs.readFileSync(path.join(root,file),'utf8'),result={file,modes:{}};let scientificExport;
 for(const mode of ['video','full']){
  const {spec,alerts}=presentation(html,id,mode);assert.ok(spec,alerts.join('\n'));assert.equal(spec.mode,mode);assert.equal(spec.presentationValidation.status,'PASS');let frames=0,lastScience=-Infinity;
  for(let k=0;k<=spec.duration*60;k++){
   const t=k/60,f=spec.at(t);spec.draw(canvas,f,t);frames++;
   assert.ok((f.graphs||0)<=1);assert.ok(f.pair||(f.importantNumbers||0)<=3);
   if(f.P!=null)assert.ok(Number.isFinite(f.P)&&f.P>=0&&f.P<=1);
   if(f.scientificTime!==undefined){assert.ok(f.scientificTime>=lastScience);lastScience=f.scientificTime;}
  }
  const exported=JSON.stringify(spec.export());for(const t of [spec.duration,0,7,spec.duration/2,0])spec.at(t);assert.equal(JSON.stringify(spec.export()),exported);
  const data=JSON.parse(exported);delete data.presentationValidation;delete data.presentationModes;
  if(scientificExport)assert.equal(JSON.stringify(data),scientificExport);else scientificExport=JSON.stringify(data);
  result.modes[mode]={duration:spec.duration,framesAt60fps:frames,contract:spec.presentationValidation,seekDoesNotChangeScience:true,scenes:spec.phases.map(p=>{const f=spec.at(Math.min(spec.duration,p.start+1));return {start:p.start,name:p.name,text:[f.title,f.subtitle,f.panel,f.center,f.caption].filter(Boolean).join('\n').replace(/<[^>]+>/g,' ')};})};
  if(mode==='video')fs.writeFileSync(path.join(__dirname,`simulation-0${id}-results.json`),exported);
 }
 result.scientificExportIdenticalAcrossModes=true;report.files.push(result);console.log(file,'both modes PASS');
 if(id===4){
  const inject=`Simulation04.validateAndSelect=network=>{const run=new Simulation04.AnnealingEngine(network,31415926).run();return {run,seed:31415926,report:Simulation04.validateTrajectory(run),trials:[]};};`;
  for(const mode of ['video','full']){const {spec:s}=presentation(html,id,mode,inject),e=s.export(),end=s.at(s.duration);assert.notEqual(e.finalEnergy,e.bestEnergy);assert.deepEqual(Array.from(end.mapState),Array.from(e.bestState));assert.notDeepEqual(Array.from(end.mapState),Array.from(e.finalState));report.bestVersusFinalWitness={seed:31415926,finalEnergy:e.finalEnergy,bestEnergy:e.bestEnergy,closingMapUsesBestInBothModes:true,productionSeedUnchanged:true};}
 }
}
const html5=fs.readFileSync(path.join(root,'index.html'),'utf8'),reference=JSON.parse(block(html5,'simulation04-reference'));
report.failClosedTests=[];
for(const field of ['seed','proposalAmplitude','T0','Tf','N','alpha','bestEnergy','finalEnergy','bestState','finalState','proposalTraceSha256','NETWORK_CONFIG','INITIAL_STATE']){
 const ref=structuredClone(reference);if(field==='bestState'||field==='finalState'||field==='INITIAL_STATE')ref[field][0]+=.01;else if(field==='NETWORK_CONFIG')ref[field].edges[0][3]+=.01;else if(field==='proposalTraceSha256')ref[field]='invalid';else ref[field]+=.01;
 const modified=html5.replace(block(html5,'simulation04-reference'),JSON.stringify(ref));const failed=presentation(modified,5);assert.equal(failed.spec,undefined);assert.equal(failed.elements.error.hidden,false);assert.equal(failed.elements.panel.hidden,true);assert.ok(failed.alerts.length);report.failClosedTests.push({field,rejectedBeforeMount:true});
}
const legacy=fs.readFileSync(path.join(root,'transitSimulation_legacy.html'),'utf8');assert.ok(!/SIMULAÇÃO 02|Simulação 02/.test(legacy));assert.ok(legacy.includes('NÃO UTILIZADO NA CADEIA PRINCIPAL DO VÍDEO'));
report.legacy={identification:'PASS',scientificMotor:'checked byte-for-byte in regression.cjs'};
fs.writeFileSync(path.join(__dirname,'presentation-results.json'),JSON.stringify(report,null,2));console.log('13 incompatible references rejected before rendering; all tests PASS');
module.exports={presentation};
