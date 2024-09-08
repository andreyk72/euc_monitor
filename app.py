import sys, time

#from heap_mon import heap_info
# ruff: noqa: E402
sys.path.append("")

time.sleep(3) #chance to connect and hit ctrl-c if anything goes really wrong. Instead "press a key to contioue"

import tft_display
import gc
import asyncio
from  ble import ble
from board import read_vbatt_loop
import tft_buttons

print('main: import done')

buttons = tft_buttons.Buttons()


initialized = False


def init():
    global initialized
    tft_display.init()
    initialized = True


def deinit():
    global initialized
    initialized = False
    tft_display.deinit()
    ble.disconnect()




def set_global_exception():
    def handle_exception(loop, context):
        import sys
        sys.print_exception(context["exception"])
        sys.exit()
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)

async def main():

    set_global_exception()
    #setup GUI loop
    gui_task = asyncio.create_task(tft_display.gui.loop_forever())
    vbatt_task = asyncio.create_task(read_vbatt_loop())
    #then go to bluetooth loop
    while initialized:
        #await ble.connect()
        await ble.connect_and_process() # main bt reading loop inside here
        await asyncio.sleep_ms(1000) # rest for one second and try to re-connect
        gc.collect()
    # stop by some exception
    gui_task.cancel() # stop GUI loop
    vbatt_task.cancel()

try:
    gc.enable()
    gc.collect()
    init()
    asyncio.run(main())
finally:
    deinit()
    asyncio.new_event_loop()  # Clear retained state
    print('main global finally')
