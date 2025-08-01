import os
import requests
import argparse
from datetime import datetime, timedelta

def view(
    url,
    token,
    id=None,
    device_name=None,
    user_name=None,
    group_name=None,
    offline_days=None,
):
    headers = {"Authorization": f"Bearer {token}"}
    pageSize = 200  # Adjusted for large-scale device management; set according to device count
    params = {
        "id": id,
        "device_name": device_name,
        "user_name": user_name,
        "group_name": group_name,
    }

    params = {
        k: "%" + v + "%" if (v != "-" and "%" not in v) else v
        for k, v in params.items()
        if v is not None
    }
    params["pageSize"] = pageSize

    devices = []

    current = 1

    while True:
        params["current"] = current
        response = requests.get(f"{url}/api/devices", headers=headers, params=params)
        response_json = response.json()

        data = response_json.get("data", [])

        for device in data:
            if offline_days is None:
                devices.append(device)
                continue
            last_online = datetime.strptime(
                device["last_online"].split(".")[0], "%Y-%m-%dT%H:%M:%S"
            )
            days_offline = (datetime.utcnow() - last_online).days
            if days_offline >= offline_days:
                devices.append({
                    "name": device.get("device_name") or device.get("info", {}).get("device_name", "Unknown"),
                    "guid": device["guid"],
                    "id": device["id"],
                    "days_offline": days_offline
                })

        total = response_json.get("total", 0)
        current += pageSize
        if len(data) < pageSize or current > total:
            break

    return devices

def check(response):
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            return response.text or "Success"
    else:
        return f"Failed: {response.status_code} {response.text}"

def disable_device(url, token, guid):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{url}/api/devices/{guid}/disable", headers=headers)
    return check(response)

def delete_device(url, token, guid):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{url}/api/devices/{guid}", headers=headers)
    return check(response)

def main():
    parser = argparse.ArgumentParser(description="Device manager")
    parser.add_argument(
        "command",
        choices=["view", "delete"],
        help="Command to execute",
    )
    parser.add_argument("--url", default="http://127.0.0.1:21114", help="URL of the API")
    parser.add_argument("--id", help="Device ID")
    parser.add_argument("--device_name", help="Device name")
    parser.add_argument("--user_name", help="User name")
    parser.add_argument("--group_name", help="Group name")
    parser.add_argument(
        "--offline_days", type=int, help="Offline duration in days, e.g., 7"
    )

    args = parser.parse_args()

    # Retrieve token from environment variable
    token = os.getenv("RUSTDESK_TOKEN")
    if not token:
        print("Error: Environment variable RUSTDESK_TOKEN is not set.")
        return

    while args.url.endswith("/"): args.url = args.url[:-1]

    devices = view(
        args.url,
        token,
        args.id,
        args.device_name,
        args.user_name,
        args.group_name,
        args.offline_days,
    )

    if args.command == "view":
        print("Devices that would be deleted:")
        for device in devices:
            print(f"{device['name']} {device['guid']} {device['days_offline']} days offline")

        print(f"\nTotal devices determined to be OK to delete: {len(devices)}")

    elif args.command == "delete":
        print("Devices that would be deleted:")
        for device in devices:
            print(f"{device['name']} {device['guid']} {device['days_offline']} days offline")

        print(f"\nTotal devices determined to be OK to delete: {len(devices)}")

        confirm = input("Do you want to delete these devices? (yes/no): ").strip().lower()
        if confirm == "yes":
            for device in devices:
                print(f"Disabling device: {device['name']} ({device['guid']})")
                response = disable_device(args.url, token, device['guid'])
                print(response)
                print(f"Deleting device: {device['name']} ({device['guid']})")
                response = delete_device(args.url, token, device['guid'])
                print(response)

if __name__ == "__main__":
    main()
