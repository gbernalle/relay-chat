import requests
import asyncio
import websockets
import json
import sys

BASE_IP = "122.85.280.1"

AUTH_URL = f"http://{BASE_IP}:8001"
CHAT_HTTP_URL = f"http://{BASE_IP}:8002"
CHAT_WS_URL = f"ws://{BASE_IP}:8002"

USER_A = "integracao_PessoaA"
USER_B = "integracao_PessoaB"
PASSWORD = "123"


def print_pass(msg):
    print(f"PASS: {msg}")


def print_fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)

def test_auth_flow():
    print(" Teste 1 - Iniciando Teste de Integração: Autenticação")

    payload = {"username": USER_A, "password": PASSWORD}
    requests.post(f"{AUTH_URL}/register", json=payload)

    response = requests.post(f"{AUTH_URL}/login", json=payload)

    if response.status_code == 200:
        print_pass(f"Login realizado com sucesso para {USER_A}")
        return response.json()["username"]
    else:
        print_fail(f"Erro no login: {response.text}")

async def test_chat_flow():
    print("\n Teste 2 - Iniciando Teste de Integração: Envio de Mensagens")

    uri_PessoaA = f"{CHAT_WS_URL}/ws/{USER_A}"
    uri_PessoaB = f"{CHAT_WS_URL}/ws/{USER_B}"

    async with websockets.connect(uri_PessoaA) as ws_PessoaA, websockets.connect(
        uri_PessoaB
    ) as ws_PessoaB:

        print_pass("Conexões WebSocket estabelecidas para PessoaA e PessoaB")

        msg_content = "Olá PessoaB, teste de integração!"
        msg_payload = {"to": USER_B, "msg": msg_content}

        await ws_PessoaA.send(json.dumps(msg_payload))
        print(f"PessoaA enviou: {msg_content}")

        try:
            response = await asyncio.wait_for(ws_PessoaB.recv(), timeout=5.0)
            data = json.loads(response)

            if data["content"] == msg_content and data["from"] == USER_A:
                print_pass(f"PessoaB recebeu corretamente: {data['content']}")
            else:
                print_fail(f"PessoaB recebeu dados incorretos: {data}")

        except asyncio.TimeoutError:
            print_fail("Timeout! PessoaB não recebeu a mensagem (Redis/WebSocket falhou).")

def test_history_flow():
    print("\n Teste 3 - Iniciando Teste de Integração: Persistência/Histórico")

    response = requests.get(f"{CHAT_HTTP_URL}/history/{USER_A}/{USER_B}")

    if response.status_code == 200:
        history = response.json()
        found = any(m["content"] == "Olá PessoaB, teste de integração!" for m in history)

        if found:
            print_pass("Mensagem encontrada no histórico (MongoDB Persistiu!).")
        else:
            print_fail("Histórico retornado mas mensagem não encontrada.")
    else:
        print_fail("Erro ao buscar histórico.")


if __name__ == "__main__":

    test_auth_flow()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_chat_flow())

    test_history_flow()

    print("\n OS TESTES DE INTEGRAÇÃO PASSARAM!")
