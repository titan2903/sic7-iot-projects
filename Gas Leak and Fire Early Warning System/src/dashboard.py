#!/usr/bin/env python3
"""
Gas Leak and Fire Early Warning System - Dashboard
Modern Web Dashboard with Real-time Monitoring, MQTT, InfluxDB, and Telegram Bot Integration

Features:
- Real-time sensor data visualization with Plotly/Dash
- MQTT subscriber for live data from ESP32
- InfluxDB integration for data persistence and historical analysis
- Telegram bot for alerts and remote commands
- Remote device control via MQTT
- Modern responsive UI design
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
import json
import asyncio
import threading
from datetime import datetime, timedelta
from collections import deque
import os
from dotenv import load_dotenv

# MQTT and InfluxDB imports
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Telegram bot imports (only what we use)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

# Dashboard Configuration
DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
DASHBOARD_PORT = os.getenv("DASHBOARD_PORT", 8050)

# MQTT Configuration
MQTT_BROKER = os.getenv(
    "MQTT_BROKER", "ab36ea92cee24b64acda14d3001e34d4.s1.eu.hivemq.cloud"
)
MQTT_PORT = os.getenv("MQTT_PORT", 8883)
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "cakrawala_mqtt")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "vXtbU7m2DjTxBSLN")
MQTT_CLIENT_ID = "dashboard_client_siragas"

# MQTT Topics
TOPIC_SENSOR_DATA = "home/sensors/data"
TOPIC_SENSOR_STATUS = "home/sensors/status"
TOPIC_SENSOR_ALERTS = "home/sensors/alerts"
TOPIC_CMD_BUZZER = "home/commands/buzzer"
TOPIC_CMD_CALIBRATE = "home/commands/calibrate"
TOPIC_CONFIG_THRESHOLDS = "home/config/thresholds"

# InfluxDB Configuration
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = os.getenv(
    "INFLUXDB_TOKEN", "218af1d808eb1d5f6ab847940d5f645ad11ddf05b1644762582c9dd186364bf7"
)
INFLUXDB_ORG = "gas_monitoring_org"
INFLUXDB_BUCKET = "sensor_data"

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN", "8400886945:AAF0aQlTCgxRWqAPPFLQ_2PeW8JL5foh7H4"
)
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "388656092")

# Support multiple chat IDs (comma separated in env var)
TELEGRAM_CHAT_IDS_STR = os.getenv("TELEGRAM_CHAT_IDS", TELEGRAM_CHAT_ID)
try:
    TELEGRAM_CHAT_IDS = [
        int(x.strip()) for x in TELEGRAM_CHAT_IDS_STR.split(",") if x.strip()
    ]
except (ValueError, AttributeError):
    # Fallback to single chat ID if parsing fails
    TELEGRAM_CHAT_IDS = (
        [int(TELEGRAM_CHAT_ID)] if TELEGRAM_CHAT_ID != "388656092" else []
    )

# Dashboard Configuration
UPDATE_INTERVAL = 2000  # ms
MAX_DATA_POINTS = 200
ALERT_RETENTION_HOURS = 24

# ============================================================================
# GLOBAL VARIABLES AND DATA STORAGE
# ============================================================================

# Real-time data storage
sensor_data = deque(maxlen=MAX_DATA_POINTS)
device_status = {"online": False, "last_seen": None}
active_alerts = []
alert_history = deque(maxlen=100)

# Device control state
buzzer_state = "AUTO"
current_thresholds = {"mq2": 700, "mq5": 800}  # Sync with ESP32 default values

# Initialize clients
mqtt_client = None
influxdb_client = None
telegram_bot = None
telegram_app = None

# ============================================================================
# INFLUXDB FUNCTIONS
# ============================================================================


def init_influxdb():
    """Initialize InfluxDB client"""
    global influxdb_client
    try:
        influxdb_client = InfluxDBClient(
            url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG
        )
        # Test connection
        health = influxdb_client.health()
        print(f"InfluxDB connection: {health.status}")
        return True
    except Exception as e:
        print(f"InfluxDB connection failed: {e}")
        return False


def write_sensor_data_to_influx(data):
    """Write sensor data to InfluxDB"""
    if not influxdb_client:
        return

    try:
        write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)

        # Sensor readings point
        point = (
            Point("sensor_readings")
            .tag("device_id", "esp32_001")
            .tag("location", "main_room")
            .field("mq2_raw", int(data.get("mq2_raw", 0)))
            .field("mq2_filtered", int(data.get("mq2_filtered", 0)))
            .field("mq5_raw", int(data.get("mq5_raw", 0)))
            .field("mq5_filtered", int(data.get("mq5_filtered", 0)))
            .field("flame_digital", int(data.get("flame", 0)))
            .time(datetime.now())
        )

        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

        # Detection events point
        detection_point = (
            Point("detection_events")
            .tag("device_id", "esp32_001")
            .tag("location", "main_room")
            .field("gas_detected", bool(data.get("gas_detected", False)))
            .field("smoke_detected", bool(data.get("smoke_detected", False)))
            .field("fire_detected", bool(data.get("fire_detected", False)))
            .time(datetime.now())
        )

        write_api.write(
            bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=detection_point
        )

    except Exception as e:
        print(f"Error writing to InfluxDB: {e}")


def get_historical_data(hours=6):
    """Retrieve historical data from InfluxDB"""
    if not influxdb_client:
        return pd.DataFrame()

    try:
        query_api = influxdb_client.query_api()
        query = f"""
        from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: -{hours}h)
        |> filter(fn: (r) => r["_measurement"] == "sensor_readings")
        |> filter(fn: (r) => r["_field"] == "mq2_filtered" or r["_field"] == "mq5_filtered")
        |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
        |> yield(name: "mean")
        """

        result = query_api.query_data_frame(query=query, org=INFLUXDB_ORG)
        return result
    except Exception as e:
        print(f"Error querying InfluxDB: {e}")
        return pd.DataFrame()


# ============================================================================
# MQTT FUNCTIONS
# ============================================================================


def on_mqtt_connect(client, userdata, flags, rc):
    """MQTT connection callback"""
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe(TOPIC_SENSOR_DATA, qos=1)
        client.subscribe(TOPIC_SENSOR_STATUS, qos=1)
        client.subscribe(TOPIC_SENSOR_ALERTS, qos=1)
        client.subscribe(
            "home/config/thresholds/ack", qos=1
        )  # Subscribe to threshold confirmations

        # Request current thresholds from ESP32 on connection
        client.publish("home/commands/get_thresholds", "REQUEST", qos=1)
        print("Requested current thresholds from ESP32")
    else:
        print(f"Failed to connect to MQTT broker: {rc}")


def on_mqtt_message(client, userdata, msg):
    """MQTT message callback"""
    global sensor_data, device_status, active_alerts, alert_history

    try:
        topic = msg.topic
        payload = json.loads(msg.payload.decode())
        timestamp = datetime.now()

        if topic == TOPIC_SENSOR_DATA:
            # Add timestamp to sensor data
            payload["timestamp"] = timestamp
            sensor_data.append(payload)

            # Write to InfluxDB
            write_sensor_data_to_influx(payload)

        elif topic == TOPIC_SENSOR_STATUS:
            device_status.update(payload)
            device_status["last_seen"] = timestamp

        elif topic == TOPIC_SENSOR_ALERTS:
            alert = payload.copy()
            alert["timestamp"] = timestamp
            active_alerts.append(alert)
            alert_history.append(alert)

            # Send Telegram notification
            send_telegram_alert(alert)

        elif topic == "home/config/thresholds/ack":
            # Update dashboard threshold state from ESP32 confirmation
            global current_thresholds
            if "mq2_threshold" in payload:
                current_thresholds["mq2"] = payload["mq2_threshold"]
            if "mq5_threshold" in payload:
                current_thresholds["mq5"] = payload["mq5_threshold"]
            print(
                f"Dashboard thresholds updated from ESP32: MQ2={current_thresholds['mq2']}, MQ5={current_thresholds['mq5']}"
            )

        print(f"MQTT [{topic}]: {payload}")

    except Exception as e:
        print(f"Error processing MQTT message: {e}")


def init_mqtt():
    """Initialize MQTT client"""
    global mqtt_client
    try:
        import ssl

        mqtt_client = mqtt.Client(client_id=MQTT_CLIENT_ID)
        mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        mqtt_client.on_connect = on_mqtt_connect
        mqtt_client.on_message = on_mqtt_message

        # Configure TLS for HiveMQ Cloud (port 8883)
        if int(MQTT_PORT) == 8883:
            context = ssl.create_default_context()
            mqtt_client.tls_set_context(context)

        mqtt_client.connect(MQTT_BROKER, int(MQTT_PORT), 60)

        # Start MQTT loop in background thread
        mqtt_client.loop_start()
        print("MQTT client initialized")
        return True
    except Exception as e:
        print(f"MQTT initialization failed: {e}")
        return False


def publish_mqtt_command(topic, message):
    """Publish command to MQTT"""
    if mqtt_client and mqtt_client.is_connected():
        mqtt_client.publish(topic, message, qos=1, retain=True)
        print(f"Published to {topic}: {message}")
        return True
    return False


# ============================================================================
# TELEGRAM BOT FUNCTIONS
# ============================================================================


async def telegram_start(update, context: ContextTypes.DEFAULT_TYPE):
    """Telegram /start command"""
    await update.message.reply_text(
        "🚨 Gas Leak & Fire Early Warning System 🚨\n\n"
        "Available commands:\n"
        "/status - Get current sensor status\n"
        "/on - Turn buzzer ON\n"
        "/off - Turn buzzer OFF\n"
        "/auto - Set buzzer to AUTO mode\n"
        "/thresholds - Show current thresholds\n"
        "/reset - Reset thresholds to default values\n"
        "/history - Show last 1 hour data summary\n"
        "/help - Show this help message"
    )


async def telegram_status(update, context: ContextTypes.DEFAULT_TYPE):
    """Telegram /status command"""
    latest_data = sensor_data[-1] if sensor_data else {}
    status_text = "📊 Current Sensor Status:\n\n"

    if latest_data:
        status_text += f"🌬️ MQ-2 (Smoke): {latest_data.get('mq2_filtered', 'N/A')}\n"
        status_text += f"⛽ MQ-5 (Gas): {latest_data.get('mq5_filtered', 'N/A')}\n"
        status_text += (
            f"🔥 Flame: {'DETECTED' if latest_data.get('fire_detected') else 'OK'}\n\n"
        )

        status_text += "🚨 Detection Status:\n"
        status_text += f"💨 Smoke: {'⚠️ DETECTED' if latest_data.get('smoke_detected') else '✅ OK'}\n"
        status_text += (
            f"⛽ Gas: {'⚠️ DETECTED' if latest_data.get('gas_detected') else '✅ OK'}\n"
        )
        status_text += f"🔥 Fire: {'🚨 DETECTED' if latest_data.get('fire_detected') else '✅ OK'}\n"
    else:
        status_text += "❌ No data available"

    status_text += (
        f"\n🌐 Device: {'🟢 Online' if device_status.get('online') else '🔴 Offline'}"
    )

    await update.message.reply_text(status_text)


async def telegram_buzzer_on(update, context: ContextTypes.DEFAULT_TYPE):
    """Telegram /on command"""
    if publish_mqtt_command(TOPIC_CMD_BUZZER, "ON"):
        await update.message.reply_text("🔊 Buzzer turned ON")
    else:
        await update.message.reply_text("❌ Failed to send command")


async def telegram_buzzer_off(update, context: ContextTypes.DEFAULT_TYPE):
    """Telegram /off command"""
    if publish_mqtt_command(TOPIC_CMD_BUZZER, "OFF"):
        await update.message.reply_text("🔇 Buzzer turned OFF")
    else:
        await update.message.reply_text("❌ Failed to send command")


async def telegram_buzzer_auto(update, context: ContextTypes.DEFAULT_TYPE):
    """Telegram /auto command"""
    if publish_mqtt_command(TOPIC_CMD_BUZZER, "AUTO"):
        await update.message.reply_text("🔄 Buzzer set to AUTO mode")
    else:
        await update.message.reply_text("❌ Failed to send command")


async def telegram_thresholds(update, context: ContextTypes.DEFAULT_TYPE):
    """Telegram /thresholds command"""
    latest_data = sensor_data[-1] if sensor_data else {}

    thresholds_text = "⚙️ Current Thresholds:\n\n"
    thresholds_text += f"🌬️ MQ-2 (Smoke): {current_thresholds['mq2']}\n"
    thresholds_text += f"⛽ MQ-5 (Gas): {current_thresholds['mq5']}\n\n"

    if latest_data:
        thresholds_text += "📊 Current Values:\n"
        thresholds_text += f"🌬️ MQ-2: {latest_data.get('mq2_filtered', 'N/A')}\n"
        thresholds_text += f"⛽ MQ-5: {latest_data.get('mq5_filtered', 'N/A')}"

    await update.message.reply_text(thresholds_text)


async def telegram_reset_thresholds(update, context: ContextTypes.DEFAULT_TYPE):
    """Telegram /reset command - reset thresholds to default values"""
    if publish_mqtt_command("home/commands/reset_thresholds", "RESET"):
        await update.message.reply_text(
            "🔄 Threshold reset command sent to ESP32\n"
            "Default values:\n"
            "🌬️ MQ-2 (Smoke): 700\n"
            "⛽ MQ-5 (Gas): 800"
        )
    else:
        await update.message.reply_text("❌ Failed to send reset command")


async def telegram_history(update, context: ContextTypes.DEFAULT_TYPE):
    """Telegram /history command - show last 1 hour data summary"""
    try:
        # Get last 1 hour of data from InfluxDB
        df = get_historical_data(hours=1)

        if df.empty:
            await update.message.reply_text(
                "📊 No historical data available for the last hour"
            )
            return

        # Process data for summary
        history_text = "📈 Last 1 Hour Summary:\n\n"

        # Get MQ2 data
        mq2_data = df[df["_field"] == "mq2_filtered"]
        if not mq2_data.empty:
            mq2_avg = mq2_data["_value"].mean()
            mq2_max = mq2_data["_value"].max()
            mq2_min = mq2_data["_value"].min()
            history_text += f"🌬️ MQ-2 (Smoke):\n"
            history_text += f"   • Average: {mq2_avg:.1f}\n"
            history_text += f"   • Max: {mq2_max:.1f}\n"
            history_text += f"   • Min: {mq2_min:.1f}\n\n"

        # Get MQ5 data
        mq5_data = df[df["_field"] == "mq5_filtered"]
        if not mq5_data.empty:
            mq5_avg = mq5_data["_value"].mean()
            mq5_max = mq5_data["_value"].max()
            mq5_min = mq5_data["_value"].min()
            history_text += f"⛽ MQ-5 (Gas):\n"
            history_text += f"   • Average: {mq5_avg:.1f}\n"
            history_text += f"   • Max: {mq5_max:.1f}\n"
            history_text += f"   • Min: {mq5_min:.1f}\n\n"

        # Add alert summary from last hour
        current_time = datetime.now()
        one_hour_ago = current_time - timedelta(hours=1)
        recent_alerts = [
            alert
            for alert in alert_history
            if alert.get("timestamp", current_time) >= one_hour_ago
        ]

        if recent_alerts:
            history_text += f"🚨 Alerts (Last Hour): {len(recent_alerts)}\n"
            alert_types = {}
            for alert in recent_alerts:
                alert_type = alert.get("alert_type", "unknown")
                alert_types[alert_type] = alert_types.get(alert_type, 0) + 1

            for alert_type, count in alert_types.items():
                history_text += f"   • {alert_type.title()}: {count}\n"
        else:
            history_text += "✅ No alerts in the last hour"

        await update.message.reply_text(history_text)

    except Exception as e:
        print(f"Error in telegram_history: {e}")
        await update.message.reply_text("❌ Failed to retrieve historical data")


def send_telegram_alert(alert):
    """Send alert notification to Telegram"""
    if not telegram_bot or not TELEGRAM_CHAT_IDS:
        return

    alert_type = alert.get("alert_type", "unknown")
    severity = alert.get("severity", "info")

    emoji_map = {"gas": "⛽", "smoke": "💨", "fire": "🔥", "multi": "🚨"}

    emoji = emoji_map.get(alert_type, "⚠️")

    message = f"{emoji} {alert_type.upper()} DETECTED! {emoji}\n"
    message += f"Device: ESP32_001\n"
    message += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    message += f"Severity: {severity.upper()}\n"

    # Send to all configured chat IDs (personal and groups)
    for chat_id in TELEGRAM_CHAT_IDS:
        try:
            # Send message in background thread
            asyncio.create_task(
                telegram_bot.send_message(chat_id=chat_id, text=message)
            )
        except Exception as e:
            print(f"Failed to send Telegram alert to chat {chat_id}: {e}")


def init_telegram():
    """Initialize Telegram bot"""
    global telegram_bot, telegram_app
    try:
        if TELEGRAM_BOT_TOKEN == "your_telegram_bot_token_here":
            print("Telegram bot token not configured")
            return False

        telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        telegram_bot = telegram_app.bot

        # Add command handlers
        telegram_app.add_handler(CommandHandler("start", telegram_start))
        telegram_app.add_handler(CommandHandler("help", telegram_start))
        telegram_app.add_handler(CommandHandler("status", telegram_status))
        telegram_app.add_handler(CommandHandler("on", telegram_buzzer_on))
        telegram_app.add_handler(CommandHandler("off", telegram_buzzer_off))
        telegram_app.add_handler(CommandHandler("auto", telegram_buzzer_auto))
        telegram_app.add_handler(CommandHandler("thresholds", telegram_thresholds))
        telegram_app.add_handler(CommandHandler("reset", telegram_reset_thresholds))
        telegram_app.add_handler(CommandHandler("history", telegram_history))

        # Start bot in background thread
        def run_telegram():
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop()
            # Initialize the app before running
            loop.run_until_complete(telegram_app.initialize())
            # Disable signal handling to avoid set_wakeup_fd error in non-main thread
            telegram_app.run_polling(stop_signals=None)

        telegram_thread = threading.Thread(target=run_telegram, daemon=True)
        telegram_thread.start()

        print("Telegram bot initialized")
        return True
    except Exception as e:
        print(f"Telegram initialization failed: {e}")
        return False


# ============================================================================
# DASH APPLICATION AND UI
# ============================================================================

# Initialize Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Gas Leak & Fire Early Warning System"

# Custom CSS styling
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body { background-color: #f8f9fa; }
            .card { box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075); }
            .status-ok { color: #28a745; }
            .status-alert { color: #ffc107; }
            .status-danger { color: #dc3545; }
            .status-critical { color: #721c24; }
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
"""


