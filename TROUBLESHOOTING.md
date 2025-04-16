# MBomb Troubleshooting Guide for Termux

## Common Issues and Solutions

### 1. Installation Issues

**Problem:** Installation fails with package errors
**Solution:**
```bash
# Update Termux
pkg update && pkg upgrade

# Clean package cache
pkg clean

# Try installation again
./install.sh
```

### 2. Python Dependencies Issues

**Problem:** Python packages fail to install
**Solution:**
```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements manually
pip install requests colorama urllib3
```

### 3. Permission Issues

**Problem:** Scripts are not executable
**Solution:**
```bash
# Make scripts executable
chmod +x run.sh bomber.py install.sh
```

### 4. Internet Connection Issues

**Problem:** Poor internet connection detected
**Solution:**
```bash
# Check internet connection
ping google.com

# If using mobile data, ensure:
# - Mobile data is enabled
# - APN settings are correct
# - No VPN is interfering
```

### 5. Storage Issues

**Problem:** Cannot write to storage
**Solution:**
```bash
# Request storage permission
termux-setup-storage

# Create necessary directories
mkdir -p ~/.config/MBomb
```

### 6. API Issues

**Problem:** APIs not working
**Solution:**
- Check if you're using the latest version
- Try different country codes
- Reduce the number of messages/calls
- Increase delay between requests

### 7. Termux Version Issues

**Problem:** Script not working in Termux
**Solution:**
- Install Termux from F-Droid (not Play Store)
- Update Termux to latest version
- Clear Termux data and reinstall

### 8. Logging Issues

**Problem:** Logs not being created
**Solution:**
```bash
# Create log directory
mkdir -p ~/.config/MBomb

# Check permissions
ls -la ~/.config/MBomb
```

### 9. Threading Issues

**Problem:** High CPU usage or crashes
**Solution:**
- Reduce number of threads
- Increase delay between requests
- Use single thread mode

### 10. SSL Certificate Issues

**Problem:** SSL verification errors
**Solution:**
- Update certificates
```bash
pkg install ca-certificates
```

## Getting Help

If you still encounter issues:
1. Check the log file: `~/.config/MBomb/mbomb.log`
2. Try running with debug mode: `python3 bomber.py --debug`
3. Report issues on GitHub with:
   - Error message
   - Log file contents
   - Termux version
   - Python version
   - Steps to reproduce 