#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import shutil
import sys
import subprocess
import string
import random
import json
import re
import time
import argparse
import zipfile
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils.decorators import MessageDecorator
from utils.provider import APIProvider

try:
    import requests
    from colorama import Fore, Style
except ImportError:
    print("\tSome dependencies could not be imported (possibly not installed)")
    print("Type `pip3 install -r requirements.txt` to install all required packages")
    sys.exit(1)

def readisdc():
    try:
        with open("isdcodes.json") as file:
            isdcodes = json.load(file)
        return isdcodes
    except Exception as e:
        mesgdcrt.FailureMessage(f"Error reading ISD codes: {str(e)}")
        sys.exit(1)

def get_version():
    try:
        return open(".version", "r").read().strip()
    except Exception:
        return '1.0'

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

    if ASCII_MODE:
        logo = ""
    version = "Version: "+__VERSION__
    contributors = "Contributors: "+" ".join(__CONTRIBUTORS__)
    print(random.choice(ALL_COLORS) + logo + RESET_ALL)
    mesgdcrt.SuccessMessage(version)
    mesgdcrt.SectionMessage(contributors)
    print()

def check_intr():
    try:
        requests.get("https://motherfuckingwebsite.com")
    except Exception:
        bann_text()
        mesgdcrt.FailureMessage("Poor internet connection detected")
        sys.exit(2)

def format_phone(num):
    num = [n for n in num if n in string.digits]
    return ''.join(num).strip()

def do_zip_update():
    success = False
    try:
        print(ALL_COLORS[0]+"Downloading ZIP update... "+RESET_ALL)
        if DEBUG_MODE:
            zip_url = "https://github.com/manishk701/MBomb/archive/dev.zip"
            dir_name = "TBomb-dev"
        else:
            zip_url = "https://github.com/manishk701/MBomb/archive/master.zip"
            dir_name = "TBomb-master"
        
        response = requests.get(zip_url)
        if response.status_code == 200:
            zip_content = response.content
            try:
                with zipfile.ZipFile(BytesIO(zip_content)) as zip_file:
                    for member in zip_file.namelist():
                        filename = os.path.split(member)
                        if not filename[1]:
                            continue
                        new_filename = os.path.join(
                            filename[0].replace(dir_name, "."),
                            filename[1])
                        source = zip_file.open(member)
                        target = open(new_filename, "wb")
                        with source, target:
                            shutil.copyfileobj(source, target)
                success = True
            except Exception:
                mesgdcrt.FailureMessage("Error occurred while extracting !!")
    except Exception:
        mesgdcrt.FailureMessage("Failed to download update")
    
    if success:
        mesgdcrt.SuccessMessage("TBomb was updated to the latest version")
        mesgdcrt.GeneralMessage("Please run the script again to load the latest version")
    else:
        mesgdcrt.FailureMessage("Unable to update TBomb.")
        mesgdcrt.WarningMessage("Grab The Latest one From https://github.com/manishk701/MBomb.git")
    sys.exit()

