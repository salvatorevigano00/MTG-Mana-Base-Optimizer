import os
import sys
import urllib.request
from mtga_parser import MTGJSONParser
from mtga_optimizer import AppCLI
from const import JSON_URL, JSON_FILE, CSV_FILE, HEADER

if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

os.chdir(base_dir)

def download_with_headers(url, filename):
    req = urllib.request.Request(
        url, 
        data=None, 
        headers=HEADER
    )
    with urllib.request.urlopen(req) as response, open(filename, 'wb') as out_file:
        out_file.write(response.read())

def setup_env():
    if not os.path.exists(JSON_FILE):
        print(f"Downloading the latest MTG database ({JSON_FILE})...")
        download_with_headers(JSON_URL, JSON_FILE)
        
    if not os.path.exists(CSV_FILE):
        print("Crunching the numbers and preparing the card database...")
        MTGJSONParser(JSON_FILE, CSV_FILE).run()

def main():
    setup_env()
    AppCLI().run()

if __name__ == "__main__":
    main()