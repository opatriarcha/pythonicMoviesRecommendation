import streamlit as st
from owlready2 import get_ontology

# Funções auxiliares
def normalizar_nome(nome):
    return nome.strip().lower().replace(" ", "_").replace("/", "_")

def obter_valor_propriedade(prop):
    try:
        return prop if isinstance(prop, str) else prop[0]
    except:
        return ""

# Caminho da ontologia
ONTO_PATH = "./ontology/amazing_videos_populated_v3.rdf"

def carregar_ontologia():
    return get_ontology(ONTO_PATH).load()

onto = carregar_ontologia()

# Configuração do Streamlit
st.set_page_config(page_title="Cadastro de Usuário", layout="centered")
st.title("\U0001F464 Cadastro de Usuário")

# Cadastro ou atualização de usuário
nome_usuario = st.text_input("Nome do usuário")

# Gêneros disponíveis na ontologia
generos = sorted(set(
    obter_valor_propriedade(g.nome_genero)
    for g in onto.Genero.instances() if hasattr(g, "nome_genero")
))
generos_selecionados = st.multiselect("Selecione um ou mais gêneros de interesse", generos)

if st.button("Salvar usuário"):
    if nome_usuario and generos_selecionados:
        id_usuario = f"usuario_{normalizar_nome(nome_usuario)}"
        usuario_existente = onto.search_one(iri="*" + id_usuario)

        if usuario_existente:
            usuario_existente.nome = nome_usuario
            usuario_existente.tem_preferencia.clear()
        else:
            usuario_existente = onto.Usuario(id_usuario)
            usuario_existente.nome = nome_usuario

        for genero_nome in generos_selecionados:
            nova_pref = onto.Preferencia(f"preferencia_{normalizar_nome(nome_usuario)}_{normalizar_nome(genero_nome)}")
            nova_pref.genero_preferido = genero_nome
            usuario_existente.tem_preferencia.append(nova_pref)

        onto.save(file=ONTO_PATH, format="rdfxml")
        st.success(f"Usuário **{nome_usuario}** cadastrado/atualizado com os gêneros: {', '.join(generos_selecionados)}")

        onto = carregar_ontologia()
    else:
        st.warning("⚠️ Informe o nome e selecione pelo menos um gênero.")

# ------------------------------------------------------------------------------
# Exibir filmes de acordo com os gêneros preferidos do usuário
st.markdown("---")
st.header("\U0001F3A5 Recomendações por Gênero de Interesse")

usuarios_disponiveis = sorted(
    [(u.name, obter_valor_propriedade(u.nome)) for u in onto.Usuario.instances()],
    key=lambda x: x[1]
)

usuario_selecionado_nome = st.selectbox("Selecione um usuário para ver filmes recomendados", [n for _, n in usuarios_disponiveis])
usuario_instancia = next((onto.search_one(iri="*" + uid) for uid, nome in usuarios_disponiveis if nome == usuario_selecionado_nome), None)

modo_busca = st.radio("Modo de recomendação:", ["Com base no gênero preferido", "Todos os filmes"])

if st.button("Buscar filmes recomendados"):
    if usuario_instancia:
        filmes_filtrados = []

        if modo_busca == "Com base no gênero preferido" and hasattr(usuario_instancia, "tem_preferencia"):
            generos_usuario = list(set(
                obter_valor_propriedade(p.genero_preferido)
                for p in usuario_instancia.tem_preferencia
                if hasattr(p, "genero_preferido") and p.genero_preferido
            ))
        else:
            generos_usuario = []  # irá retornar todos os filmes

        for filme in onto.Titulo.instances():
            if hasattr(filme, "tem_genero"):
                generos_filme = list(set(
                    obter_valor_propriedade(g.nome_genero)
                    for g in filme.tem_genero if hasattr(g, "nome_genero")
                ))
                if not generos_usuario or any(g in generos_usuario for g in generos_filme):
                    nome_filme = obter_valor_propriedade(filme.titulo) if hasattr(filme, "titulo") else filme.name
                    nota_filme = float(filme.nota) if hasattr(filme, "nota") and filme.nota else 0.0
                    filmes_filtrados.append((nome_filme, generos_filme, nota_filme))

        if filmes_filtrados:
            filmes_ordenados = sorted(filmes_filtrados, key=lambda x: x[2], reverse=True)
            st.subheader("\U0001F3AC Filmes recomendados:")
            for nome, gs, nota in filmes_ordenados:
                st.markdown(f"- **{nome}** — *{', '.join(gs)}* — Nota: **{nota:.1f}**")
        else:
            st.info("Nenhum filme encontrado para os critérios selecionados.")
    else:
        st.warning("Usuário inválido ou não encontrado.")
