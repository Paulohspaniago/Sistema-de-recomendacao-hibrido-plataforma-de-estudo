"""Ajusta pesos na validação e avalia o primeiro conteúdo inédito no teste."""
import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

from recomendador import Recomendador, carregar_dados


def divisao_temporal(interacoes):
    corte_validacao = interacoes.data.quantile(0.6)
    corte_teste = interacoes.data.quantile(0.8)
    treino = interacoes[interacoes.data < corte_validacao]
    validacao = interacoes[(interacoes.data >= corte_validacao) & (interacoes.data < corte_teste)]
    teste = interacoes[interacoes.data >= corte_teste]
    if any(parte.empty for parte in (treino, validacao, teste)):
        raise ValueError('Treino, validação e teste devem conter registros em datas distintas.')
    return treino, validacao, teste, corte_validacao, corte_teste


def preparar_exemplos(modelo, futuro, tamanho, semente=42):
    relevantes = futuro[futuro.avaliacao >= 4].groupby('id_aluno').id_material.agg(set)
    elegiveis = []
    for usuario, itens in relevantes.items():
        if usuario not in modelo.historico:
            continue
        vistos = {modelo.grupo_por_id[i] for i in modelo.historico[usuario]}
        verdade = {modelo.grupo_por_id[i] for i in itens} - vistos
        if verdade:
            elegiveis.append((usuario, vistos, verdade))
    rng = np.random.default_rng(semente)
    selecionados = rng.choice(len(elegiveis), min(tamanho, len(elegiveis)), replace=False)
    ids = modelo.materiais.id_material.to_numpy()
    grupos = modelo.materiais['_grupo_conteudo'].to_numpy()
    exemplos = []
    for pos in selecionados:
        usuario, vistos, verdade = elegiveis[pos]
        scores = modelo.scores(usuario)
        candidatos = ~np.isin(grupos, list(vistos))
        exemplos.append((np.column_stack([scores['conteudo'][candidatos], scores['colaborativo'][candidatos], scores['conhecimento'][candidatos]]), ids[candidatos], grupos[candidatos], verdade))
    if not exemplos:
        raise ValueError('Nenhum aluno elegível no período selecionado.')
    return exemplos, len(elegiveis)


def acertos(exemplos, pesos):
    """Acerto no primeiro grupo elegível, com desempate pelo menor ID."""
    valores = []
    for matriz, ids, grupos, verdade in exemplos:
        notas = matriz @ np.asarray(pesos)
        ordem = np.lexsort((ids, -notas))
        valores.append(float(grupos[ordem[0]] in verdade))
    return np.asarray(valores)


def intervalo_bootstrap(valores, semente=42, repeticoes=2000):
    rng = np.random.default_rng(semente)
    medias = np.array([rng.choice(valores, size=len(valores), replace=True).mean() for _ in range(repeticoes)])
    return [float(x) for x in np.quantile(medias, [0.025, 0.975])]


def executar(alunos, materiais, interacoes, usuarios=1000):
    treino, validacao, teste, cv, ct = divisao_temporal(interacoes)
    modelo_validacao = Recomendador(alunos, materiais, treino)
    exemplos_val, elegiveis_val = preparar_exemplos(modelo_validacao, validacao, usuarios)
    # Grade explícita de vetores em passos de 0,2; apenas validação escolhe pesos.
    grade = [tuple(i / 5 for i in p) for p in itertools.product(range(6), repeat=3) if sum(p) == 5]
    avaliacoes = [(float(acertos(exemplos_val, p).mean()), p) for p in grade]
    melhor_val, pesos = max(avaliacoes, key=lambda item: (item[0], item[1]))
    modelo_teste = Recomendador(alunos, materiais, pd.concat([treino, validacao]))
    exemplos_teste, elegiveis_teste = preparar_exemplos(modelo_teste, teste, usuarios)
    candidatos = {'hibrido_ajustado': pesos, 'hibrido_inicial': (0.4, 0.4, 0.2),
                  'conteudo': (1., 0., 0.), 'colaborativo': (0., 1., 0.), 'conhecimento': (0., 0., 1.)}
    resultados = {}
    acertos_teste = {}
    for nome, vetor in candidatos.items():
        hits = acertos(exemplos_teste, vetor)
        acertos_teste[nome] = hits
        resultados[nome] = {'precision_at_1': float(hits.mean()), 'ic_95_bootstrap': intervalo_bootstrap(hits)}
    diferenca = acertos_teste['hibrido_ajustado'] - acertos_teste['hibrido_inicial']
    return {'corte_validacao': str(cv), 'corte_teste': str(ct), 'n_treino': len(treino),
            'n_validacao': len(validacao), 'n_teste': len(teste), 'elegiveis_validacao': elegiveis_val,
            'elegiveis_teste': elegiveis_teste, 'amostra_validacao': len(exemplos_val),
            'amostra_teste': len(exemplos_teste), 'pesos_conteudo_colaborativo_conhecimento': pesos,
            'precision_validacao': melhor_val, 'grade_tamanho': len(grade), 'resultados_teste': resultados,
            'diferenca_ajustado_menos_inicial': {'precision_at_1': float(diferenca.mean()), 'ic_95_bootstrap_pareado': intervalo_bootstrap(diferenca)}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dados', default='data')
    parser.add_argument('--usuarios', type=int, default=1000)
    args = parser.parse_args()
    if args.usuarios < 1:
        parser.error('--usuarios deve ser positivo')
    alunos, materiais, interacoes, _ = carregar_dados(args.dados)
    resultado = executar(alunos, materiais, interacoes, args.usuarios)
    Path('outputs').mkdir(exist_ok=True)
    Path('outputs/validacao_temporal.json').write_text(json.dumps(resultado, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
