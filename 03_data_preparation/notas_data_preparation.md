# Notas — Data Preparation

## Momento da previsão

O alvo de regressão é calculado para **previsão antecipada**: com base nas primeiras 24 horas de internamento, prevemos a carga de dessaturação **posterior** a esse período.

## Definição operacional da carga

**Carga de dessaturação**: Σ(90 − SpO₂) para todos os registos com SpO₂ < 90%.

Esta fórmula mede a área de défice de saturação por observação (não diretamente o número de horas). Reflete a intensidade acumulada das dessaturações observadas no conjunto de registos analisado.

> ⚠️ A unidade depende da resolução dos registos (tipicamente 1/hora). Deve ser confirmada com a equipa clínica antes de comunicar resultados.

## Regras de parsing dos timestamps

- `DD/MM/YYYY` → `date(YYYY, MM, DD)`
- `YYYY-MM-DD` → padrão ISO
- `YYYY-MM-DD` com mês > 12 (ex.: `2024-13-02`) → interpretado como `YYYY-DD-MM` (2024-02-13)

Registos com timestamps inválidos (1 data não interpretável + 8 horas fora de [0,23]) são excluídos da janela temporal mas mantidos para as estatísticas agregadas do episódio.

## Resolução de timestamps duplicados

60 grupos `(episódio, data, hora)` tinham dois registos cada. Consolidados pela **mediana** de cada sinal vital. Decisão: a mediana é robusta a leituras espúrias e evita duplicar horas na janela temporal.

## SpO₂: limpeza separada

Para o cálculo da carga de dessaturação, apenas se exige que a **SpO₂ seja válida** [50,100]. Registos com FC ou perfusão inválidas mas SpO₂ válida contribuem para `desat_count`, `desat_pct` e `carga_desat_janela`.

Para as estatísticas de FC e perfusão, exige-se que todos os três sinais sejam válidos.

## Critério de elegibilidade (regressão 24h)

Um episódio é elegível para `dataset_regressao_24h.csv` se:
1. Tem **≥ 5 registos** com SpO₂ válida na janela inicial (primeiras 24 horas)
2. Tem **≥ 3 registos** com SpO₂ válida após as primeiras 24 horas (para calcular o alvo)

Limiar anterior (≥1) foi considerado demasiado permissivo: EP018 e EP042 tinham apenas 1 registo na janela inicial, insuficiente para caracterizar o estado fisiológico. O novo limiar exclui estes episódios.

## Preditores permitidos

Todos os preditores em `dataset_regressao_24h.csv` são calculados **exclusivamente** na janela das primeiras 24 horas:

| Coluna | Descrição |
|---|---|
| `n_registos_janela` | Nº total de registos na janela |
| `n_spo2_validos` | Nº de registos com SpO₂ válida |
| `n_all_validos` | Nº de registos com todos os sinais válidos |
| `sat_o2_{mean,std,min,max}` | Estatísticas de SpO₂ na janela |
| `puls_rate_{mean,std,min,max}` | Estatísticas de FC na janela |
| `perfusion_{mean,std,min,max}` | Estatísticas de perfusão na janela |
| `desat_count`, `desat_pct` | Nº e % de registos com SpO₂ < 90% na janela |
| `carga_desat_janela` | Carga de dessaturação **na janela** (não é o alvo) |

## Exclusões por fuga de informação

As seguintes colunas **não são usadas como preditores** no modelo de regressão:

- `episodio` — identificador
- `carga_dessaturacao_futura` — alvo
- `n_registos_futuro` — informação do período futuro
- `carga_dessaturacao` — carga total do episódio (não existe no dataset 24h)
- `duracao_dias`, `pat_predominante`, `pat_label` — calculados com o episódio completo

## Episódios elegíveis

Após auditoria e limpeza:
- Episódios com registos temporais válidos: 47
- Episódios elegíveis para regressão (janela 24h + dados futuros, critério ≥5/≥3): **≤43** (recalcular após execução)
- Episódios inelegíveis (sem cobertura suficiente): ≥4 (EP010, EP024, EP029, EP030 + EP018, EP042)

> Nota: EP018 e EP042 passavam o critério anterior (≥1 registo) mas são excluídos pelo novo critério (≥5 registos iniciais).

## Limitações e decisões metodológicas

### Âncora temporal
- t₀ = primeiro timestamp válido do episódio (não a hora de admissão clínica)
- A hora de admissão não está disponível nos dados
- Esta limitação deve constar no relatório de Data Understanding

### Variável-alvo: carga de dessaturação
- Fórmula: Σ(90 − SpO₂) para cada registo com SpO₂ < 90%, na janela futura
- Unidade: índice acumulado de défice de saturação (adimensional)
- Limitação: sensível à frequência de registo — episódios com mais observações acumulam mais carga mesmo com dessaturações menos severas
- Esta limitação deve ser assumida explicitamente no relatório de Modeling

## Ficheiros produzidos

| Ficheiro | Linhas | Descrição |
|---|---|---|
| `dataset_final.csv` | 47 | Agregado completo por episódio (para classificação/clustering) |
| `dataset_regressao_24h.csv` | ≤43 | Preditores 24h + alvo futuro (regressão); recalcular após novo critério |
| `train.csv` / `test.csv` | 32 / 7 | Split estratificado para classificação |
| `sinais_vitais_limpo.csv` | 9 857 | IDs normalizados, todos os registos |
| `patologias_limpo.csv` | 696 | IDs normalizados |
| `normalisation_params.csv` | 14 | Parâmetros z-score do conjunto de treino |
