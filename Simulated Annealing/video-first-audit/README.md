# Simulações para vídeo — XLIII Semana da Física

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
