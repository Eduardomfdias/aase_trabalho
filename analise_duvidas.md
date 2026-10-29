# Plano de Correção e Consolidação do Projeto AASE — Instruções para Claude Code

## 1. Objetivo

Realizar uma revisão técnica e metodológica do repositório AASE, corrigir inconsistências entre código, datasets, outputs, testes e documentação, e deixar o projeto reproduzível.

Repositório: `Eduardomfdias/aase_trabalho`

Trabalhar prioritariamente nos seguintes ficheiros:

- `relatorio_auditoria.md`
- `README.md`
- `checklist_projeto.md`
- `03_data_preparation/data_preparation.ipynb`
- `03_data_preparation/validacao_data_preparation.ipynb`
- `03_data_preparation/notas_data_preparation.md`
- `03_data_preparation/dataset_final.csv`
- `03_data_preparation/dataset_regressao_24h.csv`
- `03_data_preparation/metadata.csv`
- `04_modeling/regressao_carga_dessaturacao.ipynb`
- `04_modeling/predicoes_teste.csv`

Não assumir que esta lista é exaustiva. Inspecionar a estrutura real do repositório antes de modificar ficheiros.

## 2. Regras obrigatórias de execução

1. Inspecionar primeiro o estado do Git, a estrutura do projeto e os conteúdos atuais dos ficheiros.
2. Não apagar alterações preexistentes do utilizador.
3. Não sobrescrever alterações locais sem as identificar e compreender.
4. Não alterar dados brutos para fazer os resultados coincidirem com os outputs existentes.
5. Não inventar valores, patologias, timestamps, resultados de modelos ou critérios clínicos.
6. Não considerar um notebook validado apenas porque os seus outputs guardados parecem corretos.
7. Executar o código e regenerar os artefactos a partir das fontes disponíveis.
8. Se faltar algum ficheiro bruto ou dependência, documentar o bloqueio e continuar com as verificações possíveis.
9. Não fazer commits nem publicar alterações sem autorização explícita.
10. Manter a linguagem e o contexto académico do projeto, usando português europeu na documentação.

Antes de começar, apresentar um resumo do estado do Git, dos problemas encontrados e do plano de alterações. Depois avançar com as correções sem esperar por aprovação, exceto quando uma decisão exigir informação clínica ou de negócio que não exista no repositório.

## 3. Fase 1 — Auditoria do estado atual

### 3.1. Inventário

- Identificar os ficheiros de origem, os ficheiros gerados e os artefactos versionados.
- Identificar as instruções de execução, dependências e caminhos relativos utilizados pelos notebooks.
- Identificar outputs guardados que possam pertencer a versões anteriores do código.
- Verificar o estado do Git antes de alterar qualquer ficheiro.

### 3.2. Comparação código versus artefactos

Comparar os critérios e resultados efetivamente produzidos com os que estão escritos no código e na documentação.

Verificar especificamente:

- O número de episódios nos dados brutos, nos dados normalizados, no dataset final e no dataset de regressão.
- A normalização dos IDs dos episódios.
- A normalização e atribuição de etiquetas das patologias.
- A elegibilidade temporal de cada episódio.
- As colunas e respetiva ordem nos CSVs.
- As métricas e previsões guardadas no notebook de regressão.
- A coerência entre o relatório de auditoria, o README, as notas e a checklist.

Produzir uma tabela de discrepâncias com: ficheiro, problema, evidência, impacto, correção proposta e estado.

## 4. Fase 2 — Corrigir a preparação dos dados

### 4.1. Critérios de elegibilidade do dataset de regressão

O notebook de preparação contém atualmente um critério de pelo menos:

- 5 registos válidos de SpO₂ na janela inicial;
- 3 registos válidos de SpO₂ na janela futura.

Os artefactos anteriormente observados não respeitam consistentemente este critério.

Ações:

