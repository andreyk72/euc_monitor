# euc_monitor

Electric Unicycle real time status monitor, implemented for ESP32-S3 based board LilyGo T-Display S3 on Micropython.
Gets the real time data, such as speed, battery voltage etc from the wheel via bluetooth and shows on the display. Currently supports KingSong wheels only. 

# Features

- Shows current speed, PWM, battery percentage, controller temperature current trip disance and many more
- Several display screens with horizontal and vertical orientations, easy switch between them with the buttons.
- Can be mounted on the top of the EUC body. Special screen with sliding values - Speed 10 seconds, then Battery Percentage 5 seconds then Current Trip Distance 5 seconds, all shown with huge size font for better visibility.
- Calculates peak power and tracks maximum values. Special screen showing the maximums.
<<<<<<< HEAD
- Tracks maximums of PWM, Temperature and Minimum Battery Voltage. Shows alarm on the screen and activates buzzer beeps. Special screen with list of last alarms. Note buzzer is not a part of the LilyGo board and must be connected externally to GPIO21.
- The STLs for the device body are included.
=======
- Tracks maximums of PWM, Temperature and minimum battery voltage. Shows alarm on the screen and activates buzzer beeps. Special screen with list of last alarms. Note buzzer is not a part of the LilyGo board and must be connected externally to GPIO21.
- Monitor battery health, measure max voltage drop and the battey internal resistance (in Omhs)
- The STLs for the device body  is included.
>>>>>>> dea362d (More reliable connection, support more wheels)

# Restrictions/Problems

- Currently only KingSong communicaiton protocol is implemented
- The bluetooth device names are hardcoded, no device selection screen is implemented. The connection is done on the first wheel found in the list.
- No wake up from Deepsleep via control buttos (does not work for some reason on my board) - reset button  is required to be pressed to wake up.
- The battery percentage calculation formula is different from the one in KingSong app, and shows less percentage.
- Currently only some 16s and 20s models are configured to be detected for finding number of the battery sells. Small code change is required to add more wheel models. 


# User Manual

* Single click on the left or right button - change screens 
* Double click on the left buton - change the wheel light mode between
  - Lights Off - Leds Off
  - Lights On (Auto) - Leds Off
  - Lights On (Auto) - Leds On
* Double click on the right button - change the display backlight 
* Long press on the right button - activate deepsleep mode
* Exit from deepsleep - Reset button.

# Installation

First you need to compile and install Micropython with s3lcd display driver on your board. Please see the instructions on its github page [s3lcd driver](https://github.com/russhughes/s3lcd).

For this project esp-idf version 5.2 and micropython version 1.23 were used. 

It is important to build micropython with SPIRAM (aka PSRAM) support. There's 8mb of PSRAM installed on the board and must be visible by micropython. The internal ESP32 RAM memory is not enough for running the app. To check if the SPIRAM is available the function in heap_mon.py can be used.

The s3lcd project installation instructions contain two problems. 
- First micropython/ports directory must contain a symlink to where the s3lcd library was cloned.
- Second the build command for compilation with SPIRAM is wrong and must be the following:

The command:

     make \
	    BOARD=ESP32_GENERIC_S3 \
	    BOARD_VARIANT=SPIRAM_OCT \
	    USER_C_MODULES=../../../../s3lcd/src/micropython.cmake \
	    FROZEN_MANIFEST=../../../../s3lcd/manifest.py \
	    clean submodules all

The same variables must be used when flashing the board:

    make \
	    BOARD=ESP32_GENERIC_S3 \
	    BOARD_VARIANT=SPIRAM_OCT \
	    USER_C_MODULES=../../../../s3lcd/src/micropython.cmake \
	    FROZEN_MANIFEST=../../../../s3lcd/manifest.py \
	    erase deploy

After the micropython is sucessfully installed the python code can be deployed. For this you will need the micropython cross compiler mpy-cross (must be already provided by micropython) and mpremote utility that is usually installed via pip.

With all this available type (use your usb port path)

    $ export PORT=/dev/cu.usbmodemXXX
    $ make install

When any code changes are done run
    
    $ make run
    
This will compile the changes, upload them and start the REPL.

To start the REPL on board that is already running 

    $ make repl
    
Note the development is configured to use pre-compiled python modules (.mpy) however main.py must be available on the board.


# Configuration

## Connection to a wheel

In file ble.py you must configure names of your wheels:

    device_names = ['KSN-16X-120093','KS-16S0130']
    
The connection will be done to the first wheel found and waiting for connect.

## Add your wheel models

In order to detect number of cells of the main battery correctly the small modification in code is required. The code currently knows about some 16S and 20S wheels.
This can be done in file ble.py customizing the following code:

    BATT_16S = ['16S']
    BATT_20S = ['16X', 'S18', '18L', '18X'] #include only first 3 symbols of the model!
    
If you are connecting to a wheel with another number of cells, the small code modification is required in the file ble.py:

    if ss[1][0:3] in BATT_16S:
        g_wheeldata.cells = 16
    if ss[1][0:3] in BATT_20S:
        g_wheeldata.cells = 20
