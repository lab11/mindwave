#!/usr/bin/env python
# -*- coding:utf-8 -*-

import platform
import sys, time
from pymindwave import headset
import httplib, urllib, urllib2
import json

#serial_port = '/dev/tty.MindWaveMobile-DevA-10'

usage = "\nUsage:\n\n   python <program.py> <config>"

def main():
    mindwave = MindWaveReader()
    try:
        while True:
            # wait 1 sec to collect data
            time.sleep(1)

            mindwave.update_readings()
            mindwave.print_readings()
    
            if mindwave.send_to_gatd:
                mindwave.report_to_gatd()

    except KeyboardInterrupt:
        mindwave.clean_exit()


class MindWaveReader():
    gatd_profile_id = "PkaJoO4gav"

    serial_port = None
    send_to_gatd = None
    show_spectrum = None
    user = None

    attention = None
    meditation = None
    delta = None
    theta = None
    low_alpha = None
    high_alpha = None
    low_beta = None
    high_beta = None
    low_gamma = None
    high_gamma = None

    hs = None #headset

    def __init__(self):
        self.get_config()
        self.print_greeting()

        headset_connected = False
        try:
            while not headset_connected:
                try:
                    self.hs = self.get_headset()
                    headset_connected = True
                except:
                    print("\n** Problem connecting to headset.")
                    print("    Is {} the right serial port?".format(self.serial_port))
                    print("    Are you sure the headset is on and paired with your computer?\n")
                    raw_input("Hit <enter> to try again (^C to exit).")
                    self.get_config()
        except KeyboardInterrupt:
            print("")
            sys.exit(0)

    def update_readings(self):
        self.attention = self.hs.get('attention')
        self.meditation = self.hs.get('meditation')
        self.delta, self.theta, self.low_alpha, self.high_alpha, self.low_beta, self.high_beta, self.low_gamma, self.high_gamma = self.hs.get('waves_vector')

    def print_greeting(self):
        print("\nStarting MindWave Mobile headset reader.\n")

    def get_config(self):
        config = None
        if len(sys.argv) == 2:
            config_file = sys.argv[1]
            json_data=open(config_file).read()
            config = json.loads(json_data)
        else:
            print(usage)
            sys.exit()

        self.serial_port = config["mindwave_serial_port"]
        self.user = config["user"]
        self.send_to_gatd = self.str_to_bool(config["send_to_gatd"])
        self.show_spectrum = self.str_to_bool(config["show_spectrum"])


    def str_to_bool(self, s):
        if s.lower() == "true":
            return True
        elif s.lower() == "false":
            return False
        else:
            print("Problem with config file: {} is not a boolean.".format(s))
            return None


    def get_user_prefs(self):
        if self.send_to_gatd == None:
            gatd_flag = self.get_valid_input("Send readings to GATD? [y/n]: ", ["y","n"])
            self.send_to_gatd = True if gatd_flag == "y" else False
        if self.user == None and self.send_to_gatd == True:
            name = raw_input("\nPlease provide your uniqname (or full name if you don't have a uniqname) for inclusion in reports to GATD: ")
            self.user = name.lower()
        if self.show_spectrum == None:
            print("\nAttention and meditation levels will be shown.")
            view_flag = self.get_valid_input("Do you want to see the frequency breakdown as well? (Full screen recommended.) [y/n]: ", ["y","n"])
            self.show_spectrum = True if view_flag == "y" else False

            
    def report_to_gatd(self):
        # make sure the device is past the configuration stage
        if not (self.attention == 0 and self.meditation == 0):
            # build JSON data structure
            labels = ["attention", "meditation", "delta", "theta", "low alpha", "high alpha", "low beta", "high beta", "low gamma", "high gamma"]
            readings = [self.attention, self.meditation, self.delta, self.theta, self.low_alpha, self.high_alpha, self.low_beta, self.high_beta, self.low_gamma, self.high_gamma]
            data = {}
            for i,label in enumerate(labels):
                data[label] = readings[i]
            data["user"] = self.user
            data = json.dumps(data)
            # make POST to GATD
            url = "http://gatd.eecs.umich.edu:8081/" + str(self.gatd_profile_id)
            req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
            f = urllib2.urlopen(req)
            response = f.read()
            f.close()

    def get_valid_input(self, prompt, options):
        sel = ""
        validated = False
        while(not validated):
            sel = (raw_input(prompt)).lower()
            if sel in options:
                validated = True
            else:
                print("Please enter one of the following options: {}".format(options))
        return sel

    def print_readings(self):
        format_str = ""
        if (self.show_spectrum):
            labels = ["attention", "meditation", "delta", "theta", "low alpha", "high alpha", "low beta", "high beta", "low gamma", "high gamma"]
            readings = [self.attention, self.meditation, self.delta, self.theta, self.low_alpha, self.high_alpha, self.low_beta, self.high_beta, self.low_gamma, self.high_gamma]
            cols = [labels[i] + ": " + str(readings[i]) for i in range(len(labels))]
            for i in range(len(labels)):
                format_str += ("{: <" + str(len(labels[i]) + 8) + "} ") if i < 2 else ("{: <" + str(len(labels[i]) + 11) + "} ")
        else:
            labels = ["attention", "meditation"]
            readings = [self.attention, self.meditation]
            cols = [labels[i] + ": " + str(readings[i]) for i in range(len(labels))]
            for i in range(len(labels)):
                format_str += "{: <" + str(len(labels[i]) + 6) + "} " 

        print((format_str).format(*cols))

    def get_headset(self):
        print("\nAttempting to connect to headset...")
        self.hs = headset.Headset(self.serial_port)

        # wait some time for parser to udpate state so we might be able
        # to reuse last opened connection.
        time.sleep(1)
        if self.hs.get_state() != 'connected':
            self.hs.disconnect()
        while self.hs.get_state() != 'connected':
            time.sleep(1)
            print 'current state: {0}'.format(self.hs.get_state())
            if (self.hs.get_state() == 'standby'):
                print 'trying to connect...'
                self.hs.connect()
        print 'Connected!\n'
        return self.hs

    def clean_exit(self):
        print("\nDisconnecting...")
        self.hs.disconnect()
        self.hs.destroy()
        print("Done.")
        sys.exit(0)

if __name__ == "__main__":
    main()
