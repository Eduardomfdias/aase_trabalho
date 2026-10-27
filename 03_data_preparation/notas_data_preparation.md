# Notas de Data Preparation — AASE 2026/27

Disciplina: Aprendizagem Automática em Sistemas Empresariais  
Fase CRISP-DM: **Data Preparation**

---

## O que foi feito e porquê

### Regra fundamental
Os ficheiros em `dados_aase_202627/` são **intocáveis**.  
Toda a limpeza e transformação produz ficheiros novos em `03_data_preparation/`.

---

## Passo 1 — Normalização de IDs de episódio

**Problema encontrado:** os dois datasets usam o mesmo campo `episodio` mas com formatação inconsistente:

| ID no ficheiro original | Forma correcta |
|---|---|
| `' EP011'` (espaço à esquerda) | `EP011` |
| `'EP 016'` (espaço no meio) | `EP016` |
| `'ep018'` (minúsculas) | `EP018` |

Impacto: sem correcção, os 58 "IDs únicos" do dataset de SV são inflados — vários são duplicados do mesmo episódio com formatação diferente.

**Solução:** `strip() + replace(' ', '') + upper()` aplicado em memória antes de qualquer processamento.

**Resultado:**

| Dataset | IDs únicos antes | IDs únicos depois |
|---|---|---|
| Sinais Vitais | 58 | 47 |
| Patologias | 45 | 39 |
| Em ambos | — | 39 |

IDs com espaços em SV: `EP011, EP016, EP018, EP019, EP023, EP026, EP027, EP034, EP036`  
IDs com espaços em Pat: `EP009, EP018, EP020, EP029, EP037`

**Ficheiros gerados:**

- `sinais_vitais_limpo.csv` — cópia de `1_sinais_vitais_por_hora-1.csv` com IDs normalizados
- `patologias_limpo.csv` — cópia de `3_patologias_por_dia-1.csv` com IDs normalizados

---

## Passo 2 — Exclusão de registos inválidos

**Estratégia escolhida: exclusão** (não imputação).

**Justificação:** valores fora dos limiares fisiológicos representam erros de sensor/registo — não estados clínicos reais. Imputar esses valores introduziria ruído artificial nos modelos.

| Campo | Limite válido | Excluídos |
|---|---|---|
| SpO₂ | [50, 100] % | 74 |
| Freq. Pulso | [50, 350] bpm | 91 |
| Perfusão | [0, 20] | 70 |
| Hora | [0, 23] | 8 |

Total excluído: **242 registos** (2,5% dos 9 857 brutos). Ficam **9 615 registos válidos**.

---

## Passo 3 — Agregação por episódio

Grão final: **1 linha = 1 episódio** (47 linhas no total).

Para cada episódio foram calculadas as seguintes features a partir dos registos válidos:

| Feature | Cálculo |
|---|---|
| `sat_o2_{mean,std,min,max}` | Estatísticas de SpO₂ sobre todos os registos do episódio |
| `puls_rate_{mean,std,min,max}` | Estatísticas de FC |
| `perfusion_{mean,std,min,max}` | Estatísticas de perfusão |
| `desat_count` | Nº de registos com SpO₂ < 90% |
| `desat_pct` | `desat_count / n_registos × 100` |
| `carga_dessaturacao` | `Σ(90 − SpO₂)` para SpO₂ < 90% |
| `duracao_dias` | Nº de dias distintos com registos |
| `n_registos` | Total de registos válidos do episódio |

---

## Passo 4 — Targets

### Classificação — `pat_predominante` / `pat_label`

Para cada episódio: a patologia com **mais registos dia×episódio** em `patologias_limpo.csv`.  
Em caso de empate usa-se a primeira por ordem alfabética (determinístico).

Distribuição de classes (após dedup de IDs):

| Label | Patologia | Episódios |
|---|---|---|
| 0 | Doença das Membranas Hialinas | 24 |
| 1 | Icterícia Neonatal | 7 |
| 2 | Citomegalovírus | 4 |
| 3 | Anemia | 2 |
| 4 | Displasia Broncopulmonar | 1 |
| 5 | Persistência do Canal Arterial | 1 |

**8 episódios sem patologia:** EP007, EP012, EP021, EP028, EP031, EP035, EP044, EP047.  
Estes ficam no `dataset_final.csv` com `pat_label = -1` mas são **excluídos do split** treino/teste.

### Regressão — dois candidatos (a confirmar com docente)

- `duracao_dias` — número de dias de internamento (enunciado original)
- `carga_dessaturacao` — carga acumulada de dessaturação (definido no relatório BU)

Ambos estão incluídos no `dataset_final.csv`.

---

## Passo 5 — Normalização Z-score

Transformação: `z = (x − μ) / σ`

**Importante:** os parâmetros (μ e σ) são calculados **apenas no conjunto de treino** para evitar data leakage. O mesmo escalonamento é depois aplicado ao teste.

Os parâmetros estão guardados em `normalisation_params.csv`.  
As colunas normalizadas têm sufixo `_z` em `train.csv` e `test.csv`.

---

## Passo 6 — Divisão treino/teste 80/20

Estratificação por `pat_label` para preservar a distribuição de classes.  
Episódios sem patologia não entram no split.

| Conjunto | Episódios |
|---|---|
| Treino | 32 |
| Teste | 7 |
| **Total** | **39** |

`SEED = 42` para reprodutibilidade.

---

## Ficheiros produzidos — para que serve cada um

| Ficheiro | Para que serve |
|---|---|
| `sinais_vitais_limpo.csv` | Cópia dos sinais vitais com IDs corrigidos (ficheiro intermédio) |
| `patologias_limpo.csv` | Cópia das patologias com IDs corrigidos (ficheiro intermédio) |
| `dataset_final.csv` | **Dataset principal** — 47 episódios, 20 colunas, features + targets |
| `train.csv` | Treino dos modelos — 32 episódios, features originais + `_z` |
| `test.csv` | Avaliação dos modelos — 7 episódios, mesmo formato do treino |
| `metadata.csv` | Tabela de consulta label ↔ nome da patologia |
| `normalisation_params.csv` | μ e σ do treino — necessários para normalizar dados novos na produção |

---

## Questões em aberto

1. **Alvo de regressão:** confirmar com docente se usar `duracao_dias` ou `carga_dessaturacao`.
2. **8 episódios sem patologia:** investigar se há dados de patologia noutras fontes.
3. **Desequilíbrio de classes:** DMH domina (24/39 = 62%). Avaliar se usar oversampling (SMOTE) ou pesos de classe na modelação.
