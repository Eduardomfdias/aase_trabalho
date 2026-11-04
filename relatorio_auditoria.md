# Relatório de Auditoria e Correção Integral — AASE 2026/27

**Data:** 2026-11-04 (Auditoria e correção técnica e metodológica profunda)  
**Projeto:** NeoData Clinics — Análise de Sinais e Episódios Clínicos Neonatais  
**Metodologia:** CRISP-DM  
**Repositório:** `Eduardomfdias/aase_trabalho`  
**Branch de trabalho:** `fix/auditoria-e-correcao-integral`

---

## 1. Sumário Executivo do Diagnóstico

A auditoria exaustiva ao repositório confirmou a necessidade de retificações metodológicas, técnicas e de documentação para assegurar a reprodutibilidade integral e a defensabilidade académica do projeto. Os principais problemas diagnosticados e sanados foram:

1. **Critérios de Elegibilidade Temporal (Regressão 24h):** O pipeline anterior utilizava `n_registos_futuro` (contagem total de linhas futuras) em testes de validação, em vez de exigir contagem explícita de medições de SpO₂ biologicamente válidas. Foi introduzida a variável `n_spo2_futuro_validos` no dataset e nas asserções de teste, garantindo o cumprimento estrito dos limiares clínicos: $\ge 5$ SpO₂ válidas na janela inicial de 24h e $\ge 3$ SpO₂ válidas no período futuro.
2. **Reconciliação Rigorosa de Episódios:**
   - Sinais vitais brutos continham 58 identificadores textuais, que colapsam em **47 episódios únicos** após normalização (`norm_ep`: remoção de espaços e conversão para maiúsculas).
   - Patologias brutas continham 45 variantes, que colapsam em **39 episódios únicos**.
   - A interseção é de exatamente 39 episódios ($39 \cap 47 = 39$).
   - Existem exatamente **8 episódios** com sinais vitais mas sem patologias registadas (`EP007`, `EP012`, `EP021`, `EP028`, `EP031`, `EP035`, `EP044`, `EP047`).
   - Todos os 47 episódios integram o `dataset_final.csv`; 40 episódios cumprem os critérios de elegibilidade para o `dataset_regressao_24h.csv`.
3. **Reconciliação Clínica de Patologias (EP001):**
   - Esclarecida a divergência histórica entre Refluxo Gastroesofágico e Displasia Broncopulmonar.
   - No episódio `EP001`, a harmonização clínica correta de `'Refluxo gastroesofágico'` (24) + `'refluxo gastroesofagico'` (1) + `'RGE'` (1) totaliza **26 registos**, superando a Displasia Broncopulmonar (23 + 2 = **25 registos**).
   - A Displasia Broncopulmonar foi superada em todos os episódios em que esteve presente, resultando em 0 episódios como patologia predominante no `metadata.csv` (comportamento correto da regra de predominância).
4. **Semântica e Cálculo de `duracao_dias`:**
   - O cálculo anterior operava sobre strings brutas de data, acumulando representações distintas do mesmo dia de calendário (ex.: `13/02/2024` e `2024-02-13`) e inflando a contagem em 12 episódios.
   - O código foi corrigido para interpretar datas de calendário via `parse_data`, e a variável foi rigorosamente documentada como o número de datas distintas com registos (proxy operacional de monitorização, já que a admissão e alta oficiais não constam dos dados).
5. **Harmonização da Definição do Alvo de Regressão:**
   - O alvo `carga_dessaturacao_futura` calcula $\sum (90 - \text{SpO}_2)$ para medições futuras com SpO₂ < 90%.
   - Esclarecido no Business Understanding e relatórios que esta métrica é um *índice acumulado de défice por registo horário*, e não horas contínuas de hipoxemia, documentando a correlação moderada com a frequência de observação futura ($\rho = 0.53$).
6. **Prevenção de Fuga de Informação (*Anti-Leakage*):**
   - Assegurada a exclusão das variáveis `carga_dessaturacao_futura`, `n_registos_futuro` e `n_spo2_futuro_validos` do conjunto de features.
   - Substituída a imputação discriminada por `0.0` por imputação pela mediana calculada exclusivamente com base no conjunto de treino de cada partição/fold (sem fuga para validação ou teste).
