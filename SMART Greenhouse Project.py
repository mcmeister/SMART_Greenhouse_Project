import tkinter as tk
import urllib
import adafruit_dht
import board
import time
import threading
from datetime import datetime, timedelta
import digitalio
import requests
from urllib.parse import urlencode

# Constants and Configuration
DHT_PINS = [board.D4, board.D2, board.D3, board.D12]
GOOGLE_SCRIPT_ID_POST_DATA = "YOUR_POST_DATA_SCRIPT_ID"
GOOGLE_SCRIPT_ID_POST_STATUS = "YOUR_POST_STATUS_SCRIPT_ID"
GOOGLE_SCRIPT_ID_READ = "YOUR_READ_SCRIPT_ID"
BASE_URL = f"https://script.google.com/macros/s/{GOOGLE_SCRIPT_ID_READ}/exec?read="
URLS = {
    'min_t': BASE_URL + "P2",
    'max_t': BASE_URL + "Q2",
    'min_h': BASE_URL + "R2",
    'max_h': BASE_URL + "S2",
    'mist_on': BASE_URL + "T2",
    'mist_off': BASE_URL + "U2",
    'fan1Control': BASE_URL + "B2",
    'fan2Control': BASE_URL + "C2",
    'fan3Control': BASE_URL + "D2",
    'pumpControl': BASE_URL + "E2",
    'mistControl': BASE_URL + "F2",
    'lightControl': BASE_URL + "G2",
    'coolerControl': BASE_URL + "H2",
    'table1Control': BASE_URL + "I2",
    'table2Control': BASE_URL + "J2",
    'table3Control': BASE_URL + "K2",
    'table4Control': BASE_URL + "L2",
    'table5Control': BASE_URL + "M2",
    'sunrise': BASE_URL + "V2",
    'sunset': BASE_URL + "W2"
}
INTERVALS = {
    'read_values': 1,
    'get_data': 1,
    'control_temp_humidity': 1,
    'post_data': 600,
    'update_device_status': 5,
    'display_readings': 2
}

# Initialize sensors
dht_sensors = [adafruit_dht.DHT22(pin) for pin in DHT_PINS]
digital_devices = {
    'fan1': board.D14,
    'fan2': board.D15,
    'fan3': board.D18,
    'pump': board.D23,
    'mist': board.D21,
    'light': board.D25,
    'cooler': board.D17,
    'table1': board.D5,
    'table2': board.D6,
    'table3': board.D13,
    'table4': board.D16,
    'table5': board.D20
}
devices = {name: digitalio.DigitalInOut(pin) for name, pin in digital_devices.items()}
for device in devices.values():
    device.direction = digitalio.Direction.OUTPUT
    device.value = True

# Global variables
values = {}
last_valid_temps = [None] * 4
last_valid_hums = [None] * 4
previous_statuses = {device: 'up' for device in devices}
previous_statuses.update({f'dht{i + 1}': 'up' for i in range(len(dht_sensors))})

# Tkinter setup
root = tk.Tk()
root.title("DHT-22 Readings")
root.geometry(f"600x60+{root.winfo_screenwidth()//2 - 300}+7")
root.overrideredirect(True)
root.configure(bg='white')
root.attributes("-topmost", True)
canvas = tk.Canvas(root, bg='white', highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=1)

