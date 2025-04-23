import requests
from bs4 import BeautifulSoup
import smtplib

# Email configuration
EMAIL_ADDRESS = "gavindoyle330@gmail.com"  # Replace with your email address
EMAIL_PASSWORD = "jadk akfb cagy eyrj"    # Replace with your email password
RECIPIENT_EMAIL = "gavindoyle330@gmail.com"

# Fetch METAR information
def fetch_metar():
    url = "https://metar-taf.com/EIME"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an error for bad status codes
    soup = BeautifulSoup(response.text, 'html.parser')
    metar_element = soup.find('code', class_='text-white d-block')
    if metar_element:
        return metar_element.text.strip()
    else:
        raise ValueError("METAR information not found on the page.")

# Send email
def send_email(subject, body):
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, message)

# Main function
if __name__ == "__main__":
    try:
        metar_info = fetch_metar()
        send_email("METAR Information", metar_info)
        print("Email sent successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
