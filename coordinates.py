import subprocess
import os

os.system(
    "adb pull $(adb shell uiautomator dump | grep -oP '[^ ]+.xml') /tmp/view.xml")

getVersion = subprocess.Popen(
    """perl -ne 'printf "%d %d\n", ($1+$3)/2, ($2+$4)/2 if /content-desc="Install"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"/' /tmp/view.xml""", shell=True, stdout=subprocess.PIPE).stdout
version = getVersion.read()

getVersion = subprocess.Popen(
    """perl -ne 'printf "%d %d\n", ($1+$3)/2, ($2+$4)/2 if /content-desc="Uninstall"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"/' /tmp/view.xml""", shell=True, stdout=subprocess.PIPE).stdout
version = getVersion.read()

print(str(version.decode('UTF-8').strip()))
