# Notas Metodológicas — Modelação (AASE 2026/27)

**Fase CRISP-DM:** 4 — Modeling  
**Data:** 2026-11-04 (atualização integral com base nos dados auditados)

---

## 1. Modelação — Regressão da Carga de Dessaturação Futura

- **Dataset:** `dataset_regressao_24h.csv` (40 episódios elegíveis com $\ge 5$ SpO₂ válidos na janela inicial e $\ge 3$ SpO₂ válidos na janela futura).
- **Alvo:** `carga_dessaturacao_futura` ($\min = 0.00$, $\max = 85.57$, média $= 3.45$, mediana $= 0.00$, desvio-padrão $= 14.01$). 28 dos 40 episódios (70,0%) têm alvo igual a zero.
- **Preditores (16):** estatísticas calculadas estritamente nas primeiras 24 horas (`n_registos_janela`, `n_spo2_validos`, `n_all_validos`, `sat_o2_*`, `puls_rate_*`, `perfusion_*`, `carga_desat_janela`).
- **Prevenção de Fuga de Informação:** `carga_dessaturacao_futura`, `n_registos_futuro` e `n_spo2_futuro_validos` são rigorosamente excluídos da matriz de treino.
- **Tratamento de Valores em Falta:** Imputação pela mediana ajustada exclusivamente no conjunto de treino de cada partição/fold (sem fuga para validação/teste).

### 1.1 Resultados — Validação Cruzada Leave-One-Out (LOO CV, n=40)

| Modelo | MAE LOO | RMSE LOO | R² LOO |
|---|---|---|---|
| **Baseline (Mediana = 0.0)** | **3.451** | **14.253** | **−0.062** |
| Regressão Linear (OLS) | 12.874 | 20.040 | −1.100 |
| Ridge ($\lambda = 10.0$) | 7.023 | 14.617 | −0.117 |

### 1.2 Resultados — Split 80/20 (Treino = 32, Teste = 8)

| Modelo | MAE treino | RMSE treino | R² treino | MAE teste | RMSE teste | R² teste |
|---|---|---|---|---|---|---|
| **Baseline (Mediana)** | 4.171 | 15.926 | −0.074 | **0.574** | **1.075** | **−0.398** |
| Regressão Linear (OLS) | 7.061 | 12.056 | 0.385 | 16.584 | 21.413 | −553.204 |
| Ridge ($\lambda = 10.0$) | 6.525 | 14.416 | 0.120 | 4.053 | 4.918 | −28.232 |

### 1.3 Interpretação Clínica da Regressão
1. O **Baseline (prever sempre a mediana do treino, que é 0.0)** supera todos os modelos lineares em MAE e RMSE no teste e em Leave-One-Out.
2. Como 70% dos episódios não apresentam episódios futuros de dessaturação, a previsão constante de zero é difícil de bater com apenas 40 observações e 16 preditores colineares.
3. Modelos com coeficientes lineares ajustados sobreajustam-se ao ruído dos poucos casos positivos (e.g., EP026 com carga=85.57), gerando $R^2$ negativos.
4. **Conclusão Metodológica Honesta:** Não se demonstrou utilidade clínica preditiva superior ao baseline de monitorização padrão com a dimensão amostral e variáveis disponíveis.

---

## 2. Modelação — Classificação da Patologia Predominante

- **Dataset:** `dataset_final.csv` / `train.csv` / `test.csv` (39 episódios com diagnóstico, 8 episódios sem diagnóstico excluídos da tarefa supervisionada).
- **Desbalanceamento de Classes:** 24/39 DMH (61,5%), 7/39 Icterícia (17,9%), 4/39 CMV (10,3%), 2/39 Anemia (5,1%), 1/39 Refluxo (2,6%), 1/39 PCA (2,6%).
- **Escalonamento Z-score:** Calculado exclusivamente com as observações de treino de cada partição/fold.

### 2.1 Resultados — Validação Cruzada Leave-One-Out (LOO CV, n=39)

| Modelo | Accuracy LOO | F1-Macro LOO | F1-Weighted LOO |
|---|---|---|---|
| **Baseline (Classe Maioritária: DMH)** | **0.6154** | 0.1270 | 0.4689 |
| k-NN ($k=3$) | 0.5641 | 0.1520 | 0.4740 |
| Árvore de Decisão (`max_depth=3`) | 0.5385 | 0.1591 | **0.5003** |
| Gaussian Naive Bayes | 0.3590 | **0.1739** | 0.3665 |

### 2.2 Interpretação Clínica da Classificação
1. O baseline maioritário atinge 61,54% de acurácia prevendo invariavelmente Doença das Membranas Hialinas (DMH).
2. Dois diagnósticos possuem apenas 1 episódio e um possui 2 episódios. Nenhuma partição estatística consegue fornecer suporte representativo para aprender ou avaliar classes unitárias.
3. Sinais vitais médios de 24 horas não contêm especificidade diagnóstica patognomónica suficiente para discriminar patologias neonatais complexas.

---

## 3. Modelação — Agrupamento Não Supervisionado (Clustering)

- **Notebook:** `04_modeling/clustering_perfis_clinicos.ipynb`.
- **Dataset:** `dataset_final.csv` (47 episódios com sinais vitais).
- **Features (14):** sumários de SpO₂, frequência cardíaca e perfusão, padronizados via `StandardScaler`.
- **Algoritmos Avaliados:** k-Means ($k \in [2, 5]$) e Agrupamento Hierárquico Aglomerativo.

### 3.1 Métricas de Qualidade dos Clusters

| k | Inércia | Silhueta Média | Davies-Bouldin |
|---|---|---|---|
| **2** | **531.16** | **0.2263** | **1.6246** |
| 3 | 444.58 | 0.1918 | 1.5813 |
| 4 | 381.70 | 0.1792 | 1.4352 |
| 5 | 335.63 | 0.1448 | 1.4155 |

### 3.2 Caracterização Clínica dos Perfis ($k=2$)
- **Cluster 0 — Perfil Fisiológico Estável (37 episódios, 78,7%):**
  - SpO₂ média: 96,66%
  - Frequência Cardíaca média: 138,9 bpm
  - Índice de Perfusão médio: 1,22
  - % Dessaturação média: 0,09%
- **Cluster 1 — Perfil Fisiológico de Risco / Instável (10 episódios, 21,3%):**
  - SpO₂ média: 94,86%
  - Frequência Cardíaca média: 152,8 bpm (taquicardia reativa)
  - Índice de Perfusão médio: 1,12
  - % Dessaturação média: 2,56% (quase 30× superior ao grupo estável)

**Conclusão Clínica:** O clustering não supervisionado cumpre com êxito o objetivo de estratificação de risco (ON1/ODM1), identificando uma separação clinicamente coerente entre recém-nascidos fisiologicamente estáveis e recém-nascidos com episódios frequentes de compromisso respiratório e instabilidade hemodinâmica.
