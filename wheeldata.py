#!/usr/bin/env python3

import time, math


class Value():
    def __init__(self, initvalue, age_func, formatstr):
        #the init value parameter
        #in fact sets the value type
        self.age_func = age_func
        self.formatstr = formatstr
        self.value = initvalue
    def __str__(self):
        return self.formatstr.format(self.value)
    def setValue(self, value):
        self.value = value
    def get_age_ms(self):
        return self.age_func()




class WDataPacket():
    def __init__(self, wheeldata):
        self.last_modified = time.ticks_ms()  # result of time.ticks_ms() when the values were provided last time
        self.name = 'BaseDataPacket'
        self.wheeldata = wheeldata

    def _update_age(self):
        self.last_modified = time.ticks_ms()

    def get_age_ms(self):
        return time.ticks_diff(time.ticks_ms(), self.last_modified)

def calc_batt_percentage(batt_volts, cells): # assumes 16cell liIon battery max voltage 67.2V, storage voltage 60V
    vcell = batt_volts/cells
    min_volts = 3.2
    max_volts = 4.2
    if vcell > 4.175:
        return 100
    if vcell > 3.2: # 54.4
        return int(math.floor((vcell - min_volts)/(max_volts - min_volts) * 100))
    #if vcell > 3.2:
    #    return int((vcell - 3.2) * 100)
    else:
        return 0

class WLivePacket(WDataPacket):
    def __init__(self, wd):
        super().__init__(wd)
        self.name = 'LivePacket'

        # Data from live packet
        self.wheeldata.voltage = Value(0.0, self.get_age_ms, '{:4.1f}')
        self.wheeldata.speed = Value(0.0, self.get_age_ms,'{:4.1f}')
        self.wheeldata.odo = Value(0, self.get_age_ms, '{:5d}')
        self.wheeldata.current = Value(0.0, self.get_age_ms, '{:4.1f}')
        self.wheeldata.temperature = Value(0.0, self.get_age_ms, '{:4.1f}')
        self.wheeldata.mode = Value(0, self.get_age_ms, ':3d')
        self.wheeldata.max_speed = Value(0.0, self.get_age_ms, '{:4.1f}')
        self.wheeldata.max_current = Value(0.0, self.get_age_ms, '{:4.1f}')
        self.wheeldata.max_temperature = Value(0.0, self.get_age_ms, '{:4.1f}')
        self.wheeldata.batt_percentage = Value(0, self.get_age_ms, '{:3d}%')
        self.wheeldata.power = Value(0.0, self.get_age_ms, '{:4.0f}')
        self.wheeldata.max_power = Value(0.0, self.get_age_ms, '{:4.0f}')
        self.wheeldata.max_voltage_drop = Value(0.0, self.get_age_ms, '{:4.1f}')
        self.wheeldata.max_wd_current = Value(0.0, self.get_age_ms, '{:4.1f}')
        self.wheeldata.rest_voltage = Value(0.0, self.get_age_ms, '{:4.1f}')
        self.wheeldata.voltage_drop = Value(0.0, self.get_age_ms, '{:4.1f}')
        self.wheeldata.batt_resistance = Value(0.0, self.get_age_ms, '{:6.3f}')



    def update(self, voltage, speed, odo, current, temperature, mode):
        self.wheeldata.voltage.setValue(voltage)
        self.wheeldata.speed.setValue(speed)
        self.wheeldata.odo.setValue(odo)
        self.wheeldata.current.setValue(current)
        self.wheeldata.temperature.setValue(temperature)
        self.wheeldata.mode.setValue(mode)
        self.wheeldata.max_speed.setValue(max(self.wheeldata.max_speed.value, speed))
        self.wheeldata.max_current.setValue(max(self.wheeldata.max_current.value, current))
        self.wheeldata.max_temperature.setValue(max(self.wheeldata.max_temperature.value, temperature))
        self.wheeldata.batt_percentage.setValue(calc_batt_percentage(self.wheeldata.voltage.value, self.wheeldata.cells))
        self.wheeldata.power.setValue(self.wheeldata.voltage.value * self.wheeldata.current.value)
        self.wheeldata.max_power.setValue(max(self.wheeldata.max_power.value, self.wheeldata.power.value))
        if abs(current) < 2: # the wheel is not loaded, the consumption is minimal (less than 2 amps)
            self.wheeldata.rest_voltage.setValue(voltage)
        self.wheeldata.voltage_drop.setValue(self.wheeldata.rest_voltage.value - voltage)
        # battery health calculations
        if self.wheeldata.max_voltage_drop.value < self.wheeldata.voltage_drop.value:
            self.wheeldata.max_voltage_drop.setValue(self.wheeldata.voltage_drop.value)
            self.wheeldata.max_wd_current.setValue(current)
            if abs(current) > 0.5: # not need to calculate anything for small currents
                self.wheeldata.batt_resistance.setValue(self.wheeldata.max_voltage_drop.value / abs(current))

        self._update_age()
        self.check_alarms = True


    def __str__(self):
        return self.name + \
            f', Voltage: {str(self.wheeldata.voltage)}' + \
            f', Speed: {str(self.wheeldata.speed)}' + \
            f', Odo: {str(self.wheeldata.odo)}' + \
            f', Current: {str(self.wheeldata.current)}' + \
            f', Temperature: {str(self.wheeldata.temperature)}' + \
            f', Mode: {str(self.wheeldata.mode)}' + \
            f', Age(ms): {self.get_age_ms():5d}'

