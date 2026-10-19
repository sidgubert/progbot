import json
from pathlib import Path

from cache import buscar_cache, gravar_cache, iniciar_cache
from llm import iniciar_ollama, obter_resposta

DIRETORIO_BASE = Path(__file__).resolve().parent

NOME_ESPECIALISTA = "ProgBot"
BASE_CONHECIMENTO = DIRETORIO_BASE / "conhecimento" / "poo.json"
MODELO = "qwen2.5:1.5b"

CACHE = DIRETORIO_BASE / "cache"
MODELO_CACHE = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
NOME_CACHE = "progbot_cache"
COMANDOS_SAIDA = {"sair", "exit", "quit"}
RESPOSTA_RECUSA = "não posso responder esta pergunta"


def iniciar_persona_assistente(conhecimento: list[tuple[str, str]]) -> list[dict[str, str]]:
    diretrizes_conhecimento = "\n".join(
        f"- Pergunta: '{pergunta}' -> Resposta: '{resposta}'"
        for pergunta, resposta in conhecimento
    )

    conteudo_sistema = (
        f"Você é um especialista, perito, em programação orientada a objetos, chamado {NOME_ESPECIALISTA}.\n"
        "Regras:\n"
        "1. Se o usuário fizer uma saudação, você deve falar na sua resposta que você é um software, "
        "não é um humano, mas que pode ajudar o usuário a entender sobre orientação a objetos.\n"
        "2. Se o usuário te perguntar algo que não esteja relacionado com programação orientada a objetos, "
        f"você deve dizer '{RESPOSTA_RECUSA}'.\n"
        "3. Caso o usuário fale ou pergunte algo parecido com os itens abaixo, utilize a respectiva resposta:\n"
        f"{diretrizes_conhecimento}"
    )

    return [{"role": "system", "content": conteudo_sistema}]


def carregar_conhecimento(base_conhecimento: Path | str = BASE_CONHECIMENTO) -> tuple[bool, list[tuple[str, str]]]:
    try:
        with open(base_conhecimento, "r", encoding="utf-8") as arquivo:
            conteudo = json.load(arquivo)

        conhecimento = [
            (pergunta_resposta["pergunta"], pergunta_resposta["resposta"])
            for pergunta_resposta in conteudo
        ]

        return True, conhecimento
    except (OSError, json.JSONDecodeError, KeyError) as e:
        print(f"erro carregando conhecimento: {e}")
        return False, []


def executar() -> None:
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
    print("cache iniciado, aguardando mensagens... (digite 'sair' para encerrar)")

    persona = iniciar_persona_assistente(conhecimento)

    try:
        while True:
            mensagem = input("👤 ").strip()
            if not mensagem:
                continue
            if mensagem.lower() in COMANDOS_SAIDA:
                print("🤖 Até logo!")
                break

            encontrada, resposta = buscar_cache(mensagem, modelo_cache, colecao_cache)
            if encontrada:
                print(f"🤖 {resposta} [recuperada do cache]")
                continue

            mensagens = persona + [{"role": "user", "content": mensagem}]
            sucesso, resposta = obter_resposta(ollama, mensagens, modelo=MODELO)

            if sucesso and resposta:
                print(f"🤖 {resposta} [resposta do llm]")

                if RESPOSTA_RECUSA not in resposta.lower():
                    gravar_cache(mensagem, resposta, modelo_cache, colecao_cache)
            else:
                print("🤖 não sei responder esta pergunta, pergunte outra coisa sobre orientação a objetos")
    except (KeyboardInterrupt, EOFError):
        print("\n🤖 Encerrando o ProgBot.")


if __name__ == "__main__":
    executar()
