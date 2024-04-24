import dash
from dash import (
    html,
    Output,
    Input,
    State,
    callback,
    dcc,
    ALL,
    no_update,
    clientside_callback,
)
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_bootstrap_components as dbc
from dash_extensions import Purify, WebSocket
import config
import random
import ast
from datetime import datetime
import time

app = dash.Dash(
    __name__,
    use_pages=False,
    external_stylesheets=[dbc.themes.FLATLY, dbc.icons.FONT_AWESOME],
    title=config.site_title(),
    update_title="Updating...",
    external_scripts=["/assets/size.js"],
)


def format_message(content, time="", sender_id="", my_message=False, service=False):
    "Отформатировать сообщение для его отображения в мессенджере"
    appendix = " bg-light" if my_message else ""
    msg_layout = (
        html.Div(
            [
                (html.Strong("Вы:") if my_message else html.Strong(f"ID:{sender_id}")),
                html.Br(),
                content,
                html.P(time, className="message-time"),
            ],
            className="message table border rounded" + appendix,
        )
        if not service
        else html.Div(content, className="message table border rounded bg-warning")
    )
    return msg_layout


def test_roomid(room_id):
    "Проверка существования номера комнаты"
    if room_id == "123":
        return False
    else:
        return True


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


server = app.server
app.config.suppress_callback_exceptions = True

gotoroom = dmc.Stack(
    [
        html.H4("Dash Messenger", style={"padding-top": "20px"}),
        html.H6("Основан на технологии WebSocket"),
        html.P(
            'Чтоб подключиться к существующей комнате, нажмите на кнопку "Подключиться" и введите её ID.'
        ),
        html.P(
            'Если вы хотите создать новую комнату - нажмите на кнопку "Создать комнату" и отправьте её ID тому, с кем хотите пообщаться.'
        ),
        dbc.ButtonGroup(
            [
                dbc.Button("Подключиться", id="connect-modal"),
                dbc.Button("Создать комнату", id="create-room", n_clicks=0),
            ]
        ),
        # html.Button('Open room', id='open-room-button')
    ],
    className="boxx",
    align="center",
)

site_content = dmc.Grid(
    [
        dcc.Store(id="room_id_value"),
        dcc.Store(id="client_id_value"),
        dcc.Store(id="avaliable-rooms"),
        html.Div(id="ws-handle"),
        dmc.Col(span=3, className="hide-it"),
        dmc.Col(
            [
                html.Div(
                    gotoroom,
                    className="block-background",
                    style={"height": "75vh"},
                    id="messenger-div",
                )
            ],
            span=6,
            className="adaptive-col",
            style={
                "display": "flex",
                "justify-items": "center",
                "flex-wrap": "wrap",
                "align-content": "center",
            },
        ),
        dmc.Col(span=3, className="hide-it"),
    ],
    gutter="xl",
    style={"min-height": "100%", "padding": "5vh 0 5vh 0"},
    className="adaptive-grid",
)

header = dbc.Navbar(
    [
        dbc.NavbarBrand(config.site_title()),
        html.A(
            "На главную",
            className="btn btn-primary",
            href="/",
            style={"display": "none"},
            id="back-button",
        ),
    ],
    # fixed=True,
    style={"height": "5vh", "padding": "0 10px 0 10px"},
    class_name="adaptive-nav",
)

connect_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Подключение к существующей комнате")),
        dbc.ModalBody(
            [
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("ID комнаты"),
                        dbc.Input(placeholder="ID", id="room-id"),
                    ]
                )
            ]
        ),
        dbc.ModalFooter(
            dbc.Button(
                "Подключиться", id="connect-to-room", className="ms-auto", n_clicks=0
            )
        ),
    ],
    id="modal",
    # is_open=False
)


main_container = html.Div(
    [header, site_content, connect_modal],
    className="main_container",
)

app.layout = dmc.NotificationsProvider(main_container)


