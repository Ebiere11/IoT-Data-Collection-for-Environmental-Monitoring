import time
import json
import requests
import Adafruit_DHT
import smbus

# Define sensor types and GPIO pins
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4  # GPIO pin for DHT sensor

# I2C bus for air quality sensor (example for CCS811 sensor)
I2C_BUS = smbus.SMBus(1)
CCS811_ADDR = 0x5A  # Default I2C address for CCS811

def read_dht_sensor():
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        return {'temperature': temperature, 'humidity': humidity}
    else:
        return {'error': 'DHT sensor read failed'}

def read_air_quality_sensor():
    try:
        I2C_BUS.write_byte(CCS811_ADDR, 0x02)  # Example command to read CO2
        time.sleep(1)
        data = I2C_BUS.read_i2c_block_data(CCS811_ADDR, 0x02, 2)
        co2 = (data[0] << 8) | data[1]
        return {'co2': co2}
    except Exception as e:
        return {'error': str(e)}

def send_data_to_cloud(data):
    url = "https://example-cloud-server.com/api/environment"
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, data=json.dumps(data), headers=headers)
        return response.status_code, response.text
    except requests.exceptions.RequestException as e:
        return None, str(e)

def main():
    while True:
        dht_data = read_dht_sensor()
        air_quality_data = read_air_quality_sensor()
        
        sensor_data = {
            'temperature': dht_data.get('temperature'),
            'humidity': dht_data.get('humidity'),
            'co2': air_quality_data.get('co2'),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print("Collected Data:", sensor_data)
        status, response = send_data_to_cloud(sensor_data)
        print("Cloud Response:", status, response)
        
        time.sleep(60)  # Collect data every 60 seconds

if __name__ == "__main__":
    main()