1. Localizar e rever a implementação efetiva do filtro de elegibilidade.
2. Garantir que os limites são aplicados aos registos válidos de SpO₂, e não apenas ao número total de linhas.
3. Excluir da regressão os episódios que não cumprem os limites definidos, registando os motivos.
4. Regenerar `dataset_regressao_24h.csv` a partir do código atualizado.
5. Não fixar antecipadamente o número de episódios esperado: calculá-lo a partir dos dados reais.
6. Gerar um relatório de elegibilidade por episódio, com contagens na janela inicial e futura e motivo de inclusão ou exclusão.

### 4.2. Integridade temporal

Rever a construção das janelas:

- Confirmar a interpretação e a normalização das datas.
- Confirmar a ordenação cronológica dentro de cada episódio.
- Confirmar a deduplicação de timestamps e a aplicação da mediana.
- Verificar timestamps inválidos, datas ambíguas e registos sem hora válida.
- Garantir que os registos da janela inicial não entram na janela futura.
- Garantir que nenhum registo futuro contribui para os preditores iniciais.
- Documentar que o início da janela corresponde ao primeiro timestamp válido, caso não exista uma data de admissão clínica fiável.

Não inventar uma data de admissão. Se os dados não permitirem determinar o início clínico do internamento, manter a aproximação explicitamente documentada e assinalar a limitação.

### 4.3. Definição do alvo

A definição atualmente implementada é uma soma dos défices observados:

`carga_dessaturacao_futura = Σ(90 - SpO₂)` para observações futuras com SpO₂ inferior a 90%.

Esta variável não representa diretamente horas de dessaturação nem uma carga integrada no tempo.

Ações:

- Preservar a fórmula atual enquanto definição operacional, salvo decisão explícita e fundamentada em contrário.
- Documentar a unidade como soma de pontos percentuais de défice por observação, sem a apresentar como horas.
- Garantir que apenas valores válidos de SpO₂ contribuem para o cálculo.
- Confirmar que o alvo é finito e não negativo.
- Quantificar a relação entre o alvo e o número de observações futuras.
- Avaliar a variação da duração do seguimento futuro entre episódios.

Não alterar silenciosamente a fórmula para uma medida temporal. Se os dados não permitirem medir a duração real das dessaturações, registar essa limitação.

### 4.4. Datasets e colunas

- Garantir nomes de colunas únicos em todos os CSVs.
- Garantir que cada episódio aparece no máximo uma vez em cada dataset agregado.
- Separar claramente as finalidades de `dataset_final.csv` e `dataset_regressao_24h.csv`.
- Verificar que os targets não são incluídos como preditores da respetiva tarefa.
- Preservar os dados brutos e documentar todas as transformações.
- Garantir que os CSVs gerados podem ser reconstruídos a partir das fontes e do código versionados.

## 5. Fase 3 — Resolver a divergência nas patologias

Foi identificada uma divergência entre os outputs guardados do notebook de preparação e o ficheiro `metadata.csv`, envolvendo Refluxo Gastroesofágico e Displasia Broncopulmonar.

Não escolher uma das classes por suposição.

Ações:

1. Inspecionar os ficheiros de origem das patologias.
2. Rever a função de normalização de nomes e variantes.
3. Comparar os IDs dos episódios entre sinais vitais e patologias.
4. Confirmar a regra usada para escolher a patologia predominante em caso de empate.
5. Regenerar `dataset_final.csv` e `metadata.csv`.
6. Verificar se a etiqueta numérica corresponde sempre ao nome da patologia.
7. Verificar se a soma das contagens por classe coincide com o número de episódios rotulados.
8. Documentar episódios sem patologia e a sua exclusão da classificação supervisionada, quando aplicável.

Criar testes automáticos para assegurar que:

- Cada etiqueta corresponde a um único nome de patologia.
- Cada nome de patologia corresponde a uma única etiqueta.
- As contagens de `metadata.csv` correspondem aos episódios efetivamente rotulados.
- Não existem variantes textuais conhecidas sem normalização documentada.

Se não for possível resolver a divergência com os dados disponíveis, deixar o problema explicitamente aberto, sem escolher uma resposta arbitrária.

## 6. Fase 4 — Corrigir a avaliação da regressão

### 6.1. Atualização dos artefactos

