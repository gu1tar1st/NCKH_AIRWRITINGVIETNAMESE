import serial
import time
import tkinter as tk
import threading

#serial port configuration
SERIAL_PORT = 'COM11'
BAUD_RATE = 2000000
TIMEOUT = 0.1  #real-time reading but also remove redundancy connection

def get_classification_results(serial_connection):
    results = {}
    start_time = time.time()
    while True:
        #read data from serial port
        line = serial_connection.readline().decode('utf-8').strip()

        if line:
            print(f"Read line: {line}")  #print received result from Arduino microcontroller

            if ':' in line:
                label, value = line.split(':')
                try:
                    value = float(value)
                    results[label] = value
                except ValueError:
                    print(f"Value error with line: {line}")
                    continue

            if line.startswith('anomaly:'):
                print("Anomaly detected, stopping classification.")
                # break

        if time.time() - start_time > TIMEOUT:
            break

    return results

def write_class_to_file(class_name, file_path='output.txt'):
    try:
        with open(file_path, 'a', encoding='utf-8') as file:
            file.write(f"{class_name}\n")
        print(f"Written '{class_name}' to {file_path}")
    except Exception as e:
        print(f"Error writing to file: {e}")

def update_gui_message(message, color):
    #function to update the GUI with a new message
    label.config(text=message, fg=color, font=('Arial', 500))

def classify_and_update():
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT) as ser:
            ser.flushInput()
            print(f"Opened serial port {SERIAL_PORT} at {BAUD_RATE} baud")
            time.sleep(2)  #wait for the serial connection to initialize

            while True:
                results = get_classification_results(ser)
                if results:
                    highest_class = max(results, key=results.get)
                    if highest_class == 'anomaly':
                        update_gui_message("Ký tự lạ", 'red')
                    elif highest_class == 'idle':
                        update_gui_message("...", 'black')
                    else:
                        update_gui_message(f"{highest_class}", 'green')
                        write_class_to_file(highest_class)
                    print(f"Class with highest accuracy: {highest_class}")

                #schedule the function to be called again after a short delay
                root.after(100, classify_and_update)
                break  # prevent multiple invocations of the function

    except serial.SerialException as e:
        print(f"Could not open serial port {SERIAL_PORT}: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def start_classification():
    threading.Thread(target=classify_and_update, daemon=True).start()

#set up the tkinter GUI
root = tk.Tk()
root.title("Vietnamese AirwriTing - VAT - Giao diện hệ thống nhận dạng chữ viết Tiếng Việt")

#create a label to display messages with enlarged text
label = tk.Label(root, text="...", font=('Arial', 500), fg='black')
label.pack(padx=20, pady=20)

#start the classification process
start_classification()

#start the tkinter main loop
root.mainloop()
