from machine import Pin, ADC, PWM

#setup battery power check

vbatt = ADC(Pin(4))
vbatt.atten(ADC.ATTN_11DB) #Full range: 3.3v
#

vbatt_value = 0.0

# Buzzer pin



import asyncio

async def read_vbatt_loop():
    global vbatt_value
    while True:
        vbatt_value =  vbatt.read() * 3.6 / 4095 * 2
        #print(f'vbat: {vbatt_value}')
        await asyncio.sleep_ms(1000)

def p_batt_powered():
    if vbatt_value > 4.2:
        return False
    return True

def batt_percentage():
    if vbatt_value > 4.2:
        return 100 # usb powered
    if vbatt_value > 3.2: # normal range
        return int(100 - (4.2 - vbatt_value) * 100)
    return 0 #battery is overdischarged or damaged


class BackLight():
    def __init__(self, pin: Pin):
        self.pin = pin
        self.pwm = PWM(self.pin, freq=100, duty=64)
        self.i_duty = 0
        self.duties = [64, 128, 512, 768, 1020]

    def set_duty(self, duty):
        self.pwm.duty(duty)

    def next_duty(self):
        self.i_duty = (self.i_duty + 1) % len(self.duties)
        print('Set duty:', self.duties[self.i_duty])
        self.pwm.duty(self.duties[self.i_duty])

import tft_config
backlight = BackLight(tft_config.BACKLIGHT)

class Buzzer():
    def __init__(self, pin_number):
        self.buzzer = Pin(pin_number, Pin.OUT)
        self.buzzer.value(0)
        self.tasks = []

    async def beep_job(self, times, dur_ms = 500):
        for t in range(times):
            self.buzzer.value(1)
            await asyncio.sleep_ms(dur_ms)
            self.buzzer.value(0)
            await asyncio.sleep_ms(500)

    def do_beep(self, times):
        self.tasks.append(asyncio.create_task(self.beep_job(times)))

    def stop_all(self):
        for t in self.tasks:
            t.cancel()
            self.buzzer.value(0)
            self.tasks.remove(t)


buzzer = Buzzer(21) # buzzer is attached to pin 21
