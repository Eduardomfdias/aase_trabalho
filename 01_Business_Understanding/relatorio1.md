# AASE — Análise de Sinais e Episódios Clínicos

*Business Understanding*

Eduardo Dias – pg61456 · Gonçalo Pinto – pg65643 · Lucas Costa – pg65650 · Rui Carneiro – pg63791

2026/27 — Outubro de 2026

---

## Resumo

O presente relatório documenta a fase de Business Understanding do projeto AASE - Análise de Sinais e Episódios Clínicos, desenvolvido no âmbito da unidade curricular de Aprendizagem Automática em Sistemas Empresariais. O projeto aplica a metodologia CRISP-DM a registos clínicos de 58 episódios de internamento numa unidade de neonatologia, com o objetivo de extrair conhecimento útil para a prática assistencial a partir de sinais vitais e diagnósticos registados em contínuo. Nesta fase definiram-se três objetivos clínicos: estratificação do risco dos doentes, estimação da duração do internamento e apoio ao diagnóstico diferencial, que se traduzem em três problemas analíticos: agrupamento não supervisionado, regressão e classificação. São ainda identificados os recursos disponíveis, os riscos principais (desequilíbrio de classes e dimensão reduzida da amostra) e as respetivas estratégias de mitigação. O documento conclui com o plano das seis fases CRISP-DM e a avaliação inicial das ferramentas a utilizar.

**Palavras-chave:** CRISP-DM, prospeção de dados, neonatologia, sinais vitais, agrupamento, regressão, classificação, aprendizagem automática

---

## Abstract

This report documents the Business Understanding phase of the AASE project — Analysis of Clinical Signals and Episodes — developed in the context of the Machine Learning in Enterprise Systems course. The project applies the CRISP-DM methodology to clinical records from 58 neonatal inpatient episodes, aiming to extract actionable knowledge from continuously monitored vital signs and clinical diagnoses. Three clinical objectives were defined: patient risk stratification, prediction of length of stay, and support for differential diagnosis. These translate into three analytical problems: unsupervised clustering, regression, and classification. Key risks — class imbalance and small sample size — are identified along with mitigation strategies. The document concludes with the project plan for all six CRISP-DM phases and an initial assessment of tools and techniques.

**Keywords:** CRISP-DM, data mining, neonatology, vital signs, clustering, regression, classification, machine learning

---

## Abreviaturas, Siglas e Acrónimos

| Abreviatura / Sigla | Designação |
| --- | --- |
| AASE | Análise de Sinais e Episódios Clínicos |
| CSV | *Comma-Separated Values* |
| CRISP-DM | *Cross-Industry Standard Process for Data Mining* |
| DM | *Data Mining* |
| FC | Frequência cardíaca |
| IP | Índice de perfusão |
| MAE | *Mean Absolute Error* |
| ODM | Objetivo de Mineração de Dados |
| ON | Objetivo de Negócio |
| R² | Coeficiente de determinação |
| SpO₂ | Saturação periférica de oxigénio |
| F1-macro | Média não ponderada das pontuações F1 por classe |
| Jupyter | Ambiente interativo para execução de código |
| Python | Linguagem de programação utilizada na análise |

---

## Glossário

