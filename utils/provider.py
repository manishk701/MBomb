import threading
import requests
import json
import time
import urllib3
import logging
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import random
from concurrent.futures import ThreadPoolExecutor
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings
urllib3.disable_warnings(InsecureRequestWarning)

class APIProvider:

    api_providers = []
    delay = 0
    status = True
    _lock = threading.Lock()  # Class-level lock

    def __init__(self, country_code, target, mode, delay=0, proxy=None, max_retries=3):
        self.country_code = country_code
        self.target = target
        self.mode = mode
        self.delay = delay
        self.proxy = proxy
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive'
        })
        
        if proxy:
            self.session.proxies = {
                'http': proxy,
                'https': proxy
            }
        
        # Load API data
        try:
            with open('apidata.json', 'r') as f:
                self.api_data = json.load(f)
        except Exception as e:
            logging.error(f"Failed to load API data: {str(e)}")
            raise
            
        # Get available APIs for the country code
        self.apis = self.api_data.get(mode, {}).get(country_code, [])
        if not self.apis:
            logging.error(f"No APIs found for country code {country_code} and mode {mode}")
            raise ValueError(f"No APIs found for country code {country_code} and mode {mode}")
            
        # Initialize rate limiting
        self.rate_limit = {}
        self.rate_limit_lock = threading.Lock()
        
    def format(self):
        try:
            if not self.config:
                return
            config_dump = json.dumps(self.config)
            config_dump = config_dump.replace("{target}", self.target)
            config_dump = config_dump.replace("{cc}", self.country_code)
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

    def _check_rate_limit(self, api_name):
        """Check if we need to wait due to rate limiting"""
        with self.rate_limit_lock:
            current_time = time.time()
            if api_name in self.rate_limit:
                last_request = self.rate_limit[api_name]
                if current_time - last_request < 1:  # 1 second between requests
                    time.sleep(1)
            self.rate_limit[api_name] = current_time
            
    def _make_request(self, api, retry_count=0):
        """Make a single request with retry logic"""
        url = api['url']
        method = api['method']
        data = api.get('data', {})
        headers = api.get('headers', {})
        
        # Replace placeholders in data
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = value.format(target=self.target)
                
        try:
            self._check_rate_limit(api['name'])
            
            if method.upper() == 'GET':
                response = self.session.get(url, params=data, headers=headers, timeout=10)
            else:
                response = self.session.post(url, data=data, headers=headers, timeout=10)
                
            if response.status_code == 200:
                # Check for success identifier
                if api.get('identifier'):
                    if api['identifier'] in response.text:
                        logging.info(f"Success: {api['name']}")
                        return True
                    else:
                        logging.warning(f"Failed: {api['name']} - Identifier not found")
                        return False
                else:
                    logging.info(f"Success: {api['name']}")
                    return True
            else:
                logging.warning(f"Failed: {api['name']} - Status code: {response.status_code}")
                if retry_count < self.max_retries:
                    time.sleep(2 ** retry_count)  # Exponential backoff
                    return self._make_request(api, retry_count + 1)
                return False
                
        except Exception as e:
            logging.error(f"Error in {api['name']}: {str(e)}")
            if retry_count < self.max_retries:
                time.sleep(2 ** retry_count)
                return self._make_request(api, retry_count + 1)
            return False
            
    def hit(self):
        """Send a single request using a random API"""
        if not self.apis:
            return False
            
        api = random.choice(self.apis)
        result = self._make_request(api)
        
        # Add delay between requests
        if self.delay > 0:
            time.sleep(self.delay)
            
        return result
        
    def hit_multiple(self, count, max_workers=5):
        """Send multiple requests concurrently"""
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.hit) for _ in range(count)]
            for future in futures:
                results.append(future.result())
        return sum(results)
