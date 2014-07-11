#!/usr/bin/env python
# -*- coding:utf-8 -*-

import platform
import sys, time
from pymindwave import headset
import httplib, urllib, urllib2
import json

serial_port = '/dev/tty.MindWaveMobile-DevA-10'

def main():
    mindwave = MindWaveReader(serial_port)
    try:
        while True:
            # wait 1 sec to collect data
            time.sleep(1)

            mindwave.update_readings()
            mindwave.print_readings()
    
            if mindwave.connect_to_GATD:
                mindwave.report_to_gatd()

    except KeyboardInterrupt:
        mindwave.clean_exit()

class MindWaveReader():
    gatd_profile_id = "PkaJoO4gav"

    connect_to_GATD = None
    show_frequency_breakdown = None

    username = None

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

    hs = None

    def __init__(self, serial_port):
        self.print_greeting()
        self.get_user_prefs()

        headset_connected = False
        try:
            while not headset_connected:
                try:
                    self.hs = self.get_headset()
                    headset_connected = True
                except:
                    print("\n** Problem connecting to headset.")
                    print("    Is {} the right serial port?".format(serial_port))
                    print("    Are you sure the headset is on and paired with your computer?\n")
                    raw_input("Hit <enter> to try again (^C to exit).")
        except KeyboardInterrupt:
            print("")
            sys.exit(0)

    def update_readings(self):
        self.attention = self.hs.get('attention')
        self.meditation = self.hs.get('meditation')
        self.delta, self.theta, self.low_alpha, self.high_alpha, self.low_beta, self.high_beta, self.low_gamma, self.high_gamma = self.hs.get('waves_vector')

    def print_greeting(self):
        print("\nStarting MindWave Mobile headset reader.\n")

    def get_user_prefs(self):
        username = None
        if len(sys.argv) > 1:
            for arg in sys.argv:
                if arg == "gatd=False":
                    self.connect_to_GATD = False
                elif arg == "gatd=True":
                    self.connect_to_GATD = True
                elif arg == "showspectrum=False":
                    self.show_frequency_breakdown = False
                elif arg == "showspectrum=True":
                    self.show_frequency_breakdown = True
                elif arg[0:9] == "uniqname=":
                    username = arg.split("=")[1].lower()
        if self.connect_to_GATD == None:
            gatd_flag = self.get_valid_input("Send readings to GATD? [y/n]: ", ["y","n"])
            self.connect_to_GATD = True if gatd_flag == "y" else False
        self.username = username if username != None else None
        if self.username == None and self.connect_to_GATD == True:
            name = raw_input("\nPlease provide your uniqname (or full name if you don't have a uniqname) for inclusion in reports to GATD: ")
            self.username = name.lower()
        if self.show_frequency_breakdown == None:
            print("\nAttention and meditation levels will be shown.")
            view_flag = self.get_valid_input("Do you want to see the frequency breakdown as well? (Full screen recommended.) [y/n]: ", ["y","n"])
            self.show_frequency_breakdown = True if view_flag == "y" else False

            
    def report_to_gatd(self):
        # make sure the device is past the configuration stage
        if not (self.attention == 0 and self.meditation == 0):
            # build JSON data structure
            labels = ["attention", "meditation", "delta", "theta", "low alpha", "high alpha", "low beta", "high beta", "low gamma", "high gamma"]
            readings = [self.attention, self.meditation, self.delta, self.theta, self.low_alpha, self.high_alpha, self.low_beta, self.high_beta, self.low_gamma, self.high_gamma]
            data = {}
            for i,label in enumerate(labels):
                data[label] = readings[i]
            data["user"] = self.username
            data = json.dumps(data)
            # make POST to GATD
            url = "http://inductor.eecs.umich.edu:8081/" + str(self.gatd_profile_id)
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
        if (self.show_frequency_breakdown):
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
        self.hs = headset.Headset(serial_port)

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
