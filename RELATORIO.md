# Relatório técnico — avaliação inicial

## Arquitetura

O carregador lê interações em blocos, mantendo apenas IDs presentes nos cadastros. O modelo vetorial representa título, área, nível, descrição e tipo com TF-IDF; o perfil reúne curso, disciplinas e interesses. O componente colaborativo emprega uma matriz esparsa de avaliações positivas (nota ≥ 4), conta itens positivos compartilhados e soma as contribuições dos até 50 alunos mais semelhantes. O conhecimento soma correspondência textual da área com o perfil e uma bonificação pelo nível aproximado a partir do período. Cada componente é dividido pelo próprio máximo; o híbrido os combina com pesos 0,4, 0,4 e 0,2.

O mapa período–nível é heurístico: até o 3º período, iniciante; do 4º ao 6º, intermediário; depois, avançado. Não são pré-requisitos oficiais. A interface Streamlit permite selecionar um estudante, uma abordagem e a quantidade de materiais.

## Integridade dos dados

Dos 10.000.000 registros de interação, 200.622 têm aluno e material nos cadastros de 10.000 alunos e 10.000 materiais. As interações utilizam IDs de aluno de 1 a 100.000 e de material de 1 a 50.000; ambos os cadastros disponíveis vão de 1 a 10.000. Separadamente, 1.000.280 interações têm aluno cadastrado e 1.999.550 têm material cadastrado. Isso identifica a incompatibilidade de faixas, mas não estabelece por que os cadastros estão incompletos. A exclusão de 97,99% limita fortemente a representatividade do experimento.

Os cadastros repetem intensamente os atributos: existem apenas oito combinações de curso, período, disciplinas e interesses entre os alunos, e dez combinações de título, tipo, área, nível, descrição e autor entre os materiais. IDs distintos podem representar materiais textualmente idênticos. A avaliação por ID pode considerar incorreta uma recomendação de conteúdo igual ao de um item relevante com outro ID; a exclusão de itens vistos também funciona por ID. Não se deve interpretar a cobertura por ID como diversidade de conteúdos únicos.

## Protocolo e resultados

Na execução ampliada, o corte temporal foi 19/10/2023: registros anteriores constituem treino e registros a partir dessa data, teste. Notas ≥ 4 são relevantes; apenas alunos com histórico de treino e ao menos um item relevante novo no teste entram na população elegível. Foram sorteados 1.000 alunos com semente 42; K = 10. Precision@K usa K como denominador, Recall@K usa os itens relevantes novos e F1 é calculado por aluno e depois agregado. Cobertura é a fração dos 10.000 IDs de materiais presente nas listas. Diversidade é a fração de pares de itens recomendados com áreas diferentes, média por aluno.

| Método | Precision@10 | Recall@10 | F1@10 | Diversidade por área | Cobertura |
| --- | ---: | ---: | ---: | ---: | ---: |
| Popularidade | 0,0002 | 0,000533 | 0,000287 | 0,888467 | 0,0011 |
| Conteúdo | 0,0002 | 0,000583 | 0,000297 | 0,000000 | 0,0076 |
| Colaborativo | 0,0001 | 0,000500 | 0,000167 | 0,860600 | 0,3304 |
| Conhecimento | 0,0003 | 0,001083 | 0,000463 | 0,293022 | 0,0054 |
| Híbrido | 0,0002 | 0,000667 | 0,000308 | 0,023800 | 0,3721 |

Os valores de relevância são muito baixos. As diferenças de cobertura e diversidade são descritivas e não substituem relevância. Os dados válidos são esparsos e os metadados repetidos comprometem a interpretação; outras explicações exigem investigação. O experimento pode ser reproduzido com `python avaliar.py --dados data --usuarios 1000 --k 10`.

### Predição de notas: baselines

Usando o mesmo corte temporal e as 40.588 avaliações válidas do teste, a média global do treino obteve RMSE **1,410032** e MAE **1,195691**. A média por material regularizada com 10 observações equivalentes à média global obteve RMSE **1,426248** e MAE **1,229349**. Materiais desconhecidos no treino recebem a média global. Esses são baselines independentes, não previsões de notas do modelo híbrido.

## Pontos fortes e limitações

- Conteúdo permite tratar itens novos quando há metadados; sua descrição textual pode ser insuficiente e concentrar resultados em uma área.
- Colaborativo usa comportamento real registrado, mas fica limitado pela baixa quantidade de interações válidas e pelo problema de novos alunos e itens.
- Regras de conhecimento são interpretáveis, porém simplificam a relação entre período, disciplina e dificuldade.
- Pesos híbridos são iniciais e não foram ajustados em validação separada.
- O híbrido ranqueia itens e não prevê notas; os valores de RMSE são de baselines independentes. CTR, engajamento e satisfação não foram medidos.

## Melhorias

Investigar e corrigir IDs incompatíveis na origem; verificar duplicatas e coerência temporal; ampliar a amostra e calcular intervalos de confiança; ajustar pesos em conjunto de validação separado; testar fatoração e um preditor de avaliações para RMSE; definir regras pedagógicas com especialistas; medir cobertura por grupos e instrumentar eventos online com consentimento.
