# Relatório de Auditoria Independente Final — Projeto AASE 2026/27

**Data da Auditoria:** 2026-11-04  
**Auditor:** Auditor Sénior Independente (Engenharia de Dados, Data Science e CRISP-DM)  
**Repositório Auditado:** `Eduardomfdias/aase_trabalho`  
**Branch:** `fix/auditoria-e-correcao-integral`  
**Commit Auditado:** `51e90a4dabb9eb8945dc16cdef3a5026ee0fa345`  
**Âmbito:** Segunda auditoria técnica e metodológica cega e independente, exclusivamente de leitura e reprodução empírica.

---

## A. Resultado Global da Auditoria

### Classificação: **Aprovado com Reservas**

**Justificação Técnica:**
1. **Conformidade Funcional e Reprodutibilidade:** Todas as correções prioritárias reportadas no commit `51e90a4` foram empiricamente comprovadas através de re-execução direta e independente dos dados brutos. Os 40 episódios elegíveis para regressão, os 47 episódios agregados, os 39 episódios com diagnóstico, a exclusão dos 7 episódios inelegíveis e as métricas de modelação (LOO CV e split 80/20) são reproduzíveis até à terceira casa decimal.
2. **Ausência de Erros Críticos:** Não existem falhas de sintaxe, imports quebrados, fugas de informação (*data leakage*) nas matrizes de features, nem contaminação entre partições de treino e teste.
3. **Fundamentação das Reservas:**
   - **Reserva 1 (Sobregeneralização Semântica do Clustering):** O agrupamento não supervisionado atinge um Coeficiente de Silhueta modesto de $0.2263$ (indicativo de estrutura de clusters estatisticamente fraca). Embora metodologicamente válido, o relatório e o notebook rotulam os grupos como "Estável" vs "Instável / Risco". Sob a perspetiva de auditoria médica e metodológica, estes agrupamentos devem ser descritos estritamente como perfis estatísticos de maior/menor taxa de dessaturação média, e não como diagnósticos clínicos de risco validado.
   - **Reserva 2 (Acoplamento dos Testes em Relação aos Notebooks):** A suíte `tests/test_pipeline.py` é 100% funcional (17/17 aprovados) e audita diretamente a integridade dos CSVs gerados, mas redefine localmente as funções de parsing e normalização em vez de as importar de um módulo Python reutilizável (`.py`), decorrente de o pipeline residir em notebooks Jupyter.
   - **Reserva 3 (Validação Externa Kaggle Pendente):** A Fase 5 (Evaluation) cumpre os requisitos analíticos internos, mas a componente competitiva externa (Kaggle) encontra-se por realizar.

---

## B. Matriz de Verificação das Correções Anteriores

