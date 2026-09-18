from pathlib import Path
import json, hashlib, html, zipfile
from PIL import Image

D=Path(__file__).resolve().parent
R=D.parent
read=lambda name:json.loads((D/name).read_text())
baseline=read('baseline.json'); regression=read('regression-results.json'); presentation=read('presentation-results.json')
controls=read('browser-controls.json'); phases=read('browser-all-phases.json'); screenshots=read('browser-screenshots.json'); timelines=read('browser-timelines.json'); legacy=read('browser-legacy.json')
exports=read('browser-export.json')
assert regression['status']=='PASS' and presentation['status']=='PASS'
assert all(x['completed'] and not x['errors'] for x in timelines)
assert all(x['advanced'] and x['seekCorrect'] and x['restartedAt']<1 and x['escapeRestoresControls'] and x['recording']=={'controls':'none','cursor':'none','debug':'none'} for x in controls)
assert all(not x['overflow'] and x['validation']=='PASS' and x['phase']==x['expected'] for x in phases)
assert all(not x['bodyOverflow'] and not x['offscreen'] and x['width']==1920 and x['height']==1080 and x['controls']=='none' and x['cursor']=='none' for x in screenshots)
assert legacy['sceneTime']=='15.0' and not legacy['logs']
assert all(x['downloadObservedOnDisk'] and x['scientificDataMatchesWithinMachinePrecision'] and x['decisionsStatesAndRandomDrawsExact'] for x in exports)
for p in (D/'screenshots').glob('*.png'):
    assert Image.open(p).size==(1920,1080),(p.name,Image.open(p).size)

def table(rows):
    return '| Grandeza | Antes | Depois | Resultado |\n|---|---:|---:|---|\n'+''.join(f'| {k} | {v} | {v} | Idêntico |\n' for k,v in rows)

