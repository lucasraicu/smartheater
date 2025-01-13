import socket
import sys
import time
import subprocess

# using datetime module
import datetime;
 


def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

def run_external_program(power_limit):
    # Run the 'nvidia-smi' command with the specified power limit and suppress output
    result = subprocess.run(['nvidia-smi', f'--power-limit={power_limit}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def pause_miner():
    # Run the 'nvidia-smi' command with the specified power limit and suppress output
    result = subprocess.run(['./trex-pause.sh'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def start_miner():
    # Run the 'nvidia-smi' command with the specified power limit and suppress output
    result = subprocess.run(['./trex-start.sh'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def client_program(host, port, polling_interval, min_temp, max_temp):
    client_socket = socket.socket()
    client_socket.connect((host, port))
    
    #run_external_program(min_power)
    pause_miner()
    high_state = False
    low_state = True
    
    if low_state:
    	state='paused'
    if high_state:
    	state='running'


    while True:
        client_socket.send("temp".encode())
        data = client_socket.recv(1024).decode()
        temp_fahrenheit = float(data)
        f = str(temp_fahrenheit)
        #print('Received from server: ' + f)
        # ct stores current time
        ct = datetime.datetime.now()
        #print("current time:-", ct)
        if low_state:
        	state='paused'
        if high_state:
        	state='running'

        if min_temp <= temp_fahrenheit <= max_temp:
            #print("Temperature is within the acceptable range. Everything is fine.")
            print(ct,state,min_temp,f,max_temp)
        elif temp_fahrenheit < min_temp and low_state:
            #print("Temperature is outside the acceptable range. Action is needed.")
            start_miner()
            #run_external_program(max_power)
            low_state = False
            high_state = True
            print(ct,state,f, min_temp,max_temp)
        elif temp_fahrenheit > max_temp and high_state:
            #print("Temperature is outside the acceptable range. Action is needed.")
            pause_miner()
            #run_external_program(min_power)
            high_state = False
            low_state = True
            print(ct,state,min_temp,max_temp,f)
        else: 
        	#print("Temperature is outside the acceptable range, but power setting has been changed.")
            print(ct,state,min_temp,f,max_temp)
        time.sleep(polling_interval)

    client_socket.close()

if __name__ == '__main__':
    if len(sys.argv) != 6:
        print("Usage: python client.py <host> <port> <polling_interval> <min_temp> <max_temp> ")
        print(len(sys.argv))
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    polling_interval = int(sys.argv[3])
    min_temp = float(sys.argv[4])
    max_temp = float(sys.argv[5])
    #max_power = int(sys.argv[6])
    #min_power = int(sys.argv[7])

    client_program(host, port, polling_interval, min_temp, max_temp)
