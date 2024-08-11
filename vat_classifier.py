import serial
import time

# Serial port configuration
SERIAL_PORT = 'COM11'
BAUD_RATE = 2000000
TIMEOUT = 0.1  # real-time reading but also remove redundancy connection

def get_classification_results(serial_connection):
    results = {}
    start_time = time.time()
    while True:
        # Read data from serial port
        line = serial_connection.readline().decode('utf-8').strip()

        if line:
            print(f"Read line: {line}")  # Print received result from Arduino microcontroller

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
            #print("Timeout waiting for data")
            break

    return results

def write_class_to_file(class_name, file_path='output.txt'):
    try:
        with open(file_path, 'a', encoding='utf-8') as file:
            file.write(f"{class_name}\n")
        print(f"Written '{class_name}' to {file_path}")
    except Exception as e:
        print(f"Error writing to file: {e}")


def main():
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT) as ser:
            ser.flushInput()
            print(f"Opened serial port {SERIAL_PORT} at {BAUD_RATE} baud")
            time.sleep(2)  # Wait for the serial connection to initialize

            classification_count = 0

            while True:
                #print("Starting classification cycle...")
                results = get_classification_results(ser)
                if results:
                    highest_class = max(results, key=results.get)
                    if highest_class != 'idle' and highest_class != 'anomaly':
                        write_class_to_file(highest_class)
                    classification_count += 1
                    print(f"Class with highest accuracy: {highest_class}")
                    print(f"Total classifications processed: {classification_count}")
                #else:
                    #print("No classification results received")  # Debugging print

    except serial.SerialException as e:
        print(f"Could not open serial port {SERIAL_PORT}: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
