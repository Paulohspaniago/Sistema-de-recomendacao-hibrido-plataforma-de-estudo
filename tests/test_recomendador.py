import unittest
import pandas as pd
from recomendador import Recomendador
from avaliar import avaliar_notas


class TestRecomendador(unittest.TestCase):
    def setUp(self):
        alunos = pd.DataFrame([
            dict(id_aluno=1, curso='Programação', periodo=2, disciplinas_cursadas='Python', areas_interesse='IA'),
            dict(id_aluno=2, curso='Programação', periodo=3, disciplinas_cursadas='Python', areas_interesse='IA'),
        ])
        materiais = pd.DataFrame([
            dict(id_material=1, titulo='Python inicial', area='Programação', nivel='Iniciante', descricao='Python básico', tipo='livro'),
            dict(id_material=2, titulo='Inteligência artificial', area='IA', nivel='Iniciante', descricao='Aprendizado de máquina', tipo='artigo'),
            dict(id_material=3, titulo='Gestão', area='Gestão', nivel='Avançado', descricao='Gestão empresarial', tipo='livro'),
        ])
        interacoes = pd.DataFrame([dict(id_aluno=1, id_material=1, avaliacao=5), dict(id_aluno=2, id_material=1, avaliacao=5), dict(id_aluno=2, id_material=2, avaliacao=5)])
        self.modelo = Recomendador(alunos, materiais, interacoes)

    def test_colaborativo_exclui_visto_e_recomenda_coocorrencia(self):
        resultado = self.modelo.recomendar(1, 'colaborativo', 2)
        self.assertNotIn(1, resultado.id_material.tolist())
        self.assertEqual(resultado.iloc[0].id_material, 2)

    def test_usuario_inexistente(self):
        with self.assertRaises(ValueError):
            self.modelo.recomendar(999)

    def test_hibrido_limite(self):
        self.assertEqual(len(self.modelo.recomendar(1, 'hibrido', 1)), 1)

    def test_baseline_notas_usa_somente_media_do_treino(self):
        dados = pd.DataFrame({'data': pd.to_datetime(['2023-01-01'] * 4 + ['2023-12-01']),
                              'id_material': [1, 1, 1, 1, 2], 'avaliacao': [4., 4., 4., 4., 1.]})
        resultados, _ = avaliar_notas(dados)
        self.assertAlmostEqual(resultados.loc[0, 'rmse'], 3.0)
        self.assertAlmostEqual(resultados.loc[1, 'rmse'], 3.0)


if __name__ == '__main__':
    unittest.main()
