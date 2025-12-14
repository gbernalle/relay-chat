from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
from motor.motor_asyncio import AsyncIOMotorClient
import os
import json
import asyncio

app = FastAPI()

# Configurações
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

# Conexões
r = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client.chat_db
messages_collection = db.messages

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Gerenciador de Conexões Locais
class ConnectionManager:
    def __init__(self):
        # Mapeia user_id -> WebSocket (apenas para conexões nesta instância do servidor)
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)


manager = ConnectionManager()


# Background Task: Escutar Redis e enviar para WebSocket Local
async def redis_listener(user_id: str):
    pubsub = r.pubsub()
    await pubsub.subscribe(f"user:{user_id}")
    async for message in pubsub.listen():
        if message["type"] == "message":
            # Se chegou mensagem no Redis para este usuário, envia via WebSocket
            await manager.send_personal_message(message["data"], user_id)


@app.get("/history/{user1}/{user2}")
async def get_history(user1: str, user2: str):
    # Busca mensagens onde (remetente=u1 E destinatario=u2) OU (remetente=u2 E destinatario=u1)
    cursor = messages_collection.find(
        {"$or": [{"from": user1, "to": user2}, {"from": user2, "to": user1}]}
    ).sort(
        "timestamp", 1
    )  # Ordena por tempo

    msgs = []
    async for document in cursor:
        msgs.append({"from": document["from"], "content": document["content"]})
    return msgs


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)

    # Inicia listener do Redis para este usuário em background
    listener_task = asyncio.create_task(redis_listener(user_id))

    try:
        while True:
            data = await websocket.receive_text()
            # Espera formato JSON: {"to": "destinatario", "msg": "conteudo"}
            message_data = json.loads(data)
            to_user = message_data["to"]
            content = message_data["msg"]

            # Persistir no MongoDB
            await messages_collection.insert_one(
                {
                    "from": user_id,
                    "to": to_user,
                    "content": content,
                    "timestamp": asyncio.get_event_loop().time(),
                }
            )

            # Enviar para o Redis (canal do destinatário)
            # Isso garante que mesmo se o destinatário estiver em OUTRO container, ele receba.
            payload = json.dumps({"from": user_id, "content": content})
            await r.publish(f"user:{to_user}", payload)

            await websocket.send_text(json.dumps({"from": "eu", "content": content}))

    except WebSocketDisconnect:
        manager.disconnect(user_id)
        listener_task.cancel()
    except Exception as e:
        print(f"Erro: {e}")
