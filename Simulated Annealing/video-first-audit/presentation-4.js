(() => {
 'use strict';
 const S=Simulation04,V=VideoPresentation,{C,fmt,metric,concept,detail,note,eyebrow}=V,network=new S.UrbanNetwork(),selection=S.validateAndSelect(network),run=selection.run;
 const replay=new S.AnnealingEngine(network,selection.seed),frames=[];
 const copyResult=r=>({energy:r.energy,meanDelay:r.meanDelay,weightedDelay:r.weightedDelay,delays:Array.from(r.delays),capacities:Array.from(r.capacities),rhos:Array.from(r.rhos)});
 const capture=()=>frames.push({t:replay.time,state:Array.from(replay.state),result:copyResult(replay.result),T:replay.temperature,best:replay.bestEnergy});
 capture();while(!replay.finished){replay.step();capture();}
 if(!S.sameRun(run,replay))throw Error('Reprodução visual divergiu da trajetória validada');
 const history=Array.from({length:run.history.length},(_,i)=>({t:run.history.t[i],e:run.history.e[i],best:run.history.best[i],T:run.history.T[i]}));
 const phases=[[0,'A pergunta'],[4,'O custo atual'],[8,'Guardamos o melhor'],[13,'T alta: exploração'],[21,'T diminui'],[32,'T baixa: seleção'],[40,'Estabilização'],[45,'Resultado da execução'],[51,'Redução do custo']].map(([start,name])=>({start,name}));
 const duration=58,title='O QUE ACONTECE QUANDO RESFRIAMOS?';
 // Edit pacing here, independently of the immutable scientific schedule.
 function scientificTime(t){if(t<4)return 0;if(t<8)return (t-4)*.7/4;if(t<13)return .7;if(t<21)return V.lerp(.7,3,(t-13)/8);if(t<32)return V.lerp(3,10,(t-21)/11);if(t<40)return V.lerp(10,14,(t-32)/8);if(t<45)return V.lerp(14,16,(t-40)/5);return 16;}
 function at(t){
  const ph=V.phaseAt(phases,t),i=phases.indexOf(ph),science=scientificTime(t),sample=frames[Math.min(frames.length-1,Math.floor(science*120+1e-9))];
  const f={phase:i,title,subtitle:'RECOZIMENTO SIMULADO EM UMA EXECUÇÃO COMPLETA',scientificTime:science,sample,mapState:sample.state,mapResult:sample.result,mapTime:science,opacity:1,graphs:0,importantNumbers:0};
  if(i===0){f.opacity=.17;f.center=concept('A TEMPERATURA DIMINUI.<br>A BUSCA FICA MAIS SELETIVA.')+detail('Guardamos a melhor configuração encontrada.');}
  if(i>=1&&i<=6){
   f.importantNumbers=3;f.graphs=1;const titles=['','O CUSTO ATUAL PODE SUBIR E DESCER','GUARDAMOS O MELHOR RESULTADO','T ALTA → EXPLORAÇÃO','T DIMINUI → PIORAS FICAM MENOS PROVÁVEIS','T BAIXA → BUSCA MAIS SELETIVA','ESTABILIZAÇÃO EM BAIXA T'];
   const subtitles=['','Cada ponto da curva vem de uma decisão real do algoritmo.','O melhor custo só muda quando encontramos uma configuração ainda melhor.','Muitas pioras ainda podem ser aceitas.','A temperatura cai a cada nova proposta.','As flutuações ficam menores nesta execução.','Execução finita · melhor estado encontrado nesta execução.'];
   f.title=titles[i];f.subtitle=subtitles[i];
   const thermal=V.clamp(Math.log(sample.T/S.CONFIG.temperatureFinal)/Math.log(S.CONFIG.temperatureInitial/S.CONFIG.temperatureFinal));
   f.panel=metric('TEMPERATURA T',fmt(sample.T,5),'orange')+`<div class="bar"><span style="width:${100*thermal}%"></span></div><div class="two">${metric('CUSTO ATUAL',fmt(sample.result.energy),'cyan')}${metric('MELHOR CUSTO',fmt(sample.best),'green')}</div>`+note('Tₙ = T₀ αⁿ · barra em escala logarítmica');
   f.caption=i===1?'<b>Curva ciano → custo da configuração atual.</b>':i===2?'<span class="green">Curva verde → menor custo visitado até agora.</span>':i===6?'Execução finita: a busca conserva a melhor configuração encontrada.':'Cores das vias: atraso no modelo · pontos: fluxo ilustrativo.';
  }
  if(i>=7){f.opacity=.13;f.mapState=run.bestState;f.mapResult=run.bestResult;f.mapTime=run.bestTime;
   if(i===7){f.title='O QUE ESTA EXECUÇÃO ENCONTROU?';f.subtitle='O estado final e o melhor estado são registrados separadamente.';f.center=concept('CUSTO E(x)')+`<div class="summary"><div>${metric('ESTADO INICIAL',fmt(run.initialEnergy),'muted')}</div><div>${metric('ESTADO FINAL',fmt(run.result.energy),'cyan')}</div><div>${metric('MELHOR ESTADO<br>ENCONTRADO',fmt(run.bestEnergy),'green')}</div></div>`+note(run.result.energy===run.bestEnergy?'Nesta execução, o estado final também é o melhor encontrado.':'O melhor estado foi guardado, mesmo após outras mudanças.');f.importantNumbers=3;}
   else{f.title='MELHOR ESTADO ENCONTRADO NESTA EXECUÇÃO';f.subtitle='A configuração guardada permanece na rede ao fundo.';f.center=eyebrow('REDUÇÃO DO CUSTO EM RELAÇÃO AO INÍCIO')+`<div class="hero green" style="font-size:88px">${fmt(100*(run.initialEnergy-run.bestEnergy)/run.initialEnergy,1)}%</div>`+detail('A temperatura caiu.<br>A busca ficou mais seletiva.<br>O melhor estado ficou guardado.')+note('Resultado de uma execução finita com dados sintéticos.');f.importantNumbers=1;}
  }
  f.accessible=[f.title,f.subtitle,(f.panel||f.center||'').replace(/<[^>]+>/g,' ')].join('. ');return f;
 }
 function draw(ctx,f){
  V.map(ctx,network,f.mapState,f.mapResult,f.mapTime,{opacity:f.opacity});
  if(f.graphs){
   const points=history.slice(0,Math.floor(f.scientificTime*120+1e-9)+1);V.chart(ctx,points,{y:670,h:178,best:true,max:selection.report.maxEnergy*1.08,highlight:f.phase===1?'current':f.phase===2?'best':''});
   V.line(ctx,1230,922,1270,922,C.cyan,3);V.label(ctx,'atual',1280,929,20,C.cyan);V.line(ctx,1440,922,1480,922,C.green,4);V.label(ctx,'melhor encontrado',1490,929,20,C.green);
   if(f.phase===1||f.phase===2){const key=f.phase===1?'e':'best',point=points.at(-1),x=1230+point.t/16*594,y=848-point[key]/(selection.report.maxEnergy*1.08)*178;
    V.line(ctx,x+18,y-8,1400,704,f.phase===1?C.cyan:C.green,2);V.label(ctx,f.phase===1?'Pode subir e descer':'Só muda quando melhora',1420,711,22,f.phase===1?C.cyan:C.green);
   }
  }
 }
 function validatePresentationContract(){
  const samples=phases.map(p=>at(p.start+1)),checks=V.commonContract({duration},samples),check=(ok,label)=>checks.push({label,pass:!!ok});
  check(S.sameRun(run,replay),'Mesma trajetória, decisões, estados e melhor resultado');
  check(run.events.every((e,i)=>e.T===run.schedule.atStep(i)),'Schedule científico original preservado');
  let min=Infinity;check(history.every(p=>{min=Math.min(min,p.e);return p.best===min;}),'Curva verde é o mínimo acumulado exato');
  check(history.some(p=>p.e!==p.best),'Custo atual e melhor custo são distintos durante a execução');
  check(samples.filter(f=>f.graphs).every(f=>['TEMPERATURA T','CUSTO ATUAL','MELHOR CUSTO'].every(s=>f.panel.includes(s))),'Três grandezas principais visíveis');
  check(samples.every(f=>!/(ACEITAÇÃO|UPHILL|MICROSTATE|ITERAÇÃO|SEED)/.test(f.panel||'')),'Telemetria secundária fora da apresentação');
  check(at(48).mapState===run.bestState&&at(55).mapState===run.bestState&&at(55).mapResult===run.bestResult,'Fechamento usa bestState e bestResult');
  check(at(48).center.includes('ESTADO FINAL')&&at(48).center.includes('MELHOR ESTADO'),'Final e melhor identificados separadamente');
  check(frames.length===1921&&scientificTime(58)===16,'Todos os 1920 passos científicos são reproduzidos');
  return {status:checks.every(c=>c.pass)?'PASS':'FAIL',checks,duration,scientificDuration:16};
 }
 const presentationValidation=validatePresentationContract();if(presentationValidation.status!=='PASS')throw Error('Falha no contrato da apresentação 04');
 window.validatePresentationContract=validatePresentationContract;
 V.mount({duration,title,phases,at,draw,presentationValidation,scienceValidation:selection.report,export:()=>({...S.continuitySnapshot(selection),presentationValidation}),filename:'simulacao-04',api:'Simulation04Experiment',alias:'AnnealingExperiment',events:run.events,history});
})();