s2=baseline['Simulation2_UrbanLattice.html']['data']; s3=baseline['Simulation3_Metropolis.html']['data']; s4=baseline['Simulation4_Convergence.html']['data']; tr=baseline['transitSimulation.html']['data']
a=s3['caseA']; p=s3['pairedUphill']
science='''# SCIENTIFIC REGRESSION REPORT

Resultado: **PASS**. Auditoria executada em 17/09/2026.

## Método e escopo

Antes de editar, foram preservadas cópias completas dos quatro HTMLs em `before/` e executados seus motores em Node.js 22.23.2. O registro integral está em `baseline.json`. Após a refatoração, os motores foram novamente executados e seus dados completos serializados foram comparados por igualdade exata, sem tolerância numérica adicional. Os quatro blocos científicos também são idênticos byte a byte, confirmados por SHA-256.

Foram usados os arquivos atuais da pasta. Os nomes com sufixos “(3)” e “(4)” mencionados no pedido não estavam presentes. Não se alteraram parâmetros, seleção de seed, propostas, reflexão, sorteios, regra de aceitação, função objetivo, rede ou resfriamento. A execução científica foi separada do relógio da narração: os quadros mostram estados produzidos pelo motor original.

## Simulação 02

'''
science+=table([('Seed',s2['seed']),('Propostas',s2['summary']['iterations']),('Aceitas',s2['metrics']['accepted']),('Rejeitadas',s2['metrics']['rejected']),('Pioras aceitas',s2['metrics']['uphillAccepted']),('Pioras propostas',s2['metrics']['uphillProposed']),('E inicial',s2['summary']['initial']),('E final',s2['summary']['final']),('E mínimo',s2['summary']['min']),('E máximo',s2['summary']['max']),('T inicial',s2['summary']['temperature0']),('Amplitude calibrada',s2['summary']['amplitude'])])
science+='\nTambém foram comparados integralmente: trajetória, todos os eventos, estado final, históricos, calibração, métricas e validações independentes. A temperatura alta permanece exploratória; o mínimo visitado não substitui artificialmente o estado final.\n\n## Simulação 03\n\n'
science+=table([('Seed',s3['seed']),('Tentativa do caso de melhora',a['attempt']),('ΔE da melhora',a['delta']),('Decisão da melhora','Aceitar'),('Tentativa do caso pareado',p['attempt']),('E atual',p['currentEnergy']),('E proposto',p['candidateEnergy']),('ΔE pareado',p['delta']),('Sorteio u',p['u']),('T alta',p['high']['temperature']),('T baixa',p['low']['temperature']),('P alta',p['high']['probability']),('P baixa',p['low']['probability']),('Decisão em T alta','Aceitar'),('Decisão em T baixa','Rejeitar')])
science+='\nOs vetores `currentState` e `candidateState`, os resultados por via, as tentativas de seleção e as validações foram comparados integralmente. Na transição, 121 amostras verificam o mesmo evento, estados, ΔE e u; somente T modifica P. Os extremos preservam exatamente os valores de temperatura e probabilidade, antes de qualquer arredondamento de exibição.\n\n## Simulação 04\n\n'
science+=table([(k,s4[k]) for k in ['seed','T0','Tf','N','alpha','initialEnergy','finalEnergy','bestEnergy','bestIteration','bestTime']])
science+='''
Todos os 1.920 eventos, estados final e melhor, resultados das vias, histórico completo e contrato de continuidade foram comparados. A curva verde continua sendo o mínimo acumulado dos custos visitados. O mapa de fechamento usa `bestState` e `bestResult`.

Como a seed selecionada termina no melhor estado, foi executado um teste adicional com a seed já prevista no núcleo 31415926, apenas no ambiente de teste. Nela, o custo final é 0.4312512893505296 e o melhor custo é 0.4312451645517304. O fechamento usa o vetor do melhor estado, comprovadamente diferente do vetor final. A seed de produção continua 20260913.

## Modelo alternativo de tráfego

O motor de quatro interseções e 12 segmentos permanece separado. Foram comparados estados semafóricos, veículos individualizados, métricas, seis propostas, seis aceitações e validações. A execução determinística de referência termina com custo '''+str(tr['metrics']['energy'])+'''. Não houve erros das validações do motor.

Somente a identificação mudou: título da página, identificação principal, aviso de exclusão da cadeia 02 → 03 → 04 → 05, identificação na última cena e nome do JSON exportado. A folha de estilos também é idêntica à original. `transitSimulation.html` foi preservado; a entrega identificada é `transitSimulation_legacy.html`.

## Evidências de integridade

'''
for f in regression['files']:
    science+=f"### {f['file']}\n\nNúcleo antes e depois: `{f['beforeCoreSHA256']}`\n\nDados científicos antes e depois: `{f['beforeResultsSHA256']}`\n\n"
science+='''## Reprodução

Na pasta principal do projeto:

```bash
node video-first-audit/regression.cjs
node video-first-audit/presentation-test.cjs
```

O primeiro teste reexecuta os núcleos e compara com a captura anterior. O segundo percorre a apresentação a 60 amostras por segundo e testa seus contratos, usando um contexto de desenho simulado; ele complementa, mas não substitui, a inspeção real no navegador.

Arquivos de evidência: `baseline.json`, `regression-results.json`, `presentation-results.json` e `simulation-02/03/04-results.json`.
'''
science+='\n## Verificação adicional dos JSONs exportados pelo Chromium\n\nOs botões de exportação foram acionados nos três HTMLs. Os arquivos efetivamente baixados foram lidos e comparados com os dados produzidos em Node. Estados, seeds, sorteios e decisões coincidiram exatamente. Algumas funções matemáticas produzem diferenças de arredondamento entre runtimes: as maiores diferenças absolutas foram '+', '.join(f"S0{x['simulation']}: {x['maxAbsoluteRuntimeDifference']:.3g}" for x in exports)+'. Isso não é uma diferença antes/depois da refatoração: a comparação anterior/posterior dentro do mesmo runtime é exata, e o código científico é byte a byte igual. As diferenças entre runtimes estão discriminadas em `browser-export.json`.\n'
(D/'SCIENTIFIC_REGRESSION_REPORT.md').write_text(science)

