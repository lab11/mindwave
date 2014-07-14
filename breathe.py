import hue_manager
import time

MAX_BRIGHT= 120
toggle = False

def main():
    print("Starting mental_hue")
    [hub_addr, light_choices] = hue_manager.get_configuration()

    bridge = hue_manager.hue_connect(hub_addr)
    all_lights = bridge.get_light_objects()
    my_lights = [l for l in all_lights if l.name in light_choices]
    for light in my_lights:
        light.transitiontime = 40
        light.on = True
        light.xy = [0.1684, 0.0416]

    while True:

	    # in light.xy, x from 0 to 1 (y = 0) goes from blue to red.
	    for light in my_lights:
	    	print("{}: {}".format(light.name, light.xy))
	    	light.brightness = brightness()
	    toggle_brightness()
	    time.sleep(4)

def brightness():
	brightness = MAX_BRIGHT if toggle == True else 0
	return brightness

def toggle_brightness():
	global toggle
	toggle = not toggle

if __name__=="__main__":
	main()

