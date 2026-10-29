# Data Understanding — AASE 2026/27

**Disciplina:** Aprendizagem Automática em Sistemas Empresariais  
**Fase CRISP-DM:** 2 — Data Understanding  
**Data:** 2026-10-29

---

## 1. Fonte e descrição dos dados

Os dados provêm de um sistema de monitorização contínua de neonatologia e cobrem o período de **janeiro a abril de 2024**. São disponibilizados em dois ficheiros CSV:

| Ficheiro | Grão | Registos brutos | Colunas |
|---|---|---|---|
| `1_sinais_vitais_por_hora-1.csv` | episódio × hora | 9 857 | episodio, data, hora, sat_o2, puls_rate, perfusion |
| `3_patologias_por_dia-1.csv` | episódio × dia | 696 | episodio, data, patologia |

O ficheiro de sinais vitais regista três variáveis fisiológicas — saturação de oxigénio (SpO₂), frequência de pulso (FC) e índice de perfusão — para cada hora de observação de cada episódio. O ficheiro de patologias contém o diagnóstico registado para cada dia de cada episódio.

Os identificadores de episódio apresentam variantes de formatação nos ficheiros originais: dos 58 identificadores brutos presentes nos sinais vitais, 11 têm formatação irregular (espaços, capitalização mista, e.g., `EP 016`, `ep018`). Após normalização com a função `norm_ep()`, os dados correspondem a **47 episódios únicos**.

---

## 2. Qualidade dos dados

### 2a. Valores em falta

Nos sinais vitais, os campos numéricos apresentam uma taxa residual de valores em falta (vazios ou não conversíveis):

| Campo | Nulos | % |
|---|---|---|
| sat_o2 | 44 | 0,4% |
| puls_rate | 64 | 0,6% |
| perfusion | 42 | 0,4% |
| episodio, data, hora | 0 | 0,0% |

No ficheiro de patologias, 12 registos (1,7%) têm o campo `patologia` em branco — estes são excluídos das análises categóricas mas mantêm a linha de episódio × dia para fins de contagem de cobertura.

### 2b. Valores fora de intervalo

Foram definidos limites fisiológicos para validação de cada variável:

| Variável | Intervalo válido | Registos inválidos | % |
|---|---|---|---|
| SpO₂ | [50, 100] % | 74 | 0,75% |
| Frequência de Pulso | [50, 350] bpm | 91 | 0,92% |
| Perfusão | [0, 20] | 70 | 0,71% |
| Hora | [0, 23] | 8 | 0,08% |

Um registo é excluído se qualquer campo falhar os critérios de validade. Após filtragem, o dataset de sinais vitais conta com **9 615 registos válidos (97,5%)** e **242 excluídos (2,5%)**.

---

## 3. Estatísticas descritivas

### 3a. Sinais vitais (registos válidos, n = 9 615)

| Variável | Média | Mediana | Desvio-padrão | Mínimo | Máximo |
|---|---|---|---|---|---|
| SpO₂ (%) | 95,98 | 96,26 | 2,25 | 82,2 | 100,0 |
| Freq. Pulso (bpm) | 147,74 | 149,41 | 14,15 | 94,8 | 187,6 |
| Perfusão | 1,22 | 1,15 | 0,45 | 0,3 | 5,1 |

A SpO₂ distribui-se predominantemente acima de 90%, com apenas **119 registos de dessaturação (1,2%)** — definida como SpO₂ < 90%. A frequência de pulso está concentrada entre 130 e 170 bpm, compatível com valores neonatais. O índice de perfusão apresenta distribuição assimétrica à direita com mediana de 1,15.

### 3b. Patologias (após normalização)

Foram identificadas **10 patologias distintas** após normalização dos nomes (remoção de variantes ortográficas, acentuação e abreviaturas):

