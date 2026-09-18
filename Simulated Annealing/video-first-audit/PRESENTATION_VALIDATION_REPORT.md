# PRESENTATION VALIDATION REPORT

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
- Lógica da apresentação: 14,523 quadros amostrados a 60 Hz, incluindo todos os extremos, sem exceção de execução.
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
| Simulation2_UrbanLattice.html | 16 s | Um semáforo | [s02-estado-x.png](screenshots/s02-estado-x.png) |
| Simulation2_UrbanLattice.html | 33 s | O custo | [s02-custo-e.png](screenshots/s02-custo-e.png) |
| Simulation2_UrbanLattice.html | 54 s | Exploração com T alta | [s02-t-alta.png](screenshots/s02-t-alta.png) |
| Simulation2_UrbanLattice.html | 70 s | Mínimos locais | [s02-minimos-locais.png](screenshots/s02-minimos-locais.png) |
| Simulation3_Metropolis.html | 20 s | Aceitar a melhora | [s03-melhora-aceita.png](screenshots/s03-melhora-aceita.png) |
| Simulation3_Metropolis.html | 32 s | O custo aumentou | [s03-custo-maior.png](screenshots/s03-custo-maior.png) |
| Simulation3_Metropolis.html | 66 s | Decisão com T alta | [s03-t-alta.png](screenshots/s03-t-alta.png) |
| Simulation3_Metropolis.html | 78 s | Reduzindo a temperatura | [s03-reduzindo-t.png](screenshots/s03-reduzindo-t.png) |
| Simulation3_Metropolis.html | 86 s | Decisão com T baixa | [s03-t-baixa.png](screenshots/s03-t-baixa.png) |
| Simulation3_Metropolis.html | 92 s | Comparação das decisões | [s03-comparacao.png](screenshots/s03-comparacao.png) |
| Simulation3_Metropolis.html | 108 s | Resfriar aos poucos | [s03-ponte.png](screenshots/s03-ponte.png) |
| Simulation3_Metropolis.html | 28 s | Outra alteração | [s03-semaforo-alterado.png](screenshots/s03-semaforo-alterado.png) |
| Simulation4_Convergence.html | 18 s | T alta: exploração | [s04-t-alta.png](screenshots/s04-t-alta.png) |
| Simulation4_Convergence.html | 28 s | T diminui | [s04-resfriamento.png](screenshots/s04-resfriamento.png) |
| Simulation4_Convergence.html | 37 s | T baixa: seleção | [s04-t-baixa.png](screenshots/s04-t-baixa.png) |
| Simulation4_Convergence.html | 10 s | Guardamos o melhor | [s04-atual-melhor.png](screenshots/s04-atual-melhor.png) |
| Simulation4_Convergence.html | 47 s | Resultado da execução | [s04-resultado-final.png](screenshots/s04-resultado-final.png) |
| Simulation4_Convergence.html | 55 s | Redução do custo | [s04-reducao.png](screenshots/s04-reducao.png) |
| Simulation2_UrbanLattice.html | 4 s | A rede | [s02-rede.png](screenshots/s02-rede.png) |
| Simulation2_UrbanLattice.html | 25 s | O estado x | [s02-vetor.png](screenshots/s02-vetor.png) |
| Simulation2_UrbanLattice.html | 42 s | A função de custo | [s02-funcao-custo.png](screenshots/s02-funcao-custo.png) |
| Simulation3_Metropolis.html | 70 s | Só a temperatura muda | [s03-comparacao-controlada.png](screenshots/s03-comparacao-controlada.png) |
| Simulation3_Metropolis.html | 88 s | Decisão com T baixa | [s03-estado-mantido.png](screenshots/s03-estado-mantido.png) |
| Modelo alternativo | 15 s | Demonstração complementar | [transito-alternativo.png](screenshots/transito-alternativo.png) |

Evidências: `browser-screenshots.json`, `browser-all-phases.json`, `browser-controls.json`, `browser-timelines.json`, `browser-legacy.json`, `browser-export.json` e `presentation-results.json`. Os testes foram executados no Chromium disponível neste ambiente; outros navegadores não foram testados.
