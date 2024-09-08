#!/usr/bin/env python3

ALARM_PWM = 85
ALARM_VBAT = 56.0
ALARM_TEMP = 55.0 # degrees


import wheeldata
from board import buzzer


class Alarm():
    def __init__(self):
        self.alarms = []
        self.alarms_display = []

    def check_alarms(self, wpkt):
        if isinstance(wpkt, wheeldata.WCPULoadPacket):
        #pwm
            if wpkt.output > ALARM_PWM:
                buzzer.do_beep(5)
                self.alarms.append(f'PWM: {wpkt.output:3d}')
            #vbat
        if isinstance(wpkt, wheeldata.WLivePacket):
            if wpkt.voltage < ALARM_VBAT:
                buzzer.do_beep(7)
                self.alarms.append(f'VBat: {wpkt.voltage:4.1f}')
            #temperature
            if wpkt.temperature > ALARM_TEMP:
                buzzer.do_beep(9)
                self.alarms.append(f'Temp: {wpkt.temperature:4.1f}')

    def push_alarm(self, text):
        self.alarms.append(text)


    def get_next_alarm(self):
        if len(self.alarms) > 0:
            alm = self.alarms.pop()
            self.alarms_display.append(alm)
            return alm
        return None

alarms = Alarm()