Depois de regenerar o dataset:

- Reexecutar o notebook de regressão.
- Regenerar `predicoes_teste.csv` e os gráficos associados.
- Garantir que os outputs guardados correspondem ao código atual.
- Registar o número de episódios efetivamente usados em cada etapa.

Não reutilizar como resultados finais as métricas calculadas sobre o dataset anterior.

### 6.2. Valores em falta

O código atual substitui valores ausentes por `0.0` em `get_X()`.

Corrigir esta abordagem:

- Distinguir ausência de medição de valor clínico real.
- Implementar imputação explícita, ajustada exclusivamente aos dados de treino.
- Se for usada validação cruzada, ajustar a imputação dentro de cada fold.
- Avaliar se determinadas variáveis ou episódios devem ser excluídos quando a cobertura é insuficiente.
- Documentar a estratégia escolhida.

Não imputar o alvo. Um episódio sem alvo calculável deve ser excluído da modelação supervisionada, com o motivo registado.

### 6.3. Fuga de informação

Auditar individualmente todos os preditores.

Excluir sempre:

- `carga_dessaturacao_futura`;
- `n_registos_futuro`, por ser informação futura;
- variáveis derivadas do episódio completo ou do período futuro;
- a própria variável-alvo ou transformações equivalentes.

Rever `desat_count`, `desat_pct` e `carga_desat_janela` para confirmar que são calculadas exclusivamente na janela inicial.

Verificar também se as restantes variáveis de contagem são conhecidas no momento em que a previsão seria produzida.

Criar testes automáticos que falhem quando o alvo ou variáveis futuras entram nos preditores.

### 6.4. Avaliação e comparação

Manter um baseline simples baseado na mediana calculada apenas no treino.

Comparar o baseline com os modelos linear e Ridge, usando:

- MAE;
- RMSE;
- R², com cautela quando a variância do teste é muito pequena;
- análise dos erros por episódio.

Implementar validação cruzada adequada à pequena amostra, preferencialmente leave-one-out ou outra estratégia justificada.

Garantir que a normalização, imputação e escolha de hiperparâmetros não utilizam os dados de validação ou teste. Se for ajustado o parâmetro de Ridge, fazê-lo apenas dentro do processo de validação.

Se o baseline superar os modelos, declarar que não foi demonstrado ganho preditivo. Não escolher o modelo com base apenas no resultado de treino.

A avaliação deve continuar a ser apresentada como exploratória, não como validação clínica.

## 7. Fase 5 — Reforçar o notebook de validação

O notebook `validacao_data_preparation.ipynb` deve testar efetivamente as regras definidas na preparação.

Implementar, no mínimo, verificações para:

### Estrutura

- Ausência de colunas duplicadas.
- Unicidade de IDs nos datasets agregados.
- Tipos de dados e valores numéricos válidos.
- Ausência de targets não finitos ou negativos, quando aplicável.

### Elegibilidade temporal

- Pelo menos 5 registos válidos de SpO₂ na janela inicial.
- Pelo menos 3 registos válidos de SpO₂ na janela futura.
- Ausência de sobreposição entre janelas.
- Ordenação temporal correta.
- Exclusão ou contabilização explícita de timestamps inválidos.
- Ausência de duplicados após a consolidação dos timestamps.

### Fuga de informação

- Ausência do target nos preditores.
- Ausência de `n_registos_futuro` nos preditores.
- Ausência de features calculadas com dados futuros ou do episódio completo.

### Consistência semântica

- Fórmula do alvo documentada e testada.
- Correspondência entre etiquetas e patologias.
- Contagens do metadata consistentes com os datasets.
- Razões de exclusão contabilizadas.

### Testes de fronteira

Criar pequenos casos artificiais para testar:

- Exatamente 5 registos iniciais e 3 futuros.
- Um registo inicial abaixo do mínimo.
- Um registo futuro abaixo do mínimo.
- Datas inválidas.
- Timestamps duplicados.
- SpO₂ igual a 90%, abaixo de 90% e acima de 90%.
- Episódios sem dessaturação futura.

