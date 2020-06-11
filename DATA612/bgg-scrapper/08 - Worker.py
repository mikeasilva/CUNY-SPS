import requests
import json
from glob import glob

currently_assigned = None
mothership = "http://127.0.0.1:5000/"
done = False


def get_assignment():
    response = requests.get(mothership + "next_assignment")
    row = json.loads(response.text)
    return row


def get_user_id_by_username(username):
    response = requests.get(mothership + "user_id?username=" + username)
    row = json.loads(response.text)
    return row["id"]


def extract_ratings(json_file, item_id):
    data_for_mothership = list()
    failures = 0
    with open(json_file, encoding="utf8") as f:
        data = json.load(f)
        for i in data["items"]:
            try:
                username = i["user"]["username"]
                rating = i["rating"]
                rating_tstamp = i["rating_tstamp"]
                user_id = get_user_id_by_username(username)
                data_for_mothership.append((item_id, user_id, rating, rating_tstamp))
            except:
                failures += 1
                if failures > 10:
                    print("Mothership down!")
                    quit()
                else:
                    continue
    return data_for_mothership


def send_data_to_mothership(data):
    json_data = json.dumps(data) 
    requests.post(mothership + "data_intake", data=json_data, headers={"Content-Type":"application/json"})


def send_assignment_complete_to_mothership(i):
    requests.get(mothership + "assignment_complete?id=" + str(i))


while not done:
    assignment = get_assignment()
    if assignment["id"] == "Done":
        print("Done")
        done = True
    else:
        # Loop over the ratings and gather data for the mothership
        data_for_mothership = list()
        print("Assignment: " + str(assignment["bgg_id"]))
        for json_file in glob("./ratings/" + str(assignment["bgg_id"]) + "_*.json"):
            #print("  " + json_file)
            data_for_mothership.append(extract_ratings(json_file, assignment["id"]))
            # We don't want to loose all the hard work
            if len(data_for_mothership) >= 200:
                send_data_to_mothership(data_for_mothership)
                data_for_mothership = list()      
        # Send the data to the mothership
        send_data_to_mothership(data_for_mothership)
        # Get the next assignment
        send_assignment_complete_to_mothership(assignment["id"])
