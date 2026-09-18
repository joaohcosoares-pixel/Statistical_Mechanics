(() => {
 'use strict';
 const S=Simulation03Core,V=VideoPresentation,{C,fmt,signed,metric,concept,detail,note,eyebrow}=V,data=S.buildTeachingExperiment(),a=data.caseA,p=data.pairedUphill;
 const phases=[
  [0,'O estado atual'],[3.5,'Uma pequena alteração'],[7,'A diferença de custo'],[11,'O que ΔE significa'],
  [15,'O custo diminuiu'],[19,'Aceitar a melhora'],[23,'Novo teste'],[27,'Outra alteração'],[31,'O custo aumentou'],
  [35,'Rejeitar sempre?'],[38,'Uma piora pode ser aceita'],[41,'Critério de Metrópolis'],[46,'A temperatura'],
  [50,'O limite de aceitação'],[55,'O sorteio'],[60,'Comparar u e P'],[64,'Decisão com T alta'],
  [68,'Só a temperatura muda'],[75,'Reduzindo a temperatura'],[85,'Decisão com T baixa'],
  [89,'Comparação das decisões'],[95,'Configurações resultantes'],[100,'Exploração e seleção'],[105,'Resfriar aos poucos']
 ].map(([start,name])=>({start,name}));
 const duration=111,title='COMO O ALGORITMO DECIDE?';
 const change=e=>eyebrow('INTERSEÇÃO '+String(e.intersection).padStart(2,'0'))+concept('TEMPO DE VERDE')+`<div class="value purple">${fmt(e.beforeValue*100,0)}% → ${fmt(e.afterValue*100,0)}%</div>`+note('Apenas este semáforo muda.<br>As vias conectadas são destacadas.');
 function at(t){
  const ph=V.phaseAt(phases,t),i=phases.indexOf(ph),event=t<23?a:p;
  const f={phase:i,title,subtitle:'',event,state:event.currentState,result:event.currentResult,focus:-1,opacity:1,map:false,mapTime:0,T:null,P:null,u:null,showRuler:false,showU:false,showTest:false,decision:undefined,importantNumbers:0,graphs:0};
  if(i<=3){f.centerClass='flow';f.center=eyebrow('UMA PROPOSTA DE MUDANÇA')+`<div class="flow-row"><div><span class="symbol cyan">x</span><small>ESTADO ATUAL</small></div>${i>=1?'<span class="arrow">→</span><div><span class="symbol purple">x′</span><small>PEQUENA ALTERAÇÃO</small></div>':''}</div>`+(i>=2?`<div class="concept mono">ΔE = E(x′) − E(x)</div>`:'')+(i>=3?detail('ΔE mede como o custo mudou.'):'');}
  if(i===4){f.map=true;f.focus=a.index;f.state=a.candidateState;f.result=a.candidateResult;f.panel=change(a)+`<div class="separator"></div>`+concept('O CUSTO DIMINUIU','green')+`<div class="value green">ΔE = ${signed(a.delta)}</div>`;f.importantNumbers=3;}
  if(i===5){f.map=true;f.state=a.candidateState;f.result=a.candidateResult;f.decision=true;f.panel=concept('ΔE < 0','green')+concept('O CUSTO DIMINUIU')+`<div class="big-symbol green">✓</div><div class="value green">ACEITAR</div>`+detail('O novo estado passa a ser x.');}
  if(i===6){f.map=true;f.opacity=.20;f.center=eyebrow('NOVO TESTE')+concept('VOLTAMOS AO MESMO<br>ESTADO DE REFERÊNCIA');}
  if(i===7){f.map=true;f.focus=p.index;f.state=p.candidateState;f.result=p.candidateResult;f.panel=eyebrow('FAZEMOS OUTRA ALTERAÇÃO')+change(p);f.importantNumbers=2;}
  if(i===8){f.map=true;f.state=p.candidateState;f.result=p.candidateResult;f.panel=eyebrow('ΔE > 0')+concept('A NOVA CONFIGURAÇÃO<br>TEM CUSTO MAIOR','orange')+metric('VARIAÇÃO DO CUSTO',signed(p.delta),'orange');f.importantNumbers=1;}
  if(i===9){f.map=true;f.opacity=.13;f.center=`<div class="hero">REJEITAR SEMPRE?</div>`;}
  if(i===10){f.center=`<div class="hero purple">NÃO.</div>`+detail('Uma piora ainda pode ser aceita.');}
  if(i===11){f.title='CRITÉRIO DE METRÓPOLIS';f.center=concept('UMA PIORA AINDA PODE SER ACEITA')+`<div class="big-symbol mono purple" style="font-size:70px">P = exp(−ΔE/T)</div>`+detail('P é a probabilidade de aceitar.<br>Esta expressão vale quando ΔE > 0.');}
  if(i===12){f.title='A TEMPERATURA CONTROLA ESSA CHANCE';f.center=concept('T ALTA → MAIOR CHANCE DE ACEITAR')+metric('TEMPERATURA COMPUTACIONAL',fmt(p.high.temperature),'orange')+note('Um parâmetro do algoritmo, na mesma escala do custo.');f.importantNumbers=1;f.T=p.high.temperature;}
  if(i>=13&&i<=16){f.map=true;f.state=p.candidateState;f.result=p.candidateResult;f.opacity=.62;f.showRuler=true;f.T=p.high.temperature;f.P=p.high.probability;f.u=p.u;f.showU=i>=14;f.showTest=i>=15;
   f.panel=i===13?eyebrow('TEMPERATURA ALTA')+concept('P É O LIMITE<br>DE ACEITAÇÃO')+detail('A faixa verde aceita a proposta.<br>O restante rejeita.'):i===14?eyebrow('UM SORTEIO ALEATÓRIO')+concept('SORTEAMOS u<br>ENTRE 0 E 1')+detail('Agora comparamos u com P.'):i===15?eyebrow('A REGRA DE DECISÃO')+concept('SE u < P, ACEITAR')+detail('Caso contrário, rejeitar.'):eyebrow('TEMPERATURA ALTA')+concept('O SORTEIO CAIU<br>NA FAIXA VERDE','green')+detail('A piora foi aceita.');
   f.importantNumbers=i>=14?2:1;if(i===16)f.decision=true;
   f.caption=i===16?'A configuração proposta x′ foi aceita.':'Configuração proposta x′ · a decisão ainda não foi tomada.';
  }
  if(i===17){f.center=eyebrow('UMA COMPARAÇÃO CONTROLADA')+concept('MESMA CONFIGURAÇÃO INICIAL<br>MESMA ALTERAÇÃO<br>MESMO ΔE · MESMO SORTEIO u')+detail('↓')+`<div class="concept purple">SÓ UMA COISA MUDA: TEMPERATURA</div>`+note('Mesmo u usado apenas para comparar as duas temperaturas.<br>Em uma execução normal, cada proposta recebe um novo sorteio.');}
  if(i===18||i===19){
   const progress=V.clamp((t-75)/8);f.T=progress===1?p.low.temperature:progress===0?p.high.temperature:V.lerp(p.high.temperature,p.low.temperature,progress);f.P=S.probability(p.delta,f.T);f.u=p.u;f.map=true;f.state=p.candidateState;f.result=p.candidateResult;f.opacity=.45;f.showRuler=true;f.showU=true;f.stationary=true;f.showTest=i===19;f.importantNumbers=3;
   f.title='MESMA ALTERAÇÃO. SÓ T MUDA.';f.panel=eyebrow('T ↓ → P ↓')+metric('TEMPERATURA T',fmt(f.T),'orange')+concept(i===19?'A REGIÃO DE ACEITAÇÃO<br>FICOU MENOR QUE O SORTEIO':'A FAIXA VERDE ENCOLHE');
   if(i===19)f.decision=false;
   f.caption='Mesmo estado atual, mesma proposta e mesmo sorteio; apenas a temperatura muda.';
   if(i===19&&t>=87){f.state=p.currentState;f.result=p.currentResult;f.opacity=.62;f.caption='A proposta x′ foi rejeitada. O estado atual x foi mantido.';}
  }
  if(i===20||i===21){f.title='MESMA ALTERAÇÃO. SÓ T MUDOU.';f.pair=true;f.outcomes=i===21;f.centerClass='flow';f.center=`<div class="comparison"><div>${eyebrow('TEMPERATURA ALTA')}${concept('P MAIOR', 'green')}${i===20?'<p class="formula mono">u < P</p>':''}<div class="value green">✓ ACEITA</div></div><div>${eyebrow('TEMPERATURA BAIXA')}${concept('P MENOR','orange')}${i===20?'<p class="formula mono">u > P</p>':''}<div class="value red">× REJEITA</div></div></div>`;f.caption=i===20?'Mesmo u usado apenas para comparar as duas temperaturas.':'Após a decisão: a temperatura alta aceita x′; a baixa mantém x.';f.importantNumbers=0;}
  if(i===22){f.center=`<div class="comparison"><div>${eyebrow('T ALTA')}${concept('MAIS EXPLORAÇÃO','orange')}</div><div>${eyebrow('T BAIXA')}${concept('MAIS SELEÇÃO','cyan')}</div></div>`;}
  if(i===23){f.center=`<div class="hero">E SE REDUZIRMOS T<br>AOS POUCOS?</div>`+detail('↓')+concept('SIMULAÇÃO 04 · RESFRIAMENTO','purple');}
  if(f.pair&&!f.outcomes)f.importantNumbers=4;
  f.accessible=[f.title,(f.panel||f.center||'').replace(/<[^>]+>/g,' '),f.showRuler?`Limite de aceitação P = ${fmt(f.P)}.${f.showU?' Sorteio u = '+fmt(f.u)+'.':''}${f.decision===undefined?'':f.decision?' Aceitar.':' Rejeitar.'}`:''].join('. ');return f;
 }
 function draw(ctx,f){
  if(f.map)V.map(ctx,data.network,f.state,f.result,f.mapTime,{focus:f.focus,opacity:f.opacity,particles:false});
  if(f.showRuler)V.ruler(ctx,f.P,f.u,{showU:f.showU,showTest:f.showTest,decision:f.decision??null,stationary:f.stationary});
  if(f.pair){
   if(!f.outcomes){V.ruler(ctx,p.high.probability,p.u,{x:246,y:660,w:600,showU:true});V.ruler(ctx,p.low.probability,p.u,{x:1074,y:660,w:600,showU:true});}
   else{V.map(ctx,data.network,p.candidateState,p.candidateResult,0,{rect:{x:230,y:530,w:670,h:365},particles:false});V.map(ctx,data.network,p.currentState,p.currentResult,0,{rect:{x:1060,y:530,w:670,h:365},particles:false});}
  }
 }
 function validatePresentationContract(){
  const samples=phases.map(p=>at(p.start+1)),checks=V.commonContract({duration},samples),check=(ok,label)=>checks.push({label,pass:!!ok});
  check([16,20].every(t=>{const f=at(t);return f.T===null&&f.u===null&&!f.showRuler;}),'Melhora sem temperatura, sorteio ou régua');
  check(samples.filter(f=>f.phase<11).every(f=>f.P===null&&f.u===null&&!f.showRuler),'Nenhuma probabilidade antes da explicação de ΔE');
  check(!at(52).showU&&at(56).showU,'Primeiro o limite P, depois o sorteio u');
  check(at(63).decision===undefined&&at(65).decision===true&&at(84).decision===undefined&&at(86).decision===false,'Decisões reveladas somente nos momentos previstos');
  const transition=Array.from({length:121},(_,k)=>at(75+k*8/120));
  check(transition.every(f=>f.event===p&&f.state===p.candidateState&&f.result===p.candidateResult&&f.event.currentState===p.currentState&&f.event.delta===p.delta&&f.u===p.u&&f.mapTime===0),'Mesmos x, x′, ΔE, u e enquadramento na transição');
  check(transition.every((f,k)=>f.P===Math.exp(-p.delta/f.T)&&(!k||f.P<=transition[k-1].P)),'Somente T muda P; faixa verde diminui');
  check(transition[0].T===p.high.temperature&&transition[0].P===p.high.probability&&transition.at(-1).T===p.low.temperature&&transition.at(-1).P===p.low.probability,'Extremos da transição iguais aos valores científicos, sem arredondamento');
  check(transition.every(f=>1230+594*f.u===1230+594*p.u),'Posição visual de u permanece fixa');
  check(!at(92).outcomes&&at(97).outcomes,'Mapas resultantes divergem somente depois da decisão');
  check(at(84).state===p.candidateState&&at(88).state===p.currentState,'Após rejeitar, o mapa volta ao estado atual');
  check(at(70).center.includes('novo sorteio'),'Reutilização de u explicitamente restrita à comparação');
  return {status:checks.every(c=>c.pass)?'PASS':'FAIL',checks,duration,transitionSamples:transition.length};
 }
 const presentationValidation=validatePresentationContract();if(presentationValidation.status!=='PASS')throw Error('Falha no contrato da apresentação 03');
 window.validatePresentationContract=validatePresentationContract;
 V.mount({duration,title,phases,at,draw,presentationValidation,scienceValidation:data.validation,export:()=>({...data,presentationValidation}),filename:'simulacao-03',api:'MetropolisExperiment',events:[a,p]});
})();
