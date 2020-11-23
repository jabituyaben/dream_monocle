# CPX M0 Dream Monocle - Ben Jabituya
import time
import board
import neopixel
import digitalio
from analogio import AnalogIn
import adafruit_lis3dh
import busio
import math
import microcontroller
import array

RED = (255, 0, 0)
GREEN = (0, 255, 0)
OFF = (0, 0, 0)

brightness_button = digitalio.DigitalInOut(board.D4)
brightness_button.direction = digitalio.Direction.INPUT
brightness_button.pull = digitalio.Pull.DOWN

time_delay_button = digitalio.DigitalInOut(board.D5)
time_delay_button.direction = digitalio.Direction.INPUT
time_delay_button.pull = digitalio.Pull.DOWN

#ADVANCED SETTINGS
cooldown_delay = 200
passive_mode = False
led_brightness = 0.06
time_delay = 2
rainbow_cycle_count = 8
log_limit = 2000 #lines

i2c = busio.I2C(board.ACCELEROMETER_SCL, board.ACCELEROMETER_SDA)
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19)
lis3dh.range = adafruit_lis3dh.RANGE_8_G

analog1in = AnalogIn(board.IR_PROXIMITY)

ir_led = digitalio.DigitalInOut(board.IR_TX)
ir_led.direction = digitalio.Direction.OUTPUT

def set_delay():
    global time_delay
    global boot_time

    for led in range(time_delay):
        pixels[led] = RED
        pixels.show()
    boot_time = time.monotonic()
    time.sleep(1)
    start_time = time.monotonic()
    timegap = time.monotonic() - start_time

    while timegap < 5:
        if time_delay_button.value:
            time.sleep(0.1)
            start_time = time.monotonic()
            if time_delay  == 10:
                time_delay = 1
            else:
                time_delay += 1
            pixels.fill(OFF)
            pixels.show()

            for led in range(time_delay):
                pixels[led] = RED
                pixels.show()
        timegap = time.monotonic() - start_time
    save_settings()
    rainbow_cycle(0.05)
    pixels.fill(OFF)
    pixels.show()

def set_brightness():
    global led_brightness
    pixels.fill(GREEN)
    pixels.show()
    time.sleep(1)
    start_time = time.monotonic()
    timegap = time.monotonic() - start_time
    while timegap < 5:
        if brightness_button.value:
            time.sleep(0.1)
            start_time = time.monotonic() #reset counter
            if led_brightness > 0.1:
                led_brightness = 0.02
            else:
                led_brightness += 0.02
            pixels.brightness = led_brightness
            pixels.fill(GREEN)
            pixels.show()
        timegap = time.monotonic() - start_time
    save_settings()
    rainbow_cycle(0.05)
    pixels.fill(OFF)
    pixels.show()

def load_settings(fname):
    global led_brightness
    global time_delay
    with open(fname) as f:
        first_line = f.readline()
        settings = first_line.split("|")
        led_brightness = float(settings[0])
        time_delay = int(settings[1])

def save_settings():
    global led_brightness
    global time_delay

    settings_string = str(led_brightness) + "|" + str(time_delay)
    try:
        with open("\lucid_settings.txt", "w") as f:
            f.write(settings_string)
            f.flush
    except OSError as e:
        print(e)
        pass

def wheel(pos):
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)

def rainbow_cycle(wait):
    for i in range(10):
        rc_index = (i * 256 // 10) + 5 * 5
        pixels[i] = wheel(rc_index)
        pixels.show()
        time.sleep(wait)
        pixels[i] = OFF
        pixels.show()

def get_stanard_deviation(type):
    counter = 30
    value_samples = []
    function_start_time = time.monotonic()

    if type == "IR":
        for x in range(counter):
            ir_led.value = True
            time.sleep(0.005)
            ir_led.value = False
            time.sleep(0.001)
            value = analog1in.value
            if value > 0:
                value_samples.append(value)
            time.sleep(0.17)

    else:
        for x in range(counter):
            x,y,z = lis3dh.acceleration
            all_angles = abs(x),abs(y),abs(z)
            value_samples.append(sum(all_angles))
            time.sleep(0.05)

    if len(value_samples) > 10:
        write_to_file(str(value_samples))
        average_value = sum(value_samples)/len(value_samples)
        variance = sum(pow(x-average_value, 2) for x in value_samples) / len(value_samples)
        standard_deviation = math.sqrt(variance)
        return standard_deviation

def check_for_movement():
    global log_counter
    global log_eye_movement
    global face_movement
    function_start_time = time.monotonic()
    timer = 0

    face_movement.clear()
    while timer < 20:
        log_face_movement = get_stanard_deviation("ACCEL")
        face_movement.append(log_face_movement)
        time.sleep(5)
        timer = time.monotonic() - function_start_time
    print("face movement count = " + str(len(face_movement)))
    log_eye_movement = get_stanard_deviation("IR")

def write_to_file(sentence):
    global logfile_linecount
    global log_limit

    if logfile_linecount < log_limit:
        try:
            with open("/logfile.csv", "a") as fp:
                fp.write(sentence + ' \n')
                fp.flush()
                logfile_linecount += 1
        except OSError as e:
            print(e)
            pass

def Average(lst): 
    return sum(lst) / len(lst) 

# MAIN LOOP
boot_time = time.monotonic()
face_movement = []
log_counter = 0
log_eye_movement = 0
counter = 0
logfile_linecount = 0
REM_count = 0

try:
    file = open("/logfile.csv","w")
    file.close()
except OSError as e:
    print(e)
    pass

load_settings("/lucid_settings.txt")
pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=led_brightness, auto_write=False)

while True:
    if brightness_button.value:
        set_brightness()
    
    if time_delay_button.value:
        set_delay()

    timegap = time.monotonic() - boot_time

    if timegap > 20:
        real_timedelay = time_delay * 60 * 30
        if time_delay == 1:
            real_timedelay = 0

        if timegap > real_timedelay:
            check_for_movement()
            counter += 1
            average_face_movement = Average(face_movement)*100
            timer = time.monotonic() - boot_time
            logstring = str(round(timer)) + "," + str(round(log_eye_movement)) + "," + str(round(average_face_movement)) + "," + str(round(microcontroller.cpu.temperature))
            print(logstring)
            write_to_file(logstring)
            
            if log_eye_movement > 1000 and average_face_movement < 50:
                print("REM detected, wait for second occurance before cueing")
                if REM_count > 0:
                    print("trigger Rainbow cycle")
                    write_to_file("sweet dreams")
                    if passive_mode == False:
                        for x in range(rainbow_cycle_count):
                            rainbow_cycle(0.005)
                else:
                    REM_count += 1

            if counter == 5:
                REM_count = 0          
                counter = 0
                time.sleep(cooldown_delay)