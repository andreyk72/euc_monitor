# Define the list of Python source files
PY_SOURCES := $(wildcard *.py)

# Define the corresponding compiled files
MPY_OBJECTS := $(PY_SOURCES:.py=.mpy)

# Define the target device
DEVICE := :

# Define the mpy-cross command
MPY_CROSS := mpy-cross

# Define the mpremote command
MPREMOTE := mpremote

# File to track updated files
UPDATED_FILES := .updated_files

# Connect to the device with repl
repl:
	@$(MPREMOTE) repl

.phony: rm_updated
rm_updated:
	rm -f $(UPDATED_FILES);

# Rule to compile .py files to .mpy files
%.mpy: %.py
	$(MPY_CROSS) $<
	-echo $@ >> $(UPDATED_FILES)



# Rule to determine if a .mpy file needs to be updated
.PRECIOUS: %.mpy
.SECONDARY: $(MPY_OBJECTS)

# Rule to compile only
compile: rm_updated $(MPY_OBJECTS)

# Rule to transfer compiled .mpy files to the device
transfer:
	@if [ -f $(UPDATED_FILES) ]; then \
		for mpy in $$(cat $(UPDATED_FILES)); do \
			$(MPREMOTE) cp  $$mpy $(DEVICE); \
		done; \
		rm -f $(UPDATED_FILES); \
	fi
#	@$(MPREMOTE) repl

# Rule to compile and transfer
all: compile transfer

reset:
	$(MPREMOTE) reset ; \
    $(MPREMOTE) sleep 2


run: compile transfer  reset repl



# Clean up compiled files
clean:
	rm -f $(MPY_OBJECTS) $(UPDATED_FILES)

## Install on fresh new micropython device. Run as $> make PORT=/dev/cu.usbmodemXXX install
install: compile
	mpremote connect $(PORT) mip install aioble \
	mpremote mip install "github:peterhinch/micropython-async/v3/primitives" \
	mpremote  cp ble.mpy : \
	mpremote  cp tft_config.mpy : \
	mpremote  cp tft_buttons.mpy : \
	mpremote  cp wheeldata.mpy : \
	mpremote cp Noto*.mpy : \
	mpremote  cp tft_display.mpy : \
	mpremote  cp main.py : \
	mpremote cp app.mpy : \
	mpremote cp alarms.mpy : \
	mpremote cp heap_mon.mpy : \
    mpremote cp board.mpy :