| Termo | Definição |
| --- | --- |
| Artefacto de medição | Registo fisiológico potencialmente inválido devido a falha do sensor, movimento do doente ou interferência. Não deve ser removido automaticamente por apresentar um valor extremo. |
| Aprendizagem não supervisionada | Abordagem em que o algoritmo procura estruturas ou grupos nos dados sem utilizar uma variável-alvo. |
| Aprendizagem supervisionada | Abordagem em que o modelo aprende relações entre variáveis preditoras e uma variável-alvo conhecida. |
| Classificação | Tarefa de aprendizagem supervisionada que atribui uma observação a uma categoria ou classe. |
| Carga de dessaturação | Número de registos horários válidos com SpO₂ inferior a 90%, sujeito a confirmação clínica. |
| CRISP-DM | Metodologia de prospeção de dados com seis fases: compreensão do negócio, compreensão dos dados, preparação dos dados, modelação, avaliação e implementação. |
| Dessaturação | SpO₂ inferior a 90%, limiar operacional para identificar registos de baixa saturação. |
| Episódio de internamento | Período de hospitalização de um recém-nascido, entre a admissão e a alta. |
| Fuga de informação (*data leakage*) | Utilização de informação não disponível no momento da previsão, produzindo resultados artificialmente otimistas. |
| Frequência cardíaca (FC) | Número de batimentos cardíacos por minuto. |
| Índice de perfusão (IP) | Indicador de oximetria de pulso que reflete a intensidade do sinal pulsátil periférico. |
| Internamento neonatal | Período de cuidados hospitalares a um recém-nascido numa unidade neonatal. |
| MAE (*Mean Absolute Error*) | Média dos valores absolutos das diferenças entre valores observados e previstos. |
| Modelo de referência (*baseline*) | Modelo simples usado como comparação para avaliar se um modelo mais complexo acrescenta valor. |
| Patologia predominante | Diagnóstico definido como principal para um episódio segundo regra clínica ou documental explícita. |
| Perfil fisiológico | Conjunto de características derivadas dos sinais vitais de um episódio ou período temporal. |
| Perfil de risco | Conjunto de características potencialmente associado a diferentes níveis de risco clínico. |
| Preditor | Variável usada como entrada de um modelo para estimar uma variável-alvo. |
| Regressão | Tarefa de aprendizagem supervisionada para estimar uma variável-alvo quantitativa. |
| Saturação periférica de oxigénio (SpO₂) | Estimativa não invasiva da percentagem de hemoglobina arterial saturada com oxigénio. |
| Validação cruzada | Divisão repetida dos dados em conjuntos de treino e teste para estimar o desempenho do modelo. |
| Variável-alvo | Variável que o modelo supervisionado procura estimar ou prever. |
| Variável categórica | Variável cujos valores representam categorias ou classes. |
| Variável quantitativa | Variável que representa uma quantidade numérica, discreta ou contínua. |

---

## 1. Introdução

O presente documento regista a aplicação da fase de Business Understanding da metodologia CRISP-DM ao projeto AASE — Análise de Sinais e Episódios Clínicos. O projeto decorre no contexto de um serviço de internamento neonatal e tem como missão transformar o historial clínico de recém-nascidos em conhecimento útil para a prática assistencial.

### 1.1 CRISP-DM

O CRISP-DM organiza qualquer projeto de prospeção de dados em seis fases iterativas. A sequência não é rígida, sendo frequente regressar a fases anteriores à medida que o conhecimento avança, mas a fase de Business Understanding é sempre o ponto de partida.

**Fase 1 — Business Understanding:** Identificar os objetivos clínicos e organizacionais antes de qualquer contacto com os dados. Traduzir os objetivos clínicos em três problemas analíticos mensuráveis (agrupamento, regressão e classificação).

**Fase 2 — Data Understanding:** Explorar os dados disponíveis sem os modificar. Descrever campos, tipos, intervalos de valores, distribuições e correlações. Avaliar problemas de qualidade.

**Fase 3 — Data Preparation:** Transformar os dados brutos num dataset pronto para modelação: selecionar variáveis, limpar artefactos, construir atributos derivados por episódio e integrar as duas tabelas.

**Fase 4 — Modeling:** Selecionar os algoritmos adequados a cada problema e construir os modelos. Dada a dimensão reduzida da amostra (58 episódios), a estratégia indicada é a validação cruzada leave-one-out.

**Fase 5 — Evaluation:** Verificar se os modelos respondem às perguntas clínicas originais. Avaliar tecnicamente (métricas) e em termos de negócio (critérios CS-N1 a CS-N4). Decidir: avançar, repetir fase anterior ou iniciar novo ciclo.

**Fase 6 — Deployment:** Comunicar os resultados ao serviço. No contexto académico, traduz-se num relatório em linguagem clínica, numa apresentação final e num plano de repetição do processo com dados futuros.

### 1.2 Estrutura

O documento segue as quatro tarefas genéricas da fase de Business Understanding:

- **Capítulo 2.1** — Determinar Objetivos de Negócio
- **Capítulo 2.2** — Avaliar a Situação
- **Capítulo 2.3** — Determinar Objetivos de Mineração de Dados
- **Capítulo 2.4** — Produzir Plano do Projeto

---

## 2. Business Understanding

### 2.1 Determinar Objetivos de Negócio

#### 2.1.1 Apresentação da Organização

A NeoData Clinics atua no sector da análise de dados clínicos neonatais com o objetivo de compreender de que forma os sinais vitais e os episódios clínicos evoluem ao longo do internamento. Através de metodologias rigorosas de análise de dados, transforma registos horários de sinais vitais — saturação de oxigénio, frequência cardíaca e perfusão — em conhecimento clínico com aplicação direta na prática assistencial.