def create_layout():
    """Create the dashboard layout"""
    return dbc.Container(
        [
            # Header
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H1(
                                "Gas Leak & Fire Early Warning System",
                                className="text-center mb-4 mt-3",
                            ),
                            html.Hr(),
                        ]
                    )
                ]
            ),
            # System Status Cards
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            html.H4(
                                                "System Status",
                                                className="card-title",
                                            ),
                                            html.H2(
                                                id="system-status",
                                                className="text-center",
                                            ),
                                            html.P(
                                                id="device-status",
                                                className="text-center text-muted",
                                            ),
                                        ]
                                    )
                                ],
                                color="light",
                                outline=True,
                            )
                        ],
                        md=3,
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            html.H4(
                                                "Smoke Level", className="card-title"
                                            ),
                                            html.H2(
                                                id="smoke-level",
                                                className="text-center",
                                            ),
                                            html.P(
                                                "MQ-2 Sensor",
                                                className="text-center text-muted",
                                            ),
                                        ]
                                    )
                                ],
                                color="light",
                                outline=True,
                            )
                        ],
                        md=3,
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            html.H4(
                                                "Gas Level", className="card-title"
                                            ),
                                            html.H2(
                                                id="gas-level", className="text-center"
                                            ),
                                            html.P(
                                                "MQ-5 Sensor",
                                                className="text-center text-muted",
                                            ),
                                        ]
                                    )
                                ],
                                color="light",
                                outline=True,
                            )
                        ],
                        md=3,
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            html.H4(
                                                "Flame Sensor",
                                                className="card-title",
                                            ),
                                            html.H2(
                                                id="flame-status",
                                                className="text-center",
                                            ),
                                            html.P(
                                                "Digital Sensor",
                                                className="text-center text-muted",
                                            ),
                                        ]
                                    )
                                ],
                                color="light",
                                outline=True,
                            )
                        ],
                        md=3,
                    ),
                ],
                className="mb-4",
            ),
            # Real-time Charts
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Real-time Sensor Data"),
                                    dbc.CardBody([dcc.Graph(id="realtime-chart")]),
                                ]
                            )
                        ],
                        md=8,
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Control Panel"),
                                    dbc.CardBody(
                                        [
                                            html.H5("Buzzer Control"),
                                            dbc.ButtonGroup(
                                                [
                                                    dbc.Button(
                                                        "ON",
                                                        id="buzzer-on-btn",
                                                        color="danger",
                                                        size="sm",
                                                    ),
                                                    dbc.Button(
                                                        "OFF",
                                                        id="buzzer-off-btn",
                                                        color="secondary",
                                                        size="sm",
                                                    ),
                                                    dbc.Button(
                                                        "AUTO",
                                                        id="buzzer-auto-btn",
                                                        color="success",
                                                        size="sm",
                                                    ),
                                                ],
                                                className="mb-3",
                                            ),
                                            html.Hr(),
                                            html.H5("⚙️ Thresholds"),
                                            html.P("MQ-2 (Smoke):", className="mb-1"),
                                            dcc.Slider(
                                                id="mq2-threshold-slider",
                                                min=600,
                                                max=2000,
                                                step=50,
                                                value=1300,
                                                marks={
                                                    i: str(i)
                                                    for i in range(600, 2001, 300)
                                                },
                                                tooltip={
                                                    "placement": "bottom",
                                                    "always_visible": True,
                                                },
                                            ),
                                            html.P(
                                                "MQ-5 (Gas):", className="mb-1 mt-3"
                                            ),
                                            dcc.Slider(
                                                id="mq5-threshold-slider",
                                                min=500,
                                                max=1500,
                                                step=50,
                                                value=950,
                                                marks={
                                                    i: str(i)
                                                    for i in range(500, 1501, 200)
                                                },
                                                tooltip={
                                                    "placement": "bottom",
                                                    "always_visible": True,
                                                },
                                            ),
                                            dbc.Button(
                                                "Update Thresholds",
                                                id="update-thresholds-btn",
                                                color="primary",
                                                size="sm",
                                                className="mt-3 me-2",
                                            ),
                                            dbc.Button(
                                                "Reset to Default",
                                                id="reset-thresholds-btn",
                                                color="warning",
                                                size="sm",
                                                className="mt-3",
                                            ),
                                        ]
                                    ),
                                ]
                            )
                        ],
                        md=4,
                    ),
                ],
                className="mb-4",
            ),
            # Historical Data and Alerts
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Historical Data"),
                                    dbc.CardBody(
                                        [
                                            dbc.ButtonGroup(
                                                [
                                                    dbc.Button(
                                                        "1H",
                                                        id="hist-1h-btn",
                                                        color="outline-primary",
                                                        size="sm",
                                                    ),
                                                    dbc.Button(
                                                        "6H",
                                                        id="hist-6h-btn",
                                                        color="primary",
                                                        size="sm",
                                                    ),
                                                    dbc.Button(
                                                        "24H",
                                                        id="hist-24h-btn",
                                                        color="outline-primary",
                                                        size="sm",
                                                    ),
                                                ],
                                                className="mb-3",
                                            ),
                                            dcc.Graph(id="historical-chart"),
                                        ]
                                    ),
                                ]
                            )
                        ],
                        md=8,
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Recent Alerts"),
                                    dbc.CardBody([html.Div(id="alerts-list")]),
                                ]
                            )
                        ],
                        md=4,
                    ),
                ]
            ),
            # Auto-refresh component
            dcc.Interval(
                id="interval-component", interval=UPDATE_INTERVAL, n_intervals=0
            ),
            # Hidden divs for storing data
            html.Div(
                id="historical-timeframe", children="6", style={"display": "none"}
            ),
        ],
        fluid=True,
    )


