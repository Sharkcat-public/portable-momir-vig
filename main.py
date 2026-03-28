#TODO
# add timestamps to stdout
# better text output (alignment, splitting into multiple lines)
# better text for card display (or show the card image)
# better rng

import os
import random
import time
print(f'{time.strftime("%Y-%m-%d %H:%M:%S")} starting main momir-vig')
# https://ssd1306.readthedocs.io/en/latest/python-usage.html
# https://pillow.readthedocs.io/en/latest/reference/ImageDraw.html#module-PIL.ImageDraw
from luma.oled.device import sh1106
from luma.core.render import canvas
from luma.core.interface.serial import i2c
# https://python-escpos.readthedocs.io/en/latest/
from escpos.printer import Serial
from gpiozero import Button
from signal import pause

def get_working_dir():
    return os.path.dirname(os.path.realpath(__file__))

def display_mana_choice():
    global current_cost
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((5, 20), f"Choice: {str(current_cost)} mana", fill="white")

def display_shutdown_confirm():
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((5, 20), f"Do you want to shutdown?", fill="white")
        draw.text((5, 40), f"Yes", fill="white")
        draw.text((50, 40), f"No", fill="white")

def up_cost():
    global current_cost
    global available_cmc
    current_index = available_cmc.index(current_cost)
    current_index += 1
    if current_index >= len(available_cmc):
        current_index = 0
    current_cost = available_cmc[current_index]

def down_cost():
    global current_cost
    global available_cmc
    current_index = available_cmc.index(current_cost)
    current_index -= 1
    if current_index < 0:
        current_index = len(available_cmc) - 1
    current_cost = available_cmc[current_index]

def roll_random_card():
    global current_cost
    global current_card
    # returns path to card img
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((5, 20), "Choosing random", fill="white")
        draw.text((5, 40), f"{str(current_cost)} cost card", fill="white")
    time.sleep(2)
    cards = os.listdir(os.path.join(get_working_dir(), "cards", str(current_cost)))
    choice = random.randint(0,len(cards)-1)
    current_card = cards[choice]
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((5, 40), current_card.replace('.jpg',''), fill="white")

def print_card():
    global current_card
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((5, 20), "Printing", fill="white")
        draw.text((5, 40), current_card.replace('.jpg',''), fill="white")
    p = Serial(devfile='/dev/serial0',
               baudrate=9600,
               bytesize=8,
               parity='N',
               stopbits=1,
               timeout=1.00,
               dsrdtr=True)
    p.image(os.path.join(get_working_dir(), 'cards',str(current_cost),current_card))
    # 4 newlines to push card out of printer
    p.text('\n\n\n\n')

def left_button_func():
    global current_state
    if current_state == 0:
        down_cost()
        display_mana_choice()
    elif current_state == 1:
        roll_random_card()
        

def right_button_func():
    global current_state
    if current_state == 0:
        up_cost()
        display_mana_choice()
    elif current_state == 1:
        roll_random_card()

def accept_button_func():
    global current_state
    if current_state == -1:
        device.hide()
        os.system("shutdown now -h")
    elif current_state == 0:
        roll_random_card()
        current_state += 1
    elif current_state == 1:
        current_state += 1
        print_card()
        current_state = 0
        display_mana_choice()

def back_button_func():
    global current_state
    if current_state == -1:
        current_state += 1
        display_mana_choice()
    elif current_state == 0:
        current_state -= 1
        display_shutdown_confirm()
    elif current_state == 1:
        current_state -= 1
        display_mana_choice()

print('display setup')
# 132x64 sh1106 display
serial = i2c(port=1, address=0x3C)
device = sh1106(serial)
device.show()

print('button setup')
# 4 buttons
left_button = Button(17, bounce_time=0.01)
right_button = Button(27, bounce_time=0.01)
accept_button = Button(22, bounce_time=0.01)
back_button = Button(23, bounce_time=0.01)
left_button.when_pressed = left_button_func
right_button.when_pressed = right_button_func
accept_button.when_pressed = accept_button_func
back_button.when_pressed = back_button_func

available_cmc = []
for c in os.listdir(os.path.join(get_working_dir(), 'cards')):
    available_cmc.append(int(c))
available_cmc.sort()

# states:
# -1: shutdown
# 0: mana choice
# 1: card gen
# 2: card print
current_state = 0
current_card = None
current_cost = available_cmc[0]
display_mana_choice()

print('ready')
pause()
device.hide()
