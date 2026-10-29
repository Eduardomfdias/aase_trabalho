# Relatório de Auditoria — AASE 2026/27

**Data:** 2026-10-29 (actualizado após regeneração)
**Metodologia:** CRISP-DM
**Âmbito:** Auditoria completa conforme plano em `analise_duvidas.md` (7 fases)

---

## Tabela de discrepâncias

| # | Ficheiro | Problema | Evidência | Impacto | Correcção | Estado |
|---|---|---|---|---|---|---|
| 1 | `dataset_regressao_24h.csv` | 43 episódios em vez de 40 — EP018, EP028, EP042 violam o critério ≥5/≥3 | EP018: n_spo2_janela=1; EP028: n_futuro=2; EP042: n_spo2_janela=1 | Modelos treinados com dados inválidos | Regenerado com critério correcto → 40 episódios | ✅ Corrigido |
| 2 | `predicoes_teste.csv` | Previsões calculadas sobre dataset com 43 episódios (desactualizadas) | Ficheiro referencia EP018/EP028/EP042 como possíveis candidatos de treino | Métricas irreproduziveis | Regenerado a partir do dataset de 40 episódios | ✅ Corrigido |
| 3 | `predicoes_teste.csv` | Imputação de valores em falta por 0.0 (`get_X`) confunde ausência com valor clínico real | `get_X()` no notebook de regressão usava `0.0` como fallback | Bias nos preditores com valores em falta | Imputação substituída por média do conjunto de treino | ✅ Corrigido |
| 4 | `validacao_data_preparation.ipynb` | Testes apenas verificavam `n_registos > 0`, não os limiares ≥5/≥3 | Célula 20: `if n_registos_futuro == 0` em vez de `< 3` | EP018/EP028/EP042 passavam validação | Testes actualizados com limiares correctos + testes de fronteira (TC1–TC7) | ✅ Corrigido |
| 5 | `README.md` | "43 episódios" no campo `dataset_regressao_24h.csv` | Linha da estrutura do repositório | Documentação incorrecta | Actualizado para 40 | ✅ Corrigido |
| 6 | `notas_data_preparation.md` | Contagem "≤43" e "≥4 inelegíveis" desactualizadas | Secção "Episódios elegíveis" | Documentação incorrecta | Actualizado: 40 elegíveis, 7 inelegíveis com tabela completa | ✅ Corrigido |
| 7 | `relatorio_auditoria.md` (anterior) | Métricas da regressão calculadas sobre 43 episódios (desactualizadas) | Tabela do Ponto 5 | Métricas irreproduziveis com o código actual | Substituído por resultados da execução com 40 episódios | ✅ Corrigido |
| 8 | Fuga de informação (desat_count, desat_pct) | Excluídos de FEATURE_COLS no notebook de regressão — verificado OK | `EXCLUIR = {..., "desat_count", "desat_pct", ...}` | Sem impacto — já estava correcto | Nenhuma | ✅ OK |
| 9 | `README.md` | "58 episódios" no campo de IDs — valor antes da normalização | Secção Dados | Confusão entre IDs brutos e normalizados | Corrigido: 47 após normalização; os 58 são IDs distintos antes da normalização | ✅ OK (já estava correcto no README actual) |
| 10 | `metadata.csv` — divergência Displasia Broncopulmonar | Displasia Broncopulmonar aparece 38× nos dados brutos mas nunca como patologia predominante | EP001: Refluxo Gastroesofágico (26×) > Displasia Broncopulmonar (25×) | Não há divergência real: a patologia predominante é determinada por contagem | Nenhuma — comportamento correcto | ✅ OK |

---

## Fase 1 — Inventário e auditoria do estado actual

### 1.1 Episódios

| Fonte | Episódios únicos (brutos) | Após normalização de IDs |
|---|---|---|
| `1_sinais_vitais_por_hora-1.csv` | 58 (inclui variantes: `EP 016`, `ep016`, ` EP011`) | 47 |
| `3_patologias_por_dia-1.csv` | 45 (inclui variantes: `EP009`, ` EP020`, `ep029`) | 39 |
| `dataset_final.csv` (gerado) | — | 47 (39 com patologia, 8 sem) |
| `dataset_regressao_24h.csv` (regenerado) | — | 40 elegíveis |

### 1.2 Registos

| Dado | Valor |
|---|---|
| Registos de sinais vitais (brutos) | 9 857 |
| Registos válidos após limpeza fisiológica | 9 615 (97,5%) |
| Registos inválidos excluídos | 242 |
| Grupos de timestamps duplicados | 60 |
| Registos após deduplicação | 9 797 |
| Registos de patologias | 696 |

### 1.3 Patologias

| Patologia | Episódios com predominância |
|---|---|
| Doença das Membranas Hialinas | 24 |
| Icterícia Neonatal | 7 |
| Citomegalovírus | 4 |
| Anemia | 2 |
| Refluxo Gastroesofágico | 1 |
| Persistência do Canal Arterial | 1 |
| **Total** | **39** |