#### 2.1.2 Informação do Negócio (Background)

O internamento neonatal é um serviço de cuidados intensivos dedicado a recém-nascidos que, por prematuridade, malformação congénita ou complicações do parto, necessitam de vigilância clínica permanente. O serviço defronta-se com três dificuldades práticas:

1. **Sobrecarga de informação** — o volume de registos gerado por cada internamento torna a análise manual demorada e suscetível a erros por fadiga.
2. **Ausência de perfis de risco estruturados** — não existe método sistemático para agrupar doentes com comportamentos fisiológicos semelhantes.
3. **Diagnóstico tardio** — o padrão de alterações fisiológicas precede frequentemente o diagnóstico formal; o seu reconhecimento automático permitiria agir mais cedo.

#### 2.1.3 Objetivos de Negócio

**ON1. Estratificar o risco dos doentes internados.**
Identificar, de entre os doentes em internamento, aqueles cujo perfil fisiológico indica maior instabilidade e maior probabilidade de eventos adversos graves.

**ON2. Antecipar a severidade do percurso clínico.**
Identificar, no início do internamento, os doentes com maior propensão para acumular episódios prolongados de compromisso respiratório.

**ON3. Apoiar o diagnóstico diferencial.**
Reconhecer padrões fisiológicos consistentemente associados a certas patologias, servindo de sinal de alerta ao clínico.

#### 2.1.4 Critérios de Sucesso de Negócio

| ID | Critério |
| --- | --- |
| CS-N1 | Os subgrupos identificados são clinicamente interpretáveis e distinguíveis em termos de perfil de risco. |
| CS-N2 | O modelo de estimação da duração do internamento demonstra potencial para ser mais informativo do que a ausência de qualquer estimativa prévia. |
| CS-N3 | O modelo de apoio ao diagnóstico demonstra potencial de discriminação superior à atribuição por simples prevalência histórica. |
| CS-N4 | Os resultados são apresentados em linguagem acessível a profissionais de saúde sem formação em análise de dados. |

---

### 2.2 Avaliar a Situação

#### 2.2.1 Inventário dos Recursos Disponíveis

**Dados clínicos:**

- Registos de sinais vitais por hora (SpO₂, FC, IP) para vários episódios.
- Registo de patologias por dia, com granularidade diária.

Os episódios estão identificados apenas por códigos internos.

**Equipa e infraestrutura:**

- Um analista de dados com acesso ao domínio clínico neonatal.
- Computador pessoal com Python 3.

#### 2.2.2 Requisitos, Pressupostos e Restrições

**Requisitos:**

- R1 — Resultados interpretáveis por profissionais de saúde sem formação em ciência de dados.
- R2 — Análise documentada e reprodutível.
- R3 — Confidencialidade dos dados assegurada em todas as fases.

**Pressupostos:**

- P1 — Os episódios são representativos da prática clínica do serviço.
- P2 — A pseudonimização foi corretamente aplicada.
- P3 — Registos fora dos intervalos normais serão avaliados contextualizadamente para distinguir artefactos de eventos clínicos reais.
- P4 — A granularidade horária é suficiente para capturar padrões relevantes.

**Restrições:**

- C1 — Não é possível enriquecer os dados com variáveis externas.
- C2 — A dimensão reduzida da amostra pode limitar a generalização.
- C3 — O projeto tem carácter académico e não inclui implementação operacional.

#### 2.2.3 Riscos e Contingências

| ID | Risco | Contingência | Prob. |
| --- | --- | --- | --- |
| R1 | Desequilíbrio entre patologias compromete a comparação entre grupos. | Agregar diagnósticos de baixa frequência; reportar limitações. | Alta |
| R2 | Amostra insuficiente para validar modelos com robustez estatística. | Usar validação cruzada maximizando o uso da amostra. | Alta |
| R3 | Episódios sem cobertura completa em ambas as fontes de dados. | Documentar cobertura cruzada; realizar análises independentes. | Média |
| R4 | Inconsistências na nomenclatura de diagnósticos. | Aplicar tabela de harmonização validada manualmente. | Média |
| R5 | Artefactos de medição não detetados pelos filtros. | Controlo de qualidade complementar; documentar metodologia. | Baixa |

#### 2.2.4 Terminologia

