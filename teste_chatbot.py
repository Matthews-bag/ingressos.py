
from chatbot import perguntar

while True:
    pergunta = input("\nVocê: ")

    if pergunta.lower() in {"sair", "exit"}:
        break

    try:
        resposta = perguntar(pergunta)
        print("\nEvent Control:", resposta)
    except Exception as erro:
        print("\nErro ao consultar o Gemini:", erro)