count=sum(f['framesAt60fps'] for f in presentation['files'])
report=f'''# PRESENTATION VALIDATION REPORT

Resultado: **PASS para a nova apresentação das Simulações 02, 03 e 04**. Auditoria executada em 17/09/2026.

## Diagnóstico e mudança

As telas anteriores concentravam mapa, telemetria e regras em um mesmo quadro. A apresentação agora distribui os conceitos em 49 cenas, com pausas, destaque do semáforo alterado, mensagens maiores, uma pergunta central por etapa e revelação gradual das fórmulas.

| Arquivo | Apresentação nova | Relógio científico original |
|---|---:|---:|
| Simulação 02 | 73 s | 14 s |
| Simulação 03 | 111 s | Eventos didáticos originais; parâmetros e seleção preservados |
| Simulação 04 | 58 s | 16 s |

O prolongamento serve à leitura e à narração. Não altera o número de propostas, seus tempos científicos nem os resultados. O desenho da rede usa uma transformação uniforme das coordenadas canônicas; os pontos continuam identificados como fluxo ilustrativo.

## Verificações executadas

- Núcleos científicos: quatro comparações exatas aprovadas.
- Lógica da apresentação: {count:,} quadros amostrados a 60 Hz, incluindo todos os extremos, sem exceção de execução.
- Chromium do navegador integrado: as três timelines foram reproduzidas do início ao fim, com autoplay, sem erros ou avisos de console capturados. O modelo alternativo também completou os 15 s.
- Todas as 49 cenas foram selecionadas pelos controles reais; títulos e fase selecionada coincidiram e nenhum texto auditado ultrapassou o quadro de 1920 × 1080.
- Reprodução, pausa, reinício e navegação por tempo funcionaram nos três arquivos.
- A exportação JSON foi acionada nos três arquivos; os downloads foram encontrados no disco e seus dados científicos conferidos dentro da precisão de máquina. Estados, sorteios e decisões coincidiram exatamente com a execução em Node.
- “Gravar do início” oculta controles, painel de validações e cursor. Escape pausa e restaura os controles. O modo interativo é acessível com `?recording=0`.
- `validatePresentationContract()` executou no navegador e retornou PASS nos três arquivos; os resultados estão no painel “Validações”.
- Todos os HTMLs são autônomos: Canvas 2D, CSS e JavaScript embutidos; nenhum script, fonte ou biblioteca externa.
- Atributos de acessibilidade e descrições da cena estão em português; as atualizações de `aria-live` acontecem por cena, sem ler incessantemente os números.

## Contrato didático

**Simulação 02:** rede → semáforo → configuração x → custo E(x) → exploração com T alta → mínimos locais. Os quatro callouts de leitura da rede duram 2,8 s cada. Não há fórmula de Metrópolis, sorteio ou contadores de aceitação na apresentação principal.

**Simulação 03:** primeiro x e x′, depois ΔE; melhora aceita sem T, sorteio ou régua. Um novo teste restaura o estado de referência. Só depois surgem a probabilidade, o limite P e o sorteio u. Na redução de T, u fica imóvel e a região verde encolhe. Após rejeitar, o mapa retorna a x. A comparação usa o mesmo u apenas para isolar a temperatura, como explica a nota da cena.

**Simulação 04:** três métricas principais e um único gráfico. O custo atual e o mínimo acumulado têm cores e legendas distintas. O fechamento identifica início, final e melhor separadamente e calcula a redução usando o melhor custo. Não há promessa de ótimo global.

## Revisão visual sem áudio

Foi realizada uma revisão editorial das capturas, sem áudio. Ela permite seguir: “rede → configuração → custo”; “melhora aceita → piora pode ser aceita → T muda a chance”; e “T diminui → busca mais seletiva → melhor estado guardado”. Essa avaliação é uma inspeção técnica e editorial, **não um estudo de compreensão com espectadores**.

Títulos têm 46 px; conceitos, 38–44 px; valores principais, 50–58 px; explicações, 25–27 px; notas, 16 px. Os fechamentos usam mensagens maiores. O limite de até três números importantes tem a exceção solicitada da comparação pareada, que mostra P e u em ambos os lados.

## Correções encontradas durante os testes

Foi corrigida a sobreposição entre a anotação da curva e a nota do resfriamento. Também foi corrigida a atualização do campo de tempo para responder durante a digitação, antes que um redesenho pudesse restaurar o valor anterior. A navegação por tempo foi então repetida e aprovada nos três arquivos.

## Escopo do modelo alternativo

`transitSimulation_legacy.html` recebeu **somente mudanças de identificação**, conforme a exigência específica do pedido. A interface, os controles originais e a telemetria foram preservados. Portanto, a ocultação completa de controles e a nova hierarquia didática acima se aplicam a 02/03/04; não se afirma que a interface antiga do modelo complementar passou por essa refatoração. O original continua disponível sem alterações.

## Capturas auditadas

Todas as imagens abaixo foram capturadas no Chromium, salvas em PNG de 1920 × 1080 e inspecionadas visualmente. A captura nativa de viewport foi usada; capturas preliminares com margens introduzidas pela escala do monitor foram substituídas.

| Arquivo | Tempo da apresentação | Cena | Captura |
|---|---:|---|---|
'''
for s in screenshots:
    report+=f"| {s['file']} | {s['t']} s | {s['phase']} | [{s['screenshot']}](screenshots/{s['screenshot']}) |\n"
