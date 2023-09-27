import os
import time
import subprocess
from scanner import start_function
from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
    with open("apps.txt") as file:
        for apkName in file:
            apkName = apkName.rstrip()
            SERVER = os.environ.get("SERVER")
            APIKEY = os.environ.get("API_KEY")
            directory = os.environ.get("DIRECTORY")
            destination = directory+apkName+'.apk'
            os.system("adb shell am start -a android.intent.action.VIEW -d https://play.google.com/store/apps/details?id="+apkName+"&hl=en&gl=US")
            time.sleep(5)
            os.system("adb pull $(adb shell uiautomator dump | grep -oP '[^ ]+.xml') /tmp/view.xml")
            readCoordinates = subprocess.Popen(
                """perl -ne 'printf "%d %d\n", ($1+$3)/2, ($2+$4)/2 if /content-desc="Try again"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"/' /tmp/view.xml""", shell=True, stdout=subprocess.PIPE).stdout
            coordinates = ''
            coordinatesVersion=''
            coordinatesVersion = subprocess.Popen("""grep -R "This app isn't available for your device because it was made for an older version of Android." /tmp/view.xml""", shell=True, stdout=subprocess.PIPE).stdout
            coordinates = readCoordinates.read()
            coordinatesVer = coordinatesVersion.read()
            coordinatesCountry = subprocess.Popen("""grep -R "This item is not available in your country." /tmp/view.xml""", shell=True, stdout=subprocess.PIPE).stdout
            coordinatesCountr = coordinatesCountry.read()
            coordinatesCompat = subprocess.Popen("""grep -R "Your device isn't compatible with this version." /tmp/view.xml""", shell=True, stdout=subprocess.PIPE).stdout
            coordinatesCompt = coordinatesCompat.read()
            if coordinates.decode('UTF-8') != '':
                print("[*] App "+apkName+" not found")
                print("[*] Scanning next apk")
            elif coordinatesVer.decode('UTF-8')!='':
                print("[*] App "+apkName+" Version does not exist for this device")
            elif coordinatesCountr.decode("UTF-8")!='':
                print("[*] App "+apkName+" does not exist in country")
            elif coordinatesCompt.decode("UTF-8")!='':
                print("[*] App "+apkName+" version not compatible")
            else:
                readCoordinates = subprocess.Popen(
                    """perl -ne 'printf "%d %d\n", ($1+$3)/2, ($2+$4)/2 if /content-desc="Install"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"/' /tmp/view.xml""", shell=True, stdout=subprocess.PIPE).stdout
                coordinates = readCoordinates.read()
                coordinatesCleaned = coordinates.decode('UTF-8').strip()
                if coordinatesCleaned != '':
                    os.system("adb shell input tap " +
                            coordinatesCleaned)
                maxWaitingTime = 3600
                while True:
                    time.sleep(5)
                    os.system(
                        "adb pull $(adb shell uiautomator dump | grep -oP '[^ ]+.xml') /tmp/view.xml")
                    checkInstalled = subprocess.Popen(
                        """perl -ne 'printf "%d %d\n", ($1+$3)/2, ($2+$4)/2 if /content-desc="Uninstall"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"/' /tmp/view.xml""", shell=True, stdout=subprocess.PIPE).stdout
                    version = checkInstalled.read()
                    print("[*] waiting for apk to download")
                    installedFlag = str(version.decode('UTF-8').strip())
                    if installedFlag is not "":
                        print("[*] Apk is installed")
                        break
                    maxWaitingTime=maxWaitingTime-10
                    if maxWaitingTime<=0:
                        print("[*] Apk is taking too long to install")
                        break
                paths = ['']
                while paths[0] is '':
                    time.sleep(5)
                    apkPath = subprocess.Popen(
                        "adb shell pm path "+apkName, shell=True, stdout=subprocess.PIPE).stdout
                    apkPath = apkPath.read()
                    paths = apkPath.decode('UTF-8').split("\n")
                paths[0] = paths[0].replace("package:", "")
                print("[*]apk installed path:"+paths[0])
                os.system("adb pull "+paths[0]+" "+destination)
                DIRECTORY = os.environ.get("DIRECTORY")
                APIKEY = os.environ.get("APIKEY")
                SERVER = os.environ.get("SERVER")
                DELAY = os.environ.get("DELAY")
                try:
                    start_function(DIRECTORY,APIKEY,SERVER,DELAY)
                except:
                    print("[*] error occurred")
                os.system("adb uninstall "+apkName)
                os.system("rm /home/jaden/projects/NullCon23/backend/apks/"+apkName+".apk")