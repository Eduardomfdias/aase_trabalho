# Relatório de Revisão Final de Entrega — Projeto AASE (CRISP-DM)

**Unidade Curricular:** Aprendizagem Automática em Sistemas Empresariais (AASE)  
**Ano Letivo:** 2026/2027 — Mestrado em Engenharia e Gestão de Sistemas de Informação  
**Data da Auditoria:** 2026-11-04  
**Auditores:** Engenharia de Dados Sénior & Auditoria Independente  
**Commit Analisado:** `e3f4cca2baae473c242e2a3caaa3a45c3bc05e55` (`e3f4cca`)  
**Branch de Referência:** `main` (sincronizada localmente com `fix/auditoria-e-correcao-integral`)  

---

## 1. Objetivo e Âmbito da Revisão

O presente documento constitui a **auditoria final e independente de entrega** do Projeto 1 da UC de AASE. O escopo abrange a verificação técnica, metodológica e documental do repositório `aase_trabalho`, garantindo a estrita conformidade com as fases da metodologia CRISP-DM, a ausência de artefactos metodológicos espúrios (e.g. *data leakage*, sobregeneralização semântica, critérios incorretos de elegibilidade) e a reprodutibilidade integral dos resultados.

Esta revisão segue o princípio da verificação empírica direta: nenhum resultado ou alegação prévia foi assumido sem validação direta sobre os ficheiros, datasets, execuções de código e histórico Git.

---

## 2. Estado do Controlo de Versões (Git)

A verificação do repositório local produziu os seguintes factos confirmados:

- **Branch Atual:** `main`.
- **Commit Atual:** `e3f4cca` (`docs(clustering): corrigir interpretacao clinica dos perfis exploratorios`).
- **Presença dos Commits Chave:**
  - `51e90a4`: `fix(pipeline): auditoria e correcao tecnica e metodologica integral CRISP-DM` (presente na árvore).
  - `e3f4cca`: `docs(clustering): corrigir interpretacao clinica dos perfis exploratorios` (HEAD da `main` e da branch de correção).
- **Estado da Árvore de Trabalho (Working Tree):** Estritamente limpo (`nothing to commit, working tree clean`).
- **Alterações Locais Não Integradas:** Zero. Todas as correções técnicas e metodológicas foram fundidas na branch `main` via avanço rápido (*fast-forward*).
- **Relação com `origin/main`:** A branch local `main` encontra-se exatamente **2 commits à frente** de `origin/main` (`c860d65`), e 0 commits atrás.
- **Risco de Integração / Conflitos:** Inexistente. A história é puramente linear (`c860d65` $\to$ `51e90a4` $\to$ `e3f4cca`).
- **Política de Publicação:** Em cumprimento estrito das instruções, **não foi realizado qualquer comando `git push`** nem alteração forçada de histórico.

---

## 3. Ficheiros Inspecionados

Foram diretamente auditados e executados os seguintes artefactos:

| Componente | Ficheiros Analisados |
|---|---|
| **Documentação Central** | `README.md`, `checklist_projeto.md`, `crisp_dm_checklist.md`, `enunciado.md`, `duvidas.md`, `analise_duvidas.md` |
| **Relatórios de Auditoria** | `relatorio_auditoria.md`, `relatorio_auditoria_independente.md` |
| **Fase 1 (Business Understanding)** | `01_Business_Understanding/relatorio1.md` |
| **Fase 2 (Data Understanding)** | `02_data_understanding/relatorio_data_understanding.md`, `02_data_understanding/eda_aase.ipynb`, `eda_aase.ipynb` |
| **Fase 3 (Data Preparation)** | `03_data_preparation/data_preparation.ipynb`, `03_data_preparation/validacao_data_preparation.ipynb`, `03_data_preparation/notas_data_preparation.md`, `03_data_preparation/relatorio_data_preparation.md`, `dataset_final.csv`, `dataset_regressao_24h.csv`, `metadata.csv`, `train.csv`, `test.csv` |
| **Fase 4 (Modeling)** | `04_modeling/regressao_carga_dessaturacao.ipynb`, `04_modeling/classificacao_patologia.ipynb`, `04_modeling/clustering_perfis_clinicos.ipynb`, `04_modeling/notas_modelacao.md`, `04_modeling/predicoes_teste.csv` |
| **Testes Automatizados** | `tests/test_pipeline.py` |

