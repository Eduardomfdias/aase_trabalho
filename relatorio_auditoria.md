# Relatório de Auditoria — AASE 2026/27

**Data:** 2026-10-29  
**Metodologia:** CRISP-DM  
**Âmbito:** Revisão dos 6 pontos críticos da secção 15 do plano de auditoria (`analise_duvidas.md`)  
**Ficheiros auditados:**
- `03_data_preparation/data_preparation.ipynb`
- `04_modeling/regressao_carga_dessaturacao.ipynb`
- `03_data_preparation/train.csv` / `test.csv`
- `checklist_projeto.md` / `README.md`

---

## Ponto 1 — Definição da carga de dessaturação

**Achado:** A fórmula implementada no código é:

```python
# data_preparation.ipynb — § 3 (dataset_final.csv)
"carga_dessaturacao": round(sum(90 - v for v in desat), 4),
# onde: desat = [v for v in sat if v < 90]

# data_preparation.ipynb — § 7b (dataset_regressao_24h.csv)
carga_futura = round(
    sum(90 - r["sat_o2"] for r in futuro_rec if r["spo2_ok"] and r["sat_o2"] < 90),
    4
)
```

Esta fórmula calcula um **índice acumulado de défice de saturação** (soma dos desvios abaixo de 90%), não o número de horas com SpO₂ < 90%.

A fórmula é consistente em todos os notebooks e CSVs. O `README.md` descreve-a corretamente como "Σ(90−SpO₂) para SpO₂<90%". O `checklist_projeto.md` regista "carga de dessaturação futura" como alvo de regressão.

**Problema em aberto:** A unidade do alvo depende da frequência de registo — um episódio com 818 registos futuros tem inerentemente mais oportunidades de acumular défice do que um com 2 registos. A grandeza não está normalizada pela cobertura temporal. O próprio notebook de modelação nota: `⚠ Cobertura temporal heterogénea (janela 24h pode ter 1–24 registos por episódio)`.

**Veredicto:** ⚠️ Atenção — fórmula internamente consistente e documentada, mas a unidade é sensível à frequência de observação. Deve ser assumido explicitamente no relatório.

---

## Ponto 2 — Âncora temporal das primeiras 24h

**Achado:** O código define `t_start` como o primeiro timestamp válido do episódio:

```python
# data_preparation.ipynb — § 7b
t_start_date = records[0]["data_date"]
t_start_hora = records[0]["hora_num"]
# records está ordenado por (episodio, data_date, hora_num)
```

A janela inicial cobre `delta_h < 24`, ou seja, `[t_start, t_start + 24h[`. A janela futura cobre `delta_h >= 24`.

O `README.md` documenta explicitamente esta limitação:

> *"Âncora temporal da janela 24h: primeiro registo válido do episódio (não a hora de admissão clínica — limitação documentada)."*

A âncora é aplicada de forma consistente em todos os episódios. A diferença entre o primeiro registo e a admissão clínica real não é quantificada (não existe coluna de admissão nos dados).

**Veredicto:** ⚠️ Atenção — limitação reconhecida e documentada, mas não quantificada. A diferença pode variar entre episódios. Deve constar explicitamente no relatório de Data Understanding e de Modeling.

---

## Ponto 3 — Cobertura mínima

**Achado:** O critério de elegibilidade implementado é:

```python
# data_preparation.ipynb — § 7b
if n_janela == 0 or n_futuro == 0:
    continue  # episódio inelegível
# onde: n_janela = sum(1 for r in janela_rec if r["spo2_ok"])
#        n_futuro = sum(1 for r in futuro_rec if r["spo2_ok"])
```

Cobertura mínima = **1 registo SpO₂ válido** em cada janela. Não existe limiar para:
- número mínimo de registos na janela inicial,
- cobertura temporal mínima (horas cobertas),
- duração máxima de lacunas.

**Episódios com cobertura muito baixa aceites pelo critério:**

| Episódio | SpO₂ válidos (janela) | SpO₂ válidos (futuro) | Observação |
|----------|----------------------|----------------------|------------|
| EP018    | 1                    | 482                  | Uma única observação representa "as primeiras 24h" |
| EP042    | 1                    | 172                  | Idem |
| EP028    | 23                   | 2                    | Futuro com apenas 2 registos |
| EP033    | 24                   | 3                    | Futuro com apenas 3 registos |

