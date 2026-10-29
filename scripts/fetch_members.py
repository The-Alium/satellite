import json
import os
from pathlib import Path

import requests
import xmltodict

GROUP = os.environ["STEAM_GROUP"]
BASE_URL = f"https://steamcommunity.com/groups/{GROUP}/memberslistxml/?xml=1"
PORTRAITS_DIR = Path("./resources/portraits")


def fetch_page(page: int) -> dict:
    r = requests.get(BASE_URL, params={"p": page}, timeout=10)

    if r.status_code == 404:
        raise RuntimeError("Group is unavailable or does not exist.")

    r.raise_for_status()

    data = xmltodict.parse(r.content)

    if "memberList" not in data:
        raise RuntimeError(f"Unexpected response from Steam: {r.text[:200]}")

    return data


def page_members(data: dict) -> list[str]:
    ids = (data["memberList"].get("members") or {}).get("steamID64", [])

    # xmltodict returns a plain string when there is only one member
    return [ids] if isinstance(ids, str) else ids


def main():
    print("Getting data from Steam...")
    data = fetch_page(1)
    member_list = data["memberList"]
    members = page_members(data)

    # Steam returns at most 1000 members per page
    total_pages = int(member_list.get("totalPages", 1))

    for page in range(2, total_pages + 1):
        members.extend(page_members(fetch_page(page)))

    # Steam shuffles the order between requests, sort to keep diffs meaningful
    member_list["members"] = {"steamID64": sorted(set(members), key=int)}

    with open("members.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    files = sorted(
        path.relative_to(PORTRAITS_DIR).as_posix()
        for path in PORTRAITS_DIR.rglob("*")
        if path.is_file()
    )

    with open("portraits.json", "w", encoding="utf-8") as f:
        json.dump(files, f, indent=4, ensure_ascii=False)

    print(f"Done. {len(members)} members, {len(files)} portraits.")


if __name__ == "__main__":
    main()
