from pathlib import Path
import re

D=Path(__file__).resolve().parent;R=D.parent
def script(text,id):return re.search(r'<script id="'+id+r'"[^>]*>[\s\S]*?</script>',text).group(0)
def contents(text,id):return script(text,id).split('>',1)[1].rsplit('</script>',1)[0]
common=(D/'presentation-common.js').read_text(); modes=(D/'presentation-modes.js').read_text()
extra_css='''
#contextNote{font-size:16px;color:#929fb5;margin-top:14px;letter-spacing:.3px}.metric-label{font-size:23px}.eyebrow{font-size:23px}.series{font-size:16px!important}#mode{width:125px}#controls{gap:10px;padding:12px;font-size:16px}#chapters{max-width:310px}#clock{font-size:15px}.network-key{font-size:27px;line-height:1.9;color:var(--muted)}#center.comparison05{left:92px;right:92px;top:257px;text-align:left}.compare-05{display:grid;grid-template-columns:1fr 1fr;gap:150px}.compare-05 h2{font-size:30px;line-height:1.3;min-height:78px;margin:12px 0}.compare-05 .eyebrow{margin-bottom:12px}.compare-05 .metric{margin-top:465px}.compare-05 .value{font-size:56px}.compare-05 .metric-label{font-size:24px}.comparison-note{position:absolute;top:928px;left:94px;right:94px;font-size:16px;color:var(--muted)}
'''
template=(D/'before/Simulation2_UrbanLattice.html').read_text().split('<script id="model">')[0]
for n,filename,title in [(2,'Simulation2_UrbanLattice.html','O que o computador está tentando melhorar?'),(3,'Simulation3_Metropolis.html','Como o algoritmo decide?'),(4,'Simulation4_Convergence.html','O que acontece quando resfriamos?'),(5,'index.html','O algoritmo melhorou o modelo?')]:
    before=(D/'before'/filename).read_text()
    if n<5:head=before.split('<script id="model">')[0]; cores=script(before,'model');full=contents(before,'presentation').replace('V.mount({',f'VideoModes.mount({n},{{')
    else:
        head=template.replace('Simulação 02','Simulação 05').replace('SIMULAÇÃO 02','SIMULAÇÃO 05').replace('O que o computador está tentando melhorar?',title)
        cores='\n'.join(script(before,k) for k in ['simulation04-reference','scientific-core','model']);full=(D/'presentation-5.js').read_text()
    head=head.replace('</style>',extra_css+'\n</style>').replace('<div id="subtitle"></div>','<div id="subtitle"></div><div id="contextNote"></div>')
    head=head.replace('<button id="play">','<label>Versão <select id="mode" aria-label="Versão da apresentação"><option value="video">Vídeo</option><option value="full">Completa</option></select></label><button id="play">')
    if n==5:
        head=head.replace('O que o computador está tentando melhorar?',title)
        head=head.replace('</style>','#center.comparison05 .concept{font-size:36px;min-height:94px}.compare-05 section{position:relative;height:685px}.compare-05 .metric{position:absolute;top:580px;margin:0}#stage:has(.comparison05) #mapCaption{top:960px;font-size:16px}</style>')
    (R/filename).write_text(head+cores+'\n<script id="presentation-common">'+common+'</script>\n<script id="presentation-modes">'+modes+'</script>\n<script id="presentation">'+full+'</script>\n</body></html>\n')

legacy=(D/'before/transitSimulation.html').read_text()
for a,b in {
'02 · Rede urbana / Estado inicial — XLIII Semana da Física':'Modelo alternativo de tráfego — Demonstração complementar',
'Simulação 02: rede urbana e recozimento simulado':'Modelo alternativo de tráfego: demonstração complementar',
'SIMULAÇÃO 02 / RECOZIMENTO SIMULADO':'MODELO ALTERNATIVO DE TRÁFEGO',
'Rede urbana <span>// Estado inicial</span>':'Demonstração complementar',
'Mecânica estatística × mobilidade urbana':'NÃO UTILIZADO NA CADEIA PRINCIPAL DO VÍDEO',
"set('04 / PRÓXIMA CENA','Como o<br>algoritmo decide?','Simulação 03<br>Metrópolis em tempo real.')":"set('04 / DEMONSTRAÇÃO COMPLEMENTAR','Modelo alternativo<br>de tráfego.','Não utilizado na cadeia<br>principal do vídeo.')",
"a.download='simulation-02.json'":"a.download='transito-modelo-alternativo.json'",
"const RECORDING_MODE = true;":"const RECORDING_MODE = new URLSearchParams(location.search).get('recording') !== '0';"
}.items():
    assert a in legacy,a
    legacy=legacy.replace(a,b)
legacy=legacy.replace('</style>','.capture,.capture *{cursor:none!important;user-select:none!important}.capture #controls,.capture #debugPanel,.capture .timeline{display:none!important}body:has(.capture){cursor:none!important}</style>')
(R/'transitSimulation_legacy.html').write_text(legacy)
