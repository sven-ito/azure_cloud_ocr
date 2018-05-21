########### Python 3.2 #############
import http.client, urllib.request, urllib.parse, urllib.error, base64
import os
from os import listdir
from os.path import isfile, join
import time
import logging
import sys

API_URL = 'westcentralus.api.cognitive.microsoft.com'
INPUT_PATH = 'input/'
OUTPUT_PATH = 'output/'
WAIT_INTERVAL_IN_SEC = 5
API_KEY_FILE = '.apikey'

def get_root_logger():

    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.INFO)
    
    logFormatter = logging.Formatter("{asctime} {levelname} [{filename}:{lineno}] {message}", "%d.%m.%Y %H:%M:%S", style="{")
    
    logFileName = get_file_name_without_ext(__file__)+".log"
    
    fileHandler = logging.FileHandler(logFileName, mode='a')
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    
    return rootLogger

def read_api_key():

    f = open(API_KEY_FILE, "r")
    api_key = f.readline().strip()
    f.close()
    
    return api_key

def get_file_name_without_ext(filename):

    return os.path.splitext(filename)[0]

def azure_ocr_export_json(filename):

    api_key = read_api_key()

    headers = {
        # Request headers
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': api_key,
    }

    params = urllib.parse.urlencode({
        # Request parameters
        'language': 'de',
        'detectOrientation ': 'true',
    })

    try:
        body = open(filename, "rb")
        
        conn = http.client.HTTPSConnection(API_URL)
        conn.request("POST", "/vision/v2.0/ocr?%s" % params, body, headers)
        response = conn.getresponse()
        data = response.read()
        
        json_output_filename = get_file_name_without_ext(filename) + ".json"
        
        
        #print(data)
        conn.close()
        
        return data
        
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
        
def write_to_json_file(data, filename):

    f2 = open(filename, "wb")
    f2.write(data)
    f2.close()

def main():

    rootLogger = get_root_logger()

    mypath = INPUT_PATH
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    number_of_files = len(onlyfiles)
    
    rootLogger.info('Found '+str(number_of_files)+' files in '+INPUT_PATH+' .')
    
    i = 1
    
    for filename in onlyfiles:
    
        rootLogger.info('Working on file '+str(i)+'/'+str(number_of_files)+'.')
        input_filename = INPUT_PATH+filename
        rootLogger.info('Submitting '+input_filename+' to API.')
        data = azure_ocr_export_json(input_filename)
        json_filename = get_file_name_without_ext(filename)+'.json'
        output_filename = OUTPUT_PATH+json_filename
        rootLogger.info('Writing '+output_filename+' to disk.')
        write_to_json_file(data,output_filename)
        rootLogger.info('Pausing for '+str(WAIT_INTERVAL_IN_SEC)+' seconds.') 
        time.sleep(WAIT_INTERVAL_IN_SEC)
        
        i = i + 1

if __name__ == "__main__":
    main()