# callbacks
@callback(
    [
        Output("ws-handle", "children"),
        Output("messenger-div", "children", allow_duplicate=True),
        Output("back-button", "style"),
        Output("modal", "is_open", allow_duplicate=True),
        Output("connect-to-room", "n_clicks"),
        Output("create-room", "n_clicks"),
        Output("room_id_value", "data"),
        Output("client_id_value", "data"),
        Output("room-id", "invalid"),
    ],
    [Input("connect-to-room", "n_clicks"), Input("create-room", "n_clicks")],
    [State("modal", "is_open"), State("room-id", "value")],
    prevent_initial_call=True,
)
def openroom(connect_with_id, connect_newroom, is_open, room_id):
    client_id = str(random.randint(100, 999))
    if connect_newroom == 0 and (
        room_id == "" or room_id == None or not test_roomid(room_id)
    ):
        return [no_update] * 8 + [True]
    if connect_newroom == 1:
        room_id = str(random.randint(100, 999))
    messenger_content = [
        dmc.Stack(
            [
                dmc.Group(
                    [
                        dcc.Markdown(f"**ID комнаты**: `{room_id}`"),
                        dcc.Markdown(f"**Ваш ID**: `{client_id}`"),
                        dcc.Markdown("**Участники скрыты**", id="room-members"),
                    ]
                ),
                # dmc.LoadingOverlay(
                html.Div(
                    html.Div(
                        [format_message("Приятного общения!", service=True)],
                        className="messages-box",
                        id="messages-main-container",
                    ),
                    className="roww fill-remain",
                    id='overlay'
                ),
                html.Div(
                    [
                        dbc.InputGroup(
                            [
                                dbc.Input(
                                    placeholder="Ваше сообщение", id="message-text"
                                ),
                                dbc.Button(
                                    html.Div(className="fa fa-paperclip"), disabled=True
                                ),
                                dbc.Button("Отправить", id="send-message"),
                                dbc.Button(
                                    html.Div(className="fa fa-arrow-down"),
                                    disabled=True,
                                    id="scroll-to-bottom",
                                ),
                            ],
                        )
                    ],
                    style={"width": "100%"},
                ),
            ],
            align="center",
            className="boxx",
        )
    ]
    return (
        [
            WebSocket(url=f"ws://192.168.3.36:5000/ws/{room_id}/{client_id}", id="ws"),
            dcc.Interval(id="init-connect", interval=100, max_intervals=1),
        ],
        messenger_content,
        {"display": "unset"},
        not is_open if connect_with_id != 0 else is_open,
        0,
        0,
        room_id,
        client_id,
        False
    )


@callback(
    Output("modal", "is_open"),
    [Input("connect-modal", "n_clicks")],
    [State("modal", "is_open")],
    prevent_initial_call=True,
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open


@callback(
    [
        Output("messages-main-container", "children", allow_duplicate=True),
        Output("message-text", "value"),
        Output("ws", "send", allow_duplicate=True),
    ],
    Input("send-message", "n_clicks"),
    [
        State("messages-main-container", "children"),
        State("message-text", "value"),
        State("room_id_value", "data"),
        State("client_id_value", "data"),
    ],
    prevent_initial_call=True,
)
def send_message(n_clicks, children, text, room_id, client_id):
    if text == None:
        return [no_update] * 3
    time = datetime.now().strftime("%H:%M")
    children.append(format_message(html.P(text), time, my_message=True))
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


@callback(
    Output("ws", "send"),
    Output("messages-main-container", 'children', allow_duplicate=True),
    [
        Input("init-connect", "n_intervals"),
    ],
    prevent_initial_call=True,
)
def get_clients_in_room(n_intervals):
    return str({"task": "connect_handle"}) , no_update


@callback(
    Output("messenger-div", "children"),
    Input("ws", "state"),
    prevent_initial_call=True,
)
def states_handler(state):
    if state == None or state == "":
        return no_update
    else:
        ready_state = state["readyState"]
        print(state)
        if ready_state == 3:
            return dmc.Stack(
                [
                    html.H5("Соединение закрыто."),
                    (
                        "Сервер недоступен. Попробуйте позднее."
                        if state["code"] == 1006
                        else ''
                    ),
                    html.A(
                        "Попробовать снова",
                        className="btn btn-primary",
                        href="/",
                        style={'max-width': '40%'}
                    ),
                ],
                style={'height': '100%', 'display': 'flex', 'justify-content': 'center'},
                align='center'
            )
        else: 
            return no_update


@callback(
    [Output("messages-main-container", "children"), Output("room-members", "children")],
    Input("ws", "message"),
    [
        State("messages-main-container", "children"),
        State("room_id_value", "data"),
        State("client_id_value", "data"),
    ],
    prevent_initial_call=True,
)
def display_message(message, children, room_id, client_id):
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
                format_message(html.P(content), time, sender_id=remote_client_id)
            )
        elif msg_type == "img":
            print(f"here is img from {remote_client_id} in room {room_id}")
            # children.append(format_message(html.Img(src=text, style={'max-height': '150px'}), time, sender_id=remote_client_id))
        clts_str = make_clients_str(msg_dict, client_id)

        return children, clts_str
    elif msg_dict["task"] in ["new-client", "removed-client"]:
        # print(msg_dict)
        clts_str = make_clients_str(msg_dict, client_id)
        return no_update, clts_str


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=config.panel_port())
