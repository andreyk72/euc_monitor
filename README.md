# euc_monitor

Electric Unicycle real time status monitor, implemented for ESP32-S3 based board LilyGo T-Display S3 on Micropython.
Gets the real time data, such as speed, battery voltage etc from the wheel via bluetooth and show on the display. Currently supports only KingSong wheels. 

# Features

- Shows current speed, PWM, battery percentage, controller temperature current trip disance and many more
- Several display screens with horizontal and vertical orientations, easy switch between them with buttons.
- Can be mounted on the top of the EUC body. Special screen with sliding values - Speed 10 seconds, then battery percentage 5 seconds then Current trip distance 5 seconds, all shown with huge font for better visibility.
- Calculates peak power and tracks maximum values. Special screen showing the maximums.
- Tracks maximums of PWM, Temperature and minimum battery voltage. Shows alarm on the screen and activates buzzer beeps. Special screen with list of last alarms. Note buzzer is not a part of the LilyGo board and must be connected externally to GPIO21.
- The STLs for the device body  is included.

# Restrictions/Problems

- Currently only KingSong communicaiton protocol is implemented
- The bluetooth device name is hardcoded, no device selection screen is implemented
- No wake up from Deepsleep via control buttos (does not work for some reason on my board) - reset button  is required to be pressed to wake up.
- The battery percentage calculation formula is different from the one in KingSong app, and shows less percentage.
- Currently the percentage formula suports only 68 volt battery. Can be changed in near future.

# Installation

First you need to compile and install Micropython with s3lcd display driver on your board. Please see the instructions on its github page [s3lcd driver](https://github.com/russhughes/s3lcd).

For thsi project esp-idf version 5.2 and micropython version 1.23 were used. 

It is important to build micropython with SPIRAM (aka PSRAM) support. There's 8mb of PSRAM installed on the board and must be visible by micropython. The internal ESP32 RAM memory is not enough for running the app. To check if the SPIRAM is available the function in heap_mon.py can be used.

The s3lcd project installation instructions contain two problems. 
- First micropython/ports directory must contain a symlink to where the s3lcd library was cloned.
- Second the build command for compilation with SPIRAM is wrong and must be the following:

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