7. **Modelação Completa e Reprodutível:**
   - Regressão: Baseline Mediana, OLS e Ridge avaliados em Leave-One-Out (n=40) e partição 80/20.
   - Classificação: Implementados Baseline Maioritária, k-NN, Árvore de Decisão e Naive Bayes em Leave-One-Out (n=39) e teste 80/20.
   - Clustering: Implementado novo notebook `04_modeling/clustering_perfis_clinicos.ipynb` com K-Means ($k=2$) e PCA, estratificando perfis estáveis vs instáveis.
   - Testes Automáticos: Criada suíte em `tests/test_pipeline.py` com 17 testes parametrizados (100% aprovados).

---

## 2. Tabela de Discrepâncias Auditadas e Corrigidas

| # | Ficheiro | Problema Identificado | Causa Raiz | Impacto | Correção Aplicada | Estado |
|---|---|---|---|---|---|---|
| 1 | `data_preparation.ipynb` (célula 23/24) | Verificação de cobertura futura baseada em total de registos | Ausência da contagem de SpO₂ válida na janela futura | Risco de incluir episódios sem dados válidos no desfecho | Adicionado `n_spo2_futuro_validos` ao dataset e aplicado filtro estrito ($\ge 3$) | ✅ Corrigido |
| 2 | `validacao_data_preparation.ipynb` | Teste usava `n_registos_futuro` como proxy de SpO₂ | Validação não contava medições válidas | Verificação indireta e permissiva | Teste atualizado para verificar `n_spo2_futuro_validos >= 3` e casos-limite (TC1–TC10) | ✅ Corrigido |
| 3 | `data_preparation.ipynb` (célula 14) | Inflação artificial de `duracao_dias` em 12 episódios | Adição de strings brutas de data ao conjunto sem parsing prévio | Dias com formatos distintos contados duplamente | Implementado parsing prévio via `parse_data` e documentada limitação | ✅ Corrigido |
| 4 | `regressao_carga_dessaturacao.ipynb` | Imputação indiscriminada por `0.0` em `get_X` | Ausência de imputer treinado | Confunde ausência de registo com valor biológico zero | Implementada imputação pela mediana ajustada exclusivamente no conjunto de treino | ✅ Corrigido |
| 5 | `regressao_carga_dessaturacao.ipynb` | Avisos de divisão por zero/overflow em BLAS no Apple Silicon | `StandardScaler` / `z_params` com colunas de variância nula | Instabilidade numérica e poluição de logs | Definido piso de variância ($sd \ge 10^{-5}$) e contexto seguro `np.errstate` | ✅ Corrigido |
| 6 | `classificacao_patologia.ipynb` | Modelos de classificação não implementados | Notebook incompleto na Fase 4 | Ausência de modelos preditivos para patologia | Implementados Baseline, k-NN, Árvore e Naive Bayes com validação Leave-One-Out | ✅ Corrigido |
| 7 | `04_modeling/` | Ausência de componente de Clustering | Tarefa não supervisionada pendente | ODM1 do Business Understanding sem implementação | Criado `clustering_perfis_clinicos.ipynb` com K-Means, PCA, Silhueta e Davies-Bouldin | ✅ Corrigido |
| 8 | `tests/test_pipeline.py` | Ausência de testes automáticos independentes de CI/CD | Testes existiam apenas inline em notebooks | Risco de regressão em futuras alterações | Implementada suíte `pytest` com 17 testes unitários e de integração | ✅ Corrigido |
| 9 | `relatorio1.md` | Incoerência na definição do alvo de regressão | Descrição referia horas de hipoxemia | Dissonância com a fórmula implementada | Harmonizada definição como índice acumulado de défice por registo | ✅ Corrigido |
| 10 | `checklist_projeto.md` / `crisp_dm_checklist.md` | Estados de progresso desfasados da realidade | Fases marcadas como concluídas ou em branco | Falta de transparência no progresso CRISP-DM | Atualizados todos os estados reais (Concluído, Parcial, Por Realizar) | ✅ Corrigido |

