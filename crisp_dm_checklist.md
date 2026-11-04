# Checklist CRISP-DM — Projeto AASE 2026/27

Projeto: **NeoData Clinics — Análise de Sinais e Episódios Clínicos Neonatais**  
Estado global: **Fases 1 a 4 Concluídas ✅ | Fase 5 Avaliação Metodológica Concluída ✅ / Operacional Parcial 🟡 | Fase 6 (Deployment / Projeto 2) Por Realizar ⏳**

---

## Fase 1 — Business Understanding (Compreensão do Negócio) ✅

- [x] **Determinar Objetivos de Negócio**
  - [x] Background — contexto da neonatologia e vigilância intensiva (`§2.1.1`)
  - [x] Objetivos de negócio — ON1 (estratificação), ON2 (antecipar severidade), ON3 (apoio ao diagnóstico) (`§2.1.2`)
  - [x] Critérios de sucesso de negócio — CS-N1 a CS-N4 (`§2.1.3`)
- [x] **Avaliar a Situação**
  - [x] Inventário de recursos (`§2.2.1`)
  - [x] Requisitos, pressupostos e restrições (`§2.2.2`)
  - [x] Riscos e contingências (`§2.2.3`)
  - [x] Terminologia e glossário clínico (`§2.2.4`)
  - [x] Custos e benefícios esperados (`§2.2.5`)
- [x] **Determinar Objetivos de Prospeção de Dados**
  - [x] Objetivos analíticos — ODM1 (clustering), ODM2 (regressão 24h), ODM3 (classificação) (`§2.3.1`)
  - [x] Critérios de sucesso de prospeção (`§2.3.2`)
- [x] **Produzir Plano do Projeto**
  - [x] Plano de trabalho pelas seis fases CRISP-DM (`§2.4.1`)
  - [x] Avaliação inicial de ferramentas e bibliotecas (`§2.4.2`)

---

## Fase 2 — Data Understanding (Compreensão dos Dados) ✅

- [x] **Recolher Dados Iniciais**
  - [x] Leitura dos ficheiros brutos `1_sinais_vitais_por_hora-1.csv` e `3_patologias_por_dia-1.csv`
- [x] **Descrever Dados**
  - [x] Dicionário de dados, tipos de campos, contagem de registos e identificadores
- [x] **Explorar Dados**
  - [x] Exploração descritiva no notebook `02_data_understanding/eda_aase.ipynb`
  - [x] Análise de padrões circadianos, temporais e intra-episódio
  - [x] Matriz de correlação entre sinais vitais
- [x] **Verificar Qualidade dos Dados**
  - [x] Identificação de formatos de data não padronizados e datas inválidas (`2024-02-31`)
  - [x] Identificação de 242 registos fora de intervalos fisiológicos
  - [x] Deteção de 60 grupos de timestamps duplicados
  - [x] Relatório detalhado em `02_data_understanding/relatorio_data_understanding.md`

---

## Fase 3 — Data Preparation (Preparação dos Dados) ✅

- [x] **Selecionar Dados**
  - [x] Reconciliação de identificadores: 58 brutos → 47 normalizados em SV; 45 brutos → 39 normalizados em Patologias
  - [x] Critérios de elegibilidade temporal para regressão ($\ge 5$ SpO₂ inicial, $\ge 3$ SpO₂ futuro → 40 episódios)
- [x] **Limpar Dados**
  - [x] Filtros de validade fisiológica (9 615 registos mantidos, 242 excluídos)
  - [x] Consolidação de leituras concorrentes pela mediana
- [x] **Construir Dados**
  - [x] Engenharia de atributos nas primeiras 24h e no episódio completo
  - [x] Variável-alvo analítica: `carga_dessaturacao_futura` = $\sum(90 - \text{SpO}_2)$ para SpO₂ < 90% após 24h
  - [x] `duracao_dias` definido rigorosamente como contagem de datas de calendário distintas com registos
