import requests
import time
import logging

# URLs to monitor
urls = [
    "http://www.example.com/nonexistentpage",
    "http://httpstat.us/404",
    "http://httpstat.us/500",
    "https://www.google.com/"
]

# Logging setup
logging.basicConfig(
    filename="uptime_monitor.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# Track consecutive errors for exponential backoff
error_count = {url: 0 for url in urls}

def check_url(url):
    try:
        print(f"\nChecking URL: {url}")

        response = requests.get(url, timeout=5)
        status = response.status_code
        message = f"Status Code: {status}"

        print(message)
        logging.info(f"{url} -> {status}")

        if 200 <= status < 300:
            print("The website is UP and running.")
            error_count[url] = 0

        elif 400 <= status < 500:
            print(f"ALERT: 4xx error encountered for URL: {url}")
            logging.warning(f"Client Error at {url}")
            error_count[url] += 1

        elif 500 <= status < 600:
            print(f"ALERT: 5xx error encountered for URL: {url}")
            logging.error(f"Server Error at {url}")
            error_count[url] += 1

    except requests.exceptions.RequestException as e:
        print(f"ERROR: Could not reach {url}")
        logging.error(f"Connection error for {url}")
        error_count[url] += 1


while True:
    for url in urls:
        check_url(url)

        # Exponential backoff if multiple errors
        if error_count[url] > 0:
            wait_time = min(10 * (2 ** error_count[url]), 60)
            print(f"Retrying {url} after {wait_time} seconds due to errors...")
            time.sleep(wait_time)
        else:
            time.sleep(2)

    print("\nWaiting 10 seconds before next monitoring cycle...\n")
    time.sleep(10)