class WSpeedLimitPacket(WDataPacket):
    def __init__(self, wd):
        super().__init__(wd)
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
    def __init__(self, wd):
        super().__init__(wd)
        self.name = 'TripDataPacket'

        self.wheeldata.trip = Value(0.0, self.get_age_ms, '{:5.1f}')
        self.wheeldata.uptime = Value(0.0, self.get_age_ms, '{:6.0f}')
        self.wheeldata.topspeed = Value(0.0, self.get_age_ms, '{:4.1f}')
        self.wheeldata.fanstate = Value(0, self.get_age_ms, '{:3d}')

    def update(self, trip, uptime, topspeed, fanstate):
        self.wheeldata.trip.setValue(trip)
        self.wheeldata.uptime.setValue(uptime)
        self.wheeldata.topspeed.setValue(topspeed)
        self.wheeldata.fanstate.setValue(fanstate)
        self._update_age()
    def __str__(self):
        return self.name + \
            f', Trip: {str(self.wheeldata.trip)}' + \
            f', uptime: {str(self.wheeldata.uptime)}' + \
            f', TopSpeed: {str(self.wheeldata.topspeed)}' + \
            f', FanState: {str(self.wheeldata.fanstate)}' + \
            f', Age(ms): {self.get_age_ms():5d}'

class WCPULoadPacket(WDataPacket):
    def __init__(self, wd):
        super().__init__(wd)
        self.name = 'CPULoadPacket'

        self.wheeldata.cpuload = Value(0, self.get_age_ms, '{:3d}')
        self.wheeldata.output = Value(0, self.get_age_ms, '{:3d}')
        #calculated
        self.wheeldata.max_cpuload = Value(0, self.get_age_ms, '{:3d}')
        self.wheeldata.max_output = Value(0, self.get_age_ms, '{:3d}')

    def update(self, cpuload, output):
        self.wheeldata.cpuload.setValue(cpuload)
        self.wheeldata.output.setValue(output)
        self.wheeldata.max_cpuload.setValue(max(self.wheeldata.max_cpuload.value, cpuload))
        self.wheeldata.max_output.setValue(max(self.wheeldata.max_output.value, output))
        self._update_age()
        self.check_alarms = True



    def __str__(self):
        return self.name + \
            f', CPU Load: {str(self.wheeldata.cpuload)}' + \
            f', Output(PWM): {str(self.wheeldata.output)}' + \
            f', Age(ms): {self.get_age_ms():5d}'

class WheelData():
    def __init__(self):
        self.live_pkt = WLivePacket(self)
        self.speedlimit_pkt = WSpeedLimitPacket(self)
        self.trip_pkt = WTripPacket(self)
        self.cpuload_pkt = WCPULoadPacket(self)
        self.name = ''
        self.model = ''
        self.version = ''
        self.cells = 20 # 84v battery 16x
        self.check_alarms = False
        self.got_name_and_model = False


    def __str__(self):
        return f'{self.live_pkt}\n{self.speedlimit_pkt}\n\
        {self.trip_pkt}\n{self.cpuload_pkt}\n'

# global singleton is stored here

g_wheeldata = WheelData()
