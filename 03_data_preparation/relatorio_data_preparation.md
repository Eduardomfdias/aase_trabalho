# Data Preparation — AASE 2026/27

**Disciplina:** Aprendizagem Automática em Sistemas Empresariais  
**Fase CRISP-DM:** 3 — Data Preparation  
**Data:** 2026-10-29

---

## 1. Visão geral do pipeline

O pipeline de preparação transforma os dois ficheiros CSV de origem num conjunto de datasets analíticos prontos para modelação. O processo é implementado em `data_preparation.ipynb` e segue esta sequência:

```
Ficheiros CSV originais
  → Normalização de IDs e patologias
  → Filtros fisiológicos e tratamento de duplicados
  → Agregação por episódio (dataset_final.csv)
  → Construção da janela temporal 24h (dataset_regressao_24h.csv)
  → Normalização Z-score e divisão treino/teste
  → Datasets exportados
```

Todos os datasets produzidos têm o episódio como unidade de observação. Nenhuma informação futura entra nos preditores.

---

## 2. Tratamento de qualidade

### 2a. Normalização de identificadores

Os ficheiros originais contêm 58 identificadores brutos nos sinais vitais e 45 nas patologias, com variantes de formatação: espaços iniciais, espaços internos e capitalização mista (e.g., `' EP011'`, `'EP 016'`, `'ep018'`). A função `norm_ep(id)` remove espaços e converte para maiúsculas, produzindo **47 episódios únicos** nos sinais vitais e **40 episódios únicos** nas patologias após resolução de colisões.

### 2b. Filtros fisiológicos

São aplicados limites de validade a cada registo de sinais vitais:

| Variável | Intervalo válido | Registos excluídos |
|---|---|---|
| SpO₂ | [50, 100] % | 74 |
| Frequência de Pulso | [50, 350] bpm | 91 |
| Perfusão | [0, 20] | 70 |
| Hora | [0, 23] | 8 |

Um registo é excluído se qualquer campo falhar os critérios. O total de exclusões é **242 registos (2,5%)**, resultando em **9 615 registos válidos**. Para o cálculo da carga de dessaturação, apenas se exige que a SpO₂ seja válida — registos com FC ou perfusão inválidas mas SpO₂ válida contribuem para as métricas de dessaturação do episódio.

### 2c. Duplicados e timestamps

Foram identificados **60 grupos (episódio, data, hora) com dois registos cada**. Estes são consolidados pela **mediana** de cada sinal vital, eliminando a ambiguidade temporal sem perder informação fisiológica. A mediana é robusta a leituras espúrias pontuais.

Os timestamps de data são reconhecidos nos formatos `DD/MM/YYYY` e `YYYY-MM-DD`. Um caso especial identificado: datas no formato `YYYY-MM-DD` com mês > 12 (e.g., `2024-13-02`) são reinterpretadas como `YYYY-DD-MM`. Registos com data inválida são excluídos.

---

## 3. Construção das variáveis

### 3a. Features por episódio (dataset_final.csv)

Para cada episódio, são calculadas estatísticas agregadas sobre todos os registos válidos:

| Coluna | Descrição |
|---|---|
| `sat_o2_{mean,std,min,max}` | Média, desvio-padrão, mínimo e máximo de SpO₂ |
| `puls_rate_{mean,std,min,max}` | Idem para frequência de pulso |
| `perfusion_{mean,std,min,max}` | Idem para índice de perfusão |
| `desat_count` | Nº de registos com SpO₂ < 90% |
| `desat_pct` | % de registos com SpO₂ < 90% |
| `carga_dessaturacao` | Σ(90−SpO₂) para SpO₂ < 90% (episódio completo) |
| `duracao_dias` | Nº de dias distintos com registo |
| `n_registos` | Total de registos válidos |
| `pat_predominante` | Patologia com mais dias registados no episódio |
| `pat_label` | Código numérico da patologia (por frequência descendente) |

O `dataset_final.csv` contém **47 episódios** e é usado para classificação e clustering.

### 3b. Variável-alvo de regressão (carga_dessaturacao_futura)

A variável-alvo é definida como:

$$\text{carga} = \sum_{i:\,\text{SpO}_{2,i} < 90,\, t_i \geq t_0 + 24h} (90 - \text{SpO}_{2,i})$$

Esta fórmula calcula um **índice acumulado de défice de saturação** na janela temporal posterior às primeiras 24 horas de monitorização. A unidade é adimensional (soma de desvios percentuais). A definição é consistente em todos os notebooks e ficheiros CSV.

### 3c. Variável-alvo de classificação (pat_predominante)

A patologia predominante por episódio é selecionada pela regra **"patologia com mais dias registados"**. Em caso de empate, é escolhida a patologia com maior frequência global no dataset. Esta regra produz **6 classes** no conjunto de episódios elegíveis para classificação (após aplicação dos critérios de elegibilidade), distintas das 10 patologias presentes nos dados brutos normalizados.

---

## 4. Janela temporal (dataset_regressao_24h.csv)

### 4a. Definição das janelas

O problema de previsão é estruturado em duas janelas temporais disjuntas por episódio:

