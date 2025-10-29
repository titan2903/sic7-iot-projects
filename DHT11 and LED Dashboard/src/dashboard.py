import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.graph_objs as go
import paho.mqtt.client as mqtt
import warnings
import json
import pandas as pd
import base64
import io
from datetime import datetime
from collections import deque
import ssl

# MQTT Configuration (HiveMQ Cloud Example)
MQTT_BROKER = "ab36ea92cee24b64acda14d3001e34d4.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USERNAME = "cakrawala_mqtt"
MQTT_PASSWORD = "vXtbU7m2DjTxBSLN"

# MQTT Topics
TEMP_HUMIDITY_TOPIC = "sic/dibimbing/catalina/titanio-yudista/pub/dht"
LED_CONTROL_TOPIC = "sic/dibimbing/catalina/titanio-yudista/sub/led"

# Data storage
MAX_DATA_POINTS = 100
temperature_data = deque(maxlen=MAX_DATA_POINTS)
humidity_data = deque(maxlen=MAX_DATA_POINTS)
timestamps = deque(maxlen=MAX_DATA_POINTS)

# LED state
led_state = {"status": "off"}

# Suppress DeprecationWarning from paho.mqtt about callback API version 1
warnings.filterwarnings(
    "ignore",
    message="Callback API version 1 is deprecated, update to latest version",
    category=DeprecationWarning,
    module=r"paho\.mqtt\.client",
)

