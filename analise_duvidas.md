Analisei o código atual do repositório e os ficheiros CSV originais. A alteração deve ser um pouco mais profunda do que criar um modelo de regressão: é necessário preparar uma série temporal por episódio, definir o alvo futuro e construir preditores exclusivamente a partir das primeiras 24 horas.

O notebook atual agrega os sinais vitais de todo o episódio numa única linha. Por isso, as estatísticas atuais de SpO₂, frequência cardíaca e perfusão não podem ser reutilizadas diretamente como preditores para uma previsão feita às 24 horas.

## 1. O que os dados permitem concluir até agora

A inspeção de `1_sinais_vitais_por_hora-1.csv` revelou questões que devem ser tratadas antes de escolher definitivamente a fórmula da carga.

| Verificação                                             | Resultado observado |
| ------------------------------------------------------- | ------------------- |
| Registos de sinais vitais                               | 9 857               |
| Episódios identificados antes da normalização           | 58                  |
| Episódios após normalização dos IDs                     | 47                  |
| Registos com hora fora do intervalo 0–23                | 8                   |
| Datas com pelo menos um formato inconsistente           | Sim                 |
| Datas que não são interpretadas pela análise preliminar | 1 (`2024-02-31`)    |
| Timestamps repetidos após normalizar os IDs             | 60                  |

A coluna `data` contém sobretudo datas no formato `AAAA-MM-DD`, mas também valores com barras e pelo menos um formato como `2024-13-02`. Além disso, existem registos duplicados para o mesmo episódio e hora.

Isto significa que não devemos assumir que cada episódio tem 24 observações válidas e consecutivas nas primeiras 24 horas, nem interpretar automaticamente a contagem de registos abaixo de 90% como uma duração exata em horas.

A análise acima é uma verificação preliminar dos dados originais. Os números definitivos de episódios elegíveis para modelação só devem ser fixados depois de corrigir a interpretação das datas, resolver os timestamps duplicados e aplicar critérios explícitos de cobertura temporal.

## 2. Alterações concretas por ficheiro

### A. `03_data_preparation/data_preparation.ipynb`

