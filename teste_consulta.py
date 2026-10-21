from database import listar_ingressos

ingressos = listar_ingressos()

for codigo, idade, situacao in ingressos:
    if situacao == "fora":
        print(codigo, idade, situacao)