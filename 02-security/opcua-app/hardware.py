import os
import random
import logging
import board
import adafruit_bme680
import RPi.GPIO as GPIO

class PiHardware:
    FAN_PIN = 27
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.FAN_PIN, GPIO.OUT)
        self.low_thr = 44.0
        self.high_thr = 48.0
        self.manual_ovr = False
        self.state_overheat = False
        self._fan_state = False

    def _set_fan_state(self, state: bool):
        self._fan_state = state
        GPIO.output(self.FAN_PIN, GPIO.HIGH if state else GPIO.LOW)

    def get_fan_state(self):
        return self._fan_state
    
    def get_overheat_state(self):
        return self.state_overheat

    def get_cpu_temp(self):
        res = os.popen('vcgencmd measure_temp').readline()
        return float(res.replace("temp=","").replace("'C\n",""))

    def set_low_threshold(self, val):
        self.low_thr = val

    def get_low_threshold(self):
        return self.low_thr

    def set_high_threshold(self, val):
        self.high_thr = val

    def get_high_threshold(self):
        return self.high_thr

    def set_manual_override(self, val):
        self.manual_ovr = val

    def get_manual_override(self):
        return self.manual_ovr

    def fan_control(self, cpu_temp=None):
        if cpu_temp is None:
            cpu_temp = self.get_cpu_temp()
        self.state_overheat = cpu_temp >= self.high_thr
        if cpu_temp >= self.high_thr or self.manual_ovr:
            self._set_fan_state(True)
        elif cpu_temp <= self.low_thr and not self.manual_ovr:
            self._set_fan_state(False)