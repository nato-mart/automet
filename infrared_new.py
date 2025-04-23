#!/usr/bin/env python
import requests
import datetime
#from pathlib import Path
#import os

class Infrared:
    def __init__(self, time):

        #Getting current date
        self.now = datetime.datetime.now()
        #Cleaning up specified time
        self.time = time.replace(":","")

        self.month = "".join(('0' if len(str(self.now.month))<2 else '')+str(self.now.month))

        self.day = "".join(('0' if len(str(self.now.day))<2 else '')+str(self.now.day))


        #Creating URL
        self.url = r'https://www.met.ie/images/satellite/web17_sat_irl_ir_'+ str(self.now.year) + self.month + self.day + self.time+'.jpeg'
    def fetchInfrared(self):
        #print("test")
        try:
            #Fetch and store image (if found) in 'r'
            r = requests.get(self.url, allow_redirects=True)
            #If not found (404)..
            if r.status_code == 404:
                print("Infrared Failure: Image does not (yet) exist. Image may not yet be released, or the naming convention by Met.ie has changed!")
            #if found..
            else:
                #Write image content to file
                try:
                    open(self.time + '_infared.jpeg', 'wb').write(r.content)
                except Exception as e:
                    print("Infrared Failure: Failed to save image to disk. "+str(e))

        except Exception as e:
            print("Infrared Failure: Could not retrieve URL. Met.ie could be down. "+str(e))


def main():
    #change back to GMT once clocks go back 
    ir = Infrared("0600")
    ir.fetchInfrared()
    
    ir = Infrared("0700")
    ir.fetchInfrared()

if __name__ == "__main__": main()
