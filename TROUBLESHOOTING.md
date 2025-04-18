# Troubleshooting Guide

## Common Issues and Solutions

### 1. Installation Issues

#### Termux not found
```bash
Error: This script must be run in Termux!
```
**Solution:**
- Install Termux from F-Droid (not Play Store)
- Make sure you're running the script in Termux
- Check if Termux is properly installed: `which termux-setup-storage`

#### Package installation failed
```bash
Error: Failed to install required packages
```
**Solution:**
- Update Termux: `pkg update && pkg upgrade`
- Clear package cache: `pkg clean`
- Try installing packages individually:
  ```bash
  pkg install python
  pkg install git
  pkg install wget
  pkg install curl
  ```

### 2. Python Issues

#### Python not found
```bash
Error: Python3 is not installed
```
**Solution:**
- Install Python: `pkg install python`
- Verify installation: `python --version`
- If still not found, try: `pkg install python3`

#### Pip not found
```bash
Error: pip command not found
```
**Solution:**
- Install pip: `python -m ensurepip --upgrade`
- Upgrade pip: `python -m pip install --upgrade pip`
- Verify installation: `pip --version`

#### Package installation failed
```bash
Error: Failed to install Python dependencies
```
**Solution:**
- Update pip: `pip install --upgrade pip`
- Install packages individually:
  ```bash
  pip install requests
  pip install colorama
  pip install urllib3
  pip install beautifulsoup4
  pip install lxml
  ```
- Check internet connection
- Try using a different package index:
  ```bash
  pip install -r requirements.txt -i https://pypi.org/simple
  ```

### 3. Script Execution Issues

#### Permission denied
```bash
Error: Permission denied
```
**Solution:**
- Make scripts executable:
  ```bash
  chmod +x *.sh
  chmod +x bomber.py
  ```
- Check file ownership: `ls -l`
- Run as proper user

#### Script not found
```bash
Error: No such file or directory
```
**Solution:**
- Check current directory: `pwd`
- List files: `ls`
- Navigate to correct directory: `cd /path/to/MBomb`

### 4. Runtime Issues

#### Internet connection error
```bash
Error: Poor internet connection detected
```
**Solution:**
- Check internet connection
- Try pinging a server: `ping google.com`
- Check if using VPN (disable if using)
- Restart Termux

#### SSL errors
```bash
Error: SSL certificate verification failed
```
**Solution:**
- Update certifi: `pip install --upgrade certifi`
- Check system date/time
- Try disabling SSL verification (not recommended)
- Update system certificates

#### API errors
```bash
Error: API request failed
```
**Solution:**
- Check if APIs are working
- Try different country code
- Reduce number of requests
- Increase delay between requests
- Check log file: `cat ~/.config/MBomb/mbomb.log`

### 5. Logging

#### Where to find logs
- Main log file: `~/.config/MBomb/mbomb.log`
- Error messages are also displayed in terminal
- Check last 50 lines: `tail -n 50 ~/.config/MBomb/mbomb.log`

#### How to enable debug mode
```bash
python bomber.py --debug
```

### 6. Additional Help

If you're still experiencing issues:
1. Check the log file
2. Try running in debug mode
3. Open an issue on GitHub
4. Join the Telegram support group

Remember to include:
- Error messages
- Log file contents
- Steps to reproduce
- Your environment details 