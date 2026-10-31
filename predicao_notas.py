"""Preditor de notas por média global e desvios regularizados de aluno e material."""
import pandas as pd


class PreditorVieses:
    def __init__(self, regularizacao_aluno=10.0, regularizacao_material=10.0, iteracoes=10):
        if regularizacao_aluno < 0 or regularizacao_material < 0 or iteracoes < 1:
            raise ValueError('Regularização deve ser não negativa e iterações devem ser positivas.')
        self.regularizacao_aluno = regularizacao_aluno
        self.regularizacao_material = regularizacao_material
        self.iteracoes = iteracoes

    def fit(self, treino):
        if treino.empty:
            raise ValueError('Treino não pode estar vazio.')
        dados = treino[['id_aluno', 'id_material', 'avaliacao']].copy()
        self.media = float(dados.avaliacao.mean())
        self.minimo = float(dados.avaliacao.min())
        self.maximo = float(dados.avaliacao.max())
        self.vies_aluno = pd.Series(dtype=float)
        self.vies_material = pd.Series(dtype=float)
        # Alterna os desvios até estabilizar, usando apenas avaliações do treino.
        for _ in range(self.iteracoes):
            residuo = dados.avaliacao - self.media - dados.id_aluno.map(self.vies_aluno).fillna(0)
            por_item = residuo.groupby(dados.id_material).agg(['sum', 'count'])
            self.vies_material = por_item['sum'] / (por_item['count'] + self.regularizacao_material)
            residuo = dados.avaliacao - self.media - dados.id_material.map(self.vies_material).fillna(0)
            por_aluno = residuo.groupby(dados.id_aluno).agg(['sum', 'count'])
            self.vies_aluno = por_aluno['sum'] / (por_aluno['count'] + self.regularizacao_aluno)
        return self

    def predict(self, pares):
        notas = (self.media + pares.id_aluno.map(self.vies_aluno).fillna(0)
                 + pares.id_material.map(self.vies_material).fillna(0))
        return notas.clip(self.minimo, self.maximo).to_numpy(dtype=float)