Para EP018 e EP042, um único ponto nas primeiras 24h é insuficiente para representar o estado fisiológico inicial. Para EP028 e EP033, a carga futura é calculada sobre 2–3 registos, tornando o alvo instável.

**Veredicto:** ❌ Problema — o critério de 1 registo mínimo é demasiado permissivo. Os episódios EP018 e EP042 representam um risco metodológico real. Devem ser excluídos ou o critério deve ser justificado explicitamente.

---

## Ponto 4 — Dependência do alvo à frequência de registo

**Achado:** O alvo `carga_dessaturacao_futura` é uma soma direta. O número de registos futuros varia drasticamente entre episódios (ver tabela da célula dp0023):

| Mín. registos futuros | Máx. registos futuros |
|---|---|
| 2 (EP028) | 818 (EP026) |

Um episódio com 818 registos futuros e SpO₂ ligeiramente abaixo de 90% (ex: 89.5%) acumula `818 × 0.5 = 409` de carga, enquanto um episódio com 2 registos e SpO₂ fortemente abaixo de 90% (ex: 70%) acumula apenas `2 × 20 = 40`.

Os outputs do notebook de preparação confirmam:

```
Alvo — carga_dessaturacao_futura:
  mín=0.00  máx=85.57  média=3.21  mediana=0.00
  episódios com carga=0 (sem dessaturação futura): 30/43
```

30 de 43 episódios têm alvo = 0. A mediana é 0. O notebook não inclui análise da correlação entre `n_registos_futuro` e `carga_dessaturacao_futura`.

**Veredicto:** ❌ Problema — o alvo é influenciado pela oportunidade de observação. Episódios com mais registos têm mais oportunidade de acumular carga. Esta confusão não é abordada. A concentração de zeros (70%) condiciona gravemente a modelação.

---

## Ponto 5 — Validação do modelo (baseline vs modelos, métricas reais)

**Achado:** As métricas produzidas pelo notebook de modelação (célula reg0010):

| Modelo           | MAE treino | RMSE treino | R² treino | MAE teste | RMSE teste | R² teste      |
|-----------------|-----------|-------------|-----------|-----------|------------|---------------|
| Mediana (base)  | 4.055      | 15.460      | −0.074    | **0.034** | 0.078      | −0.246        |
| Reg. Linear     | 5.271      | 11.436      | 0.412     | 9.254     | 19.562     | **−79 316**   |
| Ridge (λ=10.0)  | 5.647      | 13.895      | 0.132     | 5.706     | 6.690      | **−9 274**    |

O baseline (predição da mediana do treino = 0 para a maioria) obtém **MAE=0.034 no teste**, enquanto Ridge obtém **MAE=5.706** e Linear **MAE=9.254**.

O R² de −79 316 (Linear) e −9 274 (Ridge) no teste indica colapso completo da capacidade de generalização. O conjunto de teste tem 9 episódios, dos quais 7 têm alvo = 0 (ver célula reg0013 — 7 erros negativos do Ridge, com previsões entre 3 e 11 para alvos zero).

A análise de erros por episódio (célula reg0013) mostra que o Ridge sistematicamente sobrestima para episódios com carga zero, nunca conseguindo prever os casos baixos com precisão.

Não existe validação cruzada LOO implementada — apenas um split único 80/20. O notebook sugere LOO como próximo passo mas não o implementa.

**Veredicto:** ❌ Problema grave — o baseline supera os modelos treinados em todas as métricas do teste. Os R² negativos massivos indicam que os modelos não generalizam. Isto resulta provavelmente da combinação de (a) 70% de zeros no alvo, (b) amostra muito pequena (n=34 treino, 16 preditores), e (c) possível correlação entre preditores e cobertura futura (ponto 4). Os resultados actuais não suportam qualquer conclusão sobre utilidade preditiva.

---

## Ponto 6 — Coerência documental

**Achado:** Verificação cruzada entre README, checklist, código e datasets:

