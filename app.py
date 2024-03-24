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
)

def format_message(text, time, side):
    if side not in ['left', 'right']:
        raise ValueError
    else:
        return html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    text,
                                    className="message-main-text",
                                ),
                                html.P(
                                    time,
                                    className="message-time"
                                ),
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
                        format_message('Ну как вообще твои дела? Как живешь? '*5, '01:50', 'left'),
                        format_message('И тебе привет!', '01:50', 'right'),  
                    ],
                    className="messages-box",
                ),
                className="roww fill-remain",
            ),
            dmc.Divider(variant="solid"),
            html.Div(
                [
                    dbc.InputGroup(
                        [
                            dbc.Input(placeholder="Ваше сообщение",
                                      id="message"),
                            dbc.Button("Отправить", id="send-message"),
                        ],
                        style={"width": "100%"},
                    ),
                ],
                className="row fit-content",
            ),
        ],
        className="boxx",
        # align='center',
        # justify='center'
    )
]

site_content = dmc.Grid(
    [
        dmc.Col(span=3, className="col-top-margin"),
        dmc.Col(
            [
                html.Div(
                    messenger_content,
                    className="block-background",
                    style={"height": "800px"},
                )
            ],
            span=6,
            className="col-top-margin",
            style={
                "display": "flex",
                "justify-items": "center",
                "flex-wrap": "wrap",
                "align-content": "center",
            },
        ),
        dmc.Col(span=3, className="col-top-margin"),
    ],
    gutter="xl",
    style={"min-height": "100vh"},
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


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=config.panel_port())
