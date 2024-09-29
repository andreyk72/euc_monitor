#import sys

# ruff: noqa: E402
#sys.path.append("")

#from micropython import const
# main.py -- put your code here!


from micropython import const

import gc
import asyncio
import bluetooth
import aioble

import random
import struct


#MPY: soft reboot
#Connecting to Device(ADDR_PUBLIC, b4:10:7b:36:2b:c5)

#device_name = 'KS-16S0130'
device_names = ['KSN-16X-120093','KS-16S0130']
KS_CHAR_UUID = bluetooth.UUID(0xffe1) #bluetooth.UUID("0000ffe1-0000-1000-8000-00805f9b34fb")
KS_SERV_UUID = bluetooth.UUID(0xffe0) # bluetooth.UUID('0000ffe0-0000-1000-8000-00805f9b34fb')


from wheeldata import g_wheeldata


def decode4byte(data: bytearray, position):
    val_h, val_l = struct.unpack_from('<HH', data, position)
    return (val_h << 16) + val_l

BATT_16S = ['16S']
BATT_20S = ['16X', 'S18', '18L', '18X'] #include only first 3 symbols of the model!

def decode_ks_packet(data: bytearray):
    #packet = struct.unpack("<B", data)
    # check header and format
    if len(data) >= 20:
        a1 = data[0] & 255
        a2 = data[1] & 255
        if a1 != 170 and a2 != 85:
            return f"Packet Is not Recognized: {data}"
    else:
        return "packet is too short: data:{}".format(data)
    if (data[16] & 255) == 0xA9: # Live data
        voltage = struct.unpack_from("<H", data, 2)[0] / 100.0
        speed = struct.unpack_from("<H", data, 4)[0] / 100.0

        odo = decode4byte(data, 6) / 1000.0 # KS18L scaler is skipped!
        current = struct.unpack_from('<h', data, 10)[0] / 100.0 # current can be negative!!
        #wd.setCurrent((data[10] & 0xFF) + (data[11] <<
        temperature = struct.unpack_from('<H', data, 12)[0] / 100.0
        mode : byte = 0x0
        if (data[15] & 255) == 224:
            mode = struct.unpack_from("<B", data, 14)[0]
        g_wheeldata.live_pkt.update(voltage, speed, odo, current, temperature, mode)
        return # str(g_wheeldata.live_pkt)

    elif (data[16] & 255) == 0xF6: # { //speed limit (PWM?)
                speedlimit = struct.unpack_from("<H", data, 2)[0] / 100.0
                g_wheeldata.speedlimit_pkt.update(speedlimit)
                return  #str(g_wheeldata.speedlimit_pkt)

    elif (data[16] & 255) == 0xB9:
        trip = decode4byte(data, 2) / 1000.0
        uptime = struct.unpack_from('<H', data, 6)[0] / 100.0
        topspeed = struct.unpack_from('<H', data, 8 )[0] / 100.0
        fanstate = struct.unpack_from('<B', data, 12)[0] # 1 if fan is running
        g_wheeldata.trip_pkt.update(trip, uptime, topspeed, fanstate)
        return  #str(g_wheeldata.trip_pkt)

    elif (data[16] & 255) == 0xf5: #cpu load
        cpuload = struct.unpack_from('<B', data, 14)[0]
        output = struct.unpack_from('<B', data, 15)[0]
        g_wheeldata.cpuload_pkt.update(cpuload, output)
        return  #str(g_wheeldata.cpuload_pkt)

    elif (data[16] & 255 ) == 0xbb: # name and model
        modelstr = str(data[2:14].decode()) #, encoding='iso-8859-1')
        ss = modelstr.split('-')
        print('Name', ss[0], 'Model', ss[1], 'Version', ss[2])
        g_wheeldata.name = ss[0]
        g_wheeldata.model = ss[1]
        g_wheeldata.version = ss[2]
        if ss[1][0:3] in BATT_16S:
            g_wheeldata.cells = 16
        if ss[1][0:3] in BATT_20S:
            g_wheeldata.cells = 20
        g_wheeldata.got_name_and_model = True
        print('Detected number of cells:', g_wheeldata.cells)
        return #Name and model", data
    else:
         return f"Not a Live Data Packet: {data}"

async def discover_chars_for_service(ks_service):
    """an example, not used in the ode currently"""
    chars = []
    async for characteristic in ks_service.characteristics():
        chars.append(characteristic)
        print('found ch:', characteristic)
    for c in chars:
        print('char:', c)
        async for descriptor in c.descriptors():
            print('\tdescriptor:',descriptor)

