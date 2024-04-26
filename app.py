import dash
from dash import (
    html,
    Output,
    Input,
    State,
    callback,
    dcc,
    no_update,
    clientside_callback,
)
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from dash_extensions import WebSocket
import config
import random
from components import callbacks_messages, callbacks_server, defs_messages

avaliable_rooms = []

app = dash.Dash(
    __name__,
    use_pages=False,
    external_stylesheets=[dbc.themes.FLATLY, dbc.icons.FONT_AWESOME],
    title=config.site_title(),
    update_title="Dash Chatrooms ↺",
    external_scripts=["/assets/size.js"],
)


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
            ],
            id="connect-buttons-group",
        ),
        dbc.Alert(
            "Сервер временно недоступен. Попробуйте позднее и перезагрузите страницу.",
            color="danger",
            style={"display": "none"},
            id="alert-disabled-server",
        ),
    ],
    className="boxx",
    align="center",
)

site_content = dmc.Grid(
    [
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
        dmc.Grid(
            [
                dmc.Col(
                    [
                        html.A(
                            dbc.NavbarBrand(
                                config.site_title(), style={"color": "black"}
                            ),
                            href="/",
                            style={"text-decoration": "none"},
                        ),
                    ],
                    span="content",
                ),
                dmc.Col(" ", span="auto"),
                dmc.Col(
                    [
                        html.Span(
                            [
                                dbc.Label(
                                    className="fa fa-moon",
                                    html_for="color-mode-switch",
                                    color="primary",
                                ),
                                dbc.Switch(
                                    id="color-mode-switch",
                                    value=True,
                                    className="d-inline-block ms-1",
                                    persistence=True,
                                ),
                                dbc.Label(
                                    className="fa fa-sun",
                                    html_for="color-mode-switch",
                                    color="primary",
                                ),
                            ]
                        )
                    ],
                    span="content",
                    style={"display": "flex", "align-items": "flex-end"},
                ),
            ],
            style={"width": "100%"},
        ),
    ],
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
)

service_elements = html.Div(
    [
        dcc.Store(id="room_id_value"),
        dcc.Store(id="client_id_value"),
        dcc.Store(id="avaliable-rooms"),
        html.Div(id="ws-handle"),
        dcc.Interval(id="rooms_query_timer"),
        WebSocket(url=f"ws://192.168.3.36:5000/ws/get_server_state", id="ws_state"),
    ]
)

main_container = html.Div(
    [header, site_content, connect_modal, service_elements], className="main_container"
)

app.layout = dmc.NotificationsProvider(main_container)


# callbacks
@callback(
    Output("ws_state", "send"),
    Input("rooms_query_timer", "n_intervals"),
)
def send_query_server_health(n_intervals):
    "Отправка запроса с наличием комнат на сервере"
    return str({"mode": "get_rooms", "n_intervals": n_intervals})


@callback(
    [
        Output("connect-modal", "disabled"),
        Output("connect-buttons-group", "style"),
        Output("alert-disabled-server", "style"),
        Output("rooms_query_timer", "disabled", allow_duplicate=True),
    ],
    [Input("ws_state", "state"), Input("ws_state", "message")],
    prevent_initial_call="initial_duplicate",
)
def get_query_server_health(state, msg):
    "Обработчик доступности сервера и информации о комнатах"
    if state == None or msg == None:
        return [no_update] * 4

    global avaliable_rooms

    show = {"display": "unset"}
    hide = {"display": "none"}

    if state["readyState"] == 3:
        return no_update, hide, show, True
    try:
        rooms = msg["data"]
        if rooms == "no_rooms":
            avaliable_rooms = []
            return True, show, hide, no_update
        else:
            avaliable_rooms = rooms.split(",")
            return False, show, hide, no_update
    except:
        return no_update, no_update, no_update


@callback(
    [
        Output("ws-handle", "children"),  # ссылка на вебсокет
        Output(
            "rooms_query_timer", "disabled"
        ),  # таймер на запрос комнат. отключаем чтоб не делать лишних запросов
        Output("messenger-div", "children", allow_duplicate=True),  # блок с сообщениями
        Output("modal", "is_open", allow_duplicate=True),  # закрыть модалку
        Output("connect-to-room", "n_clicks"),  # кнопка дял подключения к комнате
        Output("create-room", "n_clicks"),  # кнопка для создания комнаты
        Output("room_id_value", "data"),  # значение номера комнаты
        Output("client_id_value", "data"),  # значение номера коиента
        Output(
            "room-id", "invalid"
        ),  # если id комнаты неверный - поле будет подсвечено красным
    ],
    [Input("connect-to-room", "n_clicks"), Input("create-room", "n_clicks")],
    [State("modal", "is_open"), State("room-id", "value")],
    prevent_initial_call=True,
)
def openroom(connect_with_id, connect_newroom, is_open, room_id):
    "Создать новую или подключиться к известной комнате"
    client_id = str(random.randint(100, 999))
    global avaliable_rooms
    if connect_newroom == 0 and (
        room_id == "" or room_id == None or room_id not in avaliable_rooms
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
                html.Div(
                    html.Div(
                        [
                            defs_messages.format_message(
                                "Приятного общения!", service=True
                            )
                        ],
                        className="messages-box",
                        id="messages-main-container",
                    ),
                    className="roww fill-remain",
                    id="overlay",
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
        True,
        messenger_content,
        not is_open if connect_with_id != 0 else is_open,
        0,
        0,
        room_id,
        client_id,
        False,
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
    return callbacks_messages.send_message(n_clicks, children, text, room_id, client_id)


@callback(
    Output("ws", "send"),
    Output("messages-main-container", "children", allow_duplicate=True),
    [
        Input("init-connect", "n_intervals"),
    ],
    prevent_initial_call=True,
)
def get_clients_in_room(n_intervals):
    return str({"task": "connect_handle"}), no_update


@callback(
    Output("messenger-div", "children"),
    Input("ws", "state"),
    prevent_initial_call=True,
)
def states_handler(state):
    return callbacks_server.states_handler(state)


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
    return callbacks_messages.display_message(message, children, room_id, client_id)


clientside_callback(
    """
    (switchOn) => {
       document.documentElement.setAttribute('data-bs-theme', switchOn ? 'light' : 'dark');  
       return window.dash_clientside.no_update
    }
    """,
    Output("color-mode-switch", "id"),
    Input("color-mode-switch", "value"),
)

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=config.panel_port())
