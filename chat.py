from cache import *
from llm import *

import json

NOME_ESPECIALISTA = "ProgBot"
BASE_CONHECIMENTO = "conhecimento/poo.json"
MODELO = "qwen2.5:1.5b"

CACHE = "cache"
MODELO_CACHE = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
NOME_CACHE = "progbot_cache"

def iniciar_persona_assistente(conhecimento):
    persona = [
        {
            "role": "system",
            "content": f"Você é um especialista, perito, em programação orientada a objetos, chamado {NOME_ESPECIALISTA}"
        },
        {
            "role": "system",
            "content": "Se o usuário fizer uma saudação, você deve falar na sua resposta que você é um software, não é um humano, mas que pode ajudar o usuário a entender sobre orientação a objetos"
        }
    ]

    for mensagem, resposta in conhecimento:
        persona.append({
            "role": "system",
            "content": f"Caso o usuário fale ou pergunte '{mensagem}' ou algo parecido, sua resposta deve ser '{resposta}'"
        })

    persona.append(
        {
            "role": "system",
            "content": "Se o usuário te perguntar algo que não esteja relacionado com programação orientada a objeto, você deve dizer 'não posso responder esta pergunta'"
        }
    )

    return persona

def carregar_conhecimento(base_conhecimento = BASE_CONHECIMENTO):
    carregado, conhecimento = False, []

    try:
        with open(base_conhecimento, "r", encoding = "utf-8") as arquivo:
            conteudo = json.load(arquivo)
            arquivo.close()

        for pergunta_resposta in conteudo:
            pergunta = pergunta_resposta["pergunta"]
            resposta = pergunta_resposta["resposta"]

            conhecimento.append((pergunta, resposta))

        carregado = True
    except Exception as e:
        print(f"erro carregando conhecimento: {e}")

    return carregado, conhecimento

def executar():
    iniciado, ollama = iniciar_ollama()
    if not iniciado: 
        return 
    print("ollama iniciado")

    carregado, conhecimento = carregar_conhecimento()
    if not carregado:
        return 
    print("conhecimento carregado")

    iniciado, modelo_cache, colecao_cache = iniciar_cache(MODELO_CACHE, CACHE, NOME_CACHE)
    if not iniciado:
        return
    print("cache iniciado, aguardando mensagens...")

    persona = iniciar_persona_assistente(conhecimento)

    while(True):
        mensagem = input("👤 ")

        encontrada, resposta = buscar_cache(mensagem, modelo_cache, colecao_cache)
        if encontrada:
            print(f"🤖 {resposta} [recuperada do cache]")
        else:
            sucesso, resposta = obter_resposta(ollama, persona + [
                {
                    "role": "user",
                    "content": mensagem
                }
            ], modelo = MODELO)

            if sucesso:
                print(f"🤖 {resposta} [resposta do llm]")

                gravar_cache(mensagem, resposta, modelo_cache, colecao_cache)
            else:
                print(f"🤖 não sei responder esta pergunta, pergunte outra coisa sobre orientação a objetos")

if __name__ == "__main__":
    executar()
