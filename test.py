# https://ssd1306.readthedocs.io/en/latest/python-usage.html
from luma.oled.device import sh1106
from luma.core.render import canvas
from luma.core.interface.serial import i2c
# https://python-escpos.readthedocs.io/en/latest/
from escpos.printer import Serial
import os
import random
import time

serial = i2c(port=1, address=0x3C)
device = sh1106(serial)
device.show()

valid = False
while not valid:
    cost = random.randint(0,20)
    valid = os.path.exists(os.path.join('cards', str(cost)))

# https://pillow.readthedocs.io/en/latest/reference/ImageDraw.html#module-PIL.ImageDraw
with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline="white", fill="black")
    draw.text((5, 20), "Choosing random", fill="white")
    draw.text((5, 40), f"{cost} cost card", fill="white")

time.sleep(3)
cards = os.listdir(os.path.join("cards", str(cost)))
choice = random.randint(0,len(cards)-1)
chosen_card = cards[choice]

with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline="red", fill="black")
    draw.text((5, 40), chosen_card, fill="white")


p = Serial(devfile='/dev/serial0',
           baudrate=9600,
           bytesize=8,
           parity='N',
           stopbits=1,
           timeout=1.00,
           dsrdtr=True)
p.image(os.path.join("cards", str(cost), chosen_card))

time.sleep(3)
device.hide()