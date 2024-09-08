#!/usr/bin/env python3

import time, math

from alarms import alarms


class WDataPacket():
    def __init__(self):
        self.last_modified = time.ticks_ms()  # result of time.ticks_ms() when the values were provided last time
        self.name = 'BaseDataPacket'

    def _update_age(self):
        self.last_modified = time.ticks_ms()

    def get_age_ms(self):
        return time.ticks_diff(time.ticks_ms(), self.last_modified)

def calc_batt_percentage(batt_volts): # assumes 16cell liIon battery max voltage 67.2V, storage voltage 60V
    if batt_volts > 66.8:
        return 100
    if batt_volts > 54.4:
        return int(math.floor((batt_volts - 53.2) / 0.136))
    if batt_volts > 51.2:
        return int((batt_volts - 51.2) / 0.36)
    else:
        return 0

class WLivePacket(WDataPacket):
    def __init__(self):
        super().__init__()
        self.name = 'LivePacket'
        self.voltage = 0.0
        self.speed = 0.0
        self.odo = 0.0
        self.current = 0.0
        self.temperature = 0.0
        self.mode = 0
        #caluclated
        self.max_speed = 0.0
        self.max_current = 0.0
        self.max_temperature = 0.0
        self.batt_percentage = 0
        self.power = 0.0
        self.max_power = 0.0

    def update(self, voltage, speed, odo, current, temperature, mode):
        self.voltage = voltage
        self.speed = speed
        self.odo = odo
        self.current = current
        self.temperature = temperature
        self.mode = mode
        self.max_speed = max(self.max_speed, speed)
        self.max_current = max(self.max_current, current)
        self.max_temperature = max(self.max_temperature, temperature)
        self.batt_percentage = calc_batt_percentage(self.voltage)
        self.power = self.voltage * self.current
        self.max_power = max(self.max_power, self.power)
        self._update_age()
        alarms.check_alarms(self)
    def __str__(self):
        return self.name + \
            f', Voltage: {self.voltage:4.1f}' + \
            f', Speed: {self.speed:4.1f}' + \
            f', Odo: {self.odo:7.1f}' + \
            f', Current: {self.current:5.1f}' + \
            f', Temperature: {self.temperature:5.1f}' + \
            f', Mode: {self.mode:2d}' + \
            f', Age(ms): {self.get_age_ms():5d}'

class WSpeedLimitPacket(WDataPacket):
    def __init__(self):
        super().__init__()
        self.name = 'SpeedLimitPacket'
        self.speed_limit  = 0
    def update(self, speed_limit):
        self.speed_limit = speed_limit
        self._update_age()
    def __str__(self):
        return self.name + \
            f', SpeedLimit: {self.speed_limit:4.0f}' + \
            f', Age(ms): {self.get_age_ms():5d}'


class WTripPacket(WDataPacket):
    def __init__(self):
        super().__init__()
        self.name = 'TripDataPacket'
        self.trip = 0
        self.uptime = 0
        self.topspeed = 0
        self.fanstate = 0
    def update(self, trip, uptime, topspeed, fanstate):
        self.trip = trip
        self.uptime = uptime
        self.topspeed = topspeed
        self.fanstate = fanstate
        self._update_age()
    def __str__(self):
        return self.name + \
            f', Trip: {self.trip:5.1f}' + \
            f', uptime: {self.uptime:6.0f}' + \
            f', TopSpeed: {self.topspeed:4.1f}' + \
            f', FanState: {self.fanstate:1d}' + \
            f', Age(ms): {self.get_age_ms():5d}'

class WCPULoadPacket(WDataPacket):
    def __init__(self):
        super().__init__()
        self.name = 'CPULoadPacket'
        self.cpuload = 0
        self.output = 0
        #calculated
        self.max_cpuload = 0
        self.max_output = 0
    def update(self, cpuload, output):
        self.cpuload = cpuload
        self.output = output
        self.max_cpuload = max(self.max_cpuload, cpuload)
        self.max_output = max(self.max_output, output)
        self._update_age()
        alarms.check_alarms(self)

    def __str__(self):
        return self.name + \
            f', CPU Load: {self.cpuload:3d}' + \
            f', Output(PWM): {self.output:3d}' + \
            f', Age(ms): {self.get_age_ms():5d}'

class WheelData():
    def __init__(self):
        self.live_pkt = WLivePacket()
        self.speedlimit_pkt = WSpeedLimitPacket()
        self.trip_pkt = WTripPacket()
        self.cpuload_pkt = WCPULoadPacket()
    def __str__(self):
        return f'{self.live_pkt}\n{self.speedlimit_pkt}\n\
        {self.trip_pkt}\n{self.cpuload_pkt}\n'

# global singleton is stored here

g_wheeldata = WheelData()
