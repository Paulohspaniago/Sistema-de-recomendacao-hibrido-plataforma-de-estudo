# 📚 Recomendação híbrida para uma plataforma de ensino

> Projeto acadêmico em desenvolvimento para recomendar materiais didáticos a estudantes do ensino superior, considerando seu perfil e suas interações com a plataforma.

## 🎯 Objetivo

Ajudar cada estudante a descobrir livros, artigos, vídeos e outros materiais relevantes para sua trajetória acadêmica. O projeto combina três perspectivas: características dos materiais e do aluno, padrões de interação de alunos e regras pedagógicas aproximadas.

## 📋 Escopo do projeto

O sistema deverá:

1. Carregar e examinar os dados de estudantes, materiais e interações.
2. Gerar recomendações usando conteúdo, filtragem colaborativa e conhecimento pedagógico.
3. Combinar e comparar as abordagens com uma estratégia híbrida.
4. Avaliar qualidade, cobertura e diversidade das recomendações.
5. Apresentar uma demonstração funcional e documentar resultados e limitações.

## 🗃️ Dados disponíveis

| Arquivo | Conteúdo | Volume informado pelos arquivos |
| --- | --- | ---: |
| `dados_alunos.csv` | Identificador, nome, curso, período, disciplinas cursadas e áreas de interesse | 10.000 registros |
| `materiais_didaticos.csv` | Identificador, título, tipo, área, nível, descrição e autor | 10.000 registros |
| `interacoes.csv` | Identificadores do aluno e do material, tipo de interação, avaliação, duração e data | 10.000.000 registros |

Os CSVs foram fornecidos para o projeto e ainda não estão incluídos neste repositório. As contagens acima correspondem às linhas dos arquivos originais; integridade, duplicidades e correspondência entre identificadores ainda serão verificadas.

> O arquivo de interações tem aproximadamente 445 MiB. A estratégia para armazená-lo e disponibilizá-lo deverá ser definida antes de adicioná-lo ao GitHub. Dados de estudantes devem ser tratados com cuidado: nomes não são necessários para treinar os modelos.

## 🧩 Abordagens de recomendação

### 1. Baseada em conteúdo

Relacionar os atributos dos materiais — como descrição, área, tipo e nível — aos interesses, curso e histórico do estudante. Uma possibilidade é representar textos com TF-IDF e calcular similaridade de cosseno. A implementação e os atributos utilizados serão definidos e avaliados durante o desenvolvimento.

### 2. Filtragem colaborativa

Identificar padrões nas interações entre estudantes e materiais para sugerir itens que alunos com comportamentos semelhantes acessaram ou avaliaram positivamente. Avaliações e sinais implícitos, como visualizações e tempo gasto, têm significados distintos e precisarão de tratamento documentado.

Como a base é volumosa, o processamento deverá considerar estruturas esparsas ou leitura em partes, evitando pressupor que uma matriz densa seja adequada.

### 3. Conhecimento pedagógico aproximado

Usar **curso, período, disciplinas cursadas e áreas de interesse** como indícios para estimar a pertinência de um material e de seu nível. Essas regras serão aproximações explícitas: os arquivos apresentados não fornecem uma matriz formal de pré-requisitos nem notas por disciplina.

### 4. Modelo híbrido

Combinar os resultados das três abordagens em um ranking. Pesos, normalização, tratamento de alunos ou materiais novos e justificativas serão definidos e comparados experimentalmente.

## 📊 Avaliação planejada

| Tipo | Métrica | Finalidade |
| --- | --- | --- |
| Offline | Precision@K, Recall@K e F1@K | Avaliar a relevância dos itens recomendados entre os primeiros K resultados |
| Offline | RMSE | Medir o erro quando houver previsão de avaliações na mesma escala das notas observadas |
| Offline | Cobertura do catálogo | Medir a proporção de materiais distintos recomendados |
| Offline | Diversidade | Medir a variedade entre itens recomendados, conforme definição documentada |
| Online | CTR | Medir a proporção de recomendações exibidas que recebem cliques |
| Online | Tempo de engajamento | Observar o tempo de interação após a recomendação |
| Online | Pesquisa de satisfação | Coletar a percepção dos estudantes sobre as recomendações |

A avaliação offline deverá usar um protocolo de treino e teste documentado, preferencialmente respeitando as datas das interações para evitar acesso a informações futuras. A definição de relevância, os valores de K e os modelos de referência serão registrados com os resultados.

As métricas online dependem de uma aplicação instrumentada e de usuários ou testes específicos. **Nenhum resultado online ou offline foi medido ainda.**

## 📝 Relatório e entregáveis

- [ ] Código-fonte completo e instruções de execução.
- [ ] Descrição da arquitetura e das decisões de modelagem.
- [ ] Comparação das métricas entre abordagens e baselines.
- [ ] Análise de pontos fortes, limitações e melhorias.
- [ ] Demonstração funcional do sistema.
- [ ] Capturas de tela reais da demonstração neste README.

## 📖 Referência conceitual

BISPO, Alysson; FALCÃO, Larissa; SOARES, Micael; ROMEIRO, Samuel. *Sistemas de Recomendação*. Material da disciplina IN1152 — Recuperação Inteligente de Informação, Centro de Informática, Universidade Federal de Pernambuco, 2016. Apresentação fornecida para o projeto.

O material apresenta, entre outros temas, filtragem baseada em conteúdo, filtragem colaborativa, contexto e avaliação de sistemas de recomendação. Outras referências serão acrescentadas conforme a escolha dos modelos e protocolos.

## 🖥️ Demonstração

As capturas serão adicionadas aqui após a aplicação estar funcionando. A proposta é mostrar o passo a passo: seleção do estudante, visualização de seu perfil, recomendações e resultados de avaliação. As imagens deverão representar execuções reais do sistema.
