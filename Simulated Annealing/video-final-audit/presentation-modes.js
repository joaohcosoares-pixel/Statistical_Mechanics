/* Editorial clocks only. All frames still refer to the original scientific data. */
const VideoModes=(()=>{
 'use strict';
 const V=VideoPresentation,{concept,detail,note,eyebrow,metric,fmt}=V;
 const phases=rows=>rows.map(([start,name])=>({start,name}));
 const segment=(t,a,b,c,d)=>V.lerp(c,d,V.clamp((t-a)/(b-a)));
 function wrap(full,duration,rows,sourceTime,edit=()=>{}){
  return {...full,duration,phases:phases(rows),at(t){const source=sourceTime(V.clamp(t,0,duration)),f=full.at(source);f.sourceTime=source;edit(f,t);f.accessible=[f.title,f.subtitle,(f.panel||f.center||'').replace(/<[^>]+>/g,' '),f.showRuler?`P = ${fmt(f.P)}.${f.showU?' Sorteio u = '+fmt(f.u):''}`:'',f.caption||''].join('. ');return f;},draw(ctx,f,t){full.draw(ctx,f,f.sourceTime);}};
 }
 function video02(full){
  const time=t=>t<3?1:t<9?6:t<15?16:t<17?22:t<20?25:t<22?29:t<24.5?33:t<27?37:t<32?42:t<36?45+(t-32)*4:62;
  return wrap(full,40,[[0,'O que melhorar?'],[3,'Como ler a rede'],[9,'Um semáforo'],[15,'Estado x'],[20,'Custo E(x)'],[27,'Pesos das vias'],[32,'Exploração com T alta'],[36,'Por que só melhorias?']],time,(f,t)=>{
   if(t>=3&&t<9){f.title='REDE URBANA SIMPLIFICADA';f.focus=-1;f.phase=6;f.panel=eyebrow('COMO LER A REDE')+`<div class="network-key"><span class="purple">●</span> Interseção / semáforo<br><span class="cyan">━</span> Via<br>Cor → atraso no modelo<br>Pontos → fluxo ilustrativo</div>`+note('Os pontos não são veículos simulados.');}
   if(t>=22&&t<24.5)f.panel+=note('E é chamada de energia por analogia.<br>Aqui, é uma função objetivo adimensional.');
   if(t>=36){f.title='';f.center='<div class="hero">POR QUE NÃO ACEITAR<br>APENAS AS MELHORIAS?</div>';f.caption='';}
  });
 }
 function video03(full){
  const time=t=>t<1.5?1:t<3?4:t<4.5?8:t<6?12:t<8.5?16:t<12?20:t<13?24:t<15?28:t<17?32:t<18?36:t<20?39:t<23?42:t<25?47:t<28?51:t<31?56:t<34?61:t<39?66:t<44?70:t<52?75+(t-44):t<54?86:t<56?88:t<58?92:108;
  return wrap(full,60,[[0,'Uma proposta e seu custo'],[6,'Melhora: aceitar'],[12,'Novo teste: custo maior'],[18,'Uma piora pode ser aceita'],[25,'Limite P e sorteio u'],[34,'T alta: aceita'],[39,'Só T muda'],[44,'Reduzindo T'],[52,'T baixa: rejeita'],[56,'Exploração e seleção'],[58,'Resfriar aos poucos']],time,(f,t)=>{
   if(t>=56&&t<58)f.center=f.center.replace('P MAIOR','MAIS EXPLORAÇÃO').replace('P MENOR','MAIS SELEÇÃO');
  });
 }
 function video04(full){
  const time=t=>t<4?t:t<7?segment(t,4,7,4,8):t<10?segment(t,7,10,8,13):t<18?segment(t,10,18,13,21):t<27?segment(t,18,27,21,32):t<31?segment(t,27,31,32,40):t<32?segment(t,31,32,40,45):t<35?47:55;
  return wrap(full,38,[[0,'O que acontece ao resfriar?'],[4,'Custo atual e melhor custo'],[10,'T alta: exploração'],[18,'Resfriamento'],[27,'T baixa: seleção'],[32,'Melhor resultado'],[35,'Redução do custo']],time,(f,t)=>{
   if(t>=4&&t<10){f.panel=`<div class="two">${metric('CUSTO ATUAL',fmt(f.sample.result.energy),'cyan')}${metric('MELHOR CUSTO',fmt(f.sample.best),'green')}</div>`;f.importantNumbers=2;f.opacity=.40;}
   if(t>=32&&t<35){const d=full.export();f.subtitle='Guardamos a melhor configuração visitada.';f.center=concept('CUSTO E(x)')+`<div class="summary"><div>${metric('ESTADO INICIAL',fmt(d.initialEnergy),'cyan')}</div><div>${metric('MELHOR ESTADO<br>ENCONTRADO',fmt(d.bestEnergy),'green')}</div></div>`+note('EXECUÇÃO FINITA · DADOS SINTÉTICOS');f.importantNumbers=2;}
   if(t>=35){f.subtitle='A seguir: antes e depois na mesma rede.';f.center=f.center.replace('Resultado de uma execução finita com dados sintéticos.','EXECUÇÃO FINITA · DADOS SINTÉTICOS');}
  });
 }
 function validateVideo(id,video,full){
  const samples=Array.from({length:Math.round(video.duration*10)+1},(_,i)=>video.at(i/10)),checks=V.commonContract(video,samples),check=(ok,label)=>checks.push({label,pass:!!ok});
  const text=f=>[f.title,f.subtitle,f.panel,f.center,f.caption].join(' '),ranges={2:[35,42],3:[50,62],4:[30,40],5:[12,18]};
  check(video.duration>=ranges[id][0]&&video.duration<=ranges[id][1],'Duração dentro do intervalo solicitado');
  if(id===2){
   check(samples.every(f=>!/(MÍNIMOS LOCAIS|BUSCA GULOSA|exp\(|P_acc|SORTEIO|METRÓPOLIS)/i.test(text(f))),'02: nenhuma explicação de mínimos locais ou Metrópolis');
   check(video.at(40).center.includes('POR QUE NÃO ACEITAR<br>APENAS AS MELHORIAS?'),'02: termina na pergunta, sem respondê-la');
   check(video.at(40).scientificTime===14&&video.at(40).sample.result.energy===full.at(73).sample.result.energy,'02: trajetória inteira preservada, sem substituir o estado');
  }
  if(id===3){
   check(samples.filter((f,i)=>i/10>=6&&i/10<12).every(f=>f.T===null&&f.P===null&&f.u===null&&!f.showRuler),'03: melhora sem T, P, u ou régua');
   check(video.at(26).showRuler&&!video.at(26).showU&&video.at(29).showU,'03: P aparece antes de u');
   const transition=Array.from({length:121},(_,i)=>video.at(44+i*8/120)),first=transition[0],p=first.event;
   check(transition.every(f=>f.event===p&&f.event.currentState===p.currentState&&f.state===p.candidateState&&f.event.delta===p.delta&&f.u===p.u&&f.mapTime===0),'03: mesmos x, x′, ΔE e u durante a transição');
   check(transition.every((f,i)=>f.P===Math.exp(-p.delta/f.T)&&(!i||f.P<=transition[i-1].P)),'03: somente T altera P');
   check(transition.every(f=>1230+594*f.u===1230+594*p.u),'03: posição de u fixa na régua');
   check(video.at(35).decision===true&&video.at(53).decision===false,'03: T alta aceita e T baixa rejeita');
   check(video.at(41).center.includes('novo sorteio'),'03: reutilização de u explicitamente pedagógica');
   check(video.at(51.9).decision===undefined&&video.at(55).state===p.currentState,'03: rejeição só após a transição; x preservado');
  }
  if(id===4){
   const d=full.export(),f=video.at(38);let best=Infinity;
   check(full.history.every(p=>{best=Math.min(best,p.e);return p.best===best;}),'04: melhor custo é o mínimo acumulado');
   check(full.history.some((p,i)=>i&&p.e>full.history[i-1].e),'04: custo atual pode subir');
   check(d.N===1920&&full.events.length===1920&&d.coolingSchedule==='geometric','04: 1920 propostas e schedule geométrico preservados');
   check(JSON.stringify(Array.from(f.mapState))===JSON.stringify(d.bestState)&&f.mapResult.energy===d.bestEnergy,'04: fechamento usa bestState, não finalState');
   check('finalState' in d&&'bestState' in d&&'finalEnergy' in d&&'bestEnergy' in d,'04: estado final e melhor permanecem separados');
   check(video.at(32).scientificTime===16,'04: toda a trajetória termina antes do fechamento');
  }
  if(id===5){
   const d=full.export();check(d.compatibility.status==='PASS','05: contrato 04 → 05 aprovado');
   check(samples.every(f=>(f.importantNumbers||0)<=3),'05: até três métricas relevantes');
   check(video.at(4).showBefore&&!video.at(4).showAfter&&video.at(8).showBefore&&video.at(8).showAfter,'05: antes, depois e resultado em ordem');
   check(video.at(8).beforeScale===video.at(8).afterScale,'05: uma única escala fixa para os dois mapas');
   check(!/(INITIAL CONFIGURATION|MICROSTATE|CRITICAL SEGMENTS|CONGESTION PROXY)/.test(samples.map(text).join(' ')),'05: sem inglês ou telemetria avançada na tela');
   check(d.validation.checks.energyReduction&&d.validation.checks.meanReduction,'05: reduções calculadas e validadas');
  }
  return {status:checks.every(x=>x.pass)?'PASS':'FAIL',duration:video.duration,checks,sampledFrames:samples.length};
 }
 function mount(id,full){
  const video=id===2?video02(full):id===3?video03(full):id===4?video04(full):full.video;
  const validations={full:full.presentationValidation,video:validateVideo(id,video,full)};
  if(Object.values(validations).some(v=>v.status!=='PASS'))throw Error('Contrato de apresentação inválido: '+JSON.stringify(validations));
  const mode=new URLSearchParams(location.search).get('mode')==='full'?'full':'video',selected=mode==='full'?full:video;
  const originalExport=full.export;
  const spec={...selected,mode,modeValidations:validations,presentationValidation:validations[mode],context:id===3?'EXPERIMENTO DIDÁTICO CONTROLADO NO MESMO MODELO URBANO':id===4?'EXECUÇÃO COMPLETA DO RECOZIMENTO':id===5?'RESULTADO DA MESMA EXECUÇÃO DA SIMULAÇÃO 04':'',export:()=>({...originalExport(),presentationModes:validations})};
  window.validatePresentationContract=()=>JSON.parse(JSON.stringify(validations));
  console.info(`SIMULAÇÃO 0${id}\nVALIDAÇÃO CIENTÍFICA: PASS\nAPRESENTAÇÃO COMPLETA: ${validations.full.status}\nAPRESENTAÇÃO PARA VÍDEO: ${validations.video.status}`);
  return V.mount(spec);
 }
 return {mount,validateVideo,video02,video03,video04};
})();
