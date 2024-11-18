import argparse
import yaml
import requests
import time
from collections import defaultdict
from urllib.parse import urlparse

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Suppress urllib3 logs
urllib3_logger = logging.getLogger("urllib3")
urllib3_logger.setLevel(logging.WARNING)

#Uncomment to add support for sentry error spans
# import sentry_sdk
# import os
# sentry_sdk.init(
#     dsn=os.environ.get("SENTRY_DSN"),
#     # Set traces_sample_rate to 1.0 to capture 100%
#     # of transactions for tracing.
#     traces_sample_rate=1.0,
#     # Set profiles_sample_rate to 1.0 to profile 100%
#     # of sampled transactions.
#     # We recommend adjusting this value in production.
#     profiles_sample_rate=1.0,
# )

def read_config(file_path):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)

# Function to send a request and determine if it's UP or DOWN
# UP is determined if there is a succesful http status code and latency is <500ms
# Input: endpoint
# Outputs True or None (Which evals to False for our purposes)
def check_health(endpoint):
    url = endpoint["url"]
    method = endpoint.get("method", "GET").upper()
    headers = endpoint.get("headers", {})
    body = endpoint.get("body", None)
    
    try:
        start_time = time.time()
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, headers=headers, data=body, timeout=5)
        else:
            logger.error(f"Unsupported method {method}. Skipping...")
            return False
        
        latency = (time.time() - start_time) * 1000  # convert to ms
        if 200 <= response.status_code < 300 and latency < 500:
            return True
    except requests.RequestException as e:
        logger.info(f"Request failed for {url}: {e}")
    return False

def monitor_health(config_path):
    config = read_config(config_path)
    domain_stats = defaultdict(lambda: {"up": 0, "total": 0})

    try:
        while True:
            for endpoint in config:
                # Get just the domain part of the URL
                domain = urlparse(endpoint["url"]).netloc
                is_up = check_health(endpoint)
                
                domain_stats[domain]["total"] += 1
                if is_up:
                    domain_stats[domain]["up"] += 1
            
            # Log availability 
            for domain, stats in domain_stats.items():
                availability = (stats["up"] / stats["total"]) * 100
                logger.info(f"{domain} has {round(availability)}% availability percentage")
                if availability < 20 and stats["total"] > 4:
                    # Send sentry error so we are aware of low availability
                    logger.error(f"{domain} has availability < 20%! Please Investigate.")
            
            time.sleep(15)
    except KeyboardInterrupt:
        logger.info("Monitoring stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HTTP Endpoint Health Monitor")
    parser.add_argument("config", help="Path to the YAML configuration file")
    args = parser.parse_args()

    monitor_health(args.config)