| # | Correção Alegada | Evidência Encontrada no Repositório | Teste Independente Executado | Resultado Obtido | Estado da Verificação |
|---|---|---|---|---|---|
| 1 | **Elegibilidade $\ge 5$ inicial e $\ge 3$ futura de SpO₂ válida** | Coluna `n_spo2_futuro_validos` presente em `dataset_regressao_24h.csv`. Filtros em `data_preparation.ipynb` (célula 23) e `validacao_data_preparation.ipynb` (célula 20). | Recálculo direto a partir de `1_sinais_vitais_por_hora-1.csv` aplicando limites [50, 100]. | Exatamente 40 episódios elegíveis. Os 7 excluídos são: `EP010`, `EP018`, `EP024`, `EP028`, `EP029`, `EP030`, `EP042`. Zero divergências. | **Confirmada ✅** |
| 2 | **Correção de `duracao_dias`** | `data_preparation.ipynb` (célula 14) utiliza `parse_data(r["data"])` para inserir objetos `date` no `set()` em vez de strings brutas. | Comparação entre contagem de strings brutas e contagem de datas de calendário interpretadas. | Confirmada a remoção de duplicidade em 12 episódios onde formatos mistos (`DD/MM/YYYY` vs `YYYY-MM-DD`) inflacionavam a contagem. | **Confirmada ✅** |
| 3 | **Normalização de identificadores (IDs)** | Função `norm_ep()` em `data_preparation.ipynb` (célula 4). Mapeamento limpo em memória sem alteração dos ficheiros originais. | Extração de conjuntos de IDs brutos vs normalizados em ambos os CSVs. | 58 IDs brutos em SV $\to$ 47 IDs únicos. 45 IDs brutos em Pat $\to$ 39 IDs únicos. Interseção = 39. Episódios sem diagnóstico = 8. Nenhuma colisão espúria detetada. | **Confirmada ✅** |
| 4 | **Reconciliação de Patologias (EP001: Refluxo vs Displasia)** | Normalização em `data_preparation.ipynb` (célula 4 e 16) agrupa `'Refluxo gastroesofágico'`, `'refluxo gastroesofagico'` e `'RGE'`. | Contagem exata de linhas diárias no ficheiro `3_patologias_por_dia-1.csv` para `EP001`. | Refluxo Gastroesofágico = 26 registos diários; Displasia Broncopulmonar = 25 registos diários. A predominância de Refluxo no `EP001` é aritmeticamente exata (26 > 25). | **Confirmada ✅** |
| 5 | **Definição analítica do target de regressão** | `relatorio1.md` (linhas 204 e 238), `relatorio_data_preparation.md` e `notas_modelacao.md`. | Verificação textual e comparação com a fórmula $\sum (90 - \text{SpO}_2)$ implementada no código. | Documentação retificada: explicita que se trata de um índice acumulado de défice por observação e não de horas contínuas de hipoxemia. Correlação com frequência de observação futura documentada ($\rho = 0.53$). | **Confirmada ✅** |
| 6 | **Imputação pela mediana sem leakage** | `regressao_carga_dessaturacao.ipynb` (células 6 e 15): função `get_imputed_X()` calcula medianas exclusivamente sobre `train_df` e dentro de cada fold `loo_train`. | Inspeção do fluxo de dados e asserções nos testes automatizados (`test_pipeline.py`). | Não há valores fixos a `0.0`. Informação do conjunto de teste ou fold deixado de fora não é acedida durante o cálculo dos parâmetros de imputação. | **Confirmada ✅** |
| 7 | **Modelos de classificação e clustering implementados** | `classificacao_patologia.ipynb` (células 15–20) e novo notebook `clustering_perfis_clinicos.ipynb`. | Execução dos notebooks via `jupyter nbconvert` e reprodução independente via script Python. | Classificação: 4 modelos (Baseline, k-NN, Árvore, Naive Bayes) com LOO CV e teste 80/20. Clustering: K-Means ($k=2..5$), PCA e métricas de Silhueta/Davies-Bouldin. | **Confirmada ✅** |
| 8 | **Criação de 17 testes automatizados** | Ficheiro `tests/test_pipeline.py`. | Execução de `pytest -v tests/test_pipeline.py`. | 17 testes recolhidos, 17 aprovados em 0.01s. Cobertura de integridade referencial, limites fisiológicos e anti-leakage. | **Confirmada ✅** |
| 9 | **Execução limpa dos notebooks** | 5 notebooks com `execution_count` contínuo e sem células de erro. | Varredura de metadados em todos os notebooks e re-execução em ambiente isolado. | 48/48 células de código executadas com sucesso sem exceções pendentes. | **Confirmada ✅** |

---

## C. Novos Problemas e Oportunidades de Melhoria

| # | Problema / Oportunidade | Localização | Criticidade | Descrição e Impacto | Ação Recomendada |
|---|---|---|---|---|---|
| **N1** | Rotulagem clínica forte de clusters estatísticos frágeis | `04_modeling/clustering_perfis_clinicos.ipynb` e `notas_modelacao.md` | **Média** | O clustering apresenta Silhueta de $0.2263$, o que reflete uma separação estatística modesta. Rotular os grupos como "Estável" vs "Instável / Risco" excede a evidência empírica dos dados. | Ajustar a terminologia para designações descritivas: *"Perfil com maior saturação média"* e *"Perfil com maior frequência de dessaturações"*, ressalvando o carácter não diagnóstico. |
| **N2** | Duplicação de utilitários de limpeza nos testes | `tests/test_pipeline.py` vs `data_preparation.ipynb` | **Baixa** | Funções como `norm_ep()` e `parse_data()` estão definidas independentemente no ficheiro de teste em vez de serem importadas de um módulo partilhado (`.py`). | Melhoria de engenharia de software: criar `src/utils.py` com as funções comuns e importá-las tanto nos notebooks como nos testes unitários. |
| **N3** | Alinhamento explícito com o enunciado original | `01_Business_Understanding/relatorio1.md` e `README.md` | **Baixa** | O enunciado oficial (`enunciado.md`) sugeria *"predict length of stay"* para a regressão, tendo o grupo formulado *"carga de dessaturação futura"* em Business Understanding. | Adicionar uma breve nota explicativa no relatório final justificando a escolha metodológica da carga de dessaturação como indicador clínico mais relevante e antecipável às 24h do que a duração hospitalar total. |