Os testes devem falhar com mensagens explícitas quando uma condição não é cumprida. Evitar mensagens de sucesso globais quando alguma verificação relevante foi ignorada.

## 8. Fase 6 — Harmonizar a documentação

Atualizar:

### `relatorio_auditoria.md`

- Registar cada problema identificado.
- Distinguir problemas confirmados, corrigidos, parcialmente resolvidos e pendentes.
- Associar cada correção à respetiva evidência ou teste.
- Atualizar as contagens apenas depois da regeneração dos dados.
- Não declarar reprodutibilidade sem execução limpa bem-sucedida.

### `README.md`

- Explicar o objetivo do projeto.
- Distinguir a tarefa de classificação da tarefa de regressão.
- Explicar os datasets, a origem dos dados e o processo de preparação.
- Documentar a definição operacional do alvo e as suas limitações.
- Apresentar instruções de execução reproduzíveis.

### `checklist_projeto.md`

- Alinhar o alvo de regressão com a implementação efetivamente escolhida.
- Remover instruções obsoletas ou contraditórias.
- Não marcar tarefas como concluídas sem evidência.

### `notas_data_preparation.md`

- Documentar normalização de IDs, patologias, datas, deduplicação e exclusões.
- Registar critérios de elegibilidade e razões para os mesmos.
- Explicar diferenças entre os datasets.

### Notebook de regressão

- Atualizar comentários, gráficos, métricas e conclusões.
- Remover outputs desatualizados.
- Registar a seed, o split, os preditores, o método de imputação e a avaliação usada.

## 9. Fase 7 — Reprodutibilidade final

Executar o pipeline completo num ambiente limpo ou numa sequência controlada equivalente.

1. Verificar as dependências e instruções de execução.
2. Executar a preparação dos dados desde o início.
3. Executar o notebook de validação.
4. Executar o notebook de regressão.
5. Regenerar todos os artefactos produzidos pelo pipeline.
6. Comparar os artefactos gerados com os ficheiros versionados.
7. Verificar que não existem dependências de outputs antigos.
8. Executar todos os testes automáticos.
9. Rever o diff do Git e confirmar que não foram alterados ficheiros fora do âmbito sem justificação.
10. Atualizar o relatório de auditoria com os resultados efetivos.

Se a execução falhar por falta de ficheiros, dependências ou acesso a dados, não declarar sucesso. Documentar o bloqueio e indicar exatamente o que falta.

## 10. Critérios de aceitação

O projeto só pode ser classificado como **consolidado** quando:

- O código e os datasets gerados cumprem os mesmos critérios de elegibilidade.
- As patologias e etiquetas foram reconciliadas com as fontes.
- Os testes de validação cobrem estrutura, tempo, alvo e fuga de informação.
- A regressão foi reexecutada com os dados corrigidos.
- O baseline foi comparado com os modelos de forma reproduzível.
- O tratamento de valores em falta não confunde ausência com zero.
- Os documentos descrevem o estado real do projeto.
- A execução limpa e os testes terminam com sucesso.

Se subsistirem limitações clínicas ou de cobertura temporal, classificar o projeto como **consolidado com limitações documentadas**, desde que não existam inconsistências técnicas por resolver.

Se existirem divergências entre código e artefactos, falhas de testes ou resultados não reproduzíveis, classificar como **não consolidado**.

## 11. Relatório final obrigatório

No fim, apresentar:

1. Resumo executivo.
2. Ficheiros alterados.
3. Problemas corrigidos, com evidência.
4. Testes executados e respetivos resultados.
5. Número real de episódios em cada etapa.
6. Distribuição real das patologias após regeneração.
7. Métricas atualizadas da regressão.
8. Comparação com o baseline.
9. Limitações metodológicas que permanecem.
10. Problemas pendentes e respetivos motivos.
11. Instruções exatas para reproduzir os resultados.
12. Estado final: consolidado, consolidado com limitações ou não consolidado.

Não declarar tarefas concluídas sem verificar o respetivo resultado. Não fazer commit nem push sem autorização explícita.
