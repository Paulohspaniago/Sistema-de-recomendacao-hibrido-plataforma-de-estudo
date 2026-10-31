"""Avaliação offline temporal; execute: python avaliar.py --dados data --usuarios 100."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from recomendador import Recomendador, carregar_dados


def avaliar_notas(interacoes):
    """Avalia baselines de média global e média regularizada por material no futuro."""
    corte = interacoes.data.quantile(0.8)
    treino = interacoes[interacoes.data < corte]
    teste = interacoes[interacoes.data >= corte]
    if treino.empty or teste.empty:
        raise ValueError('A divisão temporal precisa conter treino e teste.')
    media = float(treino.avaliacao.mean())
    estatisticas = treino.groupby('id_material').avaliacao.agg(['mean', 'count'])
    regularizacao = 10
    estimativas = (estatisticas['count'] * estatisticas['mean'] + regularizacao * media) / (estatisticas['count'] + regularizacao)
    previsao_item = teste.id_material.map(estimativas).fillna(media)
    verdade = teste.avaliacao.to_numpy(dtype=float)
    resultados = []
    for nome, previsao in [('media_global', np.full(len(teste), media)), ('media_item_regularizada', previsao_item.to_numpy())]:
        erro = verdade - previsao
        resultados.append({'modelo': nome, 'rmse': float(np.sqrt(np.mean(erro ** 2))), 'mae': float(np.mean(np.abs(erro))), 'n_teste': len(teste)})
    return pd.DataFrame(resultados), corte


def avaliar(alunos, materiais, interacoes, k=10, usuarios=100, por_conteudo=False):
    corte = interacoes.data.quantile(0.8)
    treino = interacoes[interacoes.data < corte].copy()
    teste = interacoes[interacoes.data >= corte].copy()
    modelo = Recomendador(alunos, materiais, treino)
    teste = teste[teste.avaliacao >= 4]
    relevantes = teste.groupby('id_aluno').id_material.agg(set).to_dict()
    elegiveis = []
    for usuario, itens in relevantes.items():
        if por_conteudo:
            vistos = {modelo.grupo_por_id[i] for i in modelo.historico.get(usuario, set())}
            novos = {modelo.grupo_por_id[i] for i in itens} - vistos
        else:
            novos = itens - modelo.historico.get(usuario, set())
        if novos and usuario in modelo.user_pos and usuario in modelo.historico:
            elegiveis.append((usuario, novos))
    rng = np.random.default_rng(42)
    escolhidos = rng.choice(len(elegiveis), min(usuarios, len(elegiveis)), replace=False)
    metodos = ['popularidade', 'conteudo', 'colaborativo', 'conhecimento', 'hibrido']
    medidas = {m: [] for m in metodos}
    catalogo = {m: set() for m in metodos}
    comprimentos = {m: [] for m in metodos}
    for pos in escolhidos:
        usuario, verdade = elegiveis[pos]
        scores = modelo.scores(usuario)
        for metodo in metodos:
            rec = modelo.recomendar(usuario, metodo, k, scores=scores, conteudos_unicos=por_conteudo)
            ids = set(rec['_grupo_conteudo'] if por_conteudo else rec.id_material)
            acertos = len(ids & verdade)
            precisao = acertos / k
            recall = acertos / len(verdade)
            f1 = 2 * precisao * recall / (precisao + recall) if precisao + recall else 0
            # Diversidade intra-lista: fração de pares de áreas diferentes.
            areas = rec.area.tolist()
            pares = [(areas[i] != areas[j]) for i in range(len(areas)) for j in range(i + 1, len(areas))]
            medidas[metodo].append((precisao, recall, f1, np.mean(pares) if pares else 0))
            catalogo[metodo].update(ids)
            comprimentos[metodo].append(len(rec))
    linhas = []
    for metodo in metodos:
        media = np.mean(medidas[metodo], axis=0) if medidas[metodo] else [float('nan')] * 4
        total_catalogo = modelo.materiais['_grupo_conteudo'].nunique() if por_conteudo else len(materiais)
        linhas.append(dict(metodo=metodo, precision_at_k=media[0], recall_at_k=media[1], f1_at_k=media[2], diversidade_area=media[3], cobertura=len(catalogo[metodo]) / total_catalogo, tamanho_medio_lista=np.mean(comprimentos[metodo]) if comprimentos[metodo] else float('nan')))
    return pd.DataFrame(linhas), corte, len(escolhidos)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dados', default='data')
    parser.add_argument('--usuarios', type=int, default=100)
    parser.add_argument('--k', type=int, default=10)
    parser.add_argument('--por-conteudo', action='store_true', help='Avalia conteúdos únicos inéditos, em vez de IDs.')
    args = parser.parse_args()
    alunos, materiais, interacoes, total = carregar_dados(args.dados)
    resultado, corte, n = avaliar(alunos, materiais, interacoes, args.k, args.usuarios, por_conteudo=args.por_conteudo)
    print(f'Interações válidas: {len(interacoes):,}/{total:,}; corte temporal: {corte}; alunos avaliados: {n}')
    print(resultado.to_string(index=False))
    Path('outputs').mkdir(exist_ok=True)
    resultado.to_csv('outputs/metricas_conteudo.csv' if args.por_conteudo else 'outputs/metricas.csv', index=False)
    notas, _ = avaliar_notas(interacoes)
    print('\nBaselines de previsão de notas:')
    print(notas.to_string(index=False))
    notas.to_csv('outputs/metricas_notas.csv', index=False)