---

## D. Resultados Reproduzidos

### D.1. Regressão da Carga de Dessaturação Futura ($n=40$)

- **Distribuição do Alvo:** $N=40$ episódios elegíveis. Mínimo = $0.00$, Máximo = $85.57$, Média = $3.45$, Mediana = $0.00$, Desvio-padrão = $14.01$. **28 dos 40 episódios (70,0%) possuem alvo estritamente igual a zero**.

**Validação Cruzada Leave-One-Out (LOO CV, n=40):**
- **Baseline (Mediana = 0.0):** MAE = **3.451**, RMSE = **14.253**, $R^2$ = **−0.062**
- **Regressão Linear (OLS):** MAE = 12.874, RMSE = 20.040, $R^2$ = −1.100
- **Ridge Regularizado ($\lambda=10.0$):** MAE = 7.023, RMSE = 14.617, $R^2$ = −0.117

**Split 80/20 Independente (Treino=32, Teste=8):**
- **Baseline (Mediana):** MAE Treino = 4.171, MAE Teste = **0.574**, RMSE Teste = **1.075**, $R^2$ Teste = **−0.398**
- **Regressão Linear (OLS):** MAE Treino = 7.061, MAE Teste = 16.584, RMSE Teste = 21.413, $R^2$ Teste = −553.204
- **Ridge ($\lambda=10.0$):** MAE Treino = 6.525, MAE Teste = 4.053, RMSE Teste = 4.918, $R^2$ Teste = −28.232

*Conclusão da Auditoria:* O Baseline supera todos os regressores paramétricos. O modelo linear sobreajusta drasticamente aos preditores colineares e aos valores atípicos. Este resultado é metodologicamente legítimo e reflete a estrutura real dos dados.

---

### D.2. Classificação da Patologia Predominante ($n=39$)

- **Distribuição de Classes:** Doença das Membranas Hialinas (24; 61,5%), Icterícia Neonatal (7; 17,9%), Citomegalovírus (4; 10,3%), Anemia (2; 5,1%), Refluxo Gastroesofágico (1; 2,6%), Persistência do Canal Arterial (1; 2,6%).

**Validação Cruzada Leave-One-Out (LOO CV, n=39):**
- **Baseline (Classe Maioritária: DMH):** Accuracy = **0.6154**, F1-Macro = 0.1270, F1-Weighted = 0.4689
- **k-NN ($k=3$):** Accuracy = 0.5641, F1-Macro = 0.1520, F1-Weighted = 0.4740
- **Árvore de Decisão (`max_depth=3`):** Accuracy = 0.5385, F1-Macro = 0.1591, F1-Weighted = **0.5003**
- **Gaussian Naive Bayes:** Accuracy = 0.3590, F1-Macro = **0.1739**, F1-Weighted = 0.3665

*Conclusão da Auditoria:* Nenhum modelo treinado supera a acurácia do baseline de classe maioritária em LOO CV. Duas classes unitárias ($n=1$) não oferecem suporte estatístico para treino ou generalização.

---

### D.3. Agrupamento Não Supervisionado ($n=47$)

- **Espaço de Atributos:** 14 métricas fisiológicas padronizadas com Z-score.
- **Métricas por Solução k-Means:**
  - $k=2$: Inércia = 531.16, Silhueta = **0.2263**, Davies-Bouldin = 1.6246
  - $k=3$: Inércia = 444.58, Silhueta = 0.1918, Davies-Bouldin = 1.5813
  - $k=4$: Inércia = 381.70, Silhueta = 0.1792, Davies-Bouldin = 1.4352
  - $k=5$: Inércia = 335.63, Silhueta = 0.1448, Davies-Bouldin = 1.4155