8 episódios sem patologia registada (EP007, EP012, EP021, EP028, EP031, EP035, EP044, EP047).

A `Displasia Broncopulmonar` aparece 38× nos dados brutos mas **nunca** como patologia predominante de nenhum episódio (foi suplantada em todos os casos). Não existe divergência — é comportamento esperado da regra de predominância.

---

## Fase 2 — Preparação dos dados

### 2.1 Critérios de elegibilidade (dataset_regressao_24h.csv)

Critério implementado no código actual:
- ≥ 5 registos com SpO₂ válida na janela inicial (primeiras 24h)
- ≥ 3 registos com SpO₂ válida após as primeiras 24h

**7 episódios excluídos:**

| Episódio | SpO₂ janela | SpO₂ futuro | Motivo |
|---|---|---|---|
| EP010 | 18 | 0 | futuro insuficiente (0 < 3) |
| EP018 | 1 | 482 | janela insuficiente (1 < 5) |
| EP024 | 17 | 0 | futuro insuficiente (0 < 3) |
| EP028 | 23 | 2 | futuro insuficiente (2 < 3) |
| EP029 | 22 | 0 | futuro insuficiente (0 < 3) |
| EP030 | 4 | 0 | janela insuficiente (4 < 5) e futuro insuficiente (0 < 3) |
| EP042 | 1 | 172 | janela insuficiente (1 < 5) |

> **Nota:** EP018, EP028 e EP042 estavam presentes no ficheiro anterior (43 episódios) gerado com o critério ≥1, que é demasiado permissivo. Corrigido na regeneração.

### 2.2 Integridade temporal

- Timestamps parseados: datas no formato `DD/MM/YYYY`, `YYYY-MM-DD` e `YYYY-DD-MM` (mês > 12 → inversão automática, ex: `2024-13-02` → 2024-02-13).
- 60 grupos de timestamps duplicados consolidados por mediana.
- Janela não tem sobreposição com futuro: a divisão é `delta_h < 24` (janela) vs `delta_h >= 24` (futuro).

**Implicação de EP018:** O registo `2024-13-02` (hora 19, SpO₂ 94.18 válida) cria um único ponto na janela inicial. Os restantes 492 registos do episódio ficam no futuro (a partir de 2024-02-27, 14 dias depois). Correctamente excluído.

### 2.3 Definição do alvo

`carga_dessaturacao_futura = Σ(90 − SpO₂)` para registos futuros com SpO₂ válida e SpO₂ < 90%.

- Unidade: índice acumulado de défice de saturação por observação (não horas).
- **Limitação documentada:** sensível à frequência de registo — episódios com mais registos futuros têm mais oportunidade de acumular carga.
- 28/40 episódios têm carga futura = 0 (70%) — concentração de zeros condiciona a modelação.

---

## Fase 3 — Patologias e labels

A normalização está correcta e verificada:
- 14 patologias brutas distintas após normalização de texto.
- 6 patologias predominantes após aplicação da regra de máxima frequência.
- `metadata.csv` é consistente com `dataset_final.csv`.
- Bijactividade label ↔ nome: verificada (nenhuma label tem mais de um nome, nenhum nome tem mais de uma label).

---

## Fase 4 — Regressão

### 4.1 Dataset corrigido

| Parâmetro | Valor |
|---|---|
| Episódios elegíveis | 40 |
| Preditores | 16 (todos da janela inicial) |
| Alvo: mín | 0.00 |
| Alvo: máx | 85.57 |
| Alvo: média | 3.45 |
| Alvo: mediana | 0.00 |
| Episódios com alvo = 0 | 28/40 (70%) |

### 4.2 Imputação

Versão anterior: valores em falta imputados por `0.0` → confunde ausência de medição com valor clínico.
Versão actual: imputação pela **média do conjunto de treino** para cada coluna, calculada dentro do split (LOO: dentro de cada fold).

Nenhum valor em falta foi encontrado nos 40 episódios elegíveis — a imputação é preventiva.

### 4.3 Verificação de fuga de informação

| Coluna | Status |
|---|---|
| `carga_dessaturacao_futura` | Alvo — excluído dos preditores ✅ |
| `n_registos_futuro` | Futuro — excluído dos preditores ✅ |
| `desat_count`, `desat_pct` | Excluídos (tinham sido calculados para dataset_final, não existem no dataset 24h com esse nome exacto — o equivalente `carga_desat_janela` é da janela inicial) ✅ |
| `carga_desat_janela` | Janela inicial — permitido ✅ |

### 4.4 Métricas — Split 80/20 (treino=32, teste=8)

