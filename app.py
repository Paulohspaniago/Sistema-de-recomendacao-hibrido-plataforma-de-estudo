"""Demonstração local: streamlit run app.py."""
import os
import streamlit as st
from recomendador import Recomendador, carregar_dados

st.set_page_config(page_title='Trilhas de Estudo', page_icon='📚', layout='wide')
st.title('📚 Trilhas de Estudo')
st.caption('Recomendação híbrida de materiais didáticos para o ensino superior')


@st.cache_resource
def iniciar(pasta):
    alunos, materiais, interacoes, total = carregar_dados(pasta)
    return alunos, materiais, interacoes, total, Recomendador(alunos, materiais, interacoes)


pasta = os.environ.get('DADOS_DIR', 'data')
try:
    alunos, materiais, interacoes, total, modelo = iniciar(pasta)
except FileNotFoundError as exc:
    st.error(f'Arquivo não encontrado: {exc}. Coloque os três CSVs na pasta data/ ou defina DADOS_DIR.')
    st.stop()

st.sidebar.header('Perfil do estudante')
aluno_id = st.sidebar.selectbox('Aluno', alunos.id_aluno, format_func=lambda i: f'{i} — {modelo.alunos.loc[i, "nome"]}')
aluno = modelo.alunos.loc[aluno_id]
st.sidebar.write(f"**Curso:** {aluno['curso']}")
st.sidebar.write(f"**Período:** {aluno['periodo']}")
st.sidebar.write(f"**Disciplinas:** {aluno['disciplinas_cursadas']}")
st.sidebar.write(f"**Interesses:** {aluno['areas_interesse']}")
st.sidebar.caption(f'{len(interacoes):,} de {total:,} interações com referências válidas.')

metodos = {'Híbrido': 'hibrido', 'Conteúdo': 'conteudo', 'Colaborativo': 'colaborativo', 'Conhecimento': 'conhecimento', 'Popularidade': 'popularidade'}
selecao = st.selectbox('Abordagem', list(metodos))
k = st.slider('Quantidade de materiais', 1, 20, 10)
unicos = st.checkbox('Mostrar apenas conteúdos distintos ainda não vistos', value=True)
recomendacoes = modelo.recomendar(int(aluno_id), metodos[selecao], k, conteudos_unicos=unicos)
st.subheader(f'Recomendações para {aluno["nome"]}')
if recomendacoes.empty:
    st.info('Não encontramos conteúdos novos para este estudante na base disponível.')
elif len(recomendacoes) < k:
    st.info(f'A base contém apenas {len(recomendacoes)} conteúdos inéditos para este estudante.')
st.dataframe(recomendacoes[['titulo', 'tipo', 'area', 'nivel', 'autor', 'score']], hide_index=True, use_container_width=True)
st.caption('As regras de conhecimento são aproximações; não representam pré-requisitos oficiais. As recomendações usam apenas interações com aluno e material cadastrados.')
