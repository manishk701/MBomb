#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
import sys
import json
import time
import logging
import argparse
import string
from datetime import datetime

from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.decorators import MessageDecorator
from utils.provider import APIProvider

# Check if running in Termux
if not os.path.exists("/data/data/com.termux/files/usr"):
    print("This script must be run in Termux!")
    sys.exit(1)

try:
    import requests
    import urllib3
    from colorama import Fore, Style, init
except ImportError as e:
    print(f"\tError importing dependencies: {str(e)}")
    print("Type `pip install -r requirements.txt` to install all required packages")
    sys.exit(1)

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Initialize colorama
init(autoreset=True)

# Setup logging
log_dir = os.path.expanduser("~/.config/MBomb")
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, 'mbomb.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Global variables
DEBUG_MODE = False
ASCII_MODE = False
VERSION = "2.2b"
CONTRIBUTORS = ["TezX", "t0xic0der", "scpketer", "Stefan"]
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
        logging.info("Internet connection check successful")
    except Exception as e:
        mesgdcrt.FailureMessage("Poor internet connection detected")
        logging.error(f"Internet connection check failed: {str(e)}")
        sys.exit(2)

def readisdc():
    try:
        with open("isdcodes.json") as file:
            return json.load(file)
    except Exception as e:
        mesgdcrt.FailureMessage(f"Error loading ISD codes: {str(e)}")
        logging.error(f"Failed to load ISD codes: {str(e)}")
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

def pretty_print(cc, target, success, failed):
    requested = success + failed
    
    print(f"\n{Fore.CYAN}══════════════ BOMBING STATUS ══════════════{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Target      :{Style.RESET_ALL} +{cc} {target}")
    print(f"{Fore.YELLOW}Sent        :{Style.RESET_ALL} {requested}")
    print(f"{Fore.GREEN}Successful   :{Style.RESET_ALL} {success}")
    print(f"{Fore.RED}Failed       :{Style.RESET_ALL} {failed}")
    print(f"{Fore.CYAN}══════════════════════════════════════════{Style.RESET_ALL}\n")
    
    logging.info(f"Bombing status - Target: +{cc}{target}, Sent: {requested}, Success: {success}, Failed: {failed}")

def workernode(mode, cc, target, count, delay, max_threads):
    try:
        api = APIProvider(cc, target, mode, delay=delay)
        success, failed = 0, 0
        start_time = time.time()
        
        while success < count:
            try:
                with ThreadPoolExecutor(max_workers=max_threads) as executor:
                    jobs = []
                    for i in range(min(count - success, max_threads)):
                        jobs.append(executor.submit(api.hit))
                    
                    for job in as_completed(jobs):
                        result = job.result()
                        if result:
                            success += 1
                        else:
                            failed += 1
                        
                        pretty_print(cc, target, success, failed)
                        
                        if success + failed == count:
                            break
                            
            except KeyboardInterrupt:
                mesgdcrt.WarningMessage("Received INTR call - Exiting...")
                logging.warning("Bombing interrupted by user")
                sys.exit(1)
            except Exception as e:
                mesgdcrt.FailureMessage(f"Unexpected error: {str(e)}")
                logging.error(f"Error during bombing: {str(e)}")
                failed += 1
            
            if success + failed == count:
                break
                
        end_time = time.time()
        duration = end_time - start_time
        logging.info(f"Bombing completed in {duration:.2f} seconds")
        return (success, failed)
        
    except Exception as e:
        mesgdcrt.FailureMessage(f"Error initializing API provider: {str(e)}")
        logging.error(f"API provider initialization failed: {str(e)}")
        return (0, count)

def selectnode(mode="sms"):
    mode = mode.lower().strip()
    try:
        clr()
        bann_text()
        check_intr()

        max_limit = {"sms": 500, "call": 15, "whatsapp": 100}
        
        if mode not in WEBSITES:
            mesgdcrt.FailureMessage(f"Invalid mode - {mode}")
            logging.error(f"Invalid mode selected: {mode}")
            sys.exit(1)
            
        mesgdcrt.SectionMessage(f"Starting {WEBSITES[mode]}")
        logging.info(f"Starting {WEBSITES[mode]}")
        
        cc, target = get_phone_info()
        
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
        
        max_threads = 5
        mesgdcrt.GeneralMessage("==== API Information ====")
        mesgdcrt.GeneralMessage(f"Target        : +{cc} {target}")
        mesgdcrt.GeneralMessage(f"Amount        : {count}")
        mesgdcrt.GeneralMessage(f"Threads       : {max_threads}")
        mesgdcrt.GeneralMessage(f"Delay         : {delay}s")
        mesgdcrt.GeneralMessage("==== Starting... ====")
        
        logging.info(f"Starting bombing with parameters - Target: +{cc}{target}, Count: {count}, Threads: {max_threads}, Delay: {delay}s")
        
        success, failed = workernode(mode, cc, target, count, delay, max_threads)
        
        mesgdcrt.SuccessMessage(f"\nBombing completed with {success} successful and {failed} failed attempts")
        
    except KeyboardInterrupt:
        mesgdcrt.WarningMessage("Received INTR call - Exiting...")
        logging.warning("Program interrupted by user")
        sys.exit(1)
    except Exception as e:
        mesgdcrt.FailureMessage(f"Unexpected error: {str(e)}")
        logging.error(f"Program error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MBomb - A powerful SMS/Call/WhatsApp bomber')
    parser.add_argument("--sms", action="store_true", help="start SMS bomber")
    parser.add_argument("--call", action="store_true", help="start call bomber")
    parser.add_argument("--whatsapp", action="store_true", help="start WhatsApp bomber")
    parser.add_argument("--debug", action="store_true", help="enable debug mode")
    args = parser.parse_args()
    
    if args.debug:
        DEBUG_MODE = True
        logging.getLogger().setLevel(logging.DEBUG)
        logging.info("Debug mode enabled")
    
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
