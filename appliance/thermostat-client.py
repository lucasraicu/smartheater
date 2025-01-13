#!/usr/bin/env python3

import socket
import sys
import time
import subprocess
import datetime

import argparse
import requests
from bs4 import BeautifulSoup
import json

DEBUG = False

def get_html(url):
    response = requests.get(url)
    return response.text

def get_price_kw():

	url = 'https://fred.stlouisfed.org/series/APUS23A72610'
	html = get_html(url)
	#print(html)


	# Your HTML string
	#html = "https://fred.stlouisfed.org/series/APUS23A72610"


	# Parse the HTML
	soup = BeautifulSoup(html, 'html.parser')

	# Find the element with class "series-obs value"
	element = soup.find('td', {'class': 'series-obs value'})

	# Print the value
	if element:
		#print(f"The series-obs value is: {element.text.strip()}")
		return float(element.text.strip())
	else:
		#print("Could not find the series-obs value in the HTML.")
		return 0.0
		


def get_difficulty_levels():
    url = "https://api.ergoplatform.com/api/v1/blocks"
    response = requests.get(url)
    data = json.loads(response.text)

    # Extract the 'items' list from the JSON document
    items = data.get('items', [])

    # Extract the 'difficulty' level from each item (block) in the list
    difficulty_levels = [item.get('difficulty', 'Key not found') for item in items]

    return difficulty_levels[-1]


def get_miner_reward():
    url = "https://api.ergoplatform.com/api/v1/blocks"
    response = requests.get(url)
    data = json.loads(response.text)

    # Extract the 'items' list from the JSON document
    items = data.get('items', [])

    # Extract the 'difficulty' level from each item (block) in the list
    miner_rewards = [item.get('minerReward', 'Key not found') for item in items]

    return miner_rewards[-1]/1000000000.0

def get_erg_to_usd_exchange_rate():
    # Fetch ERG to USD exchange rate from CoinGecko
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "ergo", "vs_currencies": "usd"}
    response = requests.get(url, params=params)
    data = response.json()
    
    # Extract the exchange rate
    return data["ergo"]["usd"]

def compute_profitability(hashrate_mh_per_s,electricity_watts,time_sec):
	global DEBUG
	current_difficulty = get_difficulty_levels()
	if DEBUG:
		print("current_difficulty=",current_difficulty)


	block_reward = get_miner_reward()
	if DEBUG:
		print("block_reward= ERG",block_reward)




	# Replace these values with the current information

	electricity_kwatts = electricity_watts/1000.0


	#hashrate_mh_per_s = hashrate_per_s/1000000.0  # Your hashrate in MH/s

	hashrate_per_s = hashrate_mh_per_s * 1000000
	if DEBUG:
		print("hashrate_mh_per_s",hashrate_mh_per_s)
	#current_difficulty = 123456789  # Current mining difficulty
	#block_reward = 10  # ERG block reward
	erg_to_usd_exchange_rate = get_erg_to_usd_exchange_rate()  # ERG to USD exchange rate
	if DEBUG:
		print("erg_to_usd_exchange_rate= $",erg_to_usd_exchange_rate)


	# Calculate estimated earnings per day
	blocks_per_day = 24 * 60 * 60 / 100
	if DEBUG:
		print("blocks_per_day=",blocks_per_day)
	ergs_per_day = blocks_per_day * block_reward
	if DEBUG:
		print("ergs_per_day= ERG",ergs_per_day)
	usd_per_day = ergs_per_day * erg_to_usd_exchange_rate
	if DEBUG:
		print("usd_per_day= $",usd_per_day)

	electricity_cost = get_price_kw()
	if DEBUG:
		print("electricity_cost= $",electricity_cost)

	num_sec = time_sec

	profitability = round((block_reward * hashrate_per_s / current_difficulty) * erg_to_usd_exchange_rate * num_sec , 6)



	# Print the result
	if DEBUG:
		print("profitability= $",round(profitability,2))

	costs = round(electricity_cost*electricity_kwatts*(num_sec/3600)*-1,6)
	if DEBUG:
		print("costs= $",round(costs,2))
	return profitability,costs

