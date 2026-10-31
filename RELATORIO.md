# Relatório técnico — avaliação inicial

## Arquitetura

O carregador lê interações em blocos, mantendo apenas IDs presentes nos cadastros. O modelo vetorial representa título, área, nível, descrição e tipo com TF-IDF; o perfil reúne curso, disciplinas e interesses. O componente colaborativo emprega uma matriz esparsa de avaliações positivas (nota ≥ 4), conta itens positivos compartilhados e soma as contribuições dos até 50 alunos mais semelhantes. O conhecimento soma correspondência textual da área com o perfil e uma bonificação pelo nível aproximado a partir do período. Cada componente é dividido pelo próprio máximo; o híbrido os combina com pesos 0,4, 0,4 e 0,2.

O mapa período–nível é heurístico: até o 3º período, iniciante; do 4º ao 6º, intermediário; depois, avançado. Não são pré-requisitos oficiais. A interface Streamlit permite selecionar um estudante, uma abordagem e a quantidade de materiais.

## Integridade dos dados

Dos 10.000.000 registros de interação, 200.622 têm aluno e material nos cadastros de 10.000 alunos e 10.000 materiais. A exclusão de 97,99% limita fortemente a representatividade do experimento; a causa dos identificadores incompatíveis não foi estabelecida. Não se deve extrapolar os resultados para o conjunto original sem corrigir ou entender sua origem.

## Protocolo e resultados

Na primeira execução, o corte temporal foi 19/10/2023: registros anteriores constituem treino e registros a partir dessa data, teste. Notas ≥ 4 são relevantes; apenas alunos com histórico de treino e ao menos um item relevante novo no teste entram na população elegível. Foram sorteados 100 alunos com semente 42; K = 10. Precision@K usa K como denominador, Recall@K usa os itens relevantes novos e F1 é calculado por aluno e depois agregado. Cobertura é a fração dos 10.000 materiais presente nas listas. Diversidade é a fração de pares de itens recomendados com áreas diferentes, média por aluno.

| Método | Precision@10 | Recall@10 | F1@10 | Diversidade por área | Cobertura |
| --- | ---: | ---: | ---: | ---: | ---: |
| Popularidade | 0,0000 | 0,0000 | 0,0000 | 0,8884 | 0,0011 |
| Conteúdo | 0,0000 | 0,0000 | 0,0000 | 0,0000 | 0,0070 |
| Colaborativo | 0,0000 | 0,0000 | 0,0000 | 0,8624 | 0,0671 |
| Conhecimento | 0,0000 | 0,0000 | 0,0000 | 0,2842 | 0,0050 |
| Híbrido | 0,0000 | 0,0000 | 0,0000 | 0,0229 | 0,0834 |

O resultado zero em todos os métodos na amostra não demonstra eficácia. As diferenças de cobertura e diversidade são descritivas e não substituem relevância. A amostra é pequena e os dados válidos esparsos; outras explicações exigem investigação. O experimento pode ser reproduzido com `python avaliar.py --dados data --usuarios 100 --k 10`.

## Pontos fortes e limitações

- Conteúdo permite tratar itens novos quando há metadados; sua descrição textual pode ser insuficiente e concentrar resultados em uma área.
- Colaborativo usa comportamento real registrado, mas fica limitado pela baixa quantidade de interações válidas e pelo problema de novos alunos e itens.
- Regras de conhecimento são interpretáveis, porém simplificam a relação entre período, disciplina e dificuldade.
- Pesos híbridos são iniciais e não foram ajustados em validação separada.
- O sistema ranqueia itens, mas não prevê notas: RMSE não foi calculado. CTR, engajamento e satisfação também não foram medidos.

## Melhorias

Investigar e corrigir IDs incompatíveis na origem; verificar duplicatas e coerência temporal; ampliar a amostra e calcular intervalos de confiança; ajustar pesos em conjunto de validação separado; testar fatoração e um preditor de avaliações para RMSE; definir regras pedagógicas com especialistas; medir cobertura por grupos e instrumentar eventos online com consentimento.
