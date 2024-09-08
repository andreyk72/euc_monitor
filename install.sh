#!/usr/bin/env sh

mpremote connect /dev/cu.usbmodem1234561 mip install aioble
mpremote mip install "github:peterhinch/micropython-async/v3/primitives"

mpremote  cp ble.py :
mpremote  cp tft_config.py :
mpremote  cp tft_buttons.py :
mpremote  cp wheeldata.py :
mpremote cp Noto*.mpy :
mpremote  cp tft_display.py :
mpremote  cp main.py :
