# Checklist CRISP-DM — AASE

Projeto: **NeoData Clinics — Análise de Sinais e Episódios Clínicos**

> Itens marcados com ✅ estão cobertos no documento *Business Understanding*; a referência indica o capítulo correspondente.

---

## Fase 1 — Business Understanding (Compreensão do Negócio)

**Como aplicar:** O ponto de partida é sempre o negócio, nunca os dados. Nesta fase
identifica-se *o que* o projeto deve alcançar do ponto de vista organizacional e
clínico, antes de qualquer contacto com ficheiros ou modelos. O analista deve
entrevistar os utilizadores finais (médicos, enfermeiros), ler documentação do serviço
e formular os objetivos em linguagem clínica. Só depois esses objetivos são traduzidos
em problemas analíticos mensuráveis. O entregável final — o **plano do projeto** — é o
contrato entre o negócio e a equipa de análise para todas as fases seguintes.

### Determinar Objetivos de Negócio
- [x] Background — contexto do negócio `§2.1.1`
- [x] Objetivos de negócio `§2.1.2`
- [x] Critérios de sucesso de negócio `§2.1.3`

### Avaliar a Situação
- [x] Inventário de recursos `§2.2.1`
- [x] Requisitos, pressupostos e restrições `§2.2.2`
- [x] Riscos e contingências `§2.2.3`
- [x] Terminologia (glossário) `§2.2.4`
- [x] Custos e benefícios `§2.2.5`

### Determinar Objetivos de Prospeção de Dados
- [x] Objetivos de prospeção de dados `§2.3.1`
- [x] Critérios de sucesso de prospeção `§2.3.2`

### Produzir Plano do Projeto
- [x] Plano do projeto `§2.4.1`
- [x] Avaliação inicial de ferramentas e técnicas `§2.4.2`

---

## Fase 2 — Data Understanding (Compreensão dos Dados)

**Como aplicar:** O objetivo é conhecer os dados disponíveis sem ainda os transformar.
Carregam-se os ficheiros tal como foram fornecidos, registam-se as suas dimensões,
tipos de campos e valores extremos, e exploram-se visualmente as distribuições e
relações entre variáveis. Em paralelo avalia-se a qualidade: registos fora dos
limiares clínicos (artefactos de sensor), valores em falta e inconsistências de
nomenclatura. No caso do AASE, esta fase incide sobre os dois CSV —
`1_sinais_vitais_por_hora-1.csv` e `3_patologias_por_dia-1.csv` — e os resultados
alimentam diretamente o notebook `eda_aase.ipynb`.

### Recolher Dados Iniciais
- [ ] Relatório de recolha de dados iniciais

### Descrever Dados
- [ ] Relatório de descrição de dados

### Explorar Dados
- [ ] Relatório de exploração de dados

### Verificar Qualidade dos Dados
- [ ] Relatório de qualidade dos dados

---

## Fase 3 — Data Preparation (Preparação dos Dados)

**Como aplicar:** Com base nos problemas encontrados na fase anterior, prepara-se o
dataset que vai entrar nos modelos. A ordem habitual é: (1) seleccionar as variáveis
e registos relevantes; (2) limpar artefactos e valores inválidos; (3) construir
novos atributos calculados (e.g., carga de dessaturação por episódio, médias e
desvios-padrão dos sinais vitais); (4) integrar as duas tabelas num único dataset
por episódio; (5) formatar conforme o que cada algoritmo exige (normalização,
codificação de categorias). Cada decisão deve ser justificada e documentada, pois
afecta directamente a qualidade dos modelos.

### Seleccionar Dados
- [ ] Fundamentação para inclusão/exclusão

### Limpar Dados
- [ ] Relatório de limpeza de dados

### Construir Dados
- [ ] Atributos derivados
- [ ] Registos gerados

### Integrar Dados
- [ ] Dados fundidos (merged data)

### Formatar Dados
- [ ] Dados reformatados
- [ ] Dataset final
- [ ] Descrição do dataset

---

## Fase 4 — Modeling (Modelação)

**Como aplicar:** Escolhem-se os algoritmos mais adequados a cada um dos três
problemas definidos na Fase 1 — agrupamento (k-means ou hierárquico), regressão
(linear, ridge) e classificação (kNN, árvore de decisão). Para cada modelo define-se
previamente uma estratégia de avaliação (plano de teste) que, dada a dimensão
reduzida da amostra (58 episódios), deve ser validação cruzada *leave-one-out*.
Treina-se o modelo, ajustam-se os parâmetros de forma iterativa e registam-se todas
as configurações testadas para garantir a reprodutibilidade.

### Seleccionar Técnica de Modelação
- [ ] Técnica de modelação seleccionada
- [ ] Pressupostos de modelação

### Gerar Plano de Teste
- [ ] Plano de teste (treino/validação)

### Construir Modelo
- [ ] Configurações de parâmetros
- [ ] Modelos construídos
- [ ] Descrição dos modelos

### Avaliar Modelo
- [ ] Avaliação do modelo (model assessment)
- [ ] Configurações de parâmetros revistas

---

## Fase 5 — Evaluation (Avaliação)

**Como aplicar:** Ao contrário da avaliação técnica da Fase 4 (métricas como
índice de silhueta, R² ou exatidão), aqui verifica-se se os modelos aprovados
respondem de facto às perguntas clínicas originais (CS-N1 a CS-N4). Um modelo
tecnicamente razoável pode ser clinicamente inútil — e vice-versa. Faz-se também
uma revisão de processo: houve tarefas omitidas? Os dados foram tratados
correctamente? A fase termina com uma decisão explícita: avançar para Deployment,
repetir uma fase anterior ou iniciar um novo ciclo CRISP-DM.

### Avaliar Resultados
- [ ] Avaliação dos resultados face aos critérios de sucesso de negócio
- [ ] Modelos aprovados

### Rever Processo
- [ ] Revisão do processo (quality assurance)

### Determinar Próximos Passos
- [ ] Lista de acções possíveis
- [ ] Decisão documentada

---

## Fase 6 — Deployment (Implantação)

**Como aplicar:** Para um projeto académico como o AASE, o Deployment não implica
produção de software — implica comunicar os resultados de forma utilizável pelo
serviço de neonatologia. Produz-se um relatório em linguagem clínica (sem jargão
de análise de dados), uma apresentação final e um plano que descreve como o processo
pode ser repetido com dados de épocas futuras. Documenta-se ainda o que correu bem
e o que faria diferente — as lições aprendidas — para reutilização pelo mesmo
analista ou por outros.

### Planear Deployment
- [ ] Plano de deployment

### Planear Monitorização e Manutenção
- [ ] Plano de monitorização e manutenção

### Produzir Relatório Final
- [ ] Relatório final
- [ ] Apresentação final

### Rever Projeto
- [ ] Documentação de experiência (lições aprendidas)
