import os
import time
import requests
import tkinter as tk
from pyfirmata import Arduino, util
from sense_hat import SenseHat

TB_TOKEN = os.getenv("TB_TOKEN", "3kIu7cVkrwRg3itD2yy4")
TELEMETRY_URL = f"https://eu.thingsboard.cloud/api/v1/{TB_TOKEN}/telemetry"

SETPOINT = 25.0
BAND = 15.0
WARMUP_S = 30
TEMP_FIX = 5.466
SAMPLE_EVERY = 10          # store every 10th reading

# Hardware
board = Arduino("/dev/ttyACM0")
util.Iterator(board).start()

gas_pin = board.analog[0]
moisture_pin = board.analog[1]
light_pin = board.analog[2]
gas_pin.enable_reporting()
moisture_pin.enable_reporting()
light_pin.enable_reporting()

wiper = board.get_pin("d:9:s")
headlight = board.get_pin("d:11:p")
time.sleep(2)
sense = SenseHat()

# Lookup tables: (minimum value, result)
LIGHTING = [(0.75, 10, "DAY"), (0.45, 50, "AUTO"), (0.25, 75, "AUTO"), (0, 100, "TUNNEL")]
WIPER = [(70, 100, "FAST"), (40, 55, "MEDIUM"), (20, 25, "SLOW"), (0, 0, "OFF")]

root = tk.Tk()
root.title("Real Time Readings")
root.geometry("1200x450")
root.configure(bg="black")

canvas = tk.Canvas(root, bg="black", highlightthickness=0)
canvas.pack(fill="both", expand=True, padx=5, pady=5)

times = []   # seconds since start for each stored reading

# colour, fixed (min, max) range or None to auto-scale, stored values
series = {
    "Temperature °C": {"colour": "lime", "range": None,   "values": []},
    "Steam Level":    {"colour": "cyan", "range": (0, 1), "values": []},
    "Gas Level":      {"colour": "red",  "range": (0, 1), "values": []},}


def draw_graph():
    root.after(1000, draw_graph)      # schedule the next redraw FIRST

    canvas.delete("all")

    if len(times) < 2:
        return

    width = canvas.winfo_width()
    height = canvas.winfo_height()
    left, right, top, bottom = 55, 15, 45, 45

    def get_x(t):
        return left + t / times[-1] * (width - left - right)

    def get_y(percent):
        return height - bottom - percent / 100 * (height - top - bottom)

    # Gridlines and Y numbers
    for percent in (0, 25, 50, 75, 100):
        y = get_y(percent)
        canvas.create_line(left, y, width - right, y, fill="#444444", dash=(2, 4))
        canvas.create_text(left - 10, y, text=f"{percent}%", fill="#bbbbbb", anchor="e")

    # Axes and labels
    canvas.create_line(left, top, left, height - bottom, fill="white")
    canvas.create_line(left, height - bottom, width - right, height - bottom, fill="white")
    canvas.create_text(15, height / 2, text="Share of each line's range", fill="white", angle=90)
    canvas.create_text(width / 2, height - 12, text="Time (seconds)", fill="white")

    # X numbers
    for k in range(7):
        t = times[-1] * k / 6
        canvas.create_text(get_x(t), height - bottom + 15, text=f"{t:.0f}", fill="#bbbbbb")

    # One line per sensor, with a legend showing the latest real value
    for n, (title, s) in enumerate(series.items()):
        values = s["values"]
        low, high = s["range"] or (min(values), max(values))
        if high == low:
            high += 1

        points = []
        for t, v in zip(times, values):
            percent = min(max((v - low) / (high - low) * 100, 0), 100)
            points += [get_x(t), get_y(percent)]

        canvas.create_line(points, fill=s["colour"], width=2)
        canvas.create_text(left + n * 250, 20, text=f"● {title}: {values[-1]:.2f}",
                           fill=s["colour"], anchor="w", font=("Arial", 12, "bold"))


