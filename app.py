import dash
from dash import html, Output, Input, State, callback, dcc, ALL, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_bootstrap_components as dbc
from dash_extensions import Purify
import config

app = dash.Dash(
    __name__,
    use_pages=False,
    external_stylesheets=[dbc.themes.FLATLY],
    title=config.site_title(),
    update_title="Updating...",
    external_scripts=['/assets/scroll_to_top.js']
)


def format_message(text, time, side):
    if side not in ['left', 'right', 'full']:
        raise ValueError
    else:
        return html.Div(
            [
                html.Div(
                    [
                        html.P(
                            text,
                            className="message-main-text",
                        ) if side in ['left', 'right'] else text,
                        html.P(
                            time,
                            className="message-time"
                        ) if side in ['left', 'right'] else None,
                    ],
                    className=f"message-content-{side}",
                ),
            ],
            className=f"message-float-{side}",
        )


server = app.server
app.config.suppress_callback_exceptions = True

messenger_content = [
    dmc.Stack(
        [
            html.Div(
                html.Div(
                    [
                        format_message('Привет!', '01:50', 'left'),
                        format_message('И тебе привет!', '01:50', 'right'),
                        format_message('И тебе привет!', '01:50', 'right'),
                        format_message('И тебе привет!', '01:50', 'right'),
                        format_message('И тебе привет!', '01:50', 'right'),
                        format_message('И тебе привет!', '01:50', 'right'),
                        format_message('Связь потеряна.', '01:50', 'full'),
                    ],
                    className="messages-box",
                    id='messages-main-container'
                ),
                className="roww fill-remain",
                id='msg_scroll_box'
                
            ),
            dmc.Divider(variant="solid"),
            html.Div(
                [
                    dbc.InputGroup(
                        [
                            dbc.Input(placeholder="Ваше сообщение",
                                      id="message-text"),
                            dbc.Button("Отправить", id="send-message"),
                        ],
                        style={"width": "100%"},
                    ),
                ],
                className="row fit-content",
            ),
        ],
        className="boxx"
    )
]

site_content = dmc.Grid(
    [
        dmc.Col(span=3, className="col-top-margin adaptive-col"),
        dmc.Col(
            [
                html.Div(
                    messenger_content,
                    className="block-background",
                    style={"height": "800px"},
                )
            ],
            span=6,
            className="col-top-margin adaptive-col",
            style={
                "display": "flex",
                "justify-items": "center",
                "flex-wrap": "wrap",
                "align-content": "center",
            },
        ),
        dmc.Col(span=3, className="col-top-margin adaptive-col"),
    ],
    gutter="xl",
    style={"min-height": "100vh"},
    className='adaptive-grid'
)

header = dmc.Header(
    [
        dmc.Grid(
            [
                dmc.Col(html.H4(config.site_title()), span="content"),
                dmc.Col(span="auto"),
                dmc.Col("Кнопочки", span="content"),
            ],
            className="header-grid",
            gutter="xs",
        ),
    ],
    fixed=True,
    height=65,
)

main_container = html.Div(
    [header, site_content], style={"max-width": "98%", "margin": "auto"}
)

app.layout = dmc.NotificationsProvider(main_container)


# callbacks
@callback(
    [
        Output("messages-main-container", "children"),
        Output("message-text", "value"),
    ],
    Input("send-message", "n_clicks"),
    [
        State("messages-main-container", "children"),
        State("message-text", "value"),
    ],
    prevent_initial_call=True,
)
def send_message(n_clicks, children, text):
    children.append(format_message(text, '00:00', 'right'))
    return children, None


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=config.panel_port())