def safe_requests_get(url, retries=3, backoff_factor=0.3):
    """
    Perform a GET request with retries and exponential backoff.
    
    Args:
        url (str): URL to request.
        retries (int): Number of retry attempts.
        backoff_factor (float): Backoff factor for retries.
    
    Returns:
        response: The response object if successful, None otherwise.
    """
    for retry in range(retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response
            print(f"Error: Received status code {response.status_code} from URL {url}")
        except requests.exceptions.RequestException as e:
            print(f"Error while fetching from URL {url}: {e}")
        time.sleep(backoff_factor * (2 ** retry))
    return None

def read_values():
    """
    Read control values from the spreadsheet and update the global values dictionary.
    """
    global values
    for key, url in URLS.items():
        response = safe_requests_get(url)
        if response:
            new_value = response.text.strip()
            if values.get(key) != new_value:
                print(f"Value of {key} has changed to {new_value}")
                values[key] = new_value

def read_sensors(max_retries=3, backoff_factor=1):
    """
    Read temperature and humidity values from DHT sensors.
    
    Args:
        max_retries (int): Maximum number of retry attempts.
        backoff_factor (float): Backoff factor for retries.
    
    Returns:
        tuple: Average temperature, average humidity, and error messages.
    """
    global last_valid_temps, last_valid_hums
    error_messages = [None] * len(dht_sensors)
    for idx, dht in enumerate(dht_sensors):
        for retry in range(max_retries):
            try:
                temp = dht.temperature
                hum = dht.humidity
                if temp is not None and hum is not None:
                    last_valid_temps[idx] = temp
                    last_valid_hums[idx] = hum
                    break
            except RuntimeError as e:
                if retry < max_retries - 1:
                    time.sleep(backoff_factor * (2 ** retry))
                else:
                    last_valid_temps[idx] = None
                    last_valid_hums[idx] = None
                    error_messages[idx] = f"Sensor {idx + 1} failed"
    avg_temp = sum([t for t in last_valid_temps if t is not None]) / len([t for t in last_valid_temps if t is not None]) if last_valid_temps else None
    avg_hum = sum([h for h in last_valid_hums if h is not None]) / len([h for h in last_valid_hums if h is not None]) if last_valid_hums else None
    return avg_temp, avg_hum, error_messages

def display_readings():
    """
    Display sensor readings and statuses on the Tkinter canvas.
    """
    print("Running display_readings...")
    canvas.delete('all')
    avg_temperature, avg_humidity, error_messages = read_sensors()
    sensor_data = [(temp, hum, error) for temp, hum, error in zip(last_valid_temps, last_valid_hums, error_messages)]
    base_x = 300
    base_y = 30
    current_time = datetime.now().strftime('%H:%M')
    avg_text = f"Avg H = {avg_humidity:.1f}, Avg T = {avg_temperature:.1f} [{current_time}]" if avg_humidity and avg_temperature else "Avg H = N/A, Avg T = N/A"
    canvas.create_text(base_x, base_y - 20, anchor='center', text=avg_text)
    sensors_text = "Sensors: "
    canvas.create_text(base_x - 100, base_y, anchor='center', text=sensors_text)
    for i, (temperature, humidity, error_message) in enumerate(sensor_data):
        status_text = f"{i + 1} - {'ON' if temperature and humidity else 'OFF'}"
        color = 'green' if temperature and humidity else 'red'
        canvas.create_text(base_x - 40 + (i * 50), base_y, anchor='center', text=status_text, fill=color)
        if error_message:
            canvas.create_text(base_x - 40 + (i * 50), base_y + 20, anchor='center', text=error_message, fill='red', font=("Helvetica", 7))
    root.after(INTERVALS['display_readings'] * 1000, display_readings)

def control_temp_humidity():
    """
    Control the temperature and humidity by adjusting the devices.
    """
    global values
    avg_temp, avg_hum, _ = read_sensors()
    if avg_temp is None or avg_hum is None:
        print("No valid sensor readings!")
        return
    min_t, max_t, min_h, max_h = (float(values.get(key, 0)) for key in ['min_t', 'max_t', 'min_h', 'max_h'])
    conditions = [
        (avg_temp < min_t and avg_hum < min_h, ["Condition 1 was met", False, False, False, False]),
        (min_t <= avg_temp <= max_t and avg_hum < min_h, ["Condition 2 was met", False, False, False, False]),
        (avg_temp > max_t and avg_hum < min_h, ["Condition 3 was met", False, False, False, True]),
        (avg_temp > 28 and avg_hum < min_h, ["Condition 4 was met", False]),
        (avg_hum > 95 and avg_temp < max_t, ["Condition 5 was met", True, False, False, True])
    ]
    for condition, actions in conditions:
        if condition:
            print(actions[0])
            devices['pump'].value, devices['fan2'].value, devices['fan3'].value, devices['mist'].value = actions[1:]

    mist_on, mist_off = (datetime.strptime(values.get(key, "00:00:00"), "%H:%M:%S").time() for key in ['mist_on', 'mist_off'])
    sunrise, sunset = (datetime.strptime(values.get(key, "06:00:00"), "%H:%M:%S").time() for key in ['sunrise', 'sunset'])
    current_time = datetime.now().time()
    devices['mist'].value = mist_on <= current_time < mist_off if mist_on != mist_off else sunrise <= current_time < sunset
    devices['mist'].value = True if avg_temp < min_t or avg_hum > 95 else devices['mist'].value
    devices['mist'].value = False if avg_hum < min_h else devices['mist'].value
    devices['light'].value = sunrise <= current_time < sunset if values.get('lightControl') == 'AUTO' else devices['light'].value

def get_data_from_spreadsheet():
    """
    Retrieve control data from the Google Spreadsheet.
    """
    for var, url in URLS.items():
        response = safe_requests_get(url)
        if response:
            new_value = response.text.strip()
            if var not in values or values[var] != new_value:
                print(f"Value of {var} has changed to {new_value}")
                values[var] = new_value

def post_data_to_spreadsheet():
    """
    Post sensor data to the Google Spreadsheet.
    """
    temps = {f't{i + 1}': temp for i, temp in enumerate(last_valid_temps)}
    hums = {f'h{i + 1}': hum for i, hum in enumerate(last_valid_hums)}
    avg_temp = round(sum([t for t in last_valid_temps if t is not None]) / len([t for t in last_valid_temps if t is not None]), 1) if last_valid_temps else None
    avg_hum = round(sum([h for h in last_valid_hums if h is not None]) / len([h for h in last_valid_hums if h is not None]), 1) if last_valid_hums else None
    url_final = f"https://script.google.com/macros/s/{GOOGLE_SCRIPT_ID_POST_DATA}/exec?{urlencode(temps)}&{urlencode(hums)}&ah={avg_hum}&at={avg_temp}"
    response = safe_requests_get(url_final)
    if response:
        print(f"Payload: {response.text}")

def check_device_statuses():
    """
    Check the statuses of digital IO devices and DHT sensors.
    
    Returns:
        dict: A dictionary of device statuses.
    """
    digital_io_statuses = {name: device.value for name, device in devices.items()}
    dht_statuses = {f'dht{i + 1}': 'up' if last_valid_temps[i] is not None and last_valid_hums[i] is not None else 'down' for i in range(len(dht_sensors))}
    return {**digital_io_statuses, **dht_statuses}

def post_status_to_sheet(status_data):
    """
    Post device statuses to the Google Spreadsheet.
    
    Args:
        status_data (dict): Dictionary containing device statuses.
    """
    data_to_send = {**status_data, 'status': 'update'}
    query_string = urlencode(data_to_send, safe='/', quote_via=urllib.parse.quote)
    url_final = f"https://script.google.com/macros/s/{GOOGLE_SCRIPT_ID_POST_STATUS}/exec?{query_string}"
    try:
        response = requests.get(url_final)
        print(f"URL: {url_final}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error posting to sheet: {e}")

def print_device_statuses(statuses):
    """
    Print the statuses of devices to the console.
    
    Args:
        statuses (dict): Dictionary containing device statuses.
    """
    status_line = ", ".join([f"{device}: {status}" for device, status in statuses.items()])
    print(f"Device Statuses: {status_line}")

def update_device_status(initial=False):
    """
    Update and post device statuses if there are changes.
    
    Args:
        initial (bool): Whether this is the initial run.
    """
    global previous_statuses
    device_statuses = check_device_statuses()
    if initial:
        previous_statuses = device_statuses.copy()
        print_device_statuses(previous_statuses)
        post_status_to_sheet(device_statuses)
    else:
        status_changed = any(previous_statuses[device] != status for device, status in device_statuses.items())
        if status_changed:
            previous_statuses.update(device_statuses)
            print_device_statuses(device_statuses)
            post_status_to_sheet(device_statuses)

def periodic_task(interval, function, initial_interval=None, *args, **kwargs):
    """
    Run a function periodically in a separate thread.
    
    Args:
        interval (int): Interval in seconds between function calls.
        function (callable): Function to run periodically.
        initial_interval (int, optional): Initial delay before the first function call.
    """
    def loop():
        first_run = True
        while True:
            time.sleep(initial_interval if first_run and initial_interval else interval)
            try:
                function(*args, **kwargs)
            except Exception as e:
                print(f"Error in {function.__name__}: {e}")
            first_run = False
    thread = threading.Thread(target=loop)
    thread.start()
    return thread

# Start periodic tasks
periodic_task(INTERVALS['read_values'], read_values)
periodic_task(INTERVALS['get_data'], get_data_from_spreadsheet)
periodic_task(INTERVALS['control_temp_humidity'], control_temp_humidity)
periodic_task(INTERVALS['post_data'], post_data_to_spreadsheet, initial_interval=60)
periodic_task(INTERVALS['update_device_status'], update_device_status)
root.after(INTERVALS['display_readings'] * 1000, display_readings)
root.mainloop()
