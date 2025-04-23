import requests
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

API_KEY = "AIzaSyBdx5AwOWGLLBD-2mHcRZGG6s2USp3yA8M"  # Replace with your YouTube Data API key
CHANNEL_ID = "UC40Tw2tFuMzK305mi7nj8rg"  # Replace with the correct channel ID

def get_latest_weather_video_url():
    try:
        url = f"https://www.googleapis.com/youtube/v3/search?key={API_KEY}&channelId={CHANNEL_ID}&part=snippet,id&order=date&maxResults=1&regionCode=GB"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print("API Response:", data)  # Debugging: Print the full API response
        if "items" in data and len(data["items"]) > 0:
            video_id = data["items"][0]["id"]["videoId"]
            return f"https://www.youtube.com/watch?v={video_id}"
        else:
            print("No videos found for the channel. API Response:", data)
            return None
    except Exception as e:
        print("Error while retrieving the latest video URL:", e)
        return None

def send_email(subject, body, smtp_server, smtp_port, smtp_user, smtp_password, to_email):
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg.attach(MIMEText(body, "html"))
    
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        print("Email sent successfully.")

def main():
    video_url = get_latest_weather_video_url()
    if not video_url:
        print("Failed to retrieve the latest video URL.")
        return
    
    print("Latest video URL:", video_url)
    
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    email_body = f"""
    <html>
    <body>
        <h1>Morning Weather Brief - {today_str}</h1>
        <h2>Weather Brief Video</h2>
        <p>
            {"<a href='" + video_url + "'>Watch the latest weather brief video</a>"}
        </p>
    </body>
    </html>
    """
    # Updated SMTP settings with provided email details.
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "gavindoyle330@gmail.com"     # Provided email address
    smtp_password = "jadk akfb cagy eyrj"     # Provided email password
    to_email = "gavindoyle330@gmail.com"      # Recipient email address
    
    send_email(f"Morning Weather Brief - {today_str}", email_body,
               smtp_server, smtp_port, smtp_user, smtp_password, to_email)

if __name__ == "__main__":
    main()