| Modelo | MAE treino | RMSE treino | R² treino | MAE teste | RMSE teste | R² teste |
|---|---|---|---|---|---|---|
| Mediana (base) | 4.171 | 15.926 | −0.074 | 0.574 | 1.075 | −0.398 |
| Reg. Linear | 5.603 | 11.509 | 0.439 | 7.014 | 15.624 | −294.053 |
| Ridge (λ=10.0) | 6.198 | 14.373 | 0.126 | 3.358 | 4.594 | −24.504 |

### 4.5 Métricas — Leave-One-Out CV (n=40)

| Modelo | MAE LOO | RMSE LOO | R² LOO |
|---|---|---|---|
| Mediana (base) | 3.451 | 14.253 | −0.062 |
| Reg. Linear | 8.601 | 16.826 | −0.481 |
| Ridge (λ=10.0) | 6.097 | 14.251 | −0.062 |

**Interpretação:** O baseline (mediana do treino) supera ou iguala os modelos treinados em MAE e RMSE (LOO). O R² é negativo em todos os modelos incluindo o baseline, o que indica que a variância do alvo é dominada por 28/40 zeros — qualquer predição fixa perto de zero é quase óptima para a maioria dos casos. A utilidade preditiva **não foi demonstrada**. Conclusão correcta para o relatório: os dados disponíveis não suportam generalização com os modelos testados.

---

## Fase 5 — Notebook de validação

Testes adicionados à célula 20:

| Teste | Verifica | Resultado |
|---|---|---|
| TC1 | 5 janela + 3 futuro → elegível | ✅ |
| TC2 | 4 janela + 3 futuro → inelegível | ✅ |
| TC3 | 5 janela + 2 futuro → inelegível | ✅ |
| TC4 | SpO₂ = 90% não conta para carga | ✅ |
| TC5 | SpO₂ = 85% → carga = 5.0 | ✅ |
| TC6 | Sem dessaturação futura → alvo = 0 | ✅ |
| TC7 | SpO₂ = 250 (inválida) excluída da contagem | ✅ |
| Limiar janela ≥ 5 | Todos os 40 episódios verificados | ✅ |
| Limiar futuro ≥ 3 | Todos os 40 episódios verificados | ✅ |
| Alvo não-negativo | [0.00, 85.57] | ✅ |
| Alvo fora dos preditores | Verificado | ✅ |
| n_registos_futuro excluído | Verificado | ✅ |
| Sem variáveis globais do episódio | Verificado | ✅ |

---

## Fase 6 — Documentação harmonizada

| Ficheiro | Alterações |
|---|---|
| `notas_data_preparation.md` | Contagens actualizadas (40 elegíveis, 7 inelegíveis com tabela); nota sobre versão anterior |
| `README.md` | "43 episódios" → "40 episódios" no campo dataset_regressao_24h.csv |
| `relatorio_auditoria.md` | Substituição completa com resultados reais |

---

## Fase 7 — Reprodutibilidade

**Pipeline executado nesta sessão (equivalente à execução dos notebooks):**

1. Dados brutos lidos sem alteração (9 857 + 696 registos) ✅
2. IDs normalizados em memória: 58 variantes → 47 episódios únicos ✅
3. Timestamps parsed e deduplicados: 9 857 → 9 797 ✅
4. Limpeza fisiológica: 9 797 → 9 615 válidos ✅
5. `dataset_final.csv` gerado: 47 episódios, 20 colunas ✅ (sem alterações face à versão versionada)
6. `dataset_regressao_24h.csv` regenerado: 40 episódios (era 43) ✅
7. `predicoes_teste.csv` regenerado: 8 episódios (split 80/20) ✅
8. Todos os testes de validação passam ✅

**Nota sobre reprodutibilidade total:** A execução completa requer Jupyter + matplotlib + numpy. A sequência correcta é:
```
data_preparation.ipynb → validacao_data_preparation.ipynb → regressao_carga_dessaturacao.ipynb
```

---

## Decisão final de consolidação

> **Consolidado com limitações documentadas.**

**Correcções aplicadas nesta sessão:**
- `dataset_regressao_24h.csv` regenerado com critério correcto (40 episódios, não 43)
- Imputação de valores em falta corrigida (média do treino, não 0.0)
- LOO CV implementado para estimativa mais robusta
- Testes de validação reforçados com limiares e casos de fronteira
- Documentação actualizada

**Limitações que permanecem (não são inconsistências técnicas):**
1. O baseline supera os modelos em MAE (LOO). O projecto **não deve afirmar capacidade preditiva** — os resultados são exploratórios.
2. Concentração de 70% de zeros no alvo condiciona gravemente a modelação.
3. O alvo é sensível à frequência de registo (não normalizado pela cobertura temporal).
4. Âncora temporal = primeiro registo, não hora de admissão clínica (dados não disponíveis).
5. Amostra pequena (n=40 para regressão; n=39 para classificação com 6 classes desequilibradas).
6. LOO dá estimativas mais conservadoras que o split único: Ridge LOO MAE=6.097 vs baseline LOO MAE=3.451.