app.layout = create_layout()

# ============================================================================
# DASH CALLBACKS
# ============================================================================


@app.callback(
    [
        Output("system-status", "children"),
        Output("system-status", "className"),
        Output("device-status", "children"),
        Output("smoke-level", "children"),
        Output("smoke-level", "className"),
        Output("gas-level", "children"),
        Output("gas-level", "className"),
        Output("flame-status", "children"),
        Output("flame-status", "className"),
    ],
    [Input("interval-component", "n_intervals")],
)
def update_status_cards(n):
    """Update system status cards"""
    if not sensor_data:
        return (
            "NO DATA",
            "text-danger",
            "Device Offline",
            "N/A",
            "text-muted",
            "N/A",
            "text-muted",
            "N/A",
            "text-muted",
        )

    latest = sensor_data[-1]

    # System status
    if latest.get("fire_detected") and (
        latest.get("smoke_detected") or latest.get("gas_detected")
    ):
        system_status = "CRITICAL"
        system_class = "text-danger"
    elif latest.get("fire_detected"):
        system_status = "DANGER"
        system_class = "text-warning"
    elif latest.get("smoke_detected") or latest.get("gas_detected"):
        system_status = "ALERT"
        system_class = "text-warning"
    else:
        system_status = "OK"
        system_class = "text-success"

    # Device status
    last_seen = device_status.get("last_seen")
    if last_seen and (datetime.now() - last_seen).seconds < 30:
        device_text = "🟢 Online"
    else:
        device_text = "🔴 Offline"

    # Sensor values
    smoke_val = latest.get("mq2_filtered", 0)
    gas_val = latest.get("mq5_filtered", 0)

    smoke_class = "text-danger" if latest.get("smoke_detected") else "text-success"
    gas_class = "text-danger" if latest.get("gas_detected") else "text-success"

    flame_status = "🔥 DETECTED" if latest.get("fire_detected") else "✅ OK"
    flame_class = "text-danger" if latest.get("fire_detected") else "text-success"

    return (
        system_status,
        system_class,
        device_text,
        str(smoke_val),
        smoke_class,
        str(gas_val),
        gas_class,
        flame_status,
        flame_class,
    )


