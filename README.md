# AASE — Análise de Sinais e Episódios Clínicos Neonatais

Repositório do Projeto da unidade curricular de **Aprendizagem Automática em Sistemas Empresariais** (Mestrado em Engenharia e Gestão de Sistemas de Informação - UMinho), época 2026/27.  
Metodologia: **CRISP-DM** · Dataset: *Neonatal Vital Signs and Clinical Conditions*

---

## Estrutura do Repositório

```
aase_trabalho/
├── 01_Business_Understanding/
│   ├── relatorio1.md                         ← Relatório consolidado da Fase 1 ✅
│   └── checklist_bu.md                       ← Checklist da Fase 1 ✅
├── 02_data_understanding/
│   ├── eda_aase.ipynb                        ← Análise Exploratória dos Dados (§1–§9) ✅
│   └── relatorio_data_understanding.md       ← Relatório técnico de compreensão dos dados ✅
├── 03_data_preparation/
│   ├── data_preparation.ipynb                ← Pipeline determinístico de preparação e limpeza ✅
│   ├── validacao_data_preparation.ipynb      ← Testes automáticos e de fronteira de integridade ✅
│   ├── relatorio_data_preparation.md         ← Relatório técnico de preparação ✅
│   ├── notas_data_preparation.md             ← Regras de negócio, elegibilidade e anti-leakage
│   ├── dataset_final.csv                     ← 47 episódios únicos (agregado global)
│   ├── dataset_regressao_24h.csv             ← 40 episódios elegíveis (janela 24h + desfecho futuro)
│   ├── train.csv / test.csv                  ← Partição 80/20 estratificada para classificação
│   ├── metadata.csv                          ← Mapeamento e contagens das 6 classes predominantes
│   └── normalisation_params.csv              ← Parâmetros Z-score ajustados estritamente no treino
├── 04_modeling/
│   ├── regressao_carga_dessaturacao.ipynb    ← Regressão (Baseline, OLS, Ridge com LOO CV) ✅
│   ├── classificacao_patologia.ipynb         ← Classificação (Baseline, k-NN, Árvore, NB com LOO CV) ✅
│   ├── clustering_perfis_clinicos.ipynb      ← Agrupamento não supervisionado (k-Means, PCA) ✅
│   ├── notas_modelacao.md                    ← Resultados empíricos, métricas e interpretação clínica
│   └── predicoes_teste.csv                   ← Previsões no conjunto de teste independente
├── tests/
│   └── test_pipeline.py                      ← Suíte de testes automáticos (pytest: 17 testes) ✅
├── dados_aase_202627/                        ← Dados originais intocáveis (apenas leitura)
│   ├── 1_sinais_vitais_por_hora-1.csv        ← 9 857 registos horários brutos
│   └── 3_patologias_por_dia-1.csv            ← 696 registos de patologia diários brutos
├── checklist_projeto.md                      ← Estado de cumprimento das entregas do projeto
├── crisp_dm_checklist.md                     ← Rastreio das fases da metodologia CRISP-DM
├── relatorio_auditoria.md                    ← Relatório detalhado da auditoria e correções
└── README.md                                 ← Documentação principal do repositório
```

---

## Dados e Reconciliação

### Sinais Vitais (`1_sinais_vitais_por_hora-1.csv`)
- **9 857 registos brutos** correspondentes a **47 episódios únicos** após normalização de identificadores (os 58 identificadores iniciais continham variantes gráficas e espaços).
- **9 615 registos fisiologicamente válidos (97,5%)** após aplicação de limites biológicos neonatal (SpO₂ ∈ [50, 100], FC ∈ [50, 350], Perfusão ∈ [0, 20]).
- **60 grupos de timestamps duplicados** consolidados pela mediana.

### Patologias (`3_patologias_por_dia-1.csv`)
- **696 registos brutos** correspondentes a **39 episódios únicos** após normalização de identificadores.
- Todos os 39 episódios com diagnóstico constam da base de sinais vitais ($39 \cap 47 = 39$).
- Existem **8 episódios** apenas com monitorização de sinais vitais e sem patologia associada.
- **6 patologias predominantes** consolidadas (EP001 classificado como Refluxo Gastroesofágico com 26 registos > Displasia com 25).

---

## Objetivos e Modelos de Data Mining

| Abordagem | Alvo / Tarefa | Dataset | Melhor Desempenho (LOO CV) |
|---|---|---|---|
| **Regressão** | `carga_dessaturacao_futura`: $\sum (90 - \text{SpO}_2)$ para SpO₂ < 90% após 24h | `dataset_regressao_24h.csv` (n=40) | **Baseline da Mediana** (MAE = 3.451, RMSE = 14.253) |
| **Classificação** | `pat_predominante`: previsão da patologia por perfil de sinais | `dataset_final.csv` (n=39) | **Baseline Maioritária** (Accuracy = 61.54%) |
| **Clustering** | Estratificação de perfis fisiológicos de risco | `dataset_final.csv` (n=47) | **k-Means ($k=2$)**: Estável (78.7%) vs Instável (21.3%) |

---

## Instruções de Execução e Reprodutibilidade

### 1. Pré-requisitos
Ambiente Python 3.10+ com as dependências instaladas:
```bash
pip install pandas numpy scikit-learn matplotlib seaborn pytest jupyter nbconvert
```

### 2. Execução da Suíte de Testes Automáticos
Para verificar a integridade dos dados, ausência de leakage e regras de elegibilidade:
```bash
pytest -v tests/test_pipeline.py
```

### 3. Execução Automatizada dos Notebooks
Para re-executar os notebooks em sequência e atualizar os datasets e saídas:
```bash
# Data Preparation e Validação
jupyter nbconvert --to notebook --execute --inplace 03_data_preparation/data_preparation.ipynb
jupyter nbconvert --to notebook --execute --inplace 03_data_preparation/validacao_data_preparation.ipynb

# Modelação e Avaliação
jupyter nbconvert --to notebook --execute --inplace 04_modeling/regressao_carga_dessaturacao.ipynb
jupyter nbconvert --to notebook --execute --inplace 04_modeling/classificacao_patologia.ipynb
jupyter nbconvert --to notebook --execute --inplace 04_modeling/clustering_perfis_clinicos.ipynb
```
