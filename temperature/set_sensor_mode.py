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
    # Set repeat mode
    # The repeat setting will affect the measurement duration and thereby impact the overall energy consumption of the sensor
    # repeat, Repeat measurement config mode, there are three modes: REPEAT_HIGH, REPEAT_MEDIUM, REPEAT_LOW
  '''
  sensor.set_repeat(sensor.REPEAT_LOW)

  '''
    # Turn on or off the heater
  '''
  sensor.set_heater_on()
  sensor.set_heater_off()

  '''
    # Break off the ongoing work of the sensor to force it enter idle mode to wait the next command. Single measurement requires the sensor to be in idle status.
  '''
  sensor.sensor_break()

  '''
    # Reset the sensor
  '''
  # sensor.sensor_reset()

def loop():
  ''' Read the temperature data of a single sensor measurement, unit: °C '''
  temperature = sensor.get_temperature_single()
  print("single measurement celsius = %0.2f C\n" %temperature)

  time.sleep(1)

if __name__ == "__main__":
  setup()
  while True:
    loop()
