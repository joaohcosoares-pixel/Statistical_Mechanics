# SCIENTIFIC REGRESSION REPORT

Resultado: **PASS**. Auditoria executada em 17/09/2026.

## Método e escopo

Antes de editar, foram preservadas cópias completas dos quatro HTMLs em `before/` e executados seus motores em Node.js 22.23.2. O registro integral está em `baseline.json`. Após a refatoração, os motores foram novamente executados e seus dados completos serializados foram comparados por igualdade exata, sem tolerância numérica adicional. Os quatro blocos científicos também são idênticos byte a byte, confirmados por SHA-256.

Foram usados os arquivos atuais da pasta. Os nomes com sufixos “(3)” e “(4)” mencionados no pedido não estavam presentes. Não se alteraram parâmetros, seleção de seed, propostas, reflexão, sorteios, regra de aceitação, função objetivo, rede ou resfriamento. A execução científica foi separada do relógio da narração: os quadros mostram estados produzidos pelo motor original.

## Simulação 02

| Grandeza | Antes | Depois | Resultado |
|---|---:|---:|---|
| Seed | 20260912 | 20260912 | Idêntico |
| Propostas | 276 | 276 | Idêntico |
| Aceitas | 243 | 243 | Idêntico |
| Rejeitadas | 33 | 33 | Idêntico |
| Pioras aceitas | 122 | 122 | Idêntico |
| Pioras propostas | 155 | 155 | Idêntico |
| E inicial | 0.8669683218632138 | 0.8669683218632138 | Idêntico |
| E final | 0.746497456806198 | 0.746497456806198 | Idêntico |
| E mínimo | 0.6430624439100274 | 0.6430624439100274 | Idêntico |
| E máximo | 1.199530205039209 | 1.199530205039209 | Idêntico |
| T inicial | 0.096 | 0.096 | Idêntico |
| Amplitude calibrada | 0.15 | 0.15 | Idêntico |

Também foram comparados integralmente: trajetória, todos os eventos, estado final, históricos, calibração, métricas e validações independentes. A temperatura alta permanece exploratória; o mínimo visitado não substitui artificialmente o estado final.

## Simulação 03

| Grandeza | Antes | Depois | Resultado |
|---|---:|---:|---|
| Seed | 20260913 | 20260913 | Idêntico |
| Tentativa do caso de melhora | 2 | 2 | Idêntico |
| ΔE da melhora | -0.03006713020132845 | -0.03006713020132845 | Idêntico |
| Decisão da melhora | Aceitar | Aceitar | Idêntico |
| Tentativa do caso pareado | 19 | 19 | Idêntico |
| E atual | 0.8669683218632138 | 0.8669683218632138 | Idêntico |
| E proposto | 0.9366668688584987 | 0.9366668688584987 | Idêntico |
| ΔE pareado | 0.06969854699528488 | 0.06969854699528488 | Idêntico |
| Sorteio u | 0.3213598933070898 | 0.3213598933070898 | Idêntico |
| T alta | 0.096 | 0.096 | Idêntico |
| T baixa | 0.024 | 0.024 | Idêntico |
| P alta | 0.48382764976913584 | 0.48382764976913584 | Idêntico |
| P baixa | 0.05479775106645792 | 0.05479775106645792 | Idêntico |
| Decisão em T alta | Aceitar | Aceitar | Idêntico |
| Decisão em T baixa | Rejeitar | Rejeitar | Idêntico |

Os vetores `currentState` e `candidateState`, os resultados por via, as tentativas de seleção e as validações foram comparados integralmente. Na transição, 121 amostras verificam o mesmo evento, estados, ΔE e u; somente T modifica P. Os extremos preservam exatamente os valores de temperatura e probabilidade, antes de qualquer arredondamento de exibição.

## Simulação 04

| Grandeza | Antes | Depois | Resultado |
|---|---:|---:|---|
| seed | 20260913 | 20260913 | Idêntico |
| T0 | 0.096 | 0.096 | Idêntico |
| Tf | 1e-05 | 1e-05 | Idêntico |
| N | 1920 | 1920 | Idêntico |
| alpha | 0.995233118307486 | 0.995233118307486 | Idêntico |
| initialEnergy | 0.8669683218632138 | 0.8669683218632138 | Idêntico |
| finalEnergy | 0.4310316856997364 | 0.4310316856997364 | Idêntico |
| bestEnergy | 0.4310316856997364 | 0.4310316856997364 | Idêntico |
| bestIteration | 1916 | 1916 | Idêntico |
| bestTime | 15.966666666666667 | 15.966666666666667 | Idêntico |

