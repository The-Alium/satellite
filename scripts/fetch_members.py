import os
import json
import requests
import xmltodict

GROUP = os.environ["STEAM_GROUP"]
BASE_URL = f"https://steamcommunity.com/groups/{GROUP}/memberslistxml/?xml=1"

def main():
    print( "Getting data from Steam..." )
    r = requests.get( BASE_URL, timeout = 10 )

    if r.status_code == 404:
        raise RuntimeError( "Group is unavailable or does not exist." )

    r.raise_for_status()

    with open( "members.json", "w", encoding = "utf-8" ) as f:
        json.dump(
            xmltodict.parse( r.content ),
            f,
            indent = 2
        )

    print( "Done." )

if __name__ == "__main__":
    main()
