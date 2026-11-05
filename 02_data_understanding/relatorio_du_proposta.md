# Data Understanding — AASE 2026/27

**Disciplina:** Aprendizagem Automática em Sistemas Empresariais  
**Fase CRISP-DM:** 3 — Data Understanding  
**Autores:** Eduardo Dias, Rui Carneiro  
**Data:** novembro de 2026

---

## 3. Data Understanding

### 3.1 Recolher Dados Iniciais

#### 3.1.1 Identificação das Fontes de Dados

Os dados provêm de um sistema de monitorização contínua de uma unidade de neonatologia e cobrem o período de **janeiro a abril de 2024**. Foram disponibilizados dois ficheiros em formato CSV:

| Ficheiro | Descrição | Grão |
|---|---|---|
| `1_sinais_vitais_por_hora-1.csv` | Sinais fisiológicos horários por episódio de internamento | episódio × hora |
| `3_patologias_por_dia-1.csv` | Diagnósticos registados por dia de internamento | episódio × dia |

Cada episódio corresponde a um internamento neonatal pseudonimizado com um identificador do tipo `EP001` a `EP058`. Não foi utilizado nenhum dado de identificação pessoal.

#### 3.1.2 Processo de Recolha e Carregamento dos Dados

Os ficheiros foram carregados em Python com a biblioteca `csv` nativa. Não foi utilizada a biblioteca `pandas` por opção metodológica, recorrendo-se a `csv`, `statistics` e `collections` para toda a manipulação. O carregamento incluiu uma verificação inicial dos cabeçalhos, tipagem dos campos e registo de erros de parsing.

Durante o carregamento verificou-se que os identificadores de episódio apresentam **variantes de formatação** nos ficheiros originais: espaços à esquerda, espaços no meio e capitalização mista. Para garantir a consistência das análises, foi aplicada uma função de normalização determinística — `norm_ep()` — que remove espaços e converte para maiúsculas. Esta operação é realizada em memória, sem alterar os ficheiros originais.

#### 3.1.3 Caracterização Inicial dos Conjuntos de Dados

| Indicador | Sinais Vitais | Patologias |
|---|---|---|
| Registos brutos | 9 857 | 696 |
| IDs de episódio brutos (distintos) | 58 | 45 |
| IDs após normalização (`norm_ep`) | 47 | 39 |
| IDs com formatação irregular | 11 | 6 |
| Colunas | 6 | 3 |
| **Total de registos brutos** | **9 857** | **696** |
| **Total combinado** | **10 553** | — |

Após normalização, os dados de sinais vitais cobrem **47 episódios únicos** e os dados de patologias cobrem **39 episódios únicos**. Todos os 39 episódios com patologia estão presentes nos sinais vitais. Existem 8 episódios com sinais vitais mas sem qualquer diagnóstico registado.

---

### 3.2 Descrever os Dados

#### 3.2.1 Estrutura e Granularidade dos Dados

O ficheiro de sinais vitais regista, para cada episódio e cada hora, três variáveis fisiológicas contínuas. O ficheiro de patologias regista, para cada episódio e cada dia, o diagnóstico clínico observado. Os dois ficheiros partilham o identificador de episódio e a data como chaves de ligação, mas diferem na granularidade temporal (horária vs. diária).

#### 3.2.2 Descrição das Variáveis

**Sinais vitais:**

| Campo | Tipo | Descrição | Intervalo esperado |
|---|---|---|---|
| `episodio` | Categórico | Identificador do episódio de internamento | EP001–EP058 |
| `data` | Data | Data do registo (formatos variados) | Jan–Abr 2024 |
| `hora` | Numérico inteiro | Hora do registo | [0, 23] |
| `sat_o2` | Numérico real | Saturação de oxigénio (SpO₂) | [50, 100] % |
| `puls_rate` | Numérico real | Frequência de pulso | [50, 350] bpm |
| `perfusion` | Numérico real | Índice de perfusão | [0, 20] |

**Patologias:**

| Campo | Tipo | Descrição |
|---|---|---|
| `episodio` | Categórico | Identificador do episódio |
| `data` | Data | Data do diagnóstico |
| `patologia` | Categórico | Nome do diagnóstico |

#### 3.2.3 Dimensão e Cobertura dos Dados

