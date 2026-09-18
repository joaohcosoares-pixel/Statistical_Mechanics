const fs=require('node:fs'),vm=require('node:vm'),crypto=require('node:crypto'),path=require('node:path');
const root=path.resolve(__dirname,'..'), dir=path.join(__dirname,'before');
const names=['Simulation2_UrbanLattice.html','Simulation3_Metropolis.html','Simulation4_Convergence.html','transitSimulation.html'];
const hash=s=>crypto.createHash('sha256').update(s).digest('hex');
function core(html,i){return i<3?html.match(/<script id="model">([\s\S]*?)<\/script>/)[1]:html.match(/<script>([\s\S]*?)<\/script>/)[1];}
function load(src,i){const ctx=vm.createContext({console});vm.runInContext(src,ctx);return vm.runInContext(['Simulation02','Simulation03Core','Simulation04','UrbanCore'][i],ctx);}
function collect(C,i){
 if(i===0){const n=new C.UrbanNetwork(),cal=C.calibrate(n),e=new C.AnnealingEngine(n,cal.temperature0,cal.amplitude).run();return {seed:C.CONFIG.seed,config:C.CONFIG,network:C.NETWORK_CONFIG,initial:C.INITIAL_STATE,calibration:cal,summary:C.summarize(e,cal.reference),state:e.state.values,metrics:e.metrics,history:e.history.points,events:e.events,validation:C.validateExperiment(e,cal)};}
 if(i===1)return C.buildTeachingExperiment();
 if(i===2){const s=C.validateAndSelect(new C.UrbanNetwork());return {...C.continuitySnapshot(s),events:s.run.events,history:s.run.history};}
 const sim=new C.TrafficSimulation().warmup(),o=new C.AnnealingController(sim),dt=C.CONFIG.physicsDt;
 for(let tick=1;tick<=Math.round(C.CONFIG.duration*C.CONFIG.timeScale/dt);tick++){sim.step(dt);o.update(tick*dt/C.CONFIG.timeScale);}
 return {config:C.CONFIG,state:sim.state,metrics:sim.metrics,vehicles:sim.vehicles,history:o.history,attempted:o.attemptedMoves,accepted:o.acceptedMoves,simulationErrors:sim.validate(),optimizerErrors:o.validate()};
}
if(process.argv.includes('--capture')){
 fs.mkdirSync(dir,{recursive:true});const out={};
 names.forEach((n,i)=>{const html=fs.readFileSync(path.join(root,n),'utf8');if(fs.existsSync(path.join(dir,n)))throw Error('Baseline already exists');fs.writeFileSync(path.join(dir,n),html);const c=core(html,i),data=collect(load(c,i),i);out[n]={fileHash:hash(html),coreHash:hash(c),data};console.log('Captured',n);});
 fs.writeFileSync(path.join(__dirname,'baseline.json'),JSON.stringify(out,null,2));
}else{
 const before=JSON.parse(fs.readFileSync(path.join(__dirname,'baseline.json'),'utf8')),out={status:'PASS',files:[]};
 names.forEach((n,i)=>{const target=i===3?'transitSimulation_legacy.html':n,html=fs.readFileSync(path.join(root,target),'utf8'),c=core(html,i),data=JSON.parse(JSON.stringify(collect(load(c,i),i))),b=before[n];const same=JSON.stringify(data)===JSON.stringify(b.data),sameCore=hash(c)===b.coreHash;out.files.push({file:target,scientificCoreByteIdentical:sameCore,allScientificResultsExactlyEqual:same,beforeCoreSHA256:b.coreHash,afterCoreSHA256:hash(c),beforeResultsSHA256:hash(JSON.stringify(b.data)),afterResultsSHA256:hash(JSON.stringify(data))});if(!same||!sameCore)out.status='FAIL';console.log(target,same&&sameCore?'PASS':'FAIL');});
 fs.writeFileSync(path.join(__dirname,'regression-results.json'),JSON.stringify(out,null,2));if(out.status!=='PASS')process.exitCode=1;
}
