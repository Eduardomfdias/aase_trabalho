# AASE — Análise de Sinais e Episódios Clínicos

Repositório de dados clínicos referente à época **2026/27**, organizado para suporte à análise de episódios de internamento neonatal.

## Estrutura

```
aase_trabalho/
└── dados_aase_202627/
    ├── 1_sinais_vitais_por_hora-1.csv   # Registos horários de sinais vitais
    ├── 3_patologias_por_dia-1.csv       # Diagnósticos/patologias por episódio e dia
    └── Diretrizes-1.docx                # Diretrizes clínicas de referência
```

## Conjuntos de Dados

### `1_sinais_vitais_por_hora-1.csv`

Registos horários de monitorização por episódio de internamento.

| Campo | Descrição |
|---|---|
| `episodio` | Identificador do episódio (ex: `EP001`) |
| `data` | Data do registo |
| `hora` | Hora do registo (0–23) |
| `sat_o2` | Saturação de oxigénio (%) |
| `puls_rate` | Frequência de pulso (bpm) |
| `perfusion` | Índice de perfusão |

- **~9 857 registos** · **58 episódios** · período de janeiro a abril de 2024

### `3_patologias_por_dia-1.csv`

Patologias registadas por episódio e por dia de internamento.

| Campo | Descrição |
|---|---|
| `episodio` | Identificador do episódio |
| `data` | Data do registo |
| `patologia` | Diagnóstico/patologia registada |

- **~696 registos** · **26 patologias distintas**
- Inclui: displasia broncopulmonar, doença das membranas hialinas, icterícia neonatal, retinopatia da prematuridade, entre outras.

## Notas

- Os identificadores de episódios (`EP001`, `EP002`, …) são pseudonimizados.
- Dados de uso interno — não partilhar sem autorização.
