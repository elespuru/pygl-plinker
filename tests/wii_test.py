from pywiiuse import *
from time     import sleep

wiimotes = wiiuse_init()
found    = wiiuse_find(wiimotes,1,5)
wiimote  = wiimotes.contents

wiiuse_set_leds(wiimote,WIIMOTE_LED_1)

wiiuse_rumble(wiimote,1)
sleep(1)
wiiuse_rumble(wiimote,0)

wiiuse_motion_sensing(wiimote,1)

while 1:
    if(wiiuse_poll(wiimote,1)):
        print 'EVENT'

