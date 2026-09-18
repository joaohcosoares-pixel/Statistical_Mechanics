"""Embed presentation sources around the byte-identical, captured scientific cores."""
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
STYLE = r'''
:root{color-scheme:dark;--bg:#0f111a;--text:#f8f8f2;--muted:#9da8bd;--cyan:#8be9fd;--purple:#bd93f9;--green:#50fa7b;--orange:#ffb86c;--red:#ff6868}
*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#090b11;color:var(--text);font-family:Arial,Helvetica,sans-serif}
#stage{position:absolute;width:1920px;height:1080px;overflow:hidden;transform-origin:top left;background:var(--bg)}canvas{position:absolute;inset:0;width:1920px;height:1080px}
header{position:absolute;left:76px;right:76px;top:50px;display:flex;justify-content:space-between;align-items:flex-start}header .series{color:var(--purple);font-size:16px;letter-spacing:2px;margin-bottom:20px}h1{font-size:46px;line-height:1.13;letter-spacing:-1.3px;font-weight:500;margin:0;max-width:1550px}#subtitle{font-size:25px;line-height:1.4;margin-top:18px;color:var(--muted)}.event{text-align:right;color:var(--muted);font-size:14px;line-height:1.7;letter-spacing:1px}.event b{color:var(--cyan);font-size:28px;letter-spacing:4px;font-weight:400}
.mono,.value{font-family:Consolas,'Liberation Mono',monospace;font-variant-numeric:tabular-nums}.cyan{color:var(--cyan)}.purple{color:var(--purple)}.green{color:var(--green)}.orange{color:var(--orange)}.red{color:var(--red)}.muted{color:var(--muted)}
#panel{position:absolute;left:1230px;top:302px;width:604px}#center{position:absolute;left:160px;right:160px;top:330px;text-align:center}#center.flow{top:294px}#center .concept{font-size:44px;line-height:1.3}#center .hero{font-size:64px;line-height:1.25;font-weight:500;letter-spacing:-1px}#center .detail{font-size:27px}.eyebrow{font-size:20px;letter-spacing:1.4px;margin:0 0 22px;color:var(--purple)}.concept{font-size:38px;line-height:1.28;font-weight:500;margin:0 0 25px;letter-spacing:-.4px}.detail{font-size:25px;line-height:1.5;color:var(--muted);margin:22px 0}.formula{font-size:30px;line-height:1.5;margin:28px 0}.note{font-size:16px;color:var(--muted);line-height:1.5}.value{font-size:58px;font-weight:400;line-height:1.15}.metric-label{font-size:20px;letter-spacing:.7px;margin-bottom:12px}.metric{margin-bottom:28px}.two{display:flex;gap:50px}.two>.metric{flex:1}.two .value{font-size:50px}.separator{height:1px;background:#2a3040;margin:30px 0}.big-symbol{font-size:94px;margin:12px 0 26px}.arrow{color:var(--muted);padding:0 32px;font-size:44px}.flow-row{display:flex;align-items:center;justify-content:center;gap:60px;margin:40px 0 54px}.flow-row small{display:block;font:22px Arial,sans-serif;color:var(--muted);margin-top:18px}.flow-row .symbol{font-size:100px}.pill{border-left:4px solid var(--purple);padding-left:24px;margin:32px 0}.comparison{display:flex;gap:140px;justify-content:center;text-align:left;margin:30px auto 0}.comparison>div{width:600px}.comparison .concept{font-size:38px}.comparison .value{font-size:52px}.summary{display:flex;justify-content:center;gap:100px;margin-top:55px}.summary>div{width:380px;text-align:left}.summary .metric-label{height:54px}.summary .value{font-size:54px}.bar{height:12px;border-radius:6px;background:#2a3040;overflow:hidden;margin:18px 0 34px}.bar>span{display:block;height:100%;background:var(--orange)}
#mapCaption{position:absolute;left:92px;top:897px;color:var(--muted);font-size:18px;line-height:1.5;max-width:1050px}#mapCaption b{font-weight:400;color:var(--cyan)}footer{position:absolute;left:76px;right:76px;bottom:38px;display:flex;justify-content:space-between;font-size:15px;line-height:1.5;color:#8c98ae;border-top:1px solid #252b3b;padding-top:22px}#progress{position:absolute;bottom:0;height:3px;background:var(--purple);opacity:.7}#controls{position:absolute;bottom:100px;left:76px;right:76px;display:flex;align-items:center;gap:12px;padding:14px 18px;background:#151a28f5;border:1px solid #384058;border-radius:8px;font-size:17px;z-index:5}button,input,select{font:inherit;color:var(--text);border:1px solid #455069;background:#202737;border-radius:5px;padding:9px 12px}button{cursor:pointer}button:hover{border-color:var(--cyan)}:focus-visible{outline:3px solid var(--cyan);outline-offset:4px}#seek{width:106px}#chapters{max-width:360px}#clock{margin-left:auto;white-space:nowrap}.recording,.recording *{cursor:none!important;user-select:none!important}.recording #controls,.recording #debug{display:none!important;visibility:hidden!important;pointer-events:none!important}#debug{position:absolute;z-index:9;inset:220px 120px 170px;background:#111725f7;border:1px solid var(--purple);padding:32px;overflow:auto;font:16px/1.6 Consolas,monospace;white-space:pre-wrap}#debug[hidden],[hidden]{display:none!important}.sr-only{position:absolute!important;width:1px;height:1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap}#error{position:absolute;z-index:20;left:200px;right:200px;top:400px;background:#30202b;padding:40px;border:2px solid var(--red);font-size:24px}
'''
for n, title, filename in [(2,'O que o computador está tentando melhorar?','Simulation2_UrbanLattice.html'),(3,'Como o algoritmo decide?','Simulation3_Metropolis.html'),(4,'O que acontece quando resfriamos?','Simulation4_Convergence.html')]:
    old = (HERE/'before'/filename).read_text()
    model = re.search(r'<script id="model">([\s\S]*?)</script>',old).group(1)
    common=(HERE/'presentation-common.js').read_text()
    scene=(HERE/f'presentation-{n}.js').read_text()
    html=f'''<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Animação didática de recozimento simulado, com modelo conceitual e dados sintéticos. Funciona sem conexão."><link rel="icon" href="data:,">
<title>Simulação 0{n} · {title} — UFG</title><style>{STYLE}</style></head>
<body><main id="stage" aria-label="Simulação 0{n}: {title}">
<canvas id="scene" width="1920" height="1080" role="img" aria-label="Rede urbana conceitual, com cores que indicam o atraso do modelo e pontos de fluxo ilustrativo">Os estados e resultados desta animação são descritos no texto da cena.</canvas>
<header><div><div class="series">SIMULAÇÃO 0{n} · RECOZIMENTO SIMULADO</div><h1 id="title">{title}</h1><div id="subtitle"></div></div><div class="event"><b>UFG</b><br>XLIII SEMANA<br>DA FÍSICA</div></header>
<section id="panel" aria-label="Explicação da cena"></section><section id="center" aria-label="Ideia principal"></section><div id="mapCaption"></div>
<footer><span>MODELO CONCEITUAL · DADOS SINTÉTICOS · REDE NÃO GEORREFERENCIADA</span><span id="chapterLabel"></span></footer><div id="progress"></div>
<nav id="controls" aria-label="Controles da animação"><button id="play">Reproduzir</button><button id="restart">Reiniciar</button><label>Tempo <input id="seek" type="number" min="0" step="0.1" value="0" aria-label="Tempo da apresentação em segundos"></label><label>Cena <select id="chapters" aria-label="Escolher cena"></select></label><button id="record">Gravar do início</button><button id="export">Exportar JSON</button><button id="inspect" aria-expanded="false">Validações</button><span id="clock" class="mono"></span></nav>
<pre id="debug" hidden aria-label="Relatório de validação"></pre><p id="status" class="sr-only" role="status" aria-live="polite"></p><div id="error" role="alert" hidden></div>
</main>
<script id="model">{model}</script>
<script id="presentation-common">{common}</script>
<script id="presentation">{scene}</script>
</body></html>
'''
    (ROOT/filename).write_text(html)