O período de recolha abrange janeiro a abril de 2024, com distribuição mensal desigual: janeiro contém apenas 112 registos de sinais vitais (3 episódios), indicando que a monitorização se iniciou a meio do mês. Fevereiro, março e abril apresentam volumes semelhantes (entre 2 700 e 3 700 registos por mês) e entre 18 a 24 episódios ativos.

| Mês | Registos SV | Episódios ativos | Novos episódios |
|---|---|---|---|
| Janeiro 2024 | 112 | 3 | 3 |
| Fevereiro 2024 | 3 017 | 22 | 19 |
| Março 2024 | 3 737 | 24 | 18 |
| Abril 2024 | 2 746 | 20 | 18 |

#### 3.2.4 Estatísticas Descritivas Iniciais

**Sinais vitais (n = 9 615 registos válidos):**

| Variável | Média | Mediana | Desvio-padrão | Mínimo | Máximo |
|---|---|---|---|---|---|
| SpO₂ (%) | 95,98 | 96,26 | 2,25 | 82,2 | 100,0 |
| Frequência de Pulso (bpm) | 147,74 | 149,41 | 14,15 | 94,8 | 187,6 |
| Índice de Perfusão | 1,22 | 1,15 | 0,45 | 0,3 | 5,1 |

A SpO₂ apresenta valores predominantemente acima de 90%, com 119 registos de dessaturação — definida como SpO₂ < 90% — correspondendo a 1,2% dos registos válidos. A frequência de pulso situa-se na gama típica para neonatos. O índice de perfusão é assimétrico à direita, com mediana de 1,15 e alguns valores elevados (máximo 5,1) fisiologicamente plausíveis.

---

### 3.3 Explorar os Dados

#### 3.3.1 Distribuição dos Sinais Vitais

A SpO₂ concentra-se na gama [94–100%], com uma cauda esquerda correspondente aos episódios de dessaturação. O limiar clínico de 90% separa 119 registos (1,2%) do restante. A frequência de pulso segue uma distribuição aproximadamente simétrica centrada em 148 bpm. O índice de perfusão é fortemente assimétrico à direita: a maioria dos valores está abaixo de 2, com outliers até 5,1 que se mantêm dentro do intervalo fisiologicamente válido.

> **Gráfico 3.1 — Distribuição dos três sinais vitais (histogramas com limiar de dessaturação a SpO₂ = 90%)**  
> *Fonte: `eda_aase.ipynb` → § 4 — Distribuições dos sinais vitais*

#### 3.3.2 Evolução Temporal dos Sinais Vitais

A análise do padrão circadiano (médias horárias ao longo das 24 horas) revela variação moderada nos três sinais:

- **SpO₂:** oscila entre 95,6% (hora 7h) e 96,8% (hora 22h), sem tendência dominante;
- **Frequência de Pulso:** varia entre 143 bpm (madrugada) e 152 bpm (tarde), sugerindo actividade ligeiramente superior nas horas diurnas;
- **Perfusão:** mantém-se estável ao longo do dia (1,05–1,45), sem padrão circadiano evidente.

A nível mensal, a SpO₂ média permanece estável entre janeiro e abril (95,60%–96,06%), sem degradação ao longo do período de observação.

> **Gráfico 3.2 — Padrão circadiano: médias horárias de SpO₂, FC e perfusão**  
> *Fonte: `eda_aase.ipynb` → § 5a — Padrão Circadiano*

#### 3.3.3 Distribuição e Frequência das Patologias

Foram identificadas **10 patologias distintas** após normalização dos nomes (remoção de variantes ortográficas, acentuação e abreviaturas). A distribuição é fortemente desequilibrada:

| Patologia | Registos (episódio × dia) | % |
|---|---|---|
| Doença das Membranas Hialinas | 286 | 41,1% |
| Icterícia Neonatal | 169 | 24,3% |
| Anemia | 56 | 8,1% |
| Citomegalovírus | 51 | 7,3% |
| Displasia Broncopulmonar | 38 | 5,5% |
| Persistência do Canal Arterial | 32 | 4,6% |
| Refluxo Gastroesofágico | 28 | 4,0% |
| Sépsis | 19 | 2,7% |
| Lesão Renal Aguda | 3 | 0,4% |
| Retinopatia da Prematuridade | 2 | 0,3% |

