import dash
from dash import html, Output, Input, State, callback, dcc, ALL, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_bootstrap_components as dbc
from dash_extensions import Purify, WebSocket
import config
import random
import ast

app = dash.Dash(
    __name__,
    use_pages=False,
    external_stylesheets=[dbc.themes.FLATLY],
    title=config.site_title(),
    update_title="Updating...",
    external_scripts=['/assets/size.js']
)


def format_message(text, time, side):
    if side not in ["left", "right", "full"]:
        raise ValueError
    else:
        return html.Div(
            [
                html.Div(
                    [
                        (
                            html.P(
                                text,
                                className="message-main-text",
                            )
                            if side in ["left", "right"]
                            else text
                        ),
                        (
                            html.P(time, className="message-time")
                            if side in ["left", "right"]
                            else None
                        ),
                    ],
                    className=f"message-content-{side}",
                ),
            ],
            className=f"message-float-{side}",
        )

def test_roomid(room_id):
    if room_id == '123': return False
    else: return True

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
        dcc.Store(id='room_id_value'),
        dcc.Store(id='user_id_value'),
        html.Div(id='ws-handle'),

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
    className='main_container',
    # style={},
)

app.layout = dmc.NotificationsProvider(main_container)


# callbacks
@callback(
    [
        Output('ws-handle', 'children'),
        Output("messenger-div", "children"),
        Output("back-button", "style"),
        Output("modal", "is_open", allow_duplicate=True),
        Output("connect-to-room", "n_clicks"),
        Output("create-room", "n_clicks"),
        Output('room_id_value', 'data'),
        Output('user_id_value', 'data'),
        Output('room-id', 'invalid'),
    ],
    [Input("connect-to-room", "n_clicks"), Input("create-room", "n_clicks")],
    [
        State("modal", "is_open"),
        State('room-id', 'value')
    ],
    prevent_initial_call=True,
)
def openroom(connect_with_id, connect_newroom, is_open, room_id):
    user_id = str(random.randint(100, 999))
    if connect_newroom == 0 and (room_id == '' or room_id == None or not test_roomid(room_id)):
        return [no_update]*8 + [True]
    if connect_newroom == 1:
        room_id = str(random.randint(100, 999))
    messenger_content = [
        dmc.Stack(
            [
                dcc.Markdown(f'**ID комнаты**: `{room_id}`, **Ваш ID**: `{user_id}`'),
                html.Div(
                    html.Div(
                        [
                            format_message("Приятного общения! Для завершения диалога - нажмите на кнопку сверху или выйдите из комнаты.", "01:50", "full"),
                        ],
                        className="messages-box",
                        id="messages-main-container",
                    ),
                    className="roww fill-remain",
                    id="msg_scroll_box",
                ),
                dmc.Divider(variant="solid"),
                html.Div(
                    [
                        dbc.InputGroup(
                            [
                                dbc.Input(
                                    placeholder="Ваше сообщение", id="message-text"
                                ),
                                dbc.Button("Отправить", id="send-message"),
                            ],
                            style={"width": "100%"},
                        ),
                    ],
                    className="row fit-content",
                ),
            ],
            className="boxx",
        )
    ]
    return (
        WebSocket(url=f"ws://192.168.3.36:5000/ws/{room_id}", id="ws"),
        messenger_content,
        {"display": "unset"},
        not is_open if connect_with_id != 0 else is_open,
        0,
        0,
        room_id,
        user_id,
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
        Output("ws", "send")
    ],
    Input("send-message", "n_clicks"),
    [
        State("messages-main-container", "children"),
        State("message-text", "value"),
        State('room_id_value', 'data'),
        State('user_id_value', 'data'),
    ],
    prevent_initial_call=True,
)
def send_message(n_clicks, children, text, room_id, user_id):
    if text == None: return [no_update]*3 
    children.append(format_message(text, "00:00", "right"))
    return children, None, str({'mode': 'send', 'user_id': user_id, 'room_id': room_id, 'msg': text})

@callback(
    Output("messages-main-container", "children"),
    Input("ws", "message"),
    [
        State("messages-main-container", "children"),
        State('room_id_value', 'data'),
        State('user_id_value', 'data'),
    ],
    prevent_initial_call=True,
)
def display_message(message, children, room_id, user_id):
    print(message)
    msg_dict = ast.literal_eval(message['data'])
    text = msg_dict['msg']
    children.append(format_message(text, "00:00", "left"))
    return children



if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=config.panel_port())