async def discover_devices():
    # Scan for 5 seconds, in active mode, with very low interval/window (to
    # maximise detection rate).
    res_name = set()
    res_services = {}
    async with aioble.scan(duration_ms=10000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for device in scanner:
            if device.addr() not in res_name:
                res_name.add(result.name())
                serv = []
                for s in result.services():
                    serv.append(s)
                    print('Service: - ', s)
                res_services[result.name()] = serv

    print('Scan complete. Devices:')
    for d in res_name:

        print('Device:', d  , 'Services:', res_services.get(d, 'No Services'))
    return None




async def find_ks_device():
    async with aioble.scan(duration_ms=5000, interval_us=30000, window_us=30000, active=True) as scanner: # , active=True) as scanner:
        async for result in scanner:
            #if KS_SERV_UUID in result.services():
            #    print('nectfound device:', result.device)
            #    return result.device

            if result.name() in device_names:
                print("Device: ", result)
            #    for s in result.services():
            #        print('se:', s)
                #if KS_SERV_UUID in result.services():
                #    return result.device
                #else:
                #    print("Device is present but the service is not found")
                return result.device
    return None




from tft_display import gui



class Ble():
    def __init__(self):
        self.connection = None
        self.device = None
        self.service = None
        self.characteristic = None

    async def connect_and_process(self):
        #print('Scan for devices:')
        #await discover_devices()
        gui.jump_to_connect()
        gc.collect()
        try:
            self.device = await find_ks_device()
            if not self.device:
                print("KS Device is not found")
                return
            print("Connecting to", self.device)
            self.connection = await self.device.connect()
            if self.connection:
                print('Connected')
            else:
                print('could not connect to the device')
        except asyncio.TimeoutError:
            print("Timeout during connection")
            return
        async with self.connection:
            try:
                self.service = await self.connection.service(KS_SERV_UUID)
                if self.service:
                    print('Connected to service ', KS_SERV_UUID)
                else:
                    print('Could not connect to service' , KS_SERV_UUID)
                    return
                print('connect ot characteristic', KS_CHAR_UUID)
                self.characteristic = await self.service.characteristic(KS_CHAR_UUID)
                if self.characteristic:
                    await self.characteristic.subscribe(notify=True)
                    print('Subscribed to:', self.characteristic)

                else:
                    print('failed to get characteristic', KS_CHAR_UUID)
                    return
            except asyncio.TimeoutError:
                print("Timeout discovering services/characteristics")
                return
            gui.back_from_connect()
            try:
                    #immediately send a request!
                if not g_wheeldata.got_name_and_model: # do it untill get result (:
                    await asyncio.sleep_ms(100)
                    await self.request(0x9b) # request manufacturer and model

                #await asyncio.sleep_ms(100)
                #if self.connection.is_connected():
                #    pass
                    #await self.request(0x9B) # request manufacturer and model
                    #await asyncio.sleep_ms(100)
                    #await self.request(0x63) # request serial data
                #else:
                #    print('oops disconnected')

                while self.connection.is_connected():
                    #print('wait for notification')
                    data = await self.characteristic.notified() # yes! this method returns data that cause the notification!!!
                    res = decode_ks_packet(data)
                    if res:
                        print(res)
                    await asyncio.sleep_ms(10)
                    #cnt -= 1
                    #if cnt < 0:
                    #    return
            except Exception as e:
                print(f'BLE server disconnected: {e}')
                import sys
                sys.print_exception(e)
            finally: # set object to disconnected state
                await self.disconnect()

    def is_connected(self):
        if self.connection:
            return self.connection.is_connected()
        return False

    async def disconnect(self):
        if self.is_connected():
            await self.connection.disconnect()
        self.connection = None
        self.device = None
        self.service = None
        self.characteristic = None
        g_wheeldata.got_name_and_model = False

    async def request(self, reqtype: byte, value_2 = 0x0, value_3 = 0x0): # value_2 and value_3 - write parameter value
        if self.characteristic:
            ba = bytearray(20)
            ba[0] = 0xAA
            ba[1] = 0x55
            ba[2] = value_2
            ba[3] = value_3
            ba[16] = reqtype
            ba[17] = 0x14
            ba[18] = 0x5A
            ba[19] = 0x5A
            #print('request: ba:' , ba)
            await self.characteristic.write(ba)
        else:
            print('request: characteristic is broken')



ble = Ble()

#asyncio.run(ble_process())


async def scan():
    async with aioble.scan(duration_ms=2000, interval_us=30000, window_us=30000, active=True) as devices:  # Scan for 5 seconds
        #print('Devices:',  devices)
        #print('\n'.join(dir(devices)))
        async for result in devices:
            #print('Device:', '\n'.join(dir(device.adv_data)))
            print(f"Device: {result.name()}, Address: {result.device.addr_hex()}")
            for adv in result.services():
                print(f"Advertised Service: {adv}")
            if result.device.addr_hex() == 'b4:10:7b:36:2b:c5':
                return result.device
    return None


#asyncio.run(scan())

async def connect_and_discover(addr):
    device = await scan()
    #if not device:
    connection = await device.connect()
    print('Connection ', "\n".join(dir(connection)), '\n device: ', "\n".join(dir(device)))
    serv = []
    async for service in connection.services():
        print(f"Service UUID: {service.uuid}")
        serv.append(service)
        #characteristics = await service.discover_characteristics()
    for s in serv:
        print('For service', s)
        async for char in s.characteristics():
            print(f"Characteristic UUID: {char.uuid}")

#asyncio.run(connect_and_discover("b4:10:7b:36:2b:c5"))
