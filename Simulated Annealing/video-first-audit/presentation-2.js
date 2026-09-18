(() => {
 'use strict';
 const S=Simulation02,V=VideoPresentation,{C,fmt,metric,concept,detail,note,eyebrow}=V;
 const network=new S.UrbanNetwork(),calibration=S.calibrate(network),engine=new S.AnnealingEngine(network,calibration.temperature0,calibration.amplitude),frames=[];
 const capture=()=>frames.push({state:engine.state,result:engine.result,t:engine.time,historyLength:engine.history.points.length});
 capture();while(engine.time<S.CONFIG.duration-1e-9){engine.step();capture();}
 const scienceValidation=S.validateExperiment(engine,calibration),summary=S.summarize(engine,calibration.reference);
 const phases=[
  [0,'A pergunta'],[3,'A rede'],[5.8,'As vias'],[8.6,'As cores'],[11.4,'O fluxo ilustrativo'],
  [14.2,'Um semáforo'],[20,'A configuração'],[24,'O estado x'],[28,'Como comparar'],
  [32,'O custo'],[36,'Menor custo'],[40,'A função de custo'],[45,'Exploração com T alta'],
  [61,'Aceitar apenas melhorias?'],[65,'Busca gulosa'],[69,'Mínimos locais']
 ].map(([start,name])=>({start,name}));
 const duration=73,title='O QUE O COMPUTADOR ESTÁ TENTANDO MELHORAR?';
 function at(t){
  const p=V.phaseAt(phases,t),i=phases.indexOf(p),f={title,phase:i,importantNumbers:0,graphs:0,scientificTime:0,focus:-1,opacity:1};
  f.scientificTime=t<45?0:Math.min(14,(t-45)*14/16);f.sample=frames[Math.min(frames.length-1,Math.floor(f.scientificTime/S.CONFIG.dt+1e-9))];
  f.caption='';
  if(i===0){f.opacity=.17;f.center=concept('Cada semáforo pode mudar.<br>O que torna uma configuração melhor?');}
  if(i>=1&&i<=4){f.title='REDE URBANA SIMPLIFICADA';
   const texts=[['INTERSEÇÃO / SEMÁFORO','Cada ponto conecta as vias.'],['VIA','Cada ligação representa<br>um trecho da rede.'],['COR DA VIA','Indica o atraso no modelo.'],['FLUXO ILUSTRATIVO','Os pontos ajudam a visualizar o fluxo.<br>Não são veículos simulados.']];
   f.panel=eyebrow('COMO LER A REDE')+concept(texts[i-1][0])+detail(texts[i-1][1]);if(i===1)f.focus=6;
   if(i===3)f.panel+=`<div class="detail"><span class="cyan">MENOR ATRASO</span><br>↓<br><span class="red">MAIOR ATRASO</span></div>`;
  }
  if(i===5){const g=S.INITIAL_STATE[6];f.title='UMA ESCOLHA EM CADA SEMÁFORO';f.focus=6;f.importantNumbers=2;
   f.panel=eyebrow('INTERSEÇÃO 07')+concept('TEMPO DE VERDE')+metric('DIREÇÃO PRINCIPAL',fmt(g*100,0)+'%','green')+metric('DIREÇÃO TRANSVERSAL',fmt((1-g)*100,0)+'%','purple')+note('Frações complementares do mesmo ciclo.');}
  if(i===6){f.title='JUNTAMOS TODAS AS ESCOLHAS';f.panel=concept('UMA CONFIGURAÇÃO<br>COMPLETA DA REDE')+detail('Chamamos essa combinação<br>de <span class="cyan">estado x</span>.');}
  if(i===7){f.title='CADA CONFIGURAÇÃO É UM ESTADO';f.panel=eyebrow('ESTADO x')+`<div class="formula mono cyan">x = (g₁, g₂, …, g₁₆)</div>`+detail('Cada g representa a fração de verde<br>de um semáforo.');}
  if(i===8){f.opacity=.17;f.title='COMO SABER SE UMA CONFIGURAÇÃO É BOA?';f.center=concept('Precisamos comparar<br>as configurações.');}
  if(i===9){f.title='ASSOCIAMOS UM CUSTO A CADA ESTADO';f.panel=concept('UM ESTADO x<br>UM CUSTO E(x)')+metric('CUSTO DESTA CONFIGURAÇÃO',fmt(f.sample.result.energy))+note('Custo adimensional do modelo.');f.importantNumbers=1;}
  if(i===10){f.title='O COMPUTADOR TENTA REDUZIR ESSE CUSTO';f.panel=concept('MENOR E', 'cyan')+detail('↓')+concept('MENOR CUSTO AGREGADO<br>NO MODELO');}
  if(i===11){f.title='CADA VIA CONTRIBUI PARA O CUSTO';f.panel=concept('VIAS COM MAIOR DEMANDA<br>TÊM MAIOR PESO')+`<p class="formula mono">E(x) = Σⱼ wⱼ dⱼ(x) / d<sub>ref</sub></p>`+note('wⱼ = qⱼ / Σₖ qₖ · pesos normalizados<br>dⱼ(x): atraso na via · d_ref: escala fixa');}
  if(i===12){f.title='TEMPERATURA COMPUTACIONAL ALTA';f.subtitle='Muitas configurações são exploradas.';f.importantNumbers=1;f.graphs=1;
   f.panel=eyebrow('EXPLORAÇÃO')+concept('O CUSTO PODE SUBIR<br>E DESCER')+metric('CUSTO ATUAL E(x)',fmt(f.sample.result.energy))+note('T é um parâmetro do algoritmo.<br>Não é a temperatura das ruas.');f.caption='<b>Cada mudança aceita produz uma nova configuração.</b>';
  }
  if(i>=13){f.opacity=.13;f.title='';f.center= i===13?`<div class="hero">POR QUE NÃO ACEITAR<br>APENAS AS MELHORIAS?</div>`:i===14?`<div class="hero">UMA BUSCA GULOSA<br>PODE FICAR PRESA</div>`:`<div class="hero purple">MÍNIMOS LOCAIS</div>${detail('Melhorias pequenas podem não levar a uma saída.')}<p class="note">A próxima animação mostra como o algoritmo decide.</p>`;}
  f.accessible=[f.title,(f.panel||f.center||'').replace(/<[^>]+>/g,' ')].join('. ');return f;
 }
 function draw(ctx,f,t){
  const points=V.map(ctx,network,f.sample.state,f.sample.result,f.scientificTime||t,{focus:f.focus,opacity:f.opacity});
  if(f.phase>=1&&f.phase<=4){const target=f.phase===1?points[6]:{x:(points[5].x+points[6].x)/2,y:(points[5].y+points[6].y)/2};V.line(ctx,1190,406,target.x+40,target.y,C.purple,2);V.dot(ctx,target.x+40,target.y,4,C.purple);}
  if(f.phase===12)V.chart(ctx,engine.history.points.slice(0,f.sample.historyLength),{duration:14,best:false,max:summary.max*1.1,y:684});
 }
 function validatePresentationContract(){
  const samples=phases.map(p=>at(p.start+1)),checks=V.commonContract({duration},samples),check=(ok,label)=>checks.push({label,pass:!!ok});
  check(samples.every(f=>!/(exp\(|P_acc|ACEITAÇÃO|SORTEIO|REJEIÇÕES)/.test(f.panel||'')),'Sem fórmula de Metrópolis ou telemetria prematura');
  check(at(6).phase<at(22).phase&&at(22).phase<at(34).phase,'Ordem: rede, configuração e custo');
  check(at(71).center.includes('MÍNIMOS LOCAIS'),'Fechamento aponta para mínimos locais');
  check(frames.at(-1).t===14&&frames.at(-1).result.energy===summary.final,'Apresentação percorre toda a trajetória original');
  check(frames.every(s=>s.state.values.every(g=>g>=.2&&g<=.8)),'Todos os estados exibidos são estados do motor');
  return {status:checks.every(c=>c.pass)?'PASS':'FAIL',checks,duration,scientificDuration:14};
 }
 const presentationValidation=validatePresentationContract();
 if(presentationValidation.status!=='PASS')throw Error('Falha no contrato da apresentação 02');
 const exportData=()=>({seed:S.CONFIG.seed,network:S.NETWORK_CONFIG,initialState:S.INITIAL_STATE,calibration,summary,finalState:engine.state.values,events:engine.events,history:engine.history.points,validation:scienceValidation,presentationValidation});
 window.validatePresentationContract=validatePresentationContract;
 V.mount({duration,title,phases,at,draw,presentationValidation,scienceValidation,export:exportData,filename:'simulacao-02',api:'Simulation02Experiment',alias:'UrbanSimulation',events:engine.events,history:engine.history.points});
})();
