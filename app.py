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

# Layout de la aplicación
app.layout = dbc.Container(
    fluid=True,
    style={
        "background": "linear-gradient(135deg, #102026 20%, #5D7366 40%, #565902 60%, #ECF22E 80%, #EDF25E 100%)",
        "backgroundSize": "400% 400%",
        "animation": "gradientAnimation 15s ease infinite",
    },
    children=[
        dbc.Row(
            [
                dbc.Col(
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
                    width=8,
                ),
                dbc.Col(
                    [
                        html.H2("Details", style={"color": "#ECF22E"}),
                        html.Div(
                            id="details",
                            style={"marginBottom": "20px", "color": "#EDF25E"},
                        ),
                        dcc.Graph(
                            id="vital_signs_graph",
                            config={"displayModeBar": False},
                            style={"height": "300px"},
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
                    style={"padding": "20px", "backgroundColor": "#565902"},
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        "This is additional text displayed below the map.",
                        style={
                            "textAlign": "center",
                            "backgroundColor": "#EDF25E",
                            "padding": "10px",
                            "fontWeight": "bold",
                        },
                    ),
                    width=12,
                ),
            ],
            style={"marginTop": "10px"},
        ),
        dcc.Interval(
            id="update_interval",
            interval=1000,
            n_intervals=0,
        ),
    ],
)


# Callback para actualizar los signos vitales en la gráfica
@app.callback(
    Output("vital_signs_graph", "figure"),
    Input("update_interval", "n_intervals"),
)
def update_vital_signs(n_intervals):
    # Agregar un nuevo valor a la cola
    vital_signs_queue.append(generate_vital_sign())

    # Crear la figura de Plotly
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            y=list(vital_signs_queue),
            mode="lines+markers",
            line=dict(color="#ECF22E", width=2),
            marker=dict(size=10, color="#EDF25E", symbol="circle"),
        )
    )
    fig.update_layout(
        title="Vital Signs Over Time",
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="Time (Last 10 seconds)",
        yaxis_title="Vital Sign Value",
        xaxis=dict(showgrid=False),
        yaxis=dict(range=[50, 120], showgrid=True),
        plot_bgcolor="#102026",
        paper_bgcolor="#102026",
        font=dict(color="#ECF22E"),
    )
    return fig

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

