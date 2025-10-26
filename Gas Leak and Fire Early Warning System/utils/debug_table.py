#!/usr/bin/env python3
"""
Test script untuk debug masalah tabel sensor data
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import semua yang diperlukan
from influxdb_client import InfluxDBClient
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# InfluxDB Configuration
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = os.getenv(
    "INFLUXDB_TOKEN", "218af1d808eb1d5f6ab847940d5f645ad11ddf05b1644762582c9dd186364bf7"
)
INFLUXDB_ORG = "gas_monitoring_org"
INFLUXDB_BUCKET = "sensor_data"


def test_influxdb_connection():
    """Test koneksi InfluxDB"""
    try:
        client = InfluxDBClient(
            url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG
        )
        health = client.health()
        print(f"✅ InfluxDB connection: {health.status}")
        return client
    except Exception as e:
        print(f"❌ InfluxDB connection failed: {e}")
        return None


def test_measurements():
    """Test apakah ada data di measurement sensor_readings"""
    client = test_influxdb_connection()
    if not client:
        return

    try:
        query_api = client.query_api()

        # Query untuk cek ada measurement apa aja
        print("\n🔍 Checking available measurements...")
        measurements_query = f"""
        import "influxdata/influxdb/schema"
        schema.measurements(bucket: "{INFLUXDB_BUCKET}")
        """

        measurements = query_api.query_data_frame(
            query=measurements_query, org=INFLUXDB_ORG
        )
        if not measurements.empty and "_value" in measurements.columns:
            print("📊 Available measurements:")
            for measurement in measurements["_value"].unique():
                print(f"  - {measurement}")
        else:
            print("❌ No measurements found or empty result")

        # Query untuk cek fields di sensor_readings
        print("\n🔍 Checking fields in sensor_readings measurement...")
        fields_query = f"""
        import "influxdata/influxdb/schema"
        schema.fieldKeys(bucket: "{INFLUXDB_BUCKET}", measurement: "sensor_readings")
        """

        fields = query_api.query_data_frame(query=fields_query, org=INFLUXDB_ORG)
        if not fields.empty and "_value" in fields.columns:
            print("📊 Available fields in sensor_readings:")
            for field in fields["_value"].unique():
                print(f"  - {field}")
        else:
            print("❌ No fields found in sensor_readings or measurement doesn't exist")

        # Test actual data query
        print("\n🔍 Testing actual data query...")
        test_query = f"""
        from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: -24h)
        |> filter(fn: (r) => r["_measurement"] == "sensor_readings")
        |> limit(n: 5)
        """

        test_data = query_api.query_data_frame(query=test_query, org=INFLUXDB_ORG)
        if not test_data.empty:
            print(f"✅ Found {len(test_data)} data points in last 24h")
            print("📋 Sample columns:", list(test_data.columns))
            if "_field" in test_data.columns:
                print("📋 Available fields:", test_data["_field"].unique())
        else:
            print("❌ No data found in sensor_readings measurement")

    except Exception as e:
        print(f"❌ Error testing measurements: {e}")


def test_historical_data_table_function():
    """Test fungsi get_historical_data_table"""
    client = test_influxdb_connection()
    if not client:
        return

    print("\n🔍 Testing get_historical_data_table function...")

    try:
        query_api = client.query_api()

        # Test query yang sama dengan get_historical_data_table
        query = f"""
        from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: -6h)
        |> filter(fn: (r) => r["_measurement"] == "sensor_readings")
        |> filter(fn: (r) => r["_field"] == "mq2_raw" or 
                           r["_field"] == "mq2_filtered" or 
                           r["_field"] == "mq5_raw" or 
                           r["_field"] == "mq5_filtered" or 
                           r["_field"] == "flame_digital")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> sort(columns: ["_time"], desc: true)
        """

        print("📝 Executing query...")
        df_raw = query_api.query_data_frame(query=query, org=INFLUXDB_ORG)

        if df_raw is None or df_raw.empty:
            print("❌ Query returned empty DataFrame")
            return

        print(f"✅ Query returned {len(df_raw)} rows")
        print("📋 Columns:", list(df_raw.columns))
        print("📋 First few rows:")
        print(df_raw.head())

        # Test processing seperti di fungsi asli
        df = df_raw.copy()

        if "_time" in df.columns:
            df = df.rename(columns={"_time": "time"})

        if "time" in df.columns:
            df["Time"] = pd.to_datetime(df["time"]).dt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            df["Time"] = ""

        # Check if required fields exist
        required_fields = [
            "mq2_raw",
            "mq2_filtered",
            "mq5_raw",
            "mq5_filtered",
            "flame_digital",
        ]
        missing_fields = [field for field in required_fields if field not in df.columns]

        if missing_fields:
            print(f"⚠️  Missing fields: {missing_fields}")
        else:
            print("✅ All required fields present")

        # Process data
        df["MQ2 Raw"] = df.get("mq2_raw", pd.Series()).fillna(0).round(0).astype(int)
        df["MQ2 Filtered"] = (
            df.get("mq2_filtered", pd.Series()).fillna(0).round(0).astype(int)
        )
        df["MQ5 Raw"] = df.get("mq5_raw", pd.Series()).fillna(0).round(0).astype(int)
        df["MQ5 Filtered"] = (
            df.get("mq5_filtered", pd.Series()).fillna(0).round(0).astype(int)
        )
        df["Flame Status"] = (
            df.get("flame_digital", pd.Series())
            .fillna(0)
            .apply(lambda x: "Detected" if x == 1 else "Normal")
        )

        result_df = df[
            [
                "Time",
                "MQ2 Raw",
                "MQ2 Filtered",
                "MQ5 Raw",
                "MQ5 Filtered",
                "Flame Status",
            ]
        ]

        print(f"\n✅ Final processed DataFrame: {len(result_df)} rows")
        print("📋 Final columns:", list(result_df.columns))
        print("📋 Sample data:")
        print(result_df.head())

    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("🧪 Debug Script - Sensor Data Table Issue")
    print("=" * 50)

    test_measurements()
    test_historical_data_table_function()

    print("\n✨ Debug completed!")
