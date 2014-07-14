#!/usr/bin/env python
# -*- coding:utf-8 -*-

import mindwave_reader as mw
import hue_manager
import time

#serial_port = '/dev/tty.MindWaveMobile-DevA-9'

MAX_BRIGHT= 200

def main():
    print("Starting mental_hue")
    [hub_addr, light_choices] = hue_manager.get_configuration()

    bridge = hue_manager.hue_connect(hub_addr)
    all_lights = bridge.get_light_objects()
    my_lights = [l for l in all_lights if l.name in light_choices]
    for light in my_lights:
        light.transitiontime = 10
        light.on = True

    # Mindwave stuff
    mindwave = mw.MindWaveReader()
    try:
        while True:
            # wait 1 sec to collect data
            time.sleep(1)

            mindwave.update_readings()
            mindwave.print_readings()

            # Hue stuff
            # in light.xy, x from 0 to 1 (y = 0) goes from blue to red.
            for light in my_lights:
                light.xy = new_xy(mindwave.meditation, mindwave.attention)
                light.brightness = new_brightness(mindwave.meditation, mindwave.attention)
    
            if mindwave.connect_to_GATD:
                mindwave.report_to_gatd()

    except KeyboardInterrupt:
        light.on = False
        mindwave.clean_exit()

def new_xy(meditation, attention):
    scale = (attention-meditation)/100.0
    red_blue_balance = 0.5 + (0.5 * scale)
    return [red_blue_balance, 0]

def new_brightness(meditation, attention):
    percent_bright = (meditation + attention)/200.0
    brightness = int(MAX_BRIGHT * percent_bright)
    return brightness

if __name__ == "__main__":
    main()
