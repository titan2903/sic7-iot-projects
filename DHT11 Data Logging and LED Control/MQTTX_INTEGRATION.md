# 🔄 MQTTX Integration Guide

## 📱 **MQTTX Desktop App Integration**

Dengan MQTTX desktop app, Anda memiliki beberapa opsi penggunaan yang fleksibel:

### **🎯 Option 1: Full MQTTX (Tanpa Python Scripts)**
```
ESP32 ←→ MQTT Broker ←→ MQTTX Desktop App
```
- Subscribe DHT11 data di MQTTX
- Publish LED commands dari MQTTX
- Visual monitoring dan control

### **🎯 Option 2: Hybrid - MQTTX untuk Monitoring + Python untuk Control**
```
ESP32 ←→ MQTT Broker ←→ MQTTX (Subscribe DHT11)
                    ←→ Python (Publish LED Commands)
```

### **🎯 Option 3: Hybrid - Python untuk Monitoring + MQTTX untuk Control**
```
ESP32 ←→ MQTT Broker ←→ Python (Subscribe DHT11)
                    ←→ MQTTX (Publish LED Commands)
```

### **🎯 Option 4: Development Setup (All Clients)**
```
ESP32 ←→ MQTT Broker ←→ MQTTX (GUI Monitoring)
                    ←→ Python Subscribe (CSV Logging)
                    ←→ Python Publish (Automated Control)
```

## ⚙️ **MQTTX Configuration**

### **Connection Settings:**
```
Name: DHT11 System Monitor
Host: broker.hivemq.com
Port: 1883
Protocol: mqtt://
Client ID: mqttx_dht11_monitor
Keep Alive: 60
Clean Session: true
```

### **Subscriptions:**
```
Topic: sic/dibimbing/catalina/titanio-yudista/pub/dht
QoS: 0
Color: #4CAF50 (Green)
Alias: DHT11 Sensor Data
```

### **Publish Templates:**
```
LED ON:
  Topic: sic/dibimbing/catalina/titanio-yudista/sub/led
  Payload: ON
  
LED OFF:
  Topic: sic/dibimbing/catalina/titanio-yudista/sub/led
  Payload: OFF
```

## 📊 **MQTTX Features untuk DHT11 System**

### **1. Real-time Monitoring**
- ✅ Live data streaming dari ESP32
- ✅ JSON payload formatting
- ✅ Message timestamp
- ✅ Message count tracking

### **2. Visual Interface**
- ✅ Graph view untuk temperature/humidity trends
- ✅ Message history
- ✅ Connection status indicator
- ✅ Topic-based color coding

### **3. Testing & Debugging**
- ✅ Manual message publishing
- ✅ Payload validation
- ✅ Connection diagnostics
- ✅ Message export/import

## 🔧 **Advanced MQTTX Usage**

### **Custom Payloads untuk LED Control:**
```json
{
  "command": "ON",
  "duration": 5000,
  "mode": "blink"
}
```

### **Bulk Commands:**
```
ON
OFF
TOGGLE
BLINK:5
PULSE:10
STATUS
```

## 📈 **Monitoring Dashboard Setup**

Dengan MQTTX, Anda bisa create dashboard-like monitoring:

### **View 1: Sensor Data Tab**
- Subscribe: `sic/dibimbing/catalina/titanio-yudista/pub/dht`
- Display: Real-time temperature & humidity

### **View 2: LED Control Tab**
- Publish: `sic/dibimbing/catalina/titanio-yudista/sub/led`
- Quick buttons: ON, OFF, TOGGLE

### **View 3: System Logs Tab**
- Subscribe: `sic/dibimbing/catalina/titanio-yudista/+` (wildcard)
- Monitor: All system messages

## 🚀 **Quick Start dengan MQTTX**

1. **Open MQTTX Desktop App**
2. **Create New Connection** dengan setting yang disebutkan
3. **Connect** ke broker
4. **Add Subscription** untuk DHT11 topic
5. **Create Publish Templates** untuk LED control
6. **Start Monitoring!**

## 💡 **Best Practices**

### **Performance Tips:**
- Gunakan unique Client ID untuk setiap connection
- Set appropriate QoS level (0 untuk real-time, 1 untuk reliability)
- Enable auto-reconnect untuk connection stability

### **Development Workflow:**
1. Use MQTTX untuk visual monitoring dan debugging
2. Use Python scripts untuk automated tasks dan logging
3. Use ESP32 serial monitor untuk device debugging

## 🔍 **Troubleshooting dengan MQTTX**

### **Connection Issues:**
- Check broker URL dan port
- Verify network connectivity
- Try different client ID

### **Message Issues:**
- Validate JSON payload format
- Check topic spelling
- Verify QoS settings

### **Performance Issues:**
- Monitor message rate
- Check broker limits
- Optimize payload size

---

**🎉 MQTTX + DHT11 System = Perfect Combination!**

MQTTX memberikan visual interface yang excellent untuk monitoring dan testing, while Python scripts provide automation dan advanced logging capabilities.