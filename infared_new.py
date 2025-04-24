#!/usr/bin/env python
import requests
import datetime
from pathlib import Path

class Infrared:
    def __init__(self, time, output_dir=r"C:\Users\Nathaniel\Desktop\AUTOMET"):
        # Getting current date
        self.now = datetime.datetime.now()
        # Clean up specified time
        self.time = time.replace(":", "")
        # Format month/day with leading zero
        self.month = f"{self.now.month:02d}"
        self.day   = f"{self.now.day:02d}"
        # Build URL
        self.url = (
            f"https://www.met.ie/images/satellite/"
            f"web17_sat_irl_ir_{self.now.year}{self.month}{self.day}{self.time}.jpeg"
        )

        # Prepare output directory
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def fetchInfrared(self):
        try:
            r = requests.get(self.url, allow_redirects=True)
            if r.status_code == 404:
                print("Infrared Failure: Image does not (yet) exist.")
                return

            # Build full save-path
            filename = f"{self.time}_infrared.jpeg"
            save_path = self.output_dir / filename

            # Write image content to file
            save_path.write_bytes(r.content)
            print(f"Saved: {save_path}")

        except Exception as e:
            print("Infrared Failure:", str(e))


def main():
    # change back to GMT once clocks go back 
    # now specifying a subdirectory "sat_images"
    ir1 = Infrared("0600")
    ir1.fetchInfrared()

    ir2 = Infrared("0700")
    ir2.fetchInfrared()

if __name__ == "__main__":
    main()
