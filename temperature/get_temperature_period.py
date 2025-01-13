from __future__ import print_function
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from ky_STS3X import *

# Determine I2C address according to the ADDR pin pull-up or pull-down
# ADDR pin pull-down: STS3X_I2C_ADDRESS_A   0x4A
# ADDR pin pull-up: STS3X_I2C_ADDRESS_B   0x4B
sensor = ky_STS3X(i2c_addr = STS3X_I2C_ADDRESS_B,bus = 1)


def setup():
  sensor.begin()
  print("sensor begin successfully!!!")

  '''
    # Set measurement frequency, you must call the api if you want to adopt period measurement mode.
    # Data measurement frequency, default to be 1Hz, freq: FREQ_2S, FREQ_1HZ, FREQ_2HZ, FREQ_4HZ, FREQ_10HZ
  '''
  sensor.set_freq(sensor.FREQ_1HZ)


def loop():
  ''' Read the temperature data periodically measured by the sensor, unit: °C '''
  temperature = sensor.get_temperature_period()
  print("period measurement celsius = %0.2f C\n" %temperature)

  time.sleep(1)


if __name__ == "__main__":
  setup()
  while True:
    loop()
