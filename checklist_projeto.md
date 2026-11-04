# Checklist do Projeto — AASE 2026/27

> Metodologia: CRISP-DM · Dataset: Neonatal Vital Signs and Clinical Conditions

---

## PROJETO 1

### Entrega 1 — Business Understanding · ⏰ semana 19/10/2026 (Estado: Concluído ✅)

- [x] Definir objetivos de negócio (ON1: estratificação de risco; ON2: antecipar severidade/dessaturação; ON3: apoio ao diagnóstico)
- [x] Definir objetivos de data mining
  - [x] **Regressão** — estimar carga de dessaturação futura (janela 24h → restante internamento)
  - [x] **Classificação** — prever patologia predominante
  - [x] **Clustering** — agrupar doentes por condição e perfil clínico
- [x] Relatório entregue (`01_Business_Understanding/relatorio1.md`)

---

## Entrega 2 — Data Understanding & Data Preparation · ⏰ semana 09/11/2026 (Estado: Concluído ✅)

### Data Understanding
- [x] §1 Carregamento e descrição dos dados brutos (9 857 registos SV, 696 registos Patologias)
- [x] §2a Valores em falta e formatos não padronizados
- [x] §2b Valores fora de intervalo e filtros de plausibilidade fisiológica
- [x] §3 Estatísticas descritivas (sinais vitais + diagnósticos)
- [x] §4 Análise de distribuições e assimetrias
- [x] §5 Padrões temporais (circadiano, intra-episódio)
- [x] §6 Correlações fisiológicas
- [x] §7 Cobertura cruzada entre datasets (39 episódios na interseção, 8 apenas com SV)
- [x] §8 Co-variação entre sinais vitais e patologias
- [x] §9 Estrutura das entidades e variabilidade intra-episódio
- [x] Relatório Data Understanding escrito (`02_data_understanding/relatorio_data_understanding.md`)

### Data Preparation
- [x] Reconciliação rigorosa de identificadores (58 brutos → 47 normalizados em SV; 45 brutos → 39 normalizados em Pat)
- [x] Reconciliação clínica de patologias (EP001: Refluxo Gastroesofágico com 26 registos > Displasia com 25)
- [x] Tratamento de valores inválidos (242 registos excluídos por limites fisiológicos)
- [x] Consolidação de 60 grupos de timestamps duplicados pela mediana
- [x] Feature engineering por episódio: médias, desvios-padrão, mínimos, máximos e % dessaturação
- [x] Janela temporal de 24h ancorada no primeiro registo válido (`dataset_regressao_24h.csv`)
- [x] Critérios de elegibilidade estritos aplicados a SpO₂ válida ($\ge 5$ inicial, $\ge 3$ futura → 40 episódios)
- [x] Normalização Z-score calculada exclusivamente no treino (`normalisation_params.csv`)
- [x] Prevenção sistemática de fuga de informação (*anti-leakage*)
- [x] Datasets finais produzidos e auditados: `dataset_final.csv` (47 ep.) e `dataset_regressao_24h.csv` (40 ep.)
- [x] Relatório Data Preparation consolidado (`03_data_preparation/relatorio_data_preparation.md`)

---

## Entrega 3 — Modeling & Evaluation · ⏰ semana 14/12/2026 (Estado: Concluído na Modelação Técnica ✅ / Parcial na Competição Externa 🟡)

### Modelação — Regressão (prever carga de dessaturação futura)
- [x] Baseline (mediana do treino = 0.0)
- [x] Modelo 1 — Regressão Linear (OLS)
- [x] Modelo 2 — Ridge Regularizado ($\lambda=10.0$)
- [x] Imputação de omissos pela mediana ajustada exclusivamente no treino
- [x] Validação Leave-One-Out (LOO CV, n=40) e partição 80/20 (treino=32, teste=8)
- [x] Métricas calculadas: MAE, RMSE, R² (Baseline supera modelos lineares devido a 70% de zeros)

### Modelação — Classificação (prever patologia predominante)
- [x] Baseline (classe maioritária: DMH com 61,54% acurácia)
- [x] Modelo 1 — k-NN ($k=3$)
- [x] Modelo 2 — Árvore de Decisão (`max_depth=3`)
- [x] Modelo 3 — Gaussian Naive Bayes
- [x] Validação Leave-One-Out (LOO CV, n=39) e teste 80/20 (n=7)
- [x] Métricas calculadas: Accuracy, F1-macro, F1-weighted e Matrizes de Confusão

### Modelação — Clustering (perfis exploratórios)
- [x] Padronização Z-score e redução dimensional PCA (2 componentes)
- [x] K-Means avaliado para $k \in [2, 5]$ (Inércia, Silhueta, Davies-Bouldin)
- [x] Seleção de $k=2$ (Silhueta = 0.2263, Davies-Bouldin = 1.6246)
- [x] Caracterização descritiva dos grupos: Perfil com saturação média mais elevada (78,7%) vs Perfil com maior frequência de dessaturações (21,3%), com ressalva metodológica sobre a separação modesta

### Avaliação e Validação Global
- [x] Comparação de modelos por abordagem com análise crítica dos resultados
- [x] Suíte de testes automáticos com 17 testes parametrizados em `tests/test_pipeline.py` (100% de sucesso)
- [x] Execução e validação sequencial de todos os 5 notebooks sem falhas
- [x] Relatório técnico de modelação documentado (`04_modeling/notas_modelacao.md`)
- [ ] Submissão na plataforma Kaggle (por realizar externamente)

---

## PROJETO 2

### ⏰ Demo: 11–16 janeiro 2027 · Relatório: 17 janeiro 2027 (Estado: Por Realizar ⏳)

### Sistema BI
- [ ] Arquitetura do sistema definida
- [ ] Modelo multidimensional (Data Warehouse / Data Marts)
- [ ] Componente analítica (integração dos modelos do Projeto 1)
- [ ] Indicadores / KPIs clínicos e de gestão
- [ ] Dashboards analíticos e operacionais
- [ ] Demonstração e relatório final
