import asyncio
import websockets #type:ignore
import json

SERVER_IP = "172.20.10.8"
URI = f"ws://{SERVER_IP}:8002/ws"

async def conectar_bot(id_bot):
    # Cada bot conecta com um ID diferente
    url = f"{URI}/bot_{id_bot}"
    try:
        async with websockets.connect(url) as websocket:
            print(f" Bot {id_bot} conectado.")
            
            msg = {
                "to": "admin", 
                "msg": f"Mensagem de teste de carga do Bot {id_bot}"
            }
            await websocket.send(json.dumps(msg))
            await asyncio.sleep(2)
            
    except Exception as e:
        print(f" Erro no Bot {id_bot}: {e}")

async def teste_carga():
    print(f"--- Iniciando Teste de Carga (10 Usuários Simultâneos) ---")
    # Cria 10 tarefas simultâneas 
    tasks = []
    for i in range(1, 11):
        tasks.append(conectar_bot(i))
    
    # Executa todas ao mesmo tempo
    await asyncio.gather(*tasks)
    print("--- Teste Finalizado ---")

if __name__ == "__main__":
    asyncio.run(teste_carga())