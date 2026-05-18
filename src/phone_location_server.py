import json
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from src.location_provider import format_location, parse_phone_location


latest_location = None

PHONE_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Location Sender</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; line-height: 1.4; }
    button { font-size: 18px; padding: 12px 16px; }
    .box { margin-top: 16px; padding: 12px; border: 1px solid #ccc; border-radius: 8px; }
    .ok { color: #0a7a28; }
    .bad { color: #b00020; }
  </style>
</head>
<body>
  <h2>Location Sender</h2>
  <button onclick="startGps()">Allow Location</button>
  <div class="box">
    <div id="status">Waiting...</div>
    <div id="coords"></div>
  </div>
  <div class="box">
    <strong>Use this on the laptop browser:</strong>
    <p>Open <code>http://127.0.0.1:8765/location-page</code> on the laptop and allow location permission.</p>
    <p>Phone browsers block GPS on plain HTTP Wi-Fi pages. Laptop localhost is allowed.</p>
    <code id="loggerUrl"></code>
  </div>
  <script>
    const statusEl = document.getElementById("status");
    const coordsEl = document.getElementById("coords");
    const loggerUrlEl = document.getElementById("loggerUrl");
    loggerUrlEl.textContent = `${location.origin}/update?lat=%LAT&lon=%LON`;

    function setStatus(text, ok) {
      statusEl.textContent = text;
      statusEl.className = ok ? "ok" : "bad";
    }

    async function sendPosition(position) {
      const lat = position.coords.latitude;
      const lon = position.coords.longitude;
      const accuracy = position.coords.accuracy;
      coordsEl.textContent = `Lat: ${lat.toFixed(7)}, Long: ${lon.toFixed(7)}, accuracy: ${accuracy.toFixed(1)} m`;

      const response = await fetch(`/update?lat=${lat}&lon=${lon}`);
      if (response.ok) {
        setStatus("Sending location to detector", true);
      } else {
        setStatus("Could not send location to laptop", false);
      }
    }

    function startGps() {
      if (!navigator.geolocation) {
        setStatus("This browser does not support location.", false);
        return;
      }

      setStatus("Requesting phone GPS permission...", true);
      navigator.geolocation.watchPosition(
        sendPosition,
        (error) => {
          if (error.message.includes("secure origins")) {
            setStatus("Browser GPS blocked. Open this page on laptop localhost: http://127.0.0.1:8765/location-page", false);
          } else {
            setStatus(`Location error: ${error.message}`, false);
          }
        },
        { enableHighAccuracy: true, maximumAge: 1000, timeout: 10000 }
      );
    }
  </script>
</body>
</html>
"""


class PhoneLocationHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global latest_location

        parsed = urlparse(self.path)
        if parsed.path in {"/", "/phone", "/location-page"}:
            self.send_html(PHONE_PAGE)
            return

        if parsed.path == "/update":
            query = parse_qs(parsed.query)
            latitude = query.get("lat", query.get("latitude", [None]))[0]
            longitude = query.get("lon", query.get("lng", query.get("longitude", [None])))[0]
            print(f"[INFO] Update request from {self.client_address[0]}: lat={latitude}, lon={longitude}")
            latest_location = parse_phone_location(f"{latitude},{longitude}")
            if latest_location:
                latest_location["source"] = "phone GPS over Wi-Fi"
                print(f"[INFO] Saved location: {format_location(latest_location)}")
                self.send_json({"ok": True, "location": latest_location})
            else:
                print("[WARN] Invalid location update. Check the phone app latitude/longitude placeholders.")
                self.send_json({"ok": False, "error": "Invalid lat/lon"}, status=400)
            return

        if parsed.path == "/location":
            self.send_json(latest_location)
            return

        if parsed.path == "/status":
            self.send_json(
                {
                    "ok": True,
                    "latest": latest_location,
                    "latest_text": format_location(latest_location),
                    "update_example": "/update?lat=<latitude>&lon=<longitude>",
                }
            )
            return

        self.send_json(
            {
                "ok": True,
                "usage": "/update?lat=<latitude>&lon=<longitude>",
                "latest": latest_location,
            }
        )

    def do_POST(self):
        global latest_location

        if self.path != "/update":
            self.send_json({"ok": False, "error": "Use POST /update"}, status=404)
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length).decode("utf-8")
        print(f"[INFO] POST update from {self.client_address[0]}: {body}")
        latest_location = parse_phone_location(body)
        if latest_location:
            latest_location["source"] = "phone GPS over Wi-Fi"
            print(f"[INFO] Saved location: {format_location(latest_location)}")
            self.send_json({"ok": True, "location": latest_location})
        else:
            print("[WARN] Invalid POST location body.")
            self.send_json({"ok": False, "error": "Invalid location body"}, status=400)

    def log_message(self, format, *args):
        return

    def send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, html, status=200):
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def create_location_server(host="0.0.0.0", port=8765):
    return ThreadingHTTPServer((host, port), PhoneLocationHandler)


def main():
    host = "0.0.0.0"
    port = 8765
    server = create_location_server(host, port)
    laptop_ip = get_laptop_ip()
    print(f"[INFO] Phone location server running on http://{host}:{port}")
    print("[INFO] Open on laptop browser: http://127.0.0.1:8765/location-page")
    if laptop_ip:
        print(f"[INFO] Open this on phone: http://{laptop_ip}:{port}/phone")
        print(f"[INFO] Phone update URL: http://{laptop_ip}:{port}/update?lat=<latitude>&lon=<longitude>")
    print("[INFO] Send GPS to: http://<laptop-ip>:8765/update?lat=<latitude>&lon=<longitude>")
    print("[INFO] Latest location endpoint: http://127.0.0.1:8765/location")
    print("[INFO] Server status endpoint: http://127.0.0.1:8765/status")
    print("[INFO] Keep this terminal open while the detector is running. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Phone location server stopped.")
    finally:
        server.server_close()


def get_laptop_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        return None


if __name__ == "__main__":
    main()