report+='| Modelo alternativo | 15 s | Demonstração complementar | [transito-alternativo.png](screenshots/transito-alternativo.png) |\n'
report+='''
Evidências: `browser-screenshots.json`, `browser-all-phases.json`, `browser-controls.json`, `browser-timelines.json`, `browser-legacy.json`, `browser-export.json` e `presentation-results.json`. Os testes foram executados no Chromium disponível neste ambiente; outros navegadores não foram testados.
'''
(D/'PRESENTATION_VALIDATION_REPORT.md').write_text(report)

readme='''# Simulações para vídeo — XLIII Semana da Física

Abra `ABRIR_SIMULACOES.html` para acessar as apresentações, os controles, os JSONs e as capturas.

Os quatro HTMLs finais estão na pasta superior e são completos, independentes e utilizáveis sem internet:

- `Simulation2_UrbanLattice.html` — rede, estado e custo; 73 s.
- `Simulation3_Metropolis.html` — decisão e efeito da temperatura; 111 s.
- `Simulation4_Convergence.html` — execução completa e melhor resultado; 58 s.
- `transitSimulation_legacy.html` — modelo alternativo de tráfego, apenas reidentificado; 15 s.

## Uso das Simulações 02, 03 e 04

Ao abrir diretamente, a apresentação começa no modo de gravação, com controles e cursor ocultos. **Escape** pausa e exibe os controles. **Espaço** reproduz/pausa; **R** reinicia. O botão **Gravar do início** reinicia com a interface limpa. Não há áudio embutido: as pausas foram preparadas para narração externa.

O endereço também aceita `?recording=0` para abrir o modo interativo, `?autoplay=0` para iniciar pausado e `?autoplay=0&t=20` para revisar um quadro no segundo 20. Esses parâmetros só controlam a apresentação. Para uma captura em vídeo, use a área de conteúdo do navegador em 1920 × 1080.

O botão **Exportar JSON** entrega os dados científicos completos da execução validada, independentemente da posição de reprodução. Cópias dos dados completos de 02/03/04 acompanham esta entrega em `simulation-02-results.json`, `simulation-03-results.json` e `simulation-04-results.json`.

O modelo alternativo mantém seus controles originais, por exigência de alterar somente sua identificação. Seus valores de custo e atraso não devem ser comparados numericamente com a cadeia canônica de 16 interseções.

## Auditoria e manutenção

- `SCIENTIFIC_REGRESSION_REPORT.md`: resultados antes e depois, com hashes dos núcleos e dados.
- `PRESENTATION_VALIDATION_REPORT.md`: testes, capturas, escopo e limitações.
- `screenshots/`: quadros auditados em 1080p.
- `before/` e `baseline.json`: evidência preservada antes da refatoração.
- `presentation-common.js` e `presentation-2/3/4.js`: fontes da nova apresentação.
- `build.py`: incorpora essas fontes aos HTMLs, mantendo os núcleos capturados sem alterações.
- `regression.cjs` e `presentation-test.cjs`: verificações reproduzíveis.

Para reconstruir após uma alteração na apresentação, execute `python3 video-first-audit/build.py` na pasta principal. Depois execute os dois testes Node indicados no relatório científico. Não recapture a referência anterior para esconder uma divergência.
'''
(D/'README.md').write_text(readme)