| Elemento | README | checklist | Código | Veredicto |
|---|---|---|---|---|
| Alvo de regressão | "Σ(90−SpO₂) após 24h" ✅ | "carga de dessaturação futura" ✅ | `carga_dessaturacao_futura` ✅ | ✅ Coerente |
| λ Ridge | não mencionado | não mencionado | λ=10.0 ✅ | ✅ Sem divergência |
| n_registos_futuro excluído | não mencionado | não mencionado | `EXCLUIR = {..., "n_registos_futuro", ...}` ✅ | ✅ OK |
| Nº episódios total | "58 episódios" ❌ | "47 episódios" ✅ | 47 IDs únicos ✅ | ❌ README desatualizado |
| Patologias distintas | "14 patologias" | não mencionado | 6 classes em `metadata.csv` | ⚠️ Divergência (14 nos dados brutos, 6 após normalização/elegibilidade) |
| train/test produzidos por | classificacao_patologia.ipynb | idem | idem | ✅ Coerente |
| Âncora temporal | "primeiro registo válido — limitação" ✅ | não mencionado | confirmado no código ✅ | ✅ OK |

**Divergências encontradas:**
1. O README indica "58 episódios" mas o código encontra 47 IDs únicos após normalização. Esta discrepância não é explicada.
2. O README indica "14 patologias distintas" mas o `metadata.csv` contém 6 classes. As 14 patologias são do CLAUDE.md (valor da EDA), as 6 resultam do critério de patologia predominante após elegibilidade — a diferença não é explicada no README.

**Veredicto:** ⚠️ Atenção — duas inconsistências no README (nº de episódios, nº de patologias). O pipeline de modelação está internamente coerente. Os relatórios escritos ainda não existem.

---

## Tabela-resumo de consolidação

| Área | Ponto auditado | Veredicto | Prioridade |
|---|---|---|---|
| Definição do alvo | Fórmula Σ(90−SpO₂) — consistente mas sensível à frequência de observação | ⚠️ Atenção | Média |
| Âncora temporal | Primeiro registo válido, não admissão — documentado | ⚠️ Atenção | Baixa |
| Cobertura mínima | 1 registo aceite — EP018, EP042 com 1 único registo inicial | ❌ Problema | Alta |
| Dependência à frequência | 70% zeros; alvo não normalizado pela cobertura | ❌ Problema | Alta |
| Avaliação do modelo | Baseline supera ambos os modelos; R² negativos massivos | ❌ Problema grave | Alta |
| Coerência documental | README com "58 episódios" e "14 patologias" incorretos | ⚠️ Atenção | Baixa |

---

## Decisão final de consolidação

> **Consolidado com limitações — pipeline coerente e reproduzível, mas evidência preditiva não demonstrada.**

O pipeline de preparação é reproduzível, internamente consistente e bem estruturado. A separação temporal está correta — `n_registos_futuro` e variáveis do episódio completo são excluídos dos preditores; a normalização é calculada apenas no treino; a divisão é por episódio.

No entanto, os resultados de modelação não suportam conclusões sobre utilidade preditiva:

1. O baseline supera todos os modelos treinados no conjunto de teste — o projeto **não deve afirmar que os modelos têm capacidade preditiva**.
2. A concentração de 70% de zeros no alvo, combinada com uma amostra de 43 episódios e 16 preditores, é a causa provável do colapso dos modelos.
3. A dependência do alvo à frequência de observação pode ser um confundidor não investigado.
4. Dois episódios (EP018, EP042) têm cobertura inicial de 1 registo, o que compromete a qualidade do conjunto de preditores.

**Recomendações prioritárias antes da entrega:**

1. Excluir episódios com menos de 5 registos SpO₂ válidos na janela inicial (ou justificar explicitamente o limiar escolhido).
2. Produzir o gráfico `carga_dessaturacao_futura` vs `n_registos_futuro` para quantificar a dependência do alvo à cobertura.
3. Implementar LOO para estimar métricas mais robustas com a amostra disponível.
4. Corrigir no README: "47 episódios" e clarificar a relação entre as 14 patologias dos dados brutos e as 6 classes do modelo.
5. O relatório deve concluir que "a utilidade preditiva não foi demonstrada" — não que os modelos falham, mas que a amostra e a distribuição do alvo são insuficientes para o demonstrar.
