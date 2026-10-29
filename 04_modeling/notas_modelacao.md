# Notas metodológicas — Regressão

## Resultados da avaliação (split único 80/20)

| Modelo | MAE treino | RMSE treino | R² treino | MAE teste | RMSE teste | R² teste |
|---|---|---|---|---|---|---|
| Baseline (mediana) | 4.055 | 15.460 | −0.074 | 0.034 | 0.078 | −0.246 |
| Regressão Linear | 5.271 | 11.436 | 0.412 | 9.254 | 19.562 | −79 316 |
| Ridge (λ=10) | 5.647 | 13.895 | 0.132 | 5.706 | 6.690 | −9 274 |

> Métricas calculadas em 2026-10-29 com `dataset_regressao_24h.csv` (critério ≥1 registo).
> Após aplicação do novo critério (≥5/≥3 registos), re-executar o notebook e atualizar esta tabela.

## Interpretação

- O baseline supera os modelos treinados em todas as métricas do conjunto de teste
- R² negativos massivos indicam que os modelos não generalizam
- Causas prováveis: 70% de zeros no alvo + amostra pequena (n≈43) + 16 preditores
- **Conclusão correcta: "a utilidade preditiva não foi demonstrada com esta amostra"**
- Não afirmar que o modelo tem capacidade preditiva — o baseline (prevê sempre 0) é mais preciso no teste

## Limitações assumidas

- Split único 80/20 com ~9 episódios no teste — resultados instáveis
- LOO cross-validation recomendada como próximo passo (já descrita no notebook, não implementada)
- A concentração de zeros no alvo (70%) limita o que qualquer modelo pode aprender
- A dependência do alvo à frequência de observação não foi corrigida (ver `notas_data_preparation.md`)
- O caso com maior alvo (EP026, carga=85.57) pode não estar representado no teste

## Variáveis excluídas dos preditores (potencial leakage)

| Coluna | Motivo da exclusão |
|---|---|
| `n_registos_futuro` | Só conhecido após o período futuro |
| `duracao_dias` | Duração total do internamento, desconhecida no momento da previsão |
| `pat_predominante` / `pat_label` | Diagnóstico final consolidado |
| `carga_dessaturacao` | Carga total do episódio completo |
| `desat_count` / `desat_pct` | Calculados sobre o episódio completo em `dataset_final.csv` |

## Próximos passos recomendados

1. Re-executar `data_preparation.ipynb` com o novo critério de elegibilidade (≥5/≥3)
2. Re-executar `regressao_carga_dessaturacao.ipynb` sobre o novo dataset
3. Implementar LOO e comparar com o split único
4. Analisar correlação Spearman (alvo vs n_registos_futuro) — célula reg0015
5. Se ρ > 0.5, considerar normalizar o alvo pela cobertura temporal
