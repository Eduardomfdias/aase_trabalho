# Data Preparation — AASE 2026/27

**Disciplina:** Aprendizagem Automática em Sistemas Empresariais  
**Fase CRISP-DM:** 4 — Data Preparation  
**Autores:** Eduardo Dias, Rui Carneiro  
**Data:** novembro de 2026

---

## 4. Data Preparation

### 4.1 Selecionar os Dados

#### 4.1.1 Critérios de Seleção dos Episódios

Foram considerados todos os **47 episódios** com registos de sinais vitais válidos após normalização de identificadores. Para o dataset de classificação e clustering, nenhum episódio é excluído à partida — os 8 episódios sem diagnóstico registado recebem o valor `pat_label = -1` e são mantidos no dataset geral, sendo excluídos apenas da partição treino/teste de classificação.

Para o **dataset de regressão preditiva** (janela 24h), é aplicado um critério de elegibilidade temporal adicional descrito em 4.1.3.

#### 4.1.2 Seleção das Variáveis Relevantes

Das seis colunas do ficheiro de sinais vitais, as três variáveis fisiológicas — SpO₂, frequência de pulso e índice de perfusão — constituem a base de todas as features numéricas. O identificador, a data e a hora são usados exclusivamente para agregação e construção das janelas temporais, não entrando como preditores nos modelos.

Das três colunas do ficheiro de patologias, apenas a coluna `patologia` é utilizada para construir o alvo de classificação, após normalização dos nomes.

#### 4.1.3 Definição das Janelas Temporais

Para o problema de regressão preditiva, os dados de cada episódio são divididos em duas janelas mutuamente exclusivas:

