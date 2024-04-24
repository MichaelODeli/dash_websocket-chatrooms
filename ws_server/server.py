import ast
import asyncio
from collections import defaultdict
from quart import Quart, websocket
from datetime import datetime

app = Quart(__name__)

websocket_rooms = defaultdict(set)
rooms_and_clients = {}


async def send_task(ws, queue):
    while True:
        message = await queue.get()
        await ws.send(message)

# @app.websocket("/ws/get_rooms")
# async def get_rooms():
#     global rooms_and_clients
#     await websocket.accept()
#     while True:
#         msg = await websocket.receive()
#         await websocket.send(str())

@app.websocket("/ws/<room_id>/<client_id>")
async def ws(room_id, client_id):
    # мониторинг клиентов и комнат
    global rooms_and_clients
    if room_id not in rooms_and_clients:
        # если нет комнаты - создаем ее в словаре
        now = str(datetime.now())
        rooms_and_clients[room_id] = {
            "clients": [client_id],
            "created": now,
            "last_message": "",
        }
        print(f"new room {room_id}")
    else:
        # комната есть - добавляем нового участника в словарь
        if client_id not in rooms_and_clients[room_id]["clients"]:
            rooms_and_clients[room_id]["clients"].append(client_id)
            print(f"user {client_id} connected to room {room_id}")

    global websocket_rooms
    queue = asyncio.Queue()
    websocket_rooms[room_id].add(queue)
    try:
        task = asyncio.ensure_future(send_task(websocket._get_current_object(), queue))
        while True:
            message = await websocket.receive() # получили сообщение
            now_msg = str(datetime.now())
            rooms_and_clients[room_id]["last_connect"] = now_msg # сохраниои дату последней активности в комнате

            msg_dict = ast.literal_eval(message) # форматируем сообщение в словарь (безопасно)
            clients = ",".join(rooms_and_clients[room_id]["clients"]) # сохраняем клиентов в словарь
            msg_dict['clients-in-room'] = clients
            
            
            # print(msg_dict)
            if msg_dict["task"] == "send":
                for other in websocket_rooms[room_id]:
                    # пришло сообщение - ответная рассылка его всем участникам комнаты
                    if other is not queue:
                        await other.put(str(msg_dict))
            elif msg_dict["task"] == "connect_handle":
                # подключен клиент - рассылка уведомления всем
                for other in websocket_rooms[room_id]:
                    if other is not queue:
                        await other.put(str({'task': 'new-client', 'clients-in-room': clients}))
    finally:
        task.cancel()
        websocket_rooms[room_id].remove(queue)
        rooms_and_clients[room_id]["clients"].remove(client_id)

        print(f"user {client_id} disconnected from room {room_id}")

        if rooms_and_clients[room_id]["clients"] == []:
            # когда никого нет в комнате - она удаляется
            del rooms_and_clients[room_id]
            print(f"room {room_id} deleted")
        else:
            for other in websocket_rooms[room_id]:
                # когда клиент отключился - всем рассылка
                if other is not queue:
                    await other.put(str({'task': 'removed-client', 'clients-in-room': clients, 'removed': client_id}))


if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0")
