#!/usr/bin/env python
import urllib.request, json
from datetime import datetime, timedelta  # Import datetime and timedelta

class SunTimes:
    def __init__(self):
        # API URL with lat/long and date information (returns data for today).
        self.url = "https://api.sunrise-sunset.org/json?lat=53.349804&lng=-6.260310&date=today&formatted=0"

    def fetchAPI(self):
        #Fetching the URL and storing data in a JSON object.
        with urllib.request.urlopen(self.url) as url:
            self.data = json.loads(url.read().decode())
        self.list = []
        self.formatTime("Sunrise", "sunrise")
        self.formatTime("Sunset", "sunset")
        self.formatTime("CMT", "civil_twilight_begin")
        self.formatTime("CET", "civil_twilight_end")
        return self.list

    def formatTime(self, title, time):
        time1 = self.data['results'][time]
        index = time1.find('T')
        time2 = time1[index+1:-6]
        #If the title is one of Sunrise, Sunset, CMT, or CET, add one hour to the time.
        if title in ["Sunrise", "Sunset", "CMT", "CET"]:
            t = datetime.strptime(time2, "%H:%M:%S")
            t += timedelta(hours=1)  #CHANGE THIS LINE TO 0 FOR BACK TO ZULU
            time2 = t.strftime("%H:%M:%S")
        self.list.append(title + ": " + time2)

def main():
    times = SunTimes()
    results = times.fetchAPI()
    print(results[0])  # Sunrise
    print(results[1])  # Sunset
    print(results[2])  # CMT
    print(results[3])  # CET

if __name__ == "__main__":
    main()
