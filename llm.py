from openai import OpenAI

MODELO = "qwen3:4b"
URL_OLLAMA = "http://localhost:11434/v1/"

def iniciar_ollama():
    iniciado, ollama = False, None

    try:
        ollama = OpenAI(
            base_url = URL_OLLAMA,
            api_key = "ollama"
        )

        iniciado = True
    except Exception as e:
        print(f"ocorreu um problema iniciando o llm: {e}")

    return iniciado, ollama

def obter_resposta(ollama, mensagens, modelo = MODELO):
    sucesso, resposta = False, None

    try:
        resposta = ollama.chat.completions.create(
            messages = mensagens,
            model = modelo,
            temperature = 0.1
        )
        resposta = resposta.choices[0].message.content

        sucesso = True
    except Exception as e:
        print(f"ocorreu um erro ao obter resposta: {e}")

    return sucesso, resposta

def executar():
    iniciado, ollama = iniciar_ollama()
    if not iniciado: 
        return 
    print("ollama iniciado")

    mensagens = [
        {
            "role": "system",
            "content": "Elabore uma resposta curta para uma saudação. Na sua resposta, você deve se identificar como um sistema especialista dedicado a ensinar programação orientada a objetos"
        },
        {
            "role": "system",
            "content": "O seu nome é ProgBot. Sempre se identifique com esse nome durante saudações"
        },
        {
            "role": "user",
            "content": "olá, tudo bem?"
        }
    ]

    sucesso, resposta = obter_resposta(ollama, mensagens, modelo = "qwen2.5:1.5b")
    if sucesso:
        print(f"resposta do llm: {resposta}")
    else:
        print("não foi possível obter uma resposta do llm")

if __name__ == "__main__":
    executar()