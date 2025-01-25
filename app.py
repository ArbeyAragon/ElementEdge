import dash
from dash import Input, Output, State, html, dcc, ALL
import dash_leaflet as dl
import dash_bootstrap_components as dbc
import random
import plotly.graph_objs as go
from collections import deque
import cv2
from flask import Response
import threading

# Colores de la paleta
palette = {
    "background": "#102026",
    "border": "#5D7366",
    "area": "#565902",
    "highlight": "#ECF22E",
    "secondary": "#EDF25E",
}

# Inicializar las colas para los signos vitales
heart_rate_queue = deque(maxlen=10)  # Nivel cardíaco
oxygen_level_queue = deque(maxlen=10)  # Nivel de oxígeno
temperature_queue = deque(maxlen=10)  # Temperatura corporal
blood_pressure_queue = deque(maxlen=10)  # Presión arterial

# Función para generar valores simulados
def generate_random_value(min_value, max_value):
    return random.uniform(min_value, max_value)

# Inicializar los datos con valores aleatorios
for _ in range(10):
    heart_rate_queue.append(generate_random_value(60, 100))  # Pulsaciones por minuto
    oxygen_level_queue.append(generate_random_value(90, 100))  # Porcentaje de oxígeno
    temperature_queue.append(generate_random_value(36, 37.5))  # Temperatura en °C
    blood_pressure_queue.append(generate_random_value(110, 130))  # Presión sistólica


# Crear la aplicación Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Inicializar una cola para los signos vitales (últimos 10 segundos)
vital_signs_queue = deque(maxlen=10)

# Generar signos vitales iniciales
def generate_vital_sign():
    return random.uniform(60, 100)

# Actualizar la cola de signos vitales con datos iniciales
for _ in range(10):
    vital_signs_queue.append(generate_vital_sign())

# Datos iniciales de los marcadores
markers = [
    {
        "id": f"marker_{i}",
        "type": random.choice(["Fire", "Rescued", "Firefighter"]),
        "name": random.choice(["John Doe", "Jane Smith", "Alex Johnson", "Chris Lee", "Taylor Brown"]),
        "location": (34.0522 + random.uniform(-0.03, 0.03), -118.2437 + random.uniform(-0.03, 0.03)),
    }
    for i in range(10)
]

# Asignar colores a los tipos de marcadores
marker_colors = {
    "Fire": "#ECF22E",
    "Rescued": "#EDF25E",
    "Firefighter": "#5D7366",
}

# Asignar URL a los iconos según el tipo
icon_urls = {
    "Fire": "https://arbeyaragon.github.io/ElementEdge/fire.png",
    "Rescued": "https://arbeyaragon.github.io/ElementEdge/person_danger.png",
    "Firefighter": "https://arbeyaragon.github.io/ElementEdge/fireworker.png",
}

# Configurar captura de video
camera = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.server.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Historial de chat (lista inicial vacía)
chat_history = []
# Logo de la aplicación (puedes cambiar la URL por el logo que desees)
logo_url = "https://arbeyaragon.github.io/ElementEdge/logo.png"