- **Janela inicial** $[0\text{h}, 24\text{h}[$: todas as medições com $\Delta h < 24$ horas a partir do primeiro timestamp válido do episódio. Usada para calcular os **preditores**.
- **Janela futura** $[24\text{h}, +\infty[$: todas as medições com $\Delta h \ge 24$ horas. Usada exclusivamente para calcular o **alvo** (`carga_dessaturacao_futura`).

**Âncora temporal ($t_0$):** o primeiro timestamp com data e hora válidas no episódio. Corresponde ao início da monitorização registada, não necessariamente à hora de admissão hospitalar (dado não disponível nos ficheiros).

#### 4.1.4 Exclusão de Episódios e Justificação

Para o dataset de regressão foram excluídos 7 dos 47 episódios por não cumprirem os critérios mínimos de cobertura:

| Episódio | SpO₂ válidos na janela inicial | SpO₂ válidos no futuro | Motivo |
|---|---|---|---|
| EP018 | 1 | 482 | Janela inicial insuficiente (< 5) |
| EP042 | 1 | 172 | Janela inicial insuficiente (< 5) |
| EP030 | 4 | 0 | Ambas as janelas insuficientes |
| EP010 | 18 | 0 | Sem dados futuros (< 3) |
| EP024 | 17 | 0 | Sem dados futuros (< 3) |
| EP029 | 22 | 0 | Sem dados futuros (< 3) |
| EP028 | 23 | 2 | Dados futuros insuficientes (< 3) |

O critério mínimo de **5 registos SpO₂ válidos na janela inicial** e **3 registos SpO₂ válidos na janela futura** foi definido para garantir que os preditores caracterizam de forma minimamente estável o estado fisiológico inicial e que o alvo é mensurado com cobertura suficiente.

---

### 4.2 Limpar os Dados

#### 4.2.1 Tratamento de Registos Duplicados

Identificaram-se **60 grupos (episódio, data, hora)** com dois registos simultâneos, totalizando 120 registos envolvidos. Para cada grupo, os três sinais vitais foram consolidados pelo valor **mediano** dos dois registos. A mediana foi escolhida pela sua robustez a leituras espúrias pontuais.

Resultado: de 9 857 registos brutos passou-se a **9 797 registos** após remoção dos duplicados por consolidação.

#### 4.2.2 Tratamento de Valores Inválidos

Aplicaram-se filtros de plausibilidade biológica a todos os registos:

| Variável | Intervalo fisiológico válido | Registos excluídos |
|---|---|---|
| SpO₂ | [50, 100] % | 74 |
| Frequência de Pulso | [50, 350] bpm | 91 |
| Índice de Perfusão | [0, 20] | 70 |
| Hora | [0, 23] | 8 |

Um registo é excluído se **qualquer** campo falhar estes critérios. Foram excluídos **242 registos (2,5%)**, resultando em **9 615 registos fisiologicamente válidos**. Esta estratégia de exclusão é preferida à imputação porque os valores fora de intervalo representam erros de sensor, não estados clínicos plausíveis — a sua imputação introduziria ruído artificial.

**Exceção para o cálculo de dessaturação:** o cálculo da carga de dessaturação e a contagem de episódios de SpO₂ < 90% requerem apenas que a SpO₂ seja válida. Registos com FC ou perfusão inválidas mas SpO₂ válida contribuem para estas métricas.

> **Gráfico 4.1 — Limpeza dos dados: volume de registos válidos vs inválidos e breakdown por tipo de problema**  
> *Fonte: `data_preparation.ipynb` → § 2 — Limpeza — exclusão de registos inválidos*

#### 4.2.3 Harmonização da Nomenclatura das Patologias

O ficheiro de patologias contém variantes ortográficas, de acentuação e abreviaturas para a mesma patologia (e.g., `'dmh'`, `'Doença das Membranas Hialinas'`, `'doenca das membranas hialinas'`). Foi construído um dicionário de mapeamento (`MAPA_PAT`) que normaliza todas as variantes para uma forma canónica:

| Variante nos dados | Forma canónica |
|---|---|
| `dmh`, `doenca das membranas hialinas` | Doença das Membranas Hialinas |
| `ictericia`, `icterícia`, `ictericia neonatal` | Icterícia Neonatal |
| `cmv`, `citomegalovirus` | Citomegalovírus |
| `rge`, `refluxo gastroesofagico` | Refluxo Gastroesofágico |
| `sepsis` | Sépsis |

Após normalização, contam-se **10 patologias distintas** no conjunto total dos dados.

#### 4.2.4 Tratamento de Valores em Falta

Os valores em falta em campos numéricos de sinais vitais (44 a 64 registos por campo, < 0,7%) são tratados como inválidos e excluídos conjuntamente com os valores fora de intervalo — não é realizada imputação nesta fase. Os 12 registos de patologias com campo vazio são excluídos das análises categóricas.

---

### 4.3 Construir Atributos

#### 4.3.1 Criação de Variáveis Temporais

A partir das colunas `data` e `hora`, foi construído um timestamp completo para cada registo. Os formatos de data foram normalizados com suporte a três padrões (`DD/MM/YYYY`, `YYYY-MM-DD` e `YYYY-DD-MM` quando o mês > 12). A duração do episódio (`duracao_dias`) é calculada como o número de **datas de calendário distintas** com pelo menos um registo de sinais vitais, o que serve como proxy operacional da duração de monitorização.

#### 4.3.2 Cálculo de Indicadores Fisiológicos

Para cada episódio, foram calculadas as seguintes estatísticas a partir dos registos válidos:

| Feature | Descrição |
|---|---|
| `sat_o2_{mean, std, min, max}` | Média, desvio-padrão, mínimo e máximo de SpO₂ |
| `puls_rate_{mean, std, min, max}` | Média, desvio-padrão, mínimo e máximo de frequência de pulso |
| `perfusion_{mean, std, min, max}` | Média, desvio-padrão, mínimo e máximo de índice de perfusão |
| `desat_count` | Número de registos com SpO₂ < 90% |
| `desat_pct` | Percentagem de registos com SpO₂ < 90% |

#### 4.3.3 Construção de Variáveis Derivadas

**Carga de dessaturação (episódio completo):**

$$\text{carga\_dessaturacao} = \sum_{\substack{i\,:\,\text{SpO}_2^{(i)} < 90}} \left(90 - \text{SpO}_2^{(i)}\right)$$

Mede o défice acumulado de oxigenação ao longo de todo o episódio. Não representa horas de hipoxemia contínua — a frequência de registo horária impede a integração temporal exacta.

**Carga de dessaturação futura (janela de regressão):**

$$\text{carga\_dessaturacao\_futura} = \sum_{\substack{t \ge 24\text{h} \\ 50 \le \text{SpO}_2^{(t)} < 90}} \left(90 - \text{SpO}_2^{(t)}\right)$$

Calculada exclusivamente na janela futura, é a variável-alvo do modelo de regressão. A separação estrita entre janelas garante que nenhuma informação futura entra nos preditores.

#### 4.3.4 Definição da Variável-Alvo

**Classificação — patologia predominante:**

Para cada episódio com diagnósticos registados, a patologia predominante é a que apresenta maior número de dias registados no episódio. Em caso de empate, seleciona-se a primeira por ordem alfabética (critério determinístico). Os 39 episódios com patologia distribuem-se por 6 classes:

| Classe | Patologia | Episódios | % |
|---|---|---|---|
| 0 | Doença das Membranas Hialinas | 24 | 61,5% |
| 1 | Icterícia Neonatal | 7 | 17,9% |
| 2 | Citomegalovírus | 4 | 10,3% |
| 3 | Anemia | 2 | 5,1% |
| 4 | Refluxo Gastroesofágico | 1 | 2,6% |
| 5 | Persistência do Canal Arterial | 1 | 2,6% |

A distribuição é desequilibrada, com a DMH a representar 61,5% dos episódios classificados.

**Regressão — carga de dessaturação futura:**

O alvo de regressão apresenta uma distribuição fortemente assimétrica: 28 dos 40 episódios elegíveis (70%) têm carga futura igual a zero (sem qualquer dessaturação após as primeiras 24h). O máximo é 85,57 e a média 3,45. Esta distribuição *zero-inflated* deve ser considerada na escolha e avaliação do modelo.

> **Gráfico 4.2 — Distribuição do alvo de regressão (carga_dessaturacao_futura): histograma com destaque para episódios com carga = 0**  
> *Fonte: `04_modeling/grafico_alvo_vs_cobertura.png` ou `data_preparation.ipynb` → § 7b — Dataset de regressão — janela 24h*

> **Gráfico 4.3 — Distribuição dos três alvos: duração do internamento, carga de dessaturação e patologia predominante**  
> *Fonte: `data_preparation.ipynb` → § 4 — Targets*

---

### 4.4 Integrar os Dados

#### 4.4.1 Integração dos Sinais Vitais e das Patologias

A integração é realizada pelo identificador do episódio (após normalização `norm_ep`). Para cada episódio com sinais vitais, procura-se o conjunto de diagnósticos no ficheiro de patologias. A ligação é de **muitos-para-muitos** ao nível de registo (múltiplas horas para um episódio, múltiplos dias para um episódio), pelo que a integração é efectuada após agregação separada de cada fonte ao grão do episódio.

#### 4.4.2 Agregação dos Registos por Episódio

A agregação produz um dataset com **1 linha por episódio** e 20 colunas: 2 de identificação, 14 features numéricas, e 4 colunas de alvos (`duracao_dias`, `carga_dessaturacao`, `pat_predominante`, `pat_label`).

#### 4.4.3 Verificação da Correspondência entre Episódios

| Indicador | Valor |
|---|---|
| Episódios com sinais vitais | 47 |
| Episódios com patologia definida | 39 |
| Episódios sem patologia (pat_label = −1) | 8 |
| Episódios elegíveis para regressão 24h | 40 |
| Episódios excluídos da regressão | 7 |

---

### 4.5 Formatar os Dados

#### 4.5.1 Normalização dos Tipos de Dados

Todos os valores numéricos são arredondados a 4 casas decimais. Os identificadores são convertidos para string maiúscula sem espaços. As datas são internamente representadas como objetos `date` do Python durante o processamento, sendo exportadas no formato original dos ficheiros de origem.

#### 4.5.2 Organização dos Conjuntos de Dados Finais

| Ficheiro | Linhas | Colunas | Finalidade |
|---|---|---|---|
| `dataset_final.csv` | 47 | 20 | Agregado global por episódio (Clustering e Classificação) |
| `dataset_regressao_24h.csv` | 40 | 22 | Preditores 24h + alvo futuro (Regressão) |
| `train.csv` | 32 | 34 | Subconjunto de treino 80% estratificado (Classificação) |
| `test.csv` | 7 | 34 | Subconjunto de teste 20% estratificado (Classificação) |
| `metadata.csv` | 6 | 3 | Mapeamento label → patologia + frequências |
| `normalisation_params.csv` | 14 | 3 | Parâmetros Z-score calculados no treino |
| `sinais_vitais_limpo.csv` | 9 857 | 6 | Sinais vitais com IDs normalizados (todos os registos) |
| `patologias_limpo.csv` | 696 | 3 | Patologias com IDs normalizados |

Os ficheiros `train.csv`, `test.csv` e `normalisation_params.csv` são produzidos na Fase 4 (Modelação).

#### 4.5.3 Preparação dos Dados para as Fases de Modelação

Foram identificadas as colunas que **não** devem ser usadas como preditores em cada problema, para prevenir fuga de informação (*data leakage*):

**Para regressão (dataset_regressao_24h.csv):**
- `episodio` — identificador
- `carga_dessaturacao_futura` — alvo
- `n_registos_futuro`, `n_spo2_futuro_validos` — informação do período futuro
- `desat_count`, `desat_pct` — redundantes com `carga_desat_janela`

**Para classificação (train/test.csv):**
- `episodio`, `pat_predominante` — identificadores e alvo não numérico
- `carga_dessaturacao`, `duracao_dias` — calculados com o episódio completo (disponíveis apenas após a monitorização total)

---

### 4.6 Validação dos Dados Preparados

A validação foi implementada num notebook dedicado (`validacao_data_preparation.ipynb`) que executa verificações automáticas sobre todos os ficheiros produzidos:

| Verificação | Resultado |
|---|---|
| Colunas únicas em todos os CSVs | ✅ |
| Features ∩ Targets = ∅ (sem leakage) | ✅ |
| Alvo de regressão não-negativo e finito | ✅ [0,00; 85,57] |
| Episódios únicos e não nulos no dataset de regressão | ✅ 40 |
| Todos os episódios com ≥ 5 SpO₂ válidos na janela inicial | ✅ |
| Todos os episódios com ≥ 3 SpO₂ válidos na janela futura | ✅ |
| Datasets originais intactos | ✅ 9 857 e 696 registos |

Foram também executados **10 testes de fronteira** sobre a lógica do pipeline (separação de janelas, cálculo da carga, critérios de elegibilidade), todos aprovados.

A cobertura de classes no split treino/teste revela uma limitação estrutural: três das seis classes (Anemia, Refluxo Gastroesofágico, Persistência do Canal Arterial) não têm representação no conjunto de teste, por terem apenas 1–2 episódios no total. Esta situação decorre da dimensão da amostra e não constitui um erro do pipeline — deve ser assumida como limitação na fase de avaliação dos modelos.

> **Gráfico 4.4 — Cobertura de classes no split treino/teste (barras agrupadas)**  
> *Fonte: `validacao_data_preparation.ipynb` → § 7 — Validação F — Integridade estrutural*

---

### 4.7 Síntese da Fase de Data Preparation

A fase de Data Preparation transformou dois ficheiros CSV de origem em oito datasets analíticos prontos para modelação, com as seguintes características:

- **Dataset principal** (`dataset_final.csv`): 47 episódios × 20 colunas, com 14 features numéricas e 4 colunas de alvos; sem valores omissos; sem normalização (aplicada na Fase 4).
- **Dataset de regressão** (`dataset_regressao_24h.csv`): 40 episódios elegíveis × 22 colunas; preditores estritamente da janela inicial; alvo calculado na janela futura; separação temporal garantida e verificada automaticamente.
- **Split de classificação**: 32 episódios de treino + 7 de teste, estratificado por patologia predominante; parâmetros de normalização calculados exclusivamente no treino.

As principais decisões metodológicas e as suas justificações estão documentadas em `notas_data_preparation.md`. As limitações identificadas — distribuição *zero-inflated* do alvo de regressão, desequilíbrio de classes, classes raras sem representação no teste — são estruturais e decorrentes da dimensão da amostra, devendo ser explicitamente assumidas na fase de avaliação.