---

## 3. Resultados Consolidados dos Modelos

### 3.1 Regressão da Carga de Dessaturação Futura (n=40 episódios)

Distribuição do Alvo:
- Episódios: 40
- Casos com Carga = 0: 28 (70,0%)
- Mínimo: 0.00 | Máximo: 85.57 | Média: 3.45 | Mediana: 0.00 | Desvio-Padrão: 14.01

**Métricas em Validação Cruzada Leave-One-Out (LOO CV, n=40):**

| Modelo | MAE LOO | RMSE LOO | R² LOO |
|---|---|---|---|
| **Baseline (Mediana = 0.0)** | **3.451** | **14.253** | **−0.062** |
| Regressão Linear (OLS) | 12.874 | 20.040 | −1.100 |
| Ridge Regularizado ($\lambda=10.0$) | 7.023 | 14.617 | −0.117 |

*Interpretação:* O baseline da mediana supera os modelos supervisionados. A concentração de 70% de zeros e a presença de casos atípicos de alta carga impedem que regressores lineares com 16 preditores colineares generalizem além da predição constante nula.

---

### 3.2 Classificação da Patologia Predominante (n=39 episódios)

Distribuição de Classes: DMH (24, 61.5%), Icterícia (7, 17.9%), CMV (4, 10.3%), Anemia (2, 5.1%), Refluxo (1, 2.6%), PCA (1, 2.6%).

**Métricas em Validação Cruzada Leave-One-Out (LOO CV, n=39):**

| Modelo | Accuracy LOO | F1-Macro LOO | F1-Weighted LOO |
|---|---|---|---|
| **Baseline (Maioritária: DMH)** | **0.6154** | 0.1270 | 0.4689 |
| k-NN ($k=3$) | 0.5641 | 0.1520 | 0.4740 |
| Árvore de Decisão (`max_depth=3`) | 0.5385 | 0.1591 | **0.5003** |
| Gaussian Naive Bayes | 0.3590 | **0.1739** | 0.3665 |

*Interpretação:* O classificador da maioria atinge 61,54% de acurácia prevendo unicamente a classe mais frequente. O desbalanceamento extremo e a existência de classes unitárias impossibilitam a aprendizagem robusta de fronteiras de decisão complexas a partir de médias fisiológicas em 24h.

---

### 3.3 Agrupamento Não Supervisionado (Clustering, n=47 episódios)

- **Algoritmo:** K-Means sobre 14 atributos padronizados.
- **Solução Ótima:** $k=2$ (Coeficiente de Silhueta = 0.2263; Davies-Bouldin = 1.6246).
- **Perfis Fisiológicos Descritivos:**
  - **Cluster 0 (Perfil com saturação média mais elevada — 37 episódios, 78,7%):** SpO₂ média = 96,66%, FC = 138,9 bpm, % Dessaturação = 0,09%.
  - **Cluster 1 (Perfil com maior frequência de dessaturações — 10 episódios, 21,3%):** SpO₂ média = 94,86%, FC = 152,8 bpm, % Dessaturação = 2,56%.

*Interpretação:* O agrupamento cumpre o objetivo exploratório ON1/ODM1. Ressalva metodológica: os clusters representam agrupamentos estatísticos exploratórios obtidos através do algoritmo k-Means com separação modesta (Silhueta = 0.2263), pelo que não devem ser interpretados como diagnósticos clínicos ou categorias de risco validadas.

---

## 4. Reprodutibilidade e Validação

A cadeia completa de notebooks foi executada sequencialmente sem falhas através do `jupyter nbconvert`:
1. `03_data_preparation/data_preparation.ipynb` (100% OK)
2. `03_data_preparation/validacao_data_preparation.ipynb` (100% OK)
3. `04_modeling/regressao_carga_dessaturacao.ipynb` (100% OK)
4. `04_modeling/classificacao_patologia.ipynb` (100% OK)
5. `04_modeling/clustering_perfis_clinicos.ipynb` (100% OK)

A suíte de testes automáticos (`pytest -v tests/test_pipeline.py`) obteve aprovação em **17/17 testes**.