cards=''
for n,file,desc,duration in [(2,'Simulation2_UrbanLattice.html','Rede → configuração → custo','73 s'),(3,'Simulation3_Metropolis.html','Melhora, piora e temperatura','111 s'),(4,'Simulation4_Convergence.html','Resfriamento e melhor resultado','58 s')]:
    cards+=f'<article><span>SIMULAÇÃO 0{n} · {duration}</span><h2>{desc}</h2><p><a href="../{file}?recording=0">Abrir com controles</a></p><p><a href="../{file}">Reproduzir para gravação</a> · <a href="simulation-0{n}-results.json" download>JSON</a></p></article>'
cards+='<article><span>MODELO ALTERNATIVO · 15 s</span><h2>Demonstração complementar</h2><p><a href="../transitSimulation_legacy.html">Abrir modelo de tráfego</a></p><p>Não integra a cadeia 02 → 03 → 04 → 05.</p></article>'
gallery=''.join(f'<figure><a href="screenshots/{p.name}"><img src="screenshots/{p.name}" alt="{html.escape(p.stem)}" loading="lazy"></a><figcaption>{html.escape(p.stem)}</figcaption></figure>' for p in sorted((D/'screenshots').glob('*.png')))
(D/'ABRIR_SIMULACOES.html').write_text(f'''<!DOCTYPE html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Simulações para vídeo — UFG</title><link rel="icon" href="data:,"><style>body{{margin:0;padding:56px;background:#0f111a;color:#f8f8f2;font:20px/1.5 Arial,sans-serif}}main{{max-width:1440px;margin:auto}}h1{{font-size:44px;font-weight:500}}h2{{font-size:27px;font-weight:500}}a{{color:#8be9fd}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:24px}}article{{padding:26px;border:1px solid #343d51;border-radius:10px}}article span{{color:#bd93f9;font-size:15px}}article p{{font-size:17px}}.muted{{color:#a4afc1}}img{{width:100%;height:auto;border-radius:7px}}figure{{margin:0}}figcaption{{font-size:15px;color:#a4afc1;margin:8px 0 20px}}</style><main><p class="muted">XLIII SEMANA DA FÍSICA · UFG</p><h1>Recozimento simulado, uma ideia por vez.</h1><p>Apresentações completas para vídeo, com os resultados científicos preservados.</p><div class="grid">{cards}</div><p class="muted">Escape mostra os controles. “Gravar do início” reinicia com a interface limpa. Os arquivos funcionam sem internet.</p><p><a href="README.md">Como usar</a> · <a href="SCIENTIFIC_REGRESSION_REPORT.md">Regressão científica</a> · <a href="PRESENTATION_VALIDATION_REPORT.md">Validação da apresentação</a></p><h2>Quadros auditados em 1920 × 1080</h2><div class="grid">{gallery}</div></main></html>''')

manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/'Simulation2_UrbanLattice.html',R/'Simulation3_Metropolis.html',R/'Simulation4_Convergence.html',R/'transitSimulation_legacy.html']}
(D/'final-files-sha256.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(R/'Simulacoes_Video_First.zip','w',zipfile.ZIP_DEFLATED) as z:
    for name in manifest:z.write(R/name,name)
    for p in sorted(D.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:z.write(p,p.relative_to(R))
print('Reports and complete package created.')