@app.callback(
    Output("realtime-chart", "figure"), [Input("interval-component", "n_intervals")]
)
def update_realtime_chart(n):
    """Update real-time sensor chart"""
    if not sensor_data:
        return go.Figure().add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )

    # Convert to DataFrame
    df = pd.DataFrame(list(sensor_data))
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    fig = go.Figure()

    # Add traces
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["mq2_filtered"],
            mode="lines",
            name="MQ-2 (Smoke)",
            line=dict(color="blue", width=2),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["mq5_filtered"],
            mode="lines",
            name="MQ-5 (Gas)",
            line=dict(color="orange", width=2),
        )
    )

    # Add threshold lines
    fig.add_hline(
        y=current_thresholds["mq2"],
        line_dash="dash",
        line_color="blue",
        opacity=0.5,
        annotation_text="MQ-2 Threshold",
    )
    fig.add_hline(
        y=current_thresholds["mq5"],
        line_dash="dash",
        line_color="orange",
        opacity=0.5,
        annotation_text="MQ-5 Threshold",
    )

    fig.update_layout(
        title="Real-time Sensor Readings",
        xaxis_title="Time",
        yaxis_title="Sensor Value",
        hovermode="x unified",
        height=400,
    )

    return fig


@app.callback(
    Output("historical-chart", "figure"),
    [
        Input("hist-1h-btn", "n_clicks"),
        Input("hist-6h-btn", "n_clicks"),
        Input("hist-24h-btn", "n_clicks"),
        Input("interval-component", "n_intervals"),
    ],
    [State("historical-timeframe", "children")],
)
def update_historical_chart(btn1, btn6, btn24, n, current_timeframe):
    """Update historical data chart"""
    ctx = callback_context
    timeframe = int(current_timeframe) if current_timeframe else 6

    if ctx.triggered:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id == "hist-1h-btn":
            timeframe = 1
        elif button_id == "hist-6h-btn":
            timeframe = 6
        elif button_id == "hist-24h-btn":
            timeframe = 24

    # Get historical data from InfluxDB
    df = get_historical_data(hours=timeframe)

    if df.empty:
        return go.Figure().add_annotation(
            text="No historical data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )

    fig = go.Figure()

    # Process InfluxDB data
    if "_time" in df.columns:
        for field in ["mq2_filtered", "mq5_filtered"]:
            field_data = df[df["_field"] == field]
            if not field_data.empty:
                color = "blue" if field == "mq2_filtered" else "orange"
                name = "MQ-2 (Smoke)" if field == "mq2_filtered" else "MQ-5 (Gas)"

                fig.add_trace(
                    go.Scatter(
                        x=field_data["_time"],
                        y=field_data["_value"],
                        mode="lines",
                        name=name,
                        line=dict(color=color, width=2),
                    )
                )

    fig.update_layout(
        title=f"Historical Data ({timeframe}H)",
        xaxis_title="Time",
        yaxis_title="Sensor Value",
        hovermode="x unified",
        height=400,
    )

    return fig


@app.callback(
    Output("alerts-list", "children"), [Input("interval-component", "n_intervals")]
)
def update_alerts_list(n):
    """Update alerts list"""
    if not alert_history:
        return html.P("No recent alerts", className="text-muted")

    # Get recent alerts (last 10)
    recent_alerts = list(alert_history)[-10:]
    recent_alerts.reverse()  # Most recent first

    alerts_components = []
    for alert in recent_alerts:
        timestamp = alert.get("timestamp", datetime.now())
        alert_type = alert.get("alert_type", "unknown")
        severity = alert.get("severity", "info")

        emoji_map = {"gas": "⛽", "smoke": "💨", "fire": "🔥", "multi": "🚨"}

        color_map = {
            "info": "light",
            "alert": "warning",
            "danger": "danger",
            "critical": "danger",
        }

        emoji = emoji_map.get(alert_type, "⚠️")
        color = color_map.get(severity, "light")

        alerts_components.append(
            dbc.Alert(
                [
                    html.Strong(f"{emoji} {alert_type.upper()}"),
                    html.Br(),
                    html.Small(timestamp.strftime("%H:%M:%S")),
                    html.Br(),
                    html.Small(f"Severity: {severity}"),
                ],
                color=color,
                className="mb-2",
            )
        )

    return alerts_components


# Buzzer control callbacks
@app.callback(Output("buzzer-on-btn", "disabled"), [Input("buzzer-on-btn", "n_clicks")])
def buzzer_on_click(n_clicks):
    if n_clicks:
        publish_mqtt_command(TOPIC_CMD_BUZZER, "ON")
        global buzzer_state
        buzzer_state = "ON"
    return False


@app.callback(
    Output("buzzer-off-btn", "disabled"), [Input("buzzer-off-btn", "n_clicks")]
)
def buzzer_off_click(n_clicks):
    if n_clicks:
        publish_mqtt_command(TOPIC_CMD_BUZZER, "OFF")
        global buzzer_state
        buzzer_state = "OFF"
    return False


@app.callback(
    Output("buzzer-auto-btn", "disabled"), [Input("buzzer-auto-btn", "n_clicks")]
)
def buzzer_auto_click(n_clicks):
    if n_clicks:
        publish_mqtt_command(TOPIC_CMD_BUZZER, "AUTO")
        global buzzer_state
        buzzer_state = "AUTO"
    return False


@app.callback(
    Output("update-thresholds-btn", "disabled"),
    [Input("update-thresholds-btn", "n_clicks")],
    [State("mq2-threshold-slider", "value"), State("mq5-threshold-slider", "value")],
)
def update_thresholds(n_clicks, mq2_val, mq5_val):
    if n_clicks:
        thresholds = {"mq2_threshold": mq2_val, "mq5_threshold": mq5_val}
        publish_mqtt_command(TOPIC_CONFIG_THRESHOLDS, json.dumps(thresholds))

        global current_thresholds
        current_thresholds["mq2"] = mq2_val
        current_thresholds["mq5"] = mq5_val
    return False


@app.callback(
    Output("reset-thresholds-btn", "disabled"),
    [Input("reset-thresholds-btn", "n_clicks")],
)
def reset_thresholds(n_clicks):
    if n_clicks:
        # Send reset command to ESP32
        publish_mqtt_command("home/commands/reset_thresholds", "RESET")

        # Update local threshold values to defaults
        global current_thresholds
        current_thresholds["mq2"] = 700  # Default ESP32 values
        current_thresholds["mq5"] = 800  # Default ESP32 values
    return False


@app.callback(
    [Output("mq2-threshold-slider", "value"), Output("mq5-threshold-slider", "value")],
    [
        Input("reset-thresholds-btn", "n_clicks"),
        Input("interval-component", "n_intervals"),
    ],
)
def update_threshold_sliders(reset_clicks, n_intervals):
    """Update threshold sliders when reset is clicked or ESP32 sends new values"""
    ctx = callback_context

    if ctx.triggered:
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # If reset button was clicked, set to default values
        if trigger_id == "reset-thresholds-btn" and reset_clicks:
            return 700, 800  # Default ESP32 values

    # Otherwise return current threshold values (updated from ESP32)
    return current_thresholds["mq2"], current_thresholds["mq5"]


@app.callback(
    Output("historical-timeframe", "children"),
    [
        Input("hist-1h-btn", "n_clicks"),
        Input("hist-6h-btn", "n_clicks"),
        Input("hist-24h-btn", "n_clicks"),
    ],
)
def update_timeframe(btn1, btn6, btn24):
    ctx = callback_context
    if ctx.triggered:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id == "hist-1h-btn":
            return "1"
        elif button_id == "hist-6h-btn":
            return "6"
        elif button_id == "hist-24h-btn":
            return "24"
    return "6"


# ============================================================================
# MAIN APPLICATION
# ============================================================================


def main():
    """Main application entry point"""
    print("🚨 Gas Leak & Fire Early Warning System Dashboard")
    print("=" * 60)

    # Initialize services
    print("Initializing services...")

    # Initialize InfluxDB
    if init_influxdb():
        print("✅ InfluxDB connected")
    else:
        print("❌ InfluxDB connection failed")

    # Initialize MQTT
    if init_mqtt():
        print("✅ MQTT connected")
    else:
        print("❌ MQTT connection failed")

    # Initialize Telegram bot
    if init_telegram():
        print("✅ Telegram bot initialized")
    else:
        print("❌ Telegram bot initialization failed")

    print("=" * 60)
    print("🌐 Starting dashboard server...")
    print("📊 Dashboard URL: http://localhost:8050")
    print("🔄 Auto-refresh: 2 seconds")
    print("=" * 60)

    # Start Dash server
    app.run(debug=False, host=DASHBOARD_HOST, port=DASHBOARD_PORT)


if __name__ == "__main__":
    main()