| Patologia | Registos (episódio × dia) |
|---|---|
| Doença das Membranas Hialinas | 286 |
| Icterícia Neonatal | 169 |
| Anemia | 56 |
| Citomegalovírus | 51 |
| Displasia Broncopulmonar | 38 |
| Persistência do Canal Arterial | 32 |
| Refluxo Gastroesofágico | 28 |
| Sépsis | 19 |
| Lesão Renal Aguda | 3 |
| Retinopatia da Prematuridade | 2 |

A distribuição é fortemente desequilibrada: as duas patologias mais frequentes (DMH e Icterícia) representam 67% dos registos. Lesão Renal Aguda e Retinopatia da Prematuridade têm apenas 2–3 registos, o que limita a sua representatividade em modelos de classificação.

---

## 4. Distribuições

A SpO₂ tem distribuição concentrada na gama alta [94–100%], com uma cauda esquerda correspondente às dessaturações. A frequência de pulso segue uma distribuição aproximadamente normal centrada em 148 bpm. O índice de perfusão é fortemente assimétrico, com a maioria dos valores abaixo de 2 e alguns outliers até 5,1 (dentro do intervalo válido).

Os limiares clínicos relevantes são SpO₂ = 90% (limiar de dessaturação) e FC ∈ [100, 180] bpm para neonatos — os dados estão globalmente dentro destes intervalos, com exceção dos registos inválidos já identificados.

---

## 5. Padrões temporais

### 5a. Padrão circadiano

As médias horárias revelam variação circadiana moderada em todos os sinais vitais. A SpO₂ oscila entre 95,6% e 96,8% ao longo do dia; a FC apresenta variação ligeiramente mais acentuada (143–152 bpm). A perfusão mantém-se estável ao longo das 24 horas.

### 5b. Tendência mensal (jan–abr 2024)

| Mês | Registos | Episódios ativos | Novos episódios | SpO₂ média |
|---|---|---|---|---|
| Jan 2024 | 112 | 3 | 3 | 95,60% |
| Fev 2024 | 3 017 | 22 | 19 | 95,94% |
| Mar 2024 | 3 737 | 24 | 18 | 95,96% |
| Abr 2024 | 2 746 | 20 | 18 | 96,06% |

Janeiro tem volume reduzido (112 registos, 3 episódios), indicando que a recolha de dados foi iniciada a meio do mês. Fevereiro a abril têm distribuição homogénea. A SpO₂ média é estável entre meses, sem tendência de degradação ao longo do período.

---

## 6. Correlações entre variáveis

| Par de variáveis | r de Pearson |
|---|---|
| SpO₂ × FC | −0,196 |
| SpO₂ × Perfusão | −0,161 |
| FC × Perfusão | +0,021 |

As correlações entre sinais vitais são fracas. A associação negativa SpO₂–FC é clinicamente plausível (taquicardia compensatória durante hipóxia), mas de magnitude reduzida. A quasi-nulidade da correlação FC–Perfusão sugere independência entre estas variáveis ao nível de registo horário.

É importante notar que estas correlações são calculadas sobre 9 615 observações de apenas 47 episódios, com múltiplas medições por episódio. As observações de um mesmo episódio são dependentes entre si, pelo que os coeficientes de Pearson não devem ser interpretados como se proviessem de 9 615 pacientes independentes.

---

## 7. Relação entre datasets

Após normalização dos identificadores:

| Indicador | Valor |
|---|---|
| Episódios com sinais vitais | 47 |
| Episódios com patologias | 45 (brutos) → 40 únicos normalizados |
| Episódios presentes em ambos | 40 |
| Episódios apenas com sinais vitais | 18 (brutos, incluindo duplicados de ID) → 7 únicos reais |
| Episódios apenas com patologias | 5 |

A cobertura cruzada ao nível de dia×episódio revela lacunas: existem **86 dias-episódio com sinais vitais mas sem patologia registada**, e **111 dias-episódio com patologia mas sem sinais vitais**. Estas lacunas não representam necessariamente ausência de dados — podem refletir dias de alta/readmissão ou falhas pontuais de registo.

---

## 8. Co-variação

