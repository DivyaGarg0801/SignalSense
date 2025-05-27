from ultralytics import YOLO
import cv2
import numpy as np
import tkinter as tk
import serial
import time

# Load YOLOv8 model
model = YOLO("yolov8n.pt")

# Vehicle classes to detect
vehicle_classes = ["car", "truck", "bus", "motorbike", "bicycle"]

# Image paths
image_paths = ["1.png.jpg", "2.png.jpg", "3.png.jpg", "4.png.jpg"]
annotated_images = []
frame_results = []

# Signal timing constants
time_per_vehicle = 1  # seconds
base_time = 5         # base green time
yellow_time = 3       # fixed yellow time

# Process each image
green_times = []
vehicle_counts = []

for idx, img_path in enumerate(image_paths):
    img = cv2.imread(img_path)
    if img is None:
        print(f"Image not found: {img_path}")
        continue

    results = model(img)[0]
    vehicle_count = 0

    # Detect vehicles
    for box in results.boxes:
        cls = int(box.cls.item())
        label = model.names[cls]
        if label in vehicle_classes:
            vehicle_count += 1
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, label, (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    green_time = base_time + vehicle_count * time_per_vehicle
    green_times.append(green_time)
    vehicle_counts.append(vehicle_count)
    annotated_images.append(img)

# After getting all green times, calculate yellow and red
for idx in range(4):
    green = green_times[idx]
    vehicles = vehicle_counts[idx]
    red = sum(green_times[i] + yellow_time for i in range(4) if i != idx)

    # Annotate times on image
    img = annotated_images[idx]
    cv2.putText(img, f"Total Vehicles: {vehicles}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
    cv2.putText(img, f"Green: {green}s", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(img, f"Yellow: {yellow_time}s", (10, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    cv2.putText(img, f"Red: {red}s", (10, 150),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    frame_results.append((idx + 1, vehicles, green, yellow_time, red))

# Resize images for grid
resized_images = [cv2.resize(img, (640, 480)) for img in annotated_images]
top_row = np.hstack((resized_images[0], resized_images[1]))
bottom_row = np.hstack((resized_images[2], resized_images[3]))
grid_image = np.vstack((top_row, bottom_row))

# Show final image in OpenCV window
cv2.imshow("Vehicle Detection Grid", grid_image)
cv2.imwrite("result_grid.png", grid_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Tkinter result window
def show_result_window():
    window = tk.Tk()
    window.title("Traffic Signal Timings")
    window.geometry("850x500")

    for i, (frame_no, vehicle_count, green, yellow, red) in enumerate(frame_results):
        row = i // 2
        col = i % 2

        heading = tk.Label(window, text=f"Frame {frame_no} Result",
                           font=("Arial", 14, "bold"), fg="red", padx=10, pady=5)
        heading.grid(row=row*3, column=col, sticky="w", padx=20)

        info = tk.Label(window,
                        text=f"Total Vehicles: {vehicle_count}\n"
                             f"🟩 Green: {green} s\n"
                             f"🟨 Yellow: {yellow} s\n"
                             f"🟥 Red: {red} s",
                        font=("Arial", 12), fg="black", justify="left", padx=10)
        info.grid(row=row*3 + 1, column=col, sticky="w", padx=20)

    tk.Button(window, text="Close", font=("Arial", 12),
              command=window.destroy).grid(row=6, columnspan=2, pady=20)

    window.mainloop()

# Show result window
show_result_window()

# Send Frame 1 Data to Arduino (unchanged)

# Construct a message for all 4 lanes
all_data = []
for frame in frame_results:
    v, g, y, r = frame[1], frame[2], frame[3], frame[4]
    all_data.append(f"{v},{g},{y},{r}")

# Join all 4 with ';' and end with newline
full_data = ";".join(all_data) + "\n"
print(f"Sending all lane data to Arduino: {full_data}")

# Send to Arduino
try:
    arduino = serial.Serial(port='COM5', baudrate=9600, timeout=2)
    time.sleep(2)
    arduino.write(full_data.encode())
    print("Data sent successfully.")
    arduino.close()
except Exception as e:
    print(f"Error communicating with Arduino: {e}")
