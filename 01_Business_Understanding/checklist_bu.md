# Checklist — Business Understanding (CRISP-DM)

> Relatório: `relatorio1.md` · Entrega: semana 19/10/2026

## 1. Determinar Objetivos de Negócio

- [x] Apresentação da organização / contexto clínico
- [x] Background do problema (sobrecarga de informação, ausência de perfis de risco, diagnóstico tardio)
- [x] Objetivos de negócio definidos (ON1 estratificação de risco, ON2 antecipação da severidade, ON3 apoio ao diagnóstico)
- [x] Critérios de sucesso de negócio mensuráveis (CS-N1 a CS-N4)

## 2. Avaliar a Situação

- [x] Inventário dos recursos disponíveis (dados, equipa, infraestrutura)
- [x] Requisitos, pressupostos e restrições documentados (R1–R3, P1–P4, C1–C3)
- [x] Riscos e contingências com probabilidade (R1–R5)
- [x] Terminologia de domínio definida
- [x] Custos e benefícios estimados

## 3. Determinar Objetivos de Mineração de Dados

- [x] ODM1 — Clustering (aprendizagem não supervisionada) → ON1
- [x] ODM2 — Regressão → ON2
- [x] ODM3 — Classificação (patologia predominante) → ON3
- [x] Critérios de sucesso DM com limiares conservador e ambicioso (CS-DM1 a CS-DM3)

## 4. Produzir Plano do Projeto

- [x] Tabela com todas as 6 fases CRISP-DM, tarefas e datas
- [x] Avaliação inicial das ferramentas e técnicas (Python, NumPy, Matplotlib, Scikit-learn)

## Estrutura documental

- [x] Resumo em português
- [x] Abstract em inglês
- [x] Glossário de termos clínicos
- [x] Tabela de abreviaturas e siglas
- [x] Conclusão com síntese dos 4 pontos-chave
- [x] Próximos passos definidos (4 tarefas do Data Understanding)

---

## ⚠️ Divergência face ao enunciado

| Enunciado | Relatório |
|---|---|
| **Regressão:** prever *length of stay* (duração do internamento) | **ODM2:** prever *carga de dessaturação* (horas com SpO₂ < 90%) |

O grupo optou por um alvo de regressão clinicamente mais específico. Pode ser aceite se justificado, mas verificar com o docente se é necessário incluir também a duração do internamento como alvo alternativo.
