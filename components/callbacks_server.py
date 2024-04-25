from dash import no_update, html
import dash_mantine_components as dmc


def states_handler(state):
    "Обработка неработоспособности сервера или потери соединения при подключении к серверу"
    if state == None or state == "":
        return no_update
    else:
        ready_state = state["readyState"]
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
