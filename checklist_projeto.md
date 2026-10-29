# Checklist do Projeto — AASE 2026/27

> Metodologia: CRISP-DM · Dataset: Neonatal Vital Signs and Clinical Conditions

---

## PROJETO 1

### Entrega 1 — Business Understanding · ⏰ semana 19/10/2026 ✅

- [x] Definir objetivos de negócio
- [x] Definir objetivos de data mining
  - [x] **Regressão** — prever carga de dessaturação futura (janela 24h → restante internamento)
  - [x] **Classificação** — prever patologia
  - [x] **Clustering** — agrupar doentes por condição clínica
- [x] Relatório entregue (`01_business_understanding/business_understanding.pdf`)

---

### Entrega 2 — Data Understanding & Data Preparation · ⏰ semana 09/11/2026

#### Data Understanding
- [x] §1 Carregamento e descrição dos dados
- [x] §2a Valores em falta
- [x] §2b Valores fora de intervalo
- [x] §3 Estatísticas descritivas (SV + patologias)
- [x] §4 Distribuições
- [x] §5 Padrões temporais (circadiano, mensal, hora das dessaturações, intra-episódio)
- [x] §6 Correlações (Pearson + scatter matrix)
- [x] §7 Relação entre datasets (cobertura cruzada)
- [x] §8 Co-variação (SV por patologia, co-ocorrência, duração por patologia)
- [x] §9 Estrutura das entidades (duração, boxplots, variabilidade intra-episódio)
- [x] Relatório Data Understanding escrito

#### Data Preparation
- [x] Definir variável alvo para regressão (carga de dessaturação futura — Σ(90−SpO₂) para SpO₂<90% após 24h)
- [x] Definir variável alvo para classificação (patologia predominante por episódio)
- [x] Tratamento de valores inválidos (242 registos excluídos — limites fisiológicos)
- [x] Feature engineering
  - [x] Agregar sinais vitais por episódio (média, DP, min, max, % dessaturações)
  - [x] Janela temporal 24h para regressão (`dataset_regressao_24h.csv`)
  - [x] Codificar patologias (label encoding por frequência)
- [x] Normalização Z-score (calculada apenas no treino — `normalisation_params.csv`)
- [x] Divisão treino/teste (80/20 para classificação em `train.csv`/`test.csv`; split interno no notebook de regressão)
- [x] Datasets finais: `dataset_final.csv` (47 ep.) e `dataset_regressao_24h.csv` (40 ep.)
- [x] Relatório Data Preparation escrito

---

### Entrega 3 — Modeling & Evaluation · ⏰ semana 14/12/2026

#### Modelação — Regressão (prever carga de dessaturação futura)
- [x] Baseline (mediana do treino)
- [x] Modelo 1 — Regressão Linear (OLS via lstsq)
- [x] Modelo 2 — Ridge (λ=10.0)
- [ ] Modelo 3 — adicional (ex: Random Forest)
- [x] Métricas: MAE, RMSE, R² (treino e teste)

#### Modelação — Classificação (prever patologia)
- [ ] Baseline (classe maioritária)
- [ ] Modelo 1 — Árvore de Decisão
- [ ] Modelo 2 — Naive Bayes ou KNN
- [ ] Modelo 3 — Random Forest / SVM
- [ ] Métricas: Accuracy, F1-macro, Confusion Matrix

#### Modelação — Clustering (agrupar doentes)
- [ ] K-Means (determinar k via elbow / silhouette)
- [ ] Outro algoritmo (DBSCAN ou hierárquico)
- [ ] Caracterização dos clusters (perfil clínico de cada grupo)
- [ ] Métricas: Silhouette Score, Davies-Bouldin

#### Avaliação
- [ ] Comparação de modelos por abordagem
- [ ] Selecionar melhor modelo de cada tipo para Projeto 2
- [ ] Relatório Modeling & Evaluation escrito
- [ ] Submissão Kaggle (ranking entre grupos)

---

## PROJETO 2

### ⏰ Demo: 11–16 janeiro 2027 · Relatório: 17 janeiro 2027

#### Sistema BI
- [ ] **Arquitetura do sistema** definida (10%)
- [ ] **Modelo multidimensional** (Data Warehouse / Data Marts) (10%)
  - [ ] Tabelas de factos e dimensões desenhadas
  - [ ] ETL implementado (pode ser offline)
- [ ] **Componente analítica** — modelos de DM integrados (20%)
  - [ ] Modelo de regressão (prever duração)
  - [ ] Modelo de classificação (prever patologia)
  - [ ] Modelo de clustering (perfis de doentes)
- [ ] **Indicadores / KPIs** definidos e implementados (10%)
  - [ ] Taxa de dessaturação média
  - [ ] Duração média por patologia
  - [ ] Distribuição de clusters
- [ ] **Dashboards** (10%)
  - [ ] Dashboard operacional (sinais vitais em tempo real / histórico)
  - [ ] Dashboard analítico (modelos preditivos + clusters)
- [ ] **Qualidade e eficiência global** (10%)

#### Demonstração
- [ ] Apresentação dos resultados (5%)
- [ ] Desempenho individual (5%)

#### Relatório final (15%)
- [ ] Relatório completo do Projeto 2 submetido

#### Peer Assessment (5%)
- [ ] Avaliação dos colegas submetida
