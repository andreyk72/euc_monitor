
import gc
import asyncio
import s3lcd
import tft_config
import time
import NotoSans16 as font_16
import NotoSans24 as font_24
import NotoSans80 as font_80
import NotoSans32 as font_32
import NotoSans120 as font_120
import board


tft = tft_config.config(tft_config.TALL)
tft_initialized = False

from wheeldata import g_wheeldata

DISPLAY_REFRESH_MS = 50

def center_x_pos(font, text):
    return tft.width() // 2 - tft.write_len(font, text) // 2

def left_x_pos(font, text):
    return tft.width() // 4 - tft.write_len(font, text) // 2

def right_x_pos(font, text):
    return (tft.width() * 3) // 4 - tft.write_len(font, text) // 2


def center_text(using_font, text, fg=s3lcd.WHITE, bg=s3lcd.BLACK):
    """
    Centers the given text on the display.
    """
    s = f'{text:3d}' if isinstance(text, int) else text
    length = len(s)

    tft.write(
        using_font,
        s,
        center_x_pos(using_font, s),
        tft.height() // 2 - using_font.HEIGHT // 2,
        fg,
        bg,
    )


def color_by_latency(packet , color):
    lat = packet.get_age_ms()
    if lat < 500:
        return color
    if lat >= 500 and lat < 1500:
        return s3lcd.YELLOW
    if lat >= 1500:
        return s3lcd.RED

def color_by_cell_voltage(volt):
    if volt > 3.7:
        return s3lcd.GREEN
    if volt > 3.3:
        return s3lcd.YELLOW
    return s3lcd.RED

def color_by_batt_percent(pct):
    if pct > 40:
        return s3lcd.GREEN
    if pct > 25:
        return s3lcd.YELLOW
    return s3lcd.RED

def render_batt():
    #batt
    bpct = board.batt_percentage()
    if tft.width() < tft.height():
        r_x = 5
        r_y = 306
        p_x = 64
        p_y = 300
    else:
        r_x = 5
        r_y = 170 - 20 + 6
        p_x = 64
        p_y = 170 - 20

    tft.fill_rect(r_x, r_y, int(bpct / 2), 5 , color_by_batt_percent(bpct))
    tft.write(font_16, f'{bpct:3d}%', p_x, p_y, color_by_batt_percent(bpct))

from alarms import alarms

