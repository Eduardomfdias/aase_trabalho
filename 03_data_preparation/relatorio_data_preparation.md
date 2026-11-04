# Data Preparation — AASE 2026/27

**Disciplina:** Aprendizagem Automática em Sistemas Empresariais  
**Fase CRISP-DM:** 3 — Data Preparation  
**Data:** 2026-11-04 (revisão técnica e metodológica integral)

---

## 1. Visão geral do pipeline

O pipeline de preparação transforma os dois ficheiros CSV de origem num conjunto de datasets analíticos rigorosamente preparados para modelação. O processo é implementado em `data_preparation.ipynb` e validado em `validacao_data_preparation.ipynb`, seguindo a sequência:

```
Ficheiros CSV originais (dados_aase_202627/)
  → Normalização determinística de identificadores (IDs) e patologias
  → Filtros de plausibilidade fisiológica e consolidação de timestamps duplicados
  → Agregação global por episódio (dataset_final.csv — 47 episódios)
  → Construção de janelas temporais estritas de 24h e elegibilidade (dataset_regressao_24h.csv — 40 episódios)
  → Normalização Z-score e partição treino/teste (80/20) ajustada no treino
  → Validação estrutural de integridade e exportação de datasets
```

Todos os datasets produzidos têm o episódio como grão de observação (1 linha = 1 episódio). A separação temporal é mutuamente exclusiva e nenhuma informação futura entra nos preditores.

---

## 2. Tratamento de qualidade e reconciliação

### 2a. Normalização e reconciliação de identificadores (IDs)

Os ficheiros originais apresentam divergências superficiais de escrita (espaços à esquerda, no meio e capitalização mista):
- **Sinais vitais brutos:** 58 strings de identificador distintas → após remoção de espaços e conversão para maiúsculas (`norm_ep`), resultam em **47 episódios únicos**. Exemplos: `' EP011'`, `'EP 016'`, `'ep016'`, `' EP016'` colapsam para `EP011` e `EP016`.
- **Patologias brutas:** 45 strings de identificador distintas → após normalização, resultam em **39 episódios únicos**.
- **Reconciliação cruzada:** Todos os 39 episódios com patologia estão presentes nos sinais vitais ($39 \cap 47 = 39$). Existem exatamente **8 episódios** que possuem registos de sinais vitais mas nenhuma patologia associada (`EP007`, `EP012`, `EP021`, `EP028`, `EP031`, `EP035`, `EP044`, `EP047`). Não existem episódios com patologia que não tenham sinais vitais.

### 2b. Filtros fisiológicos

São aplicados limites de plausibilidade biológica validados para neonatologia:

| Variável | Intervalo fisiológico válido | Registos brutos excluídos |
|---|---|---|
| SpO₂ | [50, 100] % | 74 |
| Frequência Cardíaca (Pulso) | [50, 350] bpm | 91 |
| Índice de Perfusão | [0, 20] | 70 |
| Hora | [0, 23] | 8 |

Um registo é considerado inválido se qualquer campo falhar estes critérios. Foram excluídos **242 registos (2,5%)**, resultando em **9 615 registos fisiologicamente válidos**. Para a determinação de elegibilidade e cálculo de carga de dessaturação, exige-se estritamente que a SpO₂ seja válida.

### 2c. Duplicados e timestamps

Identificaram-se **60 grupos (episódio, data, hora)** com leituras concorrentes no mesmo instante temporal. Estes registos foram consolidados pela **mediana** de cada sinal vital, garantindo robustez a leituras espúrias e eliminando a multiplicidade temporal.

Os formatos de data contemplam `DD/MM/YYYY`, `YYYY-MM-DD` e inversão de mês/dia `YYYY-DD-MM` quando mês > 12 (ex.: `2024-13-02`). O registo com data espúria `2024-02-31` em `EP016` é tratado como timestamp inválido.

---

## 3. Construção das variáveis e reconciliação clínica

### 3a. Features por episódio (dataset_final.csv)

Grão: 1 linha por episódio. Total de **47 episódios**:

| Coluna | Descrição |
|---|---|
| `sat_o2_{mean,std,min,max}` | Estatísticas de SpO₂ ao longo do episódio |
| `puls_rate_{mean,std,min,max}` | Estatísticas de frequência cardíaca |
| `perfusion_{mean,std,min,max}` | Estatísticas de índice de perfusão |
| `desat_count` | Contagem de medições com SpO₂ < 90% |
| `desat_pct` | Percentagem de medições com SpO₂ < 90% |
| `carga_dessaturacao` | $\sum (90 - \text{SpO}_2)$ para SpO₂ < 90% |
| `duracao_dias` | Nº de dias de calendário distintos com registos de sinais vitais (proxy operacional de monitorização; datas reais de admissão e alta hospitalar não constam dos dados brutos) |
| `n_registos` | Contagem de registos válidos no episódio |
| `pat_predominante` | Patologia com maior frequência de dias registados no episódio |
| `pat_label` | Código numérico da classe (0 a 5; -1 para episódios sem diagnóstico) |

### 3b. Reconciliação das patologias (EP001: Refluxo vs Displasia)

A patologia predominante é determinada pela contagem de dias registados para cada diagnóstico. Para o episódio `EP001`:
- **Refluxo Gastroesofágico:** 24 registos de `'Refluxo gastroesofágico'` + 1 de `'refluxo gastroesofagico'` + 1 de `'RGE'` = **26 registos**.
- **Displasia Broncopulmonar:** 23 registos de `'Displasia broncopulmonar'` + 2 de `'Displasia Broncopulmonar'` = **25 registos**.

