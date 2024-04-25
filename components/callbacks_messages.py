from dash import no_update, html, dcc
import ast
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from components import defs_messages
from datetime import datetime
import random
from dash_extensions import WebSocket

def display_message(message, children, room_id, client_id):
    "Отображение пришедшего сообщения с сервера"
    if message == None or message == "":
        return no_update, no_update

    msg_dict = ast.literal_eval(message["data"])
    if msg_dict["task"] == "send":
        content = msg_dict["content"]
        remote_client_id = msg_dict["client_id"]
        time = msg_dict["time"]
        msg_type = msg_dict["msg_type"]
        if msg_type == "text":
            # print(message)
            children.append(
                defs_messages.format_message(html.P(content), time, sender_id=remote_client_id)
            )
        elif msg_type == "img":
            print(f"here is img from {remote_client_id} in room {room_id}")
            # children.append(format_message(html.Img(src=text, style={'max-height': '150px'}), time, sender_id=remote_client_id))
        clts_str = defs_messages.make_clients_str(msg_dict, client_id)

        return children, clts_str
    elif msg_dict["task"] in ["new-client", "removed-client"]:
        # print(msg_dict)
        clts_str = defs_messages.make_clients_str(msg_dict, client_id)
        return no_update, clts_str


def send_message(n_clicks, children, text, room_id, client_id):
    "Отправка сообщения на сервер"
    if text == None:
        return [no_update] * 3
    time = datetime.now().strftime("%H:%M")
    children.append(defs_messages.format_message(html.P(text), time, my_message=True))
    return (
        children,
        None,
        str(
            {
                "task": "send",
                "msg_type": "text",
                "client_id": client_id,
                "room_id": room_id,
                "content": text,
                "time": time,
            }
        ),
    )