alarm_counter = 0
alarm_text = ""
def render_alarm():
    global alarm_counter, alarm_text
    al = alarms.get_next_alarm()
    if al:
        print("show_alarm:", al)
        alarm_counter =  (1000 // DISPLAY_REFRESH_MS) * 5  # show for 5 seconds
        alarm_text = al
        center_text(font_32, al, s3lcd.YELLOW, s3lcd.RED)
    if alarm_counter > 0:
        alarm_counter -= 1
        center_text(font_32, alarm_text, s3lcd.YELLOW, s3lcd.RED)



class Screen():
    def __init__(self):
        self.name = 'Abstract'
    def render():
        pass

class ConnectScreen(Screen):
    def __init__(self):
        self.name = 'Connect'
    def render(self):
        tft.rotation(tft_config.TALL)
        tft.fill(s3lcd.BLACK)
        center_text(font_24, 'Connecting...')
        render_batt()
        render_alarm()
        tft.show()

class MainScreen(Screen):
    def __init__(self):
        self.name = 'Main'
    def render(self):
        tft.rotation(tft_config.TALL)
        tft.fill(s3lcd.BLACK)
        #print('write text')
        tft.write(font_24, 'Speed', 5, 5, s3lcd.WHITE)
        tft.write(font_16, f'Lat:{g_wheeldata.live_pkt.get_age_ms()/1000:4.1f}', 110, 5 , s3lcd.RED)
        speed_s = '{:4.1f}'.format(g_wheeldata.live_pkt.speed)
        tft.write(font_80, speed_s , center_x_pos(font_80, speed_s), 42, \
                  color_by_latency(g_wheeldata.live_pkt, s3lcd.GREEN))

        tft.write(font_24,  'PWM', 5, 130, s3lcd.WHITE)
        tft.write(font_16, f'Lat:{g_wheeldata.cpuload_pkt.get_age_ms()/1000:4.1f}', 110, 130 , s3lcd.RED)
        pwm_s = '{:3d}'.format(g_wheeldata.cpuload_pkt.output)
        tft.write(font_80, pwm_s, center_x_pos(font_80, pwm_s), 162, \
                  color_by_latency(g_wheeldata.live_pkt, s3lcd.BLUE))

        #battery
        tft.write(font_24, 'Batt', left_x_pos(font_24, 'Batt'), 246, s3lcd.WHITE)
        batt_s = '{:3d}%'.format(g_wheeldata.live_pkt.batt_percentage)
        tft.write(font_24, batt_s, left_x_pos(font_24, batt_s), 274, s3lcd.GREEN)

        #temp
        tft.write(font_24, 'Temp', right_x_pos(font_24, 'Temp'), 246, s3lcd.WHITE)
        temp_s = '{:4.1f}'.format(g_wheeldata.live_pkt.temperature)
        tft.write(font_24, temp_s , right_x_pos(font_24, temp_s), 274, s3lcd.BLUE)

        render_batt()
        render_alarm()
        #commit
        tft.show()

class MaxScreen(Screen):
    def __init__(self):
        self.name = 'Max'
    def render(self):
        tft.rotation(tft_config.TALL)
        tft.fill(s3lcd.BLACK)
        tft.write(font_24, 'MAX', 5, 5, s3lcd.WHITE)
        tft.write(font_24, f'Speed:', 5, 42, s3lcd.CYAN)
        tft.write(font_24, f'{g_wheeldata.live_pkt.max_speed:4.1f}' , 90,42 , s3lcd.GREEN)
        tft.write(font_24, f'PWM: ', 5, 79, s3lcd.CYAN)
        tft.write(font_24, f'{g_wheeldata.cpuload_pkt.max_output:3d}', 90, 79, s3lcd.BLUE)
        tft.write(font_24, f'Curr:', 5, 116, s3lcd.CYAN)
        tft.write(font_24, f'{g_wheeldata.live_pkt.max_current:4.1f}', 90 ,116 , s3lcd.YELLOW)

        tft.write(font_24, f'Temp:', 5, 153, s3lcd.CYAN)
        tft.write(font_24, f'{g_wheeldata.live_pkt.max_temperature:4.1f}', 90 , 153, s3lcd.GREEN)
        tft.write(font_24, f'CPU:', 5, 190, s3lcd.CYAN)
        tft.write(font_24, f'{g_wheeldata.cpuload_pkt.max_cpuload:3d}', 90, 190, s3lcd.BLUE)

        tft.write(font_24, 'Trip:', 5, 225, s3lcd.CYAN)
        tft.write(font_24, f'{g_wheeldata.trip_pkt.trip:5.1f}', 90, 225, s3lcd.MAGENTA)

        tft.write(font_24, 'Power', 5, 225, s3lcd.CYAN)
        pow = int(g_wheeldata.live_pkt.max_power)
        tft.write(font_24, f'{pow:4d}', 90, 225, s3lcd.MAGENTA)


        render_batt()
        render_alarm()
        tft.show()

class AlarmsScreen(Screen):
    def __init__(self):
        self.name = 'Alarms'

    def render(self):
        tft.rotation(tft_config.TALL)
        tft.fill(s3lcd.BLACK)
        tft.write(font_24, 'Alarms',  5, 5, s3lcd.BLUE)
        posmax = 320 # points on display
        posy = 24 + 5 + 5
        pos_p = 16 + 4
        for al in reversed(alarms.alarms_display):
            if posy + pos_p < posmax:
                tft.write(font_16, al, 5, posy, s3lcd.YELLOW)
                posy += pos_p
        render_batt()
        render_alarm()
        tft.show()

class PowerScreen(Screen):
    def __init__(self):
        self.name = 'Power'

    def render(self):
        tft.rotation(tft_config.WIDE)
        tft.fill(s3lcd.BLACK)
        tft.write(font_24, 'Power', 2 , 2, s3lcd.WHITE)
        pow = int(g_wheeldata.live_pkt.power)
        center_text(font_120, f'{pow:4d}', color_by_latency(g_wheeldata.live_pkt, s3lcd.GREEN))

        iv_str = f'I:{g_wheeldata.live_pkt.current:4.1f} V:{g_wheeldata.live_pkt.voltage:4.1f}'
        s_size = tft.write_len(font_24, iv_str)

        tft.write(font_24, iv_str, tft.width() - s_size - 2, tft.height() - 24 - 2, s3lcd.RED)

        render_batt()
        render_alarm()
        tft.show()

class PWMScreen(Screen):
    def __init__(self):
        self.name = 'PWM'

    def render(self):
        tft.rotation(tft_config.WIDE)
        tft.fill(s3lcd.BLACK)
        tft.write(font_24, 'PWM', 2 , 2, s3lcd.WHITE)
        pwm = int(g_wheeldata.cpuload_pkt.output)
        center_text(font_120, f'{pwm:3d}', color_by_latency(g_wheeldata.cpuload_pkt, s3lcd.GREEN))

        iv_str = f'I:{g_wheeldata.live_pkt.current:4.1f} V:{g_wheeldata.live_pkt.voltage:4.1f}'
        s_size = tft.write_len(font_24, iv_str)

        tft.write(font_24, iv_str, tft.width() - s_size - 2, tft.height() - 24 - 2, s3lcd.RED)

        render_batt()
        render_alarm()
        tft.show()

class SlideScreen(Screen):
    def __init__(self):
        self.name = 'Slide'
        self.scr_index = 0
        self.slide_map = [[10, self.render_speed], [3, self.render_batt], [3, self.render_dist]]
        self.timeframe = self.slide_map[self.scr_index][0]
        asyncio.create_task(self.screen_job())

    def render_speed(self):
        tft.write(font_32, 'Speed', 0 , 2, s3lcd.YELLOW)
        center_text(font_120, f'{g_wheeldata.live_pkt.speed:4.1f}', color_by_latency(g_wheeldata.cpuload_pkt, s3lcd.GREEN))

        iv_str = f'KM/H'
        s_size = tft.write_len(font_32, iv_str)

        tft.write(font_32, iv_str, tft.width() - s_size - 2, tft.height() - 32 - 2, s3lcd.YELLOW)


    def render_batt(self):
        tft.write(font_32, 'Batt', 0 , 2, s3lcd.YELLOW)
        center_text(font_120, f'{g_wheeldata.live_pkt.batt_percentage:3d}%', color_by_latency(g_wheeldata.cpuload_pkt, s3lcd.MAGENTA))

        iv_str = f'Voltage:{g_wheeldata.live_pkt.voltage:4.1f}V'
        s_size = tft.write_len(font_24, iv_str)

        tft.write(font_24, iv_str, tft.width() - s_size - 2, tft.height() - 24 - 2, s3lcd.YELLOW)


    def render_dist(self):
        tft.write(font_32, 'Trip', 0, 2, s3lcd.YELLOW)
        center_text(font_120, f'{g_wheeldata.trip_pkt.trip:5.1f}', color_by_latency(g_wheeldata.cpuload_pkt, s3lcd.CYAN))

        iv_str = f'KM'
        s_size = tft.write_len(font_32, iv_str)

        tft.write(font_32, iv_str, tft.width() - s_size - 2, tft.height() - 32 - 2, s3lcd.YELLOW)


    def render(self):
        tft.rotation(tft_config.WIDE)
        tft.fill(s3lcd.BLACK)

        self.slide_map[self.scr_index][1]() # call current slide function

        render_batt()
        render_alarm()
        tft.show()


    def next_screen(self):
        self.scr_index = (self.scr_index + 1) % len(self.slide_map)
        self.timeframe = self.slide_map[self.scr_index][0]

    async def screen_job(self):
        while True:
            await asyncio.sleep(self.timeframe)
            self.next_screen()






class Gui():
    def __init__(self):
        self.screens = {'Connect' : ConnectScreen(), 'Main' : MainScreen(), \
                        'Max' : MaxScreen(), 'Alarms' : AlarmsScreen(), \
                        'Power' : PowerScreen(), 'PWM' : PWMScreen(), 'Slide': SlideScreen()}
        self.state = 'Connect'
        #self.page = 'Main'
        self.page_n = 1
        self.pages = ['Alarms', 'Main', 'Max', 'Slide' , 'Power', 'PWM'] # the list of pages that can be navigated via left / right button

    def render(self):
        if tft_initialized:
            self.screens[self.state].render()
        else:
            print('the tft is not initialized!!!')

    def next_page(self):
        self.page_n = (self.page_n + 1) % len(self.pages)
        self.state = self.pages[self.page_n]

    def prev_page(self):
        if self.page_n == 0:
            self.page_n = len(self.pages) - 1
        else:
            self.page_n = self.page_n - 1
        self.state = self.pages[self.page_n]

    async def loop_forever(self):
        while tft_initialized:
            self.render()
            await asyncio.sleep_ms(DISPLAY_REFRESH_MS)





gui = Gui()


def init():
    global tft_initialized
    if not tft_initialized:
        print("Init display:")
        tft.init()
    tft.rotation(4) # default is landscape
    tft.fill(s3lcd.BLUE)
    tft.show()
    tft_initialized = True

def deinit():
    global tft_initialized
    print('deinit')
    tft.deinit()
    tft_initialized = False

def test():
        init()
        gui.state='Connect'
        gui.render()
        deinit()




#main()