# MQTT Client
mqtt_client = mqtt.Client()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(TEMP_HUMIDITY_TOPIC)
        print(f"Subscribed to {TEMP_HUMIDITY_TOPIC}")
    else:
        print(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    try:
        # Decode message
        message = msg.payload.decode()
        data = json.loads(message)

        # Extract sensor data
        if "temperature" in data and "humidity" in data:
            temperature = data["temperature"]
            humidity = data["humidity"]
            timestamp = datetime.now()

            # Store data
            temperature_data.append(temperature)
            humidity_data.append(humidity)
            timestamps.append(timestamp)

            print(f"Received - Temp: {temperature}°C, Humidity: {humidity}%")

    except Exception as e:
        print(f"Error processing message: {e}")


def setup_mqtt():
    """Setup MQTT client"""
    try:
        # Set username and password
        mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

        # Set SSL/TLS
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        mqtt_client.tls_set_context(context)

        # Set callbacks
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message

        # Connect to broker
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

        # Start loop in separate thread
        mqtt_client.loop_start()
        print("MQTT client started")

    except Exception as e:
        print(f"Error setting up MQTT: {e}")


def publish_led_command(command):
    """Publish LED control command"""
    try:
        payload = json.dumps({"led": command})
        result = mqtt_client.publish(LED_CONTROL_TOPIC, payload)
        if result.rc == 0:
            led_state["status"] = command
            print(f"LED command sent: {command}")
        else:
            print(f"Failed to send LED command: {command}")
    except Exception as e:
        print(f"Error publishing LED command: {e}")


# Initialize MQTT
setup_mqtt()

# Create Dash app
app = dash.Dash(__name__)

# Custom CSS for better styling
external_stylesheets = ['https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Modern CSS styling with proper container
app.layout = html.Div(
    className="main-container",
    children=[
        # Header Section
        html.Div(
            [
                html.H1(
                    "🌡️ DHT11 IoT Dashboard",
                    style={
                        "textAlign": "center",
                        "color": "#ffffff",
                        "marginBottom": 0,
                        "fontSize": "2.5rem",
                        "fontWeight": "300",
                        "letterSpacing": "1px",
                    },
                ),
                html.P(
                    "Real-time Temperature & Humidity Monitoring",
                    style={
                        "textAlign": "center",
                        "color": "#e8f4fd",
                        "margin": "10px 0 0 0",
                        "fontSize": "1.1rem",
                        "fontWeight": "300",
                    },
                ),
            ],
            style={
                "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                "padding": "40px 20px",
                "marginBottom": "30px",
                "borderRadius": "0 0 20px 20px",
                "boxShadow": "0 4px 20px rgba(0,0,0,0.1)",
            },
        ),
        
        # Content Container
        html.Div(
            className="container",
            children=[
        
        # Status & LED Control Section
        html.Div(
            className="control-section",
            children=[
                # Device Control Card
                html.Div(
                    className="control-card",
                    children=[
                        html.H3(
                            "� Device Control",
                            style={
                                "color": "#2c3e50",
                                "marginBottom": "20px",
                                "fontSize": "1.4rem",
                                "fontWeight": "500",
                                "textAlign": "center",
                            },
                        ),
                        html.Div(
                            className="button-group",
                            children=[
                                html.Button(
                                    "💡 Turn ON",
                                    id="led-on-btn",
                                    n_clicks=0,
                                    className="btn btn-success",
                                ),
                                html.Button(
                                    "💡 Turn OFF",
                                    id="led-off-btn",
                                    n_clicks=0,
                                    className="btn btn-danger",
                                ),
                            ],
                        ),
                        html.Div(
                            id="led-status",
                            className="status-display",
                            children="LED Status: OFF",
                        ),
                    ],
                ),
                
                # Export Controls Card
                html.Div(
                    className="export-card",
                    children=[
                        html.H3(
                            "📊 Data Export",
                            style={
                                "color": "#2c3e50",
                                "marginBottom": "20px",
                                "fontSize": "1.4rem",
                                "fontWeight": "500",
                                "textAlign": "center",
                            },
                        ),
                        html.P(
                            "Total Records: 0",
                            id="record-count",
                            className="record-count",
                        ),
                        html.Button(
                            "📥 Download CSV",
                            id="download-btn",
                            n_clicks=0,
                            className="btn btn-primary btn-full",
                        ),
                        dcc.Download(id="download-dataframe-csv"),
                    ],
                ),
            ],
        ),
        
        # Current Values Section
        html.Div(
            className="readings-section",
            children=[
                html.H3(
                    "📈 Live Readings",
                    className="section-title",
                ),
                html.Div(
                    className="readings-grid",
                    children=[
                        # Temperature Card
                        html.Div(
                            className="reading-card temp-card",
                            children=[
                                html.Div("🌡️", className="card-icon"),
                                html.H2(
                                    id="current-temp",
                                    children="--°C",
                                    className="reading-value temp-value",
                                ),
                                html.P("Temperature", className="reading-label"),
                            ],
                        ),
                        
                        # Humidity Card
                        html.Div(
                            className="reading-card humidity-card",
                            children=[
                                html.Div("💧", className="card-icon"),
                                html.H2(
                                    id="current-humidity",
                                    children="--%",
                                    className="reading-value humidity-value",
                                ),
                                html.P("Humidity", className="reading-label"),
                            ],
                        ),
                    ]
                ),
            ],
        ),
        
        # Charts Section
        html.Div(
            className="charts-section",
            children=[
                html.H3("📊 Historical Charts", className="section-title"),
                dcc.Graph(id="temperature-chart", className="chart"),
                dcc.Graph(id="humidity-chart", className="chart"),
            ],
        ),
        
        # Data Table Section
        html.Div(
            className="table-section",
            children=[
                html.H3("📋 Historical Data Table", className="section-title"),
                dash_table.DataTable(
                    id="data-table",
                    columns=[
                        {"name": "Time", "id": "timestamp", "type": "datetime"},
                        {"name": "Temperature (°C)", "id": "temperature", "type": "numeric", "format": {"specifier": ".1f"}},
                        {"name": "Humidity (%)", "id": "humidity", "type": "numeric", "format": {"specifier": ".1f"}},
                    ],
                    data=[],
                    sort_action="native",
                    page_action="native",
                    page_current=0,
                    page_size=10,
                    style_table={
                        "overflowX": "auto",
                        "borderRadius": "10px",
                        "border": "1px solid #e9ecef",
                    },
                    style_header={
                        "backgroundColor": "#f8f9fa",
                        "color": "#495057",
                        "fontWeight": "600",
                        "textAlign": "center",
                        "border": "1px solid #dee2e6",
                        "fontSize": "1rem",
                        "padding": "12px",
                    },
                    style_cell={
                        "textAlign": "center",
                        "padding": "12px",
                        "fontSize": "0.95rem",
                        "border": "1px solid #dee2e6",
                        "backgroundColor": "#ffffff",
                        "fontFamily": "'Inter', sans-serif",
                    },
                    style_data_conditional=[
                        {
                            "if": {"row_index": "odd"},
                            "backgroundColor": "#f8f9fa",
                        }
                    ],
                ),
            ],
        ),
        
        # Auto-refresh interval
        dcc.Interval(
            id="interval-component",
            interval=2 * 1000,  # Update every 2 seconds
            n_intervals=0,
        ),
        
        # Footer
        html.Div(
            className="footer",
            children=[
                html.P(
                    "🚀 DHT11 IoT Dashboard | Real-time monitoring with MQTT",
                    style={"margin": 0, "fontSize": "0.9rem"},
                ),
            ],
        ),
            ], # Close container
        ),
    ], # Close main-container
)

# Add custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            * {
                box-sizing: border-box;
            }
            
            body {
                margin: 0;
                padding: 0;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                background-color: #f5f7fa;
            }
            
            .main-container {
                min-height: 100vh;
                background-color: #f5f7fa;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 20px;
            }
            
            .control-section {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .control-card, .export-card {
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                border: 1px solid #e9ecef;
            }
            
            .button-group {
                display: flex;
                gap: 10px;
                justify-content: center;
                margin-bottom: 20px;
            }
            
            .btn {
                border: none;
                padding: 12px 25px;
                border-radius: 25px;
                cursor: pointer;
                fontSize: 1rem;
                fontWeight: 500;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
                text-align: center;
            }
            
            .btn-success {
                background-color: #27ae60;
                color: white;
                box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3);
            }
            
            .btn-success:hover {
                background-color: #219a52;
                transform: translateY(-2px);
            }
            
            .btn-danger {
                background-color: #e74c3c;
                color: white;
                box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
            }
            
            .btn-danger:hover {
                background-color: #c0392b;
                transform: translateY(-2px);
            }
            
            .btn-primary {
                background-color: #3498db;
                color: white;
                box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
            }
            
            .btn-primary:hover {
                background-color: #2980b9;
                transform: translateY(-2px);
            }
            
            .btn-full {
                width: 100%;
            }
            
            .status-display {
                text-align: center;
                fontSize: 1.2rem;
                fontWeight: 500;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 10px;
                border: 2px solid #e9ecef;
            }
            
            .record-count {
                fontSize: 1rem;
                color: #6c757d;
                margin-bottom: 15px;
                text-align: center;
            }
            
            .readings-section {
                margin-bottom: 30px;
            }
            
            .section-title {
                color: #2c3e50;
                text-align: center;
                margin-bottom: 25px;
                fontSize: 1.6rem;
                fontWeight: 500;
            }
            
            .readings-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                max-width: 800px;
                margin: 0 auto;
            }
            
            .reading-card {
                background: white;
                padding: 30px 20px;
                border-radius: 15px;
                text-align: center;
                transition: transform 0.3s ease;
                border: 2px solid;
            }
            
            .reading-card:hover {
                transform: translateY(-5px);
            }
            
            .temp-card {
                border-color: #fde8e8;
                box-shadow: 0 4px 20px rgba(231, 76, 60, 0.1);
            }
            
            .humidity-card {
                border-color: #e8f4fd;
                box-shadow: 0 4px 20px rgba(52, 152, 219, 0.1);
            }
            
            .card-icon {
                fontSize: 3rem;
                margin-bottom: 10px;
            }
            
            .reading-value {
                margin: 0;
                fontSize: 2.5rem;
                fontWeight: 600;
            }
            
            .temp-value {
                color: #e74c3c;
            }
            
            .humidity-value {
                color: #3498db;
            }
            
            .reading-label {
                margin: 10px 0 0 0;
                fontSize: 1.1rem;
                color: #6c757d;
                fontWeight: 500;
            }
            
            .charts-section, .table-section {
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                border: 1px solid #e9ecef;
                margin-bottom: 30px;
            }
            
            .chart {
                margin-bottom: 20px;
            }
            
            .data-table {
                border-radius: 10px;
                overflow: hidden;
            }
            
            .data-table .dash-table-container {
                border-radius: 10px;
            }
            
            .footer {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 15px 15px 0 0;
                margin-top: 20px;
                border: 1px solid #e9ecef;
                text-align: center;
                color: #6c757d;
            }
            
            /* Responsive Design */
            @media (max-width: 768px) {
                .control-section,
                .readings-grid {
                    grid-template-columns: 1fr;
                    gap: 15px;
                }
                
                .button-group {
                    flex-direction: column;
                    align-items: center;
                }
                
                .reading-value {
                    fontSize: 2rem;
                }
                
                .section-title {
                    fontSize: 1.4rem;
                }
                
                .control-card, .export-card, .charts-section, .table-section {
                    padding: 20px;
                }
            }
            
            @media (max-width: 480px) {
                .reading-value {
                    fontSize: 1.8rem;
                }
                
                .card-icon {
                    fontSize: 2.5rem;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


# Callback for LED control
@app.callback(
    Output("led-status", "children"),
    [Input("led-on-btn", "n_clicks"), Input("led-off-btn", "n_clicks")],
)
def control_led(on_clicks, off_clicks):
    ctx = dash.callback_context

    if not ctx.triggered:
        return f"LED Status: {led_state['status'].upper()}"

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "led-on-btn":
        publish_led_command("on")
        return "LED Status: ON"
    elif button_id == "led-off-btn":
        publish_led_command("off")
        return "LED Status: OFF"

    return f"LED Status: {led_state['status'].upper()}"


# Callback for updating current values and record count
@app.callback(
    [
        Output("current-temp", "children"),
        Output("current-humidity", "children"),
        Output("record-count", "children"),
    ],
    [Input("interval-component", "n_intervals")],
)
def update_current_values(n):
    if len(temperature_data) > 0 and len(humidity_data) > 0:
        current_temp = f"{temperature_data[-1]:.1f}°C"
        current_humidity = f"{humidity_data[-1]:.1f}%"
    else:
        current_temp = "--°C"
        current_humidity = "--%"
    
    record_count = f"Total Records: {len(temperature_data)}"
    
    return current_temp, current_humidity, record_count


# Callback for updating data table
@app.callback(
    Output("data-table", "data"),
    [Input("interval-component", "n_intervals")]
)
def update_data_table(n):
    if len(temperature_data) == 0:
        return []
    
    # Create DataFrame with latest data first
    data = []
    for i in range(len(temperature_data) - 1, -1, -1):  # Reverse order (latest first)
        data.append({
            "timestamp": timestamps[i].strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": round(temperature_data[i], 1),
            "humidity": round(humidity_data[i], 1)
        })
    
    return data


# Callback for CSV download
@app.callback(
    Output("download-dataframe-csv", "data"),
    [Input("download-btn", "n_clicks")],
    prevent_initial_call=True,
)
def download_csv(n_clicks):
    if n_clicks is None or len(temperature_data) == 0:
        return dash.no_update
    
    # Create DataFrame
    df = pd.DataFrame({
        "Timestamp": [ts.strftime("%Y-%m-%d %H:%M:%S") for ts in timestamps],
        "Temperature_C": [round(temp, 1) for temp in temperature_data],
        "Humidity_Percent": [round(hum, 1) for hum in humidity_data]
    })
    
    # Generate filename with current timestamp
    filename = f"dht11_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return dcc.send_data_frame(df.to_csv, filename, index=False)


# Callback for updating charts
@app.callback(
    [Output("temperature-chart", "figure"), Output("humidity-chart", "figure")],
    [Input("interval-component", "n_intervals")],
)
def update_charts(n):
    # Temperature chart
    temp_fig = go.Figure()
    if len(temperature_data) > 0:
        temp_fig.add_trace(
            go.Scatter(
                x=list(timestamps),
                y=list(temperature_data),
                mode="lines+markers",
                name="Temperature",
                line=dict(color="#e74c3c", width=2),
                marker=dict(size=6),
            )
        )

    temp_fig.update_layout(
        title={
            "text": "🌡️ Temperature Trend",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 18, "color": "#2c3e50"}
        },
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
        hovermode="x unified",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font={"family": "Segoe UI, sans-serif", "size": 12},
        margin={"l": 50, "r": 50, "t": 60, "b": 50},
        xaxis={"gridcolor": "#f0f0f0", "showgrid": True},
        yaxis={"gridcolor": "#f0f0f0", "showgrid": True},
    )

    # Humidity chart
    humidity_fig = go.Figure()
    if len(humidity_data) > 0:
        humidity_fig.add_trace(
            go.Scatter(
                x=list(timestamps),
                y=list(humidity_data),
                mode="lines+markers",
                name="Humidity",
                line=dict(color="#3498db", width=2),
                marker=dict(size=6),
            )
        )

    humidity_fig.update_layout(
        title={
            "text": "💧 Humidity Trend",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 18, "color": "#2c3e50"}
        },
        xaxis_title="Time",
        yaxis_title="Humidity (%)",
        hovermode="x unified",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font={"family": "Segoe UI, sans-serif", "size": 12},
        margin={"l": 50, "r": 50, "t": 60, "b": 50},
        xaxis={"gridcolor": "#f0f0f0", "showgrid": True},
        yaxis={"gridcolor": "#f0f0f0", "showgrid": True},
    )

    return temp_fig, humidity_fig


if __name__ == "__main__":
    print("Starting DHT11 Dashboard...")
    print("Dashboard will be available at: http://127.0.0.1:8050")
    app.run(debug=True, host="0.0.0.0", port=8050)
