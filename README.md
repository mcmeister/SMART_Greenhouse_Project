# SMART Greenhouse Project

This project implements a smart greenhouse system using Python, DHT22 sensors, and Tkinter for the graphical user interface. The system retrieves sensor data, controls various devices, and posts data to Google Sheets for logging and monitoring.

## Features

- **Sensor Integration**: Reads temperature and humidity data from multiple DHT22 sensors.
- **Device Control**: Controls fans, pumps, misting systems, lights, and cooling systems based on sensor data.
- **Data Logging**: Posts sensor data and device statuses to Google Sheets.
- **Real-time Monitoring**: Displays real-time sensor readings and statuses on a Tkinter GUI.

## Prerequisites

- Python 3.x
- Tkinter
- Adafruit_DHT library
- Requests library

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/mcmeister/SMART_Greenhouse_Project.git
    cd SMART_Greenhouse_Project
    ```

2. **Install dependencies**:
    ```sh
    pip install adafruit-circuitpython-dht requests
    ```

3. **Connect hardware**:
    - Connect DHT22 sensors to the specified GPIO pins on your Raspberry Pi or compatible hardware.
    - Connect the digital devices (fans, pumps, etc.) to the specified GPIO pins.

## Usage

1. **Configure Google Scripts**:
    - Set up Google Scripts for reading and posting data.
    - Update the script IDs in the code with your own Google Script IDs.

2. **Run the script**:
    ```sh
    python SMART_Greenhouse_Project.py
    ```

## Code Overview

### Main Components

- **Sensor Reading**:
    - Reads temperature and humidity values from DHT22 sensors.
    - Handles retries and error handling for reliable readings.

- **Device Control**:
    - Controls various devices based on sensor data and predefined conditions.
    - Supports automatic and manual control modes.

- **Data Logging**:
    - Posts sensor data and device statuses to Google Sheets.
    - Retrieves control values from Google Sheets.

- **GUI**:
    - Displays real-time sensor readings and device statuses using Tkinter.
    - Updates every 2 seconds to reflect the latest data.

### Functions

- `safe_requests_get(url, retries, backoff_factor)`: Performs a GET request with retries and exponential backoff.
- `read_values()`: Reads control values from the Google Spreadsheet.
- `read_sensors(max_retries, backoff_factor)`: Reads temperature and humidity values from DHT sensors.
- `display_readings()`: Displays sensor readings and statuses on the Tkinter canvas.
- `control_temp_humidity()`: Controls the temperature and humidity by adjusting the devices.
- `get_data_from_spreadsheet()`: Retrieves control data from the Google Spreadsheet.
- `post_data_to_spreadsheet()`: Posts sensor data to the Google Spreadsheet.
- `check_device_statuses()`: Checks the statuses of digital IO devices and DHT sensors.
- `post_status_to_sheet(status_data)`: Posts device statuses to the Google Spreadsheet.
- `print_device_statuses(statuses)`: Prints the statuses of devices to the console.
- `update_device_status(initial)`: Updates and posts device statuses if there are changes.
- `periodic_task(interval, function, initial_interval, *args, **kwargs)`: Runs a function periodically in a separate thread.

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

Viacheslav Vorotilin


## Acknowledgements

- Adafruit for the DHT22 library.
- Google for providing Google Sheets and Google Scripts for data logging.

## Contact

If you have any questions or feedback, please feel free to reach out.

