from colorama import Fore, Style


class IconicDecorator(object):
    def __init__(self):
        self.PASS = Style.BRIGHT + Fore.GREEN + "[ ✔ ]" + Style.RESET_ALL
        self.FAIL = Style.BRIGHT + Fore.RED + "[ ✘ ]" + Style.RESET_ALL
        self.WARN = Style.BRIGHT + Fore.YELLOW + "[ ! ]" + Style.RESET_ALL
        self.HEAD = Style.BRIGHT + Fore.CYAN + "[ # ]" + Style.RESET_ALL
        self.CMDL = Style.BRIGHT + Fore.BLUE + "[ → ]" + Style.RESET_ALL
        self.STDS = "     "


class StatusDecorator(object):
    def __init__(self):
        self.PASS = Style.BRIGHT + Fore.GREEN + "[ SUCCESS ]" + Style.RESET_ALL
        self.FAIL = Style.BRIGHT + Fore.RED + "[ FAILURE ]" + Style.RESET_ALL
        self.WARN = Style.BRIGHT + Fore.YELLOW + "[ WARNING ]"\
            + Style.RESET_ALL
        self.HEAD = Style.BRIGHT + Fore.CYAN + "[ SECTION ]" + Style.RESET_ALL
        self.CMDL = Style.BRIGHT + Fore.BLUE + "[ COMMAND ]" + Style.RESET_ALL
        self.STDS = "           "


class MessageDecorator:
    def __init__(self):
        self.BLUE = Style.BRIGHT + Fore.BLUE
        self.RED = Style.BRIGHT + Fore.RED
        self.GREEN = Style.BRIGHT + Fore.GREEN
        self.YELLOW = Style.BRIGHT + Fore.YELLOW
        self.MAGENTA = Style.BRIGHT + Fore.MAGENTA
        self.RESET = Style.RESET_ALL
        
    def SuccessMessage(self, message):
        print(f"{self.GREEN}[+] {message}{self.RESET}")
        
    def FailureMessage(self, message):
        print(f"{self.RED}[-] {message}{self.RESET}")
        
    def WarningMessage(self, message):
        print(f"{self.YELLOW}[!] {message}{self.RESET}")
        
    def SectionMessage(self, message):
        print(f"{self.MAGENTA}[*] {message}{self.RESET}")
        
    def GeneralMessage(self, message):
        print(f"{self.BLUE}[#] {message}{self.RESET}")
        
    def CommandMessage(self, message):
        return f"{self.YELLOW}[>] {message}{self.RESET}"