Todos os 1.920 eventos, estados final e melhor, resultados das vias, histórico completo e contrato de continuidade foram comparados. A curva verde continua sendo o mínimo acumulado dos custos visitados. O mapa de fechamento usa `bestState` e `bestResult`.

Como a seed selecionada termina no melhor estado, foi executado um teste adicional com a seed já prevista no núcleo 31415926, apenas no ambiente de teste. Nela, o custo final é 0.4312512893505296 e o melhor custo é 0.4312451645517304. O fechamento usa o vetor do melhor estado, comprovadamente diferente do vetor final. A seed de produção continua 20260913.

## Modelo alternativo de tráfego

O motor de quatro interseções e 12 segmentos permanece separado. Foram comparados estados semafóricos, veículos individualizados, métricas, seis propostas, seis aceitações e validações. A execução determinística de referência termina com custo 0.5345554849563292. Não houve erros das validações do motor.

Somente a identificação mudou: título da página, identificação principal, aviso de exclusão da cadeia 02 → 03 → 04 → 05, identificação na última cena e nome do JSON exportado. A folha de estilos também é idêntica à original. `transitSimulation.html` foi preservado; a entrega identificada é `transitSimulation_legacy.html`.

## Evidências de integridade

### Simulation2_UrbanLattice.html

Núcleo antes e depois: `0d7a54edf87a06f65dce43581f374eae5c0cfc24a767a4dbf17eec13d13f1a37`

Dados científicos antes e depois: `25b04f7db50997705f4a990694c3e7bd9cb7e932a47a8e855bb875a7beea9acc`

### Simulation3_Metropolis.html

Núcleo antes e depois: `ea5b924cd2c7c18f9dc029caa0bfee2f5e8d10cba7833142660903f0c36aae68`

Dados científicos antes e depois: `a8502eb80bed042f17d372084301891d31e0a8301d24daf1a0f8ebacaa4e232d`

### Simulation4_Convergence.html

Núcleo antes e depois: `77c08ca132048ad924a86b2a34080b6e7d4d210b7d0e09ee2eedf7269c1d9987`

Dados científicos antes e depois: `a89c96d2f5943af5b1e3e063cd31342aa2a72f755c60c499ddd9fabd2fed3d5b`

### transitSimulation_legacy.html

Núcleo antes e depois: `fedf4e98a00f6cece2cd8863dedb20612e7e41de5ba7d85e6b7b1438448b85fa`

Dados científicos antes e depois: `1dfbb6e6f2e739c424f46b65f89dc64bc44068111bfff2f0c05f4efec09d85c4`

## Reprodução

Na pasta principal do projeto:

```bash
node video-first-audit/regression.cjs
node video-first-audit/presentation-test.cjs
```

O primeiro teste reexecuta os núcleos e compara com a captura anterior. O segundo percorre a apresentação a 60 amostras por segundo e testa seus contratos, usando um contexto de desenho simulado; ele complementa, mas não substitui, a inspeção real no navegador.

Arquivos de evidência: `baseline.json`, `regression-results.json`, `presentation-results.json` e `simulation-02/03/04-results.json`.

## Verificação adicional dos JSONs exportados pelo Chromium

Os botões de exportação foram acionados nos três HTMLs. Os arquivos efetivamente baixados foram lidos e comparados com os dados produzidos em Node. Estados, seeds, sorteios e decisões coincidiram exatamente. Algumas funções matemáticas produzem diferenças de arredondamento entre runtimes: as maiores diferenças absolutas foram S02: 1.22e-15, S03: 2.78e-17, S04: 2.78e-17. Isso não é uma diferença antes/depois da refatoração: a comparação anterior/posterior dentro do mesmo runtime é exata, e o código científico é byte a byte igual. As diferenças entre runtimes estão discriminadas em `browser-export.json`.