As duas patologias mais frequentes (DMH e Icterícia Neonatal) representam 65,4% dos registos. Lesão Renal Aguda e Retinopatia da Prematuridade têm apenas 2–3 registos, o que limita a sua representatividade em qualquer modelo de classificação.

> **Gráfico 3.3 — Frequência das patologias (barras horizontais, ordenadas por frequência)**  
> *Fonte: `eda_aase.ipynb` → § 3b — Distribuição de patologias*

A análise de co-ocorrência mostra que muitos episódios apresentam múltiplos diagnósticos simultâneos. O par mais frequente é **DMH + Icterícia Neonatal** (17 episódios), seguido de Anemia + DMH e Anemia + Icterícia (4 episódios cada). Este padrão de comorbilidade implica a necessidade de uma regra explícita para selecionar a patologia predominante por episódio, o que é abordado na fase de Data Preparation.

> **Gráfico 3.4 — Heatmap de co-ocorrência de patologias (nº de episódios com cada par)**  
> *Fonte: `eda_aase.ipynb` → § 8b — Co-ocorrência de patologias*

#### 3.3.4 Relações entre Variáveis Fisiológicas

Os coeficientes de correlação de Pearson entre os três sinais vitais são fracos:

| Par de variáveis | r de Pearson |
|---|---|
| SpO₂ × Frequência de Pulso | −0,196 |
| SpO₂ × Índice de Perfusão | −0,161 |
| Frequência de Pulso × Índice de Perfusão | +0,021 |

A associação negativa SpO₂–FC é clinicamente plausível (taquicardia compensatória em resposta à hipoxemia), mas de magnitude reduzida. A quasi-nulidade da correlação FC–Perfusão sugere independência prática entre estas variáveis ao nível de registo horário.

**Nota metodológica:** estas correlações são calculadas sobre 9 615 observações provenientes de apenas 47 episódios, com múltiplas medições por episódio. As observações de um mesmo episódio não são independentes entre si, pelo que os coeficientes não devem ser interpretados como se proviessem de 9 615 pacientes independentes.

A análise de sinais vitais médios por episódio por patologia mostra diferenças modestas entre grupos: a **Anemia** apresenta a maior taxa de dessaturação (1,86%) e a **Citomegalovírus** a menor (0,16%). A sobreposição entre grupos é considerável, o que antecipa limitações no poder discriminativo dos sinais vitais como único preditor da patologia.

#### 3.3.5 Principais Observações da Análise Exploratória

1. Os sinais vitais são estáveis e fisiologicamente plausíveis na sua maioria (97,5% de registos válidos).
2. As dessaturações são eventos raros (1,2%), o que implica uma distribuição muito assimétrica para qualquer variável-alvo baseada nelas.
3. A heterogeneidade de duração dos episódios (1–37 dias, mediana 7) e de número de registos por episódio (4–830, mediana 142) é um fator estrutural relevante: episódios mais longos acumulam mais oportunidade de registar dessaturações.
4. A co-morbilidade é frequente, exigindo uma regra de desambiguação para a patologia predominante.
5. As correlações entre sinais vitais são fracas, sugerindo que os três sinais transportam informação parcialmente complementar.

---

### 3.4 Verificar a Qualidade dos Dados

#### 3.4.1 Valores em Falta e Registos Incompletos

**Sinais vitais:**

| Campo | Registos com valor vazio ou não numérico | % |
|---|---|---|
| sat_o2 | 44 | 0,4% |
| puls_rate | 64 | 0,6% |
| perfusion | 42 | 0,4% |
| episodio, data, hora | 0 | 0,0% |

**Patologias:** 12 registos (1,7%) têm o campo `patologia` em branco. Estes são excluídos das análises categóricas mas a linha episódio × dia é mantida para fins de contagem de cobertura temporal.

Os valores em falta nos campos numéricos de sinais vitais correspondem a registos em que o sensor não produziu uma leitura válida. São tratados como inválidos conjuntamente com os valores fora de intervalo (ver 3.4.2).

#### 3.4.2 Valores Fora dos Intervalos de Validade

Foram definidos intervalos de plausibilidade biológica para neonatologia, que servem simultaneamente como critério de validação:

| Variável | Intervalo válido | Registos inválidos | % |
|---|---|---|---|
| SpO₂ | [50, 100] % | 74 | 0,75% |
| Frequência de Pulso | [50, 350] bpm | 91 | 0,92% |
| Índice de Perfusão | [0, 20] | 70 | 0,71% |
| Hora | [0, 23] | 8 | 0,08% |