# Layout actualizado con el Header
app.layout = dbc.Container(
    fluid=True,
    style={
        "background": "linear-gradient(135deg, #102026 20%, #5D7366 40%, #565902 60%, #ECF22E 80%, #EDF25E 100%)",
        "backgroundSize": "400% 400%",
        "animation": "gradientAnimation 15s ease infinite",
    },
    children=[
        # Header de la aplicación
        dbc.Row(
            [
                dbc.Col(
                    html.Img(
                        src=logo_url,
                        style={"height": "60px", "marginRight": "15px"},
                    ),
                    width="auto",
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.H1(
                                "ElementEdge Monitoring",
                                style={"color": "#ECF22E", "marginBottom": "5px"},
                            ),
                            html.P(
                                "An application for monitoring vital signs, managing emergencies, and visualizing interactive maps.",
                                style={"color": "#EDF25E", "fontSize": "16px"},
                            ),
                        ]
                    ),
                ),
            ],
            align="center",
            style={
                "padding": "10px",
                "backgroundColor": "#5D7366",
                "borderBottom": f"2px solid {palette['border']}",
            },
        ),
        # Contenido principal
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            dl.Map(
                                style={
                                    "height": "80vh",
                                    "border": f"2px solid #5D7366",
                                    "background": "linear-gradient(135deg, #102026, #5D7366, #565902, #ECF22E, #EDF25E)",
                                },
                                center=(34.0522, -118.2437),
                                zoom=13,
                                children=[
                                    dl.TileLayer(),
                                    dl.LayerGroup(
                                        [
                                            dl.Marker(
                                                id={"type": "marker", "index": marker["id"]},
                                                position=marker["location"],
                                                children=[
                                                    dl.Tooltip(marker["type"]),
                                                    dl.Popup(f"{marker['name']} ({marker['type']})"),
                                                ],
                                                icon=dict(
                                                    iconUrl=icon_urls[marker["type"]],
                                                    iconSize=[30, 30],
                                                    iconAnchor=[15, 15],
                                                ),
                                            )
                                            for marker in markers
                                        ]
                                    ),
                                ],
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        id="chat-history",
                                        style={
                                            "height": "300px",
                                            "overflowY": "auto",
                                            "padding": "10px",
                                            "backgroundColor": "#5D7366",
                                            "color": "#EDF25E",
                                            "border": f"1px solid {palette['border']}",
                                            "borderRadius": "5px",
                                            "marginBottom": "10px",
                                        },
                                    ),
                                    dbc.InputGroup(
                                        [
                                            dbc.Input(
                                                id="chat-input",
                                                placeholder="Type your message...",
                                                style={"backgroundColor": "#102026", "color": "#ECF22E"},
                                            ),
                                            dbc.Button(
                                                "Send",
                                                id="send-button",
                                                color="success",
                                                n_clicks=0,
                                                style={"backgroundColor": "#ECF22E", "color": "#102026"},
                                            ),
                                        ],
                                        className="mb-3",
                                    ),
                                ],
                                style={"marginTop": "10px"},
                            ),
                        ],
                        style={"position": "relative"},
                    ),
                    width=8,
                ),
                dbc.Col(
                    [
                        html.H2("Details", style={"color": "#ECF22E"}),
                        html.Div(
                            id="details",
                            style={"marginBottom": "20px", "color": "#EDF25E"},
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dcc.Graph(
                                        id="heart_rate_graph",
                                        config={"displayModeBar": False},
                                        style={"height": "150px"},
                                    ),
                                    width=6,
                                ),
                                dbc.Col(
                                    dcc.Graph(
                                        id="oxygen_level_graph",
                                        config={"displayModeBar": False},
                                        style={"height": "150px"},
                                    ),
                                    width=6,
                                ),
                            ],
                            style={"marginBottom": "10px"},
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dcc.Graph(
                                        id="temperature_graph",
                                        config={"displayModeBar": False},
                                        style={"height": "150px"},
                                    ),
                                    width=6,
                                ),
                                dbc.Col(
                                    dcc.Graph(
                                        id="blood_pressure_graph",
                                        config={"displayModeBar": False},
                                        style={"height": "150px"},
                                    ),
                                    width=6,
                                ),
                            ],
                            style={"marginBottom": "10px"},
                        ),
                        html.Div(
                            [
                                html.Img(
                                    src="/video_feed",
                                    style={"width": "100%", "border": "2px solid #5D7366"},
                                ),
                            ],
                            style={"marginTop": "20px"},
                        ),
                    ],
                    width=4,
                    style={
                        "padding": "20px",
                        "backgroundColor": "#565902",
                        "height": "100vh",
                        "display": "flex",
                        "flexDirection": "column",
                    },
                ),
            ]
        ),
        dcc.Interval(
            id="update_interval",
            interval=1000,
            n_intervals=0,
        ),
    ],
)


# Callback para manejar el chat
@app.callback(
    Output("chat-history", "children"),
    [Input("send-button", "n_clicks")],
    [State("chat-input", "value")],
)
def update_chat(n_clicks, user_message):
    global chat_history

    if n_clicks > 0 and user_message:
        # Simular una respuesta del chatbot
        bot_response = f"Bot: You said '{user_message}'"

        # Actualizar el historial de mensajes
        chat_history.append(f"User: {user_message}")
        chat_history.append(bot_response)

        # Construir el historial de chat como elementos de lista
        chat_elements = [
            html.Div(msg, style={"marginBottom": "5px"}) for msg in chat_history
        ]
        return chat_elements

    # Si no hay mensajes nuevos, mostrar el historial actual
    return [html.Div(msg, style={"marginBottom": "5px"}) for msg in chat_history]



