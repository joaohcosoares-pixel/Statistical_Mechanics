(()=>{
 'use strict';
 try{
  const S=Simulation05,V=VideoPresentation,{C,concept,detail,note,eyebrow,metric,fmt}=V;
  const reference=JSON.parse(document.getElementById('simulation04-reference').textContent),data=new S.ComparisonData(new S.UrbanNetwork(),reference);
  // ComparisonData throws before any result is rendered if 04 → 05 fails.
  const title='O ALGORITMO MELHOROU O MODELO?',fullDuration=28;
  const rows=[[0,'A pergunta'],[3,'Mesma rede e demanda'],[6,'Configuração inicial'],[12,'Melhor configuração encontrada'],[19,'Redução do custo'],[24,'Resultado agregado']];
  const phases=rows.map(([start,name])=>({start,name}));
  function at(t){
   const f={title,showBefore:t>=6,showAfter:t>=12,importantNumbers:0,graphs:0,beforeScale:S.delayColor,afterScale:S.delayColor};
   if(t<3){f.center=concept('ANTES × DEPOIS')+detail('O que mudou na mesma rede?');}
   else if(t<6){f.center=concept('MESMA REDE<br>MESMA DEMANDA')+detail('Outra configuração semafórica.');}
   else if(t<19){
    const card=(before)=>eyebrow(before?'ANTES':'DEPOIS')+concept(before?'CONFIGURAÇÃO INICIAL':'MELHOR CONFIGURAÇÃO<br>ENCONTRADA')+metric(before?'CUSTO INICIAL E₀':'MELHOR CUSTO E',fmt(before?data.initialMetrics.energy:data.bestEnergy),before?'cyan':'green');
    f.centerClass='comparison05';f.center=`<div class="compare-05"><section>${card(true)}</section><section>${t>=12?card(false):''}</section></div>`;f.importantNumbers=t>=12?2:1;
    f.subtitle='MESMA REDE · MESMA DEMANDA · OUTRA CONFIGURAÇÃO SEMAFÓRICA';
    f.caption='Escala de cores fixa nos dois mapas · pontos representam fluxo ilustrativo.';
   }else{
    f.showBefore=true;f.showAfter=true;f.dim=true;f.center=eyebrow('REDUÇÃO DO CUSTO')+`<div class="hero green" style="font-size:88px">${fmt(data.energyReduction,1)}%</div>`;
    if(data.validation.checks.meanReduction)f.center+=`<div style="margin-top:35px">${metric('ATRASO MÉDIO DO MODELO','↓ '+fmt(data.delayReduction,1)+'%','cyan')}</div>`;
    f.center+=note('MELHOR ESTADO VISITADO NESTA EXECUÇÃO<br>SEM GARANTIA DE ÓTIMO GLOBAL');f.importantNumbers=2;
    f.caption='Alguns trechos podem piorar localmente. O resultado principal é agregado.';
    if(t>=24){f.title='O RESULTADO PRINCIPAL É AGREGADO';f.subtitle='Melhor custo da rede não significa melhora em todos os trechos.';}
   }
   f.accessible=[f.title,f.subtitle,(f.center||'').replace(/<[^>]+>/g,' '),f.caption||''].join('. ');return f;
  }
  function draw(ctx,f,t){
   const opacity=f.dim?.10:1,common={opacity,particles:!f.dim,colorScale:S.delayColor};
   if(f.showBefore)V.map(ctx,data.network,data.initialState,data.initialMetrics,t,{...common,rect:{x:92,y:407,w:805,h:413}});
   if(f.showAfter)V.map(ctx,data.network,data.bestState,data.bestMetrics,t,{...common,rect:{x:1035,y:407,w:805,h:413}});
  }
  const snapshot=()=>({seed:data.seed,modelVersion:S.NETWORK_CONFIG.version,NETWORK_CONFIG:S.NETWORK_CONFIG,INITIAL_STATE:data.initialState,initialState:data.initialState,bestState:data.bestState,finalState:data.finalState,bestEnergy:data.bestEnergy,finalEnergy:data.lastEnergy,bestResult:data.bestResult,initialMetrics:data.initialMetrics,bestMetrics:data.bestMetrics,energyReduction:data.energyReduction,delayReduction:data.delayReduction,metricChanges:data.metricChanges,bestIteration:data.bestIteration,bestTime:data.bestTime,lastEnergy:data.lastEnergy,schedule:data.schedule,particlesPerPanel:data.particles,events:data.events,compatibility:data.compatibility,validation:data.validation,visualScale:S.COLOR_STOPS});
  const fullChecks=V.commonContract({},phases.map(p=>at(p.start+1)));
  fullChecks.push({label:'Contrato 04 → 05 e métricas validados antes da exibição',pass:data.compatibility.status==='PASS'&&data.validation.status==='PASS'});
  fullChecks.push({label:'Cores de 04 e 05 usam a mesma função de transferência',pass:[...data.initialMetrics.delays,...data.bestMetrics.delays,...S.COLOR_STOPS.map(x=>x[0])].every(d=>V.delayColor(d)===S.delayColor(d))});
  const presentationValidation={status:fullChecks.every(c=>c.pass)?'PASS':'FAIL',duration:fullDuration,checks:fullChecks};
  const full={duration:fullDuration,title,phases,at,draw,presentationValidation,scienceValidation:{comparison:data.validation,compatibility:data.compatibility,trajectory:data.trajectoryValidation},export:snapshot,filename:'simulacao-05',api:'Simulation05Experiment',alias:'ComparisonExperiment',events:data.events,history:data.events};
  full.video={...full,duration:16,phases:[[0,'Antes × depois'],[2,'Antes'],[6,'Depois'],[10,'Resultado agregado']].map(([start,name])=>({start,name})),at(t){const source=t<2?4:t<6?7:t<10?13:20;const f=at(source);if(t<2){f.title=title;f.center=concept('ANTES × DEPOIS')+detail('MESMA REDE · MESMA DEMANDA');}f.accessible=[f.title,f.subtitle,(f.center||'').replace(/<[^>]+>/g,' '),f.caption||''].join('. ');return f;}};
  VideoModes.mount(5,full);
 }catch(error){const el=document.getElementById('error');el.hidden=false;el.textContent='O resultado não será exibido: a validação falhou. '+error.message;document.getElementById('panel').hidden=true;document.getElementById('center').hidden=true;console.error(error);}
})();