[Abrir o notebook de preparação atual](https://github.com/Eduardomfdias/aase_trabalho/blob/main/03_data_preparation/data_preparation.ipynb?utm_source=chatgpt.com)

Este notebook deve continuar responsável pela limpeza e preparação geral, mas precisa de passar a produzir também um dataset específico para a previsão antecipada.

Alteração 1 — Normalizar e validar os timestamps.

Adicionar uma secção após a leitura dos dados originais, antes da filtragem e agregação:

```
import pandas as pd    return pd.NaTsv = pd.DataFrame(sv_raw).copy()sv["episodio"] = (    sv["episodio"].astype(str)    .str.strip().str.replace(" ", "", regex=False)    .str.upper())sv["data_parsed"] = sv["data"].map(parse_data)sv["hora_num"] = pd.to_numeric(sv["hora"], errors="coerce")sv["timestamp"] = (    sv["data_parsed"]    + pd.to_timedelta(sv["hora_num"], unit="h"))print("Datas inválidas:", sv["data_parsed"].isna().sum())print("Horas inválidas:",      (~sv["hora_num"].between(0, 23)).sum())print("Timestamps inválidos:", sv["timestamp"].isna().sum())duplicados = sv.duplicated(    ["episodio", "timestamp"], keep=False)print("Registos com timestamp duplicado:", duplicados.sum())
```

Esta secção deve gerar uma tabela de auditoria com os problemas encontrados, em vez de os corrigir silenciosamente. A interpretação de `2024-13-02` acima é uma regra provisória baseada no padrão observado e deve ser confirmada com a fonte dos dados.

Alteração 2 — Resolver os timestamps repetidos.

Depois da auditoria, os registos com o mesmo episódio e timestamp devem ser consolidados ou corrigidos na origem. Se não for possível recuperar a origem, uma opção é usar a mediana das medições duplicadas, documentando essa decisão.

Não se deve eliminar duplicados arbitrariamente nem deixar que várias observações da mesma hora contribuam repetidamente para a carga.

Alteração 3 — Separar a limpeza de SpO₂ da limpeza das outras variáveis.

O código atual exclui um registo se qualquer um dos três sinais vitais estiver inválido. Para calcular a carga de dessaturação, a validade da SpO₂ deve ser avaliada separadamente: uma SpO₂ válida não deve desaparecer do cálculo apenas porque a frequência cardíaca está em falta.

Alteração 4 — Criar um dataset próprio para a regressão antecipada.

Manter `dataset_final.csv` para a análise geral e acrescentar:

`03_data_preparation/dataset_regressao_24h.csv`

Este novo dataset deve ter uma linha por episódio elegível, com:

- identificador do episódio;
- estatísticas dos sinais vitais nas primeiras 24 horas;
- cobertura temporal e número de observações nessa janela;
- carga observada nas primeiras 24 horas, se for definida como uma variável útil;
- carga de dessaturação posterior às primeiras 24 horas, depois de acordada a definição do alvo;
- indicadores de qualidade e elegibilidade, quando necessários para auditoria.

O alvo deste dataset deve ser claramente identificado. Para previsão verdadeiramente antecipada, recomendo usar a carga posterior às primeiras 24 horas, e não a carga total que inclui o período já observado.

### B. Definir e auditar a carga antes de a calcular

O relatório de negócio fala em horas abaixo de 90% de SpO₂, mas o código atual calcula:

```
sum(90 - v for v in desat)
```

Isto é uma soma de défices de saturação por observação; não é automaticamente o número de horas em dessaturação.

Antes de fixar a definição, acrescentar uma secção de auditoria que responda a estas perguntas:

1. Quantos episódios têm datas e horas válidas?
2. Quantos têm observações repetidas no mesmo timestamp?
3. Quantas observações existem em cada janela inicial de 24 horas?
4. Existem lacunas temporais longas?
5. Quantos episódios têm dados suficientes tanto na janela inicial como no período posterior?
6. A frequência dos registos permite estimar duração abaixo de 90% ou apenas uma carga baseada nas observações?

A regra de elegibilidade deve ser definida e documentada. Por exemplo, exigir uma cobertura mínima da janela inicial e um número mínimo de observações futuras. O limiar exato deve ser decidido com base na distribuição real da cobertura, e não escolhido arbitrariamente.

Até esta auditoria estar concluída, a definição final do alvo deve permanecer pendente.

### C. `03_data_preparation/validacao_data_preparation.ipynb`

[Abrir o notebook de validação atual](https://github.com/Eduardomfdias/aase_trabalho/blob/main/03_data_preparation/validacao_data_preparation.ipynb?utm_source=chatgpt.com)

Adicionar testes específicos para o cenário de regressão:

- ausência de colunas duplicadas;
- timestamps válidos e ordenáveis;
- contagem de duplicados antes e depois da consolidação;
- confirmação de que todos os preditores vêm da janela inicial;
- confirmação de que o alvo é calculado apenas com o período posterior;
- verificação de que nenhum episódio inelegível entra no dataset de modelação;
- ausência de valores impossíveis ou não finitos no alvo;
- confirmação de que a mesma janela temporal é aplicada a todos os episódios.

Corrigir também a inconsistência existente: o notebook de validação espera `sinais_vitais_limpo.csv` e `patologias_limpo.csv`, mas o notebook de preparação atual não os produz de forma explícita. Os dois notebooks devem usar os mesmos nomes, caminhos e regras de transformação.

## 3. Criar o notebook de modelação

Criar `04_modeling/regressao_carga_dessaturacao.ipynb`.

Estrutura proposta

1\. Dados e elegibilidade

Ler `dataset_regressao_24h.csv`, verificar a unidade do alvo e apresentar o número de episódios incluídos e excluídos.

2\. Seleção de preditores

Usar apenas variáveis calculadas nas primeiras 24 horas. Excluir o alvo futuro, as variáveis de carga calculadas sobre o episódio completo e as estatísticas globais do episódio.

3\. Modelos

Começar com uma previsão pela mediana do treino como referência e comparar com regressão linear e Ridge.

4\. Avaliação

Calcular MAE, RMSE e \\(R^2\\), guardar as previsões por episódio e comparar todos os modelos com a referência.

5\. Interpretação clínica

Analisar os erros, a incerteza, a cobertura temporal e as limitações de generalização. Não apresentar os resultados como validação clínica.

### Código-base para impedir fuga de informação

Depois de o dataset de regressão estar construído e o nome do alvo confirmado, a seleção de variáveis pode ser explícita:

```
TARGET = "carga_dessaturacao_futura"EXCLUIR = {    "episodio",    TARGET,    "carga_dessaturacao",  # carga do episódio completo    "desat_count",         # se calculado no episódio completo    "desat_pct",           # se calculado no episódio completo    "duracao_dias",        # calculada com o episódio completo    "pat_predominante",    "pat_label",}FEATURE_COLS = [    c for c in df.columns    if c not in EXCLUIR    and not c.endswith("_total")]X = df[FEATURE_COLS]y = df[TARGET]assert TARGET not in FEATURE_COLSassert "carga_dessaturacao" not in FEATURE_COLSassert df["episodio"].is_unique
```

Esta é uma base ilustrativa: os nomes finais devem corresponder às colunas efetivamente produzidas. O teste `endswith("_total")` não substitui uma lista de preditores autorizados; para maior segurança, a implementação final deve preferir uma lista explícita de variáveis calculadas na janela inicial.

Para uma amostra tão pequena, começaria com validação cruzada ao nível do episódio, comparando com a mediana calculada exclusivamente em cada conjunto de treino. O `R²` deve ser interpretado com cautela; o MAE será geralmente mais fácil de explicar aos profissionais de saúde, desde que a unidade do alvo esteja definida.

## 4. Corrigir as colunas e os ficheiros de saída

No notebook de preparação, corrigir a sobreposição atual entre `FEATURE_COLS`, `BASE_COLS` e `TARGET_COLS`. Em particular, `n_registos` e `carga_dessaturacao` não devem aparecer duplicadas no cabeçalho dos CSVs.

Também recomendo que os ficheiros `train.csv` e `test.csv` existentes não sejam utilizados automaticamente na regressão: foram criados no contexto de classificação e estratificação por patologia. A regressão deve ter uma divisão própria, baseada nos episódios elegíveis para previsão temporal.

Os episódios sem patologia identificada podem participar na regressão, desde que tenham dados temporais válidos e um alvo calculável. A patologia não deve ser um critério de exclusão nem um preditor se não estiver disponível no momento da previsão.

## 5. Atualizar a documentação

No ficheiro `03_data_preparation/notas_data_preparation.md`, substituir a questão em aberto sobre o alvo por uma secção que documente:

- o momento da previsão: após as primeiras 24 horas;
- a definição operacional aprovada para a carga;
- as regras de parsing e consolidação dos timestamps;
- o critério de cobertura mínima;
- a definição do alvo futuro;
- os preditores permitidos e as exclusões por fuga de informação;
- o número final de episódios elegíveis, calculado após a auditoria.

Atualizar também o relatório de Data Understanding para registar os problemas temporais encontrados e o relatório de Data Preparation para explicar o novo dataset de regressão. O `README.md` deverá indicar como executar a preparação e a modelação.

## Ordem recomendada para implementar

1. Auditar e corrigir as datas, horas e timestamps duplicados.
2. Produzir uma tabela de cobertura temporal por episódio.
3. Decidir a definição de carga compatível com a resolução real dos dados.
4. Criar o dataset com preditores das primeiras 24 horas e alvo futuro.
5. Validar automaticamente a ausência de fuga de informação.
6. Criar o notebook de regressão e avaliar os modelos.
7. Atualizar a documentação com os resultados reais.

A decisão técnica mais importante é não treinar já sobre `dataset_final.csv` tal como está. Esse ficheiro contém estatísticas de todo o episódio, pelo que não representa o cenário de previsão antecipada. O novo dataset deve ser produzido a partir dos registos temporais e só depois usado para treinar o modelo.

Estas são as alterações concretas recomendadas; ainda não alterei ficheiros no GitHub.
