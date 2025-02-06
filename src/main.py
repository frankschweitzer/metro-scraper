import requests # type: ignore
import os
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
        print(train)
        if train["Destination"] == destination:
            print("MATCH")
            print("_______________")
            print(train)
            print("_______________")
            eligible_trains.append(train)
    print("SEARCHED ALL ELIGIBLE TRAINS")
    return eligible_trains


def email_notification():
    pass


if __name__ == "__main__":
    departing_station = "Foggy Bottom"
    destination_station = "Largo"
    
    """ RETRIEVE & CLEAN DATA """
    raw_next_trains = fetch_next_trains(departing_station)
    parsed_next_trains = parse_train_data(raw_next_trains)
    
    """ RETREIVE TRAINS FOR DESIRED ROUTE """
    eligible_trains = find_eligible_trains(departing=departing_station, destination=destination_station, trains=parsed_next_trains)    