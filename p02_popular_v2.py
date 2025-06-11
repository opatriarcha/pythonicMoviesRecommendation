import datetime
start = datetime.datetime.now()

import os
os.system('clear')

################################################################################

import pandas as pd
from owlready2 import *

################################################################################

print(' Ontology load '.center(80,'#'))

onto = get_ontology('./ontology/amazing_videos.rdf').load()

print("Classes existentes:")
for cls in onto.classes():
    print(f"- {cls.name}")

################################################################################

def read_first_n_rows_tsv(filename, n=50):
    chunk_size = 1000
    selected_rows = []

    for chunk in pd.read_csv(filename, sep='\t', dtype=str, na_values='\\N', chunksize=chunk_size):
        valid_chunk = chunk.dropna(how='all')  
        selected_rows.extend(valid_chunk.to_dict(orient='records'))

        if len(selected_rows) >= n:
            break

    return pd.DataFrame(selected_rows[:n])

def limpar_nome(titulo):
    return titulo.strip().lower().replace(" ", "_").replace(":", "").replace(".", "").replace(",", "").replace("'", "").replace('"', "")

df_names = read_first_n_rows_tsv('dados/name.basics.tsv', n=150)
df_titles = read_first_n_rows_tsv('dados/title.basics.tsv', n=150)
df_ratings = read_first_n_rows_tsv('dados/title.ratings.tsv', n=150)

df_ratings['averageRating'] = df_ratings['averageRating'].astype(float)
df_ratings['numVotes'] = df_ratings['numVotes'].astype(int)

for _, row in df_names.iterrows():
    pessoa = onto.Pessoa(f"pessoa_{row['nconst']}")
    if pd.notna(row['primaryName']):
        pessoa.nome = row['primaryName']
    if pd.notna(row['birthYear']) and row['birthYear'].isdigit():
        pessoa.ano_nascimento = int(row['birthYear'])
    if pd.notna(row['deathYear']) and row['deathYear'].isdigit():
        pessoa.ano_morte = int(row['deathYear'])

for _, row in df_titles.iterrows():
    titulo = onto.Titulo(f"titulo_{row['tconst']}")
    
    if pd.notna(row['primaryTitle']):
        titulo.titulo = row['primaryTitle']
    if pd.notna(row['startYear']) and row['startYear'].isdigit():
        titulo.ano = int(row['startYear'])

    if pd.notna(row['genres']):
        for g in row['genres'].split(','):
            nome_genero = g.strip().lower().replace(" ", "_")
            genero = onto.search_one(nome_genero=g.strip())
            if not genero:
                genero = onto.Genero(f"genero_{nome_genero}")
                genero.nome_genero = g.strip()
            titulo.tem_genero.append(genero)

for _, row in df_ratings.iterrows():
    if pd.isna(row['tconst']):
        continue

    # Busca usando tconst original
    titulo = onto.search_one(iri="*titulo_" + row['tconst'])

    if titulo and pd.notna(row['averageRating']):
        titulo.nota = row['averageRating']
        titulo.nota_media = row['averageRating']

    if titulo and pd.notna(row['numVotes']):
        titulo.quantidade_votos = row['numVotes']
        titulo.total_votos = row['numVotes']

    # Opcional: renomear o IRI para incluir o nome do filme
    if titulo and hasattr(titulo, "titulo"):
        nome_limpo = limpar_nome(titulo.titulo[0])
        novo_nome = f"{nome_limpo}_{row['tconst']}"
        titulo.name = novo_nome  # altera o nome da instância


################################################################################

onto.save(file="./ontology/amazing_videos_populated.rdf", format="rdfxml")
onto.save(file='./ontology/amazing_videos_populated.ttl', format='ntriples')
print('\nOntologia salva como "amazing_videos_populated.rdf"\n')

################################################################################

end = datetime.datetime.now()
time = end - start

hour = str(time.seconds // 3600).zfill(2)
min = str((time.seconds % 3600) // 60).zfill(2)
sec = str(time.seconds % 60).zfill(2)

msg_time = f' Time:{hour}:{min}:{sec} '
print(msg_time.center(80,'#'))

################################################################################

