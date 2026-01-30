import os
import json
import requests

API_KEY = os.environ["STEAM_API_KEY"]
GROUP_INPUT = os.environ["STEAM_GROUP"]

def resolve_group_id(group):
    if group.isdigit():
        return group

    r = requests.get(
        "https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/",
        params={
            "key": API_KEY,
            "vanityurl": group,
            "url_type": 2,
        },
        timeout=15
    )

    r.raise_for_status()

    data = r.json()["response"]

    if data.get("success") != 1:
        raise RuntimeError("Failed to resolve Steam Group ID")

    return data["steamid"]

def fetch_members(group_id):
    members = []
    page = 1

    while True:
        r = requests.get(
            "https://api.steampowered.com/ISteamUser/GetGroupMembersList/v1/",
            params={
                "key": API_KEY,
                "steamid": group_id,
                "page": page,
            },
            timeout=15
        )

        if r.status_code == 404:
            print("Steam Group not found or you don't have access to it!")
            return []

        r.raise_for_status()

        data = r.json().get("response", {})
        members.extend(data.get("members", []))

        if "next_page" not in data:
            break

        page = data["next_page"]

    return members

def main():
    group_id = resolve_group_id(GROUP_INPUT)
    members = fetch_members(group_id)
    member_count = len(members)

    with open("members.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "group_id": group_id,
                "count": member_count,
                "members": members,
            },
            f,
            indent=2
        )

    print(f"Got {member_count} members.")

if __name__ == "__main__":
    main()