def pause_miner():

	# Execute the first curl command to get the session ID
	session_id_command = "curl -s 'http://127.0.0.1:4067/login?password=@Ionel400' | cut -f4 -d'\"'"
	session_id = subprocess.check_output(session_id_command, shell=True, text=True).strip()

	# Build the URL with the obtained session ID and send the pause request
	url = f"http://127.0.0.1:4067/control?sid={session_id}&pause=true"
	subprocess.run(['curl', '-s', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

	# Print a message indicating that t-rex is paused
	#print("t-rex paused")


def start_miner():

	# Execute the first curl command to get the session ID
	session_id_command = "curl -s 'http://127.0.0.1:4067/login?password=@Ionel400' | cut -f4 -d'\"'"
	session_id = subprocess.check_output(session_id_command, shell=True, text=True).strip()

	# Build the URL with the obtained session ID and send the resume request
	url = f"http://127.0.0.1:4067/control?sid={session_id}&pause=false"
	subprocess.run(['curl', '-s', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

	# Print a message indicating that t-rex is resumed
	#print("t-rex resumed")

def get_hashrate():
    try:
        # Execute the first curl command to get the session ID
        session_id_command = "curl -s 'http://127.0.0.1:4067/login?password=@Ionel400' | cut -f4 -d'\"'"
        session_id = subprocess.check_output(session_id_command, shell=True, text=True).strip()

        # Build the URL with the obtained session ID and send the summary request
        url = f"http://127.0.0.1:4067/summary?sid={session_id}"
        response = subprocess.check_output(['curl', '-s', url], text=True)

        # Parse the JSON response and extract hashrate_minute
        data = json.loads(response)
        hashrate_minute = data.get('hashrate_minute')
        #print(hashrate_minute)

        return hashrate_minute
    except Exception as e:
        print(f"Error: {e}")
        return None
        
def get_power():
    try:
        # Execute the first curl command to get the session ID
        session_id_command = "curl -s 'http://127.0.0.1:4067/login?password=@Ionel400' | cut -f4 -d'\"'"
        session_id = subprocess.check_output(session_id_command, shell=True, text=True).strip()

        # Build the URL with the obtained session ID and send the summary request
        url = f"http://127.0.0.1:4067/summary?sid={session_id}"
        response = subprocess.check_output(['curl', '-s', url], text=True)

        # Parse the JSON response and extract hashrate_minute
        data = json.loads(response)
        #print(data)
        power = 0
        for p in data["gpus"]:
        	#print(p["power_avr"])
        	power += int(p["power"])
        #gpu_power_avr1 = data["gpus"][0]["power_avr"]
        #gpu_power_avr2 = data["gpus"][1]["power_avr"]
        #gpu_power_avr3 = data["gpus"][2]["power_avr"]
        #gpu_power_avr4 = data["gpus"][3]["power_avr"]
        
        #print(gpu_power_avr1,gpu_power_avr2,gpu_power_avr2,gpu_power_avr3)

        return power
    except Exception as e:
        print(f"Error: {e}")
        return None
        


def get_weather_data(zip_code):
    # Create the URL based on the zip code
    url = f"https://www.google.com/search?q=weather+{zip_code}"
    
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract the temperature
        temperature_raw = soup.find('div', attrs={'class': 'BNeawe iBp4i AP7Wnd'}).text
        temperature = ''.join(filter(str.isdigit, temperature_raw))
        
        # Extract other weather information
        weather_info = soup.find('div', attrs={'class': 'BNeawe tAd8D AP7Wnd'}).text
        weather_data = weather_info.split('\n')
        time = weather_data[0]
        sky_description = weather_data[1]
        
        # Extract additional weather details
        other_weather_details = soup.find_all('div', attrs={'class': 'BNeawe s3v9rd AP7Wnd'})
        
        # Return the extracted weather data
        return temperature
    else:
        # If the request was unsuccessful, return None
        return -459.67

def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

def run_external_program(power_limit):
    # Run the 'nvidia-smi' command with the specified power limit and suppress output
    result = subprocess.run(['nvidia-smi', f'--power-limit={power_limit}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

#def pause_miner():
    # Run the 'nvidia-smi' command with the specified power limit and suppress output
#    result = subprocess.run(['./trex-pause.sh'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

#def start_miner():
    # Run the 'nvidia-smi' command with the specified power limit and suppress output
#    result = subprocess.run(['./trex-start.sh'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def client_program(host, port, polling_interval, min_temp, max_temp, zipcode):
    while True:
        try:
            file_log = open('data-thermostat.csv', 'a')
            client_socket = socket.socket()
            client_socket.connect((host, port))
    
            #run_external_program(min_power)
            pause_miner()
            high_state = False
            low_state = True
    
            if low_state:
                state = 'paused'
            if high_state:
                state = 'running'

            while True:
                client_socket.send("temp".encode())
                data = client_socket.recv(1024).decode()
                temp_fahrenheit = round(float(data), 2)
                f = str(temp_fahrenheit)
        
                ct = datetime.datetime.now()
                unix_time = int(ct.timestamp())
                outside_temperature = get_weather_data(zipcode)
                
                hash_rate = round(get_hashrate()/1000000.0,1)
                power_watts = get_power()
                
                profit,costs = compute_profitability(hash_rate,power_watts,polling_interval)

                if low_state:
                    state = 'paused'
                if high_state:
                    state = 'running'

                if min_temp <= temp_fahrenheit <= max_temp:
                	pass
                    #print(ct, state, min_temp, max_temp, f, outside_temperature)
                elif temp_fahrenheit < min_temp and low_state:
                    start_miner()
                    low_state = False
                    high_state = True
                    #print(ct, state, min_temp, max_temp, f, outside_temperature)
                elif temp_fahrenheit > max_temp and high_state:
                    pause_miner()
                    high_state = False
                    low_state = True
                    #print(ct, state, min_temp, max_temp, f, outside_temperature)
                else:
                	pass
                    #print(ct, state, min_temp, max_temp, f, outside_temperature)
                
                print(ct, state, min_temp, max_temp, f, outside_temperature, hash_rate, power_watts,profit,costs,round(profit*1440,2),round(costs*1440,2))
                file_log.write(str(unix_time)+","+ state+","+ str(min_temp)+","+ str(max_temp)+","+ str(f)+","+ str(outside_temperature)+","+ str(hash_rate)+","+ str(power_watts)+","+ str(profit)+","+ str(costs)+","+ str(round(profit*1440,2))+","+ str(round(costs*1440,2))+"\n")
                file_log.flush()
        
        
                time.sleep(polling_interval)

            client_socket.close()
            file_log.close()
        except Exception as e:
            print(e)
            print("error, will try again in", polling_interval, "seconds")
            time.sleep(polling_interval)


if __name__ == '__main__':
    if len(sys.argv) != 7:
        print("Usage: ./your_script.py <host> <port> <polling_interval> <min_temp> <max_temp> <zipcode>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    polling_interval = int(sys.argv[3])
    min_temp = float(sys.argv[4])
    max_temp = float(sys.argv[5])
    zipcode = int(sys.argv[6])

    client_program(host, port, polling_interval, min_temp, max_temp, zipcode)
