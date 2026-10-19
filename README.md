# Smart Vehicle Cabin Monitoring and Automation System

## Overview

This project implements a sensor-driven vehicle cabin monitoring and automation system using Python, Arduino and Raspberry Pi. It integrates environmental sensors, automated vehicle functions and real-time telemetry to demonstrate how embedded systems can improve driver comfort, visibility and cabin safety.

The system monitors temperature, gas levels, ambient light and moisture, then uses programmed control logic to respond to changing environmental conditions. Sensor readings and system status are visualised through a live dashboard and transmitted to ThingsBoard for remote monitoring.

## Key Features

- **Cabin Temperature Monitoring:** Reads temperature data from a Raspberry Pi Sense HAT and applies a correction factor to compensate for temperature differences caused by the Raspberry Pi's CPU.
- **Gas Detection and Alarm:** Establishes an initial gas baseline during a warm-up period and activates an alarm response when readings exceed that baseline.
- **Automatic Climate Control Logic:** Calculates a fan output percentage based on cabin temperature and a configurable setpoint, with the gas alarm taking priority.
- **Automatic Headlight Control:** Adjusts headlight output and selects lighting modes based on ambient light levels, including day, automatic and tunnel conditions.
- **Rain-Sensing Wiper Control:** Maps moisture sensor readings to wiper speed modes and controls servo movement to simulate intermittent and continuous wiping.
- **Real-Time Data Visualisation:** Displays temperature, moisture and gas readings on a live Tkinter graph.
- **IoT Telemetry:** Sends sensor readings, control outputs and system status to ThingsBoard Cloud for remote monitoring.
- **Embedded Hardware Integration:** Connects Arduino-based analogue sensors and actuators with Raspberry Pi processing and Sense HAT status indication.

## Technologies Used

- **Programming:** Python
- **Embedded Systems:** Arduino, Raspberry Pi, Raspberry Pi Sense HAT
- **Hardware Interfaces:** PyFirmata, analogue sensors, servo control and PWM output
- **Visualisation:** Tkinter and Canvas
- **IoT and Cloud Monitoring:** ThingsBoard Cloud, HTTP REST API and JSON telemetry
- **Libraries:** Requests, PyFirmata, Sense HAT API

## System Operation

1. Environmental sensors continuously collect temperature, gas, ambient light and moisture readings.
2. Python processes and smooths sensor data, establishes a gas baseline and evaluates predefined control thresholds.
3. The control logic determines fan output, headlight settings and wiper behaviour.
4. The Sense HAT LED matrix provides a visual status indicator for system warm-up, normal operation and gas alarm conditions.
5. A graphical dashboard displays sensor trends, while ThingsBoard receives telemetry approximately every two seconds.

## Engineering Skills Demonstrated

- Embedded software development and hardware–software integration
- Sensor data acquisition and signal smoothing
- Threshold-based control logic and actuator management
- Real-time monitoring and graphical data visualisation
- IoT connectivity and cloud telemetry
- Debugging, system integration and modular Python programming

## Potential Applications

The project demonstrates concepts relevant to automotive electronics, intelligent vehicle systems, environmental sensing and connected-device development. Its sensor-driven architecture provides a foundation for exploring automated vehicle functions and real-time monitoring.

## Future Improvements

- Introduce sensor fault detection and more robust calibration.
- Improve gas alarm reliability using validated thresholds and sustained readings.
- Add fault handling for disconnected hardware and network failures.
- Implement a more comprehensive testing strategy and configurable control parameters.
- Evaluate the control logic using simulated driving and environmental conditions.

*This is an educational prototype. The control functions are demonstrations and are not validated for use in a real vehicle or as safety-critical automotive systems.*
