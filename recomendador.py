"""Recomendação educacional: conteúdo, conhecimento e coocorrência colaborativa."""
from pathlib import Path
import re
import unicodedata

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


def normalizar(valor):
    texto = unicodedata.normalize('NFKD', str(valor).lower())
    return ''.join(c for c in texto if not unicodedata.combining(c))


def carregar_dados(pasta):
    pasta = Path(pasta)
    alunos = pd.read_csv(pasta / 'dados_alunos.csv').fillna('')
    materiais = pd.read_csv(pasta / 'materiais_didaticos.csv').fillna('')
    partes = []
    total = 0
    for bloco in pd.read_csv(pasta / 'interacoes.csv', chunksize=300_000):
        total += len(bloco)
        valido = bloco.id_aluno.isin(alunos.id_aluno) & bloco.id_material.isin(materiais.id_material)
        partes.append(bloco.loc[valido].copy())
    interacoes = pd.concat(partes, ignore_index=True)
    interacoes['data'] = pd.to_datetime(interacoes['data'], errors='coerce')
    interacoes = interacoes.dropna(subset=['data', 'avaliacao'])
    return alunos, materiais, interacoes, total


class Recomendador:
    def __init__(self, alunos, materiais, interacoes):
        self.alunos = alunos.set_index('id_aluno', drop=False)
        self.materiais = materiais.reset_index(drop=True).copy()
        colunas_grupo = ['titulo', 'tipo', 'area', 'nivel', 'descricao', 'autor']
        self.materiais['_grupo_conteudo'] = pd.factorize(pd.MultiIndex.from_frame(
            self.materiais[colunas_grupo].fillna('').astype(str)
        ))[0]
        self.grupo_por_id = dict(zip(self.materiais.id_material, self.materiais['_grupo_conteudo']))
        self.interacoes = interacoes.copy()
        self.item_pos = {int(v): i for i, v in enumerate(self.materiais.id_material)}
        self.user_ids = sorted(self.alunos.index.tolist())
        self.user_pos = {int(v): i for i, v in enumerate(self.user_ids)}
        textos = self.materiais[['titulo', 'area', 'nivel', 'descricao', 'tipo']].fillna('').astype(str).agg(' '.join, axis=1).map(normalizar)
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
        self.item_vectors = self.vectorizer.fit_transform(textos)
        self.areas_normalizadas = self.materiais.area.map(normalizar).to_numpy()
        self.niveis_normalizados = self.materiais.nivel.map(normalizar).to_numpy()
        self.palavras_por_area = {area: set(re.findall(r'\w+', area)) for area in set(self.areas_normalizadas)}
        inter = self.interacoes
        self.historico = inter.groupby('id_aluno')['id_material'].agg(set).to_dict()
        positivos = inter[inter.avaliacao >= 4].drop_duplicates(['id_aluno', 'id_material'])
        rows = positivos.id_aluno.map(self.user_pos).to_numpy(dtype=int)
        cols = positivos.id_material.map(self.item_pos).to_numpy(dtype=int)
        self.matriz = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(len(self.user_ids), len(self.materiais)))
        self.popularidade = np.asarray(self.matriz.sum(axis=0)).ravel()

    @staticmethod
    def escala(x):
        x = np.asarray(x, dtype=float)
        return x / x.max() if len(x) and x.max() > 0 else np.zeros_like(x)

    def scores(self, aluno_id):
        if aluno_id not in self.alunos.index:
            raise ValueError('Aluno não encontrado.')
        aluno = self.alunos.loc[aluno_id]
        perfil = normalizar(' '.join(str(aluno[c]) for c in ['curso', 'disciplinas_cursadas', 'areas_interesse']))
        conteudo = linear_kernel(self.vectorizer.transform([perfil]), self.item_vectors).ravel()
        user = self.user_pos[aluno_id]
        # Vizinhos dividem itens bem avaliados; evita matriz densa usuário × usuário.
        similaridades = (self.matriz @ self.matriz[user].T).tocoo()
        vizinhos = [(int(i), float(v)) for i, v in zip(similaridades.row, similaridades.data) if i != user and v > 0]
        vizinhos = sorted(vizinhos, key=lambda x: -x[1])[:50]
        colaborativo = np.zeros(len(self.materiais))
        if vizinhos:
            indices, pesos = zip(*vizinhos)
            colaborativo = np.asarray(self.matriz[list(indices)].T @ np.asarray(pesos)).ravel()
        palavras = set(re.findall(r'\w+', perfil))
        nivel = pd.to_numeric(pd.Series([aluno['periodo']]), errors='coerce').fillna(1).iloc[0]
        esperado = 'iniciante' if nivel <= 3 else 'intermediario' if nivel <= 6 else 'avancado'
        areas_relevantes = {area for area, tokens in self.palavras_por_area.items() if tokens & palavras}
        conhecimento = np.isin(self.areas_normalizadas, list(areas_relevantes)).astype(float)
        conhecimento += 0.3 * (self.niveis_normalizados == esperado)
        return {'popularidade': self.escala(self.popularidade), 'conteudo': self.escala(conteudo), 'colaborativo': self.escala(colaborativo), 'conhecimento': self.escala(conhecimento)}

    def recomendar(self, aluno_id, metodo='hibrido', k=10, scores=None, conteudos_unicos=False):
        if k < 1:
            raise ValueError('k deve ser positivo.')
        scores = self.scores(aluno_id) if scores is None else scores
        if metodo == 'hibrido':
            score = 0.4 * scores['conteudo'] + 0.4 * scores['colaborativo'] + 0.2 * scores['conhecimento']
        elif metodo in scores:
            score = scores[metodo].copy()
        else:
            raise ValueError('Método desconhecido.')
        resultado = self.materiais.copy()
        resultado['score'] = score
        resultado = resultado[~resultado.id_material.isin(self.historico.get(aluno_id, set()))]
        resultado = resultado.sort_values(['score', 'id_material'], ascending=[False, True])
        if conteudos_unicos:
            vistos = {self.grupo_por_id[i] for i in self.historico.get(aluno_id, set())}
            resultado = resultado[~resultado['_grupo_conteudo'].isin(vistos)]
            resultado = resultado.drop_duplicates('_grupo_conteudo')
        return resultado.head(k)
