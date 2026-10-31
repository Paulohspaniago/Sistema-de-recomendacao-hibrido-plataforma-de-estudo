# 📚 Recomendação híbrida para uma plataforma de ensino

> Protótipo acadêmico para recomendar materiais didáticos a estudantes do ensino superior, considerando seu perfil e suas interações com a plataforma.

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

Os CSVs foram fornecidos para o projeto e não estão incluídos neste repositório. Dos 10 milhões de registros de interações, apenas **200.622 (2,01%)** possuem simultaneamente identificadores de aluno e material presentes nos respectivos cadastros. Apenas esses registros são usados pelo protótipo.

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

O protótipo combina os escores normalizados com pesos de 40% para conteúdo, 40% para colaborativo e 20% para conhecimento. Estes pesos são escolhas iniciais, não otimizadas. Itens já acessados pelo aluno são removidos do ranking.

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

As métricas online dependem de uma aplicação instrumentada e de usuários ou testes específicos; ainda não foram medidas. O protótipo atual não prevê notas, de modo que RMSE também permanece pendente.

### Primeira avaliação offline

Na execução local com `--usuarios 100 --k 10`, a divisão temporal usou 19/10/2023 como início do teste, considerou relevantes notas ≥ 4 e excluiu itens já vistos no treino. A amostra de alunos foi escolhida com semente 42. Os cinco métodos obtiveram **Precision@10, Recall@10 e F1@10 iguais a zero** nessa amostra. Isso não comprova eficácia; exige investigação e avaliações adicionais. Detalhes e resultados completos estão em [RELATORIO.md](RELATORIO.md).

## ▶️ Executar localmente

Requer Python 3.10 ou superior e os três CSVs originais em `data/`, com seus nomes originais. No diretório do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

O navegador abrirá a demonstração. A primeira leitura percorre os 10 milhões de interações e pode levar algum tempo. Alternativamente, defina `DADOS_DIR` com o caminho da pasta dos CSVs.

Para avaliação e testes:

```bash
python avaliar.py --dados data --usuarios 100 --k 10
python -m unittest discover -s tests -v
```

## 📝 Relatório e entregáveis

- [x] Protótipo com instruções de execução.
- [x] Descrição da arquitetura e comparação inicial das abordagens.
- [ ] Previsão de notas e avaliação RMSE; validação ampliada e melhorias.
- [x] Interface local de demonstração.
- [ ] Capturas de tela reais da demonstração neste README.

## 📖 Referência conceitual

BISPO, Alysson; FALCÃO, Larissa; SOARES, Micael; ROMEIRO, Samuel. *Sistemas de Recomendação*. Material da disciplina IN1152 — Recuperação Inteligente de Informação, Centro de Informática, Universidade Federal de Pernambuco, 2016. Apresentação fornecida para o projeto.

O material apresenta, entre outros temas, filtragem baseada em conteúdo, filtragem colaborativa, contexto e avaliação de sistemas de recomendação. Outras referências serão acrescentadas conforme a escolha dos modelos e protocolos.

## 🖥️ Demonstração

As capturas serão adicionadas aqui após a aplicação estar funcionando. A proposta é mostrar o passo a passo: seleção do estudante, visualização de seu perfil, recomendações e resultados de avaliação. As imagens deverão representar execuções reais do sistema.