---

## 4. Verificações Metodológicas Realizadas e Resultados

### 4.1 Separação Temporal Estrita (Janela Inicial vs. Janela Futura)
- **Implementação:** O instante de ancoragem $t_0$ é definido como o primeiro timestamp horário válido com sinais vitais no episódio. A janela inicial de monitorização abrange o intervalo semiaberto $[t_0, t_0 + 24\text{ h}[$. A janela de seguimento futuro abrange todos os registos com timestamp $t \ge t_0 + 24\text{ h}$.
- **Verificação:** Zero sobreposição temporal detetada nos registos ou no cálculo de preditores.

### 4.2 Prevenção Rigorosa de Fuga de Informação (*Data Leakage*)
- **Variáveis Preditores:** As 16 variáveis estatísticas dos modelos preditivos (`sat_o2_*`, `puls_rate_*`, `perfusion_*`, `carga_desat_janela`, etc.) são computadas estritamente a partir das observações da janela inicial de 24 horas.
- **Isolamento de Preditores:** As variáveis pós-janela (`carga_dessaturacao_futura`, `n_registos_futuro`, `n_spo2_futuro_validos`) são explicitamente removidas da matriz de features antes do treino.
- **Imputação de Dados:** O preenchimento de valores ausentes pela mediana é ajustado exclusivamente no subconjunto de treino de cada divisão (*train-only fit*), sendo aplicado como transformação sobre a partição de teste/validação sem qualquer contaminação bidirecional.

### 4.3 Critérios de Elegibilidade Fisiológica e Contagem de $\text{SpO}_2$
- **Critério Documentado vs. Implementado:** A elegibilidade exige:
  1. $\ge 5$ medições válidas de $\text{SpO}_2$ no intervalo fisiológico $[50, 100]\%$ na janela inicial ($0 \le t < 24\text{ h}$);
  2. $\ge 3$ medições válidas de $\text{SpO}_2$ no intervalo fisiológico $[50, 100]\%$ na janela futura ($t \ge 24\text{ h}$).
- **Resultado Empírico:**
  - Amostra total com sinais vitais: 47 episódios únicos normalizados.
  - Episódios elegíveis para regressão: **exatamente 40**.
  - Episódios excluídos: **exatamente 7** (`EP010`, `EP018`, `EP024`, `EP028`, `EP029`, `EP030`, `EP042`), todos por insuficiência de observações válidas de $\text{SpO}_2$ na janela futura ou em ambas as janelas.

### 4.4 Coerência do Target de Regressão e Interpretação
- **Definição Operacional:** `carga_dessaturacao_futura` $= \sum (90 - \text{SpO}_2)$ para todas as observações com $\text{SpO}_2 < 90\%$ na janela futura ($t \ge 24\text{ h}$).
- **Distribuição Observada:** Mínimo $= 0.00$, Máximo $= 85.57$, Média $= 3.45$, Mediana $= 0.00$, Desvio-padrão $= 14.01$. Em 28 dos 40 episódios (70,0%), a carga futura de dessaturação é estritamente nula.
- **Análise Crítica:** Devido à forte assimetria e preponderância de zeros, o preditor ingénuo da mediana ($0.0$) atinge $\text{MAE} = 3.451$ e $\text{RMSE} = 14.253$ em Leave-One-Out, superando a Regressão Linear e Ridge ($\lambda=10$). Os modelos lineares sobreajustam-se aos casos atípicos com hipoxemia severa (e.g. EP026), gerando $R^2$ negativos. Esta conclusão é reportada com total honestidade científica, sem ocultação de limitações.

### 4.5 Resolução do Problema N1: Rotulagem dos Clusters e Ressalva Metodológica
- **Evidência Empírica do Agrupamento:** No particionamento não supervisionado via *k-Means* ($k=2$), as médias calculadas confirmam:
  - **Cluster 0 (37 episódios, 78,7%):** $\text{SpO}_2$ média $= 96,66\%$, $\text{FC} = 138,9\text{ bpm}$, $\text{IP} = 1,22$, $\%$ Dessaturação $= 0,09\%$. Designação adotada: **«Perfil com saturação média mais elevada»**.
  - **Cluster 1 (10 episódios, 21,3%):** $\text{SpO}_2$ média $= 94,86\%$, $\text{FC} = 152,8\text{ bpm}$, $\text{IP} = 1,12$, $\%$ Dessaturação $= 2,56\%$. Designação adotada: **«Perfil com maior frequência de dessaturações»**.
- **Coeficiente de Silhueta:** $0.2263$ (Davies-Bouldin $= 1.6246$), caracterizando uma separação estatística modesta.
- **Ressalva Metodológica Obrigatória:** Encontra-se explicitamente integrada no notebook executado `04_modeling/clustering_perfis_clinicos.ipynb`, em `notas_modelacao.md`, no `README.md`, na checklist e nos relatórios:
  > *Os clusters representam agrupamentos estatísticos exploratórios obtidos através do algoritmo k-Means. A separação observada é modesta (Silhueta = 0.2263), pelo que os perfis identificados não devem ser interpretados como diagnósticos clínicos, categorias de risco validadas ou indicadores autónomos de estabilidade clínica.*
- **Conformidade Semântica:** Todas as designações inadequadas («Estável» vs «Instável / Risco») foram completamente eliminadas das conclusões do clustering.

---

## 5. Testes e Reprodutibilidade

### 5.1 Execução da Suíte de Testes Automatizada
A suíte completa de testes parametrizados em `tests/test_pipeline.py` foi executada em ambiente macOS com Python 3.12:

```text
============================= test session starts ==============================
platform darwin -- Python 3.12.7, pytest-9.2.0, pluggy-1.7.0 -- /usr/local/bin/python3
cachedir: .pytest_cache
rootdir: /Users/rui.carneiro/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Mestrado/AASE/aase_trabalho
plugins: platformdirs-4.14.5, anyio-4.16.0
collected 17 items

tests/test_pipeline.py::test_id_normalization PASSED                     [  5%]
tests/test_pipeline.py::test_date_parsing_formats PASSED                 [ 11%]
tests/test_pipeline.py::test_physiological_filtering PASSED              [ 17%]
tests/test_pipeline.py::test_eligibility_tc1_exact_thresholds PASSED     [ 23%]
tests/test_pipeline.py::test_eligibility_tc2_insufficient_initial PASSED [ 29%]
tests/test_pipeline.py::test_eligibility_tc3_insufficient_future PASSED  [ 35%]
tests/test_pipeline.py::test_eligibility_tc4_no_valid_spo2 PASSED        [ 41%]
tests/test_pipeline.py::test_eligibility_tc5_invalid_records_do_not_count PASSED [ 47%]
tests/test_pipeline.py::test_target_calculation_threshold_90 PASSED      [ 52%]
tests/test_pipeline.py::test_target_calculation_hypoxemia_deficit PASSED [ 58%]
tests/test_pipeline.py::test_target_calculation_zero_desaturation PASSED [ 64%]
tests/test_pipeline.py::test_window_temporal_separation PASSED           [ 70%]
tests/test_pipeline.py::test_anti_leakage_feature_selection PASSED       [ 76%]
tests/test_pipeline.py::test_train_only_median_imputation PASSED         [ 82%]
tests/test_pipeline.py::test_dataset_regressao_24h_integrity PASSED      [ 88%]
tests/test_pipeline.py::test_dataset_final_integrity PASSED              [ 94%]
tests/test_pipeline.py::test_metadata_consistency PASSED                 [100%]

============================== 17 passed in 0.01s ==============================
```
- **Taxa de Sucesso:** 17 de 17 testes aprovados (**100% de sucesso**, 0 falhas).

### 5.2 Validação da Execução dos Notebooks
Todos os notebooks das fases analíticas contêm saídas devidamente gravadas e reprodutíveis:
1. `02_data_understanding/eda_aase.ipynb`: Executado, com análise univariada, bivariada e circadianas completas.
2. `03_data_preparation/data_preparation.ipynb`: Executado, gerando os ficheiros limpos e consolidados.
3. `03_data_preparation/validacao_data_preparation.ipynb`: Executado, validando distribuições e nulos.
4. `04_modeling/regressao_carga_dessaturacao.ipynb`: Executado sem erros, com validação LOO e split 80/20.
5. `04_modeling/classificacao_patologia.ipynb`: Executado sem erros, com baselines e modelos supervisionados.
6. `04_modeling/clustering_perfis_clinicos.ipynb`: Executado integralmente *in-place*, com gráficos PCA e métricas de silhueta.

---

## 6. Avaliação das Fases CRISP-DM

| Fase CRISP-DM | Estado Auditado | Evidência Concreta e Fundamentação |
|---|---|---|
| **1. Business Understanding** | **Concluído ✅** | Relatório `01_Business_Understanding/relatorio1.md` formalmente estruturado. Objetivos de Negócio (ON1 a ON3), Critérios de Sucesso (CS-N1 a CS-N4) e Objetivos de Mineração de Dados (ODM1 a ODM3) definidos com precisão e alinhamento com a área de neonatologia. |
| **2. Data Understanding** | **Concluído ✅** | Dicionário de variáveis, identificação de 242 registos fisiologicamente inválidos (2,5%), análise de correlações e padrões circadianos documentados em `02_data_understanding/relatorio_data_understanding.md` e `eda_aase.ipynb`. |
| **3. Data Preparation** | **Concluído ✅** | Preservação intocada dos ficheiros de origem (`1_sinais_vitais_por_hora-1.csv` e `3_patologias_por_dia-1.csv`). Normalização de identificadores (47 episódios). Tratamento de formatos de datas múltiplos. Filtragem de limites fisiológicos. Resolução documentada de coocorrência de patologias em EP001. Elegibilidade rigorosa de $\text{SpO}_2$ ($\ge 5$ inicial, $\ge 3$ futuro) com 40 episódios elegíveis. Imputação pela mediana sem fuga. 17 testes automáticos. |
| **4. Modeling** | **Concluído ✅** | Cobertura integral das três famílias analíticas exigidas pelo enunciado: **Regressão** (Linear, Ridge, Baseline Mediana), **Classificação** (k-NN, Árvore de Decisão, Naive Bayes, Baseline Maioritária) e **Clustering** (k-Means $k \in [2,5]$, PCA). Validação rigorosa com Leave-One-Out (LOO CV) e partição treino/teste 80/20. |
| **5. Evaluation** | **Concluído com Reserva Externa 🟡** | Avaliação analítica e metodológica completa e documentada face aos critérios de sucesso de negócio (honestidade sobre baselines não batidos em regressão e desbalanceamento extremo em classificação). Reserva: **Submissão à competição Kaggle pendente** de submissão formal pelos autores do grupo. |
| **6. Deployment** | **Previsto para Projeto 2 ⏳** | O enunciado da UC define explicitamente que a fase de implementação decorrerá no **Projeto 2** (janeiro de 2027), através da construção do Data Warehouse, rotinas ETL e Dashboards analíticos em Power BI/Tableau. |

---

## 7. Classificação dos Problemas Encontrados

| Nível de Gravidade | Problema Identificado | Localização | Descrição e Impacto | Ação Recomendada / Estado |
|---|---|---|---|---|
| **Crítico** | *Nenhum* | — | Não existem falhas que invalidem os resultados, causem quebras de execução ou configurem *data leakage*. | Nenhuma ação necessária. |
| **Alto** | *Nenhum* | — | Todos os problemas metodológicos maiores (elegibilidade de SpO₂, leakage, target de regressão e identificadores) foram previamente corrigidos no commit `51e90a4`. | Problemas encerrados com sucesso. |
| **Médio** | Submissão na plataforma Kaggle por formalizar | Competição Kaggle TP1 | O enunciado atribui 30% da classificação à performance dos modelos no ranking relativo inter-grupos. A submissão do ficheiro `04_modeling/predicoes_teste.csv` (ou predições do baseline ótimo) deve ser enviada para a plataforma. | Submeter o ficheiro gerado na plataforma Kaggle antes do prazo final da avaliação contínua. |
| **Baixo** | Redundância de ficheiro de EDA na raiz | `eda_aase.ipynb` vs `02_data_understanding/eda_aase.ipynb` | Existe uma versão inicial do notebook de EDA na raiz do repositório, paralela à versão consolidada dentro da diretoria `02_data_understanding/`. Não introduz qualquer erro de execução. | Manter como está ou arquivar futuramente para manter o histórico original. |
| **Baixo (Futuro)** | N2 — Modularização de código auxiliar | Pipeline global | As rotinas de parsing de datas e normalização de identificadores estão replicadas em funções internas nos notebooks em vez de centralizadas num pacote `src/utils.py`. | Transitar como refatorização de código para o Projeto 2. |
| **Baixo (Futuro)** | N3 — Engenharia de alvos alternativos de dessaturação | Tarefa de Regressão | Possibilidade de explorar métricas relativas (e.g. rácio de tempo sob hipoxemia ou taxa horária de dessaturação) face à duração total do internamento. | Transitar como melhoria analítica para o Projeto 2. |

---

## 8. Limitações Metodológicas que Devem Ser Reconhecidas na Entrega

Os autores devem assegurar que a apresentação oral e o relatório final mencionam explicitamente as seguintes limitações reais dos dados clínicos:

1. **Dimensão Amostral Reduzida ($n=40$ a $47$ episódios):** Impossibilita a generalização estatística de modelos de alta capacidade parametrizada e restringe o poder dos testes de significância.
2. **Preponderância de Zeros na Regressão:** Em 70% dos episódios, a carga de dessaturação futura é nula, tornando o preditor ingénuo da mediana ($0.0$) extremamente difícil de superar com modelos lineares simples, resultando em $R^2$ negativos.
3. **Desbalanceamento Extremo na Classificação:** A Doença das Membranas Hialinas (DMH) representa 61,5% dos diagnósticos, enquanto 3 patologias possuem apenas 1 ou 2 observações. Nenhum algoritmo supervisionado consegue aprender classes unitárias sem representatividade amostral.
4. **Separação Estatística Modesta no Clustering:** A silhueta de $0.2263$ evidencia que os clusters são aproximações exploratórias do continuum fisiológico neonatal e não diagnósticos clínicos validados.

---

## 9. Parecer Final e Prontidão para Entrega

Com base nas verificações técnicas, na integridade dos dados, na conformidade metodológica com o processo CRISP-DM e na taxa de 100% de sucesso nos testes automatizados, emite-se o seguinte parecer:

### **Classificação: APTO PARA ENTREGA**

### Justificação:
1. **Rigor Técnico e Metodológico Integral:** A elegibilidade foi corrigida para contagem estrita de medições válidas de $\text{SpO}_2$; a segregação temporal é rigorosa; e o *data leakage* foi eliminado na seleção de preditores e na imputação de treino.
2. **Metodologia CRISP-DM Completa:** Todas as fases sob a alçada do Projeto 1 (Business Understanding, Data Understanding, Data Preparation, Modeling e Evaluation analítica) estão concluídas, alinhadas entre si e fundamentadas clinicamente. A fase de Deployment está formalmente atribuída ao Projeto 2.
3. **Reprodutibilidade Comprovada:** Todos os 5 notebooks executam com sucesso de ponta a ponta e 17/17 testes automatizados de regressão foram aprovados.
4. **Honestidade Científica:** Os relatórios não manipulam os resultados para esconder $R^2$ negativos ou a superioridade dos baselines da mediana e classe maioritária, demonstrando maturidade analítica e conformidade com as boas práticas académicas.

---

## 10. Ações Recomendadas Antes da Submissão Definitiva

1. **Submissão no Kaggle:** Efetuar o upload do ficheiro de predições (`04_modeling/predicoes_teste.csv`) para a competição Kaggle da unidade curricular, conforme estipulado no enunciado.
2. **Publicação Remota Git (`git push`):** Quando a equipa docente ou o utilizador determinarem a submissão do repositório, executar a sincronização da branch `main` local com o repositório remoto (`origin/main`):
   ```bash
   git push origin main
   ```
   *(Nota: Por cumprimento estrito das instruções da presente auditoria, o comando não foi executado nesta sessão).*