Um registo é excluído se **qualquer** campo falhar os critérios — a validade é conjunta. Após filtragem, o dataset conta com **9 615 registos válidos (97,5%)** e **242 excluídos (2,5%)**.

**Nota importante:** valores estatisticamente extremos mas fisiologicamente possíveis (e.g., SpO₂ de 83% ou FC de 185 bpm) são **mantidos**, pois correspondem a estados clínicos reais e informativos para os modelos.

#### 3.4.3 Duplicados e Inconsistências

Identificaram-se **60 grupos (episódio, data, hora)** com dois registos simultâneos no ficheiro de sinais vitais, totalizando 120 registos envolvidos. Estes correspondem provavelmente a leituras redundantes do sistema de monitorização. A resolução deste problema é realizada na fase de Data Preparation (ver secção 4.2.1).

Adicionalmente, detetaram-se inconsistências nos formatos de data:
- Formato `DD/MM/YYYY` (maioritário);
- Formato `YYYY-MM-DD` (padrão ISO);
- Formato `YYYY-MM-DD` com mês > 12, interpretado como `YYYY-DD-MM` (ex.: `2024-13-02` = 13 de fevereiro).

Um registo apresenta uma data inválida que não pode ser interpretada por qualquer dos formatos acima — é excluído da análise temporal mas mantido para estatísticas agregadas do episódio.

#### 3.4.4 Consistência entre Fontes de Dados

| Indicador | Valor |
|---|---|
| Episódios com sinais vitais (após normalização) | 47 |
| Episódios com patologias (após normalização) | 39 |
| Episódios presentes em ambos os ficheiros | 39 |
| Episódios apenas com sinais vitais (sem diagnóstico) | 8 |
| Episódios apenas com patologias (sem sinais vitais) | 0 |

A cobertura temporal cruzada ao nível de dia×episódio revela lacunas bidirecionais: existem dias em que há sinais vitais registados mas nenhum diagnóstico, e dias em que há diagnósticos mas sem sinais vitais. Estas lacunas podem refletir diferenças no protocolo de registo entre equipas ou períodos de alta temporária, e não necessariamente ausência de dados.

#### 3.4.5 Síntese dos Problemas de Qualidade Identificados

| Problema | Dimensão | Estratégia de resolução |
|---|---|---|
| IDs com formatação irregular | 11 em SV, 6 em Pat | Normalização `norm_ep()` em memória |
| Nomes de patologias com variantes | Múltiplas abreviaturas e acentuações | Dicionário `MAPA_PAT` + `norm_pat()` |
| Registos com valores em falta ou inválidos | 242 (2,5%) | Exclusão |
| Timestamps duplicados | 60 grupos (120 registos) | Consolidação pela mediana |
| Formatos de data múltiplos | 3 formatos distintos + 1 inválido | Parser com fallback por ordem |
| Episódios sem diagnóstico | 8 episódios | Mantidos em dataset geral, excluídos do split de classificação |

---

### 3.5 Síntese da Fase de Data Understanding

A análise exploratória permitiu caracterizar o conjunto de dados de forma abrangente e fundamentar as decisões de preparação. Os principais resultados são:

- Os dados cobrem **47 episódios de internamento neonatal** num período de quatro meses, com um total de 9 615 registos fisiológicos válidos após limpeza.
- A qualidade global dos dados é elevada (97,5% de registos válidos), com problemas localizados e tratáveis: formatação irregular de identificadores, duplicados temporais, e uma pequena percentagem de leituras fora dos limites fisiológicos.
- As dessaturações (SpO₂ < 90%) são **eventos raros** (1,2% dos registos), o que condiciona a distribuição da variável-alvo de regressão.
- A distribuição das patologias é desequilibrada, com predominância da DMH (41,1% dos registos). Quatro classes têm representação muito reduzida a nível de episódio, o que limita a generalização de modelos de classificação.
- As correlações entre sinais vitais são fracas, sendo os três sinais parcialmente independentes entre si.
- A heterogeneidade de duração e volume de observações por episódio é um fator estrutural que influencia diretamente a construção dos alvos de regressão e a elegibilidade temporal dos episódios.

Estas conclusões fundamentam diretamente as decisões de limpeza, transformação e construção de variáveis descritas na fase seguinte.
