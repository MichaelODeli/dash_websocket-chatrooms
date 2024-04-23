import ast
import asyncio
from collections import defaultdict
from quart import Quart, websocket

app = Quart(__name__)

websocket_rooms = defaultdict(set)

async def send_task(ws, queue):
    while True:
        message = await queue.get()
        await ws.send(message)


@app.websocket("/ws/<id>")
async def ws(id):
    global websocket_rooms
    queue = asyncio.Queue()
    websocket_rooms[id].add(queue)
    try:
        task = asyncio.ensure_future(send_task(websocket._get_current_object(), queue))
        while True:
            message = await websocket.receive()
            msg_dict = ast.literal_eval(message)
            print(msg_dict)
            for other in websocket_rooms[id]:
                if other is not queue:
                    await other.put(message)
    finally:
        task.cancel()
        await task
        websocket_rooms[id].remove(queue)


if __name__ == "__main__":
    app.run(port=5000, host='0.0.0.0')