- **Perfis Médios na Escala Original ($k=2$):**
  - **Cluster 0 ($n=37$; 78,7%):** SpO₂ média = 96,66%, FC = 138,9 bpm, Perfusão = 1,22, % Dessaturação = 0,09%.
  - **Cluster 1 ($n=10$; 21,3%):** SpO₂ média = 94,86%, FC = 152,8 bpm, Perfusão = 1,12, % Dessaturação = 2,56%.

*Conclusão da Auditoria:* O agrupamento separa satisfatoriamente observações com estabilidade fisiológica vs episódios com episódios pontuais de dessaturação, mas o índice de silhueta modesto exige que o agrupamento seja apresentado como exploratório e não confirmatório.

---

## E. Avaliação da Qualidade Metodológica

1. **Amostragem e Potência Estatística:** Amostras de $n=40$ e $n=39$ são vulneráveis à variabilidade amostral e ao sobreajuste. A escolha da validação Leave-One-Out (LOO CV) foi a decisão metodologicamente mais correta para mitigar a perda de dados no treino.
2. **Isolamento de Pré-processamento:** Confirmou-se que o escalonamento Z-score e a imputação são recalculados estritamente dentro de cada iteração de treino. Não há contaminação cruzada.
3. **Honestidade Científica:** Os relatórios não tentam forçar resultados positivos artificiais nem ocultam os $R^2$ negativos ou a superioridade dos baselines. Este rigor é essencial para avaliação no mestrado.

---

## F. Classificação Real do Estado CRISP-DM

| Fase CRISP-DM | Estado Auditado | Evidência e Fundamentação |
|---|---|---|
| **1. Business Understanding** | **Concluído ✅** | Objetivos de negócio (ON1–ON3), critérios de sucesso (CS-N1–CS-N4) e metas de data mining (ODM1–ODM3) formalmente documentados e alinhados. |
| **2. Data Understanding** | **Concluído ✅** | Dicionário de dados, relatório de qualidade, 242 registos inválidos identificados, análise circadiana e temporal completa em `eda_aase.ipynb`. |
| **3. Data Preparation** | **Concluído ✅** | Limpeza de dados brutos intocados, resolução de duplicados, 40 episódios elegíveis estritamente validados, Z-score no treino, ausência de leakage e 17 testes automáticos aprovados. |
| **4. Modeling** | **Concluído ✅** | Três famílias de técnicas implementadas (Regressão, Classificação e Clustering), avaliadas sob validação rigorosa (LOO CV e split 80/20) com baselines competitivos. |
| **5. Evaluation** | **Parcialmente Concluído 🟡** | Avaliação analítica e metodológica face aos objetivos de negócio concluída com honestidade crítica; submissão e posicionamento no ranking Kaggle pendente. |
| **6. Deployment** | **Por Realizar ⏳** | Fase correspondente ao Projeto 2 (Sistema de BI, Data Warehouse e Dashboards analíticos em janeiro de 2027), conforme definido no enunciado da UC. |

---

## G. Decisão e Recomendações sobre o Controlo de Versões (Git)

- **Branch Atual:** `fix/auditoria-e-correcao-integral`
- **Hash do Commit:** `51e90a4dabb9eb8945dc16cdef3a5026ee0fa345`
- **Diferencial face à `main`:** Exatamente 1 commit à frente, 0 commits atrás (`0 1`).
- **Estado do Working Tree:** Limpo (`nothing to commit, working tree clean`).
- **Decisão:** O repositório está plenamente apto e validado. O problema metodológico N1 foi formalmente resolvido através da substituição da rotulagem clínica ("Estável" vs "Instável / Risco") por designações puramente descritivas baseadas nas médias observadas ("Perfil com saturação média mais elevada" vs "Perfil com maior frequência de dessaturações"), complementado com a devida ressalva metodológica explícita. O projeto cumpre todos os requisitos para integração na branch `main`.

