import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import logging
from colorama import Fore, Style

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# URL of the surface pressure charts page
BASE_URL = "https://weather.metoffice.gov.uk/maps-and-charts/surface-pressure"

# Directory to save images
SAVE_DIR = "surface_pressure_charts"
os.makedirs(SAVE_DIR, exist_ok=True)

# Headers to simulate a real browser visit
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_issue_datetime():
    """Fetch and print the issued date and time of the surface pressure charts."""
    response = requests.get(BASE_URL, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Failed to fetch page: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    time_tag = soup.find("time")  # Locate the <time> tag

    if time_tag and time_tag.has_attr("datetime"):
        issued_datetime_str = time_tag["datetime"]
        issued_datetime = datetime.strptime(issued_datetime_str, "%Y-%m-%dT%H:%M:%SZ")
        print(f"{Fore.CYAN}Charts issued at: {issued_datetime.strftime('%H:%M UTC on %d %b %Y')}{Style.RESET_ALL}")  
    else:
        print("Could not find issue date/time on the page.")


def print_issue_datetime():
    """Fetch the issued date and time from the Met Office webpage and print it."""
    response = requests.get(BASE_URL, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch page: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    time_tag = soup.find("time")

    if time_tag and time_tag.has_attr("datetime"):
        issued_datetime_str = time_tag["datetime"]
        issued_datetime = datetime.strptime(issued_datetime_str, "%Y-%m-%dT%H:%M:%SZ")
        print(f"Charts issued at: {issued_datetime.strftime('%H:%M UTC on %d %b %Y')}")
    else:
        print("Could not find issue date/time on the page.")

def fetch_surface_pressure_charts(url=BASE_URL):
    """Scrape and download all available surface pressure chart images from the Met Office website."""
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        logging.error(f"Failed to fetch page: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    print_issue_datetime()  # Print the issued date and time

    # Iterate over expected chart IDs (chartColour1 to chartColour7)
    for i in range(0, 8):  
        li_id = f"chartColour{i}"
        li_tag = soup.find("li", id=li_id)
        if li_tag:
            img = li_tag.find("img")
            if img:
                img_src = img.get("src") or img.get("data-src")  # Handle lazy-loaded images
                if img_src:
                    img_url = urljoin(url, img_src)
                    logging.info(f"Found chart {li_id}: {img_url}")
                    download_chart(img_url, i)
                else:
                    logging.warning(f"No image source found in {li_id}")
            else:
                logging.warning(f"No <img> tag found in {li_id}")
        else:
            logging.warning(f"No <li> tag found for {li_id}")

def download_chart(img_url, index):
    """Download and save the surface pressure chart image with a unique name."""
    try:
        img_response = requests.get(img_url, headers=HEADERS)
        img_response.raise_for_status()

        # Use a structured naming convention with current timestamp
        filename = f"SPC_chart_{index}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gif"
        filepath = os.path.join(SAVE_DIR, filename)

        with open(filepath, 'wb') as f:
            f.write(img_response.content)
        
        logging.info(f"Downloaded: {filename}")

    except requests.RequestException as e:
        logging.error(f"Failed to download {img_url}: {e}")

if __name__ == '__main__':
    fetch_surface_pressure_charts()
    logging.info(f"Images saved in: {os.path.abspath(SAVE_DIR)}")

if __name__ == '__main__':
    get_issue_datetime()

