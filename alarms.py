#!/usr/bin/env python3

ALARM_PWM = 85
ALARM_VBAT_PER_CELL = 3.5 # volts per cell
ALARM_TEMP = 55.0 # degrees


from board import buzzer
from wheeldata import g_wheeldata as wd
import asyncio

#wd = wheeldata.g_wheeldata

def get_alarm_vbat():
    return ALARM_VBAT_PER_CELL * wd.cells

async def alarms_loop():
    while True:
        if wd.check_alarms:
            alarms.check_alarms()
            wd.check_alarms = False
        await asyncio.sleep_ms(100)


class Alarm():
    def __init__(self):
        self.alarms = []
        self.alarms_display = []

    def check_alarms(self):
        if wd.output.value > ALARM_PWM:
            buzzer.do_beep(5)
            self.alarms.append(f'PWM: {str(wd.output)}')
        #vbat
        if wd.voltage.value < get_alarm_vbat():
            buzzer.do_beep(7)
            self.alarms.append(f'VBat: {str(wd.voltage)}')
        #temperature
        if wd.temperature.value > ALARM_TEMP:
            buzzer.do_beep(9)
            self.alarms.append(f'Temp: {str(wd.temperature)}')

    def push_alarm(self, text):
        self.alarms.append(text)


    def get_next_alarm(self):
        if len(self.alarms) > 0:
            alm = self.alarms.pop()
            self.alarms_display.append(alm)
            return alm
        return None

alarms = Alarm()