- **Âncora temporal (t₀):** primeiro timestamp válido do episódio. Nota: a hora de admissão clínica não está disponível nos dados; o primeiro registo é usado como aproximação, com a limitação de que o intervalo entre admissão e primeira medição pode variar.
- **Janela inicial:** registos com `delta_h < 24h` (relativo a t₀). Os preditores são calculados exclusivamente nesta janela.
- **Janela futura:** registos com `delta_h ≥ 24h`. O alvo é calculado exclusivamente nesta janela.

As duas janelas não se sobrepõem: a medição exatamente na fronteira (delta_h = 24h) pertence à janela futura.

### 4b. Critérios de elegibilidade

Um episódio é incluído no `dataset_regressao_24h.csv` se satisfizer ambas as condições:

1. **≥ 5 registos SpO₂ válidos** na janela inicial (primeiras 24 horas)
2. **≥ 3 registos SpO₂ válidos** na janela futura

O critério anterior (≥1 registo em cada janela) foi revisto após auditoria metodológica: os episódios EP018 e EP042 tinham apenas **1 registo** na janela inicial — insuficiente para caracterizar o estado fisiológico neonatal nas primeiras 24 horas. O limiar ≥5 foi definido com base na capacidade mínima de representação, não para otimizar métricas de modelação.

Episódios excluídos e motivos:

| Episódio | Motivo |
|---|---|
| EP018 | 1 registo SpO₂ válido na janela inicial |
| EP042 | 1 registo SpO₂ válido na janela inicial |
| EP010, EP024, EP029, EP030 | Sem cobertura temporal suficiente (ausência de dados futuros) |

### 4c. Episódios elegíveis

Após aplicação dos critérios, o `dataset_regressao_24h.csv` contém **≤43 episódios** (valor exato depende da última execução do notebook com o critério ≥5/≥3). Cada linha corresponde a um único episódio, com os preditores da janela inicial e o alvo da janela futura.

---

## 5. Normalização e divisão treino/teste

**Normalização Z-score:** calculada exclusivamente sobre o conjunto de treino. Os parâmetros (média e desvio-padrão por feature) são armazenados em `normalisation_params.csv` e aplicados ao conjunto de teste sem recalculação, evitando data leakage do teste para o treino.

**Divisão treino/teste para classificação:** split estratificado 80/20 por patologia predominante, produzindo `train.csv` (32 episódios) e `test.csv` (7 episódios). A estratificação garante representação de cada classe em ambos os conjuntos.

**Split para regressão:** implementado internamente no notebook de modelação sobre o `dataset_regressao_24h.csv`, com a mesma proporção 80/20.

---

## 6. Datasets produzidos

| Ficheiro | Linhas | Descrição | Uso |
|---|---|---|---|
| `dataset_final.csv` | 47 | Agregado completo por episódio | Classificação, Clustering |
| `dataset_regressao_24h.csv` | ≤43 | Preditores 24h + alvo futuro | Regressão |
| `train.csv` | 32 | Split treino (classificação) | Treino de modelos de classificação |
| `test.csv` | 7 | Split teste (classificação) | Avaliação de classificação |
| `sinais_vitais_limpo.csv` | 9 857 | IDs normalizados, todos os registos | Referência / auditoria |
| `patologias_limpo.csv` | 696 | IDs normalizados | Referência / auditoria |
| `normalisation_params.csv` | 14 | Parâmetros Z-score do treino | Aplicação em produção/teste |

---

## 7. Limitações e decisões metodológicas

**Âncora temporal aproximada.** O primeiro timestamp válido do episódio é usado como proxy da hora de admissão clínica. Esta aproximação é aplicada de forma consistente em todos os episódios, mas a diferença entre admissão real e primeiro registo não é quantificável com os dados disponíveis. Episódios onde a monitorização começou tarde relativamente à admissão podem ter preditores que representam um estado fisiológico posterior às "primeiras 24 horas" clínicas.

**Sensibilidade do alvo à frequência de observação.** A variável-alvo `carga_dessaturacao_futura` é uma soma acumulada: episódios com mais registos futuros têm maior oportunidade de acumular carga, independentemente da gravidade clínica. O número de registos futuros varia de 2 a 818 entre episódios. Esta confusão entre cobertura e gravidade clínica não é corrigida no pipeline atual e deve ser assumida explicitamente na interpretação dos resultados de modelação.

**Concentração de zeros no alvo.** 30 dos 43 episódios (70%) têm `carga_dessaturacao_futura = 0`, uma vez que não apresentam SpO₂ < 90% na janela futura. Esta distribuição condiciona fortemente a modelação: um preditor constante que preveja sempre 0 obtém um erro absoluto médio próximo de zero, e os modelos aprendidos não conseguem necessariamente superar este baseline. A conclusão metodológica correta é que a utilidade preditiva dos modelos treinados não fica demonstrada apenas com as métricas obtidas neste dataset.

**Variáveis excluídas dos preditores por risco de leakage.** As seguintes colunas não são usadas como features de regressão: `episodio` (identificador), `carga_dessaturacao_futura` (alvo), `n_registos_futuro` (conhecida apenas após o período futuro), `duracao_dias` e `pat_predominante` (calculadas com o episódio completo).
