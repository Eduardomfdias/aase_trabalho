# AASE — Análise de Sinais e Episódios Clínicos

Repositório do Projeto 1 da disciplina **Aprendizagem Automática em Sistemas Empresariais** (Mestrado EGSI), época 2026/27.  
Metodologia: **CRISP-DM** · Dataset: Neonatal Vital Signs and Clinical Conditions

---

## Estrutura do repositório

```
aase_trabalho/
├── 01_Business_Understanding/
│   ├── relatorio1.md                         ← relatório entregue ✅
│   └── checklist_bu.md
├── 02_data_understanding/
│   └── eda_aase.ipynb                        ← EDA completo (§1–§9) ✅
├── 03_data_preparation/
│   ├── data_preparation.ipynb                ← pipeline de preparação ✅
│   ├── validacao_data_preparation.ipynb      ← testes de validação ✅
│   ├── notas_data_preparation.md             ← decisões documentadas
│   ├── dataset_final.csv                     ← 47 episódios, agregado completo
│   ├── dataset_regressao_24h.csv             ← 43 episódios, preditores 24h + alvo futuro
│   ├── train.csv / test.csv                  ← split para classificação (32/7)
│   └── normalisation_params.csv             ← parâmetros z-score do treino
├── 04_modeling/
│   ├── regressao_carga_dessaturacao.ipynb    ← regressão ✅
│   ├── classificacao_patologia.ipynb         ← classificação (em curso)
│   └── predicoes_teste.csv                  ← previsões Ridge/OLS no conjunto de teste
├── dados_aase_202627/                        ← datasets originais (não versionar)
│   ├── 1_sinais_vitais_por_hora-1.csv        ← ~9 857 registos horários
│   └── 3_patologias_por_dia-1.csv            ← 696 registos de patologias
├── checklist_projeto.md                      ← estado de todas as entregas
└── enunciado.md
```

---

## Dados originais

### `1_sinais_vitais_por_hora-1.csv`

Registos horários de monitorização por episódio de internamento.

| Campo | Descrição |
|---|---|
| `episodio` | Identificador do episódio (ex: `EP001`) |
| `data` | Data do registo |
| `hora` | Hora do registo (0–23) |
| `sat_o2` | Saturação de oxigénio — SpO₂ (%) |
| `puls_rate` | Frequência de pulso (bpm) |
| `perfusion` | Índice de perfusão |

- **9 857 registos brutos** · **58 episódios** · período: janeiro–abril 2024
- Válidos após limpeza: **9 615** (97,5%) · excluídos: 242 (valores fora dos limites fisiológicos)

### `3_patologias_por_dia-1.csv`

Patologias registadas por episódio e por dia de internamento.

| Campo | Descrição |
|---|---|
| `episodio` | Identificador do episódio |
| `data` | Data do registo |
| `patologia` | Diagnóstico/patologia registada |

- **696 registos** · **14 patologias distintas** após normalização

---

## Objetivos de Data Mining

| Abordagem | Alvo | Dataset |
|---|---|---|
| **Regressão** | Carga de dessaturação futura — Σ(90−SpO₂) para SpO₂<90% após as primeiras 24h | `dataset_regressao_24h.csv` |
| **Classificação** | Patologia predominante (14 classes) | `dataset_final.csv` + `train/test.csv` |
| **Clustering** | Perfil fisiológico por episódio | `dataset_final.csv` |

---

## Como executar

**Pré-requisitos:** Python 3.x, `matplotlib`, `numpy`

**Sequência obrigatória:**

```bash
# 1. EDA (leitura apenas — não gera ficheiros)
jupyter notebook 02_data_understanding/eda_aase.ipynb

# 2. Preparação (gera todos os datasets em 03_data_preparation/)
jupyter notebook 03_data_preparation/data_preparation.ipynb

# 3. Validação da preparação
jupyter notebook 03_data_preparation/validacao_data_preparation.ipynb

# 4. Modelação — regressão
jupyter notebook 04_modeling/regressao_carga_dessaturacao.ipynb

# 5. Modelação — classificação
jupyter notebook 04_modeling/classificacao_patologia.ipynb
```

> Os ficheiros em `dados_aase_202627/` são **apenas de leitura** e nunca devem ser alterados.

---

## Notas

- Os identificadores de episódios (`EP001`…`EP058`) são pseudonimizados.
- IDs com variantes (`EP 016`, `ep016`) são normalizados em memória durante a preparação.
- Limiares de validade: SpO₂ ∈ [50,100], FC ∈ [50,350], Perfusão ∈ [0,20].
- Âncora temporal da janela 24h: primeiro registo válido do episódio (não a hora de admissão clínica — limitação documentada).
