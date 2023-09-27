"""
MOBSF REST API Python Requests
"""

import json
# from msilib.schema import Directory
from turtle import pos
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import argparse
import logging
import os
import urllib.error
import urllib.parse
import urllib.request
from dotenv import load_dotenv
import time

load_dotenv()
logger = logging.getLogger(__name__)

SERVER = os.environ.get("SERVER")
APIKEY = os.environ.get("API_KEY")


def upload(FILE, SERVER, APIKEY):
    """Upload File"""
    print("Uploading file")
    multipart_data = MultipartEncoder(
        fields={'file': (FILE, open(FILE, 'rb'), 'application/octet-stream')})
    headers = {'Content-Type': multipart_data.content_type,
               'Authorization': APIKEY}
    response = requests.post(SERVER + '/api/v1/upload',
                             data=multipart_data, headers=headers)
    if response.status_code == 200 and 'hash' in response.json():
        logger.info('[OK] Upload OK: %s', FILE)
    else:
        logger.error('Performing Upload: %s', FILE)
    print(response.text)
    return response.json()


def scan(data, APIKEY, SERVER):
    """Scan the file"""
    print("Scanning file")
    post_dict = data
    print(post_dict)
    headers = {'Authorization': APIKEY}
    response = requests.post(SERVER + '/api/v1/scan',
                             data=post_dict, headers=headers)
    print(response.text)
    return response.json()


def pdf(data, APIKEY, SERVER):
    """Generate PDF Report"""
    print("Generate PDF report")
    headers = {'Authorization': APIKEY}
    data = {"hash": json.loads(data)["hash"]}
    response = requests.post(
        SERVER + '/api/v1/download_pdf', data=data, headers=headers, stream=True)
    with open("report.pdf", 'wb') as flip:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                flip.write(chunk)
    print("Report saved as report.pdf")
    return response.json()


def json_resp(data, APIKEY, SERVER, mins=0):
    """Generate JSON Report"""
    print("Generate JSON report")
    headers = {'Authorization': APIKEY}
    data = {"hash":data['appsec']["hash"]}
    time.sleep(mins*60)
    response = requests.post(
        SERVER + '/api/v1/report_json', data=data, headers=headers)
    resp = response.json()

    if "report" in resp and resp['report'] == "Report not Found":
        print("waiting for "+str(mins)+" mins")
        json_resp(data, APIKEY, SERVER, mins)
    return response.json()


def delete(data, APIKEY, SERVER):
    """Delete Scan Result"""
    print("Deleting Scan")
    headers = {'Authorization': APIKEY}
    data = {"hash": data["hash"]}
    response = requests.post(
        SERVER + '/api/v1/delete_scan', data=data, headers=headers)
    print(response.text)
    return response.json()


def start_function(DIRECTORY, APIKEY, SERVER, DELAY):
    directory = DIRECTORY
    print(directory)
    uploaded = []
    mimes = {
        '.apk': 'application/octet-stream',
        '.ipa': 'application/octet-stream',
        '.appx': 'application/octet-stream',
        '.zip': 'application/zip',
    }
    for filename in os.listdir(directory):
        fpath = os.path.join(directory, filename)
        _, ext = os.path.splitext(fpath)
        if ext in mimes:
            RESP = upload(fpath, SERVER, APIKEY)
            RESP = scan(RESP, APIKEY, SERVER)
            fp=open("/home/jaden/projects/NullCon23/results/"+filename+".json","w")
            json.dump(RESP, fp,indent=4)
            fp.close()