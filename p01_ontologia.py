import datetime
start = datetime.datetime.now()

import os
os.system('clear')

################################################################################

from owlready2 import *

################################################################################

onto = get_ontology("http://each.br/amazing_videos.owl")

with onto:
    class Pessoa(Thing): pass

    class Ator(Pessoa): pass
    class Diretor(Pessoa): pass
    class Usuario(Pessoa): pass

    class Titulo(Thing): pass
    class Genero(Thing): pass   
    class Avaliacao(Thing): pass
    class Preferencia(Thing): pass
    class TituloAlternativo(Thing): pass
    class PapelPrincipal(Thing): pass


with onto: 
    class nome(DataProperty, FunctionalProperty): #conjunto name.basics.tsv.gz
        domain = [Pessoa]
        range = [str]

    class ano_nascimento(DataProperty, FunctionalProperty): #conjunto name.basics.tsv.gz
        domain = [Pessoa]
        range = [int]

    class ano_morte(DataProperty, FunctionalProperty): #conjunto name.basics.tsv.gz
        domain = [Pessoa]
        range = [int]

with onto:
    class titulo(DataProperty, FunctionalProperty): #title.basics.tsv.gz
        domain = [Titulo]
        range = [str]

    class ano(DataProperty, FunctionalProperty): #title.basics.tsv.gz
        domain = [Titulo]
        range = [int]

    class nota(DataProperty, FunctionalProperty): #title.ratings.tsv.gz
        domain = [Titulo, Avaliacao]
        range = [float]

    class quantidade_votos(DataProperty, FunctionalProperty): #title.ratings.tsv.gz
        domain = [Titulo]
        range = [int]

    class nome_genero(DataProperty, FunctionalProperty): #title.basics.tsv.gz
        domain = [Genero]
        range = [str]


with onto:
    class nome_usuario(DataProperty, FunctionalProperty): #cadastro de usuários
        domain = [Usuario]
        range = [str]

    class genero_preferido(DataProperty, FunctionalProperty): #cadastro de usuários
        domain = [Preferencia]
        range = [str]

    class nota_usuario(DataProperty, FunctionalProperty): #cadastro de usuários
        domain = [Avaliacao]
        range = [float]

    class avaliador(ObjectProperty): #cadastro de usuários
        domain = [Avaliacao]
        range = [Usuario]

    class filme_avaliado(ObjectProperty): #cadastro de usuários
        domain = [Avaliacao]
        range = [Titulo]


with onto:
    class tem_diretor(ObjectProperty): #title.crew.tsv.gz
        domain = [Titulo]
        range = [Diretor]

    class atua_em(ObjectProperty): #title.principals.tsv.gz
        domain = [Ator]
        range = [Titulo]
 
    class tem_preferencia(ObjectProperty): #cadastro de usuários
        domain = [Usuario]
        range = [Preferencia]

    class realizou_avaliacao(ObjectProperty): #cadastro de usuários
        domain = [Usuario]
        range = [Avaliacao]

    class avaliou(ObjectProperty): #cadastro de usuários
        domain = [Avaliacao]
        range = [Titulo]


    #inversas

    class dirige(ObjectProperty): pass
    tem_diretor.inverse_property = dirige

    class tem_ator(ObjectProperty): pass
    atua_em.inverse_property = tem_ator

    class avaliador(ObjectProperty): pass
    realizou_avaliacao.inverse_property = avaliador

    class foi_avaliado_por(ObjectProperty): pass
    avaliou.inverse_property = foi_avaliado_por

with onto:
    class tem_genero(ObjectProperty):
        domain = [Titulo]
        range = [Genero]

    class tem_avaliacao(ObjectProperty):
        domain = [Titulo]
        range = [Avaliacao]

    class tem_titulo_alternativo(ObjectProperty):
        domain = [Titulo]
        range = [TituloAlternativo]

    class nota_media(DataProperty, FunctionalProperty):
        domain = [Titulo]
        range = [float]

    class total_votos(DataProperty, FunctionalProperty):
        domain = [Titulo]
        range = [int]

    Titulo.is_a.append(tem_genero.min(1, Genero))
    Titulo.is_a.append(tem_avaliacao.min(1, Avaliacao))

    Avaliacao.equivalent_to.append(Avaliacao & (nota_media.exactly(1, float)))


################################################################################

onto.save(file="./ontology/amazing_videos.rdf", format="rdfxml")
onto.save(file="./ontology/amazing_videos.ttl", format="turtle")

print("Ontologia criada e salva com sucesso.")

################################################################################

end = datetime.datetime.now()
time = end - start

hour = str(time.seconds // 3600).zfill(2)
min = str((time.seconds % 3600) // 60).zfill(2)
sec = str(time.seconds % 60).zfill(2)

msg_time = f' Time:{hour}:{min}:{sec} '
print(msg_time.center(80,'#'))

################################################################################