old=(HERE/'before'/'transitSimulation.html').read_text()
changes={
'02 · Rede urbana / Estado inicial — XLIII Semana da Física':'Modelo alternativo de tráfego — Demonstração complementar',
'Simulação 02: rede urbana e recozimento simulado':'Modelo alternativo de tráfego: demonstração complementar',
'SIMULAÇÃO 02 / RECOZIMENTO SIMULADO':'MODELO ALTERNATIVO DE TRÁFEGO',
'Rede urbana <span>// Estado inicial</span>':'Demonstração complementar',
'Mecânica estatística × mobilidade urbana':'NÃO FAZ PARTE DA CADEIA SIMULAÇÃO 02 → 03 → 04 → 05',
"set('04 / PRÓXIMA CENA','Como o<br>algoritmo decide?','Simulação 03<br>Metrópolis em tempo real.')":"set('04 / DEMONSTRAÇÃO COMPLEMENTAR','Modelo alternativo<br>de tráfego.','Fora da sequência<br>principal 02 → 03 → 04 → 05.')",
"a.download='simulation-02.json'":"a.download='transito-modelo-alternativo.json'"
}
for a,b in changes.items():
    assert a in old,a
    old=old.replace(a,b)
(ROOT/'transitSimulation_legacy.html').write_text(old)
