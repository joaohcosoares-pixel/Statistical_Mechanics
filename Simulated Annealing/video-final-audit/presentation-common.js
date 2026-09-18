/* Presentation only: no proposal, random draw, energy or acceptance is computed here. */
const VideoPresentation = (() => {
 'use strict';
 const C={bg:'#0f111a',text:'#f8f8f2',muted:'#9da8bd',cyan:'#8be9fd',purple:'#bd93f9',green:'#50fa7b',orange:'#ffb86c',red:'#ff6868'};
 const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v)),lerp=(a,b,t)=>a+(b-a)*t;
 const fmt=(v,n=3)=>Number(v).toLocaleString('pt-BR',{minimumFractionDigits:n,maximumFractionDigits:n});
 const signed=(v,n=3)=>(v>0?'+':'')+fmt(v,n);
 const metric=(label,value,color='cyan')=>`<div class="metric"><div class="metric-label">${label}</div><div class="value ${color}">${value}</div></div>`;
 const concept=(text,color='')=>`<h2 class="concept ${color}">${text}</h2>`;
 const detail=text=>`<p class="detail">${text}</p>`;
 const note=text=>`<p class="note">${text}</p>`;
 const eyebrow=text=>`<div class="eyebrow">${text}</div>`;
 const phaseAt=(phases,t)=>phases.findLast(p=>t>=p.start)||phases[0];
 const rgb=h=>[1,3,5].map(i=>parseInt(h.slice(i,i+2),16));
 function delayColor(d){const stops=[[.04,C.cyan],[.09,C.green],[.13,C.orange],[.28,'#ff5555']];let k=1;while(k<3&&d>stops[k][0])k++;const [a,ca]=stops[k-1],[b,cb]=stops[k],f=clamp((d-a)/(b-a)),aa=rgb(ca),bb=rgb(cb);return `rgb(${aa.map((v,i)=>Math.round(lerp(v,bb[i],f))).join(',')})`;}
 function label(ctx,text,x,y,size=22,color=C.muted,align='left'){ctx.fillStyle=color;ctx.font=`${size}px Arial`;ctx.textAlign=align;ctx.fillText(text,x,y);ctx.textAlign='left';}
 function line(ctx,x1,y1,x2,y2,color,width=2){ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.strokeStyle=color;ctx.lineWidth=width;ctx.stroke();}
 function dot(ctx,x,y,r,color){ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fillStyle=color;ctx.fill();}
 function map(ctx,network,state,result,time,{rect={x:85,y:293,w:1065,h:562},focus=-1,opacity=1,particles=true,colorScale=delayColor}={}){
  // Uniform affine transform preserves the canonical coordinates and all angles.
  const scale=Math.min(rect.w/1100,rect.h/650),ox=rect.x+(rect.w-1100*scale)/2,oy=rect.y+(rect.h-650*scale)/2;
  const points=network.nodes.map(n=>({x:ox+n.x*scale,y:oy+n.y*scale}));
  ctx.save();ctx.globalAlpha=opacity;ctx.lineCap='round';
  network.edges.forEach((e,j)=>{
   const a=points[e.a],b=points[e.b],near=focus<0||e.a===focus||e.b===focus,d=result.roads?result.roads[j].delay:result.delays[j];
   ctx.globalAlpha=opacity*(near?1:.14);line(ctx,a.x,a.y,b.x,b.y,'#242b3b',17);line(ctx,a.x,a.y,b.x,b.y,colorScale(d),5);
   if(particles){const count=Math.max(3,Math.round(e.q*17));for(let k=0;k<count;k++){
    const u=(k/count+time*(.035/(1+2*d))+(j*.137)%1)%1;
    dot(ctx,lerp(a.x,b.x,u),lerp(a.y,b.y,u),2.7,'#f4f7ff');}}
  });
  points.forEach((p,i)=>{
   const near=focus<0||i===focus;ctx.globalAlpha=opacity*(near?1:.16);
   if(i===focus){const r=38;const grad=ctx.createRadialGradient(p.x,p.y,5,p.x,p.y,65);grad.addColorStop(0,'#bd93f94a');grad.addColorStop(1,'#bd93f900');ctx.fillStyle=grad;ctx.fillRect(p.x-65,p.y-65,130,130);ctx.strokeStyle=C.purple;ctx.lineWidth=2;ctx.beginPath();ctx.arc(p.x,p.y,r,0,Math.PI*2);ctx.stroke();}
   dot(ctx,p.x,p.y,14,C.bg);ctx.strokeStyle=near?'#7f8ba4':'#394258';ctx.lineWidth=2;ctx.beginPath();ctx.arc(p.x,p.y,14,0,Math.PI*2);ctx.stroke();
   const g=state.values?state.values[i]:state[i],green=((time/4.8+network.nodes[i].offset)%1)<g;
   dot(ctx,p.x-5,p.y,3.7,green?C.green:C.red);dot(ctx,p.x+5,p.y,3.7,green?C.red:C.green);
   if(i===focus)label(ctx,String(i+1).padStart(2,'0'),p.x,p.y+66,26,C.purple,'center');
  });ctx.restore();return points;
 }
 function chart(ctx,points,{x=1230,y=685,w=594,h=180,duration=16,best=true,highlight='',max=1.1}={}){
  const px=t=>x+clamp(t/duration)*w,py=e=>y+h-clamp(e/max)*h;
  ctx.save();ctx.lineCap='round';
  for(let k=0;k<=2;k++){const yy=y+k*h/2;line(ctx,x,yy,x+w,yy,'#293044',1);}
  const draw=(key,color,width)=>{ctx.beginPath();points.forEach((p,i)=>{if(i)ctx.lineTo(px(p.t),py(p[key]));else ctx.moveTo(px(p.t),py(p[key]));});ctx.lineWidth=width;ctx.strokeStyle=color;ctx.stroke();};
  draw('e',C.cyan,3);if(best)draw('best',C.green,4);
  const last=points.at(-1);if(last){dot(ctx,px(last.t),py(last.e),5,C.cyan);if(best)dot(ctx,px(last.t),py(last.best),5,C.green);
   if(highlight){const key=highlight==='best'?'best':'e',color=key==='best'?C.green:C.cyan;ctx.strokeStyle=color;ctx.lineWidth=2;ctx.beginPath();ctx.arc(px(last.t),py(last[key]),13,0,Math.PI*2);ctx.stroke();}}
  label(ctx,'início',x,y+h+28,17);label(ctx,'fim da execução',x+w,y+h+28,17,C.muted,'right');label(ctx,'E',x-18,y+6,18);
  ctx.restore();
 }
 function ruler(ctx,P,u,{x=1230,y=688,w=594,showU=false,showTest=false,decision=null,stationary=false}={}){
  ctx.save();ctx.fillStyle='#33303e';ctx.fillRect(x,y,w,30);ctx.fillStyle='#50fa7b99';ctx.fillRect(x,y,w*P,30);
  label(ctx,'0',x,y+61,20);label(ctx,'1',x+w,y+61,20,C.muted,'right');
  label(ctx,'ACEITA',x,y+99,20,C.green);label(ctx,'REJEITA',x+w,y+99,20,C.red,'right');
  line(ctx,x+w*P,y-28,x+w*P,y+34,C.green,3);
  label(ctx,`P = ${fmt(P)}`,x+w*P,y-44,22,C.green,'center');
  if(showU){const ux=x+w*u;line(ctx,ux,y+32,ux,y+123,C.purple,3);dot(ctx,ux,y+15,7,C.purple);label(ctx,`u = ${fmt(u)}${stationary?' · não muda':''}`,ux,y+154,22,C.purple,'center');}
  if(showTest)label(ctx,decision===null?(u<P?'u < P':'u ≥ P'):(decision?'✓ ACEITAR':'× REJEITAR'),x+w/2,y+215,36,decision===null?C.text:decision?C.green:C.red,'center');
  ctx.restore();
 }
 function commonContract(spec,frames){
  const checks=[];const check=(ok,label)=>{checks.push({label,pass:!!ok});};
  check(document.documentElement.lang==='pt-BR','Idioma da apresentação: português');
  check(document.querySelectorAll('#scene').length===1,'Um único Canvas de apresentação');
  check(!document.querySelector('script[src],link[rel="stylesheet"]'),'Sem bibliotecas ou folhas externas');
  check(frames.every(f=>!/(URBAN NETWORK|INITIAL STATE|HIGH.T EXPLORATION|ACCEPTANCE RATE|CURRENT ENERGY|BEST ENERGY FOUND|RUNNING MINIMUM)/.test([f.title,f.subtitle,f.panel,f.center,f.caption].join(' '))),'Conceitos visíveis em português');
  check(frames.every(f=>(f.graphs||0)<=1&&(f.pair||(f.importantNumbers||0)<=3)),'Até um gráfico e três números principais; exceção explícita para a comparação pareada');
  const styles=[...document.styleSheets].flatMap(s=>[...s.cssRules].map(r=>r.cssText)).join('\n');
  check(styles.includes('.recording #controls')&&styles.includes('display: none !important'),'Controles ocultos no modo de gravação');
  check(styles.includes('cursor: none !important'),'Cursor oculto em toda a gravação');
  check(frames.every(f=>!/(ÓTIMO GLOBAL|SOLUÇÃO ÓTIMA|MELHOR CONFIGURAÇÃO POSSÍVEL)/.test([f.title,f.panel,f.center].join(' ').replaceAll('SEM GARANTIA DE ÓTIMO GLOBAL',''))),'Sem promessa de ótimo global');
  return checks;
 }
 function mount(spec){
  const $=id=>document.getElementById(id),params=new URLSearchParams(location.search),canvas=$('scene'),ctx=canvas.getContext('2d');
  let recording=params.has('recording')?params.get('recording')!=='0':spec.mode==='video',time=clamp(Number(params.get('t'))||0,0,spec.duration),running=params.has('autoplay')?params.get('autoplay')==='1':recording,last=performance.now(),lastPhase='',lastHUD=-Infinity;
  const setRecording=v=>{recording=v;document.body.classList.toggle('recording',v);$('controls').inert=v;$('debug').hidden=true;$('inspect').setAttribute('aria-expanded','false');};
  setRecording(recording);$('seek').max=spec.duration;
  $('mode').value=spec.mode;
  $('mode').onchange=()=>{const url=new URL(location.href);url.searchParams.set('mode',$('mode').value);url.searchParams.set('recording','0');url.searchParams.set('autoplay','0');url.searchParams.delete('t');location.href=url.href;};
  spec.phases.forEach(p=>{const o=document.createElement('option');o.value=p.start;o.textContent=p.name;$('chapters').append(o);});
  function resize(){const s=Math.min(innerWidth/1920,innerHeight/1080),stage=$('stage');stage.style.transform=`scale(${s})`;stage.style.left=(innerWidth-1920*s)/2+'px';stage.style.top=(innerHeight-1080*s)/2+'px';}
  function setHTML(el,html){if(el.innerHTML!==html)el.innerHTML=html;}
  function render(force=false){
   const f=spec.at(time),phase=phaseAt(spec.phases,time);ctx.clearRect(0,0,1920,1080);spec.draw(ctx,f,time);
   if(force||time-lastHUD>=.1||lastPhase!==phase.name||!running){
    $('title').textContent=f.title??spec.title;$('subtitle').textContent=f.subtitle||'';
    $('contextNote').textContent=spec.context||'';
    setHTML($('panel'),f.panel||'');setHTML($('center'),f.center||'');$('center').className=f.centerClass||'';
    $('panel').hidden=!f.panel;$('center').hidden=!f.center;setHTML($('mapCaption'),f.caption||'');
    $('chapterLabel').textContent=phase.name;$('clock').textContent=fmt(time,1)+' / '+fmt(spec.duration,1)+' s';
    if(document.activeElement!==$('seek'))$('seek').value=time.toFixed(1);
    $('chapters').value=phase.start;$('play').textContent=running?'Pausar':'Reproduzir';$('play').setAttribute('aria-label',running?'Pausar animação':'Reproduzir animação');lastHUD=time;
   }
   // Gentle entry belongs to presentation time, never to the scientific clock.
   const enter=clamp((time-phase.start)/.45);$('panel').style.opacity=.35+.65*enter;$('center').style.opacity=.35+.65*enter;
   $('progress').style.width=1920*time/spec.duration+'px';
   canvas.setAttribute('aria-label',f.accessible||'Rede conceitual: cores indicam atraso do modelo; pontos são fluxo ilustrativo.');
   $('stage').dataset.phase=phase.name;$('stage').dataset.time=time.toFixed(3);$('stage').dataset.scientificTime=String(f.scientificTime??'');
   $('stage').dataset.decision=f.decision===undefined?'':String(f.decision);$('stage').dataset.validation=spec.presentationValidation.status;
   $('stage').dataset.mode=spec.mode;$('stage').dataset.duration=String(spec.duration);$('stage').dataset.probability=f.showRuler?String(f.P):'';$('stage').dataset.draw=f.showU?String(f.u):'';$('stage').dataset.drawPosition=f.showU?String(1230+594*f.u):'';
   if(lastPhase!==phase.name){$('status').textContent=phase.name+'. '+(f.accessible||'');lastPhase=phase.name;}
  }
  function seek(t){time=clamp(t,0,spec.duration);lastHUD=-Infinity;last=performance.now();render(true);}
  function frame(now){const dt=Math.max(0,(now-last)/1000);last=now;if(running){time=Math.min(spec.duration,time+dt);if(time>=spec.duration)running=false;}render();requestAnimationFrame(frame);}
  $('play').onclick=()=>{if(time>=spec.duration)seek(0);running=!running;last=performance.now();render(true);};
  $('restart').onclick=()=>{running=true;seek(0);};
  // Respond while editing as well as on commit; a frame must never erase a
  // newly typed time before the field's change event is delivered.
  const seekInput=()=>{running=false;seek(Number($('seek').value)||0);};
  $('seek').oninput=seekInput;$('seek').onchange=seekInput;
  $('chapters').onchange=()=>{running=false;seek(Number($('chapters').value));};
  $('record').onclick=()=>{setRecording(true);running=true;seek(0);};
  $('inspect').onclick=()=>{const open=$('debug').hidden;$('debug').hidden=!open;$('inspect').setAttribute('aria-expanded',String(open));$('debug').textContent=JSON.stringify({apresentacao:spec.presentationValidation,modos:spec.modeValidations,ciencia:spec.scienceValidation},null,2);};
  $('export').onclick=()=>{const blob=new Blob([JSON.stringify(spec.export(),null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=spec.filename+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
  document.addEventListener('keydown',e=>{if(['INPUT','SELECT','BUTTON'].includes(document.activeElement.tagName)&&e.code!=='Escape')return;if(e.code==='Space'){e.preventDefault();$('play').click();}if(e.code==='KeyR')$('restart').click();if(e.code==='Escape'){running=false;setRecording(false);render(true);}if(!recording&&e.code==='ArrowRight'){running=false;seek(time+1);}if(!recording&&e.code==='ArrowLeft'){running=false;seek(time-1);}});
  document.addEventListener('visibilitychange',()=>{last=performance.now();});
  addEventListener('resize',resize);resize();render(true);requestAnimationFrame(frame);
  const api=Object.freeze({snapshot:()=>JSON.parse(JSON.stringify({...spec.export(),presentationModes:spec.modeValidations,playback:{time,running,recording,mode:spec.mode,duration:spec.duration,phase:phaseAt(spec.phases,time).name}})),presentation:()=>JSON.parse(JSON.stringify(spec.modeValidations)),events:()=>JSON.parse(JSON.stringify(spec.events||[])),history:()=>JSON.parse(JSON.stringify(spec.history||[]))});
  window[spec.api]=api;if(spec.alias)window[spec.alias]=api;
  return api;
 }
 return {C,clamp,lerp,fmt,signed,metric,concept,detail,note,eyebrow,phaseAt,map,chart,ruler,label,line,dot,delayColor,commonContract,mount};
})();
