import json
import os
import subprocess
import urllib.request


def format_location(location):
    if location is None:
        return "Location: unavailable"

    latitude = float(location["latitude"])
    longitude = float(location["longitude"])
    return f"Lat: {latitude:.6f}, Long: {longitude:.6f}"


def get_manual_location():
    latitude = os.getenv("GPS_LATITUDE")
    longitude = os.getenv("GPS_LONGITUDE")
    if latitude is None or longitude is None:
        return None

    try:
        return {
            "latitude": float(latitude),
            "longitude": float(longitude),
            "source": "manual GPS environment variables",
        }
    except ValueError:
        return None


def parse_nmea_coordinate(raw_value, direction):
    if not raw_value or not direction:
        return None

    degree_digits = 2 if direction in {"N", "S"} else 3
    try:
        degrees = float(raw_value[:degree_digits])
        minutes = float(raw_value[degree_digits:])
    except ValueError:
        return None

    decimal = degrees + minutes / 60

    if direction in {"S", "W"}:
        decimal *= -1

    return decimal


def parse_nmea_location(sentence):
    parts = sentence.strip().split(",")
    if len(parts) < 6 or parts[0] not in {"$GPGGA", "$GNGGA", "$GPRMC", "$GNRMC"}:
        return None

    if parts[0] in {"$GPRMC", "$GNRMC"}:
        if len(parts) < 7 or parts[2] != "A":
            return None
        latitude = parse_nmea_coordinate(parts[3], parts[4])
        longitude = parse_nmea_coordinate(parts[5], parts[6])
    else:
        if len(parts) < 7 or parts[6] == "0":
            return None
        latitude = parse_nmea_coordinate(parts[2], parts[3])
        longitude = parse_nmea_coordinate(parts[4], parts[5])

    if latitude is None or longitude is None:
        return None

    return {
        "latitude": latitude,
        "longitude": longitude,
        "source": "phone GPS (NMEA)",
    }


def parse_lat_lon_text(text):
    cleaned = text.strip()
    if not cleaned:
        return None

    try:
        data = json.loads(cleaned)
        if data is None:
            return None
        if not isinstance(data, dict):
            return None
        latitude = data.get("latitude", data.get("lat"))
        longitude = data.get("longitude", data.get("lon", data.get("lng")))
    except json.JSONDecodeError:
        parts = cleaned.replace(";", ",").split(",")
        if len(parts) < 2:
            return None
        latitude = parts[0].strip()
        longitude = parts[1].strip()

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (TypeError, ValueError):
        return None

    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        return None

    return {
        "latitude": latitude,
        "longitude": longitude,
        "source": "phone GPS",
    }


def parse_phone_location(line):
    return parse_nmea_location(line) or parse_lat_lon_text(line)


def get_wifi_phone_location(timeout_seconds=3):
    url = os.getenv("PHONE_LOCATION_URL", "http://127.0.0.1:8765/location")

    try:
        with urllib.request.urlopen(url, timeout=timeout_seconds) as response:
            body = response.read().decode("utf-8")
    except Exception:
        return None

    location = parse_phone_location(body)
    if location:
        location["source"] = f"{location['source']} over Wi-Fi"

    return location


def get_windows_location(timeout_seconds=15):
    powershell_script = f"""
Add-Type -AssemblyName System.Device
$watcher = New-Object System.Device.Location.GeoCoordinateWatcher
$started = $watcher.TryStart($false, [TimeSpan]::FromSeconds({timeout_seconds}))
$coord = $watcher.Position.Location
if ($started -and -not $coord.IsUnknown) {{
    [PSCustomObject]@{{
        latitude = $coord.Latitude
        longitude = $coord.Longitude
        source = "Windows Location Services"
    }} | ConvertTo-Json -Compress
}}
"""
    try:
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-Command", powershell_script],
            capture_output=True,
            text=True,
            timeout=timeout_seconds + 5,
            check=False,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return None

    output = completed.stdout.strip()
    if not output:
        return None

    try:
        location = json.loads(output)
    except json.JSONDecodeError:
        return None

    if location.get("latitude") is None or location.get("longitude") is None:
        return None

    return parse_lat_lon_text(json.dumps(location))


def get_ip_location(timeout_seconds=5):
    try:
        with urllib.request.urlopen("https://ipapi.co/json/", timeout=timeout_seconds) as response:
            location = json.loads(response.read().decode("utf-8"))
    except Exception:
        return None

    latitude = location.get("latitude")
    longitude = location.get("longitude")
    if latitude is None or longitude is None:
        return None

    return {
        "latitude": latitude,
        "longitude": longitude,
        "source": "IP location (approximate)",
    }


def get_current_location():
    location_getters = [
        get_manual_location,
        get_wifi_phone_location,
        get_windows_location,
    ]

    if os.getenv("ALLOW_APPROX_IP_LOCATION", "0") == "1":
        location_getters.append(get_ip_location)

    for location_getter in location_getters:
        location = location_getter()
        if location is not None:
            return location

    return None


if __name__ == "__main__":
    location = get_current_location()
    print(location)
    print(format_location(location))
