print('starting')
# https://ssd1306.readthedocs.io/en/latest/python-usage.html
# https://pillow.readthedocs.io/en/latest/reference/ImageDraw.html#module-PIL.ImageDraw
from luma.oled.device import sh1106
from luma.core.render import canvas
from luma.core.interface.serial import i2c
# https://python-escpos.readthedocs.io/en/latest/
from escpos.printer import Serial
from gpiozero import Button
from signal import pause
import os
import random
import time

print('display setup')
# 132x64 sh1106 display
serial = i2c(port=1, address=0x3C)
device = sh1106(serial)
device.show()

print('button setup')
# 2 buttons
left_button = Button(17, bounce_time=0.3)
right_button = Button(27, bounce_time=0.3)

current_card = None
current_cost = 0
with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline="white", fill="black")
    draw.text((5, 20), f"Choice: {str(current_cost)} mana", fill="white")

def up_cost():
    current_cost += 1
    if current_cost > 8:
        current_cost = 0
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((5, 20), f"Choice: {str(current_cost)} mana", fill="white")

left_button.when_pressed = up_cost
    
def choose_random_card(cost):
    # returns path to card img
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((5, 20), "Choosing random", fill="white")
        draw.text((5, 40), f"{str(cost)} cost card", fill="white")
    time.sleep(3)
    cards = os.listdir(os.path.join("cards", str(cost)))
    choice = random.randint(0,len(cards)-1)
    chosen_card = cards[choice]
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((5, 40), chosen_card.replace('.jpg',''), fill="white")
    return chosen_card

def get_card():
    current_card = choose_random_card(current_cost)
    print_card(os.path.join('cards',str(current_cost),current_card))

right_button.when_pressed = get_card

def print_card(path):
    p = Serial(devfile='/dev/serial0',
               baudrate=9600,
               bytesize=8,
               parity='N',
               stopbits=1,
               timeout=1.00,
               dsrdtr=True)
    p.image(path)
    # 4 newlines to push card out of printer
    p.text('\n\n\n\n')

print('ready')
pause()
