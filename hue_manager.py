import sys, sched, time, threading
from threading import Timer
from phue import Bridge
import json

#Globals
window = 2 #num in avg
times = [] #times to be averages
timeout_val = 0.2 #seconds before timeout
max_brightness = 200 #max value of lamp given by phue
last_time = 0 

bridge = None
lights = None
light = None

usage = "\nUsage:\n\n   python <program.py> <config>"

def get_configuration():
  global bridge, lights, light
  config = get_json_config()
  # Connect to hue
  hub_addr = get_hub_addr() if "hue_bridge_addr" not in config else config["hue_bridge_addr"]
  bridge = hue_connect(hub_addr)
  all_lights = bridge.get_light_objects()
  lights = [] 
  #lights should be a list of reachable lights only
  for (i, l) in enumerate(all_lights):
    if (bridge.get_light(l.name))['state']['reachable'] == True:
      lights.append(l)
  light_choices = get_bulb_choices()

  return [hub_addr, light_choices] 

def get_json_config():
    data = None
    if len(sys.argv) == 2:
        config_file = sys.argv[1]
        json_data = open(config_file).read()
        data = json.loads(json_data)
    else:
        print(usage)
        sys.exit()
    return data

def hue_connect(addr):
  bridge = None
  not_connected = True
  while(not_connected):
    try:
      bridge = Bridge(addr)
      bridge.connect()
      not_connected = False
    except:
      print("\nGo push the button on the hub to authorize this program. I'll wait.\n")
      raw_input("Hit enter when you're done. ")
  return bridge

def get_hub_addr():
  address = "4908hue.eecs.umich.edu"
  sel = ""
  validated = False
  while(not validated):
    sel = (raw_input("Connecting to hub at address {}. Is this okay? [y/n]: ".format(address))).lower()
    if sel == 'y' or sel == 'n':
      validated = True
    else:
      print("Please enter y or n.")
  if sel == 'n':
    address = raw_input("Enter the new hub address (ip or domain name): ")
  return address


def get_bulb_choices():
  print("\nReachable bulbs:\n")
  print("\n".join(["   [{}] {}".format(i+1, str(light.name)) for (i, light) in enumerate(lights)]))
  input_verified = False
  selection = ""
  while(not input_verified):
    selections = (raw_input("\n   Select bulb number(s). (Comma separate multiple numbers): ")).replace(" ","").split(",")
    selected_lights = []
    for selection in selections:
      try:
        selection_index = int(selection)-1
        if selection_index < 0 or selection_index >= len(lights):
          raise Exception
        input_verified = True
        selected_lights.append(lights[selection_index].name)
      except:
        print("   '{}' is not a valid selection. Try again.".format(selection))
        input_verified = False
        break
  return selected_lights


def set_brightness(brightness):
  light.brightness = brightness

def get_weighted_brightness():
  avg_speed = sum(times)/len(times)
  avg_speed_map = int(((avg_speed / timeout_val) * max_brightness)) 
  brightness = max_brightness - avg_speed_map
  if (brightness < 0): 
    brightness = 0 
  return brightness

def append_time():
  global last_time
  cur_time = time.time()
  delta_time = cur_time-last_time  
  times.append(delta_time)
  if (len(times) == window):
    times.pop(0)
  last_time = cur_time

def timeout():
  if (time.time() - last_time > timeout_val):
    light.brightness = 0
   
def process_event():
  append_time()
  set_brightness(get_weighted_brightness()) 

def main():
  global bridge, light
  addr = sys.argv[1]
  light_name = sys.argv[2]
  bridge = hue.hue_connect(addr)
  all_lights = bridge.get_light_objects()
  light = [l for l in all_lights if l.name == light_name][0]

  print("\n   Good to go! Start typing.\n")

  while (1):
    if (len(raw_input()) != 0):
      t = threading.Thread(target=process_event) 
      t.daemon = True
      t.start()    
      t.join()
    Timer(int(timeout_val), timeout, ()).start()

if __name__=="__main__":
  main()
