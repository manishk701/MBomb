import threading
import requests
import json
import time
import urllib3
import logging
from requests.exceptions import RequestException

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class APIProvider:

    api_providers = []
    delay = 0
    status = True
    _lock = threading.Lock()  # Class-level lock

    def __init__(self, cc, target, mode, delay=0):
        try:
            with open('apidata.json', 'r') as file:
                PROVIDERS = json.load(file)
        except Exception as e:
            logging.error(f"Error loading apidata.json: {str(e)}")
            try:
                response = requests.get(
                    "https://raw.githubusercontent.com/TezX/MBomb/master/apidata.json",
                    verify=False,
                    timeout=10
                )
                PROVIDERS = response.json()
            except Exception as e:
                logging.error(f"Error fetching apidata.json: {str(e)}")
                raise Exception("Failed to load API data")

        self.config = None
        self.cc = cc
        self.target = target
        self.mode = mode
        self.index = 0
        self.api_version = PROVIDERS.get("version", "2")
        APIProvider.delay = delay
        providers = PROVIDERS.get(mode.lower(), {})
        APIProvider.api_providers = providers.get(cc, [])
        if len(APIProvider.api_providers) < 10:
            APIProvider.api_providers += providers.get("multi", [])

    def format(self):
        try:
            if not self.config:
                return
            config_dump = json.dumps(self.config)
            config_dump = config_dump.replace("{target}", self.target)
            config_dump = config_dump.replace("{cc}", self.cc)
            self.config = json.loads(config_dump)
        except Exception as e:
            logging.error(f"Error formatting config: {str(e)}")
            raise

    def select_api(self):
        try:
            if not APIProvider.api_providers:
                raise IndexError("No API providers available")
            
            with APIProvider._lock:
                self.index = (self.index + 1) % len(APIProvider.api_providers)
                self.config = APIProvider.api_providers[self.index]
                
                perma_headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Connection": "keep-alive"
                }
                
                if "headers" in self.config:
                    self.config["headers"].update(perma_headers)
                else:
                    self.config["headers"] = perma_headers
                
                self.format()
        except Exception as e:
            logging.error(f"Error selecting API: {str(e)}")
            self.index = -1

    def remove(self):
        try:
            with APIProvider._lock:
                if 0 <= self.index < len(APIProvider.api_providers):
                    del APIProvider.api_providers[self.index]
                    return True
        except Exception as e:
            logging.error(f"Error removing API: {str(e)}")
        return False

    def request(self):
        self.select_api()
        if not self.config or self.index == -1:
            return None
        
        try:
            # Special handling for WhatsApp
            if self.mode.lower() == "whatsapp":
                if "web.whatsapp.com" in self.config.get("url", ""):
                    response = requests.get(
                        self.config["url"],
                        params=self.config.get("params", {}),
                        headers=self.config.get("headers", {}),
                        verify=False,
                        timeout=30
                    )
                    return response.status_code == 200
                elif "api.whatsapp.com" in self.config.get("url", ""):
                    response = requests.post(
                        self.config["url"],
                        data=self.config.get("data", {}),
                        headers=self.config.get("headers", {}),
                        verify=False,
                        timeout=30
                    )
                    return response.status_code == 200
                else:
                    response = requests.request(
                        method=self.config.get("method", "GET"),
                        url=self.config["url"],
                        json=self.config.get("data", {}),
                        headers=self.config.get("headers", {}),
                        verify=False,
                        timeout=30
                    )
                    return response.status_code == 200
            
            # Normal request handling for other modes
            identifier = self.config.pop("identifier", "").lower()
            del self.config['name']
            self.config['timeout'] = 30
            self.config['verify'] = False
            
            response = requests.request(**self.config)
            return identifier in response.text.lower()
            
        except RequestException as e:
            logging.error(f"Request error: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error in request: {str(e)}")
            return False

    def hit(self):
        try:
            if not APIProvider.status:
                return False
                
            time.sleep(APIProvider.delay)
            
            with APIProvider._lock:
                response = self.request()
                if response is False:
                    self.remove()
                elif response is None:
                    APIProvider.status = False
                return response
                
        except Exception as e:
            logging.error(f"Error in hit: {str(e)}")
            return False
