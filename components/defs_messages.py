from dash import html

def make_clients_str(msg_dict, client_id):
    "Подготовить строку с подключенными клиентами в комнате"
    clients = msg_dict["clients-in-room"].split(",")
    try:
        clients.remove(client_id)
        clients.remove(msg_dict["removed"])
    except:
        pass
    if clients == []:
        clts_str = "В комнате только Вы."
    else:
        room_members = ", ".join(clients) if len(clients) > 0 else clients[0]
        clts_str = f"**Участники**: `{room_members}`"
    return clts_str

def format_message(content, time="", sender_id="", my_message=False, service=False):
    "Отформатировать сообщение для его отображения в мессенджере"
    appendix = " bg-light text-primary" if my_message else ""
    msg_layout = (
        html.Div(
            [
                (html.Strong("Вы:") if my_message else html.Strong(f"ID:{sender_id}")),
                html.Br(),
                content,
                html.P(time, className="message-time"),
            ],
            className="message message-hover table border rounded p-1" + appendix,
        )
        if not service
        else html.Div(content, className="message table border rounded alert alert-warning text-primary text-center p-2")
    )
    return msg_layout