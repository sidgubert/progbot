from chat import *
from llm import *

MODELO_ASSISTENTE = "qwen2.5:3b"
MODELO_JULGAMENTO = "qwen3:4b" 

def iniciar_persona_julgamento(conhecimento):
    persona = [
        {
            "role": "system",
            "content": f"Você é um especialista, perito, em programação orientada a objetos"
        },
        {
            "role": "system",
            "content": "Sua função é avaliar se uma determinada resposta responde adequadamente uma pergunta sobre programação orientada a objetos"
        }
    ]

    for mensagem, resposta in conhecimento:
        persona.append({
            "role": "system",
            "content": f"Caso a pergunta seja '{mensagem}' ou algo parecido, você deve verificar se a resposta é '{resposta}' ou algo parecido"
        })

    persona.append(
        {
            "role": "system",
            "content": "A sua resposta deve conter APENAS uma string que informe, 'ATENDE', se a resposta responde a pergunta e 'NÃO ATENDE' se a resposta não responde a pergunta. Não é necessário explicar o seu julgamento."
        }
    )

    return persona

def avaliar_alucinacoes(ollama, julgador):
    alucinacoes = [
        {
            "pergunta": "O que é Programação Orientada a Objetos?",
            "resposta": "É um tipo de pássaro que viaja para o sul no inverno"
        },
        {
            "pergunta": "O que é uma classe?",
            "resposta": "É um tipo de comida que serve para alimentar pássaros"
        }
    ]

    for alucinacao in alucinacoes:
        pergunta = alucinacao["pergunta"]
        resposta = alucinacao["resposta"]

        print(f"julgando a resposta '{resposta}' para a pergunta '{pergunta}'")

        sucesso, julgamento = obter_resposta(ollama, julgador + [
            {
                "role": "user",
                "content": f"pergunta '{pergunta}', resposta '{resposta}'"
            }
        ], modelo = MODELO_JULGAMENTO)
        assert(sucesso == True)

        print(f"resposta do julgador: {julgamento}")
        assert("NÃO ATENDE" in julgamento)

        print("👍👍 a alucinação foi julgada insatisfatória 👍👍")

def julgar_assistente(ollama, conhecimento, assistente, julgador):
    for pergunta, _ in conhecimento:
        sucesso, resposta = obter_resposta(ollama, assistente + [
            {
                "role": "user",
                "content": pergunta
            }
        ], modelo = MODELO_ASSISTENTE)
        assert(sucesso == True)

        print(f"julgando a resposta '{resposta}' para a pergunta '{pergunta}'")

        sucesso, julgamento = obter_resposta(ollama, julgador + [
            {
                "role": "user",
                "content": f"pergunta '{pergunta}', resposta '{resposta}'"
            }
        ], modelo = MODELO_JULGAMENTO)
        assert(sucesso == True)

        print(f"resposta do julgador: {julgamento}")
        assert("NÃO ATENDE" not in julgamento)

        print("👍👍 a resposta do assistente foi julgada satisfatória 👍👍")


if __name__ == "__main__":
    iniciado, ollama = iniciar_ollama()
    assert(iniciado == True)

    carregado, conhecimento = carregar_conhecimento()
    assert(carregado == True)

    julgador = iniciar_persona_julgamento(conhecimento)
    assistente = iniciar_persona_assistente(conhecimento)

    avaliar_alucinacoes(ollama, julgador)
    julgar_assistente(ollama, conhecimento, assistente, julgador)

    print("👍👍 julgamento finalizando com sucesso! 👍👍")