| Termo | Definição |
| --- | --- |
| Episódio de internamento | Período de hospitalização entre admissão e alta. |
| SpO₂ | Percentagem de hemoglobina saturada com oxigénio. Valores normais em neonatologia: 91–100%. |
| Dessaturação | SpO₂ abaixo de 90%. |
| FC | Número de contrações cardíacas por minuto. Referência neonatal: 100–180 bpm. |
| IP | Medida da qualidade da circulação periférica. |
| Carga de dessaturação | Número de horas com SpO₂ < 90% ao longo do internamento. |
| Patologia predominante | Diagnóstico clínico principal registado para o episódio. |
| Artefacto de medição | Registo tecnicamente inválido por falha de sensor, mobilização ou interferência. |
| Perfil de risco | Conjunto de características fisiológicas para antecipar probabilidade de eventos adversos. |

#### 2.2.5 Custos e Benefícios

**Custos:** Sem custos financeiros diretos. Ferramentas de código aberto. Custo real estimado: 40–60 horas de análise.

**Benefícios esperados:**

- Apoio à decisão clínica através de modelos de estratificação de risco.
- Eficiência assistencial pela identificação de subgrupos com perfis distintos.
- Diagnóstico mais célere pelo reconhecimento de padrões fisiológicos.
- Reutilizabilidade do processo analítico com dados futuros.

---

### 2.3 Determinar Objetivos de Mineração de Dados

#### 2.3.1 Objetivos de Mineração de Dados

**ODM1 — Agrupamento: Identificar perfis clínicos de risco (aprendizagem não supervisionada)**
*Objetivo de negócio: ON1*

Induzir automaticamente grupos de episódios com base nos indicadores fisiológicos resumidos de cada doente, sem informação sobre diagnósticos.

*Questão clínica:* Existem subgrupos naturais de recém-nascidos com padrões fisiológicos consistentemente distintos, que justifiquem protocolos de vigilância diferenciados?

---

**ODM2 — Regressão: Estimar a carga de dessaturação do internamento (aprendizagem supervisionada)**
*Objetivo de negócio: ON2*

Construir um modelo que estime a carga de dessaturação (horas com SpO₂ < 90%) a partir de dados fisiológicos disponíveis num momento inicial.

*Questão clínica:* É possível estimar a carga de dessaturação que um recém-nascido poderá acumular durante o internamento, para apoiar a avaliação do risco respiratório?

---

**ODM3 — Classificação: Prever a patologia predominante (aprendizagem supervisionada)**
*Objetivo de negócio: ON3*

Construir um modelo que atribua a cada episódio uma patologia predominante prevista com base nos padrões de sinais vitais.

*Questão clínica:* O padrão de alterações fisiológicas contém informação suficiente para antecipar a patologia predominante, contribuindo para um diagnóstico mais rápido?

#### 2.3.2 Critérios de Sucesso de Mineração de Dados

| ID | Nível | Critério | Justificação |
| --- | --- | --- | --- |
| CS-DM1 | Conservador | Índice de silhueta > 0,20 para k ótimo (2 ≤ k ≤ 6). | Acima do limiar de "estrutura fraca" (0,15) com dados clínicos ruidosos. |
| CS-DM1 | Ambicioso | Índice de silhueta > 0,40 e grupos validados clinicamente. | Qualidade "estrutura razoável"; coerência com taxa de dessaturação e FC média por grupo. |
| CS-DM2 | Conservador | MAE ≤ MAE_baseline − 10% e R² > 0,15. | Melhoria mínima sobre o preditor naïve; n=45. |
| CS-DM2 | Ambicioso | MAE ≤ MAE_baseline − 25% e R² > 0,35. | Equivale a errar menos de 1 dia face ao baseline. |
| CS-DM3 | Conservador | F1-Macro > 0,35 e Balanced Accuracy > 45% (validação cruzada 5-fold). | Claramente superior ao baseline; exequível com 14 classes e amostra pequena. |
| CS-DM3 | Ambicioso | F1-Macro > 0,55 e Balanced Accuracy > 60%. | Bom desempenho multiclasse com dados desbalanceados (DMH = 39%). |

---

### 2.4 Produzir Plano do Projeto

#### 2.4.1 Plano do Projeto