def send_telemetry(data):
    try:
        requests.post(TELEMETRY_URL, json=data, timeout=5).raise_for_status()
    except requests.RequestException as e:
        print(f"ThingsBoard error: {e}")


def cabin_temp():
    raw = sense.get_temperature()
    with open("/sys/class/thermal/thermal_zone0/temp") as f:
        cpu = int(f.read()) / 1000
    return raw - (cpu - raw) / TEMP_FIX


start = time.time()
gas = gas_pin.read() or 0.0
gas_readings = []
baseline = None
loop_count = 0
wiper_position = 20
wiper_direction = 1
last_wiper_move = time.time()
last_telemetry = time.time()


def main_loop():
    global gas, baseline, loop_count
    global wiper_position, wiper_direction, last_wiper_move, last_telemetry

    reading = gas_pin.read()
    if reading is not None:
        gas = 0.8 * gas + 0.2 * reading

    temp = cabin_temp()
    light = light_pin.read() or 0.0
    moisture = moisture_pin.read() or 0.0

    elapsed = time.time() - start
    warming = elapsed < WARMUP_S

    # Gas baseline
    if warming:
        gas_readings.append(gas)
    elif baseline is None:
        baseline = sum(gas_readings) / len(gas_readings)
        print("Gas baseline established: %.3f" % baseline)

    alarm = baseline is not None and gas > baseline

    # Fan
    duty = 1.0 if alarm else min(max((temp - SETPOINT) / BAND, 0), 1)
    fan_percent = round(duty * 100)

    # Headlights
    headlight_percent, lighting_mode = next((h, m) for limit, h, m in LIGHTING if light >= limit)
    headlight.write(headlight_percent / 100)

    # Wipers
    moisture_percent = round(moisture * 100)
    wiper_speed, wiper_mode = next((s, m) for limit, s, m in WIPER if moisture_percent >= limit)

    if wiper_speed == 0:
        wiper.write(20)
    elif time.time() - last_wiper_move >= 0.12 - wiper_speed / 100 * 0.09:
        wiper_position += wiper_direction * 5

        if wiper_position >= 160:
            wiper_position, wiper_direction = 160, -1
        elif wiper_position <= 20:
            wiper_position, wiper_direction = 20, 1

        wiper.write(wiper_position)
        last_wiper_move = time.time()

    # Sense HAT colour
    sense.set_pixels([(255, 0, 0) if alarm else (0, 60, 255) if warming else (0, 255, 0)] * 64)

    # Store every tenth reading for the graph
    loop_count += 1
    if loop_count % SAMPLE_EVERY == 0:
        times.append(elapsed)
        series["Temperature °C"]["values"].append(temp)
        series["Steam Level"]["values"].append(moisture)
        series["Gas Level"]["values"].append(gas)

    # ThingsBoard every 2 seconds
    if time.time() - last_telemetry >= 2:
        send_telemetry({
            "temperature": round(temp, 2),
            "gas_level": round(gas, 3),
            "gas_alarm": alarm,
            "fan_percent": fan_percent,
            "light_level": round(light, 3),
            "headlight_percent": headlight_percent,
            "lighting_mode": lighting_mode,
            "moisture_level": round(moisture, 3),
            "wiper_speed": wiper_speed,
            "wiper_mode": wiper_mode,
        })
        last_telemetry = time.time()

    base_text = "%.3f" % baseline if baseline is not None else "calculating"
    print("temp %.1f  gas %.3f  baseline %s  light %.3f  moisture %.3f  "
          "fan %d%%  headlights %d%%  wiper %d%%  %s"
          % (temp, gas, base_text, light, moisture,
             fan_percent, headlight_percent, wiper_speed, wiper_mode))

    root.after(50, main_loop)


main_loop()
draw_graph()

try:
    root.mainloop()
except KeyboardInterrupt:
    print("\nStopping system...")
finally:
    wiper.write(20)
    headlight.write(0)
    sense.clear()
    board.exit()
    root.destroy()
    print("System stopped.")