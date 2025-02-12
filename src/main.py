import requests # type: ignore
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv # type: ignore

""" CONSTANTS """
load_dotenv()
LOCATION_CODES = {
    "Foggy Bottom" : "C04",
    "McLean" : "N01",
    "Mt Vernon Square" : "E01",
    "U Street" : "E03"
}
METRO_API_BASE_URL = "https://api.wmata.com/StationPrediction.svc/json/GetPrediction/"
API_KEY = os.getenv("API_KEY")


def fetch_next_trains(departing_station):
    url = f"{METRO_API_BASE_URL}{LOCATION_CODES[departing_station]}"
    params = {
        "api_key" : API_KEY
    }
    
    try:
        response = requests.get(url=url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching next trains: {e}")
        return None
    

def parse_train_data(jsonBody):
    next_trains = []
    for train in jsonBody['Trains']:
        t = {
            "Departing" : train["LocationName"],
            "Destination" : train["Destination"],
            "ETD" : train["Min"]
        }
        next_trains.append(t)
    return next_trains


def find_eligible_trains(departing, destination, trains):
    eligible_trains = []
    print("SEARCHING FOR ELIGIBLE TRAINS")
    for train in trains:
        if train["Destination"] == destination:
            eligible_trains.append(train)
    print("SEARCHED ALL ELIGIBLE TRAINS")
    return eligible_trains


def email_notification(email, trains):
    sender_email = "metro.status.notification@gmail.com"
    sender_password = os.getenv("EMAIL_PASSWORD")
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "Next Trains Information"
    
    body = "Here are the next trains:\n\n"
    for train in trains:
        body += f"Departing: {train['Departing']}, Destination: {train['Destination']}, ETD: {train['ETD']} minutes\n"
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, email, text)
        server.quit()
        print(f"Email sent to {email}")
    except Exception as e:
        print(f"Failed to send email: {e}")


def lambda_handler():
    users = {
        'Frank' : {
            'email' : os.getenv("F_EMAIL"),
            'departing_station' : 'Foggy Bottom',
            'destination_station' : 'Largo'
        },
        'Georgia' : {
            'email' : os.getenv("G_EMAIL"),
            'departing_station' : 'U Street',
            'destination_station' : 'Branch Av'
        }
    }
    
    for person, info in users.items():
        """ RETRIEVE & CLEAN DATA """
        raw_next_trains = fetch_next_trains(info['departing_station'])
        parsed_next_trains = parse_train_data(raw_next_trains)
        
        """ RETREIVE TRAINS FOR DESIRED ROUTE """
        eligible_trains = find_eligible_trains(departing=info['departing_station'], destination=info['destination_station'], trains=parsed_next_trains)
        
        """ EMAIL USER THE NEXT TRAINS """
        email_notification(email=info['email'], trains=eligible_trains)