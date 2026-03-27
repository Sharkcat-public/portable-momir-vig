# https://ssd1306.readthedocs.io/en/latest/python-usage.html
from luma.oled.device import sh1106
from luma.core.render import canvas
from luma.core.interface.serial import i2c
serial = i2c(port=1, address=0x3C)
device = sh1106(serial)
# https://pillow.readthedocs.io/en/latest/reference/ImageDraw.html#module-PIL.ImageDraw
with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline="white", fill="black")
    draw.text((30, 40), "Hello World", fill="white")
    
# https://python-escpos.readthedocs.io/en/latest/    
# from escpos.printer import Serial
# p = Serial(devfile='/dev/serial0',
#            baudrate=9600,
#            bytesize=8,
#            parity='N',
#            stopbits=1,
#            timeout=1.00,
#            dsrdtr=True)
# p.text("Hello World\n")
# p.image("cards/4/Nissa, Worldsoul Speaker.jpg")