- [x] **Integrar Dados**
  - [x] Cruzamento de sinais vitais e patologias predominantes (39 com diagnóstico, 8 sem diagnóstico)
  - [x] Ficheiro consolidado `dataset_final.csv` (47 episódios)
- [x] **Formatar Dados**
  - [x] Prevenção estrita de data leakage
  - [x] Normalização Z-score calculada apenas no conjunto de treino
  - [x] Dataset preditivo `dataset_regressao_24h.csv` (40 episódios elegíveis)
  - [x] Validação automática por asserções em `validacao_data_preparation.ipynb` e `tests/test_pipeline.py`

---

## Fase 4 — Modeling (Modelação) ✅

- [x] **Selecionar Técnicas de Modelação**
  - [x] Regressão: Baseline Mediana, Regressão Linear OLS, Ridge Regularizado ($\lambda=10.0$)
  - [x] Classificação: Baseline Maioritária, k-NN ($k=3$), Árvore de Decisão (`max_depth=3`), Gaussian Naive Bayes
  - [x] Clustering: k-Means ($k=2$ a 5) e Agrupamento Hierárquico
- [x] **Gerar Plano de Teste**
  - [x] Validação Leave-One-Out (LOO CV) para máxima robustez em amostras pequenas ($n=40$ e $n=39$)
  - [x] Partição 80/20 independente para confirmação
- [x] **Construir Modelos**
  - [x] Execução de `04_modeling/regressao_carga_dessaturacao.ipynb`
  - [x] Execução de `04_modeling/classificacao_patologia.ipynb`
  - [x] Execução de `04_modeling/clustering_perfis_clinicos.ipynb`
- [x] **Avaliar Modelos**
  - [x] Regressão: Baseline MAE=3.451 supera OLS (12.874) e Ridge (7.023)
  - [x] Classificação: Baseline Maioritária Accuracy=61.54% supera modelos complexos
  - [x] Clustering: Solução $k=2$ (Silhueta=0.2263, DB=1.6246) com perfis estável (78.7%) vs instável (21.3%)

---

## Fase 5 — Evaluation (Avaliação) 🟡 (Metodológica: Concluída | Operacional: Parcial)

- [x] **Avaliar Resultados face aos Objetivos de Negócio**
  - [x] ON1 (Estratificação de risco): **Atingido** via clustering não supervisionado (grupos interpretáveis e fisiologicamente consistentes).
  - [x] ON2 (Antecipar severidade respiratória): **Limitação crítica identificada**. A utilidade preditiva às 24h não superou o baseline empírico devido a 70% de zeros e dimensão amostral reduzida.
  - [x] ON3 (Apoio ao diagnóstico): **Limitação crítica identificada**. Sinais vitais de 24h não possuem especificidade suficiente para discriminar patologias raras com 1 ou 2 exemplos.
- [x] **Revisão do Processo (Quality Assurance)**
  - [x] Auditoria técnica integral: eliminação de discrepâncias de contagem, correção de imputação de missing values e erradicação de riscos de data leakage.
- [ ] **Determinar Próximos Passos**
  - [x] Documentação das lições aprendidas e limitações remanescentes
  - [ ] Preparação para integração analítica no Projeto 2 (BI)

---

## Fase 6 — Deployment (Implantação / Projeto 2) ⏳

- [ ] **Planear Deployment**
  - [ ] Integração dos modelos de prospeção de dados na componente analítica do sistema de BI
- [ ] **Planear Monitorização e Manutenção**
  - [ ] Estratégia de re-treino à medida que novos episódios clínicos forem registados
- [ ] **Produzir Relatório Final e Apresentação**
  - [ ] Demonstração prática do sistema de BI e dashboards (semana 11–16 janeiro 2027)
- [ ] **Rever Projeto e Lições Aprendidas**
  - [ ] Relatório final consolidado do Projeto 2 (17 janeiro 2027)
