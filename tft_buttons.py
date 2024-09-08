# input pins for buttons: you will need to change these to match your wiring

from machine import Pin, deepsleep
#from machine import deepsleep
import esp32
from primitives import Pushbutton
#from app import deinit
from tft_display import gui
from board import backlight
from alarms import alarms
from time import sleep
import asyncio

async def deepsleep_job():
    await asyncio.sleep(2)
    wake = Pin(0, Pin.IN)
    esp32.wake_on_ext0(wake, level = esp32.WAKEUP_ANY_HIGH)
    deepsleep()

def right_longpress():
    print("Right putton long press... going deepsleep")
    alarms.push_alarm('Deepsleep')
    asyncio.create_task(deepsleep_job())

from ble import ble

class LedLightMode():
    # Light modes on kingsong: 0 - off, 1 - on, 2 - auto
    # led modes on kingsong 0 - off, 1 - on
    # here mode is: 0 - light off, led off
    # 1 - light auto, led off
    # 2 - light auto, led on
    def __init__(self):
        self.mode = 0
        self.lightmodes = [[0, 1], [2, 1], [2, 0]]
        self.lightmode_strings = ['Off', 'Li', 'Li+Le']

    def toggle(self):
        #print('Toggle lights')
        if ble.is_connected():
            self.mode = (self.mode + 1) % 3 # 0, 1, 2
            await ble.request(0x6c, self.lightmodes[self.mode][1] , 0x00) # set LED mode
            await ble.request(0x73, self.lightmodes[self.mode][0] + 0x12, 0x01) # set light mode
            alarms.push_alarm('Light:' + self.lightmode_strings[self.mode])
           # print('Lights request is done')

ledLightMode = LedLightMode()





class Buttons:
    def __init__(self):
        self.name = "t-display-s3"
        self.left = Pin(0, Pin.IN)
        self.right = Pin(14, Pin.IN)


        self.push_left = Pushbutton(self.left)
        self.push_right = Pushbutton(self.right)
        self.push_right.long_func(right_longpress)
        self.push_left.press_func(gui.prev_page)
        self.push_right.press_func(gui.next_page)
        self.push_right.double_func(backlight.next_duty)
        self.push_left.double_func(ledLightMode.toggle)



        # need more buttons for roids.py
#        self.fire = 0
#        self.thrust = 0
#        self.hyper = 0