Como 26 > 25, o diagnóstico predominante de `EP001` é legitimamente **Refluxo Gastroesofágico**. A Displasia Broncopulmonar aparece 38 vezes no ficheiro bruto, mas foi sempre superada em frequência noutros episódios (ex.: no `EP026`, a DMH teve 17 registos vs 13 de Displasia). Assim, a ausência de Displasia Broncopulmonar como patologia predominante em `metadata.csv` reflete a regra objetiva de prevalência individual.

Distribução das 6 classes predominantes (39 episódios):
1. Doença das Membranas Hialinas: 24 (61,5%)
2. Icterícia Neonatal: 7 (17,9%)
3. Citomegalovírus: 4 (10,3%)
4. Anemia: 2 (5,1%)
5. Refluxo Gastroesofágico: 1 (2,6%)
6. Persistência do Canal Arterial: 1 (2,6%)

---

## 4. Janela temporal e elegibilidade (dataset_regressao_24h.csv)

### 4a. Definição estrita das janelas

- **Âncora temporal ($t_0$):** primeiro timestamp com dados válidos no episódio. Nota metodológica: não corresponde necessariamente à admissão hospitalar (dado não registado), servindo como proxy de início da monitorização.
- **Janela inicial ($[0, 24\text{h}[$):** medições com $\Delta h = (t - t_0) < 24$ horas.
- **Janela futura ($[24\text{h}, +\infty[$):** medições com $\Delta h \ge 24$ horas.

As janelas são mutuamente exclusivas e temporalmente disjuntas.

### 4b. Critérios de elegibilidade

Para assegurar estabilidade na caracterização inicial e mensuração do desfecho futuro, um episódio só é elegível se cumprir:
1. **$\ge 5$ observações válidas de SpO₂** ($50 \le \text{SpO}_2 \le 100$) na janela inicial;
2. **$\ge 3$ observações válidas de SpO₂** ($50 \le \text{SpO}_2 \le 100$) na janela futura.

Total de episódios avaliados: 47.  
**Episódios elegíveis:** exatamente **40 episódios**.  
**Episódios excluídos (7):**
- `EP018`: SpO₂ inicial = 1 (< 5), SpO₂ futuro = 482 (insuficiência inicial);
- `EP042`: SpO₂ inicial = 1 (< 5), SpO₂ futuro = 172 (insuficiência inicial);
- `EP030`: SpO₂ inicial = 4 (< 5), SpO₂ futuro = 0 (< 3) (ambas insuficientes);
- `EP010`: SpO₂ inicial = 18, SpO₂ futuro = 0 (< 3) (sem seguimento futuro);
- `EP024`: SpO₂ inicial = 17, SpO₂ futuro = 0 (< 3) (sem seguimento futuro);
- `EP029`: SpO₂ inicial = 22, SpO₂ futuro = 0 (< 3) (sem seguimento futuro);
- `EP028`: SpO₂ inicial = 23, SpO₂ futuro = 2 (< 3) (seguimento futuro insuficiente).

### 4c. Variável-alvo analítica (`carga_dessaturacao_futura`)

$$\text{carga\_dessaturacao\_futura} = \sum_{\substack{t \ge 24\text{h} \\ 50 \le \text{SpO}_2 < 90}} (90 - \text{SpO}_2)$$

Esta métrica quantifica o **índice acumulado de défice de oxigenação pontual**. Não representa horas acumuladas de hipoxemia contínua, uma vez que a frequência de amostragem horária e os períodos sem registo não permitem integração temporal contínua exata.

---

## 5. Prevenção de Data Leakage e Tratamento de Dados

1. **Exclusão estrita de preditores futuros:** `carga_dessaturacao_futura`, `n_registos_futuro` e `n_spo2_futuro_validos` são expressamente excluídos da matriz de features.
2. **Exclusão de variáveis de episódio completo:** `duracao_dias`, `carga_dessaturacao`, `pat_predominante` e `pat_label` são excluídas da regressão preditiva às 24 horas.
3. **Imputação sem fuga de informação:** Qualquer valor omisso é imputado pela mediana calculada **estritamente sobre o conjunto de treino** (e dentro de cada fold na validação Leave-One-Out).
4. **Padronização Z-score:** Os parâmetros de média e desvio-padrão são derivados unicamente do conjunto de treino de cada iteração.

---

## 6. Datasets Finais Produzidos

| Ficheiro | Linhas | Colunas | Finalidade |
|---|---|---|---|
| `dataset_final.csv` | 47 | 20 | Agregado global do episódio (Clustering e Classificação) |
| `dataset_regressao_24h.csv` | 40 | 22 | Preditores das primeiras 24h + desfecho futuro (Regressão) |
| `train.csv` | 32 | 34 | Subconjunto de treino 80% (Classificação) |
| `test.csv` | 7 | 34 | Subconjunto de teste 20% (Classificação) |
| `metadata.csv` | 6 | 3 | Mapeamento das 6 classes predominantes e frequências |
| `normalisation_params.csv` | 14 | 3 | Parâmetros de escalonamento Z-score obtidos no treino |
| `sinais_vitais_limpo.csv` | 9 857 | 6 | Sinais vitais com identificadores normalizados |
| `patologias_limpo.csv` | 696 | 3 | Patologias com identificadores normalizados |
