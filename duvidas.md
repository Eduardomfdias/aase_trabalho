# Revisão CRISP-DM — Data Understanding e Data Preparation

**Repositório analisado:** [Eduardomfdias/aase_trabalho](https://github.com/Eduardomfdias/aase_trabalho)  
**Âmbito:** fases `02_data_understanding` e `03_data_preparation`  
**Objetivo:** consolidar a revisão técnica dos notebooks, datasets, validações e checklists, identificando pontos fortes, riscos, inconsistências e ações prioritárias.

> **Nota de âmbito:** esta revisão baseia-se na inspeção do código, dos ficheiros e dos outputs guardados no repositório. Não corresponde a uma execução integral de todos os notebooks num ambiente limpo e reproduzível. Os resultados guardados foram analisados, mas devem ser confirmados através de uma execução limpa após as correções.

## 1. Sumário executivo

A fase **Data Understanding** contém exploração descritiva útil: caracterização dos sinais vitais, dados em falta, distribuições, correlações e análise de patologias. Contudo, parte das contagens e análises por episódio pode ficar distorcida por diferenças de formatação nos identificadores e por uma normalização de patologias que não é consistente entre notebooks.

A fase **Data Preparation** constrói os artefactos principais — dataset final, divisão treino/teste, metadados e parâmetros de normalização — mas tem problemas que devem ser resolvidos antes de avançar para **Modeling**:

1. **Cabeçalhos duplicados** em `dataset_final.csv`, `train.csv` e `test.csv`.
2. **Fuga de informação (*target leakage*)**: `carga_dessaturacao` aparece simultaneamente como variável preditora e alvo.
3. **Risco de fuga temporal**, dependendo do objetivo de previsão, porque várias features parecem resumir o episódio inteiro.
4. **Definição ambígua do alvo** `duracao_dias`, calculado como número de datas distintas em vez de uma duração clínica validada.
5. **Reprodutibilidade incompleta**: o notebook de preparação não gera os ficheiros intermédios que o notebook de validação espera encontrar.
6. **Divisão treino/teste pouco representativa** para classes raras: algumas classes não têm qualquer exemplo no conjunto de teste.

**Conclusão:** a preparação de dados ainda não deve ser considerada pronta para modelação. Os problemas de estrutura do dataset e de leakage são bloqueadores prioritários.

## 2. Fontes e artefactos analisados

- [Notebook EDA — `02_data_understanding/eda_aase.ipynb`](https://github.com/Eduardomfdias/aase_trabalho/blob/main/02_data_understanding/eda_aase.ipynb)
- [Notebook de preparação — `03_data_preparation/data_preparation.ipynb`](https://github.com/Eduardomfdias/aase_trabalho/blob/main/03_data_preparation/data_preparation.ipynb)
- [Notebook de validação — `03_data_preparation/validacao_data_preparation.ipynb`](https://github.com/Eduardomfdias/aase_trabalho/blob/main/03_data_preparation/validacao_data_preparation.ipynb)
- [Notas de preparação — `03_data_preparation/notas_data_preparation.md`](https://github.com/Eduardomfdias/aase_trabalho/blob/main/03_data_preparation/notas_data_preparation.md)
- [Dataset final — `03_data_preparation/dataset_final.csv`](https://github.com/Eduardomfdias/aase_trabalho/blob/main/03_data_preparation/dataset_final.csv)
- [Treino — `03_data_preparation/train.csv`](https://github.com/Eduardomfdias/aase_trabalho/blob/main/03_data_preparation/train.csv)
- [Teste — `03_data_preparation/test.csv`](https://github.com/Eduardomfdias/aase_trabalho/blob/main/03_data_preparation/test.csv)
- [Checklist CRISP-DM — `crisp_dm_checklist.md`](https://github.com/Eduardomfdias/aase_trabalho/blob/main/crisp_dm_checklist.md)
- [Checklist do projeto — `checklist_projeto.md`](https://github.com/Eduardomfdias/aase_trabalho/blob/main/checklist_projeto.md)

## 3. Data Understanding

### 3.1 Pontos positivos

A análise exploratória cobre várias dimensões relevantes:

- dimensão e cobertura dos dados;
- distribuição e qualidade dos sinais vitais;
- valores em falta;
- estatísticas descritivas;
- relações entre variáveis;
- observações com SpO₂ baixa;
- distribuição de patologias e coocorrências;
- análise temporal, incluindo gráficos mensais quando as datas podem ser interpretadas.

Os outputs guardados no notebook EDA indicam:

| Indicador | Resultado observado |
| --- | ---: |
| Registos de sinais vitais | 9 857 |
| Registos de patologia | 696 |
| Registos vitais válidos após filtragem | 9 615 |
| Registos excluídos | 242 (cerca de 2,5%) |
| SpO₂ média | 95,98% |
| Pulso médio | 147,74 bpm |
| Perfusão média | 1,22 |
| Observações com SpO₂ < 90% | 119 em 9 615 |

Valores em falta registados na EDA:

| Variável | Valores em falta |
| --- | ---: |
| SpO₂ (`sat_o2`) | 44 |
| Pulso (`pulse`) | 64 |
| Perfusão (`perfusion`) | 42 |
| Patologia | 12 |

Correlações de Pearson guardadas no notebook:

| Par de variáveis | Correlação |
| --- | ---: |
| SpO₂ e pulso | -0,1957 |
| SpO₂ e perfusão | -0,1612 |
| Pulso e perfusão | +0,0205 |

Estas correlações são descritivas. Como existem várias medições por episódio, as observações não devem ser tratadas automaticamente como independentes; uma análise inferencial exigiria considerar a estrutura repetida dos dados.

### 3.2 Identificadores de episódio

A EDA analisa os identificadores sem aplicar, em todos os pontos relevantes, a mesma normalização usada na preparação. Variações como `EP016`, `EP 016` e `ep016` podem ser tratadas como episódios diferentes, fragmentando contagens, cruzamentos entre fontes e agregações.

As contagens reportadas diferem consoante a abordagem:

| Fonte/abordagem | IDs/episódios reportados |
| --- | ---: |
| EDA: IDs nos sinais vitais | 58 |
| EDA: IDs nas patologias | 45 |
| EDA: interseção | 40 |
| Preparação, após normalização | 47 IDs nos sinais vitais |
| Preparação, após normalização | 39 IDs de patologia |
| Preparação, após normalização | 39 em comum |
| Preparação | 8 episódios apenas nos sinais vitais |

**Impacto:** as estatísticas por episódio e a cobertura entre ficheiros podem não representar corretamente os episódios clínicos únicos até que os IDs sejam normalizados de forma consistente antes de todas as análises.

**Ação recomendada:** centralizar a normalização de IDs numa função reutilizada pela EDA, preparação e validação; documentar quantos IDs são fundidos e verificar colisões.

### 3.3 Normalização das patologias

A normalização de rótulos não é equivalente em todos os notebooks. A preparação trata algumas variantes que a EDA pode manter separadas — por exemplo, variantes de “icterícia” e “RGE”.

**Impacto:** contagens de patologias, frequências e coocorrências podem ficar fragmentadas ou não coincidir com as classes finais usadas na modelação.

**Ação recomendada:** definir um dicionário único e versionado de equivalências de patologias; aplicá-lo antes de qualquer contagem, visualização, codificação ou divisão treino/teste.

### 3.4 Datas e análise temporal

A preparação calcula `duracao_dias` contando valores de data distintos tal como aparecem nos registos. A EDA tenta interpretar vários formatos para alguns gráficos, mas pode ignorar silenciosamente datas que não consegue analisar.

Isto cria uma inconsistência: a duração pode contar strings de data diferentes como dias diferentes, mesmo quando representam a mesma data, e pode não validar datas inválidas.

**Ação recomendada:**

1. converter as datas para um tipo temporal normalizado;
2. registar e inspecionar datas inválidas ou ambíguas;
3. definir explicitamente se `duracao_dias` significa dias com registos, diferença entre primeira e última data, ou duração clínica de internamento;
4. usar a mesma regra em EDA, preparação e validação.

Não se deve chamar “duração do internamento” à variável sem uma definição clínica e uma fonte de dados que a sustentem.

### 3.5 Dados em falta, filtros e duplicados

A preparação filtra registos quando os campos numéricos ou a hora não podem ser convertidos. A função de conversão segura devolve `None` para valores em falta ou não numéricos; por isso, os registos excluídos incluem ambos os casos.

As notas por variável indicam exclusões de 74 para SpO₂, 91 para pulso, 70 para perfusão e 8 para hora. Estes números **não são necessariamente exclusões independentes**: um mesmo registo pode falhar em mais do que uma coluna. O total de linhas excluídas reportado é 242.

A EDA e a preparação não documentam uma análise sistemática de duplicados nem uma regra explícita para os tratar.

**Ações recomendadas:**

- distinguir valores em falta, valores não numéricos, valores fora do intervalo e registos com hora inválida;
- produzir uma tabela de qualidade com contagens por motivo e número de linhas únicas afetadas;
- analisar duplicados exatos e duplicados por chave clínica/temporal;
- não eliminar duplicados automaticamente sem definir a chave e a regra;
- documentar todos os filtros e o número de linhas antes/depois de cada etapa.

### 3.6 Interpretação clínica e estatística

A EDA identifica 119 observações com SpO₂ inferior a 90%. É útil como sinal descritivo, mas a interpretação clínica depende do contexto, da duração do evento, da qualidade da medição e da população em estudo.

As correlações guardadas são relativamente fracas e não demonstram causalidade. A análise deve também ter em conta que várias observações pertencem ao mesmo episódio.

**Ações recomendadas:**

- justificar os limiares clínicos utilizados e indicar a respetiva origem;
- apresentar distribuições por episódio, além das distribuições por registo;
- distinguir claramente resultados descritivos de conclusões clínicas ou inferenciais.

## 4. Data Preparation

### 4.1 Cabeçalhos duplicados — bloqueador

Os ficheiros gerados apresentam cabeçalhos duplicados:

| Ficheiro | Linhas de dados | Colunas no cabeçalho | Nomes únicos | Duplicados |
| --- | ---: | ---: | ---: | --- |
| `dataset_final.csv` | 47 | 22 | 20 | `n_registos`, `carga_dessaturacao` |
| `train.csv` | 32 | 38 | 36 | `n_registos`, `carga_dessaturacao` |
| `test.csv` | 7 | 38 | 36 | `n_registos`, `carga_dessaturacao` |

A causa identificada no código é a sobreposição entre listas de colunas: `BASE_COLS` inclui `n_registos`, que também aparece em `FEATURE_COLS`; `carga_dessaturacao` surge como feature e como target.

**Riscos:**

- acesso ambíguo a colunas com o mesmo nome;
- comportamento inesperado em bibliotecas de análise/modelação;
- confusão entre variáveis preditoras e alvos;
- maior dificuldade em validar e reproduzir os resultados.

**Correção necessária:** construir as colunas com nomes únicos de forma explícita e validar a unicidade antes de guardar qualquer CSV. A validação deve falhar se houver duplicados.

### 4.2 Fuga de informação: `carga_dessaturacao` — bloqueador

`carga_dessaturacao` está incluída tanto em `FEATURE_COLS` como em `TARGET_COLS`.

Isto significa que a variável a prever também pode ser entregue ao modelo como entrada, tornando a avaliação inválida para esse alvo.

**Correção necessária:** separar inequivocamente:

- identificadores e metadados;
- variáveis preditoras;
- alvos.

Nenhuma coluna-alvo deve aparecer nas features do modelo. Deve existir uma verificação automática da interseção entre as listas.

### 4.3 Possível fuga temporal

A preparação parece calcular estatísticas e indicadores a partir de medições de todo o episódio. Entre as features estão indicadores como `desat_count`, `desat_pct`, estatísticas de SpO₂ e `carga_dessaturacao`.

Se o objetivo for prever um resultado antes do fim do episódio, essas variáveis podem incorporar informação futura ou ser calculadas usando medições posteriores ao momento em que a previsão deveria ser feita.

**Ação necessária:** definir primeiro a pergunta de modelação e o instante de previsão. Depois, calcular features apenas com informação disponível até esse instante. Se o objetivo for uma classificação retrospetiva do episódio completo, isso deve ser declarado e não apresentado como previsão prospetiva.

### 4.4 Definição de `carga_dessaturacao`

A variável é calculada somando `(90 - SpO₂)` para medições com SpO₂ inferior a 90%. Esta métrica é uma soma de défices por observação, não uma integração temporal.

Por isso, pode depender da frequência de amostragem e do número de registos: dois episódios com gravidade semelhante podem ter valores diferentes se tiverem sido medidos com frequências distintas.

**Ação recomendada:** documentar a fórmula e as limitações. Se se pretende medir carga ao longo do tempo, avaliar uma definição que considere os intervalos temporais entre medições, com validação clínica e técnica adequada.

### 4.5 Definição e validade dos alvos

O código inclui `duracao_dias`, `carga_dessaturacao`, `pat_predominante` e `pat_label` nos alvos.

Antes de modelar, é necessário decidir quais destes são verdadeiramente objetivos de previsão e se são compatíveis com o mesmo cenário de uso. Em particular:

- `duracao_dias` pode representar dias distintos com registos, não necessariamente duração real de internamento;
- `carga_dessaturacao` é derivada dos próprios sinais vitais e exige cuidado com features que a reproduzem;
- `pat_predominante` e `pat_label` representam rótulos categóricos; a codificação numérica não deve ser interpretada como escala ordinal.

A codificação de classes segue a frequência e, em caso de empate, uma regra alfabética. É determinística, mas a ordem numérica das classes não tem significado clínico.

**Ação recomendada:** definir cada alvo, a sua fonte, fórmula, unidade, momento de disponibilidade e métrica de avaliação antes da fase Modeling.

### 4.6 Desbalanceamento e divisão treino/teste

Os metadados reportam 39 episódios com rótulo, distribuídos assim:

| Patologia | Episódios |
| --- | ---: |
| Doença das Membranas Hialinas | 24 |
| Icterícia Neonatal | 7 |
| Citomegalovírus | 4 |
| Anemia | 2 |
| Displasia Broncopulmonar | 1 |
| Persistência do Canal Arterial | 1 |
| **Total** | **39** |

Existem ainda 8 episódios sem patologia, mantidos no dataset final com `pat_label = -1`, mas excluídos da divisão supervisionada.

A divisão observada contém 32 episódios de treino e 7 de teste. O teste inclui:

| Patologia | Exemplos no teste |
| --- | ---: |
| Doença das Membranas Hialinas | 5 |
| Icterícia Neonatal | 1 |
| Citomegalovírus | 1 |
| Anemia | 0 |
| Displasia Broncopulmonar | 0 |
| Persistência do Canal Arterial | 0 |

A divisão 80/20 por classe não consegue garantir exemplos de teste para classes com apenas um ou dois casos. Assim, métricas globais podem ocultar desempenho inexistente ou não mensurável nas classes raras.

**Ações recomendadas:**

- apresentar sempre as contagens por classe em treino e teste;
- evitar conclusões fortes com uma amostra tão pequena;
- considerar validação cruzada estratificada quando tecnicamente viável, reconhecendo que classes com um único caso continuam a ser um problema;
- avaliar se a tarefa multiclasse é defensável com esta quantidade e distribuição de exemplos;
- manter todas as transformações aprendidas apenas com treino quando aplicável, evitando ajustar parâmetros com o conjunto de teste.

### 4.7 Parâmetros de normalização

`normalisation_params.csv` contém parâmetros para 16 features e inclui `carga_dessaturacao`, que também é alvo. Isto reforça a necessidade de separar formalmente features e targets.

Deve confirmar-se que quaisquer parâmetros de normalização são ajustados exclusivamente no conjunto de treino e depois aplicados, sem novo ajuste, a validação e teste.

### 4.8 Inconsistência entre preparação e validação

O notebook `data_preparation.ipynb` gera os artefactos finais, mas não gera `sinais_vitais_limpo.csv` e `patologias_limpo.csv`, que o notebook `validacao_data_preparation.ipynb` espera encontrar.

As notas descrevem estes ficheiros intermédios como cópias com IDs normalizados; isso não significa necessariamente que todas as colunas ou rótulos estejam limpos e harmonizados. A normalização de patologia usada para derivar os alvos pode não ser persistida nos CSV intermédios.

**Impacto:** a validação pode depender de ficheiros preexistentes, de uma execução anterior ou de passos manuais não documentados.

**Ações recomendadas:**

1. gerar todos os ficheiros necessários num pipeline único e reproduzível, ou remover a dependência dos intermédios;
2. declarar claramente quais ficheiros são fontes, intermediários e outputs finais;
3. garantir que a validação começa a partir dos dados brutos e pode ser executada num ambiente limpo;
4. persistir transformações importantes ou documentar que são apenas usadas em memória.

### 4.9 Limitações do notebook de validação

A validação existente verifica apenas um subconjunto das propriedades necessárias. Não deteta de forma suficiente:

- cabeçalhos duplicados;
- sobreposição entre features e targets;
- fuga temporal;
- datas inválidas ou inconsistentes;
- cobertura das classes em treino/teste;
- reprodução integral dos outputs a partir dos dados brutos;
- coerência entre as listas de features da preparação e da validação.

Por isso, a indicação de que as verificações atuais passam não deve ser interpretada como prova de que a preparação está pronta para modelação.

## 5. Consistência documental e CRISP-DM

O estado dos checklists é inconsistente:

- `crisp_dm_checklist.md` mantém tarefas das fases 2 e 3 por assinalar;
- `checklist_projeto.md` assinala algumas tarefas de EDA como concluídas, mas indica que o relatório ainda não está concluído;
- várias tarefas da preparação permanecem por assinalar.

**Ação recomendada:** alinhar os checklists com o estado real dos artefactos. Uma tarefa só deve ser marcada como concluída quando houver evidência verificável — por exemplo, notebook executado de forma limpa, testes aprovados, outputs atualizados e documentação consistente.

## 6. Plano de correção prioritário

### Prioridade 1 — Bloqueadores antes de Modeling

- [ ] Remover nomes de colunas duplicados em todos os datasets exportados.
- [ ] Separar features, identificadores, metadados e targets.
- [ ] Remover `carga_dessaturacao` das features quando for o alvo.
- [ ] Definir explicitamente o objetivo de previsão e o momento em que a previsão acontece.
- [ ] Rever todas as features para evitar informação futura ou derivação direta/indireta do alvo.
- [ ] Confirmar que a normalização é ajustada apenas com os dados de treino.

### Prioridade 2 — Integridade e qualidade dos dados

- [ ] Normalizar IDs antes de qualquer análise ou junção.
- [ ] Usar um único dicionário de normalização de patologias em todos os notebooks.
- [ ] Normalizar e validar datas antes de calcular durações ou gráficos temporais.
- [ ] Distinguir valores em falta, não numéricos, inválidos e fora de intervalo.
- [ ] Definir e documentar uma estratégia de análise de duplicados.
- [ ] Documentar a fórmula, a unidade e as limitações de `carga_dessaturacao`.
- [ ] Rever os limiares clínicos e as respetivas justificações.

### Prioridade 3 — Reprodutibilidade e testes

- [ ] Fazer com que a preparação gere todos os artefactos de que a validação depende.
- [ ] Executar os notebooks pela ordem correta num ambiente limpo.
- [ ] Atualizar os outputs guardados após a execução bem-sucedida.
- [ ] Adicionar testes automáticos para unicidade dos cabeçalhos, tipos, valores em falta, ranges e interseção features/targets.
- [ ] Adicionar testes para a contagem de episódios, cobertura entre fontes e distribuição de classes.
- [ ] Garantir que o conjunto de teste não é usado para ajustar transformações.

### Prioridade 4 — Documentação

- [ ] Harmonizar `crisp_dm_checklist.md` e `checklist_projeto.md`.
- [ ] Documentar as decisões de limpeza e as razões para exclusões.
- [ ] Documentar a definição operacional de cada target.
- [ ] Registar limitações da amostra e das classes raras.
- [ ] Distinguir claramente análise descritiva, inferência e objetivo de previsão.

## 7. Critérios mínimos para considerar a preparação validada

A fase Data Preparation deve ser considerada pronta para Modeling apenas quando, pelo menos:

1. todos os ficheiros finais têm nomes de coluna únicos;
2. features e targets são disjuntos;
3. o cenário de previsão e o instante de disponibilidade das variáveis estão documentados;
4. datas, IDs e rótulos são normalizados de forma consistente;
5. os motivos de exclusão e o tratamento de duplicados são auditáveis;
6. os datasets podem ser regenerados a partir dos dados de origem num ambiente limpo;
7. a divisão treino/teste e as limitações de classes estão documentadas;
8. as verificações automáticas passam e os checklists refletem o estado real.

## 8. Veredito final

**Data Understanding:** existe uma base exploratória útil, mas as conclusões por episódio, patologia e tempo precisam de ser recalculadas depois de uniformizar IDs, rótulos e datas. As estatísticas por registo são informativas, mas devem ser interpretadas tendo em conta as medições repetidas por episódio.

**Data Preparation:** os artefactos principais estão presentes, mas a preparação tem falhas estruturais e metodológicas importantes. Os cabeçalhos duplicados, a sobreposição de `carga_dessaturacao` entre features e targets e a falta de uma definição clara do cenário temporal são os pontos mais urgentes.

**Decisão recomendada:** não avançar para Modeling com os datasets atuais sem corrigir os bloqueadores da Prioridade 1 e repetir a validação integral. Depois, executar os notebooks de ponta a ponta e atualizar a documentação.

## 9. Referências do repositório

- [Repositório principal](https://github.com/Eduardomfdias/aase_trabalho)
- [EDA](https://github.com/Eduardomfdias/aase_trabalho/blob/main/02_data_understanding/eda_aase.ipynb)
- [Preparação](https://github.com/Eduardomfdias/aase_trabalho/blob/main/03_data_preparation/data_preparation.ipynb)
- [Validação](https://github.com/Eduardomfdias/aase_trabalho/blob/main/03_data_preparation/validacao_data_preparation.ipynb)
- [Notas da preparação](https://github.com/Eduardomfdias/aase_trabalho/blob/main/03_data_preparation/notas_data_preparation.md)
- [Checklist CRISP-DM](https://github.com/Eduardomfdias/aase_trabalho/blob/main/crisp_dm_checklist.md)
- [Checklist do projeto](https://github.com/Eduardomfdias/aase_trabalho/blob/main/checklist_projeto.md)