# Callback para actualizar los gráficos
@app.callback(
    [
        Output("heart_rate_graph", "figure"),
        Output("oxygen_level_graph", "figure"),
        Output("temperature_graph", "figure"),
        Output("blood_pressure_graph", "figure"),
    ],
    Input("update_interval", "n_intervals"),
)
def update_vital_signs(n_intervals):
    # Actualizar las colas con nuevos valores
    heart_rate_queue.append(generate_random_value(60, 100))
    oxygen_level_queue.append(generate_random_value(90, 100))
    temperature_queue.append(generate_random_value(36, 37.5))
    blood_pressure_queue.append(generate_random_value(110, 130))

    # Crear gráficos para cada cola
    heart_rate_fig = go.Figure(go.Scatter(
        y=list(heart_rate_queue), 
        mode="lines+markers",
        line=dict(color=palette["highlight"], width=2),
        marker=dict(size=8, color=palette["secondary"], symbol="circle"),
    ))
    oxygen_level_fig = go.Figure(go.Bar(
        y=list(oxygen_level_queue), 
        marker_color=palette["area"]
    ))
    temperature_fig = go.Figure(go.Scatter(
        y=list(temperature_queue), 
        fill="tozeroy", 
        line=dict(color=palette["border"], width=2),
        fillcolor=palette["secondary"],
    ))
    blood_pressure_fig = go.Figure(go.Scatter(
        y=list(blood_pressure_queue), 
        mode="lines", 
        line=dict(color=palette["area"], width=2),
    ))

    # Configurar estilos de los gráficos
    for fig, title in zip(
        [heart_rate_fig, oxygen_level_fig, temperature_fig, blood_pressure_fig],
        ["Heart Rate (BPM)", "Oxygen Level (%)", "Temperature (°C)", "Blood Pressure (Systolic)"],
    ):
        fig.update_layout(
            title=title,
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis_title="Time (Last 10 seconds)",
            yaxis_title=title.split(" ")[0],
            plot_bgcolor=palette["background"],
            paper_bgcolor=palette["background"],
            font=dict(color=palette["highlight"]),
            xaxis=dict(showgrid=False, color=palette["secondary"]),
            yaxis=dict(showgrid=True, gridcolor=palette["border"], color=palette["secondary"]),
        )

    return heart_rate_fig, oxygen_level_fig, temperature_fig, blood_pressure_fig


# Añadir una variable global para el marcador seleccionado
selected_marker_id = None

# Callback para manejar la selección de un marcador y actualizar su apariencia
@app.callback(
    Output({"type": "marker", "index": ALL}, "icon"),
    Input({"type": "marker", "index": ALL}, "n_clicks"),
    State({"type": "marker", "index": ALL}, "id"),
)
def update_marker_selection(n_clicks, ids):
    global selected_marker_id
    if not any(n_clicks):
        return [dict(iconUrl=icon_urls[marker["type"]], iconSize=[30, 30], iconAnchor=[15, 15]) for marker in markers]

    clicked_index = n_clicks.index(1)
    selected_marker_id = ids[clicked_index]["index"]

    # Actualizar los íconos según el marcador seleccionado
    icons = []
    for marker in markers:
        if marker["id"] == selected_marker_id:
            icons.append(
                dict(
                    iconUrl="https://arbeyaragon.github.io/ElementEdge/fireworker_selected.png",  # Ícono destacado
                    iconSize=[40, 40],
                    iconAnchor=[20, 20],
                )
            )
        else:
            icons.append(
                dict(
                    iconUrl=icon_urls[marker["type"]],
                    iconSize=[30, 30],
                    iconAnchor=[15, 15],
                )
            )
    return icons

# Callback para mostrar detalles del marcador seleccionado
@app.callback(
    Output("details", "children"),
    Input({"type": "marker", "index": ALL}, "n_clicks"),
    State({"type": "marker", "index": ALL}, "id"),
)
def display_marker_details(n_clicks, ids):
    global selected_marker_id
    if not any(n_clicks):
        return "Click on a marker to see details."

    clicked_index = n_clicks.index(1)
    selected_marker_id = ids[clicked_index]["index"]
    marker = next((m for m in markers if m["id"] == selected_marker_id), None)
    if marker:
        return html.Div(
            [
                html.H4(marker["name"], style={"color": "#ECF22E"}),
                html.P(f"Role: {marker['type']}", style={"color": "#EDF25E"}),
            ]
        )
    return "No details available."

if __name__ == "__main__":
    app.run_server(debug=True)

