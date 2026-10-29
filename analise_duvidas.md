# AASE — Plano detalhado de auditoria e consolidação do projeto

O objetivo é fazer uma revisão sistemática de todo o trabalho, desde a compreensão dos dados até à avaliação da regressão, para garantir que o projeto está coerente com o objetivo clínico, metodologicamente sólido, tecnicamente reproduzível e devidamente documentado.

A revisão deve ser feita por esta ordem: primeiro confirmar o que o modelo pretende prever; depois auditar os dados e a sua preparação; em seguida validar a separação temporal e a ausência de data leakage; só depois avaliar os modelos e consolidar a documentação.

O foco será o repositório [AASE — Grupo 2](https://github.com/Eduardomfdias/aase_trabalho?utm_source=chatgpt.com), especialmente:

- [Análise exploratória — EDA](https://github.com/Eduardomfdias/aase_trabalho/blob/main/02_data_understanding/eda_aase.ipynb?utm_source=chatgpt.com)
- [Preparação dos dados](https://github.com/Eduardomfdias/aase_trabalho/blob/main/03_data_preparation/data_preparation.ipynb?utm_source=chatgpt.com)
- [Validação da preparação](https://github.com/Eduardomfdias/aase_trabalho/blob/main/03_data_preparation/validacao_data_preparation.ipynb?utm_source=chatgpt.com)
- [Notas de preparação](https://github.com/Eduardomfdias/aase_trabalho/blob/main/03_data_preparation/notas_data_preparation.md?utm_source=chatgpt.com)
- [Dataset de regressão temporal](https://github.com/Eduardomfdias/aase_trabalho/blob/main/03_data_preparation/dataset_regressao_24h.csv?utm_source=chatgpt.com)
- [Notebook de regressão](https://github.com/Eduardomfdias/aase_trabalho/blob/main/04_modeling/regressao_carga_dessaturacao.ipynb?utm_source=chatgpt.com)

Os pontos seguintes combinam o que foi identificado nas revisões anteriores do projeto com critérios de auditoria que deves aplicar à versão atual. Um ponto assinalado para verificação não significa necessariamente que continue por resolver: deves confirmar o estado atual do código e dos resultados.

## 1. Prioridade máxima: confirmar que o modelo resolve o problema certo

Antes de mexeres no código, escreve numa página a definição formal do problema. Esta é a referência contra a qual todos os notebooks, datasets, gráficos e conclusões serão avaliados.

### 1.1. Confirmar o objetivo de negócio

O projeto pretende estimar a carga de dessaturação de um episódio de internamento neonatal a partir de sinais vitais recolhidos numa janela inicial de 24 horas.

Tens de esclarecer:

- Qual é a decisão ou atividade clínica que esta estimativa pretende apoiar?
- Em que momento seria disponibilizada a previsão?
- Que informação estaria efetivamente disponível nesse momento?
- O objetivo é estimar a carga de dessaturação nas 24 horas seguintes ou durante todo o restante internamento?
- O resultado é um indicador exploratório para análise ou pretende apoiar uma decisão clínica específica?
- Quais são os limites de utilização do protótipo?

A formulação do objetivo deve ser suficientemente concreta para que duas pessoas independentes construam o mesmo alvo a partir dos mesmos dados.

### 1.2. Resolver a definição da variável-alvo

Este é um dos pontos mais importantes de toda a consolidação.

Nas versões anteriormente analisadas, o código calculava `carga_dessaturacao_futura` através da soma de:

\\[ \sum\_{i:\\,SpO\_{2,i}<90}(90-SpO\_{2,i}) \\]

Esta fórmula calcula um índice acumulado de défice de saturação por observação. Não calcula diretamente o número de horas com SpO₂ abaixo de 90%.

A definição descrita no objetivo de negócio — horas com saturação inferior a 90% — representa uma grandeza diferente.

Tens de escolher, justificar e implementar uma definição única.

| Opção                                       | O que mede                                   | Principal questão                                                               |
| ------------------------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------- |
| Índice acumulado por observação             | Soma dos défices de SpO₂ abaixo do limiar    | Depende da frequência de medição.                                               |
| Número de horas com SpO₂ abaixo de 90%      | Duração estimada da dessaturação             | Exige timestamps e regras para intervalos sem medições.                         |
| Percentagem do tempo com SpO₂ abaixo de 90% | Proporção do tempo observado em dessaturação | Exige estimar de forma consistente o tempo observado e o tempo em dessaturação. |
| Carga nas 24 horas seguintes                | Carga durante um horizonte fixo              | Requer cobertura suficiente nesse horizonte.                                    |
| Carga até ao fim do episódio                | Carga durante o restante internamento        | O horizonte varia entre episódios.                                              |

Auditorias a executar:

- Verificar a fórmula implementada no código, sem depender apenas do nome da coluna.
- Comparar essa fórmula com a definição no relatório de negócio.
- Confirmar a unidade matemática do resultado.
- Confirmar que o nome `carga_dessaturacao_futura` descreve realmente o que é calculado.
- Verificar se a definição é consistente em todos os notebooks e ficheiros CSV.
- Recalcular manualmente o alvo para alguns episódios e comparar com o valor exportado.
- Documentar o tratamento de valores iguais a 90%, inferiores a 90%, em falta e inválidos.
- Documentar como são tratados intervalos sem medições, especialmente se o alvo representar tempo.
- Confirmar que a definição escolhida é clinicamente interpretável e adequada ao objetivo de previsão.

Não alteres a fórmula apenas para obter métricas melhores. A definição deve ser escolhida antes de avaliar os modelos.

### 1.3. Confirmar o horizonte temporal

Se a janela inicial corresponder às primeiras 24 horas, tens de definir exatamente o que acontece depois.

Por exemplo:

- Janela inicial: desde \\(t_0\\) até antes de \\(t_0+24h\\).
- Instante de previsão: \\(t_0+24h\\).
- Janela futura: desde \\(t_0+24h\\) até antes de \\(t_0+48h\\).

Este é um exemplo de horizonte futuro fixo, não uma indicação de que o projeto já o implementa.

A alternativa é prever a carga desde o fim das primeiras 24 horas até ao final do internamento. Nesse caso, o horizonte futuro deixa de ser igual para todos os episódios.

Tens de verificar:

- Se o código usa um horizonte futuro fixo ou variável.
- Se essa decisão coincide com o objetivo de negócio.
- Se a janela de preditores e a janela do alvo são disjuntas.
- Se a medição exatamente na fronteira temporal é incluída em apenas uma janela.
- Se episódios que terminam antes do fim do horizonte são excluídos ou tratados explicitamente.
- Se os episódios sem cobertura suficiente são identificados.
- Se a documentação descreve o horizonte efetivamente implementado.

A escolha tem consequências diretas: não se deve comparar a carga acumulada durante períodos muito diferentes como se fosse a mesma quantidade clínica.

## 2. Auditoria da estrutura do repositório e dos fluxos de trabalho

Antes de rever fórmulas, confirma que cada ficheiro tem uma finalidade clara e que não existem versões contraditórias dos mesmos dados.

### 2.1. Verificar os artefactos principais

| Artefacto                                              | O que deves auditar                                                                                       |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| `02_data_understanding/eda_aase.ipynb`                 | Se a análise exploratória corresponde aos dados de origem atuais e se as conclusões são reproduzíveis.    |
| `03_data_preparation/data_preparation.ipynb`           | Se todas as transformações estão documentadas e se os datasets são gerados corretamente.                  |
| `03_data_preparation/validacao_data_preparation.ipynb` | Se os testes verificam a qualidade clínica e temporal, além da estrutura dos ficheiros.                   |
| `03_data_preparation/notas_data_preparation.md`        | Se descreve as regras que o código realmente executa.                                                     |
| `03_data_preparation/dataset_final.csv`                | Se corresponde ao objetivo para o qual foi criado e não é confundido com o dataset temporal de regressão. |
| `03_data_preparation/dataset_regressao_24h.csv`        | Se contém uma linha por episódio, preditores válidos e alvo exclusivamente futuro.                        |
| `04_modeling/regressao_carga_dessaturacao.ipynb`       | Se o treino, a validação, as métricas e os gráficos correspondem à versão atual dos dados.                |
| `train.csv` e `test.csv`                               | Se pertencem ao fluxo de modelação ainda utilizado e se não estão desatualizados.                         |
| `normalisation_params.csv`                             | Se os parâmetros são compatíveis com as features e foram estimados sem informação de teste.               |
| `checklist_projeto.md`                                 | Se o alvo e o estado das fases estão atualizados.                                                         |
| `README.md` e relatório final                          | Se explicam o fluxo completo e apresentam resultados atuais, não históricos.                              |

### 2.2. Auditar dependências entre ficheiros

Verifica se cada notebook:

- Lê os ficheiros corretos e a partir de caminhos documentados.
- Gera os outputs de que os passos seguintes necessitam.
- Não depende de variáveis existentes apenas porque o kernel foi executado anteriormente.
- Não lê silenciosamente ficheiros antigos produzidos por outra versão do código.
- Não depende de ficheiros locais que não estão disponíveis a outros membros da equipa.
- Identifica claramente os dados de origem e os datasets derivados.
- Executa sem erros quando todas as células são executadas pela ordem correta.

Um problema a verificar, identificado numa revisão anterior, era a existência de diferenças entre os ficheiros que a preparação produzia e os que o notebook de validação esperava encontrar. Confirma se esta situação foi corrigida.

### 2.3. Distinguir os dois datasets principais

Não assumas que `dataset_final.csv` e `dataset_regressao_24h.csv` são intercambiáveis.

O primeiro pode servir para análises agregadas ao episódio completo. O segundo deve representar o problema temporal de previsão.

Para cada um, regista:

- unidade de observação;
- número de episódios;
- chave primária;
- colunas e respetivas definições;
- janela temporal representada;
- regras de exclusão;
- finalidade analítica;
- notebooks que o consomem.

Critério de aceitação: uma pessoa que abra o repositório deve conseguir perceber imediatamente qual é o dataset apropriado para cada objetivo e porquê.

## 3. Auditoria da qualidade e compreensão dos dados — Data Understanding

A fase de compreensão dos dados deve demonstrar que conheces a estrutura, a qualidade, as limitações e as características clínicas dos dados antes de os utilizares para modelação.

### 3.1. Reconciliação dos episódios e identificadores

Uma revisão anterior encontrou diferenças entre os IDs observados na EDA e os IDs existentes após a normalização na preparação. Também foram identificadas variantes de escrita, como `EP016`, `EP 016` e `ep016`.

Confirma se a normalização atual resolve essas diferenças sem fundir episódios distintos.

- Conta os IDs únicos nos ficheiros de sinais vitais e patologias.
- Normaliza os IDs antes de fazer junções ou calcular interseções.
- Verifica se a normalização gera colisões entre IDs originalmente distintos.
- Calcula o número de episódios presentes nas duas fontes.
- Lista episódios apenas com sinais vitais.
- Lista episódios apenas com patologias.
- Lista episódios presentes em ambas as fontes.
- Compara os episódios de origem com os episódios no dataset final.
- Explica todas as diferenças de contagem.

Cria uma tabela de reconciliação com esta estrutura:

| Indicador                           | Valor atual | Explicação                         |
| ----------------------------------- | ----------- | ---------------------------------- |
| Episódios com sinais vitais         | A calcular  | IDs únicos após normalização       |
| Episódios com patologias            | A calcular  | IDs únicos após normalização       |
| Episódios presentes nas duas fontes | A calcular  | Interseção dos IDs                 |
| Episódios excluídos                 | A calcular  | Com motivo por episódio            |
| Episódios elegíveis para regressão  | A calcular  | Critérios temporais e de cobertura |

Não basta indicar que os números são diferentes. Tens de conseguir explicar porquê.

### 3.2. Auditoria das patologias

Verifica se a normalização dos nomes das patologias é consistente entre a EDA, a preparação e os datasets finais.

- Identifica variantes ortográficas, diferenças de maiúsculas/minúsculas, espaços e acentos.
- Usa um dicionário explícito de normalização.
- Confirma que todas as variantes relevantes são mapeadas para a categoria pretendida.
- Quantifica as patologias antes e depois da normalização.
- Confirma a regra utilizada quando um episódio tem várias patologias.
- Verifica como são tratados episódios sem patologia associada.
- Distingue ausência de registo de ausência real de patologia.
- Confirma que rótulos desconhecidos não são convertidos silenciosamente em classes válidas.

Na análise anterior, as classes eram bastante desequilibradas: havia uma classe com muitos mais episódios do que as restantes, e algumas patologias tinham apenas um ou dois episódios. Confirma se a distribuição atual continua semelhante.

Se também pretendes manter um cenário de classificação, esta distribuição condiciona a forma como podes avaliar o modelo. Não deves apresentar métricas de desempenho para classes que praticamente não têm exemplos de avaliação.

### 3.3. Auditoria dos sinais vitais

Para cada variável — SpO₂, pulso/frequência cardíaca e perfusão — cria um resumo de qualidade.

| Verificação         | O que registar                         |
| ------------------- | -------------------------------------- |
| Tipo de dados       | Numérico, texto ou misto               |
| Valores em falta    | Número e percentagem                   |
| Valores inválidos   | Número e regras aplicadas              |
| Valores extremos    | Número e método de identificação       |
| Unidade             | Unidade efetivamente representada      |
| Intervalo observado | Mínimo, máximo e quantis               |
| Episódios afetados  | Número de episódios com problemas      |
| Decisão             | Manter, corrigir, excluir ou sinalizar |

Confirma ainda:

- A conversão numérica trata corretamente os formatos presentes nos dados.
- Strings vazias e marcadores de ausência são reconhecidos.
- Os limites de validade têm justificação.
- Os valores extremos são investigados antes de serem excluídos.
- Não se confunde um valor clinicamente invulgar com um erro de registo.
- A unidade de cada variável é consistente.
- Os filtros não removem observações válidas por causa da ausência de outra variável que não é necessária para a análise.
- A contagem de observações excluídas é reproduzível.

Na EDA anterior foram contabilizadas 9 857 medições de sinais vitais, das quais 9 615 foram consideradas válidas segundo as regras então utilizadas. Foram também identificadas 242 exclusões. Estes valores são referências históricas: devem ser recalculados na versão atual e as diferenças explicadas.

### 3.4. Auditar valores em falta e exclusões

Esta é uma verificação essencial porque as regras de filtragem podem alterar a população que o modelo representa.

Por exemplo, se uma linha for excluída sempre que qualquer sinal vital esteja em falta, perdes também uma medição de SpO₂ que poderia ser válida para calcular a carga de dessaturação.

Tens de distinguir:

1. valores em falta;
2. valores que não podem ser convertidos;
3. valores que falham os critérios de validade;
4. duplicados removidos;
5. episódios excluídos por cobertura insuficiente;
6. episódios excluídos por falta de dados na janela futura.

- Regista a contagem por motivo.
- Regista o número de linhas afetadas por cada motivo.
- Calcula o total de linhas efetivamente removidas, evitando somar categorias sobrepostas como se fossem independentes.
- Analisa quantos episódios ficam afetados por cada regra.
- Verifica se as exclusões se concentram em determinados tipos de episódios.
- Documenta o efeito das exclusões na distribuição do alvo.

Resultado esperado: uma tabela de auditoria que permita reconstruir o percurso dos dados desde a origem até ao dataset de modelação.

### 3.5. Auditar datas, horas e duplicados

A qualidade temporal é determinante para a regressão.

Verifica:

- Todos os timestamps são convertidos para um formato temporal consistente.
- Os formatos inválidos são contabilizados.
- Os timestamps são ordenados dentro de cada episódio.
- Existem medições com timestamp repetido.
- Existem datas impossíveis ou intervalos temporais anómalos.
- A regra de consolidação de medições no mesmo instante está documentada.
- A regra é aplicada antes da divisão em janelas.
- Os intervalos entre medições são analisados.
- A duração observada de cada episódio é calculada corretamente.
- A ausência de medições durante um intervalo longo não é interpretada automaticamente como ausência de dessaturação.

Se usares a mediana para consolidar várias medições no mesmo instante, confirma que essa é uma decisão deliberada e que os resultados são consistentes com essa regra.

### 3.6. Rever os resultados da EDA

A EDA não deve limitar-se a produzir gráficos. Deve justificar decisões de preparação e modelação.

Para cada gráfico ou análise, pergunta:

- Que questão responde?
- Que conclusão suporta?
- Que decisão do projeto decorre dessa conclusão?
- A conclusão continua válida depois das alterações recentes?
- A conclusão é descritiva ou está a sugerir causalidade?

Confirma especialmente:

- Distribuições dos sinais vitais.
- Distribuição das observações por episódio.
- Distribuição temporal das medições.
- Frequência de valores em falta e inválidos.
- Frequência de dessaturações segundo o limiar operacional.
- Relação entre variáveis fisiológicas.
- Diferenças de cobertura entre episódios.
- Distribuição das patologias.
- Possíveis efeitos de episódios com muito mais medições do que os restantes.

Uma correlação calculada sobre milhares de observações repetidas não equivale a uma correlação entre milhares de doentes independentes. O relatório deve reconhecer que as medições de um mesmo episódio estão relacionadas.

## 4. Auditoria da preparação — Data Preparation

A preparação deve transformar dados de origem em dados analiticamente válidos sem introduzir inconsistências nem utilizar informação futura no cenário de previsão.

### 4.1. Verificar o pipeline de preparação

Percorre o notebook `data_preparation.ipynb` de cima para baixo e identifica a finalidade de cada transformação.

- Normalização de IDs.
- Normalização de patologias.
- Conversão de tipos.
- Tratamento de valores inválidos.
- Tratamento de valores em falta.
- Tratamento de duplicados.
- Construção das variáveis agregadas.
- Construção das janelas temporais.
- Aplicação de critérios de elegibilidade.
- Exportação dos datasets.
- Validação dos outputs.

Para cada etapa, regista as entradas, as saídas, o número de registos antes e depois e a justificação da transformação.

### 4.2. Verificar nomes e integridade das colunas

Em revisões anteriores foram identificados nomes de colunas duplicados, nomeadamente `n_registos` e `carga_dessaturacao`, em alguns datasets.

Confirma se esse problema foi eliminado em todos os ficheiros que continuam ativos.

- Não existem nomes de colunas duplicados.
- Cada coluna tem uma única definição.
- As colunas de identificação não são usadas acidentalmente como preditores.
- A variável-alvo não aparece duplicada com nomes diferentes.
- As colunas geradas por transformações têm nomes claros.
- As colunas de controlo não são confundidas com features clínicas.
- O dataset exportado corresponde às colunas esperadas pelo notebook de modelação.

O facto de um CSV abrir corretamente não garante que o seu esquema seja inequívoco. Esta validação deve ser automatizada.

### 4.3. Rever a construção de `dataset_regressao_24h.csv`

Esta é uma auditoria específica do cenário temporal.

Verifica, para cada episódio:

1. Qual é o instante inicial.
2. Quantas medições válidas existem na janela inicial.
3. Quantas medições válidas existem na janela futura.
4. Qual é a duração efetivamente coberta.
5. Se as duas janelas se sobrepõem.
6. Se o alvo foi calculado apenas com as observações futuras.
7. Se todas as features foram calculadas apenas com a janela inicial.
8. Se o episódio cumpre os critérios mínimos de elegibilidade.

Uma revisão anterior identificou episódios com apenas uma observação na janela inicial e episódios com poucas medições futuras. Confirma se continuam presentes e se a sua inclusão é justificável.

### 4.4. Definir critérios de cobertura mínima

Não basta exigir uma observação válida de cada lado do corte temporal.

Uma única observação inicial pode não representar adequadamente o estado fisiológico nas primeiras 24 horas. Da mesma forma, duas medições futuras podem não permitir estimar de forma fiável uma carga que supostamente representa um horizonte extenso.

Define critérios explícitos para:

- número mínimo de observações iniciais;
- número mínimo de observações futuras;
- cobertura temporal mínima;
- duração máxima de lacunas tolerada;
- tratamento de episódios com interrupção precoce da monitorização;
- tratamento de episódios sem cobertura completa do horizonte;
- regras de exclusão e respetivos motivos.

Os limites não devem ser escolhidos para melhorar artificialmente os resultados do modelo. Devem ser justificados pela finalidade analítica e pela qualidade real dos dados.

Faz também uma análise de sensibilidade: compara o número de episódios e os resultados sob diferentes regras de cobertura plausíveis, sem escolher retrospetivamente a regra que dá a melhor métrica.

### 4.5. Auditar a normalização e o pré-processamento

Se existirem normalização, imputação ou seleção de features antes do treino, confirma em que momento são calculadas.

- Os parâmetros não são estimados usando o conjunto de teste.
- Os parâmetros são ajustados apenas com o treino de cada fold durante a validação cruzada.
- O mesmo procedimento é aplicado na avaliação e na utilização futura do modelo.
- As features transformadas continuam a ter significado.
- Os ficheiros de parâmetros correspondem à versão efetiva do pipeline.

Se o ficheiro `normalisation_params.csv` for utilizado para aplicar transformações, deves verificar a origem de cada parâmetro e garantir que não contém informação calculada a partir de dados que deveriam estar reservados para avaliação.

## 5. Auditoria da separação temporal e do data leakage

Esta secção é um dos principais critérios de aprovação do trabalho.

Data leakage ocorre quando o modelo recebe informação que não estaria disponível no momento em que a previsão seria feita. Pode acontecer mesmo que não exista uma coluna chamada “alvo” entre os preditores.

### 5.1. Confirmar a âncora temporal

A revisão anterior indicava que as primeiras 24 horas eram contadas a partir do primeiro timestamp válido, e não necessariamente da hora clínica de admissão.

Confirma:

- Existe uma hora de admissão fiável?
- Se não existe, a primeira medição válida é usada como aproximação?
- A aproximação é aplicada consistentemente?
- A diferença entre primeiro registo e admissão é reconhecida como limitação?
- A elegibilidade, as features e o alvo usam a mesma âncora?
- O relatório descreve exatamente essa regra?

Se o objetivo for fazer uma previsão 24 horas após a admissão, mas o código começar a contar a partir da primeira medição, tens de explicar a diferença ou alterar o desenho. Não deves tratar os dois instantes como equivalentes sem evidência.

### 5.2. Auditar cada feature individualmente

Cria um inventário com estas colunas:

| Campo           | Pergunta                                             |
| --------------- | ---------------------------------------------------- |
| Nome            | Qual é a variável?                                   |
| Definição       | Como é calculada?                                    |
| Origem          | De que dados deriva?                                 |
| Janela          | Que período de observação utiliza?                   |
| Disponibilidade | Já é conhecida no instante da previsão?              |
| Risco           | Pode conter informação futura ou um proxy do futuro? |
| Decisão         | Manter, transformar ou excluir?                      |

Revê especialmente as variáveis já identificadas no projeto:

- `sat_o2_mean`, `sat_o2_std`, `sat_o2_min`, `sat_o2_max`;
- estatísticas de pulso;
- estatísticas de perfusão;
- `desat_count`;
- `desat_pct`;
- `carga_desat_janela`;
- `n_spo2_validos`;
- `n_all_validos`;
- `n_registos_janela`;
- `n_registos_futuro`.

Para cada uma, confirma que é calculada exclusivamente com informação disponível até ao momento da previsão.

### 5.3. Colunas que exigem atenção especial

`n_registos_futuro`

O número de medições futuras só é conhecido depois de terminado o período futuro. Por isso, não deve entrar nos preditores de uma previsão feita antes desse período.

Pode ser utilizado para auditoria da qualidade do alvo e para estudar a cobertura, mas não como feature antecipada.

`carga_dessaturacao`, `desat_count` e `desat_pct`

Confirma se são calculados apenas na janela inicial ou sobre o episódio completo. Se usarem o episódio completo, não podem ser utilizados como preditores de uma previsão antecipada.

`duracao_dias`

Se representar a duração total do internamento, é normalmente uma variável conhecida apenas depois de terminado o episódio. A sua inclusão como preditor pode introduzir leakage.

`pat_predominante` e `pat_label`

Se forem derivados do diagnóstico final ou de informação consolidada ao longo do internamento, não devem ser usados como preditores de uma previsão nas primeiras 24 horas, a menos que a informação esteja realmente disponível no momento de previsão e isso faça parte do objetivo definido.

### 5.4. Verificações automatizadas de leakage

O notebook de validação deve conter testes explícitos que falhem quando:

- O alvo aparece em `X`.
- Uma coluna proibida aparece entre as features.
- Uma feature usa observações posteriores ao corte.
- As janelas temporalmente separadas apresentam sobreposição.
- Um parâmetro de pré-processamento foi ajustado com dados de teste.
- O mesmo episódio aparece em treino e teste.
- A lista efetiva de features diverge da lista aprovada.

A prevenção de leakage não deve depender apenas de uma revisão manual feita uma vez.

## 6. Auditoria da variável-alvo e da sua distribuição

Depois de confirmar a definição e a separação temporal, analisa se o alvo tem propriedades que permitem uma regressão informativa.

### 6.1. Estatísticas que deves recalcular

Para a versão atual de `dataset_regressao_24h.csv`, calcula:

- número de episódios;
- número de valores em falta;
- número de valores não finitos;
- mínimo e máximo;
- média e mediana;
- desvio-padrão;
- quartis;
- percentagem de alvos iguais a zero;
- percentagem de valores positivos;
- distribuição dos valores extremos.

Uma revisão anterior encontrou 43 episódios elegíveis, 30 alvos iguais a zero em 43 e mediana igual a zero. Estes números devem ser confirmados novamente.

### 6.2. Interpretar a concentração de zeros

Se muitos episódios tiverem alvo igual a zero, o modelo pode conseguir uma boa métrica simplesmente prevendo valores baixos.

Isto não significa necessariamente que o modelo tenha aprendido a identificar episódios com maior carga de dessaturação.

Tens de verificar:

- Se os zeros representam realmente ausência de dessaturação ou ausência de observações suficientes.
- Se o alvo está concentrado perto de zero.
- Se existem poucos episódios com carga elevada.
- Se esses episódios estão representados na avaliação.
- Se os erros são maiores nos episódios de carga elevada.
- Se o baseline constante já tem desempenho forte devido à distribuição.
- Se as métricas escondem a incapacidade de prever casos extremos.

Se os zeros forem causados por falta de observações ou cobertura insuficiente, o problema não é apenas estatístico: pode ser um problema de qualidade da variável-alvo.

### 6.3. Analisar a relação com a cobertura futura

Nas versões anteriores, `n_registos_futuro` variava muito entre episódios.

Verifica se a carga futura aumenta com o número de medições ou com a duração da observação.

- Gráfico do alvo versus número de medições futuras.
- Gráfico do alvo versus duração observada.
- Identificação de episódios com cobertura muito baixa.
- Identificação de episódios com cobertura muito elevada.
- Comparação da distribuição do alvo entre grupos de cobertura.
- Avaliação de quanto da variabilidade do alvo pode resultar da oportunidade de observar, e não apenas do fenómeno clínico.

Se o alvo for uma soma por observação, é expectável que a frequência de registo possa influenciar o resultado. Isso deve ser resolvido ou assumido explicitamente antes de se concluir que o modelo estima a carga clínica pretendida.

## 7. Auditoria do treino, validação e avaliação dos modelos

O objetivo não é obter a melhor métrica possível à força. É verificar se a avaliação mede de forma credível a capacidade de generalizar para episódios que não foram utilizados no treino.

### 7.1. Verificar a unidade de divisão dos dados

A unidade de avaliação deve ser o episódio.

- Todos os registos de um mesmo episódio permanecem no mesmo conjunto.
- Nenhuma transformação utiliza os alvos do conjunto de teste.
- O conjunto de teste não é utilizado para escolher hiperparâmetros.
- A divisão não foi escolhida por produzir resultados mais favoráveis.
- O número de episódios por conjunto é reportado.

Se cada linha do dataset já corresponder a um episódio único, confirma a unicidade da chave e que a divisão é efetivamente feita por episódio.

### 7.2. Verificar o baseline

O baseline é essencial para saber se a regressão acrescenta valor.

No caso de uma regressão, um baseline constante pode prever a mediana do alvo observada no conjunto de treino. A mediana nunca deve ser calculada com os valores reais do conjunto avaliado.

Confirma:

- O baseline é treinado apenas com os dados de treino.
- As suas previsões são calculadas nas mesmas observações avaliadas para os outros modelos.
- As métricas são calculadas com a mesma definição de alvo.
- O baseline é apresentado no relatório.
- A comparação não é feita entre conjuntos diferentes.

Na avaliação anterior, o baseline apresentava erros muito inferiores aos dos modelos linear e Ridge no split analisado. Confirma se os resultados atuais alteraram essa conclusão.

### 7.3. Verificar as métricas

As métricas principais são:

- MAE: erro absoluto médio, na unidade do alvo.
- RMSE: raiz do erro quadrático médio, que penaliza mais os erros grandes.
- R²: comparação com uma referência baseada na variabilidade do alvo; pode ser negativo e ser instável quando a amostra é pequena.

Audita:

- As métricas são calculadas corretamente.
- A unidade do MAE e RMSE está explícita.
- O número de episódios avaliados aparece junto às métricas.
- As métricas do baseline e dos modelos usam as mesmas observações.
- Os resultados correspondem à execução atual do notebook.
- As limitações da distribuição do alvo são discutidas.
- A conclusão não depende apenas de uma métrica isolada.

Não estabeleças um limite de erro aceitável sem justificar o seu significado para o objetivo clínico. Uma métrica só ganha interpretação prática quando a unidade do alvo está definida.

### 7.4. Auditar a dimensão da amostra e o sobreajustamento

Com poucas dezenas de episódios, utilizar muitas features pode gerar um modelo instável.

- Compara o número de episódios de treino com o número de features.
- Identifica features redundantes ou altamente correlacionadas.
- Justifica a complexidade dos modelos.
- Verifica se os resultados dependem fortemente de um ou dois episódios.
- Compara os resultados em diferentes partições ou folds.
- Evita apresentar uma única divisão como prova definitiva de generalização.

Na revisão anterior, o conjunto de teste tinha apenas nove episódios e não incluía o caso com o maior alvo observado. Isso limitava a capacidade de avaliar os erros nos episódios com maior carga. Confirma a composição do teste atual, incluindo a amplitude dos valores reais.

### 7.5. Rever a validação cruzada

A validação cruzada por episódio pode ajudar a utilizar melhor uma amostra pequena, mas não elimina a incerteza.

Verifica se:

- A estratégia de validação está explicitamente definida.
- Cada episódio recebe previsões fora do fold em que foi treinado.
- O pré-processamento é ajustado de novo em cada fold.
- A seleção de hiperparâmetros é feita sem consultar o fold de avaliação.
- O baseline é recalculado dentro de cada fold.
- As previsões e os erros são guardados por episódio.
- São reportadas a média e a variabilidade das métricas.

Se utilizares Leave-One-Out, cada modelo é treinado em quase todos os episódios e avaliado num único episódio. É útil em certos contextos de amostra pequena, mas as métricas podem continuar a ser muito sensíveis a episódios individuais. Deve ser descrito como uma estratégia de avaliação, não como garantia de robustez.

### 7.6. Auditar o tratamento de valores em falta no modelo

Uma revisão anterior identificou imputação de valores em falta por `0.0` em features. Confirma se continua a existir.

Substituir uma ausência por zero pode confundir:

- uma saturação real;
- uma frequência cardíaca real;
- uma ausência de medição;
- um valor que nem sequer foi calculado.

Deves:

- Identificar todas as colunas com valores em falta.
- Confirmar a estratégia de imputação.
- Ajustar a imputação apenas no treino de cada fold.
- Considerar indicadores de ausência quando fizer sentido.
- Verificar se a imputação altera substancialmente as previsões.
- Garantir que a estratégia é idêntica no treino e na utilização futura.

### 7.7. Verificar consistência entre código e resultados

Na revisão anterior existia uma divergência entre o valor de `alpha` indicado no texto/gráfico da Ridge e o valor usado nos resultados.

Confirma:

- O valor de `alpha` no código coincide com o valor documentado.
- O gráfico corresponde aos resultados atuais.
- Os outputs do notebook não são de uma execução antiga.
- A tabela final é gerada a partir dos resultados efetivos.
- As sementes aleatórias, quando aplicáveis, estão documentadas.
- As versões das bibliotecas estão registadas.

A recomendação é executar o notebook de modelação de raiz depois de corrigidas as questões metodológicas, em vez de confiar nos outputs guardados anteriormente.

## 8. Auditoria dos resultados e da interpretação clínica

Mesmo quando o pipeline é tecnicamente correto, é necessário verificar se as conclusões são proporcionais à evidência.

### 8.1. Análise de erros por episódio

Produz uma tabela com:

| Episódio   | Alvo real | Previsão | Erro absoluto | Observações futuras | Cobertura |
| ---------- | --------- | -------- | ------------- | ------------------- | --------- |
| Episódio A | —         | —        | —             | —                   | —         |
| Episódio B | —         | —        | —             | —                   | —         |

Os valores devem ser preenchidos a partir da execução atual, não manualmente a partir de outputs antigos.

Investiga:

- episódios com maiores erros absolutos;
- episódios em que o modelo prevê carga quase nula apesar de o alvo ser elevado;
- episódios com alvo zero e previsão elevada;
- relação entre erro e número de medições;
- relação entre erro e cobertura;
- relação entre erro e variabilidade dos sinais vitais iniciais.

Se apresentares exemplos, remove identificadores pessoais e limita a exposição de dados clínicos ao necessário para a avaliação académica.

### 8.2. Gráficos de diagnóstico

Inclui, se forem informativos:

1. valores reais versus valores previstos;
2. distribuição dos resíduos;
3. erro absoluto por episódio;
4. distribuição do alvo;
5. alvo versus número de medições futuras;
6. resultados do baseline versus resultados do modelo.

Cada gráfico deve ter título, eixos, unidades e uma interpretação. Não incluas gráficos apenas para aumentar o volume do relatório.

### 8.3. Verificar o valor para o profissional de saúde

A pergunta não é apenas se o modelo prevê bem, mas se a previsão é útil para o fim proposto.

- O alvo corresponde a uma grandeza que pode ser interpretada.
- O erro é apresentado na unidade correta.
- Está definido que tipo de erro teria importância prática.
- O modelo acrescenta informação face ao baseline.
- A incerteza e as limitações estão explícitas.
- A previsão não é apresentada como diagnóstico nem como recomendação clínica autónoma.
- O relatório distingue potencial de utilização de benefício efetivamente demonstrado.

Se não houver evidência de utilidade superior ao baseline, a conclusão correta é que a utilidade preditiva ainda não foi demonstrada. Isso não invalida necessariamente o trabalho de análise e preparação, mas limita o que se pode afirmar sobre o modelo.

## 9. Auditoria dos testes de validação

O notebook de validação deve testar regras substantivas do projeto, não apenas confirmar que os ficheiros existem.

### 9.1. Testes estruturais

- O ficheiro de saída existe.
- O dataset pode ser carregado.
- A chave do episódio é única e não nula.
- Não existem colunas duplicadas.
- O esquema de colunas corresponde ao esperado.
- Os tipos de dados são adequados.
- O alvo é finito e respeita o domínio definido.

### 9.2. Testes temporais

- A janela inicial e a janela futura não se sobrepõem.
- O corte é consistente em todos os episódios.
- Os timestamps são válidos e ordenados.
- O alvo é recalculável a partir da janela futura.
- As features são recalculáveis apenas a partir da janela inicial.
- Os episódios cumprem os critérios de cobertura.
- As exclusões por falta de cobertura são explicáveis.

### 9.3. Testes de modelação

- O conjunto de features não inclui colunas proibidas.
- O split não divide o mesmo episódio entre treino e teste.
- A imputação e a normalização são ajustadas apenas no treino.
- O baseline é calculado corretamente.
- O conjunto de teste não influencia a escolha do modelo.
- As métricas são recalculáveis a partir das previsões guardadas.

### 9.4. Testes de regressão do pipeline

Sempre que alterares a preparação, verifica se os resultados fundamentais mudaram.

Regista:

- número de episódios;
- número de colunas;
- número de episódios excluídos;
- distribuição do alvo;
- features finais;
- resultados do baseline;
- resultados dos modelos;
- hash ou versão do código, se disponível.

Não exijas que todos os números se mantenham iguais depois de uma alteração legítima. Exige, isso sim, que cada diferença seja explicada e que os testes relevantes continuem a passar.

## 10. Auditoria da documentação e do CRISP-DM

A documentação deve representar a implementação final, não a intenção original nem uma versão anterior do projeto.

### 10.1. Business Understanding

Confirma:

- O objetivo de negócio é específico.
- O cenário de regressão está claramente definido.
- A variável-alvo tem a mesma definição que no código.
- O horizonte temporal coincide com a preparação.
- As métricas de sucesso são justificadas.
- As limitações do conjunto de dados são reconhecidas.
- Os critérios de sucesso não pressupõem resultados que ainda não foram demonstrados.

### 10.2. Data Understanding

O relatório deve explicar:

- origem e estrutura dos dados;
- unidade de análise;
- número de episódios;
- variáveis disponíveis;
- qualidade e limitações;
- valores em falta;
- inconsistências de IDs e datas;
- distribuição dos sinais vitais;
- distribuição das patologias;
- principais conclusões que motivaram a preparação.

### 10.3. Data Preparation

Documenta:

- normalização dos IDs;
- normalização das patologias;
- conversões e filtros;
- tratamento de duplicados;
- tratamento de valores em falta;
- construção das features;
- definição das janelas;
- definição do alvo;
- critérios de elegibilidade;
- ficheiros de saída e respetivas finalidades.

### 10.4. Modeling

Documenta:

- modelos avaliados;
- features utilizadas;
- estratégia de validação;
- tratamento de valores em falta;
- baseline;
- hiperparâmetros;
- métricas;
- resultados por episódio;
- limitações e razões para escolher ou não um modelo.

### 10.5. Checklist, README e notas

Na revisão anterior, o `checklist_projeto.md` ainda indicava `duracao_dias` como alvo de regressão, apesar de o cenário de trabalho ter passado para carga de dessaturação.

Confirma se a divergência foi corrigida.

Verifica também se:

- O README descreve a sequência de execução.
- O checklist reflete as decisões atuais.
- As notas de preparação correspondem ao código.
- O relatório de negócio não descreve uma fórmula diferente.
- Os resultados apresentados correspondem à última execução.
- Os outputs antigos estão identificados como históricos ou removidos.
- As limitações são explícitas.
- O projeto não afirma que o modelo está clinicamente validado sem evidência apropriada.

## 11. Auditoria da reprodutibilidade

A consolidação não está concluída se os resultados só puderem ser reproduzidos pelo autor original.

### 11.1. Execução limpa

- Reinicia o kernel de cada notebook.
- Executa todas as células pela ordem apresentada.
- Confirma que não existem variáveis dependentes de execução anterior.
- Confirma que todos os ficheiros de entrada estão disponíveis.
- Confirma que todos os outputs necessários são gerados.
- Confirma que os caminhos funcionam noutro ambiente de execução.
- Confirma que não existem dependências locais não documentadas.

### 11.2. Ambiente

Documenta:

- versão de Python;
- principais bibliotecas;
- ficheiros de dependências, se existirem;
- sementes aleatórias;
- comandos ou sequência para executar o pipeline;
- origem dos dados;
- limitações de acesso aos dados.

### 11.3. Resultados finais

A partir de uma execução limpa, gera novamente:

- datasets preparados;
- tabela de validação;
- resultados da avaliação;
- previsões por episódio;
- gráficos finais;
- tabelas usadas no relatório.

Compara-os com os outputs anteriores. Se houver diferenças, identifica a causa antes de publicar os resultados.

## 12. Ordem recomendada para efetuar a revisão

Para evitar trabalho duplicado, segue esta sequência.

## 1

Definir o problema

Aprovar a definição do alvo, a unidade, a janela inicial, o horizonte futuro e o uso pretendido.

Entregável: especificação formal do cenário de regressão.

## 2

Auditar os dados de origem

Reconciliar IDs, patologias, datas, sinais vitais, duplicados e valores em falta.

Entregável: relatório de qualidade e reconciliação.

## 3

Auditar a preparação temporal

Confirmar a âncora temporal, a separação das janelas, a cobertura e a construção do alvo.

Entregável: dataset validado e tabela de exclusões.

## 4

Auditar o leakage e o pré-processamento

Inspecionar cada feature e garantir que as transformações são ajustadas apenas nos dados de treino.

Entregável: inventário de features aprovado e testes automáticos.

## 5

Reavaliar os modelos

Comparar baseline, regressão linear e Ridge com uma estratégia de avaliação apropriada ao número de episódios.

Entregável: métricas reproduzíveis e erros por episódio.

## 6

Consolidar a documentação

Atualizar README, checklist, notas, relatório de negócio e conclusões.

Entregável: documentação coerente com o código final.

## 7

Executar a auditoria final

Executar os notebooks de raiz, verificar todos os testes e registar os problemas que permanecem.

Entregável: decisão final de consolidação e limitações assumidas.

## 13. Checklist de trabalho para acompanhar a revisão

Podes usar esta lista para controlar o progresso da auditoria.

## Progresso da auditoria

### 0/33

### Objetivo

Definir formalmente o alvo e a sua unidade

Escolher o horizonte temporal futuro

Confirmar a âncora temporal

Documentar a finalidade e os limites de uso

### Data Understanding

Reconciliar os IDs entre fontes

Auditar a normalização das patologias

Auditar sinais vitais e unidades

Quantificar ausências, inválidos e exclusões

Auditar timestamps e duplicados

Rever as conclusões da EDA

### Data Preparation

Verificar o esquema dos datasets

Eliminar nomes de colunas duplicados

Validar a separação temporal

Definir cobertura mínima

Recalcular e validar o alvo

Documentar a lista de features

### Leakage

Confirmar que nenhuma feature usa dados futuros

Excluir n_registos_futuro dos preditores

Excluir alvos e proxies do alvo

Garantir pré-processamento apenas no treino

Garantir divisão por episódio

### Modelação

Recalcular a distribuição do alvo

Comparar com baseline

Validar MAE, RMSE e R²

Avaliar a variabilidade entre folds

Inspecionar erros por episódio

Confirmar hiperparâmetros e outputs

### Documentação e reprodução

Atualizar README e checklist

Alinhar relatório de negócio e código

Executar notebooks de raiz

Regerar outputs finais

Registar limitações e decisões

Emitir decisão final de consolidação

Reiniciar listaCopiar checklist

## 14. Critérios para considerar o projeto consolidado

A consolidação deve ser avaliada por critérios de aceitação, não apenas pela ausência de erros de execução.

| Área                | Critério para aprovação                                                 |
| ------------------- | ----------------------------------------------------------------------- |
| Objetivo clínico    | Alvo, unidade, horizonte e uso pretendido definidos sem ambiguidades.   |
| Qualidade dos dados | IDs, datas, duplicados, ausências e exclusões auditados.                |
| Preparação          | Transformações reproduzíveis e esquemas de datasets coerentes.          |
| Temporalidade       | Features exclusivamente iniciais e alvo exclusivamente futuro.          |
| Cobertura           | Critérios de elegibilidade explícitos e aplicados de forma consistente. |
| Leakage             | Colunas e transformações proibidas excluídas e controladas por testes.  |
| Modelação           | Avaliação por episódio, baseline comparável e métricas reproduzíveis.   |
| Interpretação       | Conclusões proporcionais ao tamanho e à qualidade da amostra.           |
| Documentação        | README, checklist, relatório e notebooks concordantes.                  |
| Reprodutibilidade   | Execução limpa e outputs regeneráveis.                                  |

A decisão final deve enquadrar-se numa destas três categorias:

- Consolidado: os critérios essenciais estão cumpridos e as conclusões são sustentadas pela avaliação.
- Consolidado com limitações: o pipeline está coerente e reproduzível, mas a evidência é exploratória ou a amostra é insuficiente para demonstrar utilidade preditiva robusta.
- Ainda não consolidado: existem contradições no alvo, problemas de temporalidade, leakage, avaliação contaminada ou falhas de reprodução.

## 15. Os problemas que eu verificaria primeiro no teu projeto

Com base nas revisões anteriores, começaria por estes seis pontos, por esta ordem:

1. Definição da carga de dessaturação: confirmar que a fórmula implementada mede a grandeza descrita no objetivo de negócio.
2. Âncora das primeiras 24 horas: confirmar se o primeiro registo válido representa adequadamente o início do episódio para a pergunta de previsão.
3. Cobertura mínima: verificar se os episódios com poucas observações iniciais ou futuras continuam a ser aceites.
4. Dependência do alvo da frequência de registo: quantificar se a carga aumenta sobretudo porque existem mais observações futuras.
5. Validação do modelo: verificar se o baseline continua a superar os modelos e se a avaliação representa episódios com cargas elevadas.
6. Coerência documental: confirmar que o README, o checklist, o relatório de negócio e o notebook de regressão descrevem exatamente o mesmo cenário.

Estes pontos têm precedência sobre melhorias estéticas nos gráficos, reorganização de células ou adição de modelos mais complexos.

Conclusão: o objetivo da consolidação não é provar que a regressão funciona. É provar que a variável-alvo tem significado, que os dados usados para prever estão disponíveis no momento correto, que a avaliação é justa e que as conclusões refletem o que os resultados realmente demonstram. Se estas condições forem satisfeitas, o projeto estará metodologicamente muito mais sólido, mesmo que a conclusão final seja que o modelo ainda não demonstra utilidade preditiva suficiente.