def do_git_update():
    success = False
    try:
        print(ALL_COLORS[0]+"UPDATING "+RESET_ALL, end='')
        process = subprocess.Popen("git checkout . && git pull",
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        
        while process:
            print(ALL_COLORS[0]+'.'+RESET_ALL, end='')
            time.sleep(1)
            returncode = process.poll()
            if returncode is not None:
                break
        success = not process.returncode
    except Exception:
        success = False
    print("\n")
    
    if success:
        mesgdcrt.SuccessMessage("TBomb was updated to the latest version")
        mesgdcrt.GeneralMessage("Please run the script again to load the latest version")
    else:
        mesgdcrt.FailureMessage("Unable to update TBomb.")
        mesgdcrt.WarningMessage("Make Sure To Install 'git'")
        mesgdcrt.GeneralMessage("Then run command:")
        print("git checkout . && git pull https://github.com/manishk701/MBomb.git HEAD")
    sys.exit()

def update():
    if shutil.which('git'):
        do_git_update()
    else:
        do_zip_update()

def check_for_updates():
    if DEBUG_MODE:
        mesgdcrt.WarningMessage("DEBUG MODE Enabled! Auto-Update check is disabled.")
        return
    mesgdcrt.SectionMessage("Checking for updates")
    fver = requests.get(
        "https://raw.githubusercontent.com/manishk701/MBomb/master/.version"
    ).text.strip()
    if fver != __VERSION__:
        mesgdcrt.WarningMessage("An update is available")
        mesgdcrt.GeneralMessage("Starting update...")
        update()
    else:
        mesgdcrt.SuccessMessage("TBomb is up-to-date")
        mesgdcrt.GeneralMessage("Starting TBomb")

def notifyen():
    try:
        if DEBUG_MODE:
            url = "https://github.com/manishk701/MBomb/raw/dev/.notify"
        else:
            url = "https://github.com/manishk701/MBomb/raw/master/.notify"
        noti = requests.get(url).text.upper()
        if len(noti) > 10:
            mesgdcrt.SectionMessage("NOTIFICATION: " + noti)
            print()
    except Exception:
        pass

def get_phone_info():
    while True:
        target = ""
        cc = input(mesgdcrt.CommandMessage("Enter your country code (Without +): "))
        cc = format_phone(cc)
        if not country_codes.get(cc, False):
            mesgdcrt.WarningMessage(f"The country code ({cc}) that you have entered is invalid or unsupported")
            continue
        target = input(mesgdcrt.CommandMessage("Enter the target number: +" + cc + " "))
        target = format_phone(target)
        if ((len(target) <= 6) or (len(target) >= 12)):
            mesgdcrt.WarningMessage(f"The phone number ({target}) that you have entered is invalid")
            continue
        return (cc, target)

def get_mail_info():
    mail_regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    while True:
        target = input(mesgdcrt.CommandMessage("Enter target mail: "))
        if not re.search(mail_regex, target, re.IGNORECASE):
            mesgdcrt.WarningMessage(f"The mail ({target}) that you have entered is invalid")
            continue
        return target

def pretty_print(cc, target, success, failed):
    requested = success+failed
    mesgdcrt.SectionMessage("Bombing is in progress - Please be patient")
    mesgdcrt.GeneralMessage("Please stay connected to the internet during bombing")
    mesgdcrt.GeneralMessage("Target       : " + cc + " " + target)
    mesgdcrt.GeneralMessage("Sent         : " + str(requested))
    mesgdcrt.GeneralMessage("Successful   : " + str(success))
    mesgdcrt.GeneralMessage("Failed       : " + str(failed))
    mesgdcrt.WarningMessage("This tool was made for fun and research purposes only")
    mesgdcrt.SuccessMessage("TBomb was created by SpeedX")

def workernode(mode, cc, target, count, delay, max_threads):
    api = APIProvider(cc, target, mode, delay=delay)
    clr()
    mesgdcrt.SectionMessage("Gearing up the Bomber - Please be patient")
    mesgdcrt.GeneralMessage("Please stay connected to the internet during bombing")
    mesgdcrt.GeneralMessage("API Version   : " + api.api_version)
    mesgdcrt.GeneralMessage("Target        : " + cc + target)
    mesgdcrt.GeneralMessage("Amount        : " + str(count))
    mesgdcrt.GeneralMessage("Threads       : " + str(max_threads) + " threads")
    mesgdcrt.GeneralMessage("Delay         : " + str(delay) + " seconds")
    mesgdcrt.WarningMessage("This tool was made for fun and research purposes only")
    print()
    input(mesgdcrt.CommandMessage("Press [CTRL+Z] to suspend the bomber or [ENTER] to resume it"))

    if len(APIProvider.api_providers) == 0:
        mesgdcrt.FailureMessage("Your country/target is not supported yet")
        mesgdcrt.GeneralMessage("Feel free to reach out to us")
        input(mesgdcrt.CommandMessage("Press [ENTER] to exit"))
        bann_text()
        sys.exit()

    success, failed = 0, 0
    start_time = time.time()
    batch_size = 20  # Increased batch size for speed
    current_batch = 0
    retry_count = 0
    max_retries = 3
    last_success_time = time.time()
    consecutive_failures = 0
    max_consecutive_failures = 3
    success_history = []
    failure_history = []
    dynamic_delay = delay
    optimal_threads = max_threads
    provider_stats = {}
    speed_boost = False
    
    while success < count:
        batch_start = time.time()
        current_batch += 1
        batch_target = min(batch_size, count - success)
        
        mesgdcrt.SectionMessage(f"Processing Batch {current_batch} ({batch_target} messages)")
        
        with ThreadPoolExecutor(max_workers=optimal_threads) as executor:
            futures = []
            for i in range(batch_target):
                futures.append(executor.submit(api.hit))
                
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result is None:
                        mesgdcrt.FailureMessage("Bombing limit for your target has been reached")
                        mesgdcrt.GeneralMessage("Try Again Later !!")
                        input(mesgdcrt.CommandMessage("Press [ENTER] to exit"))
                        bann_text()
                        sys.exit()
                    if result:
                        success += 1
                        retry_count = 0
                        consecutive_failures = 0
                        last_success_time = time.time()
                        success_history.append(time.time())
                        # Remove old success entries (older than 30 seconds)
                        success_history = [t for t in success_history if time.time() - t < 30]
                        
                        # Speed boost logic
                        if len(success_history) >= 10 and not speed_boost:
                            speed_boost = True
                            optimal_threads = min(max_threads * 2, 50)  # Double threads if possible
                            dynamic_delay = max(0.1, dynamic_delay * 0.5)  # Reduce delay
                            mesgdcrt.SuccessMessage("Speed boost activated!")
                    else:
                        failed += 1
                        retry_count += 1
                        consecutive_failures += 1
                        failure_history.append(time.time())
                        # Remove old failure entries (older than 30 seconds)
                        failure_history = [t for t in failure_history if time.time() - t < 30]
                        
                        # Calculate success rate in the last 30 seconds
                        recent_success = len(success_history)
                        recent_failures = len(failure_history)
                        recent_total = recent_success + recent_failures
                        recent_success_rate = (recent_success / recent_total * 100) if recent_total > 0 else 0
                        
                        # Dynamic adjustment based on recent performance
                        if recent_success_rate < 70:  # Reduced threshold for speed
                            dynamic_delay = min(1.0, dynamic_delay + 0.1)  # Reduced max delay
                            optimal_threads = max(1, optimal_threads - 1)
                            speed_boost = False
                            mesgdcrt.WarningMessage(f"Adjusting settings: Delay={dynamic_delay:.2f}s, Threads={optimal_threads}")
                        elif recent_success_rate > 90 and dynamic_delay > delay:  # Increased threshold
                            dynamic_delay = max(0.1, dynamic_delay - 0.1)  # Reduced min delay
                            optimal_threads = min(max_threads * 2, optimal_threads + 1)
                            mesgdcrt.SuccessMessage(f"Optimizing settings: Delay={dynamic_delay:.2f}s, Threads={optimal_threads}")
                    
                    elapsed_time = time.time() - start_time
                    messages_per_second = success / elapsed_time if elapsed_time > 0 else 0
                    success_rate = (success / (success + failed) * 100) if (success + failed) > 0 else 0
                    estimated_time = (count - success) / messages_per_second if messages_per_second > 0 else 0
                    
                    clr()
                    print(f"\n{Fore.LIGHTGREEN_EX}Success: {success} | {Fore.LIGHTRED_EX}Failed: {failed}")
                    print(f"{Fore.LIGHTYELLOW_EX}Speed: {messages_per_second:.2f} messages/second")
                    print(f"{Fore.LIGHTCYAN_EX}Time elapsed: {elapsed_time:.2f} seconds")
                    print(f"{Fore.LIGHTMAGENTA_EX}Progress: {(success / count * 100):.2f}%")
                    print(f"{Fore.LIGHTBLUE_EX}Success Rate: {success_rate:.2f}%")
                    print(f"{Fore.LIGHTWHITE_EX}Estimated time remaining: {estimated_time:.2f} seconds")
                    print(f"{Fore.LIGHTYELLOW_EX}Current Delay: {dynamic_delay:.2f} seconds")
                    print(f"{Fore.LIGHTCYAN_EX}Current Threads: {optimal_threads}")
                    print(f"{Fore.LIGHTMAGENTA_EX}Recent Success Rate: {recent_success_rate:.2f}%")
                    if speed_boost:
                        print(f"{Fore.LIGHTGREEN_EX}Speed Boost: ACTIVE")
                    
                except Exception as e:
                    failed += 1
                    mesgdcrt.WarningMessage(f"An error occurred: {str(e)}")
                    continue
        
        # Batch completion handling
        batch_time = time.time() - batch_start
        if batch_time < 5:  # Reduced wait time
            time.sleep(0.1)  # Reduced sleep time
        elif batch_time > 10:  # Reduced threshold
            optimal_threads = max(1, optimal_threads - 1)
            speed_boost = False
            mesgdcrt.WarningMessage(f"Reducing threads to {optimal_threads} for better stability")
            
        # Check if we need to increase delay
        if time.time() - last_success_time > 10:  # Reduced threshold
            dynamic_delay = min(1.0, dynamic_delay + 0.1)  # Reduced max delay
            speed_boost = False
            mesgdcrt.WarningMessage(f"Increasing delay to {dynamic_delay:.2f} seconds")

    print("\n")
    mesgdcrt.SuccessMessage("Bombing completed!")
    print(f"{Fore.LIGHTGREEN_EX}Total Success: {success}")
    print(f"{Fore.LIGHTRED_EX}Total Failed: {failed}")
    print(f"{Fore.LIGHTYELLOW_EX}Average Speed: {success / (time.time() - start_time):.2f} messages/second")
    print(f"{Fore.LIGHTCYAN_EX}Total Time: {time.time() - start_time:.2f} seconds")
    print(f"{Fore.LIGHTBLUE_EX}Final Success Rate: {(success / count * 100):.2f}%")
    time.sleep(1.5)
    bann_text()
    sys.exit()

def selectnode(mode="sms"):
    mode = mode.lower().strip()
    try:
        clr()
        bann_text()
        check_intr()
        check_for_updates()
        notifyen()

        max_limit = {"sms": 500, "call": 15, "mail": 200, "whatsapp": 100}
        cc, target = "", ""
        if mode in ["sms", "call", "whatsapp"]:
            cc, target = get_phone_info()
            if cc != "91":
                max_limit.update({"sms": 100})
        elif mode == "mail":
            target = get_mail_info()
        else:
            raise KeyboardInterrupt

        limit = max_limit[mode]
        while True:
            try:
                message = ("Enter number of {type}".format(type=mode.upper()) +
                         " to send (Max {limit}): ".format(limit=limit))
                count = int(input(mesgdcrt.CommandMessage(message)).strip())
                if count > limit or count == 0:
                    mesgdcrt.WarningMessage("You have requested " + str(count)
                                          + " {type}".format(type=mode.upper()))
                    mesgdcrt.GeneralMessage("Automatically capping the value"
                                          " to {limit}".format(limit=limit))
                    count = limit
                
                # Optimized delay calculation
                base_delay = 0.5
                if count > 200:
                    base_delay = 0.8
                elif count > 100:
                    base_delay = 0.6
                
                delay = float(input(
                    mesgdcrt.CommandMessage(f"Enter delay time (in seconds, recommended: {base_delay}): "))
                    .strip())
                delay = max(delay, base_delay)
                
                # Optimized thread calculation
                max_thread_limit = min(count, 10)  # Reduced max threads
                if count > 200:
                    max_thread_limit = min(count // 30, 10)
                elif count > 100:
                    max_thread_limit = min(count // 20, 10)
                
                max_threads = int(input(
                    mesgdcrt.CommandMessage(
                        "Enter Number of Thread (Recommended: {max_limit}): "
                        .format(max_limit=max_thread_limit)))
                    .strip())
                max_threads = min(max_threads, max_thread_limit)
                
                if (count < 0 or delay < 0):
                    raise Exception
                break
            except KeyboardInterrupt as ki:
                raise ki
            except Exception:
                mesgdcrt.FailureMessage("Read Instructions Carefully !!!")
                print()

        workernode(mode, cc, target, count, delay, max_threads)
    except KeyboardInterrupt:
        mesgdcrt.WarningMessage("Received INTR call - Exiting...")
        sys.exit()

mesgdcrt = MessageDecorator("icon")
if sys.version_info[0] != 3:
    mesgdcrt.FailureMessage("TBomb will work only in Python v3")
    sys.exit()

try:
    country_codes = readisdc()["isdcodes"]
except FileNotFoundError:
    update()

__VERSION__ = get_version()
__CONTRIBUTORS__ = ['Manish Kumar', 'WH No- 8809377701', 'mintu virus', 'abhinav Sharma']

ALL_COLORS = [Fore.GREEN, Fore.RED, Fore.YELLOW, Fore.BLUE,
              Fore.MAGENTA, Fore.CYAN, Fore.WHITE]
RESET_ALL = Style.RESET_ALL

ASCII_MODE = False
DEBUG_MODE = False

description = """TBomb - Your Friendly Spammer Application

TBomb can be used for many purposes which incudes -
\t Exposing the vulnerable APIs over Internet
\t Friendly Spamming
\t Testing Your Spam Detector and more ....

TBomb is not intented for malicious uses.
"""

parser = argparse.ArgumentParser(description=description,
                               epilog='Coded by TezX !!!')
parser.add_argument("-sms", "--sms", action="store_true",
                   help="start TBomb with SMS Bomb mode")
parser.add_argument("-call", "--call", action="store_true",
                   help="start TBomb with CALL Bomb mode")
parser.add_argument("-mail", "--mail", action="store_true",
                   help="start TBomb with MAIL Bomb mode")
parser.add_argument("-whatsapp", "--whatsapp", action="store_true",
                   help="start TBomb with WhatsApp Bomb mode")
parser.add_argument("-ascii", "--ascii", action="store_true",
                   help="show only characters of standard ASCII set")
parser.add_argument("-u", "--update", action="store_true",
                   help="update TBomb")
parser.add_argument("-c", "--contributors", action="store_true",
                   help="show current TBomb contributors")
parser.add_argument("-v", "--version", action="store_true",
                   help="show current TBomb version")

if __name__ == "__main__":
    args = parser.parse_args()
    if args.ascii:
        ASCII_MODE = True
        mesgdcrt = MessageDecorator("stat")
    if args.version:
        print("Version: ", __VERSION__)
    elif args.contributors:
        print("Contributors: ", " ".join(__CONTRIBUTORS__))
    elif args.update:
        update()
    elif args.mail:
        selectnode(mode="mail")
    elif args.call:
        selectnode(mode="call")
    elif args.sms:
        selectnode(mode="sms")
    elif args.whatsapp:
        selectnode(mode="whatsapp")
    else:
        choice = ""
        avail_choice = {
            "1": "SMS",
            "2": "CALL",
            "3": "MAIL",
            "4": "WHATSAPP"
        }
        try:
            while (choice not in avail_choice):
                clr()
                bann_text()
                print("Available Options:\n")
                for key, value in avail_choice.items():
                    print("[ {key} ] {value} BOMB".format(key=key,
                                                         value=value))
                print()
                choice = input(mesgdcrt.CommandMessage("Enter Choice : "))
            selectnode(mode=avail_choice[choice].lower())
        except KeyboardInterrupt:
            mesgdcrt.WarningMessage("Received INTR call - Exiting...")
            sys.exit()
    sys.exit()