### 8a. Sinais vitais por patologia

| Patologia | n episódios | SpO₂ média | FC média | % dessaturações |
|---|---|---|---|---|
| Doença das Membranas Hialinas | 29 | 96,42% | 143,6 bpm | 0,64% |
| Icterícia Neonatal | 21 | 96,57% | 144,6 bpm | 0,59% |
| Anemia | 7 | 96,16% | 148,2 bpm | 1,86% |
| Citomegalovírus | 7 | 96,83% | 145,4 bpm | 0,16% |
| Persistência do Canal Arterial | 3 | 95,82% | 145,6 bpm | 0,48% |
| Sépsis | 3 | 96,88% | 139,5 bpm | 0,49% |

Anemia apresenta a maior taxa de dessaturação (1,86%), enquanto Citomegalovírus tem a menor (0,16%). As diferenças entre patologias são modestas, o que limita o poder discriminativo dos sinais vitais como preditores da patologia.

### 8b. Co-ocorrência de patologias

O par mais frequente é **Doença das Membranas Hialinas + Icterícia Neonatal** (17 episódios), seguido de Anemia + DMH e Anemia + Icterícia Neonatal (4 episódios cada). A co-morbilidade é frequente — muitos episódios apresentam 2 ou mais diagnósticos simultâneos, o que levanta a necessidade de definir uma regra de patologia predominante para classificação.

---

## 9. Estrutura das entidades observadas

A duração dos internamentos varia consideravelmente:

| Indicador | Valor |
|---|---|
| Duração mínima | 1 dia |
| Duração máxima | 37 dias |
| Duração média | 9,9 dias |
| Duração mediana | 7 dias |
| Observações por episódio (mín/máx/média/mediana) | 4 / 830 / 204,6 / 142 |

A heterogeneidade de duração e volume de registos por episódio é um fator estrutural importante: episódios mais longos acumulam naturalmente mais observações e, consequentemente, mais oportunidade de registar dessaturações. Este efeito deve ser tido em conta na definição e interpretação da variável-alvo de regressão.

---

## 10. Conclusões e impacto na preparação

A análise exploratória fundamenta as seguintes decisões na fase de Data Preparation:

1. **Normalização de IDs obrigatória** — 11 variantes de identificador nos sinais vitais e 6 nas patologias exigem uma função de normalização (`norm_ep`) antes de qualquer junção entre datasets.

2. **Filtros fisiológicos** — a presença de 242 registos inválidos (2,5%) justifica a aplicação de limites de validade [SpO₂∈[50,100], FC∈[50,350], Perfusão∈[0,20], Hora∈[0,23]] como etapa de limpeza.

3. **Resolução de duplicados por mediana** — 60 grupos (episódio, data, hora) tinham dois registos, consolidados pela mediana de cada sinal vital para evitar duplicação de horas na janela temporal.

4. **Patologia predominante por episódio** — a co-ocorrência frequente de múltiplas patologias exige uma regra de seleção (patologia com mais dias registados por episódio) para o alvo de classificação.

5. **Variável-alvo de regressão: carga de dessaturação futura** — definida como Σ(90−SpO₂) para registos com SpO₂ < 90%, calculada exclusivamente na janela posterior às primeiras 24 horas. A baixa frequência de dessaturações (1,2%) e a heterogeneidade de duração antecedem uma distribuição do alvo com concentração de zeros.

6. **Critério de elegibilidade temporal** — a variabilidade no número de observações por episódio (4 a 830) implica que nem todos os episódios têm cobertura suficiente para construir preditores fiáveis nas primeiras 24 horas. O critério mínimo (≥5 registos SpO₂ válidos na janela inicial, ≥3 na janela futura) deve ser aplicado explicitamente.

7. **Âncora temporal** — a hora de admissão clínica não está disponível nos dados. O primeiro timestamp válido do episódio é usado como aproximação de t₀, com a limitação que a diferença entre admissão real e primeiro registo pode variar entre episódios.
