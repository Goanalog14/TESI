import requests
import os

virus_folder = "/home/simone/Scrivania/hello_flask/virus_directory"
url = "http://127.0.0.1:50100/uploader"

for file in os.listdir(virus_folder):
    virus_path = os.path.join(virus_folder,file)
    with open(virus_path,'rb') as f:
        r = requests.post(url,files={'file':f})
        if r.status_code == 200:
            print(f"file {f} inviato con successo!")
        else:
            print(f"invio del file {f} fallito")