| Fase | Tarefa CRISP-DM | Fase | Data |
| --- | --- | --- | --- |
| 1 | Determinar objetivos de negócio | Business Understanding | 21/09/2026 – 26/09/2026 |
| 1 | Avaliar a situação | Business Understanding | 21/09/2026 – 26/09/2026 |
| 1 | Determinar objetivos de prospeção de dados | Business Understanding | 21/09/2026 – 26/09/2026 |
| 1 | Produzir plano do projeto | Business Understanding | 21/09/2026 – 26/09/2026 |
| 2 | Recolher dados iniciais | Data Understanding | 28/09/2026 – 03/10/2026 |
| 2 | Descrever dados | Data Understanding | 28/09/2026 – 03/10/2026 |
| 2 | Explorar dados | Data Understanding | 05/10/2026 – 10/10/2026 |
| 2 | Verificar qualidade dos dados | Data Understanding | 05/10/2026 – 10/10/2026 |
| 3 | Selecionar dados | Data Preparation | 12/10/2026 – 17/10/2026 |
| 3 | Limpar dados | Data Preparation | 12/10/2026 – 17/10/2026 |
| 3 | Construir atributos | Data Preparation | 19/10/2026 – 24/10/2026 |
| 3 | Integrar dados | Data Preparation | 19/10/2026 – 24/10/2026 |
| 3 | Formatar dados | Data Preparation | 19/10/2026 – 24/10/2026 |
| 4 | Selecionar técnica de modelação | Modeling | 26/10/2026 – 31/10/2026 |
| 4 | Gerar plano de teste | Modeling | 02/11/2026 – 07/11/2026 |
| 4 | Construir modelo | Modeling | 09/11/2026 – 14/11/2026 |
| 4 | Avaliar modelo | Modeling | 16/11/2026 – 21/11/2026 |
| 5 | Avaliar resultados | Evaluation | 23/11/2026 – 28/11/2026 |
| 5 | Rever processo | Evaluation | 23/11/2026 – 28/11/2026 |
| 5 | Determinar próximos passos | Evaluation | 30/11/2026 – 05/12/2026 |
| 6 | Planear deployment | Deployment | 07/12/2026 – 12/12/2026 |
| 6 | Planear monitorização e manutenção | Deployment | 14/12/2026 – 19/12/2026 |
| 6 | Produzir relatório final | Deployment | 04/01/2027 – 09/01/2027 |
| 6 | Rever projeto | Deployment | 11/01/2027 – 16/01/2027 |

#### 2.4.2 Avaliação Inicial das Ferramentas e Técnicas

O projeto é desenvolvido em Python 3 com notebooks Jupyter, combinando código, resultados e interpretação clínica em documentos reprodutíveis.

| Ferramenta | Aplicação |
| --- | --- |
| Python stdlib (csv, statistics, collections) | Leitura dos ficheiros e cálculo de estatísticas de resumo. |
| NumPy | Operações numéricas e cálculo de correlações. |
| Matplotlib | Visualização de padrões clínicos: distribuições, evolução temporal, comparações entre grupos. |
| Scikit-learn (fases 3 e 4) | Implementação e avaliação dos três modelos (agrupamento, regressão, classificação). |

**Adequação ao contexto:**

- **Agrupamento** — indicado porque a questão clínica é exploratória e pretende descobrir grupos, não confirmar categorias definidas.
- **Regressão** — a carga de dessaturação é uma variável numérica, tornando a regressão o enquadramento natural.
- **Classificação** — a patologia predominante é categórica; a validação por leave-one-out é a estratégia mais robusta para amostras pequenas.

---

## 3. Conclusão

Esta fase de Business Understanding estabeleceu o enquadramento clínico e analítico do projeto AASE:

- **Missão clara** — apoio à prática clínica neonatal através de estratificação de risco, antecipação de complicações respiratórias e apoio ao diagnóstico diferencial.
- **Três perguntas clínicas concretas** — traduzidas em agrupamento, regressão e classificação.
- **Riscos conhecidos e mitigados** — desequilíbrio entre patologias e dimensão reduzida da amostra têm estratégias de contingência definidas.
- **Plano estruturado** — seis fases CRISP-DM mapeadas em tarefas e entregáveis específicos.

---

## 4. Próximos Passos

A fase seguinte é o **Data Understanding**, em quatro tarefas:

1. **Recolha de dados iniciais** — carregar os dois ficheiros CSV e documentar volume, estrutura e método de aquisição.
2. **Descrição dos dados** — caracterizar campos, tipos, intervalos e granularidade temporal.
3. **Exploração dos dados** — analisar distribuições, padrões temporais, correlações e co-ocorrências de diagnósticos.
4. **Verificação da qualidade dos dados** — quantificar artefactos, valores em falta e inconsistências na nomenclatura de patologias.
