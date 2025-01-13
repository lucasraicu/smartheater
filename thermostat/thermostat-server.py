from __future__ import print_function
import sys
import time
import os
import threading  # Import the threading module for threads
import concurrent.futures  # Import the concurrent.futures module for multiprocessing
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from ky_STS3X import *

import socket
import datetime

sensor = ky_STS3X(i2c_addr=STS3X_I2C_ADDRESS_B, bus=1)

# Global variable to store the current temperature
current_temperature = None
ct = None

def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

def read_temperature():
    global current_temperature
    global ct
    while True:
        # Read the temperature sensor every second and store the value in the global variable
        ct = datetime.datetime.now()
        current_temperature = sensor.get_temperature_period()
        temp_fahrenheit = celsius_to_fahrenheit(current_temperature)
        current_temperature = temp_fahrenheit
        time.sleep(60)

def handle_client(conn, address):
    while True:
        data = conn.recv(1024).decode()
        if not data:
            # If the client closed the connection, data will be empty
            print("Client", address, "closed the connection.")
            break

        if data == "temp":
            if current_temperature is not None:
                print(ct, current_temperature)
                str_temp = str(current_temperature)
            else:
                str_temp = "Temperature not available"
        else:
            str_temp = "unknown"

        try:
            conn.send(str_temp.encode())
        except BrokenPipeError:
            print("Client", address, "closed the connection.")
            break

    conn.close()

def server_program(port):
    sensor.begin()
    sensor.set_freq(sensor.FREQ_1HZ)

    host = socket.gethostname()

    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(5)  # Listen for up to 5 connections

    print("Server is listening on port", port)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        while True:
            conn, address = server_socket.accept()
            print("Connection from:", address)
            
            # Submit the client handling task to the ThreadPoolExecutor
            executor.submit(handle_client, conn, address)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    
    # Start the thread to read the temperature sensor
    temperature_thread = threading.Thread(target=read_temperature)
    temperature_thread.daemon = True  # Set the thread as daemon so it will exit when the main program exits
    temperature_thread.start()
    
    server_program(port)
