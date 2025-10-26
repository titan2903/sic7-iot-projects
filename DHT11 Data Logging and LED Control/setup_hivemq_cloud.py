#!/usr/bin/env python3
"""
HiveMQ Cloud Configuration Helper
Helps setup HiveMQ Cloud credentials for DHT11 project
"""

import os
import re
import sys


def setup_hivemq_cloud_config():
    """Interactive setup for HiveMQ Cloud credentials"""

    print("HiveMQ Cloud Configuration Helper")
    print("=" * 50)
    print()

    # Get HiveMQ Cloud credentials
    print("Please enter your HiveMQ Cloud credentials:")
    print("   (You can find these in HiveMQ Cloud Console)")
    print()

    # Get cluster host
    cluster_host = input("Cluster Host (e.g., abc123def.s1.hivemq.cloud): ").strip()
    if not cluster_host or not cluster_host.endswith(".s1.hivemq.cloud"):
        print("❌ Invalid cluster host format!")
        print("   Expected format: xxxxxxxxx.s1.hivemq.cloud")
        return False

    # Get username and password
    username = input("Username: ").strip()
    if not username:
        print("❌ Username cannot be empty!")
        return False

    password = input("Password: ").strip()
    if not password:
        print("❌ Password cannot be empty!")
        return False

    print()
    print("Updating configuration files...")

    # Update files
    files_updated = 0

    # Update main.cpp
    main_cpp_path = "src/main.cpp"
    if update_main_cpp(main_cpp_path, cluster_host, username, password):
        files_updated += 1
    print(f"Updated {main_cpp_path}")

    # Update subscribe_dht.py
    subscribe_py_path = "src/subscribe_dht.py"
    if update_python_script(subscribe_py_path, cluster_host, username, password):
        files_updated += 1
    print(f"Updated {subscribe_py_path}")

    # Update publish_led_control.py
    publish_py_path = "src/publish_led_control.py"
    if update_python_script(publish_py_path, cluster_host, username, password):
        files_updated += 1
    print(f"Updated {publish_py_path}")

    # Update MQTTX profile
    mqttx_profile_path = "mqttx_hivemq_cloud_profile.json"
    if update_mqttx_profile(mqttx_profile_path, cluster_host, username, password):
        files_updated += 1
    print(f"Updated {mqttx_profile_path}")

    print()
    print(f"Configuration complete! Updated {files_updated} files.")
    print()
    print("Next steps:")
    print("   1. Upload firmware to ESP32")
    print("   2. Test Python scripts: python3 src/subscribe_dht.py")
    print("   3. Import MQTTX profile from mqttx_hivemq_cloud_profile.json")
    print()
    print("📖 For detailed setup guide, see: HIVEMQ_CLOUD_SETUP.md")

    return True


def update_main_cpp(file_path, cluster_host, username, password):
    """Update main.cpp with HiveMQ Cloud credentials"""
    try:
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False

        with open(file_path, "r") as file:
            content = file.read()

        # Replace placeholders
        content = re.sub(
            r'const char\* mqtt_server = "YOUR_CLUSTER_HOST\.s1\.hivemq\.cloud";',
            f'const char* mqtt_server = "{cluster_host}";',
            content,
        )

        content = re.sub(
            r'const char\* mqtt_user = "YOUR_HIVEMQ_USERNAME";',
            f'const char* mqtt_user = "{username}";',
            content,
        )

        content = re.sub(
            r'const char\* mqtt_pass = "YOUR_HIVEMQ_PASSWORD";',
            f'const char* mqtt_pass = "{password}";',
            content,
        )

        with open(file_path, "w") as file:
            file.write(content)

        return True

    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False


def update_python_script(file_path, cluster_host, username, password):
    """Update Python script with HiveMQ Cloud credentials"""
    try:
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False

        with open(file_path, "r") as file:
            content = file.read()

        # Replace placeholders
        content = re.sub(
            r'MQTT_BROKER = "YOUR_CLUSTER_HOST\.s1\.hivemq\.cloud"',
            f'MQTT_BROKER = "{cluster_host}"',
            content,
        )

        content = re.sub(
            r'MQTT_USERNAME = "YOUR_HIVEMQ_USERNAME"',
            f'MQTT_USERNAME = "{username}"',
            content,
        )

        content = re.sub(
            r'MQTT_PASSWORD = "YOUR_HIVEMQ_PASSWORD"',
            f'MQTT_PASSWORD = "{password}"',
            content,
        )

        with open(file_path, "w") as file:
            file.write(content)

        return True

    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False


def update_mqttx_profile(file_path, cluster_host, username, password):
    """Update MQTTX profile with HiveMQ Cloud credentials"""
    try:
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False

        with open(file_path, "r") as file:
            content = file.read()

        # Replace placeholders
        content = re.sub(
            r'"host": "YOUR_CLUSTER_HOST\.s1\.hivemq\.cloud"',
            f'"host": "{cluster_host}"',
            content,
        )

        content = re.sub(
            r'"username": "YOUR_HIVEMQ_USERNAME"', f'"username": "{username}"', content
        )

        content = re.sub(
            r'"password": "YOUR_HIVEMQ_PASSWORD"', f'"password": "{password}"', content
        )

        with open(file_path, "w") as file:
            file.write(content)

        return True

    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False


def main():
    """Main function"""
    # Change to project directory
    project_dir = "/home/titan/PlatformIO/Projects/DHT11 Data Logging and LED Control"

    if os.path.exists(project_dir):
        os.chdir(project_dir)
        print(f"Working directory: {project_dir}")
        print()
    else:
        print(f"Project directory not found: {project_dir}")
        return 1

    # Run setup
    if setup_hivemq_cloud_config():
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
