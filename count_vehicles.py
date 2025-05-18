from ultralytics import YOLO
import cv2
import numpy as np
import tkinter as tk

# Load YOLOv8 model
model = YOLO("yolov8n.pt")

# Vehicle classes to detect
vehicle_classes = ["car", "truck", "bus", "motorbike", "bicycle"]

# Image paths
image_paths = ["1.png.jpg", "2.png.jpg", "3.png.jpg", "4.png.jpg"]
annotated_images = []
frame_results = []

# Process each image
for idx, img_path in enumerate(image_paths):
    img = cv2.imread(img_path)
    if img is None:
        print(f"Image not found: {img_path}")
        continue

    results = model(img)[0]
    vehicle_count = 0

    # Detect and annotate vehicles
    for box in results.boxes:
        cls = int(box.cls.item())
        label = model.names[cls]
        if label in vehicle_classes:
            vehicle_count += 1
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, label, (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # Timer logic
    time_per_vehicle = 1  # seconds per vehicle
    base_time = 5  # minimum allocated time
    allocated_time = base_time + vehicle_count * time_per_vehicle

    # Display on image
    cv2.putText(img, f"Total Vehicles: {vehicle_count}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(img, f"Time Allocated: {allocated_time} sec", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

    # Store results
    annotated_images.append(img)
    frame_results.append((idx + 1, vehicle_count, allocated_time))

# Resize images to make grid
resized_images = [cv2.resize(img, (640, 480)) for img in annotated_images]
top_row = np.hstack((resized_images[0], resized_images[1]))
bottom_row = np.hstack((resized_images[2], resized_images[3]))
grid_image = np.vstack((top_row, bottom_row))

# Show final image in OpenCV window
cv2.imshow("Vehicle Detection Grid", grid_image)
cv2.imwrite("result_grid.png", grid_image)  # Optional: Save the grid image
cv2.waitKey(0)
cv2.destroyAllWindows()

# Function to show results window using tkinter
def show_result_window():
    window = tk.Tk()
    window.title("Result Window")
    window.geometry("700x400")  # Increased window size

    for i, (frame_no, vehicle_count, time_alloc) in enumerate(frame_results):
        row = i // 2
        col = i % 2

        # Heading (in red)
        heading = tk.Label(window, text=f"Result for Frame {frame_no}",
                           font=("Arial", 14, "bold"), fg="red", padx=10, pady=5)
        heading.grid(row=row*2, column=col, sticky="w", padx=20)

        # Vehicle and time info (in black)
        info = tk.Label(window,
                        text=f"Total Number of Vehicles : {vehicle_count}\nTime Allocated : {time_alloc} seconds",
                        font=("Arial", 12), fg="black", justify="left", padx=10)
        info.grid(row=row*2 + 1, column=col, sticky="w", padx=20)

    # Button to close the window
    tk.Button(window, text="Show Resultant Frame", font=("Arial", 12),
              command=window.destroy).grid(row=5, columnspan=2, pady=20)

    window.mainloop()


# Show the tkinter result window
show_result_window()
# Store results
annotated_images.append(img)
frame_results.append((idx + 1, vehicle_count, allocated_time))

import serial
import time

# Send only Frame 1 data
frame_1_data = frame_results[0]
vehicle_count = frame_1_data[1]
allocated_time = frame_1_data[2]

data_to_send = f"{vehicle_count},{allocated_time}\n"  # Sending in CSV format

try:
    arduino = serial.Serial(port='COM5', baudrate=9600, timeout=2)  # Change COM port as needed
    time.sleep(2)
    arduino.write(data_to_send.encode())
    print(f"Sent to Arduino: {data_to_send}")
    arduino.close()
except Exception as e:
    print(f"Error communicating with Arduino: {e}")